# 06_PERFORMANCE_CONCURRENCY_SCALABILITY.md

# Enterprise Performance Engineering, High Concurrency & Scalability Standard

## 1. Architectural Philosophy: Performance by Design

In multi-app enterprise Frappe deployments, scalability is not achieved through post-launch server upgrades. It is designed into the data access layer, controller methods, and queue architecture from day one.

### The Enterprise Performance Budget:

- **Interactive Web/Mobile Endpoints:** $\le 300\text{ ms}$ (p95) response time under 100 concurrent users.
- **Bulk Processing & Data Import:** Batching $\ge 1,000$ records per transaction without database lock timeouts or memory bloat.
- **Background Queue Latency:** Zero queue starvation; short-queue jobs execute within $< 5\text{ seconds}$ of enqueueing.

---

## 2. N+1 Query Elimination & QueryBuilder Batching

The single most frequent performance failure in Frappe applications is invoking `frappe.get_doc()` or issuing a SQL query inside a loop over list records.

### Anti-Pattern (N+1 Query Explosion):

```python
# CRITICAL DEFECT: 1 + N queries (100 orders = 101 database roundtrips)
orders = frappe.get_all("Sales Order", filters={"status": "To Deliver"}, fields=["name"])
for order in orders:
    doc = frappe.get_doc("Sales Order", order.name)  # Executes query per loop!
    process_order(doc)
```

### The Enterprise Batching Pattern:

Fetch all parent and child records in exactly two indexed queries, then assemble them in memory using a dictionary:

```python
# ENTERPRISE STANDARD: Exactly 2 queries regardless of record count
order_names = frappe.get_all(
    "Sales Order",
    filters={"status": "To Deliver"},
    pluck="name"
)

if not order_names:
    return []

# Query 1: Fetch parent records
parents = frappe.get_all(
    "Sales Order",
    filters={"name": ["in", order_names]},
    fields=["name", "customer", "grand_total", "delivery_date"]
)

# Query 2: Batch fetch child items
items = frappe.get_all(
    "Sales Order Item",
    filters={"parent": ["in", order_names]},
    fields=["parent", "item_code", "qty", "rate", "amount"]
)

# Assemble in memory in O(N) time
items_by_parent = frappe.utils.collections.groupby(items, key="parent")
for parent in parents:
    parent["items"] = items_by_parent.get(parent["name"], [])
    process_batched_order(parent)
```

---

## 3. High-Volume Serial & Barcode Logistics Architecture

Enterprise operations frequently receive, track, and issue thousands of serialized items (equipment barcodes, device serials, asset components).

### Scalability Principles for High-Volume Records:

1. **Chunked Database Inserts:** When processing batches of $> 500$ serial numbers, chunk the records into batches of 200–500 to avoid MariaDB `max_allowed_packet` exhaustion and long-held transaction row locks.
2. **Bulk Insertion API:** Prefer `frappe.db.bulk_insert()` or parameterized batch inserts over individual `doc.insert()` loops when creating ledger logs or serial tracking rows:
   ```python
   # High-throughput batch insert (10x faster than doc.insert loops)
   serial_rows = [
       (serial_no, item_code, warehouse, now_timestamp)
       for serial_no in serial_list
   ]
   frappe.db.bulk_insert(
       "Serial Tracking Entry",
       fields=["serial_no", "item_code", "warehouse", "creation"],
       values=serial_rows
   )
   ```
3. **Database Streaming & Generators:** For large data exports or reconciliation jobs, use database cursors or pagination chunks (`start=offset, page_length=1000`) rather than loading millions of rows into Python memory at once.

---

## 4. Background Workers & Queue Sizing Strategy

Frappe uses Python RQ (Redis Queue). An architect must partition background workloads across appropriate queues based on execution duration:

| Queue Name |   Timeout    | Sizing Purpose & Workload Types                                      | Example Operations                                                                           |
| :--------- | :----------: | :------------------------------------------------------------------- | :------------------------------------------------------------------------------------------- |
| `short`    |  300s (5m)   | High-priority, latency-sensitive tasks triggered by user events.     | Real-time WhatsApp/SMS alerts, transactional webhooks, immediate notification logs.          |
| `default`  | 1500s (25m)  | Standard asynchronous business tasks.                                | Branded PDF proposal compilation, stock reconciliation recalculation, email digest dispatch. |
| `long`     | 9000s (2.5h) | Heavy batch processing, bulk imports, and scheduled synchronization. | Bulk serial number importing, third-party API batch syncs, month-end ledger aggregations.    |

### Background Job Guidelines:

- **`enqueue_after_commit` Standard:** Always use `frappe.enqueue(..., enqueue_after_commit=True)`. This guarantees the job only triggers after the enclosing database transaction has committed successfully, preventing worker race conditions where the job executes before data is written.
- **Idempotency Invariant:** Background jobs can be re-delivered due to network hiccups or worker timeouts. Every job handler must check whether the operation has already been completed before executing side-effects:
  ```python
  def sync_external_telemetry(device_id: str, date: str):
      # Idempotency check: abort if already synced
      if frappe.db.exists("Device Telemetry Log", {"device_id": device_id, "date": date}):
          return
      ...
  ```
- **Distributed Locking:** For operations that must never run concurrently on the same resource, use Redis distributed locks:
  ```python
  lock = frappe.cache().lock(f"lock:order_process:{order_name}", timeout=60)
  if not lock.acquire(blocking=False):
      frappe.throw(_("Document is currently being processed by another worker. Please retry."))
  try:
      execute_order_settlement(order_name)
  finally:
      lock.release()
  ```

---

## 5. Layered Caching Architecture

Caching must be explicit, targeted, and paired with immediate write-path invalidation:

```
[ Incoming Request ]
         │
         ▼
[ Redis Cache Lookup ] ──(Cache Hit)──► Return Cached Value (< 5ms)
         │ (Cache Miss)
         ▼
[ Database Query / Complex Calculation ]
         │
         ▼
[ Write to Redis Cache ] ──► Return Fresh Value
```

### Implementation Guidelines:

1. **Namespace Partitioning:** Cache keys must follow strict namespacing: `f"app_name:{doctype}:{identifier}:{metric}"`.
2. **Explicit Write-Path Invalidation:** Never rely solely on TTLs (Time-To-Live) for critical business data. Invalidate the cache explicitly inside the controller's `on_update` and `on_trash` lifecycle hooks:
   ```python
   def on_update(self):
       frappe.cache().delete_value(f"my_app:pipeline_progress:{self.name}")
   ```
3. **Request-Level Memoization:** For identical lookups repeated multiple times within a single HTTP request lifecycle, use a local Python dictionary or `functools.lru_cache` on request-bound helper methods.

---

## 6. Frontend Performance & Asset Optimization

When building custom portals or Frappe UI single-page apps:

- **Route-Level Code Splitting:** Use dynamic imports (`() => import('./views/StageDetail.vue')`) so the initial bundle downloads only the core shell, deferring heavy stage views until navigated.
- **Virtual Scrolling for Large Lists:** Never render $> 100$ DOM nodes for list records simultaneously. Use virtual list components (e.g. `vue-virtual-scroller`) for high-volume list screens.
- **Input Debouncing:** Debounce search-as-you-type and filter inputs by $\ge 300\text{ ms}$ to prevent overloading the backend with concurrent search requests.

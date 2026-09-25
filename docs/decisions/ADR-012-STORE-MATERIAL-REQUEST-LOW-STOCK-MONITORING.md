# ADR-012: Store Material Request & Automated Low-Stock Replenishment Architecture

## Status

Accepted

## Date

2026-09-25

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), **Step 12: Store Material Request & Automated Low-Stock Monitoring** (Flow 2: Step 01 of 08) serves as the operational demand-generation gateway and inventory replenishment engine for all procurement and supply chain activities. It directly precedes Step 13 (Supplier Request for Quotation — RFQ), Step 14 (Supplier Quotation Comparative Evaluation Matrix & Landed Cost), and Step 15 (Purchase Order Authorization).

Under legacy solar EPC procurement practices and standard ERP implementations, warehouse inventory control and material requisitioning suffered from acute operational friction, supply vulnerabilities, and governance blindspots:

1. **Reactive, Informal Requisitions ("WhatsApp Procurement"):** Line warehouse staff and site technicians traditionally requested hardware through unstructured phone calls, handwritten paper chits, or private WhatsApp messages. These informal requests lacked project attribution, budget validation, and technical specifications, leading to unverified purchases, duplicate orders, and commercial leakage.
2. **Naive Ledger Counting vs. Pipeline Solvency Blindness:** Standard inventory systems evaluate replenishment using simple ledger balances (`actual_qty`). In fast-moving Solar EPC projects, this naive calculation results in either catastrophic stockouts (when on-hand stock appears sufficient but is already earmarked for active site dispatches) or severe over-purchasing (when reorder alerts fire repeatedly despite open Purchase Orders already in transit).
3. **Class-A Solar Asset Mismanagement:** High-value serialized assets—such as Monocrystalline PERC/TOPCon PV Modules, Solar String/Central Inverters, and High-Tension (HT) DC Cables—were requisitioned without strict project tagging, minimum pallet batch packaging rounding, or priority escalation, leading to freight inefficiencies and mismatched warranties.
4. **Lack of Demand Lead-Time Feasibility:** Site supervisors frequently requested major balance-of-system (BOS) components with unrealistic "Required-by" deadlines (e.g., requesting custom galvanized structures with a 2-day delivery window when manufacturer fabrication lead time is 14 days), forcing costly emergency freight and air shipments.
5. **Absence of SCM Turnaround (SLA) Tracking:** Material requests sat unreviewed in purchasing queues for days without SLA countdowns or managerial accountability, directly causing downstream site installation delays.
6. **Disconnected Downstream Pipeline:** Material requests lacked end-to-end traceability to downstream procurement artifacts, creating a fractured audit trail between initial store indents, supplier RFQs, quote comparisons, and released Purchase Orders.

---

## Decision

We establish an authoritative architectural standard for **Step 12: Store Material Request & Automated Low-Stock Monitoring**, extending ERPNext's native `tabMaterial Request` (`is_submittable = 1`) and implementing dedicated domain calculation services, background monitoring daemons, and multi-tier notification brokers within `solar_module`:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    STEP 12: STORE MATERIAL REQUEST & LOW-STOCK ARCHITECTURE                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Demand Trigger Channel A: Project BOM]            [Demand Trigger Channel B: Background Daemon]│
│   • Originated by Store Assistant / Project Eng       • Automated low-stock runner (tasks.py)     │
│   • Tied to Survey Design BOM (STEP_03)               • Scans tabBin across regional warehouses   │
│           │                                                          │                           │
│           └──────────────────────────┬───────────────────────────────┘                           │
│                                      ▼                                                           │
│                   [True Pipeline Solvency Computation Engine]                                    │
│                   Projected = Actual + Ordered + Indented - Reserved                             │
│                                      │                                                           │
│                                      ▼                                                           │
│                   [Verification Gate 1: Duplicate Open Indent Check]                             │
│                   • Rejects redundant MR if open unfulfilled MR exists for item/warehouse        │
│                                      │                                                           │
│                                      ▼                                                           │
│                   [Verification Gate 2: Lead Time & Schedule Date Check]                         │
│                   • Enforces: schedule_date >= today + supplier_lead_time_days                   │
│                   • Emergency bypass requires Purchase Manager / Admin sign-off                  │
│                                      │                                                           │
│                                      ▼                                                           │
│                   [Verification Gate 3: Project BOM Headroom Netting]                            │
│                   • Asserts: requested_qty <= (bom_qty - issued_qty - open_mr_qty)               │
│                                      │                                                           │
│                                      ▼                                                           │
│                   [Submit Material Request (docstatus = 1)]                                      │
│                   • Initiates Tiered Turnaround SLA (4h Emergency / 24h Project / 48h Routine)   │
│                   • Logs incident in tabSolar Low Stock Incident Log (if daemon triggered)       │
│                                      │                                                           │
│                                      ▼                                                           │
│                   [Multi-Channel SCM Notification Broker]                                        │
│                   • Automated WhatsApp & Email to Store Manager & Purchase Assistant             │
│                   • Escalation to Purchase Manager & Admin for Class-A Solar Assets              │
│                                      │                                                           │
│                                      ▼                                                           │
│                   [Downstream SCM Procurement Handshake]                                         │
│                   ──▶ Step 13: Supplier Request for Quotation (RFQ)                              │
│                   ──▶ Step 14: Supplier Quotation & Comparative Matrix Evaluation                │
│                   ──▶ Step 15: Purchase Order Placement (PO)                                     │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Standard ERPNext `Material Request` as Core Requisition Entity

Rather than inventing a parallel requisition ledger, Step 12 extends ERPNext's native `tabMaterial Request` (`is_submittable = 1`, Purpose: `Purchase` or `Material Transfer`):

- **Native Ledger Alignment:** Reuses standard item tables (`tabMaterial Request Item`), warehouse links, and stock reservation mechanisms.
- **Solar Extension Namespace:** Isolates all custom fields under the `custom_*` prefix in `solar_module` (e.g., `custom_project_reference`, `custom_sales_order`, `custom_urgency_level`, `custom_trigger_source`, `custom_workflow_status`, `custom_sla_deadline`, `custom_delay_reason`).
- **Relational Integrity:** Implements clean 3NF foreign key links to `tabProject`, `tabSales Order`, and upstream engineering design records.

### 2. Dual-Trigger Demand Inception Model

Material Requests originate through two distinct, strictly governed channels:

- **Channel A: Project-Linked Indents:** Initiated by `Store Assistant` or `Project Engineer` for active Solar EPC sites. Line items are rigorously validated against the unissued headroom of the approved Survey Engineering Design BOM (`STEP_03`).
- **Channel B: Automated Low-Stock Replenishment:** Spawned programmatically by a scheduled background daemon (`solar_module.tasks.monitor_low_stock`) scanning warehouse bins against multi-warehouse reorder policies (`tabItem Reorder`).

### 3. True Solvency Mathematics & Dynamic Replenishment Sizing

To eliminate the flaws of naive ledger counting, the system calculates pipeline solvency using true projected stock:

$$\text{Projected Stock} = \text{Actual Qty} + \text{Ordered Qty (Open POs)} + \text{Indented Qty (Open MRs)} - \text{Reserved Qty (Allocated to Active Projects)}$$

When $\text{Projected Stock} \le \text{Reorder Level}$, the replenishment daemon computes the recommended requisition quantity:

$$\text{Replenishment Qty} = \max\Big(\text{Min Order Qty},\ (\text{Reorder Level} - \text{Projected Stock}) + (\text{Lead Time (Days)} \times \text{Average Daily Consumption})\Big)$$

For Class-A equipment (such as PV Modules), quantities are automatically rounded up to the nearest pallet packaging unit (e.g., multiples of 36 modules).

### 4. Hard Verification Stage-Gates

The `MaterialRequest` controller enforces three hard server-side gates:

- **Gate 1 (Duplicate Indent Prevention):** Blocks submission if an open, unfulfilled `Material Request` already exists for the identical item and target warehouse, preventing duplicate procurement pipelines.
- **Gate 2 (Lead-Time Feasibility):** Strictly checks that the requested delivery schedule date satisfies $\text{schedule\_date} \ge \text{today} + \text{lead\_time\_days}$. Any expedited date requires `custom_urgency_level = 'Critical Breakdown'` and explicit authorization by `Purchase Manager` or `Admin`.
- **Gate 3 (Project BOM Headroom Netting):** For project-linked requisitions, the controller validates that requested quantities do not exceed the remaining unissued BOM balance from `STEP_03`, preventing rogue project over-draws.

### 5. Downstream Procurement Traceability: RFQ $\rightarrow$ Quotation Comparison $\rightarrow$ PO

Step 12 guarantees a closed-loop chain of custody into downstream procurement:

- **Step 13 (Supplier RFQ):** Approved requisitions are grouped by item category and supplier shortlist, auto-populating `tabRequest for Quotation`.
- **Step 14 (Supplier Quotation & Comparative Matrix):** Supplier quotations submitted via portal or desk are evaluated side-by-side on landed cost, lead time, payment terms, and vendor rating scorecards to determine the optimal supplier.
- **Step 15 (Purchase Order Authorization):** Authorized winning quotes are converted into formal `tabPurchase Order` records with zero manual transcription.

### 6. Tiered SLA Architecture & Mandatory Delay Audit Logging

To eliminate procurement latency:

- **Emergency / Breakdown Requisitions:** 4-hour SLA to RFQ or PO initiation.
- **Project Milestone Requisitions:** 24-hour SLA.
- **Routine Buffer Replenishment:** 48-hour SLA.
- **Mandatory Delay Log:** If the SLA deadline breaches, the document transitions to `Overdue`, locking downstream status updates until a formal explanation is appended to `tabSolar Stage Delay Log` (`tabRemark-Delay Log`) with managerial sign-off.

### 7. Zero "User" Suffix Compliance & Supreme Authority Standard

- **Role Standard:** Strict adherence to functional enterprise roles: `Store Assistant`, `Store Manager`, `Purchase Assistant`, `Purchase Manager`, `Project Engineer`, and `Admin`.
- **Authority Boundary:**
  - `System Manager`: Apex technical framework command, Python source code, DocType schemas, bench CLI, Redis workers.
  - `Admin`: Apex project-level operational command, managing `Solar SLA Settings`, `Solar Notification Settings`, and delay approvals. Restricted from source code and schemas.

---

## Consequences

### Positive Consequences

1. **Elimination of Project Stalls:** Dynamic projected stock math and automated reorder triggers prevent material stockouts, ensuring 100% on-time project installation.
2. **Zero Duplicate Procurement:** Duplicate indent verification eliminates redundant purchases and excess inventory holding costs.
3. **Optimized Freight & Packaging:** Pallet packaging rounding and lead-time feasibility checks eliminate unbudgeted air freight and emergency courier surcharges.
4. **End-to-End Auditability:** Complete digital traceability from initial site/warehouse indent through RFQ (`STEP_13`), quote comparison (`STEP_14`), and PO (`STEP_15`).

### Trade-offs & Mitigations

1. **Trade-off:** Strict lead-time checking may block genuine site emergency requirements.
   - _Mitigation:_ `Critical Breakdown` urgency flag with mandatory justification text allows immediate fast-tracking upon `Purchase Manager` or `Admin` authorization.
2. **Trade-off:** High-frequency bin monitoring daemons can cause database overhead on large SKU catalogs.
   - _Mitigation:_ Targeted SQL indexing on `tabBin` `(item_code, warehouse, actual_qty)` and batch execution via RQ `default` background queue during off-peak intervals.

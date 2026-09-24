# 03_DOCTYPE_SCHEMA_RELATIONAL_DESIGN.md

# Enterprise Schema Design, DocType Modeling & Relational Architecture Standard

## 1. Architectural Philosophy: Schema Discipline

In Frappe Framework and ERPNext, relational database schemas are defined via metadata JSON (`DocType`). Because Frappe dynamically generates database tables, indexes, and ORM behaviors directly from DocType definitions, **improper schema modeling is the single largest driver of technical debt, data corruption, and performance degradation**.

An enterprise architect does not freehand DocType schemas. Every entity is evaluated against the standards, patterns, and conventions established in core Frappe and ERPNext.

---

## 2. Decision Matrix: Custom DocType vs. Custom Field vs. Child Table

When introducing domain requirements into an ecosystem containing Frappe, ERPNext, Frappe CRM, and Frappe HRMS, evaluate where data belongs using this strict decision ladder:

```
                                  [ New Data Requirement ]
                                             │
                                             ▼
                             Is this an attribute of an existing
                              core entity (Customer, Item, Lead,
                                  Sales Order, Project, etc.)?
                                      ├─── YES ───► Add Custom Field (`custom_*`) via Fixtures
                                      └─── NO
                                             │
                                             ▼
                             Does the data have an independent
                             lifecycle, independent permissions,
                              and multiple foreign references?
                                      ├─── YES ───► Create Standalone Custom DocType
                                      └─── NO
                                             │
                                             ▼
                             Is the data strictly owned by one
                            parent, saved/deleted with it, and
                              never queried independently?
                                      ├─── YES ───► Create Child Table DocType (`istable: 1`)
                                      └─── NO  ───► Architectural Re-Evaluation Required
```

### Detailed Decision Criteria:

1. **Extend Core DocTypes (`custom_*` fields):**
   - Use when enhancing standard business entities (e.g., adding technical specifications to `Item`, billing flags to `Sales Order`, or GPS coordinates to `Lead`).
   - Fields MUST be prefixed with `custom_` (Frappe enforces this).
   - Exported cleanly via `hooks.py` fixtures with strict module filtering:
     ```python
     fixtures = [
         {"dt": "Custom Field", "filters": [["module", "=", "My_App"]]}
     ]
     ```
2. **Standalone Custom DocTypes:**
   - Use when modeling new business concepts with their own workflows, separate actors, or audit trails (e.g., `Technical Audit`, `Statutory Dossier`, `Asset Register`).
   - Must have an explicit Module assignment matching the custom app.
3. **Child Tables (`istable: 1`):**
   - Use for repeating rows whose existence depends entirely on the parent document (e.g., invoice line items, photo checklists, calculation parameters).
   - Anti-pattern: Modeling a one-to-many relationship as a child table when child rows need independent querying, bulk reporting, or separate permissions. Child tables do not support standard `frappe.get_list()` with row-level security.

---

## 3. Autonaming & Identity Strategy

Every DocType requires a deliberate autonaming strategy decided at design time. Changing an autoname pattern post-launch requires data migrations across every foreign key `Link` field in the database.

| Autoname Pattern                  | Mechanism                              | Use Case                                                              | Example                                            |
| :-------------------------------- | :------------------------------------- | :-------------------------------------------------------------------- | :------------------------------------------------- |
| `naming_series:`                  | Atomic counters in `tabSeries`         | Sequential, human-readable documents (orders, invoices, audits)       | `AUD-.YYYY.-.#####` $\rightarrow$ `AUD-2026-00001` |
| `field:<fieldname>`               | Uses unique value of a field           | Master records with a natural, unique business identifier             | `field:tax_id`                                     |
| `format:{prefix}-{field}-{#####}` | Formatted sequential string            | Composite identifiers combining static prefix, category, and sequence | `format:SRV-{branch}-{#####}`                      |
| `hash`                            | 10-character hexadecimal               | Internal/system records where human readability is not required       | `a8f3b9c1d2`                                       |
| `autoincrement`                   | Database native auto-increment integer | High-throughput system logs and append-only ledgers                   | `100452`                                           |

### Naming Series Governance:

- Always use dot-separated date formatting (`.YYYY.`, `.YY.`, `.MM.`) to ensure sequence resets behave predictably per financial or calendar year.
- Never construct manual serial strings using `frappe.db.count()` or string concatenation—concurrent transactions will generate duplicate keys and deadlock. Rely on Frappe's atomic `naming_series` engine.

---

## 4. Submittable Documents vs. Mutable Workflow Documents

Learn from ERPNext's architectural distinction between master data, operational documents, and transactional ledgers:

```
[ docstatus: 0 (Draft) ] ───► [ docstatus: 1 (Submitted) ] ───► [ docstatus: 2 (Cancelled) ]
                                            │
                                            ▼
                                  [ docstatus: 0 (Amended) ]
```

1. **Transactional / Legal Immutability (`is_submittable: 1`):**
   - Use for documents that establish financial liability, legal commitments, or physical inventory movements (e.g., contracts, commercial proposals, purchase receipts).
   - Submission freezes the document (`docstatus: 1`). Changes require the standard Frappe Cancel $\rightarrow$ Amend workflow, preserving an immutable audit trail.
2. **Operational / Master Data (Non-Submittable):**
   - Use for entities that undergo continuous refinement or long-term operational updates (e.g., customer profiles, technical audits, asset registers).
   - Govern progress and approvals using **Frappe Workflow** states rather than submit/cancel semantics.

---

## 5. Child Table Architectural Patterns

In enterprise Frappe applications, child tables commonly follow one of three proven design patterns:

### Pattern A: Mandatory Verification Checklist Table

Used for on-site audits, quality checks, and statutory submissions requiring complete evidence before approval:

- **Fields:** `checklist_item` (`Data`), `is_mandatory` (`Check`), `attached_document` (`Attach`), `status` (`Select: Pending/Verified/Rejected`), `verified_by` (`Link: User`), `verification_date` (`Datetime`).
- **Enforcement:** The parent controller's `validate()` iterates through the table and throws a validation error if any row marked `is_mandatory: 1` has an empty `attached_document`.

### Pattern B: Parametric Calculation Table

Used for complex engineering formulas, cable sizing, or multi-factor pricing matrices:

- **Fields:** `parameter_name` (`Data`), `unit` (`Link: UOM`), `input_value` (`Float`), `formula_factor` (`Float`), `calculated_result` (`Float`).
- **Enforcement:** Calculations are executed server-side in the domain service during `before_save()`, writing back to read-only fields on child rows.

### Pattern C: Dynamic BOM & Material Explosion Table

Used for generating multi-item requisitions from engineering specifications:

- **Fields:** `item_code` (`Link: Item`), `item_name` (`Data`), `qty` (`Float`), `uom` (`Link: UOM`), `rate` (`Currency`), `amount` (`Currency`), `category` (`Select`).
- **Enforcement:** Quantities and item codes are populated from master templates and frozen upon parent submission.

---

## 6. Fieldtype Selection & Precision Standards

Always select fieldtypes that enforce data integrity at the database level:

| Data Type                 | Correct Fieldtype                 | Anti-Pattern | Justification                                                                              |
| :------------------------ | :-------------------------------- | :----------- | :----------------------------------------------------------------------------------------- |
| Monetary Amounts          | `Currency`                        | `Float`      | Handles currency precision, symbol formatting, and multi-currency exchange rates natively. |
| Ratios & Percentages      | `Percent`                         | `Float`      | Native percentage rendering (0–100%) without manual UI multiplier math.                    |
| Foreign Key Link          | `Link`                            | `Data`       | Enforces foreign key referential integrity in MariaDB and powers Frappe search popups.     |
| Geolocation Coordinates   | `Geolocation` / `Float` (lat/lng) | `Data`       | Enables map visualization, GeoJSON storage, and spatial queries.                           |
| Single-Choice Enumeration | `Select`                          | `Data`       | Enforces controlled vocabulary at the schema level.                                        |
| File Attachments          | `Attach` / `Attach Image`         | `Data`       | Manages file storage, public/private access tokens, and CDN linking.                       |

---

## 7. Database Indexing & Performance Design

An unindexed foreign key or status field is guaranteed to degrade into a slow-query incident as table volume grows:

1. **Single-Column Search Indexes (`search_index: 1`):**
   - Apply to every field frequently used in `filters=` queries (e.g., `status`, `assigned_to`, `territory`, `date`).
   - Apply to external business identifiers (e.g., customer mobile numbers, external contract references).
2. **Unique Constraints (`unique: 1`):**
   - Apply to fields that must be globally unique across the system (e.g., national identity numbers, serialized device identifiers).
3. **Composite Database Indexes:**
   - When queries consistently filter by two or more columns together (e.g., `WHERE status = 'Pending' AND assigned_to = 'user@example.com'`), single-column indexes are suboptimal.
   - Plan composite indexes created via database migration patches:
     ```python
     # patch.py
     def execute():
         frappe.db.add_index("Technical Audit", ["status", "assigned_to"], "idx_audit_status_assignee")
     ```

---

## 8. Schema Change Governance Post-Launch

Once a DocType has production data, schema modifications require strict discipline:

- **Never Change Fieldtypes In-Place:** Changing a `Data` field to a `Link` field directly in DocType JSON can fail or corrupt existing data during `bench migrate`. Plan a phased migration patch to validate and convert existing values.
- **Renaming Fields is a Breaking Change:** Renaming a fieldname breaks every linked report, print format, client script, and integration query. If renaming is essential, maintain a temporary computed getter or backwards-compatible alias in the controller until all dependents are updated.

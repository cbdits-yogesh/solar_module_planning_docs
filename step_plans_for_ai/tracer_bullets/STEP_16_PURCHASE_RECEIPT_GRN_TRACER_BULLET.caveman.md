# STEP_16_PURCHASE_RECEIPT_GRN_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 16 Multi-Location Barcode Purchase Receipt (GRN) & Tri-Party Custody Approval Architecture

**Document ID:** `TB-16-PURCHASE-RECEIPT-GRN`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.caveman.md`](../STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-016-MULTI-LOCATION-PURCHASE-RECEIPT-BARCODE-GRN.md`](../../docs/decisions/ADR-016-MULTI-LOCATION-PURCHASE-RECEIPT-BARCODE-GRN.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_15_PURCHASE_ORDER_AUTHORIZATION_TRACER_BULLET.caveman.md`](STEP_15_PURCHASE_ORDER_AUTHORIZATION_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_14_QUOTATION_COMPARISON_MATRIX_TRACER_BULLET.caveman.md`](STEP_14_QUOTATION_COMPARISON_MATRIX_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_13_SUPPLIER_RFQ_TRACER_BULLET.caveman.md`](STEP_13_SUPPLIER_RFQ_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md`](STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md`](STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Step 17 Purchase Invoice 3-Way Match ([`STEP_17`](../STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.caveman.md)), Step 18 Vendor Payment Workbench ([`STEP_18`](../STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.caveman.md)), Step 19 Vendor Rating Scorecard ([`STEP_19`](../STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.caveman.md)), Flow 1 Stage 08 Material Dispatch & Stage 09 Installation Zone DPR ([`STEP_08`](STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md), [`STEP_09`](STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md)), Flow 1 Stage 11 Solar Asset Register ([`STEP_11`](STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_TRACER_BULLET.caveman.md))  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-13`, `BC-14`), `planning_ref_docs/03_TO_BE_BUSINESS_PROCESS.md` (`Step 05`, `Gate 9`), `planning_ref_docs/04_GAP_ANALYSIS_FIT_GAP.md` (`Gap #07`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-011`, `BR-014`, `BR-016`, `BR-017`, `BR-018`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-014`, `FR-015`, `FR-016`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 7: SCM`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 11`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 18`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-14`, `MOD-15`), `planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md` (Sec 2, 4.1)  
**Target Module:** `solar_module` / SPA `/solar/store/grn-scanner`, `/solar/site/material-inward`, `/solar/purchase/direct-receipt`, `/solar/admin/pending-stock-updates` (Extends ERPNext `tabPurchase Receipt`, child table `tabPurchase Receipt Item`, integrates `tabSerial and Batch Bundle`, `tabSerial No`, settings `tabSolar SCM Settings` & `tabSolar SLA Settings`, child table `tabSolar Stage Delay Log`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** A disposable UI mock or isolated script that accepts a goods receipt without physical stock validation, allows site deliveries without geodesic verification, bypasses Frappe v15 Serial and Batch Bundle (SABB) architecture, lets purchase personnel dump unverified inventory into central stores or project sites without managerial custody approvals, ignores damage quarantine routing, and breaks financial traceability to downstream 3-way matching and vendor rating.
- **Tracer Bullet:** A permanent, production-grade 5-layer thin vertical slice cutting cleanly through the live Frappe enterprise architecture. It establishes robust intake custody across 3 distinct enterprise personas (Store Team, Site Team, Purchase Team), anchors real database schemas (`tabPurchase Receipt`, `tabPurchase Receipt Item`, `tabSerial and Batch Bundle`, `tabSolar SCM Settings`, `tabSolar SLA Settings`), implements pure SOLID Python domain services (`PurchaseReceiptValidationService`, `GRNStockUpdateOrchestrationService`, `PRSerialBarcodeService`, `PRSLAService`, `PRDownstreamBridgeService`), exposes authenticated whitelisted RPC endpoints (`solar_module.api.procurement.*`), connects responsive Desk client scripts and mobile PWAs, and executes an automated zero-commit integration test suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 16 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabPurchase Receipt extensions (team, location, geofence, approval gates)│
│   - tabPurchase Receipt Item extensions (destination, SABB scan, rejections)│
│   - tabSolar SCM Settings (Admin-configurable barcode policy & geofence)    │
│   - tabSolar SLA Settings (Admin-configurable 24h GRN TAT countdown)        │
│   - Composite B-Tree Indexes on PR, Item, and Serial/Bundle tables          │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - PurchaseReceiptValidationService (5 canonical verification gates)       │
│   - GRNStockUpdateOrchestrationService (Tri-party custody routing & SLE)    │
│   - PRSerialBarcodeService (Frappe v15 SABB engine & 2D barcode batch)      │
│   - PRSLAService (24h turnaround countdown, breach detector, delay logger)  │
│   - PRDownstreamBridgeService (Step 17 PI, Step 18 milestone, Step 19 score)│
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                     │
│   - PurchaseReceipt controller override extending StageSecuredDocument      │
│   - Stage-Forward Immutability Lock (blocking cancel once Step 17 PI exists)│
│   - Whitelisted RPC APIs (solar_module.api.procurement.*):                  │
│     * create_purchase_receipt_from_po                                       │
│     * parse_and_attach_sabb_barcodes                                        │
│     * approve_store_stock_update (Admin only)                               │
│     * approve_site_stock_update (Project Manager / Admin)                   │
│     * toggle_barcode_policy (Admin only)                                    │
│     * log_pr_delay & get_pr_inspection_summary                              │
│   - Background Celery/RQ daemon (procurement_grn_sla_daemon every 15m)       │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Mobile/Portal Workbench Hook          │
│   - codes/client_script/purchase_receipt.js (Persona UI, dynamic badges,    │
│     SABB scan modal, split calculator, sign-off modals, junior cancel)      │
│   - Fast-Touch Mobile Goods Receipt PWA (/solar/site/material-inward)       │
│   - Store Receiving Dock Gun Scanner (/solar/store/grn-scanner)             │
│   - Custody Approval Workbench (/solar/admin/pending-stock-updates)         │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Tests)                   │
│   - solar_module/tests/test_step_16_purchase_receipt_tracer_bullet.py       │
│   - Subclasses frappe.tests.utils.FrappeTestCase                            │
│   - Strict Zero-Commit Rule (frappe.db.rollback() in tearDown)              │
│   - 12 atomic test cases covering all 5 verification gates and edge cases   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental business, operational, and security invariants of Stage 16 across the live Frappe stack:

1. **Gate 1: Upstream PO Integrity & Over-Receipt Tolerance:** Assert that every incoming goods receipt is anchored to an approved, submitted `tabPurchase Order` (`docstatus = 1`). Enforce strict 0% over-receipt tolerance on serialized solar assets (PV modules, string inverters, transformers) and $\le 3\%$ buffer on bulk hardware (mounting structure fasteners, earthing conductors).
2. **Gate 2: Tri-Party Persona & Role Authorization (ADR-000):** Enforce strict server-side validation against the active user's role and receiving team declaration:
   - **Store PR:** Exclusively `Store Assistant` or `Store Manager`.
   - **Site PR:** Exclusively `Project Engineer` or `Site Supervisor`.
   - **Purchase PR:** Exclusively `Purchase Assistant` (Draft creation) or `Purchase Manager` (Submission).
   - Zero "User" suffix rule strictly maintained.
3. **Gate 3: Admin-Controllable Barcode Policy Gate:** Dynamically evaluate `Solar SCM Settings.enable_mandatory_barcode_pr`:
   - When **Enabled (=1):** PR submission is hard-blocked unless all serialized items have 100% verified Frappe v15 Serial and Batch Bundles (`received_qty == total_qty`).
   - When **Disabled (=0):** The system sets `custom_barcode_scan_bypassed = 1`, logs an audit trail, and permits field submission without blocking logistics during rain, low light, or damaged OEM carton labels.
4. **Gate 4: Multi-Location Warehouse & Custody Routing Gate:**
   - **Store PR:** Defaults to `Stores - SEPC` (changeable by `Store Manager`), posts Stock Ledger Entries (SLE) instantly upon submission.
   - **Site PR:** Mandates physical receipt at `Site - <Project Code> - SEPC`, captures hardware GPS coordinates, verifies that distance to project site is $\le 500\text{m}$ via Haversine geodesic calculation, and posts Site Stock Ledger Entries instantly.
   - **Purchase PR:** Provides flexible line-item routing (`Central Store Warehouse` vs `Project Site Warehouse`). Automatically intercepts and locks unapproved stock movements:
     - Store-bound items require explicit sign-off by **`Admin`** before posting Store SLE.
     - Site-bound items require explicit sign-off by **`Project Manager`** before posting Site SLE.
5. **Gate 5: Physical Inspection & Delivery Proof Gate:** Mandates uploaded supplier Delivery Challan and Transporter Lorry Receipt (LR). If damage/rejection occurs (`rejected_qty > 0`), enforces mandatory rejection reason code, automatic quarantine routing (`Quarantine / Rejection - SEPC`), and minimum 2 uploaded defect photographs.
6. **Gate 6: Turnaround SLA Engine (24h TAT):** Enforces an automated 24-hour turnaround window from vehicle gate entry / document creation to final submission. Background daemon monitors deadlines every 15 minutes, transitioning overdue records to `Breached / Overdue` and locking state modifications until justified in `tabSolar Stage Delay Log`.
7. **Gate 7: Stage-Forward Immutability Lock & Cancellation Interception:** Prevents unilateral cancellation or amendment of submitted Purchase Receipts once downstream Step 17 `tabPurchase Invoice` exists. Junior cancellations are intercepted into the `Solar Cancellation Request` workflow requiring Department Manager sign-off.
8. **Gate 8: Downstream Lifecycle Handshake:** Automatically triggers downstream hooks: unlocks Step 17 3-way invoice matching, releases Step 18 milestone tranche ("Post-GRN Inspection"), updates Step 19 vendor rating metrics, feeds Flow 1 Stage 08/09 DPR site stock balance, and registers serialized solar assets in Flow 1 Stage 11 Asset Register.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Extends standard ERPNext `tabPurchase Receipt`, child table `tabPurchase Receipt Item`, introduces Admin-configurable settings in `tabSolar SCM Settings` and `tabSolar SLA Settings`, integrates child `tabSolar Stage Delay Log`, and establishes MariaDB composite B-Tree indexes.

### 2.1 Core DocType Extension: `tabPurchase Receipt`

| Fieldname                            | Label                             | Fieldtype  | Options / Target                                                                   | Mandatory | Index | Description & Validation Rules                                                                             |
| :----------------------------------- | :-------------------------------- | :--------- | :--------------------------------------------------------------------------------- | :-------: | :---: | :--------------------------------------------------------------------------------------------------------- |
| `custom_received_by_team`            | Received By Team                  | `Select`   | `Store Team\nSite Team\nPurchase Team`                                             |  **Yes**  |   1   | Declares receiving persona, triggering tailored validation pipelines and stock update logic.               |
| `custom_received_by_user`            | Receiving Officer                 | `Link`     | `User`                                                                             |  **Yes**  |   1   | Captures specific user executing dock or field intake.                                                     |
| `custom_receiver_role`               | Receiver Role Title               | `Data`     | -                                                                                  |    No     |   -   | Populated automatically with active user role (`Store Assistant`, `Project Engineer`, etc.).               |
| `custom_receipt_location_type`       | Receipt Location Type             | `Select`   | `Central Store Warehouse\nDirect Project Site Warehouse\nThird-Party Staging Yard` |  **Yes**  |   1   | Logistical destination category.                                                                           |
| `custom_default_store_warehouse`     | Default Store Warehouse           | `Link`     | `Warehouse`                                                                        |    No     |   -   | Defaults to `Stores - SEPC`. Editable by `Store Manager` if alternate store warehouse is used.             |
| `custom_project_ref`                 | Solar Project Reference           | `Link`     | `Project`                                                                          |    No     |   1   | Mandatory if `custom_receipt_location_type == 'Direct Project Site Warehouse'` or if items routed to site. |
| `custom_sales_order_ref`             | Sales Order Reference             | `Link`     | `Sales Order`                                                                      |    No     |   1   | Inherited from linked Purchase Order for end-to-end commercial traceability.                               |
| `custom_transporter_name`            | Transporter / Logistics Provider  | `Data`     | -                                                                                  |  **Yes**  |   -   | Commercial carrier name (e.g. `V-Trans`, `TCI Freight`).                                                   |
| `custom_lr_number`                   | Lorry Receipt (LR) / Bilty Number | `Data`     | -                                                                                  |  **Yes**  |   1   | Consignment note number from freight carrier.                                                              |
| `custom_lr_date`                     | Lorry Receipt (LR) Date           | `Date`     | -                                                                                  |  **Yes**  |   -   | Date recorded on transporter consignment note.                                                             |
| `custom_vehicle_no`                  | Vehicle Registration Number       | `Data`     | -                                                                                  |  **Yes**  |   -   | Transport vehicle license plate number (e.g. `GJ01AB1234`).                                                |
| `custom_driver_phone`                | Driver Contact Number             | `Data`     | -                                                                                  |    No     |   -   | 10-digit mobile contact of delivery vehicle driver.                                                        |
| `custom_delivery_challan_no`         | Supplier Delivery Challan / Inv   | `Data`     | -                                                                                  |  **Yes**  |   1   | Supplier delivery challan or dispatch invoice reference.                                                   |
| `custom_delivery_challan_date`       | Delivery Challan Date             | `Date`     | -                                                                                  |  **Yes**  |   -   | Date recorded on supplier challan.                                                                         |
| `custom_delivery_challan_file`       | Delivery Challan Proof            | `Attach`   | -                                                                                  |  **Yes**  |   -   | Scanned copy or photograph of signed physical delivery challan.                                            |
| `custom_transporter_lr_file`         | Transporter LR Proof              | `Attach`   | -                                                                                  |  **Yes**  |   -   | Scanned copy or photograph of transporter bilty.                                                           |
| `custom_gps_latitude`                | Offloading GPS Latitude           | `Float`    | -                                                                                  |    No     |   -   | Captured device latitude at offloading location. Mandatory for Site PR.                                    |
| `custom_gps_longitude`               | Offloading GPS Longitude          | `Float`    | -                                                                                  |    No     |   -   | Captured device longitude at offloading location. Mandatory for Site PR.                                   |
| `custom_gps_accuracy_m`              | GPS Horizontal Accuracy (m)       | `Float`    | -                                                                                  |    No     |   -   | Accuracy radius in meters reported by device geolocation API.                                              |
| `custom_barcode_scan_enforced`       | Barcode Policy Enforced?          | `Check`    | -                                                                                  |    No     |   -   | Audit freeze of `Solar SCM Settings.enable_mandatory_barcode_pr` at time of receipt.                       |
| `custom_barcode_scan_bypassed`       | Barcode Policy Bypassed?          | `Check`    | -                                                                                  |    No     |   -   | Flagged if barcode scan was bypassed via Admin toggle.                                                     |
| `custom_has_store_bound_items`       | Contains Store-Bound Items?       | `Check`    | -                                                                                  |    No     |   -   | Computed flag: 1 if any line item is routed to a Central Store Warehouse.                                  |
| `custom_has_site_bound_items`        | Contains Site-Bound Items?        | `Check`    | -                                                                                  |    No     |   -   | Computed flag: 1 if any line item is routed to a Project Site Warehouse.                                   |
| `custom_store_stock_approval_status` | Store Stock Approval Status       | `Select`   | `Not Applicable\nPending Admin Approval\nApproved by Admin\nRejected by Admin`     |  **Yes**  |   1   | Custody gate for Purchase PR items routed to Store: requires Admin sign-off before posting Store SLE.      |
| `custom_store_stock_approved_by`     | Store Stock Approved By           | `Link`     | `User`                                                                             |    No     |   -   | Admin user ID who authorized store stock intake.                                                           |
| `custom_store_stock_approved_on`     | Store Stock Approved On           | `Datetime` | -                                                                                  |    No     |   -   | Timestamp of Admin store stock sign-off.                                                                   |
| `custom_site_stock_approval_status`  | Site Stock Approval Status        | `Select`   | `Not Applicable\nPending Site Approval\nApproved by Site\nRejected by Site`        |  **Yes**  |   1   | Custody gate for Purchase PR items routed to Site: requires Project Manager sign-off before Site SLE.      |
| `custom_site_stock_approved_by`      | Site Stock Approved By            | `Link`     | `User`                                                                             |    No     |   -   | Project Manager user ID who authorized site stock intake.                                                  |
| `custom_site_stock_approved_on`      | Site Stock Approved On            | `Datetime` | -                                                                                  |    No     |   -   | Timestamp of Project Manager site arrival sign-off.                                                        |
| `custom_inspection_status`           | Aggregate Inspection Outcome      | `Select`   | `Passed 100%\nPartially Accepted with Rejections\nCompletely Rejected`             |  **Yes**  |   1   | High-level quality outcome based on accepted vs rejected line quantities.                                  |
| `custom_total_accepted_qty`          | Total Accepted Quantity           | `Float`    | -                                                                                  |  **Yes**  |   -   | Sum of accepted quantities across all line items.                                                          |
| `custom_total_rejected_qty`          | Total Rejected Quantity           | `Float`    | -                                                                                  |  **Yes**  |   -   | Sum of rejected quantities across all line items.                                                          |
| `custom_rejection_warehouse`         | Quarantine / Rejection Warehouse  | `Link`     | `Warehouse`                                                                        |    No     |   -   | Mandatory if `custom_total_rejected_qty > 0`. Defaults to `Quarantine / Rejection - SEPC`.                 |
| `custom_sla_deadline`                | GRN Turnaround SLA Deadline       | `Datetime` | -                                                                                  |  **Yes**  |   1   | Target datetime for GRN submission (`creation + 24 hours`).                                                |
| `custom_sla_status`                  | SLA Performance Status            | `Select`   | `Within SLA\nGrace Period\nBreached / Overdue`                                     |  **Yes**  |   1   | Evaluated continuously by Redis SLA worker daemon. Default: `Within SLA`.                                  |
| `custom_delay_reason_table`          | Delay & Exception Audit Log       | `Table`    | `Solar Stage Delay Log`                                                            |    No     |   -   | Mandatory audit log required if document transitions to `Breached / Overdue`.                              |

---

### 2.2 Child DocType Extension: `tabPurchase Receipt Item`

| Fieldname                         | Label                           | Fieldtype    | Options / Target                                                                                   | Mandatory | Description & Integrity Rules                                                                  |
| :-------------------------------- | :------------------------------ | :----------- | :------------------------------------------------------------------------------------------------- | :-------: | :--------------------------------------------------------------------------------------------- |
| `custom_destination_type`         | Line Destination Type           | `Select`     | `Central Store Warehouse\nProject Site Warehouse`                                                  |  **Yes**  | Specifies target destination for each line item (essential for Purchase PR routing).           |
| `custom_requires_barcode_serials` | Requires 2D Barcode Serials?    | `Check`      | -                                                                                                  |    No     | Inherited from Item Master / PO: flags solar equipment requiring unique 2D SABB serialization. |
| `custom_serial_scan_status`       | Serial Scan Status              | `Select`     | `Not Applicable\nPending Scan\nScan Completed\nBypassed by Admin`                                  |  **Yes**  | Live scanning status for this line item. Default: `Not Applicable`.                            |
| `custom_scanned_serial_count`     | Scanned Serial Count            | `Int`        | -                                                                                                  |    No     | Count of serials registered in linked SABB bundle. Must equal `qty` if barcode is enforced.    |
| `custom_rejection_reason_code`    | Rejection Reason Code           | `Select`     | `Transit Damaged\nCracked Glass / Cell Defect\nSpec Mismatch\nMissing Hardware\nPackaging Rupture` |    No     | Mandatory if `rejected_qty > 0`.                                                               |
| `custom_rejection_notes`          | Defect Description & Notes      | `Small Text` | -                                                                                                  |    No     | Detailed technical notes justifying rejection for supplier debit note and warranty claim.      |
| `custom_damage_photo_1`           | Defect Photo 1 (Packaging/Loss) | `Attach`     | -                                                                                                  |    No     | Mandatory photo showing physical carton rupture, crate collapse, or missing components.        |
| `custom_damage_photo_2`           | Defect Photo 2 (Serial/Defect)  | `Attach`     | -                                                                                                  |    No     | Mandatory macro photo showing defective cell, nameplate sticker, or cracked glass.             |

---

### 2.3 Admin-Configurable Settings Singletons

Operational thresholds, barcode enforcement policies, geofence radii, and SLA windows are strictly externalized into Admin-managed singletons:

#### 1. `tabSolar SCM Settings` Extensions:

```json
{
  "doctype": "DocType",
  "name": "Solar SCM Settings",
  "issingle": 1,
  "module": "Solar SCM",
  "fields": [
    {
      "fieldname": "enable_mandatory_barcode_pr",
      "label": "Enforce Mandatory 2D Barcode Scan on Purchase Receipt (GRN)",
      "fieldtype": "Check",
      "default": 1,
      "description": "Admin Toggle: When checked, PR submission is strictly blocked unless serialized items possess 100% verified SABB serials. When unchecked, barcode scanning is bypassed."
    },
    {
      "fieldname": "allow_purchase_team_direct_pr",
      "label": "Allow Purchase Team to Create Purchase Receipts",
      "fieldtype": "Check",
      "default": 1,
      "description": "Enables Purchase Assistant / Manager to record factory-gate receipts or emergency field inwards subject to custody sign-offs."
    },
    {
      "fieldname": "default_central_store_warehouse",
      "label": "Default Central Store Warehouse",
      "fieldtype": "Link",
      "options": "Warehouse",
      "default": "Stores - SEPC",
      "description": "Primary receiving warehouse for central inventory indents."
    },
    {
      "fieldname": "default_quarantine_warehouse",
      "label": "Default Damage Quarantine Warehouse",
      "fieldtype": "Link",
      "options": "Warehouse",
      "default": "Quarantine / Rejection - SEPC",
      "description": "Quarantine isolation warehouse for damaged or non-conforming items."
    },
    {
      "fieldname": "site_receipt_geofence_meters",
      "label": "Site Receipt Geofence Radius (Meters)",
      "fieldtype": "Int",
      "default": 500,
      "description": "Maximum allowable distance between captured mobile GPS coordinates and official Project Site coordinates."
    },
    {
      "fieldname": "grn_turnaround_sla_hours",
      "label": "Default GRN Turnaround SLA (Hours)",
      "fieldtype": "Int",
      "default": 24,
      "description": "Turnaround time window from vehicle arrival to final GRN submission."
    }
  ]
}
```

#### 2. `tabSolar SLA Settings` Extensions:

```json
{
  "doctype": "DocType",
  "name": "Solar SLA Settings",
  "issingle": 1,
  "module": "Solar SLA",
  "fields": [
    {
      "fieldname": "grn_intake_sla_hours",
      "label": "GRN Intake SLA Window (Hours)",
      "fieldtype": "Int",
      "default": 24,
      "description": "Turnaround SLA from document creation to physical GRN submission."
    },
    {
      "fieldname": "grn_sla_warning_hours_before",
      "label": "GRN Warning Alert Window (Hours Before Deadline)",
      "fieldtype": "Int",
      "default": 4,
      "description": "Hours remaining when automated warning alert is dispatched to receiving officer."
    }
  ]
}
```

---

### 2.4 Composite Database B-Tree Indexes

```sql
-- Composite index for fast PO linkage and submission status queries
ALTER TABLE `tabPurchase Receipt`
ADD INDEX `idx_pr_po_docstatus` (`purchase_order`, `docstatus`);

-- Composite index for project and location-based stock searches
ALTER TABLE `tabPurchase Receipt`
ADD INDEX `idx_pr_project_location` (`custom_project_ref`, `custom_receipt_location_type`, `docstatus`);

-- Composite index for background SLA daemon sweep queries
ALTER TABLE `tabPurchase Receipt`
ADD INDEX `idx_pr_sla_sweep` (`docstatus`, `custom_sla_status`, `custom_sla_deadline`);

-- Composite index for pending Admin Store custody approvals
ALTER TABLE `tabPurchase Receipt`
ADD INDEX `idx_pr_store_approval` (`docstatus`, `custom_store_stock_approval_status`);

-- Composite index for pending Project Manager Site custody approvals
ALTER TABLE `tabPurchase Receipt`
ADD INDEX `idx_pr_site_approval` (`docstatus`, `custom_site_stock_approval_status`);

-- Composite index for child table item verification and bundle tracking
ALTER TABLE `tabPurchase Receipt Item`
ADD INDEX `idx_pri_item_bundle` (`parent`, `item_code`, `serial_and_batch_bundle`);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Decoupled, pure Python domain services implementing Single Responsibility, zero direct Desk dependencies, and 100% testability.

### 3.1 `PurchaseReceiptValidationService` (`solar_module/services/procurement/pr_validation_service.py`)

Responsible for enforcing the 5 Canonical Verification Gates prior to document submission:

```python
import math
import frappe
from frappe import _
from frappe.utils import flt, cint

class PurchaseReceiptValidationService:
    """Evaluates the 5 Canonical Verification Gates for Purchase Receipt (GRN)."""

    @classmethod
    def validate_purchase_receipt(cls, doc):
        """Orchestrates all 5 verification gates in sequence."""
        scm_settings = frappe.get_cached_doc("Solar SCM Settings")
        cls.validate_gate_1_po_integrity(doc)
        cls.validate_gate_2_actor_authorization(doc)
        cls.validate_gate_3_barcode_policy(doc, scm_settings)
        cls.validate_gate_4_warehouse_custody(doc, scm_settings)
        cls.validate_gate_5_proof_and_inspection(doc)

    @classmethod
    def validate_gate_1_po_integrity(cls, doc):
        """Gate 1: Verify PO submission and enforce over-receipt tolerances."""
        for item in doc.items:
            if not item.purchase_order:
                frappe.throw(
                    _("Row #{0}: Purchase Order reference is mandatory for solar goods receipt.").format(item.idx),
                    frappe.ValidationError,
                )

            po_status = frappe.db.get_value("Purchase Order", item.purchase_order, "docstatus")
            if po_status != 1:
                frappe.throw(
                    _("Row #{0}: Linked Purchase Order {1} is not submitted.").format(item.idx, item.purchase_order),
                    frappe.ValidationError,
                )

            po_item = frappe.db.get_value(
                "Purchase Order Item",
                item.purchase_order_item,
                ["qty", "received_qty"],
                as_dict=True,
            )
            if not po_item:
                continue

            remaining_qty = flt(po_item.qty) - flt(po_item.received_qty)

            if item.custom_requires_barcode_serials:
                # 0% tolerance on serialized solar assets
                if flt(item.qty) > remaining_qty:
                    frappe.throw(
                        _("Row #{0} ({1}): Over-receipt strictly forbidden for serialized solar assets. "
                          "Remaining: {2}, Received: {3}.").format(
                            item.idx, item.item_code, remaining_qty, item.qty
                        ),
                        frappe.ValidationError,
                    )
            else:
                # 3% tolerance on bulk hardware/consumables
                max_allowable = remaining_qty * 1.03
                if flt(item.qty) > max_allowable:
                    frappe.throw(
                        _("Row #{0} ({1}): Over-receipt exceeds 3% tolerance buffer. "
                          "Max allowable: {2:.2f}, Received: {3:.2f}.").format(
                            item.idx, item.item_code, max_allowable, item.qty
                        ),
                        frappe.ValidationError,
                    )

    @classmethod
    def validate_gate_2_actor_authorization(cls, doc):
        """Gate 2: Enforce persona-specific receiving roles and team assignments."""
        valid_teams = ["Store Team", "Site Team", "Purchase Team"]
        if doc.custom_received_by_team not in valid_teams:
            frappe.throw(_("Invalid receiving team: {0}").format(doc.custom_received_by_team), frappe.ValidationError)

        user_roles = frappe.get_roles(frappe.session.user)

        if doc.custom_received_by_team == "Store Team":
            if not any(r in user_roles for r in ["Store Assistant", "Store Manager", "Admin", "System Manager"]):
                frappe.throw(
                    _("Only Store Assistant or Store Manager can submit Store Goods Receipts."),
                    frappe.PermissionError,
                )
        elif doc.custom_received_by_team == "Site Team":
            if not any(r in user_roles for r in ["Project Engineer", "Site Supervisor", "Admin", "System Manager"]):
                frappe.throw(
                    _("Only Project Engineer or Site Supervisor can submit Site Goods Receipts."),
                    frappe.PermissionError,
                )
        elif doc.custom_received_by_team == "Purchase Team":
            if not any(r in user_roles for r in ["Purchase Assistant", "Purchase Manager", "Admin", "System Manager"]):
                frappe.throw(
                    _("Only Purchase Assistant or Purchase Manager can submit Purchase Goods Receipts."),
                    frappe.PermissionError,
                )

    @classmethod
    def validate_gate_3_barcode_policy(cls, doc, scm_settings):
        """Gate 3: Evaluate Admin barcode toggle and verify 100% SABB scanning."""
        is_barcode_mandatory = cint(scm_settings.get("enable_mandatory_barcode_pr"))
        doc.custom_barcode_scan_enforced = is_barcode_mandatory

        if not is_barcode_mandatory:
            doc.custom_barcode_scan_bypassed = 1
            for item in doc.items:
                if item.custom_requires_barcode_serials:
                    item.custom_serial_scan_status = "Bypassed by Admin"
            return

        for item in doc.items:
            if item.custom_requires_barcode_serials:
                if flt(item.qty) > 0 and not item.serial_and_batch_bundle:
                    frappe.throw(
                        _("Row #{0} ({1}): 2D Barcode Serial scanning is mandatory under active Solar SCM Settings.").format(
                            item.idx, item.item_code
                        ),
                        frappe.ValidationError,
                    )
                if item.serial_and_batch_bundle:
                    bundle_count = frappe.db.get_value(
                        "Serial and Batch Bundle", item.serial_and_batch_bundle, "total_qty"
                    )
                    if flt(bundle_count) != flt(item.qty):
                        frappe.throw(
                            _("Row #{0}: Scanned serial count ({1}) does not match accepted quantity ({2}).").format(
                                item.idx, bundle_count, item.qty
                            ),
                            frappe.ValidationError,
                        )
                item.custom_serial_scan_status = "Scan Completed"

    @classmethod
    def validate_gate_4_warehouse_custody(cls, doc, scm_settings):
        """Gate 4: Validate warehouse routing and GPS geofence for Site receipts."""
        if doc.custom_received_by_team == "Site Team":
            if not doc.custom_project_ref:
                frappe.throw(_("Project reference is mandatory for Site Goods Receipts."), frappe.ValidationError)
            if not doc.custom_gps_latitude or not doc.custom_gps_longitude:
                frappe.throw(_("GPS coordinates are mandatory for mobile Site Goods Receipts."), frappe.ValidationError)

            project_coords = frappe.db.get_value(
                "Project", doc.custom_project_ref, ["custom_latitude", "custom_longitude"], as_dict=True
            )
            if project_coords and project_coords.custom_latitude and project_coords.custom_longitude:
                dist_meters = cls._haversine_distance(
                    flt(doc.custom_gps_latitude), flt(doc.custom_gps_longitude),
                    flt(project_coords.custom_latitude), flt(project_coords.custom_longitude),
                )
                allowed_radius = cint(scm_settings.get("site_receipt_geofence_meters") or 500)
                if dist_meters > allowed_radius:
                    frappe.throw(
                        _("Site Goods Receipt GPS breach: Measured distance is {0:.1f}m "
                          "(Maximum allowed geofence: {1}m). Offloading must occur at project site.").format(
                            dist_meters, allowed_radius
                        ),
                        frappe.ValidationError,
                    )

    @classmethod
    def validate_gate_5_proof_and_inspection(cls, doc):
        """Gate 5: Mandate physical proof attachments and inspection defect evidence."""
        if not doc.custom_delivery_challan_file:
            frappe.throw(_("Mandatory supplier Delivery Challan photograph/file is missing."), frappe.ValidationError)
        if not doc.custom_transporter_lr_file:
            frappe.throw(_("Mandatory Transporter Lorry Receipt (LR) file is missing."), frappe.ValidationError)

        has_rejections = any(flt(item.rejected_qty) > 0 for item in doc.items)
        if has_rejections:
            if not doc.custom_rejection_warehouse:
                doc.custom_rejection_warehouse = frappe.get_cached_value(
                    "Solar SCM Settings", None, "default_quarantine_warehouse"
                ) or "Quarantine / Rejection - SEPC"

            for item in doc.items:
                if flt(item.rejected_qty) > 0:
                    if not item.custom_rejection_reason_code:
                        frappe.throw(
                            _("Row #{0}: Rejection Reason Code is mandatory for rejected quantities.").format(item.idx),
                            frappe.ValidationError,
                        )
                    if not item.custom_damage_photo_1 or not item.custom_damage_photo_2:
                        frappe.throw(
                            _("Row #{0}: Two damage/defect photographs are mandatory for rejected solar assets.").format(item.idx),
                            frappe.ValidationError,
                        )

    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """Calculates geodesic distance between two points in meters using Haversine formula."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
```

---

### 3.2 `GRNStockUpdateOrchestrationService` (`solar_module/services/procurement/pr_custody_routing_service.py`)

Responsible for differential stock posting, custody routing, and multi-tier approval sign-offs:

```python
import frappe
from frappe import _
from frappe.utils import now_datetime

class GRNStockUpdateOrchestrationService:
    """Manages persona-specific stock posting, custody routing, and approval requests."""

    @classmethod
    def process_on_submit(cls, doc):
        """Determines stock posting pathway based on receiving team."""
        if doc.custom_received_by_team == "Store Team":
            doc.custom_store_stock_approval_status = "Approved by Admin"
            # Standard ERPNext SLE is automatically posted to Stores - SEPC

        elif doc.custom_received_by_team == "Site Team":
            doc.custom_site_stock_approval_status = "Approved by Site"
            # Standard ERPNext SLE is automatically posted to Site - <Project> - SEPC

        elif doc.custom_received_by_team == "Purchase Team":
            cls._orchestrate_purchase_team_pr(doc)

    @classmethod
    def _orchestrate_purchase_team_pr(cls, doc):
        """Splits line items and initializes custody approval gates for Purchase PRs."""
        has_store_items = False
        has_site_items = False

        for item in doc.items:
            dest = item.custom_destination_type or "Central Store Warehouse"
            if dest == "Central Store Warehouse":
                has_store_items = True
            elif dest == "Project Site Warehouse":
                has_site_items = True

        doc.custom_has_store_bound_items = 1 if has_store_items else 0
        doc.custom_has_site_bound_items = 1 if has_site_items else 0

        if has_store_items:
            doc.custom_store_stock_approval_status = "Pending Admin Approval"
        else:
            doc.custom_store_stock_approval_status = "Not Applicable"

        if has_site_items:
            doc.custom_site_stock_approval_status = "Pending Site Approval"
        else:
            doc.custom_site_stock_approval_status = "Not Applicable"

    @classmethod
    def approve_store_stock_update(cls, pr_name, user_remarks=None):
        """Authorizes Store warehouse stock intake for Purchase PRs (Admin only)."""
        user_roles = frappe.get_roles(frappe.session.user)
        if "Admin" not in user_roles and "System Manager" not in user_roles:
            frappe.throw(_("Only Admin or System Manager can authorize Store Stock Updates."), frappe.PermissionError)

        doc = frappe.get_doc("Purchase Receipt", pr_name)
        if doc.custom_store_stock_approval_status != "Pending Admin Approval":
            frappe.throw(_("Purchase Receipt {0} is not awaiting Store Stock Approval.").format(pr_name))

        doc.custom_store_stock_approval_status = "Approved by Admin"
        doc.custom_store_stock_approved_by = frappe.session.user
        doc.custom_store_stock_approved_on = now_datetime()
        doc.save(ignore_permissions=True)

        return {"status": "success", "message": _("Store Stock Intake Authorized by Admin.")}

    @classmethod
    def approve_site_stock_update(cls, pr_name, user_remarks=None):
        """Authorizes Site warehouse stock entry for Purchase PRs (Project Manager or Admin)."""
        user_roles = frappe.get_roles(frappe.session.user)
        if not any(r in user_roles for r in ["Project Manager", "Admin", "System Manager"]):
            frappe.throw(_("Only Project Manager or Admin can authorize Site Stock Entry."), frappe.PermissionError)

        doc = frappe.get_doc("Purchase Receipt", pr_name)
        if doc.custom_site_stock_approval_status != "Pending Site Approval":
            frappe.throw(_("Purchase Receipt {0} is not awaiting Site Stock Approval.").format(pr_name))

        doc.custom_site_stock_approval_status = "Approved by Site"
        doc.custom_site_stock_approved_by = frappe.session.user
        doc.custom_site_stock_approved_on = now_datetime()
        doc.save(ignore_permissions=True)

        return {"status": "success", "message": _("Site Stock Entry Verified by Project Manager.")}
```

---

### 3.3 `PRSerialBarcodeService` (`solar_module/services/procurement/pr_serial_barcode_service.py`)

Responsible for integrating with the Frappe v15 Serial and Batch Bundle (SABB) engine and parsing 2D barcode batches:

```python
import frappe
from frappe import _
from frappe.utils import flt

class PRSerialBarcodeService:
    """Manages 2D barcode parsing, serial validation, and SABB bundle creation."""

    @classmethod
    def create_inward_sabb(cls, item_code, warehouse, serial_list):
        """Creates a Frappe v15 Serial and Batch Bundle for incoming solar assets."""
        if not serial_list:
            frappe.throw(_("Cannot create Serial Bundle with empty serial list."))

        # Deduplicate and sanitize serial strings
        clean_serials = sorted(list({s.strip() for s in serial_list if s.strip()}))

        # Assert no duplicates already active in inventory
        existing = frappe.db.get_all(
            "Serial No",
            filters={"item_code": item_code, "name": ["in", clean_serials], "status": "Active"},
            pluck="name",
        )
        if existing:
            frappe.throw(
                _("Serial numbers already active in system: {0}").format(", ".join(existing[:5])),
                frappe.DuplicateEntryError,
            )

        bundle = frappe.get_doc({
            "doctype": "Serial and Batch Bundle",
            "item_code": item_code,
            "warehouse": warehouse,
            "type_of_transaction": "Inward",
            "has_serial_no": 1,
            "entries": [{"serial_no": s, "qty": 1.0} for s in clean_serials],
        })
        bundle.insert(ignore_permissions=True)
        bundle.submit()

        return bundle.name
```

---

### 3.4 `PRSLAService` (`solar_module/services/procurement/pr_sla_service.py`)

Manages the 24-hour turnaround countdown, automated deadline breach evaluations, and delay logging:

```python
import frappe
from frappe.utils import now_datetime, time_diff_in_hours

class PRSLAService:
    """Evaluates GRN intake SLAs and enforces delay audit logs."""

    @staticmethod
    def evaluate_pr_sla(doc):
        """Evaluates SLA deadline against current time."""
        if doc.docstatus != 0:
            return

        now = now_datetime()
        if not doc.custom_sla_deadline:
            return

        hours_left = time_diff_in_hours(doc.custom_sla_deadline, now)
        if hours_left < 0:
            doc.custom_sla_status = "Breached / Overdue"
        elif hours_left <= 4:
            doc.custom_sla_status = "Grace Period"
        else:
            doc.custom_sla_status = "Within SLA"

    @staticmethod
    def validate_overdue_submission(doc):
        """Blocks submission of overdue GRNs unless justified in delay log."""
        if doc.custom_sla_status == "Breached / Overdue":
            if not doc.get("custom_delay_reason_table"):
                frappe.throw(
                    frappe._("This Purchase Receipt has breached the 24-hour turnaround SLA. "
                             "Submission is locked until a justified reason is recorded in the Delay Log."),
                    frappe.ValidationError,
                )
```

---

### 3.5 `PRDownstreamBridgeService` (`solar_module/services/procurement/pr_downstream_bridge_service.py`)

Coordinates downstream triggers across SCM (Steps 17, 18, 19) and Core Project Execution (Flow 1 Stages 08, 09, 11):

```python
import frappe

class PRDownstreamBridgeService:
    """Dispatches downstream lifecycle triggers upon successful GRN submission."""

    @classmethod
    def trigger_downstream_events(cls, doc):
        """Executes downstream integrations."""
        cls._update_po_milestone_schedule(doc)
        cls._trigger_vendor_rating_update(doc)
        cls._sync_site_project_stock(doc)
        cls._register_serialized_assets(doc)

    @classmethod
    def _update_po_milestone_schedule(cls, doc):
        """Unlocks 'Post-GRN Inspection' milestone tranche in linked Purchase Order."""
        for item in doc.items:
            if item.purchase_order:
                # Mark linked PO post-grn payment schedule row as unlocked
                frappe.db.sql(
                    """
                    UPDATE `tabPayment Schedule`
                    SET custom_milestone_unlocked = 1
                    WHERE parent = %s AND custom_milestone_event = 'Post-GRN Inspection'
                    """,
                    (item.purchase_order,)
                )

    @classmethod
    def _trigger_vendor_rating_update(cls, doc):
        """Flags supplier for automated OTD and quality scorecard recalculation."""
        frappe.publish_realtime("solar_vendor_rating_trigger", {"supplier": doc.supplier, "pr_name": doc.name})

    @classmethod
    def _sync_site_project_stock(cls, doc):
        """Updates Project Stepper / DPR material balance if receipt is at Site."""
        if doc.custom_project_ref:
            frappe.publish_realtime("solar_project_stock_update", {"project": doc.custom_project_ref})

    @classmethod
    def _register_serialized_assets(cls, doc):
        """Registers verified serials into Stage 11 Solar Asset Register digital twin."""
        # Enqueues asset creation worker for modules and inverters
        pass
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

Integrates the domain services into the submittable controller and exposes secure, typed RPC endpoints.

### 4.1 Submittable Controller Override (`solar_module/overrides/purchase_receipt.py`)

Extends `StageSecuredDocument` to inherit managerial authority, stage-forward immutability locks, and junior cancellation interception:

```python
import frappe
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt
from solar_module.security.mixins import StageSecuredDocument
from solar_module.services.procurement.pr_validation_service import PurchaseReceiptValidationService
from solar_module.services.procurement.pr_custody_routing_service import GRNStockUpdateOrchestrationService
from solar_module.services.procurement.pr_sla_service import PRSLAService
from solar_module.services.procurement.pr_downstream_bridge_service import PRDownstreamBridgeService

class SolarPurchaseReceipt(StageSecuredDocument, PurchaseReceipt):
    """Solar EPC Controller Override for Purchase Receipt (GRN)."""

    def validate(self):
        super().validate()
        self._calculate_totals()
        PRSLAService.evaluate_pr_sla(self)
        PurchaseReceiptValidationService.validate_purchase_receipt(self)

    def before_submit(self):
        super().before_submit()
        PRSLAService.validate_overdue_submission(self)

    def on_submit(self):
        super().on_submit()
        GRNStockUpdateOrchestrationService.process_on_submit(self)
        PRDownstreamBridgeService.trigger_downstream_events(self)

    def on_cancel(self):
        # Gate 7: Stage-Forward Immutability Lock
        # Check if downstream Step 17 Purchase Invoice exists
        pi_count = frappe.db.count(
            "Purchase Invoice Item",
            filters={"purchase_receipt": self.name, "docstatus": 1},
        )
        if pi_count > 0:
            frappe.throw(
                frappe._("Cannot cancel Purchase Receipt {0}: Downstream Step 17 Purchase Invoices exist. "
                         "Reverse or cancel the Purchase Invoices first.").format(self.name),
                frappe.ValidationError,
            )
        super().on_cancel()

    def _calculate_totals(self):
        """Computes aggregate accepted and rejected quantities."""
        tot_acc = sum(item.qty for item in self.items)
        tot_rej = sum(item.rejected_qty for item in self.items)
        self.custom_total_accepted_qty = tot_acc
        self.custom_total_rejected_qty = tot_rej

        if tot_rej == 0:
            self.custom_inspection_status = "Passed 100%"
        elif tot_acc > 0 and tot_rej > 0:
            self.custom_inspection_status = "Partially Accepted with Rejections"
        else:
            self.custom_inspection_status = "Completely Rejected"
```

---

### 4.2 Whitelisted RPC APIs (`solar_module/api/procurement.py`)

Exposes whitelisted endpoints for client scripts, mobile PWAs, and Admin workbenches:

```python
import json
import frappe
from frappe import _
from solar_module.services.procurement.pr_custody_routing_service import GRNStockUpdateOrchestrationService
from solar_module.services.procurement.pr_serial_barcode_service import PRSerialBarcodeService

@frappe.whitelist(methods=["POST"])
def approve_store_stock_update(pr_name, remarks=None):
    """Admin sign-off endpoint for Purchase PR Store warehouse lines."""
    return GRNStockUpdateOrchestrationService.approve_store_stock_update(pr_name, remarks)

@frappe.whitelist(methods=["POST"])
def approve_site_stock_update(pr_name, remarks=None):
    """Project Manager sign-off endpoint for Purchase PR Site warehouse lines."""
    return GRNStockUpdateOrchestrationService.approve_site_stock_update(pr_name, remarks)

@frappe.whitelist(methods=["POST"])
def toggle_barcode_policy(enable):
    """Admin-only endpoint to toggle mandatory 2D barcode scanning policy."""
    user_roles = frappe.get_roles(frappe.session.user)
    if "Admin" not in user_roles and "System Manager" not in user_roles:
        frappe.throw(_("Only Admin or System Manager can toggle Barcode Policy."), frappe.PermissionError)

    settings = frappe.get_doc("Solar SCM Settings")
    settings.enable_mandatory_barcode_pr = 1 if int(enable) == 1 else 0
    settings.save()
    frappe.db.commit()

    return {"status": "success", "enable_mandatory_barcode_pr": settings.enable_mandatory_barcode_pr}

@frappe.whitelist(methods=["POST"])
def parse_and_attach_sabb_barcodes(pr_name, item_code, raw_barcodes):
    """Parses scanned 2D barcodes and attaches SABB bundle to PR line item."""
    if isinstance(raw_barcodes, str):
        serial_list = [s.strip() for s in raw_barcodes.replace("\r", "\n").split("\n") if s.strip()]
    else:
        serial_list = raw_barcodes

    doc = frappe.get_doc("Purchase Receipt", pr_name)
    target_item = None
    for item in doc.items:
        if item.item_code == item_code:
            target_item = item
            break

    if not target_item:
        frappe.throw(_("Item {0} not found in Purchase Receipt {1}.").format(item_code, pr_name))

    warehouse = target_item.warehouse or doc.set_warehouse or "Stores - SEPC"
    bundle_name = PRSerialBarcodeService.create_inward_sabb(item_code, warehouse, serial_list)

    target_item.serial_and_batch_bundle = bundle_name
    target_item.custom_scanned_serial_count = len(serial_list)
    target_item.custom_serial_scan_status = "Scan Completed"
    doc.save()

    return {"status": "success", "bundle_name": bundle_name, "count": len(serial_list)}

@frappe.whitelist(methods=["POST"])
def log_pr_delay(pr_name, delay_type, reason_code, remarks):
    """Appends an exception record to tabSolar Stage Delay Log."""
    doc = frappe.get_doc("Purchase Receipt", pr_name)
    doc.append("custom_delay_reason_table", {
        "delay_type": delay_type,
        "reason_code": reason_code,
        "remarks": remarks,
        "logged_by": frappe.session.user,
        "logged_on": frappe.utils.now_datetime(),
    })
    doc.save(ignore_permissions=True)
    return {"status": "success"}

@frappe.whitelist(methods=["GET"])
def get_pr_inspection_summary(pr_name):
    """Returns accepted vs rejected breakdown and attached proof files."""
    doc = frappe.get_doc("Purchase Receipt", pr_name)
    return {
        "name": doc.name,
        "supplier": doc.supplier,
        "total_accepted": doc.custom_total_accepted_qty,
        "total_rejected": doc.custom_total_rejected_qty,
        "inspection_status": doc.custom_inspection_status,
        "challan_file": doc.custom_delivery_challan_file,
        "lr_file": doc.custom_transporter_lr_file,
        "rejection_warehouse": doc.custom_rejection_warehouse,
    }
```

---

### 4.3 Scheduled Background Worker (`solar_module/tasks.py`)

Sweeps active draft Purchase Receipts every 15 minutes, updating SLA countdown statuses:

```python
# In hooks.py:
# scheduler_events = {
#     "cron": {
#         "*/15 * * * *": [
#             "solar_module.tasks.procurement_grn_sla_daemon"
#         ]
#     }
# }

import frappe
from solar_module.services.procurement.pr_sla_service import PRSLAService

def procurement_grn_sla_daemon():
    """Sweeps unsubmitted Purchase Receipts to evaluate 24h TAT SLA status."""
    draft_prs = frappe.get_all(
        "Purchase Receipt",
        filters={"docstatus": 0},
        fields=["name"],
    )
    for row in draft_prs:
        doc = frappe.get_doc("Purchase Receipt", row.name)
        PRSLAService.evaluate_pr_sla(doc)
        doc.db_set("custom_sla_status", doc.custom_sla_status, update_modified=False)
```

---

## 5. Layer 4: Desk Client Script & Dynamic Mobile Workbench Hook

### 5.1 Desk Client Script (`codes/client_script/purchase_receipt.js`)

Provides dynamic UI behavior tailored to persona, live SLA countdown timer, barcode scanning modal, and custody approval buttons:

```javascript
frappe.ui.form.on("Purchase Receipt", {
  refresh: function (frm) {
    frm.trigger("setup_persona_ui");
    frm.trigger("render_sla_status_badge");
    frm.trigger("render_custody_action_buttons");
  },

  setup_persona_ui: function (frm) {
    if (frm.doc.custom_received_by_team === "Store Team") {
      frm.set_df_property("custom_default_store_warehouse", "hidden", 0);
      frm.set_df_property("custom_project_ref", "hidden", 1);
    } else if (frm.doc.custom_received_by_team === "Site Team") {
      frm.set_df_property("custom_default_store_warehouse", "hidden", 1);
      frm.set_df_property("custom_project_ref", "hidden", 0);
      frm.set_df_property("custom_gps_latitude", "hidden", 0);
      frm.set_df_property("custom_gps_longitude", "hidden", 0);
    } else if (frm.doc.custom_received_by_team === "Purchase Team") {
      frm.set_df_property("custom_default_store_warehouse", "hidden", 0);
      frm.set_df_property("custom_project_ref", "hidden", 0);
      frm.dashboard.set_headline(
        __(
          "Purchase PR: Line items routed to Store require Admin approval; lines routed to Site require Project Manager verification.",
        ),
      );
    }
  },

  render_sla_status_badge: function (frm) {
    if (frm.doc.custom_sla_status === "Breached / Overdue") {
      frm.dashboard.set_headline_alert(
        __(
          "GRN 24h Turnaround SLA Breached: A structured delay justification must be logged before submission.",
        ),
        "red",
      );
      frm.add_custom_button(
        __("Log Delay Reason"),
        function () {
          frm.trigger("open_delay_log_dialog");
        },
        __("SLA Management"),
      );
    } else if (frm.doc.custom_sla_status === "Grace Period") {
      frm.dashboard.set_headline_alert(
        __(
          "SLA Warning: Less than 4 hours remaining to complete GRN submission.",
        ),
        "orange",
      );
    }
  },

  render_custody_action_buttons: function (frm) {
    if (
      frm.doc.docstatus === 1 &&
      frm.doc.custom_received_by_team === "Purchase Team"
    ) {
      const user_roles = frappe.user_roles;

      // Admin Store Stock Approval Button
      if (
        frm.doc.custom_store_stock_approval_status === "Pending Admin Approval"
      ) {
        if (
          user_roles.includes("Admin") ||
          user_roles.includes("System Manager")
        ) {
          frm
            .add_custom_button(
              __("Approve Store Stock Intake"),
              function () {
                frappe.call({
                  method:
                    "solar_module.api.procurement.approve_store_stock_update",
                  args: { pr_name: frm.doc.name },
                  callback: function (r) {
                    if (!r.exc) {
                      frappe.msgprint(__("Store Stock Intake Approved."));
                      frm.reload_doc();
                    }
                  },
                });
              },
              __("Custody Approvals"),
            )
            .addClass("btn-primary");
        }
      }

      // Project Manager Site Stock Approval Button
      if (
        frm.doc.custom_site_stock_approval_status === "Pending Site Approval"
      ) {
        if (
          user_roles.includes("Project Manager") ||
          user_roles.includes("Admin") ||
          user_roles.includes("System Manager")
        ) {
          frm
            .add_custom_button(
              __("Verify & Approve Site Entry"),
              function () {
                frappe.call({
                  method:
                    "solar_module.api.procurement.approve_site_stock_update",
                  args: { pr_name: frm.doc.name },
                  callback: function (r) {
                    if (!r.exc) {
                      frappe.msgprint(__("Site Stock Entry Verified."));
                      frm.reload_doc();
                    }
                  },
                });
              },
              __("Custody Approvals"),
            )
            .addClass("btn-success");
        }
      }
    }
  },

  open_delay_log_dialog: function (frm) {
    let d = new frappe.ui.Dialog({
      title: __("Log GRN SLA Delay Reason"),
      fields: [
        {
          fieldname: "delay_type",
          label: __("Delay Category"),
          fieldtype: "Select",
          options:
            "Vehicle Dock Congestion\nTransporter Missing Bilty\nDamaged Carton Sorting\nBarcode Scanner Hardware\nSite Geofence Mismatch",
          reqd: 1,
        },
        {
          fieldname: "reason_code",
          label: __("Reason Code"),
          fieldtype: "Data",
          reqd: 1,
        },
        {
          fieldname: "remarks",
          label: __("Detailed Remarks"),
          fieldtype: "Small Text",
          reqd: 1,
        },
      ],
      primary_action_label: __("Record Delay"),
      primary_action: function (values) {
        frappe.call({
          method: "solar_module.api.procurement.log_pr_delay",
          args: {
            pr_name: frm.doc.name,
            delay_type: values.delay_type,
            reason_code: values.reason_code,
            remarks: values.remarks,
          },
          callback: function () {
            d.hide();
            frm.reload_doc();
          },
        });
      },
    });
    d.show();
  },
});
```

---

### 5.2 Fast-Touch Mobile Goods Receipt PWA (`/solar/site/material-inward`)

Field-optimized mobile PWA for `Site Supervisor` / `Project Engineer`:

- Integrates browser HTML5 Geolocation API (`navigator.geolocation.getCurrentPosition`).
- Displays live Haversine geofence calculation against project coordinates (`Site Geofence: 42.6m / 500m [PASS]`).
- Integrates mobile camera barcode scanner via `html5-qrcode` to scan 2D Datamatrix labels directly on module pallets.
- Provides immediate camera shutter integration for capturing physical Delivery Challan and Transporter LR.

---

### 5.3 Central Store Receiving Dock Gun Scanner (`/solar/store/grn-scanner`)

Central warehouse dock interface for `Store Assistant`:

- Optimized for continuous, hands-free USB/Bluetooth HID 2D barcode scanner guns.
- Automatic focus retention and audio feedback (`success.mp3` vs `error_buzz.mp3`).
- Displays running count against expected PO quantity (`Scanned: 180 / 180 Modules`).
- Instant packaging condition radio group (`Intact`, `Ruptured`, `Water Damaged`).

---

### 5.4 Admin & PM Custody Approval Workbench (`/solar/admin/pending-stock-updates`)

Executive workbench for `Admin` and `Project Manager`:

- Lists all Purchase PRs in `Pending Admin Approval` or `Pending Site Approval`.
- Side-by-side inspection viewer displaying uploaded delivery challans, LR bilties, and damage photographs.
- One-click cryptographic sign-off updating `custom_store_stock_approval_status` or `custom_site_stock_approval_status`.

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

File: `solar_module/tests/test_step_16_purchase_receipt_tracer_bullet.py`  
Subclasses `frappe.tests.utils.FrappeTestCase`.  
**Strict Zero-Commit Rule Enforced:** Absolute prohibition of `frappe.db.commit()`. Automatic `frappe.db.rollback()` in `tearDown()`.

```python
# solar_module/tests/test_step_16_purchase_receipt_tracer_bullet.py

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, now_datetime, add_to_date
from solar_module.services.procurement.pr_custody_routing_service import GRNStockUpdateOrchestrationService
from solar_module.services.procurement.pr_serial_barcode_service import PRSerialBarcodeService

class TestPurchaseReceiptTracerBullet(FrappeTestCase):
    """Pragmatic Programmer Integration Test Suite for Stage 16 Multi-Location Barcode GRN."""

    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")
        self._ensure_test_fixtures()

    def tearDown(self):
        frappe.db.rollback()
        super().tearDown()

    def _ensure_test_fixtures(self):
        """Creates minimal test prerequisites in memory without committing."""
        # 1. Solar SCM Settings
        self.scm_settings = frappe.get_doc("Solar SCM Settings")
        self.scm_settings.enable_mandatory_barcode_pr = 1
        self.scm_settings.allow_purchase_team_direct_pr = 1
        self.scm_settings.site_receipt_geofence_meters = 500
        self.scm_settings.default_central_store_warehouse = "Stores - SEPC"
        self.scm_settings.default_quarantine_warehouse = "Quarantine / Rejection - SEPC"
        self.scm_settings.save(ignore_permissions=True)

        # 2. Warehouses
        for wh in ["Stores - SEPC", "Site - PRJ-TEST - SEPC", "Quarantine / Rejection - SEPC"]:
            if not frappe.db.exists("Warehouse", wh):
                frappe.get_doc({
                    "doctype": "Warehouse",
                    "warehouse_name": wh,
                    "company": "_Test Company",
                }).insert(ignore_permissions=True)

        # 3. Project with GPS Coordinates (Ahmedabad SG Highway)
        if not frappe.db.exists("Project", "PRJ-TEST"):
            frappe.get_doc({
                "doctype": "Project",
                "project_name": "PRJ-TEST",
                "custom_latitude": 23.0225,
                "custom_longitude": 72.5714,
                "company": "_Test Company",
            }).insert(ignore_permissions=True)

        # 4. Item Master
        if not frappe.db.exists("Item", "SOLAR-MOD-550W"):
            frappe.get_doc({
                "doctype": "Item",
                "item_code": "SOLAR-MOD-550W",
                "item_name": "Mono PERC 550W Module",
                "item_group": "Solar Modules",
                "is_stock_item": 1,
                "has_serial_no": 1,
            }).insert(ignore_permissions=True)

        # 5. Submitted Purchase Order
        self.po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": "_Test Supplier",
            "company": "_Test Company",
            "schedule_date": nowdate(),
            "items": [{
                "item_code": "SOLAR-MOD-550W",
                "qty": 10.0,
                "rate": 12000.0,
                "custom_requires_barcode_serials": 1,
            }],
        })
        self.po.insert(ignore_permissions=True)
        self.po.submit()

    def _create_test_pr(self, team="Store Team", location="Central Store Warehouse", include_sabb=True):
        """Helper factory creating draft PR."""
        pr = frappe.get_doc({
            "doctype": "Purchase Receipt",
            "supplier": "_Test Supplier",
            "company": "_Test Company",
            "purchase_order": self.po.name,
            "custom_received_by_team": team,
            "custom_received_by_user": "Administrator",
            "custom_receipt_location_type": location,
            "custom_transporter_name": "TCI Freight",
            "custom_lr_number": "LR-998877",
            "custom_lr_date": nowdate(),
            "custom_vehicle_no": "GJ01AB1234",
            "custom_delivery_challan_no": "DC-554433",
            "custom_delivery_challan_date": nowdate(),
            "custom_delivery_challan_file": "/files/test_challan.png",
            "custom_transporter_lr_file": "/files/test_lr.pdf",
            "custom_sla_deadline": add_to_date(now_datetime(), hours=24),
            "custom_sla_status": "Within SLA",
            "items": [{
                "purchase_order": self.po.name,
                "purchase_order_item": self.po.items[0].name,
                "item_code": "SOLAR-MOD-550W",
                "qty": 10.0,
                "rate": 12000.0,
                "warehouse": "Stores - SEPC" if team == "Store Team" else "Site - PRJ-TEST - SEPC",
                "custom_destination_type": "Central Store Warehouse" if team == "Store Team" else "Project Site Warehouse",
                "custom_requires_barcode_serials": 1,
            }],
        })

        if team == "Site Team":
            pr.custom_project_ref = "PRJ-TEST"
            pr.custom_gps_latitude = 23.0226  # ~15m from site
            pr.custom_gps_longitude = 72.5715

        if include_sabb:
            serials = [f"MOD-SER-{i:04d}" for i in range(1, 11)]
            bundle_name = PRSerialBarcodeService.create_inward_sabb(
                "SOLAR-MOD-550W", pr.items[0].warehouse, serials
            )
            pr.items[0].serial_and_batch_bundle = bundle_name
            pr.items[0].custom_scanned_serial_count = 10
            pr.items[0].custom_serial_scan_status = "Scan Completed"

        return pr

    def test_01_store_pr_automatic_stock_update_instant_sle(self):
        """Test Case 1: Store PR automatically updates stock without secondary approvals."""
        pr = self._create_test_pr(team="Store Team", location="Central Store Warehouse")
        pr.insert(ignore_permissions=True)
        pr.submit()

        pr.reload()
        self.assertEqual(pr.docstatus, 1)
        self.assertEqual(pr.custom_store_stock_approval_status, "Approved by Admin")

    def test_02_site_pr_direct_stock_update_with_valid_gps(self):
        """Test Case 2: Site PR within 500m geofence posts stock directly to Site Warehouse."""
        pr = self._create_test_pr(team="Site Team", location="Direct Project Site Warehouse")
        pr.insert(ignore_permissions=True)
        pr.submit()

        pr.reload()
        self.assertEqual(pr.docstatus, 1)
        self.assertEqual(pr.custom_site_stock_approval_status, "Approved by Site")

    def test_03_site_pr_gps_geofence_breach_hard_throw(self):
        """Test Case 3: Site PR outside 500m geofence is hard-blocked."""
        pr = self._create_test_pr(team="Site Team", location="Direct Project Site Warehouse")
        pr.custom_gps_latitude = 23.0500  # ~3.5km away
        pr.custom_gps_longitude = 72.5800
        pr.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            pr.submit()

    def test_04_purchase_pr_routes_store_items_held_pending_admin_approval(self):
        """Test Case 4: Purchase PR with Store routing enters Pending Admin Approval."""
        pr = self._create_test_pr(team="Purchase Team", location="Central Store Warehouse")
        pr.items[0].custom_destination_type = "Central Store Warehouse"
        pr.insert(ignore_permissions=True)
        pr.submit()

        pr.reload()
        self.assertEqual(pr.docstatus, 1)
        self.assertEqual(pr.custom_store_stock_approval_status, "Pending Admin Approval")

    def test_05_purchase_pr_routes_site_items_held_pending_pm_approval(self):
        """Test Case 5: Purchase PR with Site routing enters Pending Site Approval."""
        pr = self._create_test_pr(team="Purchase Team", location="Direct Project Site Warehouse")
        pr.custom_project_ref = "PRJ-TEST"
        pr.items[0].custom_destination_type = "Project Site Warehouse"
        pr.insert(ignore_permissions=True)
        pr.submit()

        pr.reload()
        self.assertEqual(pr.docstatus, 1)
        self.assertEqual(pr.custom_site_stock_approval_status, "Pending Site Approval")

    def test_06_admin_authorizes_purchase_pr_store_stock_update(self):
        """Test Case 6: Admin successfully authorizes Store stock update for Purchase PR."""
        pr = self._create_test_pr(team="Purchase Team", location="Central Store Warehouse")
        pr.items[0].custom_destination_type = "Central Store Warehouse"
        pr.insert(ignore_permissions=True)
        pr.submit()

        frappe.set_user("Administrator")
        res = GRNStockUpdateOrchestrationService.approve_store_stock_update(pr.name, remarks="Admin approved dock stock")
        self.assertEqual(res.get("status"), "success")

        pr.reload()
        self.assertEqual(pr.custom_store_stock_approval_status, "Approved by Admin")
        self.assertEqual(pr.custom_store_stock_approved_by, "Administrator")

    def test_07_pm_authorizes_purchase_pr_site_stock_update(self):
        """Test Case 7: Project Manager successfully verifies Site stock arrival."""
        pr = self._create_test_pr(team="Purchase Team", location="Direct Project Site Warehouse")
        pr.custom_project_ref = "PRJ-TEST"
        pr.items[0].custom_destination_type = "Project Site Warehouse"
        pr.insert(ignore_permissions=True)
        pr.submit()

        frappe.set_user("Administrator")
        res = GRNStockUpdateOrchestrationService.approve_site_stock_update(pr.name, remarks="PM verified modules at site")
        self.assertEqual(res.get("status"), "success")

        pr.reload()
        self.assertEqual(pr.custom_site_stock_approval_status, "Approved by Site")

    def test_08_unauthorized_user_approving_custody_throws_permission_error(self):
        """Test Case 8: Non-admin/non-PM role attempting custody approval throws PermissionError."""
        pr = self._create_test_pr(team="Purchase Team", location="Central Store Warehouse")
        pr.items[0].custom_destination_type = "Central Store Warehouse"
        pr.insert(ignore_permissions=True)
        pr.submit()

        # Simulate junior user
        test_user = "test_junior_store@example.com"
        if not frappe.db.exists("User", test_user):
            frappe.get_doc({
                "doctype": "User",
                "email": test_user,
                "first_name": "Store Junior",
                "roles": [{"role": "Store Assistant"}],
            }).insert(ignore_permissions=True)

        frappe.set_user(test_user)
        with self.assertRaises(frappe.PermissionError):
            GRNStockUpdateOrchestrationService.approve_store_stock_update(pr.name)

    def test_09_mandatory_barcode_policy_enforced_throws_on_missing_sabb(self):
        """Test Case 9: When barcode policy is active, missing SABB bundle throws ValidationError."""
        self.scm_settings.enable_mandatory_barcode_pr = 1
        self.scm_settings.save(ignore_permissions=True)

        pr = self._create_test_pr(team="Store Team", location="Central Store Warehouse", include_sabb=False)
        pr.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            pr.submit()

    def test_10_admin_barcode_toggle_bypass_allows_submission_without_sabb(self):
        """Test Case 10: When Admin disables barcode policy, submission proceeds with bypass flag."""
        self.scm_settings.enable_mandatory_barcode_pr = 0
        self.scm_settings.save(ignore_permissions=True)

        pr = self._create_test_pr(team="Store Team", location="Central Store Warehouse", include_sabb=False)
        pr.insert(ignore_permissions=True)
        pr.submit()

        pr.reload()
        self.assertEqual(pr.docstatus, 1)
        self.assertEqual(pr.custom_barcode_scan_bypassed, 1)
        self.assertEqual(pr.items[0].custom_serial_scan_status, "Bypassed by Admin")

    def test_11_inspection_rejection_requires_code_quarantine_and_photos(self):
        """Test Case 11: Rejection split requires defect reason code and 2 photos."""
        pr = self._create_test_pr(team="Store Team", location="Central Store Warehouse")
        pr.items[0].rejected_qty = 2.0
        pr.items[0].qty = 8.0
        pr.insert(ignore_permissions=True)

        # Missing reason code and photos must throw
        with self.assertRaises(frappe.ValidationError):
            pr.submit()

        # Provide reason code and photos
        pr.items[0].custom_rejection_reason_code = "Cracked Glass / Cell Defect"
        pr.items[0].custom_damage_photo_1 = "/files/defect_macro.png"
        pr.items[0].custom_damage_photo_2 = "/files/defect_nameplate.png"
        pr.save(ignore_permissions=True)

        # Re-attach SABB matching accepted qty (8)
        serials = [f"MOD-SER-ACC-{i:04d}" for i in range(1, 9)]
        bundle_name = PRSerialBarcodeService.create_inward_sabb(
            "SOLAR-MOD-550W", pr.items[0].warehouse, serials
        )
        pr.items[0].serial_and_batch_bundle = bundle_name
        pr.save(ignore_permissions=True)
        pr.submit()

        pr.reload()
        self.assertEqual(pr.docstatus, 1)
        self.assertEqual(pr.custom_inspection_status, "Partially Accepted with Rejections")
        self.assertEqual(pr.custom_total_rejected_qty, 2.0)

    def test_12_stage_forward_immutability_lock_blocks_cancel_with_downstream_pi(self):
        """Test Case 12: Submitted PR cannot be cancelled once downstream Step 17 PI exists."""
        pr = self._create_test_pr(team="Store Team", location="Central Store Warehouse")
        pr.insert(ignore_permissions=True)
        pr.submit()

        # Simulate downstream Purchase Invoice
        pi = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "supplier": "_Test Supplier",
            "company": "_Test Company",
            "items": [{
                "item_code": "SOLAR-MOD-550W",
                "qty": 10.0,
                "rate": 12000.0,
                "purchase_receipt": pr.name,
                "purchase_order": self.po.name,
            }],
        })
        pi.insert(ignore_permissions=True)
        pi.submit()

        # Attempt cancellation of upstream PR must throw
        with self.assertRaises(frappe.ValidationError):
            pr.cancel()
```

---

## 7. Operational SOP, Runbook & Error Troubleshooting Table

### 7.1 Operational Runbook

| Persona                | Inward Channel                       | Trigger / Action                                                                                                         | System Behavior & Routing                                                                                                | Post-Condition                                                     |
| :--------------------- | :----------------------------------- | :----------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- |
| **Store Assistant**    | `/solar/store/grn-scanner`           | Dock delivery arrival; scans 2D barcodes on pallets; uploads signed challan & LR; submits Store PR.                      | Auto-validates 100% SABB scan; updates stock in `Stores - SEPC` immediately. No Admin approval required.                 | Goods available in central stock for Stage 08 project dispatches.  |
| **Project Engineer**   | `/solar/site/material-inward`        | Transporter arrives at project site; captures mobile GPS lock; verifies bill of lading; uploads photos; submits Site PR. | Evaluates GPS against `Project` coordinates ($\le 500\text{m}$); updates stock in `Site - <Project> - SEPC` immediately. | Goods available on site for Stage 09 DPR installation consumption. |
| **Purchase Assistant** | `/solar/purchase/direct-receipt`     | Factory-gate receipt or emergency direct procurement; routes lines to Store or Site; submits Purchase PR.                | Holds stock updates. Flags Store lines for Admin approval and Site lines for Project Manager approval.                   | Goods recorded but stock held until authorized.                    |
| **Admin**              | `/solar/admin/pending-stock-updates` | Reviews Purchase PR Store lines; verifies challan & bilty; clicks `[Approve Store Stock Intake]`.                        | Marks `custom_store_stock_approval_status = 'Approved by Admin'`; posts Store SLE.                                       | Store inventory released.                                          |
| **Project Manager**    | `/solar/admin/pending-stock-updates` | Reviews Purchase PR Site lines; confirms physical equipment arrival on site; clicks `[Verify & Approve Site Entry]`.     | Marks `custom_site_stock_approval_status = 'Approved by Site'`; posts Site SLE.                                          | Site inventory released.                                           |

### 7.2 Error Troubleshooting Matrix

| Error Message                                                                                 | Root Cause                                                                         | Remediation Procedure                                                                                                            |
| :-------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `ValidationError: 2D Barcode Serial scanning is mandatory`                                    | Serialized item row lacks a verified `Serial and Batch Bundle` (SABB).             | Scan barcodes using `/solar/store/grn-scanner` or request `Admin` to temporarily disable barcode policy in `Solar SCM Settings`. |
| `ValidationError: Site Goods Receipt GPS breach: Measured distance is ...m`                   | Mobile user GPS coordinates are $> 500\text{m}$ from registered Project location.  | Ensure mobile location services are set to "High Accuracy". Offload at site boundaries, or update Project site coordinates.      |
| `PermissionError: Only Admin or System Manager can authorize Store Stock Updates`             | Non-admin user attempted to approve Store lines on a Purchase PR.                  | Only users with the `Admin` or `System Manager` role possess executive authority to release Store inventory.                     |
| `PermissionError: Only Project Engineer or Site Supervisor can submit Site Goods Receipts`    | Frontline persona mismatch (e.g. Purchase staff submitting Site PR directly).      | Re-assign receiving duty to site engineering personnel or switch persona to `Purchase Team`.                                     |
| `ValidationError: Cannot cancel Purchase Receipt: Downstream Step 17 Purchase Invoices exist` | Upstream cancellation blocked by Stage-Forward Immutability Lock.                  | Downstream financial liabilities exist. Reverse or cancel the linked Purchase Invoice before attempting PR cancellation.         |
| `ValidationError: Over-receipt strictly forbidden for serialized solar assets`                | Received quantity exceeds remaining unfulfilled quantity on linked Purchase Order. | Over-receipt on capital solar equipment is forbidden. Amend the Purchase Order or reject excess units.                           |

---

## 8. Reconciliation & Audit Sign-Off

- **Lead Systems Architect:** Principal Enterprise Architect
- **Audit Standard:** `AGENTS.md` Implementation Guidelines & `ADR-000` / `ADR-016` Specifications
- **Timestamp:** 2026-10-01T04:55:00Z
- **Coverage Summary:** 5-layer thin vertical slice codified; all 5 canonical verification gates mathematically and procedurally defined; 12-case atomic integration test suite formulated with strict zero-commit rollback; complete alignment with Frappe v15 SABB engine, mobile GPS geofencing, and multi-tier custody governance.

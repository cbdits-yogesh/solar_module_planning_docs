# ADR-016: Multi-Location Barcode Purchase Receipt (GRN) & Tri-Party Custody Approval Architecture

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), **Step 16: Purchase Receipt (Goods Receipt Note / GRN)** (Flow 2: Step 05 of 08 / Global Step 16) represents the critical physical receiving, serialized asset ingestion, and inventory custody recognition gateway within the **Solar EPC Procurement & Vendor Governance Lifecycle (Flow 2)**. It operates immediately downstream of Step 15 ([`ADR-015`](./ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md), `tabPurchase Order`), verifying incoming vendor shipments against authorized purchase contracts, updating stock ledgers, and unlocking downstream processes including Step 17 (3-Way Matching), Step 18 (Post-GRN Milestone Payment Disbursements), Step 19 (Vendor Performance Rating Scorecards), and Flow 1 Stage 08/09/11 (Site Installation, Surplus Reconciliation, and Solar Asset Register).

Under conventional solar EPC operations and out-of-the-box ERPNext implementations, goods receipt suffers from four severe systemic failure points:

1. **Rigid Single-Warehouse Centralization vs. Direct-to-Site Heavy Logistics:**  
   In Solar EPC projects, equipment spans two fundamentally distinct logistical categories:
   - _Central Warehouse Staging:_ Inverters, string monitoring boxes, DC cables, MC4 connectors, and small installation hardware that land at Central Store for kitting, staging, and pre-commissioning testing.
   - _Direct-to-Site Heavy Shipments:_ Mounting structures (hundreds of tonnes of galvanized cold-rolled steel), 40-foot shipping containers of solar PV modules, and heavy HT step-up transformers that are delivered directly to remote solar project sites to eliminate ₹50,000–₹100,000 in secondary freight, demurrage, crating damage, and double-handling hazards.  
     Restricting Goods Receipt strictly to central warehouse clerks forces remote site deliveries to sit unrecorded for weeks, blocking supplier payments, halting future dispatches, and distorting financial liability.
2. **Custody Ambiguity in Procurement / Field Receipts:**  
   Purchase team engineers frequently execute factory-gate pre-dispatch inspections, emergency local buys, or direct vendor shipments where neither store nor site personnel are present. If the Purchase team can unilaterally force stock into a Store Warehouse without store awareness, or into a Site Warehouse without site physical confirmation, severe inventory leakage and ghost stock disputes emerge. Conversely, preventing the Purchase team from recording receipts halts 3-way matching and vendor milestone release.
3. **Hardcoded Barcode Scanning Bottlenecks in Field Realities:**  
   While 100% 2D barcode scanning (QR / Data Matrix) into Frappe v15 Serial and Batch Bundles (SABB) is vital for high-value serialized assets (solar PV modules and inverters) to preserve 25-year manufacturer warranty claims, field conditions vary widely. Adverse weather, damaged supplier barcode labels, emergency deliveries, or remote areas with no scanner hardware create operational gridlock if barcode scanning is hardcoded as an immutable, non-bypassable barrier.
4. **Disjointed Downstream Milestone & Rating Triggers:**  
   Standard ERP setups treat Goods Receipt as a static stock movement rather than a critical commercial trigger. Out-of-the-box receipts fail to automatically update PO milestone payment schedules (e.g. unlocking the 10% Post-GRN payment tranche), fail to feed vendor On-Time Delivery (OTD) and quality rejection ratings (Step 19), and fail to feed serial registers for lifecycle O&M asset tracking (Flow 1 Stage 11).

---

## Decision

We establish an authoritative, comprehensive architectural standard for **Step 16: Multi-Location Barcode Purchase Receipt (GRN) & Tri-Party Custody Approval Architecture**, extending ERPNext's native `tabPurchase Receipt` and `tabPurchase Receipt Item` within `solar_module` while decoupling domain logic into pure service layers:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         STEP 16: PURCHASE RECEIPT (GRN) ARCHITECTURE                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Purchase Order (STEP_15)] ──▶ Delivery Routing: Central Store vs Direct Project Site          │
│                 │                                                                                │
│                 ├───────────────────────────────┬────────────────────────────────┐               │
│                 ▼                               ▼                                ▼               │
│        [1. STORE TEAM PR]               [2. SITE TEAM PR]              [3. PURCHASE TEAM PR]     │
│       (Store Assistant/Mgr)           (Project Engineer/Sup)           (Purchase Assistant/Mgr)  │
│                 │                               │                                │               │
│                 ▼                               ▼                                ▼               │
│     Default: Stores - SEPC             Direct Site Warehouse            Flexible Line Routing:   │
│     (Changeable to other               Site - <Project> - SEPC          (Store vs Site Warehouses│
│      authorized store wh)                       │                        per line item)          │
│                 │                               │                                │               │
│                 ▼                               ▼                                ▼               │
│     [Barcode Scan Gate]             [Barcode Scan Gate]              [Barcode Scan Gate]         │
│     Admin Toggle Controlled         Admin Toggle Controlled          Admin Toggle Controlled     │
│     (Solar SCM Settings)            (Solar SCM Settings)             (Solar SCM Settings)        │
│                 │                               │                                │               │
│                 ▼                               ▼                                ▼               │
│     [Automatic Stock Update]        [Automatic Stock Update]         [Custody Verification Gate] │
│     Posts directly to SLE           Posts directly to Site SLE                   │               │
│     Stores - SEPC                   Site - <Project> - SEPC                      │               │
│     (docstatus = 1)                 (GPS & Proof Verified)                       │               │
│                                                                                  │               │
│                                                    ┌─────────────────────────────┴─────────┐     │
│                                                    ▼                                       ▼     │
│                                          [Lines Routed to Site]                 [Lines Routed to]│
│                                          Approval Req to:                       [Store Warehouse]│
│                                          Project Manager                        Approval Req to: │
│                                          (Verifies site arrival)                Admin            │
│                                                    │                                       │     │
│                                                    ▼                                       ▼     │
│                                          [On PM Approval]                       [On Admin Appr]  │
│                                          Posts Site SLE                         Posts Store SLE  │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Tri-Party Receiving Personas & Role Delegation

To guarantee accountability across all operational scenarios while strictly adhering to the **Zero "User" Suffix Rule**:

1. **Store Team (`Store Assistant`, `Store Manager`):**
   - Receives goods at Central Warehouse dock (`Stores - SEPC` by default).
   - Allows changing the destination warehouse if multiple store warehouses exist (e.g. `Regional Store - North`, `Fabrication Staging Yard`) provided the target warehouse belongs to the store domain.
   - Executes dock inspection, physical pallet verification, and high-throughput 2D barcode scanning.
   - **Stock Update:** Commits stock **automatically** to the selected Store Warehouse upon document submission (`docstatus = 1`).
2. **Site Team (`Project Engineer`, `Site Supervisor`):**
   - Receives heavy structures, containerized PV modules, and equipment delivered directly to the project location.
   - Validates physical offloading, transporter Lorry Receipt (LR), vendor Delivery Challan, and package condition.
   - Captures GPS geotag verification (must fall within configured project geofence radius, default 500m).
   - **Stock Update:** Commits stock **automatically** to the linked Project Site Warehouse (`Site - <Project Code> - SEPC`). Site PR does **NOT** require Admin store-update approval, ensuring site installation teams can immediately consume materials without administrative delays.
3. **Purchase Team (`Purchase Assistant`, `Purchase Manager`):**
   - Executes direct factory-gate pre-dispatch receipts, emergency offsite purchases, or inwards where field/store personnel are unavailable.
   - Provides line-level multi-destination routing: Purchase can allocate items (few, some, or all) to a **Store Warehouse** OR a **Site Warehouse**.
   - **Controlled Custody Approvals:**
     - For items routed to **Store Warehouse**: Cannot unilaterally inflate store inventory. System routes lines into `Pending Admin Approval`, requiring explicit sign-off by **`Admin`** before posting to the Store Stock Ledger.
     - For items routed to **Site Warehouse**: System routes lines into `Pending Site Approval`, requiring explicit sign-off by the **`Project Manager`** to verify that goods have physically arrived and been inspected on-site before posting to the Site Stock Ledger.

### 2. Admin-Controllable Barcode Policy (`Solar SCM Settings`)

Barcode scanning must not paralyze operations during field emergencies:

- We introduce `enable_mandatory_barcode_pr` (`Check`, default 1) in `tabSolar SCM Settings`, editable **strictly by `Admin`** or `System Manager`.
- **When Enabled:** Enforces 100% 2D barcode scanning via Frappe v15 `tabSerial and Batch Bundle` (SABB) for all items marked `custom_requires_barcode_serials = 1`. Scanned serial count must match `accepted_qty` exactly.
- **When Disabled:** Bypasses mandatory barcode scanning blocks. Goods receipts can proceed via manual entry, lot numbers, or bulk intake, logging `custom_barcode_scan_bypassed = 1` for executive audit traceability.

### 3. Five Immutable Server-Side Verification Gates

Every Purchase Receipt is gated by `PurchaseReceiptValidationService`:

- **Gate 1 (PO Integrity & Over-Receipt Tolerance):** Linkage to submitted `tabPurchase Order` (`docstatus = 1`). Hard-blocks over-receipt on serialized assets (modules, inverters); allows configurable tolerance ($\le 3\%$) for bulk DC cables/consumables.
- **Gate 2 (Role & Persona Authorization):** Enforces authorized role credentials (`Store Assistant`, `Store Manager`, `Project Engineer`, `Site Supervisor`, `Purchase Assistant`, `Purchase Manager`, `Admin`) and valid team selection (`Store Team`, `Site Team`, `Purchase Team`).
- **Gate 3 (Admin Barcode Policy):** Evaluates `Solar SCM Settings.enable_mandatory_barcode_pr` and validates SABB bundle completeness and serial uniqueness in `tabSerial No`.
- **Gate 4 (Multi-Location Warehouse & Custody Routing):** Validates warehouse legitimacy and routes approval requests (to `Admin` for Store deliveries, to `Project Manager` for Site deliveries) on Purchase Team PRs.
- **Gate 5 (Physical Proof & Geotagging):** Mandates upload of Delivery Challan and Transporter LR. Enforces GPS coordinates for Site PRs. For damaged goods, requires defect classification and photo evidence (minimum 2 photographs) routing to `Quarantine / Rejection - SEPC`.

### 4. Downstream Automated Integrations

1. **Step 17 (3-Way Matching):** Ingests accepted quantity and accepted warehouse for rate/quantity reconciliation against PO and incoming Purchase Invoice.
2. **Step 18 (Milestone Payments):** Automatically updates `tabPurchase Order` milestone terms, releasing the "Post-GRN Inspection" tranche in `tabPayment Schedule`.
3. **Step 19 (Vendor Performance Rating):** Dispatches asynchronous event to `VendorRatingService`, computing On-Time Delivery (OTD) based on actual GRN posting date vs PO promised delivery date, and Quality Score based on `accepted_qty / (accepted_qty + rejected_qty)`.
4. **Flow 1 Project Execution:** Immediately updates Site Available Stock for Stage 08/09 (Installation Execution & Zone DPR consumption) and registers serial numbers for Stage 11 (Solar Asset Register & O&M).

---

## Alternatives Considered

### 1. Enforce All Goods to Pass Physically Through Central Store

- _Pros:_ Complete centralized inventory control.
- _Cons:_ Catastrophic logistical inefficiencies for solar EPC. Transporting 50 tonnes of mounting structures or containers of solar panels to a central store and then re-shipping them to a remote desert or rooftop site adds ₹50,000–₹100,000 per project, risks crating damage, and causes 7–14 days of project delay.
- _Rejected:_ Direct-to-site delivery with digital verification is a non-negotiable industry requirement.

### 2. Allow Purchase Team to Update Store/Site Stock Directly Without Approvals

- _Pros:_ Fewer approval clicks.
- _Cons:_ Destroys inventory custody accountability. A procurement officer could book stock in a central store that never arrived, or book items into a site where the site supervisor has received nothing, leading to financial fraud and material shortages.
- _Rejected:_ Dual custody verification (Admin approval for Store, Project Manager approval for Site) guarantees audit-proof integrity.

### 3. Hardcoded Immutable Barcode Enforcement

- _Pros:_ Guarantees 100% serial capture at all times.
- _Cons:_ Paralyses site work during rain, barcode sticker damage, or scanner battery failure. In solar EPC, installation crews cannot sit idle at ₹25,000/day labor costs because an individual panel's QR code is smudged.
- _Rejected:_ Admin-controllable toggle in `Solar SCM Settings` provides necessary operational resilience while preserving governance.

---

## Consequences

### Positive

- **Logistical Optimization:** Eliminates double-freight handling by legally and physically supporting direct site receipts.
- **Absolute Custody Integrity:** Store Managers and Site Project Managers are protected against unauthorized inventory injections by Purchase.
- **High-Throughput Serial Tracking:** Frappe v15 SABB engine ensures rapid scanning of thousands of PV modules while preventing duplicate serial fraud.
- **Operational Resilience:** Admin toggle allows bypass of barcode blockers during field emergencies without code modifications.
- **Closed-Loop SCM:** Direct feed into 3-way invoice matching, milestone disbursements, and vendor rating scorecards.

### Negative / Trade-offs

- **Process Complexity:** Purchase PR requires a two-step posting process (submission followed by Admin or Project Manager approval before SLE generation).
- **Network Dependency for Site Geotagging:** Remote sites require initial connectivity or cached offline sync to register GPS coordinates and upload delivery documents.

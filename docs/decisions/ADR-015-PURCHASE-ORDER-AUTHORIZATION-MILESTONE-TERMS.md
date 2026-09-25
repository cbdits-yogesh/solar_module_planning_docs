# ADR-015: Purchase Order Authorization, Solar Milestone Payment Terms & Multi-Location Delivery Routing Architecture

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), **Step 15: Purchase Order Authorization & Milestone Terms** (Flow 2: Step 04 of 08 / Global Step 15) represents the binding commercial contract release gateway within the **Solar EPC Procurement & Vendor Governance Lifecycle (Flow 2)**. It ingests the winning commercial award from Step 14 ([`ADR-014`](./ADR-014-SUPPLIER-QUOTATION-COMPARATIVE-EVALUATION-MATRIX.md), `tabQuotation Comparison Matrix`), locks the negotiated landed rates and specifications, enforces multi-tier executive authorization thresholds, establishes disciplined milestone payment schedules, and preconditions delivery routing to Central Stores or Working Sites for Step 16 ([`STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md`](../../step_plans/STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md)).

Under conventional solar EPC operations and out-of-the-box ERPNext implementations, the Purchase Order process suffers from critical operational and financial vulnerabilities:

1. **Unregulated Procurement Release (Rogue / Maverick Buying):** Out-of-the-box ERP purchase orders can often be submitted by individual buyers without enforced financial authority delegation. High-value capital commitments (e.g. ₹5,000,000 for utility string inverters or bifacial solar modules) are released without CFO or Managing Director authorization, causing sudden cash flow crises.
2. **Ambiguous Payment Terms & Cash Flow Exposure:** Solar suppliers typically demand structured milestone payments (e.g. 15% Advance, 70% Against Dispatch/Lading Bill, 10% Post-GRN Site Inspection, 5% Retention upon Grid Synchronization). In standard ERP setups, POs are issued with generic terms ("Immediate", "Net 30"), leaving Accounts with no contractual basis to hold back retention money against equipment defects or delay liquidations.
3. **Rigid Single-Project Constraints vs. Central Bulk Buying:** Real-world solar EPC procurement operates across multiple modes:
   - _Single-Project Orders:_ Equipment procured for a specific site (e.g. 100 kW Rooftop).
   - _Consolidated Multi-Project Buying:_ Bulk container purchasing of modules or inverters split across 5 upcoming sites to negotiate volume discounts.
   - _Central Inventory Replenishment:_ Periodic safety stock replenishment initiated by Store Material Requests (Flow 2: Step 01 / `STEP_12`).
     Forcing every PO to rigidly link to a single engineering design BOM causes severe operational paralysis for central store managers and bulk purchasing executives.
4. **Logistics & Delivery Site Ambiguity:** Solar components must either be shipped to the **Central Warehouse** (for staging, bundling, or testing) or **Directly to the Working Site** (to avoid double handling and demurrage costs for heavy mounting structures, transformers, and containers of panels). Without explicit delivery routing in the PO, transporters deliver to central stores by default, creating ₹50,000+ unnecessary re-freight charges.
5. **Rate Inflation & Spec Drift Post-Quotation:** Once a quotation is approved in a comparative evaluation sheet, manual PO re-entry allows unscrupulous or careless buyers to silently inflate unit rates or modify component specifications (e.g. downgrading panel wattage from 545W to 535W) without triggering executive alerts.
6. **Delivery Schedule Blindspots & Liquidated Damages (LD):** DISCOM interconnection timelines (Stage 10) carry strict statutory deadlines. A 2-week delay in supplier delivery can trigger project liquidated damages of 0.5% per week. Standard POs lack automated vendor acknowledgment tracking and turn-around time (SLA) enforcement.

---

## Decision

We establish an authoritative, comprehensive architectural standard for **Step 15: Purchase Order Authorization & Milestone Terms**, extending ERPNext's native `tabPurchase Order` and `tabPurchase Order Item` within `solar_module` while decoupling domain logic into pure service layers:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     STEP 15: PURCHASE ORDER AUTHORIZATION & SCM ARCHITECTURE                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Step 14: Quotation Comparison Matrix Award Approved] OR [Authorized Central Stock MR / Indent]│
│                                │                                                                 │
│                                ▼                                                                 │
│   [Verification Gate 1: Upstream Sourcing & Rate Integrity Gate]                                 │
│   • Enforces linkage to submitted tabQuotation Comparison Matrix (or authorized Single Source)   │
│   • Validates that PO line rates <= Awarded Comparison landed rates (Zero rate inflation)        │
│                                │                                                                 │
│                                ▼                                                                 │
│   [Verification Gate 2: Multi-Tier Financial Authority Delegation]                              │
│   • Tier 1 (< ₹50,000): Purchase Manager (Purchase Assistant drafts only)                       │
│   • Tier 2 (₹50,000 - ₹5,00,000): Configurable (Purchase Manager / Accounts Manager / Admin)     │
│   • Tier 3 (> ₹5,00,000 - ₹50,00,000): Admin (Project Supreme Command)                           │
│   • Tier 4 (> ₹50,00,000): Admin (Project Supreme Command)                                       │
│                                │                                                                 │
│                                ▼                                                                 │
│   [Verification Gate 3: Solar Milestone Payment Schedule & Retention Gate]                      │
│   • Mandates structured milestone breakdown (Advance, Dispatch/LR, Post-GRN, Retention/PBG)     │
│   • Forbids generic single-bullet "Immediate" terms for capital equipment purchases             │
│                                │                                                                 │
│                                ▼                                                                 │
│   [Verification Gate 4: Configurable Project Budget & Commercial BOM Check (Optional)]           │
│   • Automatically bypassed for Central Inventory Replenishment & Consolidated Bulk POs           │
│   • When project is linked, optionally verifies headroom against Commercial Proposal / SO BOM    │
│   • Governed by configurable toggle in Solar SCM Settings (Developer/Admin switchable)           │
│                                │                                                                 │
│                                ▼                                                                 │
│   [Verification Gate 5: Multi-Location Delivery Routing & Barcode Preconditioning]               │
│   • Explicit routing: Central Store Warehouse vs Direct Working Site Warehouse                   │
│   • Flags custom_requires_barcode_serials = 1 to enforce Sabhav SABB scanning in Step 16 GRN     │
│                                │                                                                 │
│                                ▼                                                                 │
│   [Submit Purchase Order (docstatus = 1) & 24h/48h SLA Engine]                                   │
│   • Closes 24h PO Release SLA clock; initiates 48h Vendor Acknowledgment countdown               │
│   • Passwordless vendor confirmation via /solar/po-portal/:token                                 │
│   • Overdue SLA breaches enforce mandatory entries in tabRemark-Delay Log                        │
│                                │                                                                 │
│                                ▼                                                                 │
│   [Downstream Hand-off] ──▶ Step 16: Multi-Location Barcode GRN (Store OR Site)                  │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Extended Core Entity Model: Standard ERPNext `tabPurchase Order`

To preserve 100% upgrade safety without altering core code, all enterprise attributes are isolated under the `custom_*` namespace:

- **Upstream Sourcing Links:** `custom_comparison_matrix_ref` (`Link` to `Quotation Comparison Matrix`), `custom_awarded_quotation_ref` (`Link` to `Supplier Quotation`), `custom_material_request_ref` (`Link` to `Material Request`), `custom_is_single_source` (`Check`).
- **Project Classification & Routing:**
  - `custom_po_classification` (`Select`: `Project-Specific Solar Equipment`, `Multi-Project Consolidated Bulk`, `Central Inventory Replenishment`, `Consumables & Hardware`, `Subcontracting & Services`).
  - `custom_project_ref` (`Link` to `Project`, optional for bulk/replenishment).
  - `custom_sales_order_ref` (`Link` to `Sales Order`, optional).
  - `custom_delivery_location_type` (`Select`: `Central Store Warehouse`, `Direct Site Warehouse`).
  - `custom_target_site_warehouse` (`Link` to `Warehouse`).
- **Financial Delegation & Authorization:**
  - `custom_authorization_tier` (`Select`: `Tier 1: Up to ₹1,00,000`, `Tier 2: Up to ₹10,00,000`, `Tier 3: Up to ₹50,00,000`, `Tier 4: Above ₹50,00,000`).
  - `custom_authorized_by` (`Link` to `User`), `custom_authorized_on` (`Datetime`), `custom_authorization_remarks` (`Small Text`).
- **Milestone Payment Governance:**
  - `custom_advance_pct` (`Percent`), `custom_advance_amount` (`Currency`), `custom_advance_cleared` (`Check`), `custom_advance_payment_ref` (`Link` to `Payment Entry`).
  - `custom_retention_pct` (`Percent`, e.g. 5%), `custom_retention_due_event` (`Select`: `On Grid Synchronization / COD`, `On Final Acceptance Test`, `Against Performance Bank Guarantee (PBG)`).
  - `custom_liquidated_damages_clause` (`Check`, defaults to 1 for capital solar assets: 0.5% per week up to 5%).
- **Vendor Portal Confirmation & SLA:**
  - `custom_portal_token` (`Data`, 256-bit UUID), `custom_vendor_acknowledgment_status` (`Select`: `Pending Acknowledgment`, `Acknowledged & Confirmed`, `Exceptions Raised`).
  - `custom_vendor_ack_date` (`Datetime`), `custom_sla_deadline` (`Datetime`), `custom_sla_status` (`Select`: `On Time`, `Overdue`), `custom_delay_reason_table` (`Table` to `Remark-Delay Log`).

### 2. Multi-Tier Financial Authority Matrix Gate

Submission of `Purchase Order` (`docstatus = 1`) enforces hard server-side financial authority checks aligned with ADR-020:

$$\text{Net PO Total} = \sum (\text{Qty} \times \text{Rate}) + \text{Taxes} - \text{Discounts}$$

- **Tier 1 ($< ₹50,000$):** Can be submitted strictly by `Purchase Manager` (frontline `Purchase Assistant` drafts only, cannot submit).
- **Tier 2 ($₹50,000 \text{ to } ₹5,00,000$):** Requires authorization by the single active approver role configured in `Solar SCM Settings.tier_2_approver_role` (`Purchase Manager`, `Accounts Manager`, or `Admin`).
- **Tier 3 ($> ₹5,00,000 \text{ to } ₹50,00,000$):** Exclusive sign-off authority reserved for **`Admin`** (Project Supreme Command).
- **Tier 4 ($> ₹50,00,000$):** High-value capex threshold reserved strictly for **`Admin`** (Project Supreme Command).

Attempting to submit without meeting the designated role authorization raises an immediate `frappe.PermissionError` / `frappe.ValidationError`.

### 3. Solar Milestone Payment Schedule & Retention Engine

Capital solar procurement mandates structured milestone terms via ERPNext's `tabPayment Schedule` child table:

1. **Advance Tranche (10%–20%):** Triggers `Payment Entry` creation in Accounts. Materials are not scheduled for manufacturing or release until advance clearance is recorded.
2. **Dispatch / In-Transit Tranche (60%–70%):** Payable upon presentation of Transporter Lorry Receipt (LR), signed packing list, and factory inspection certificate.
3. **Receipt & Inspection Tranche (10%–20%):** Released strictly after Step 16 GRN completion and 100% 2D barcode serial scan verification.
4. **Retention Tranche (5%–10%):** Held until commercial COD certification (Stage 10 Grid Sync) or replaced by a formal Performance Bank Guarantee (PBG).

Single-bullet "Immediate" or "Due on Receipt" payment terms are hard-blocked for items classified under `Critical Solar Equipment`.

### 4. Configurable / Optional Project Headroom Check (Developer / Admin Governed)

Addressing real-world procurement flexibility:

1. **Non-Project / Bulk Purchases:** When `custom_project_ref` is blank or `custom_po_classification` is set to `Central Inventory Replenishment` or `Multi-Project Consolidated Bulk`, all project budget and BOM headroom checks are **completely bypassed**.
2. **Project-Linked Orders:** When a single project is linked, checking cumulative PO quantities against the Commercial Proposal / Sales Order BOM (`tabQuotation` / `tabSales Order`) is designed as a **Configurable Governance Option** (`enforce_project_bom_ceiling` in `Solar SCM Settings`):
   - If enabled by the Admin/Developer: Validates that cumulative ordered items do not exceed the baseline proposal plus an allowed engineering contingency margin (default: 5%).
   - If disabled: Emits a soft warning badge in Desk rather than blocking submission, allowing implementation teams to adopt the level of rigidity appropriate for their operational maturity.

### 5. Multi-Location Delivery Routing for Step 16 GRN

The PO explicitly fixes delivery destination to streamline downstream logistics:

- **Central Store Warehouse (`Stores - SEPC`):** Transporters deliver to headquarters warehouse for kit staging, buffer storage, or bench testing.
- **Direct Site Warehouse (`Site - <Project Code> - SEPC`):** Transporters deliver directly to site. Step 16 GRN can be executed by on-site `Site Supervisor` / `Project Engineer` via mobile barcode scanner without routing through central store inventory.
- Line items are tagged with `custom_requires_barcode_serials = 1` for PV modules, inverters, and LT/HT breakers, enforcing Frappe v15 Serial and Batch Bundle (SABB) capture upon receipt.

### 6. 24h Release & 48h Vendor Acknowledgment SLA Engine

1. **24-Hour PO Release SLA:** Computed from the timestamp of `Quotation Comparison Matrix` submission. If the PO is not authorized and released within 24 hours, it transitions to `Overdue`.
2. **48-Hour Vendor Acknowledgment SLA:** Computed upon PO submission. Transmits an automated tokenized link (`/solar/po-portal/:token`) to the supplier.
3. **Delay Logging Invariant:** If an SLA deadline is breached, document state changes cannot proceed without appending a structured justification to `tabRemark-Delay Log`.

---

## Alternatives Considered

### Alternative 1: Out-of-the-Box ERPNext Purchase Order Without Custom Gates

- **Pros:** Zero custom code, instant setup.
- **Cons:** Any junior purchasing clerk can issue multi-million rupee orders. No milestone payment enforcement, no landed cost protection, no site vs store routing distinction, and zero vendor SLA tracking.
- **Rejected:** Completely unsuited for high-value Solar EPC project governance and cash-flow management.

### Alternative 2: Rigid Hard-Coding Against Survey Engineering Design BOM for All POs

- **Pros:** Maximum theoretical control against initial site survey designs.
- **Cons:** Causes total failure when purchasing central store inventory, purchasing consolidated bulk containers across multiple upcoming pipelines, or purchasing consumables. Furthermore, commercial agreements are grounded in Commercial Proposals and Sales Orders, not preliminary survey drawings.
- **Rejected:** Severely cripples purchasing agility and real-world supply chain operations.

### Alternative 3: External Contract Management System (CMS) Integration

- **Pros:** Third-party legal contract lifecycle tools.
- **Cons:** Adds third-party license costs, introduces API synchronization delays, fragments audit trails away from ERPNext accounting ledgers, and complicates mobile GRN execution.
- **Rejected:** A decoupled, domain-driven ERPNext extension provides complete native cohesion at lower cost and higher performance.

---

## Consequences

### Positive Consequences

- **Executive Financial Protection:** Multi-tier authorization matrix eliminates unauthorized commitments and preserves enterprise liquidity.
- **Elimination of Rate Inflation:** Upstream comparison matrix rate lock ensures that negotiated landed rates cannot be manipulated post-award.
- **Cash Flow Predictability:** Enforced milestone schedules align Accounts disbursements with physical equipment delivery and on-site testing.
- **Operational Supply Chain Flexibility:** Supports single-project, multi-project consolidated, and central inventory replenishment procurement paths without artificial bottlenecks.
- **Seamless Step 16 GRN Preconditioning:** Clear site vs store delivery routing and serialized asset flags ensure zero confusion during physical goods intake.

### Negative / Trade-Off Consequences

- **Approval Latency for High-Value Orders:** Tier 4 orders require Admin / MD sign-off, which may introduce minor wait times if executive approvers are unavailable (mitigated by automated mobile WhatsApp notifications).
- **Vendor Portal Adaptation:** Suppliers must interact with the lightweight passwordless acknowledgment link to confirm delivery milestones.

---

## Compliance & Invariants

1. **Enterprise Role Standard:** Strict adherence to the **Zero "User" Suffix Rule** ([`step_plans/README.md#5-enterprise-persona--role-naming-standard-zero-user-suffix-rule`](../../step_plans/README.md#5-enterprise-persona--role-naming-standard-zero-user-suffix-rule)) and [`ADR-020`](ADR-020-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md): `Purchase Assistant`, `Purchase Manager`, `Accounts Assistant`, `Accounts Manager`, `Store Assistant`, `Store Manager`, `Site Supervisor`, `Project Engineer`, `Project Manager`, `Admin`.
2. **Authority Standard:** Clean separation between `Admin` (Project Supreme Command) and `System Manager` (Framework Supreme / Developer).
3. **Database Integrity:** 3NF relational schema with explicit database indexes on foreign keys (`custom_comparison_matrix_ref`, `custom_project_ref`, `custom_material_request_ref`).
4. **Testing Protocol:** 100% automated test coverage inheriting from `IntegrationTestCase` with zero database commits (`frappe.db.commit()` prohibited).

# ADR-018: Joint Vendor Payment Monitoring Workbench, Dual-Cadence Notification Engine (T-1 & T-0) & Closed-Loop Procurement Settlement Architecture

## Status

Accepted

## Date

2026-09-25

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), **Step 18: Joint Vendor Payment Monitoring Workbench** (Flow 2: SCM, Store, Purchase & Vendor Procurement Lifecycle — Step 07 of 08 / Global Step 18) constitutes the definitive financial execution, liquidity governance, and multi-department collaborative settlement engine.

Positioned downstream of Step 15 ([`ADR-015`](./ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md), `tabPurchase Order` milestone terms), Step 16 ([`ADR-016`](./ADR-016-MULTI-LOCATION-PURCHASE-RECEIPT-BARCODE-GRN.md), `tabPurchase Receipt`), and Step 17 ([`ADR-017`](./ADR-017-PURCHASE-INVOICE-3WAY-MATCH-ADMIN-ENTRY-GOVERNANCE.md), `tabPurchase Invoice` 3-way match validation), this stage governs the actual disbursement of corporate funds against commercial procurement commitments across all solar EPC project archetypes.

In utility-scale and commercial rooftop solar EPC projects, procurement of high-value equipment (tier-1 bifacial PV modules, string/central inverters, HT power transformers, and galvanized mounting structures) involves substantial capital outlay. Commercial supplier contracts enforce strict multi-stage payment terms:

- **Tranche 1 (Advance):** 10%–20% payable with Purchase Order release to trigger raw material procurement and production slots.
- **Tranche 2 (Dispatch / Transit):** 60%–70% payable against Transporter Lorry Receipt (LR) and Factory Acceptance Test (FAT) inspection certificates prior to factory gate release.
- **Tranche 3 (Site Receipt / Delivery):** 10%–20% payable upon physical receipt, barcode GRN clearance (Step 16), and 3-way match verification (Step 17).
- **Tranche 4 (Performance Retention):** 5%–10% retained until grid synchronization (Step 10) or submission of a Performance Bank Guarantee (PBG).

Under conventional ERP operations and legacy practices, vendor payment management suffers from four severe systemic failures:

1. **The Inter-Departmental Information Blackout:**  
   The Procurement/Purchase team commits to suppliers on specific delivery schedules tied to payment milestones. However, the Finance & Accounts team operates in a separate functional silo, processing disbursements according to bank liquidity and payment runs without real-time synchronization with Purchase. Consequently, Purchase personnel spend excessive hours calling or emailing Accounts to ask: _"Has Supplier X's advance been disbursed? Can we request factory loading?"_ Meanwhile, suppliers halt dispatches or charge container detention penalties due to unnotified payment delays.

2. **Missing Proactive Alerts and Due-Date Blindspots:**  
   Payment terms specified in Purchase Orders or credit periods in Purchase Invoices (e.g., Net 30, Net 45) are buried in static child tables (`tabPayment Schedule`). Neither Purchase nor Accounts receives automated, proactive advance warnings before obligations mature. Obligations are only discovered when suppliers issue legal notices, withhold warranties, or freeze subsequent orders.

3. **Milestone Prerequisite Disconnect (Uncontrolled Cash Leakage):**  
   Accounts teams often disburse payments without verified visibility into operational prerequisites—such as whether factory inspection certificates were signed off, whether the shipment Lorry Receipt (LR) was validated, or whether the site GRN passed quality inspection with zero short-shipments. Disbursing funds prematurely forfeits commercial leverage and risks paying for defective or missing goods.

4. **Lack of Dual-Workspace Upcoming Payment Visibility:**  
   Standard ERPNext separates Buying workspaces from Accounts workspaces without providing a synchronized operational desk. Purchase cannot view impending supplier cash calls to plan logistics, while Accounts cannot view future procurement milestones to forecast working capital and project cash flows.

---

## Decision

We establish an authoritative, comprehensive architectural standard for **Step 18: Joint Vendor Payment Monitoring Workbench, Dual-Cadence Notification Engine (T-1 & T-0) & Closed-Loop Procurement Settlement Architecture**, extending ERPNext core accounting entities (`tabPayment Schedule`, `tabPayment Entry`, `tabPurchase Order`, `tabPurchase Invoice`) within `solar_module` while decoupling domain logic into pure service layers.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      STEP 18: JOINT VENDOR PAYMENT MONITORING ARCHITECTURE                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Purchase Order Milestones] ──┐                                                                │
│   (Advance, LR, GRN, Retention) │                                                                │
│                                 ├─▶ [Unified Payment Obligation Engine]                          │
│   [Purchase Invoice Schedules]  │   (Normalizes PO Milestones & PI Due Dates)                    │
│   (3-Way Match Cleared, Net 30) ┘                                                                │
│                                                   │                                              │
│                     ┌─────────────────────────────┴────────────────────────────┐                 │
│                     ▼                                                          ▼                 │
│   ┌───────────────────────────────────────────┐      ┌─────────────────────────────────────────┐ │
│   │   DUAL-CADENCE NOTIFICATION DAEMON        │      │   DUAL-WORKSPACE UPCOMING DESKS         │ │
│   │   (Daily Celery / RQ Worker at 08:00 AM)  │      │                                         │ │
│   ├───────────────────────────────────────────┤      ├─────────────────────────────────────────┤ │
│   │ 1. T-1 Day Alert (Due Tomorrow):          │      │ • Purchase Desk (/solar/procurement):   │ │
│   │    Notifies BOTH Purchase & Accounts      │      │   - Milestone blockers & advance status │ │
│   │ 2. T-0 Day Alert (Due Today):             │      │   - Prerequisite readiness (LR, GRN)    │ │
│   │    High-priority alert to BOTH teams      │      │ • Accounts Desk (/solar/accounts):      │ │
│   │ 3. Multi-Channel: In-App, Email, WhatsApp │      │   - Liquidity buckets & cash forecast   │ │
│   │ 4. Governed by Solar Notification Settings│      │   - TDS Sec 194Q & bank ledger balance  │ │
│   └───────────────────────────────────────────┘      └─────────────────────────────────────────┘ │
│                                                   │                                              │
│                                                   ▼                                              │
│                                   [Payment Prerequisite Gate]                                    │
│                                    - Advance: Signed PO verified                                 │
│                                    - Transit: LR & Inspection verified                           │
│                                    - Post-GRN: 3-Way Match & GRN verified                        │
│                                    - Retention: Grid Sync verified                               │
│                                                   │                                              │
│                                                   ▼                                              │
│                                      [Accounts Executes Payment]                                 │
│                                       (Creates tabPayment Entry)                                 │
│                                                   │                                              │
│                                                   ▼                                              │
│                              [CLOSED-LOOP SETTLEMENT OBSERVER HOOK]                              │
│                               `on_submit` of tabPayment Entry                                    │
│                                                   │                                              │
│                     ┌─────────────────────────────┴────────────────────────────┐                 │
│                     ▼                                                          ▼                 │
│   [INSTANT PURCHASE NOTIFICATION]                              [MILESTONE RECONCILIATION]        │
│   - Supplier Name & Paid Amount (INR)                          - Updates tabPayment Schedule     │
│   - Bank Reference / UTR Number                                - Clears obligation status        │
│   - Payment Mode & Instrument Date                             - Unlocks shipment / logistics    │
│   - Remaining PO/PI Balance                                    - Feeds Step 19 Vendor Rating     │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Unified Payment Obligation Normalization Model

Rather than maintaining fragmented tracking across disparate purchase orders and commercial invoices, the system introduces a **Unified Payment Obligation Engine** (`VendorPaymentScheduleService`):

1. **Purchase Order Commitments:** Extracts milestone tranches from `Purchase Order.payment_schedule` (Advance, LR/Transit, GRN, Retention) prior to invoice receipt.
2. **Purchase Invoice Commitments:** Extracts credit schedules from `Purchase Invoice.payment_schedule` once invoices pass Step 17 3-way match validation.
3. **Deduplication & Cross-Referencing:** When a Purchase Invoice is booked against a PO with pre-existing milestone tranches, the engine links the invoice credit term directly to the corresponding PO milestone row, preventing double-counting of payment liabilities.

### 2. Dual-Cadence Proactive Notification Engine (T-1 and T-0 Alerts)

To eliminate payment blindspots and surprise cash crunches, a scheduled daily background daemon (`VendorPaymentNotificationDaemon`, executing daily at 08:00 AM) inspects all open, unreconciled payment obligations:

1. **T-1 Day Alert (One Day Before Payment Day):**
   - Identifies all obligations where `due_date == today + 1 day` and `custom_settlement_status != 'Disbursed'`.
   - Dispatches a synchronized reminder to **both the Purchase Team** (`Purchase Manager`, `Purchase Assistant` mapped to the project/PO) and **the Accounts Team** (`Accounts Officer`, `Accounts Assistant`).
   - Alerts Purchase to verify that all physical prerequisites (e.g., test certificates, bill of lading) are in place.
   - Alerts Accounts to plan bank liquidity and queue payment vouchers for processing.
2. **T-0 Day Alert (On Payment Day):**
   - Identifies all obligations where `due_date == today` and `custom_settlement_status != 'Disbursed'`.
   - Dispatches a high-priority, actionable alert to **both Purchase and Accounts**.
   - Direct deep-links allow Accounts to launch the payment preparation modal directly from the notification.
3. **Multi-Channel & Granular Toggle Governance:**
   - Multi-channel delivery: Frappe in-app `Notification Log` (badge count and real-time banner), system transactional email, and optional WhatsApp Business notification.
   - All alerts are governed by toggle switches in `tabSolar Notification Settings` (`notify_vendor_payment_t_minus_1`, `notify_vendor_payment_t_zero`), customizable by `Admin` without code changes.

### 3. Closed-Loop Instant Settlement Notification to Purchase

To eliminate inter-departmental inquiries and communication lags:

1. **Event-Driven Observer Hook:**  
   The platform binds a lifecycle hook (`on_submit`) to ERPNext's native `Payment Entry` (`tabPayment Entry`).
2. **Automated Purchase Broadcast:**  
   When an Accounts Officer submits a `Payment Entry` against a Supplier with references to a `Purchase Order` or `Purchase Invoice`, `VendorPaymentSettlementService` immediately intercepts the transaction and broadcasts a rich notification to the Purchase team:
   - **Disbursed Amount:** Total INR paid.
   - **Bank Transaction Reference:** UTR Number / Cheque Number / Transaction ID.
   - **Payment Mode:** RTGS, NEFT, IMPS, or Cheque.
   - **Target Supplier & Project:** Supplier Name, Project ID, PO/PI document reference numbers.
   - **Remaining Outstanding Balance:** Residual unbilled or unpaid balance on the PO/PI.
3. **Operational Unlocking:**  
   Receiving this notification programmatically updates the Purchase procurement desk, allowing the Purchase Representative to issue a formal dispatch clearance note to the supplier without waiting for manual confirmation.

### 4. Dual-Workspace Dedicated Upcoming Payment Sections

To empower both operational teams without cross-domain cognitive clutter, dedicated views are rendered across the platform:

1. **Purchase Workspace Upcoming Payments Section (`/solar/procurement`):**
   - **Milestone & Delivery Blocker Orientation:** Displays impending payments categorized by milestone type (`Advance Payment`, `Against LR / Factory Dispatch`, `Post-GRN Final`, `Retention Release`).
   - **Prerequisite Traffic Light:** Indicates whether operational prerequisites are satisfied (e.g., `PO Signed [✔]`, `FAT Inspection Report Uploaded [✔]`, `GRN Accepted [✔]`, `3-Way Match Passed [✔]`).
   - **Quick Actions:** `[Nudge Accounts Team]`, `[Upload Dispatch Prerequisite]`, `[View Commercial Contract]`.
2. **Accounts Workspace Upcoming Payments Section (`/solar/accounts`):**
   - **Liquidity & Cash Flow Orientation:** Groups obligations into time horizons (`Due Today`, `Due Tomorrow`, `Due This Week`, `Due in 30 Days`, `Overdue`).
   - **Statutory & Banking Details:** Displays TDS u/s 194Q / TCS u/s 206C(1H) applicability, verified supplier bank IFSC/Account status, and available early-payment cash discounts.
   - **Quick Actions:** `[Create Payment Entry]`, `[Batch Bank Transfer Export]`, `[Place on Dispute Hold]`.
3. **Collaborative Joint Workbench (`/solar/procurement/payment-workbench`):**
   - A unified screen accessible to both teams, providing bi-directional commenting, dispute tagging (`Quality Hold`, `Rate Discrepancy Hold`), and executive delay tracking.

### 5. Enforced Verification Gates

Before payment execution can proceed, the system enforces hard validation gates:

- **Gate 1 (Prerequisite Verification Gate):** Prevents payment disbursement if milestone prerequisites are incomplete (e.g., blocking Tranche 2 if LR is missing, or blocking Tranche 3 if Step 17 3-way match is in `Discrepancy Hold`).
- **Gate 2 (Statutory TDS / TCS Lock):** Enforces automated computation of TDS u/s 194Q (0.1% on cumulative purchases exceeding ₹50 Lakhs in the fiscal year).
- **Gate 3 (Supplier Bank Verification Gate):** Asserts that target bank account details in `Payment Entry` match an active, verified bank account record linked to `Supplier Master`.

---

## Alternatives Considered

### 1. Standard Out-of-the-Box ERPNext Accounts Payable (AP) Aging Report

- **Pros:** Native feature; zero custom schema.
- **Cons:** Strictly retrospective and invoice-based; completely blind to pre-invoice Purchase Order milestones (Advance and Transit tranches, which represent 80% of solar EPC procurement value); offers zero automated T-1/T-0 notifications; leaves Purchase team in a total communication blackout.
- **Rejected:** Incapable of managing high-value milestone-driven solar EPC procurement.

### 2. Manual Daily Email Reminders via Frappe Notification Doctype

- **Pros:** Configurable in desk UI.
- **Cons:** Frappe's standard `Notification` DocType cannot dynamically evaluate combined PO milestone child tables and PI credit tables, cannot correlate prerequisites (e.g., checking if GRN is submitted), and cannot generate synchronized multi-recipient alerts for T-1 and T-0 without duplicate messages.
- **Rejected:** Lacks the domain intelligence and multi-table reconciliation required for solar EPC contracts.

### 3. External Third-Party Treasury / AP Automation SaaS

- **Pros:** Specialized cash management features.
- **Cons:** Introduces data fragmentation, high recurring subscription costs, vendor lock-in, and synchronization lags with ERPNext General Ledger.
- **Rejected:** Frappe Framework's event bus and background worker queues support native, seamless implementation within `solar_module`.

---

## Consequences

### Positive Consequences

- **Zero Supply Chain Halts:** Automated T-1 and T-0 alerts prevent supplier order and shipment freezes caused by forgotten payment dates.
- **Elimination of Phone/Chat Chasing:** Instant automated settlement alerts to Purchase eliminate manual follow-ups, speeding up solar equipment dispatches by 3–5 days.
- **Cash Leakage Prevention:** Milestone prerequisite gates prevent disbursements before physical inspection, LR verification, or 3-way match clearance.
- **Accurate Cash Forecasting:** Dual-workspace upcoming payment desks provide both Purchase and Accounts with clear forward visibility into capital commitments.
- **Statutory Compliance:** Guarantees 100% adherence to TDS u/s 194Q and MSME statutory payment timelines (45-day rule under Section 43B(h)).

### Negative / Trade-Off Consequences

- **Scheduler Dependency:** Proactive notifications rely on the reliable execution of Frappe background Redis workers (`bench worker`). If Celery/Redis daemons stall, notifications could be delayed (mitigated by L3 health-check monitors).
- **Maintenance of Milestone Terms:** Purchase teams must diligently configure accurate milestone terms in Purchase Orders rather than using flat lumpsum amounts.

---

## Traceability Matrix

| Architectural Dimension | Specification Target         | Code Implementation                                                                                                                  |
| :---------------------- | :--------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| **BRD Requirements**    | `BR-015`, `BR-017`, `BR-018` | [`planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md`](../planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md)                |
| **FRS Specifications**  | `FR-015`, `FR-017`, `FR-018` | [`planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md`](../planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md)  |
| **Step Specification**  | `STEP_18`                    | [`step_plans/STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.md`](../step_plans/STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.md)    |
| **Domain Services**     | Service Layer                | `VendorPaymentScheduleService`, `VendorPaymentNotificationDaemon`, `VendorPaymentSettlementService`, `VendorPaymentWorkbenchService` |
| **Database Extensions** | 3NF Schema                   | `tabPayment Schedule` (custom fields), `tabPayment Entry` (custom fields), `tabSolar Notification Settings`                          |
| **Testing Standard**    | Automated Suite              | `solar_module/tests/test_step_18_vendor_payment_workbench.py` (Zero DB commits)                                                      |

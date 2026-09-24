# ADR-017: Purchase Invoice 3-Way Match Verification & Admin-Governed Departmental Entry Authorization Architecture

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), **Step 17: Purchase Invoicing & 3-Way Match Verification** (Flow 2: Step 06 of 08 / Global Step 17) is the definitive commercial recognition, statutory tax validation, and general ledger liability gateway within the **Solar EPC Procurement & Vendor Governance Lifecycle (Flow 2)**.

Positioned downstream of Step 15 ([`ADR-015`](./ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md), `tabPurchase Order`) and Step 16 ([`ADR-016`](./ADR-016-MULTI-LOCATION-PURCHASE-RECEIPT-BARCODE-GRN.md), `tabPurchase Receipt`), this stage reconciles vendor commercial tax invoices against contracted PO terms and verified GRN physical receipts before posting accounts payable liabilities to the General Ledger. It unlocks downstream milestone disbursements in Step 18 (`tabPayment Entry` / Vendor Payment Workbench), feeds commercial pricing adherence scores into Step 19 (`tabVendor Rating`), and guarantees 100% compliance with Indian Goods & Services Tax (GST) Input Tax Credit (ITC) matching under GSTR-2B.

Under conventional solar EPC operations and standard out-of-the-box ERPNext implementations, purchase invoicing suffers from four critical systemic failure modes:

1. **Rigid Role Silos vs. Field Realities (The Tri-Department Dilemma):**  
   Standard ERP configurations rigidly restrict Purchase Invoice entry to Accounts personnel. However, across diverse solar EPC project archetypes (Utility-Scale vs. C&I vs. Residential Rooftop), invoice intake realities vary drastically:
   - _Accounts Centralized Model:_ Invoices arrive via email/EDI directly at head office; Accounts verifies GST portal (GSTR-2B) and TDS applicability before booking.
   - _Store Field Inward Model:_ Transporters deliver physical tax invoices, e-Way bills, and delivery challans directly to remote project sites or central stores alongside physical cargo. Requiring remote site personnel to courier physical bills to head office before entry creates a 2–4 week data blackout, misplaced paper bills, and missed early-payment cash discounts.
   - _Purchase Fast-Track Model:_ High-value solar components (PV modules, central inverters, HT power transformers) operate under tight LC or milestone-advance conditions where the Procurement team must book proforma/commercial invoices immediately upon factory dispatch to secure shipment release.  
     When an ERP forces a single rigid persona on all projects, organizations either face severe invoice backlogs or bypass ERP controls through shadow spreadsheets.

2. **The Danger of Uncontrolled Multi-Department Entry (Duplicate Billing Chaos):**  
   Conversely, granting open, uncoordinated PI entry permissions simultaneously to Accounts, Store, and Purchase leads to catastrophic financial distortion:
   - Duplicate invoice booking (e.g. Store enters the bill from the physical truck challan while Accounts enters the PDF received via supplier email).
   - Inadvertent double payments to suppliers.
   - Skewed General Ledger liabilities and duplicate ITC claims leading to statutory GST tax notices and penalties.

3. **Disjointed 3-Way Match Verification (Quantity & Rate Leakage):**  
   Standard ERPs often permit invoices to be created directly from Purchase Orders without validating actual physical receipt, or permit billing against items quarantined/rejected during dock inspection. Furthermore, price creep (small deviations in freight, packing, or unit rates slipped into vendor invoices) frequently passes undetected without deterministic mathematical variance thresholds.

4. **Missing Closed-Loop Downstream Governance:**  
   Standard setups treat invoice booking as an isolated bookkeeping task rather than a dynamic commercial trigger. Submitted invoices fail to automatically update PO milestone payment schedules, fail to notify joint payment workbenches, and fail to feed vendor rating scorecards on contract price adherence.

---

## Decision

We establish an authoritative, comprehensive architectural standard for **Step 17: Purchase Invoice 3-Way Match Verification & Admin-Governed Departmental Entry Authorization Architecture**, extending ERPNext's native `tabPurchase Invoice` and `tabPurchase Invoice Item` within `solar_module` while decoupling domain logic into pure service layers:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         STEP 17: PURCHASE INVOICE (PI) ARCHITECTURE                              │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Solar SCM Settings] ──▶ Admin Supreme Governance: authorized_pi_entry_department              │
│                                (Configurable: 'Accounts' | 'Store' | 'Purchase')                 │
│                                                                                                  │
│                 ┌───────────────────────────────┼────────────────────────────────┐               │
│                 ▼                               ▼                                ▼               │
│        [1. ACCOUNTS ENTRY]              [2. STORE ENTRY]               [3. PURCHASE ENTRY]       │
│       (Accounts Assistant/Off)        (Store Assistant/Mgr)           (Purchase Assistant/Mgr)   │
│                 │                               │                                │               │
│                 └───────────────────────────────┼────────────────────────────────┘               │
│                                                 ▼                                                │
│                                 [Gate 1: Entry Authorization]                                    │
│                                  Asserts session user role                                       │
│                                  matches Admin policy setting                                    │
│                                                 │                                                │
│                                                 ▼                                                │
│                                ┌─────────────────────────────────┐                               │
│                                │   THE 3-WAY MATCHING ENGINE     │                               │
│                                ├─────────────────────────────────┤                               │
│                                │ - Gate 2: Billed Qty ≤ Recd Qty │                               │
│                                │   (Linked Purchase Receipt)     │                               │
│                                │ - Gate 3: Rate Variance ≤ Tol % │                               │
│                                │   (Admin Override if exceeded)  │                               │
│                                │ - Gate 4: Duplicate Bill Check  │                               │
│                                │ - Gate 5: Statutory Tax/TDS     │                               │
│                                └────────────────┬────────────────┘                               │
│                                                 │                                                │
│                                                 ▼                                                │
│                                   [Document Submitted (GL)]                                      │
│                                   Posts Accounts Payable                                         │
│                                                 │                                                │
│                 ┌───────────────────────────────┴────────────────────────────────┐               │
│                 ▼                                                                ▼               │
│   [Step 18: Payment Workbench]                                     [Step 19: Vendor Rating]      │
│   Unlocks Post-GRN / Invoice milestone                             Price Adherence Score         │
│   tranche in Vendor Payment Schedule                               (15% weighting)               │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Admin-Governed Departmental Entry Authorization (`Solar SCM Settings`)

To eliminate multi-department entry chaos while providing the enterprise flexibility required across diverse solar project operations:

1. **Singleton Configuration Schema:**  
   We introduce `authorized_pi_entry_department` (`Select`, default `Accounts`, options: `Accounts`, `Store`, `Purchase`) in the singleton DocType `tabSolar SCM Settings`.
2. **Supreme Administrative Governance:**  
   This configuration is manageable **strictly by `Admin`** (Project Supreme Command) or **`System Manager`** (Developer/Technical Supreme). Operational line personnel are barred from altering this setting.
3. **Departmental Role Enforcement:**
   - When set to **`Accounts`**: Only users holding `Accounts Assistant` or `Accounts Officer` roles (plus `Admin` / `System Manager`) can create, edit, or submit `Purchase Invoice`.
   - When set to **`Store`**: Only users holding `Store Assistant` or `Store Manager` roles (plus `Admin` / `System Manager`) can create, edit, or submit `Purchase Invoice`.
   - When set to **`Purchase`**: Only users holding `Purchase Assistant` or `Purchase Manager` roles (plus `Admin` / `System Manager`) can create, edit, or submit `Purchase Invoice`.
4. **Hard Server-Side Gate:**  
   Enforced in `validate()` and `before_insert()` hooks via `PurchaseInvoiceValidationService`. Any unauthorized attempt raises an explicit `frappe.PermissionError`:  
   `_("Purchase Invoice entry is currently restricted to the '{0}' department by Admin policy in Solar SCM Settings.").format(authorized_dept)`.
5. **Dynamic UI Adaptation:**  
   Frappe Desk quick-action buttons ("Create Purchase Invoice" in PO and GRN) and `/solar` Vue SPA navigation cards inspect `frappe.boot.solar_scm_settings.authorized_pi_entry_department` and dynamically disable or display clear guidance based on the user's active role.
6. **Policy Audit Trail (`tabSolar SCM Policy Log`):**  
   Every policy transition by Admin captures timestamp, previous department, new department, user ID, and mandatory operational justification.

### 2. Deterministic 3-Way Match Engine (PO vs GRN vs PI)

Every submitted Purchase Invoice must undergo automated line-level 3-way reconciliation:

1. **Quantity Match Gate (PO vs GRN vs PI):**
   - Billed quantity (`qty`) in `tabPurchase Invoice Item` must be linked to a valid `Purchase Receipt Item` (`custom_grn_item_ref`).
   - Asserts: $\sum \text{Billed Qty} \le \text{Accepted Qty}$ in linked GRN.
   - Billing against items routed to `Quarantine / Rejection - SEPC` is strictly prohibited.
2. **Price Variance Gate (PO vs PI):**
   - Asserts that unit rates in PI do not exceed PO contracted unit rates beyond the allowed tolerance:
     $$\Delta_{\text{rate}} = \frac{|\text{Billed Rate} - \text{PO Rate}|}{\text{PO Rate}} \times 100 \le \text{Tolerance \%}$$
   - Configurable in `Solar SCM Settings.pi_rate_variance_tolerance_percent` (default $0.0\%$, max permissible $\pm 1.0\%$).
   - If variance exceeds tolerance, the document transitions to `Discrepancy / Variance Hold`. It cannot be submitted without explicit **Admin Price Override** sign-off with recorded justification.
3. **Duplicate Invoice Lockout Gate:**
   - Validates uniqueness on composite key `(supplier, bill_no, fiscal_year)`. Prevents accidental or fraudulent double-entry across fiscal periods.
4. **Statutory Tax & TDS Verification Gate:**
   - Enforces HSN code and GST rate consistency against the PO baseline.
   - For commercial solar EPC contracts, validates proper application of the statutory 70:30 Goods vs Service tax split.
   - Enforces Section 194Q TDS / 206C(1H) TCS deduction tags.

### 3. Turnaround SLA Engine (24-Hour TAT)

- **Clock Inception:** Triggered upon physical invoice receipt / GRN completion.
- **Target SLA:** 24 operational hours (configurable in `Solar SCM Settings.pi_turnaround_sla_hours`).
- **Redis Worker Daemon:** Background task `solar_module.tasks.recompute_pi_slas` checks active drafts every 15 minutes.
- **Delay Audit Log:** Breaches transition the invoice to `custom_sla_status = 'Breached / Overdue'`, requiring mandatory justification in `custom_delay_reason_table` (`tabRemark-Delay Log`) before submission.

### 4. Downstream Automated Integrations

1. **Step 18 (Vendor Payment Workbench):** Updates `tabPurchase Order` milestone terms, releasing the invoice payment tranche into `tabVendor Payment Workbench` for scheduled disbursement.
2. **Step 19 (Vendor Performance Rating):** Dispatches asynchronous event to `VendorRatingService`, logging price adherence score ($15\%$ weighting in overall supplier scorecard).
3. **General Ledger (Core Accounts):** Posts accounting entries crediting Accounts Payable (`Creditors - SEPC`) and debiting Stock Received But Not Billed / Expense accounts.

---

## Alternatives Considered

### 1. Hardcode PI Creation Exclusively to Accounts

- _Pros:_ Maximum orthodox financial orthodoxy.
- _Cons:_ Creates massive paperwork backlogs for remote solar sites where physical invoices arrive with transporter trucks. Invoices sit unentered in site offices for weeks, suppliers freeze subsequent dispatches, and early-payment cash discounts are lost.
- _Rejected:_ Modern solar EPC operations require the flexibility to authorize Store or Purchase teams when project conditions dictate.

### 2. Allow Open, Unrestricted Entry by Accounts, Store, and Purchase Simultaneously

- _Pros:_ Maximum convenience; anyone can enter bills anytime.
- _Cons:_ Disastrous for financial and statutory integrity. Inevitably causes duplicate invoice entries, double payments, conflicting GL liabilities, and audit disallowances under GST GSTR-2B.
- _Rejected:_ Admin-governed single-department authorization provides agility while maintaining absolute operational discipline.

### 3. Post-Facto Invoice Rerouting & Re-Approval Workflow

- _Pros:_ Any department enters a draft; Accounts reviews and submits.
- _Cons:_ Produces massive "draft dumping" where incomplete, erroneous drafts sit unowned in queues, obscuring true corporate liability and SLA countdowns.
- _Rejected:_ Upfront departmental authorization ensures that only designated, accountable teams initiate invoice entries.

---

## Consequences

### Positive

- **Operational Flexibility with Administrative Control:** Enables the executive leadership (`Admin`) to tailor invoicing responsibility dynamically to project scale, site remoteness, or procurement velocity without code changes.
- **Zero Duplicate Billing:** Eliminates inter-departmental duplicate entries and duplicate GST ITC claims.
- **Audit-Proof 3-Way Matching:** Programmatically guarantees that no vendor is paid for goods not physically accepted or at rates unapproved in purchase orders.
- **Sub-24-Hour Invoice Turnaround:** Enforced SLA timers and delay logging eliminate vendor payment disputes and maintain healthy supplier relationships.
- **Automated SCM Closed-Loop:** Seamless handoff into Step 18 payment scheduling and Step 19 vendor rating.

### Negative / Trade-offs

- **Administrative Overhead:** Shifting entry authorization between departments requires an Admin action and documented justification.
- **Temporary Lockout on Role Transitions:** If Admin switches authorization from Accounts to Store, pending Accounts drafts must be completed or handed over under administrative supervision.

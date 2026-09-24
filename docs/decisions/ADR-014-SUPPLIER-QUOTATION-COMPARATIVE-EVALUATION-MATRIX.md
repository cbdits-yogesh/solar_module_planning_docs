# ADR-014: Supplier Quotation Comparative Evaluation Matrix & Landed Cost Governance Architecture

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), **Step 14: Supplier Quotation Comparative Evaluation Matrix** (Flow 2: Step 03 of 08 / Global Step 14) is the central commercial evaluation, landed cost normalization, and supplier award decision engine. It directly consumes supplier bids ingested via Step 13 (Supplier Request for Quotation — RFQ) and determines the formal purchase award that spawns Step 15 (Purchase Order Placement).

Under legacy solar EPC procurement practices and standard ERP implementations, the quotation evaluation process suffered from severe structural deficiencies, financial leakage, and compliance blindspots:

1. **Flawed Base-Price Comparisons (Hidden Landed Cost Leakage):** Purchasing buyers routinely evaluated suppliers solely on raw quoted unit rates. In solar EPC procurement, commercial terms diverge dramatically:
   - Supplier A quotes an ex-factory basic price of ₹18.20/Wp with freight payable extra at ₹0.85/Wp, transit insurance extra at 0.15%, and 18% GST.
   - Supplier B quotes FOR Site (freight and insurance included) at ₹19.10/Wp with 12% GST.
   - Supplier C quotes ex-works basic price with unstated unloading terms.
     Comparing raw unit prices without algorithmic landed cost normalization ($ \text{Basic} + \text{Freight} + \text{Insurance} + \text{P\&F} + \text{Non-creditable Taxes} + \text{Site Offloading} $) resulted in false "L1" selections, creating unexpected 4–7% cost overruns upon logistics invoicing.
2. **Subjective Sourcing & Buyer Bias (Maverick Purchasing):** Purchasing staff frequently awarded orders to favored vendors under the guise of "better relationship" or subjective quality claims without structured justification. Without an immutable comparison matrix, management had zero audit trail explaining why higher bids were accepted.
3. **Lead Time Blindspots Causing Site Stoppages:** Solar EPC projects are bound by strict liquidated damages (LD) and DISCOM statutory synchronization deadlines (Stage 10). Selecting an L1 vendor with a 45-day manufacturing lead time over an L2 vendor with a 7-day dispatch lead time to save 0.5% in purchase cost often resulted in site installation crews idling for weeks, triggering massive overall project delay costs.
4. **Disconnection from Historical Vendor Quality:** Bids were evaluated in isolation from historical performance data. Delinquent suppliers with high historical rejection rates or chronic delivery delays were awarded contracts over proven Tier 1 vendors simply because their paper quote was marginally lower.
5. **Lack of Immutable Audit Trails in Standard ERP Reports:** Standard ERPNext provides a client-side ephemeral report ("Quotation Comparison"). This report cannot be submitted, version-controlled, digitally signed, or locked. Procurement decisions could be altered after the fact, leaving no regulatory or audit trail for ISO 9001, Sarbanes-Oxley, or internal EPC commercial audits.
6. **Bid Tampering in High-Value Tenders:** Standard systems lacked an unsealing gate for sealed bids. In tenders exceeding ₹1,000,000, unmasked quotations could be viewed selectively by buyers prior to deadline closure, compromising tender confidentiality.
7. **Evaluation Latency Bottlenecks:** Submitted quotations sat in buyer inboxes for days without structured turnaround time (SLA) tracking, delaying equipment procurement and delaying project commissioning.

---

## Decision

We establish an authoritative, comprehensive architectural standard for **Step 14: Supplier Quotation Comparative Evaluation Matrix**, extending ERPNext's native `tabSupplier Quotation` and introducing a dedicated, submittable governance DocType **`tabQuotation Comparison Matrix`** (`is_submittable = 1`) within `solar_module`:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                          STEP 14: SUPPLIER QUOTATION EVALUATION ARCHITECTURE                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Step 13: RFQ Dispatched & Quotes Ingested via Portal / Desk]                                  │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Verification Gate 1: Sealed Bids Unsealing Check]                                             │
│   • Asserts sealed bids unsealing ceremony executed if tender > ₹10L                             │
│   • Validates active validity dates (today <= valid_till)                                        │
│           │                                                                                      │
│           ▼                                                                                      │
│   [True Landed Cost Normalization Engine]                                                        │
│   • Normalizes Base Rate + P&F + Freight + Insurance + Taxes - Input Tax Credit (ITC)            │
│   • Computes Effective Net Landed Cost per Unit and per BOM Line                                 │
│           │                                                                                      │
│           ▼                                                                                      │
│   [100-Point Multi-Factor Scoring Algorithm]                                                     │
│   • Commercial Landed Cost (50%): Dynamic L1 ratio scaling                                       │
│   • Delivery Lead Time Feasibility (25%): Penalty curve vs project milestone requirement         │
│   • Historical Vendor Rating (15%): Direct injection from Step 19 Scorecard                      │
│   • Commercial Terms & Warranty (10%): Credit days + warranty duration                           │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Verification Gate 2: Non-L1 Selection Governance]                                             │
│   • If selected supplier is L1: Streamlined standard approval path                               │
│   • If selected supplier is Non-L1: Enforces mandatory justification (min 40 chars)              │
│     and explicit authorization by Purchase Manager or Admin                                      │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Submit Quotation Comparison Matrix (docstatus = 1)]                                           │
│   • Freezes line-item comparison snapshot, scores, rankings, and award decision                  │
│   • Closes 48-Hour Evaluation SLA clock (or flags Overdue with mandatory delay reason)           │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Programmatic Downstream PO Instantiation] ──▶ Step 15: Purchase Order Placement               │
│   • Spawns ERPNext tabPurchase Order pre-populated with winning rates and delivery terms         │
│   • Automatically rejects non-awarded quotes and triggers regret communication                   │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Dual-Entity Data Architecture: Extended Native Quotes & Dedicated Comparison Matrix

To maintain 100% ERPNext core compatibility while achieving enterprise governance:

- **`tabSupplier Quotation` (Core Extension):** Standard ERPNext transactional records are extended with solar logistics fields (`custom_rfq_reference`, `custom_freight_charges`, `custom_transit_insurance`, `custom_unloading_charges`, `custom_landed_cost_unit`, `custom_net_effective_total`, `custom_promised_lead_time_days`, `custom_warranty_months`, `custom_is_sealed`).
- **`tabQuotation Comparison Matrix` (Standalone Submittable DocType):** Rather than relying on an ephemeral client-side report, a permanent submittable DocType (`is_submittable = 1`) is introduced. It captures the side-by-side snapshot of all competing bids for an RFQ, computed landed costs, scoring parameters, evaluator notes, and the formal award decision. Submitting this record permanently freezes the evaluation audit trail.

### 2. True Landed Cost Normalization Engine

All incoming quotations are mathematically normalized to eliminate hidden logistics and tax discrepancies:
$$\text{Landed Cost per Unit} = \text{Basic Rate} + \frac{\text{P\&F} + \text{Freight} + \text{Insurance} + \text{Unloading}}{\text{Quantity}} + \text{Non-Creditable Tax}$$
$$\text{Net Effective Cost} = \text{Landed Cost per Unit} - \text{Eligible GST Input Tax Credit (ITC)}$$
This guarantees that an ex-factory quote with high freight is objectively compared against an FOR-Site quote where freight is absorbed by the vendor.

### 3. 100-Point Multi-Factor Scoring Algorithm

Procurement awards are evaluated across four weighted dimensions:

1. **Commercial Landed Cost Score ($W_{\text{cost}} = 50\%$):**
   $$S_{\text{cost}} = \left(\frac{\text{Landed Cost}_{L1}}{\text{Landed Cost}_{\text{vendor}}}\right) \times 50$$
2. **Delivery Lead Time Score ($W_{\text{lead}} = 25\%$):**
   $$S_{\text{lead}} = \max\left(0, 25 \times \left(1 - \frac{\text{Lead Time}_{\text{vendor}} - \text{Lead Time}_{\min}}{\text{Target Required Lead Time}}\right)\right)$$
3. **Vendor Quality & Performance Score ($W_{\text{vendor}} = 15\%$):**
   Pulls real-time 4-factor rating score from Step 19 (`tabVendor Rating`):
   $$S_{\text{vendor}} = \text{Rating Score}_{\text{Step 19}} \times 0.15$$
4. **Commercial Terms & Warranty Score ($W_{\text{terms}} = 10\%$):**
   Evaluates payment terms (credit days vs advance) and equipment warranty duration (e.g. 10/25-year solar PV module warranty).
   $$\text{Composite Evaluation Score} = S_{\text{cost}} + S_{\text{lead}} + S_{\text{vendor}} + S_{\text{terms}} \quad (0 - 100)$$

### 4. Enforced Non-L1 Selection Governance Gate

To eliminate buyer favoritism and maverick procurement:

- The system automatically identifies the **L1 Landed Cost Supplier**.
- If the purchasing evaluator selects a supplier other than L1 (e.g., L2 or L3 selected because of immediate 48-hour delivery or Tier 1 Bloomberg NEF tiering):
  - The checkbox `is_l1_selected` is evaluated as `0`.
  - The field `non_l1_justification` becomes **strictly mandatory** (minimum 40 characters).
  - The document requires explicit digital sign-off from `Purchase Manager` or `Admin`. Saving or submitting without manager sign-off raises an immediate `ValidationError`.

### 5. Sealed Bid Integration & Unmasking Protocol

For high-value tenders initiated in Step 13 with `custom_sealed_bids = 1`:

- The matrix creation endpoint verifies that the bid deadline has passed and the formal unsealing ceremony has been executed (`custom_bids_unsealed = 1`).
- Premature attempts to generate a comparison matrix while bids remain sealed are hard-blocked with an authorization error.

### 6. 48-Hour Evaluation Turnaround SLA & Redis Daemon

- An automated 48-hour SLA clock begins upon RFQ deadline closure or tender unsealing.
- A background worker (`solar_module.tasks.monitor_quotation_evaluation_sla`) scans open evaluations every 15 minutes.
- If the matrix is not submitted within 48 hours, the status transitions to `Overdue`, alerting the `Purchase Manager` and requiring mandatory justification in `tabRemark-Delay Log`.

### 7. Programmatic Downstream PO Instantiation (Step 15 Handoff)

Upon formal submission of the `Quotation Comparison Matrix`:

- An ERPNext `tabPurchase Order` is programmatically instantiated for the awarded supplier with exact normalized rates, payment terms, and delivery schedules.
- Bid line items are locked to prevent duplicate PO issuance.
- Non-awarded quotes transition to `Lost` / `Rejected`, and regret notifications are dispatched via transactional email/WhatsApp.

---

## Alternatives Considered

### Alternative 1: Using Standard ERPNext Quotation Comparison Report Only

- **Pros:** Zero custom DocType development; uses existing Frappe Desk reporting framework.
- **Cons:** Standard report is purely visual and ephemeral. It cannot be submitted, cannot enforce approval gates, cannot store non-L1 justifications, cannot calculate multi-factor composite scores, and leaves zero audit trail for ISO/EPC compliance.
- **Rejected:** Fails enterprise governance, risk mitigation, and auditability requirements.

### Alternative 2: Pure L1 Cost-Based Auto-Award

- **Pros:** Simple logic; always picks the lowest dollar quote.
- **Cons:** Ignores delivery lead times, project synchronization milestones, component warranties, and supplier quality ratings. In solar EPC, an L1 module delivery delayed by 3 weeks costs 10x more in installation crew downtime and DISCOM delay penalties than the initial price difference.
- **Rejected:** Unacceptable operational risk for utility and commercial solar EPC projects.

### Alternative 3: Manual Spreadsheet Upload (Offline Excel Matrix)

- **Pros:** Familiar to legacy purchasing buyers.
- **Cons:** High error rate in formula manipulation, prone to tampering, disconnected from ERP purchase order generation, and lacks real-time vendor scorecard integration.
- **Rejected:** Perpetuates the exact legacy silos and manual transcription bottlenecks being eradicated.

---

## Consequences

### Positive Consequences

- **True Landed Cost Accuracy:** Eliminates unexpected freight and tax variances, protecting project gross margins by 3–5%.
- **Zero Maverick Purchasing:** Mandatory non-L1 justification and managerial authorization eliminate buyer favoritism and enforce procurement transparency.
- **Project Schedule Protection:** Multi-factor scoring factors in lead time urgency, preventing site work stoppages and DISCOM deadline penalties.
- **Audit-Proof Decision Trail:** Every award is backed by an immutable, submittable comparison record with complete timestamping and scoring history.
- **Seamless Downstream Flow:** 1-click PO creation eliminates data re-entry latency and transcription errors.

### Negative / Trade-Off Consequences

- **Initial Configuration Overhead:** Requires maintaining freight estimates, delivery location types, and vendor rating weights.
- **Process Rigor:** Buyers cannot quickly place verbal or informal purchase orders without generating and submitting the comparative matrix.

---

## Compliance & Invariants

1. **Role Standard:** Adheres strictly to the **Zero "User" Suffix Rule** (`Purchase Assistant`, `Purchase Manager`, `Store Manager`, `Project Engineer`, `Admin`).
2. **Authority Standard:** Clean boundary between `Admin` (Project Supreme Command) and `System Manager` (Framework Supreme / Developer).
3. **Database Integrity:** 3NF relational schema with foreign key cascades and indexes on `(rfq_reference, evaluation_status)`.
4. **Testing Protocol:** 100% automated test coverage inheriting `FrappeTestCase` with zero database commits (`frappe.db.commit()` prohibited).

# ADR-019: Vendor Performance Rating Scorecard, 4-Factor Balanced Evaluation Engine & Two-Tier Admin Supreme Approval Architecture

## Status

Accepted

## Date

2026-09-25

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), **Step 19: Vendor Performance Rating Scorecard** (Flow 2: SCM, Store, Purchase & Vendor Procurement Lifecycle — Step 08 of 08 / Global Step 19) constitutes the definitive supplier evaluation, quality assurance governance, and strategic procurement intelligence engine.

Positioned downstream of Step 15 ([`ADR-015`](./ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md), `tabPurchase Order`), Step 16 ([`ADR-016`](./ADR-016-MULTI-LOCATION-PURCHASE-RECEIPT-BARCODE-GRN.md), `tabPurchase Receipt`), Step 17 ([`ADR-017`](./ADR-017-PURCHASE-INVOICE-3WAY-MATCH-ADMIN-ENTRY-GOVERNANCE.md), `tabPurchase Invoice`), and Step 18 ([`ADR-018`](./ADR-018-JOINT-VENDOR-PAYMENT-MONITORING-WORKBENCH.md), `tabPayment Entry` / Workbench), this stage synthesizes operational execution data into an objective, data-driven supplier scorecard that directly governs future procurement shortlists and contract awards.

In utility-scale and commercial rooftop solar EPC projects, equipment procurement represents 70%–80% of total capital expenditure. Key equipment (tier-1 bifacial PV modules, string/central inverters, galvanized module mounting structures, solar DC/HT cabling, and transformers) directly dictates 25-year plant performance, degradation rates, and statutory grid synchronization timelines (Step 10). Under legacy practices and standard ERP implementations, supplier management suffers from four major systemic vulnerabilities:

1. **Subjective Procurement Bias & Single-Vendor Dependency:**  
   Purchase decisions frequently rely on personal buyer relationships, manual negotiation memory, or unverified supplier claims rather than empirical operational performance. Poorly performing vendors continue receiving Requests for Quotation (RFQs) and Purchase Orders despite chronic delivery delays or quality rejections.

2. **Unpenalized Delivery Delays & Logistics Blindspots:**  
   Suppliers routinely promise aggressive delivery lead times during RFQ bidding to win contracts, but deliver weeks behind schedule. Because delivery performance is rarely quantified against contractual PO promised dates (`schedule_date`), recurring delays go unpenalized, directly causing site idle labor, crane demobilization charges, and DISCOM statutory SLA breaches.

3. **Defect Slippage & Quality Disconnect:**  
   Quality issues captured during goods receipt (e.g., transit breakage, micro-cracks in PV modules, inverter factory acceptance test failures, defective galvanized coating) are resolved piecemeal via credit notes or rework without impacting the vendor's enterprise rating. Consequently, high-risk suppliers continue shipping sub-standard components to solar sites.

4. **Disconnected Upstream Procurement Loop:**  
   Even when vendor issues are recognized by site teams, the insights remain trapped in warehouse logs or email threads. Upstream procurement teams drafting RFQs (Step 13) or evaluating bids in the Quotation Comparison Matrix (Step 14) operate in total isolation from historical vendor quality and delivery reliability metrics.

---

## Decision

We establish an authoritative, comprehensive architectural standard for **Step 19: Vendor Performance Rating Scorecard, 4-Factor Balanced Evaluation Engine & Two-Tier Admin Supreme Approval Architecture**.

Under this governance model:

- **Purchase Manager Filling & Technical Evaluation:** The **`Purchase Manager`** (supported by the `Quality Engineer`) acts as the operational evaluator who reviews automated transactional metrics (OTD, rejections, billing deviations), evaluates qualitative service responsiveness, and submits the scorecard for executive approval.
- **Admin Supreme Approval Cockpit & Notification:** The **`Admin`** (Project Supreme Command) is automatically notified upon scorecard submission and holds the supreme, exclusive authority to execute one of three actions:
  1. **Approve:** Formally submits the scorecard (`docstatus = 1`), permanently freezing the evaluation and updating the supplier's tier and rolling average on `tabSupplier`.
  2. **Reject:** Rejects the evaluation with mandatory justification, leaving supplier status unchanged.
  3. **Ask for Reason & Re-Rate:** Returns the scorecard to the Purchase Manager (`stage_status = 'Returned for Re-Rating'`) with specific inquiry notes, requiring re-evaluation and resubmission.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│             STEP 19: TWO-TIER VENDOR RATING & ADMIN SUPREME APPROVAL ARCHITECTURE                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Step 15: Purchase Order]   ──▶ Contractual Schedule Date, Agreed Unit Rates, Milestone Terms  │
│   [Step 16: Barcode GRN]      ──▶ Actual Posting Date, Accepted vs Rejected Qty, MTCs            │
│   [Step 17: Purchase Invoice] ──▶ Invoiced Rates, Variance Analysis, Statutory Tax Compliance   │
│   [Step 18: Payment Desk]     ──▶ Settlement Turnaround, Credit Period Adherence                 │
│                                                   │                                              │
│                                                   ▼                                              │
│                   ┌────────────────────────────────────────────────────────────┐                 │
│                   │        TRANSACTIONAL & PERIODIC RATING ENGINE TRIGGER      │                 │
│                   │   (Auto-spawned on GRN/PI closure OR Monthly Batch Daemon) │                 │
│                   └────────────────────────────────────────────────────────────┘                 │
│                                                   │                                              │
│                                                   ▼                                              │
│                   ┌────────────────────────────────────────────────────────────┐                 │
│                   │          TIER 1: PURCHASE MANAGER EVALUATION DESK          │                 │
│                   ├────────────────────────────────────────────────────────────┤                 │
│                   │ • Automated Metrics: OTD (35%) + Quality (35%) + Price(15%)│                 │
│                   │ • Qualitative Scoring: Service Responsiveness (15%)        │                 │
│                   │ • Executive Commentary: Mandatory justification (≥20 chars)│                 │
│                   │ • Click: [Submit for Admin Approval]                       │                 │
│                   └────────────────────────────────────────────────────────────┘                 │
│                                                   │                                              │
│                                                   ▼                                              │
│                               [REAL-TIME NOTIFICATION DISPATCH TO ADMIN]                         │
│                                (In-App Bell Alert, Email, WhatsApp Integration)                  │
│                                                   │                                              │
│                                                   ▼                                              │
│                   ┌────────────────────────────────────────────────────────────┐                 │
│                   │       TIER 2: ADMIN SUPREME APPROVAL DECISION GATEWAY      │                 │
│                   │             (Admin Cockpit / Decision Buttons)             │                 │
│                   ├──────────────────────────────┬─────────────────────────────┤                 │
│                   │                              │                             │                 │
│                   ▼                              ▼                             ▼                 │
│         [ACTION 1: APPROVE]             [ACTION 2: REJECT]            [ACTION 3: RE-RATE]        │
│         - docstatus = 1                 - stage_status = Rejected     - Enter inquiry notes      │
│         - Freezes scorecard             - Logs rejection reason       - Status: Returned for     │
│         - Updates tabSupplier           - Closes evaluation             Re-Rating                │
│         - Feeds Step 13 & 14            - Zero supplier impact        - Alerts Purchase Manager  │
│                   │                                                            │                 │
│                   │                                                            ▼                 │
│                   │                                              [PM RE-EVALUATES & RESUBMITS]   │
│                   │                                                                              │
│                   ▼                                                                              │
│   ┌──────────────────────────────────────────────┐                                               │
│   │        CLOSED-LOOP PROCUREMENT FEEDBACK      │                                               │
│   ├──────────────────────────────────────────────┤                                               │
│   │ 1. tabSupplier Master: Rolling score & Tier  │                                               │
│   │ 2. Step 13 RFQ: Auto-shortlist Tier 1/2      │                                               │
│   │ 3. Step 13 RFQ: Hard-block Blacklisted       │                                               │
│   │ 4. Step 14 Matrix: 15% Landed Cost Weight    │                                               │
│   │ 5. Supplier Portal: Formal Scorecard PDF     │                                               │
│   └──────────────────────────────────────────────┘                                               │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1. The 4-Factor Balanced Scorecard Mathematical Model

The evaluation engine calculates an overall score ($S_{total} \in [0, 100]$) based on four weighted criteria, whose weights ($W_i$) are administratively configurable in `tabSolar SCM Settings` ($W_{OTD} + W_{QRR} + W_{PACI} + W_{SRSC} = 100\%$):

$$S_{total} = (W_{OTD} \times S_{OTD}) + (W_{QRR} \times S_{QRR}) + (W_{PACI} \times S_{PACI}) + (W_{SRSC} \times S_{SRSC})$$

#### Factor 1: On-Time Delivery (OTD) — Default Weight: 35%

Automated calculation comparing the contractual promised delivery date in Step 15 `Purchase Order Item.schedule_date` against the physical goods receipt timestamp in Step 16 `Purchase Receipt.posting_date`:

- Let $\Delta_{days} = \text{Date}_{GRN} - \text{Date}_{PO\_Promised}$.
- If $\Delta_{days} \le 0$ (On-time or early delivery): $S_{OTD} = 100\%$.
- If $\Delta_{days} > 0$ (Delayed delivery), a graduated delay penalty curve applies:
  - $1 \le \Delta_{days} \le 3$: $S_{OTD} = 85\%$
  - $4 \le \Delta_{days} \le 7$: $S_{OTD} = 65\%$
  - $8 \le \Delta_{days} \le 14$: $S_{OTD} = 40\%$
  - $\Delta_{days} > 14$: $S_{OTD} = 0\%$
- For multi-item deliveries, line items are normalized by total received commercial value:
  $$S_{OTD} = \frac{\sum (Item\_Amount_i \times S_{OTD, i})}{\sum Item\_Amount_i}$$

#### Factor 2: Quality & Rejection Rate (QRR) — Default Weight: 35%

Automated calculation derived from the physical inspection and barcode scanning results recorded in Step 16 `Purchase Receipt`:

- Basic Quality Ratio:
  $$S_{base\_quality} = \left( \frac{\sum Qty_{accepted}}{\sum Qty_{received}} \right) \times 100$$
- Critical Equipment Penalty: For major solar assets (PV modules, inverters, power transformers), latent defects or test failures (e.g., flash test underperformance $> 3\%$, EL micro-cracking $> 1\%$, insulation resistance failure) trigger a critical quality penalty ($P_{critical} = 25$ points), ensuring sub-standard lots are heavily penalized:
  $$S_{QRR} = \max(0, S_{base\_quality} - P_{critical})$$

#### Factor 3: Price Adherence & Commercial Integrity (PACI) — Default Weight: 15%

Evaluates contract price stability between Step 15 `Purchase Order` and Step 17 `Purchase Invoice`:

- Base Price Adherence: If invoiced unit rate $\le$ PO contracted unit rate with zero unauthorized variations: $S_{PACI} = 100\%$.
- Rate Escalation Penalty: If invoiced unit rate exceeds PO rate without an approved amendment, $S_{PACI}$ decreases by 5% for every 1% price variance.
- Debit Note Deductions: Commercial disputes resulting in supplier debit notes or billing rejections deduct 10 points per occurrence.

#### Factor 4: Service Responsiveness & SCM Collaboration (SRSC) — Default Weight: 15%

Qualitatively evaluated by the **Purchase Manager** and **Quality Engineer** across four 25-point operational dimensions (Total = 100 points):

1. **RFQ Responsiveness & Commercial Flexibility (0–25 pts):** Speed of quotation submission, willingness to match market rates, transparency in freight/lead-time commitments.
2. **Technical & Statutory Documentation Speed (0–25 pts):** Timeliness of Mill Test Certificates (MTC), PV module flash reports, warranty certificates, and e-way bills.
3. **RMA & Warranty Turnaround (0–25 pts):** Speed of replacing rejected goods, dispatch of warranty spares, and resolution of site technical queries.
4. **Account Management & Proactive Communication (0–25 pts):** Proactive notifications of manufacturing bottlenecks, transparency in shipment tracking, and relationship integrity.

---

### 2. Multi-Tier Supplier Classification & Upstream Governance

The calculated score dynamically categorizes suppliers into standardized enterprise performance tiers, updating `tabSupplier.custom_vendor_tier`:

| Tier Level | Designation                    | Score Range          | Operational Privileges & System Action                                                                                                                  | Upstream RFQ & PO Governance                                                                                             |
| :--------- | :----------------------------- | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------- |
| **Tier 1** | **Preferred / Strategic**      | $\ge 85.0\%$         | • Eligible for multi-project annual rate contracts.<br>• Priority payment processing in Step 18.<br>• Waived pre-dispatch factory inspection (FAT).     | • Auto-suggested / pre-selected in Step 13 RFQs.<br>• Receives 5% commercial score bonus in Step 14 Comparison Matrix.   |
| **Tier 2** | **Approved / Standard**        | $70.0\% - 84.9\%$    | • Standard procurement eligible.<br>• Standard 3-way match and payment terms.                                                                           | • Included in regular RFQ competitive bidding pools.<br>• Standard evaluation in Step 14 Comparison Matrix.              |
| **Tier 3** | **Probationary / Conditional** | $50.0\% - 69.9\%$    | • Restricted to non-critical BOM equipment.<br>• Mandatory 100% pre-dispatch inspection (FAT).<br>• PO value capped at ₹10 Lakhs unless Admin approved. | • Cannot be sole-source awarded.<br>• Requires written justification by Purchase Manager to issue RFQ.                   |
| **Tier 4** | **Disqualified / Blacklisted** | $< 50.0\%$ or Breach | • Complete commercial freeze.<br>• Barred from receiving RFQs or Purchase Orders.<br>• Pending payments subject to audit review.                        | • Hard blocked by system validation gates in Step 13 and Step 15.<br>• Removal requires formal `Admin` Supreme approval. |

---

### 3. Two-Tier Approval Architecture & The Admin Tri-Action Decision Gateway

To ensure complete managerial accountability and executive governance, rating execution is bifurcated into two distinct operational phases:

1. **Phase 1: Purchase Manager Filling & Review:**  
   The `Purchase Manager` reviews the automatically calculated OTD, Quality, and Price scores, scores the qualitative Service checklist, inputs executive commentary ($\ge 20$ chars), and clicks `[Submit for Admin Approval]`. The document state transitions to `Pending Admin Approval`, triggering immediate notification dispatch.

2. **Phase 2: Admin Supreme Decision Gateway:**  
   The `Admin` (Project Supreme Command) receives the notification and reviews the completed scorecard on the Admin Approval Cockpit. The Admin executes one of three decisive actions:
   - **Action 1: Approve Scorecard (`admin_approve_vendor_rating`):**  
     Admin formally approves the scorecard. The controller executes `doc.submit()` (`docstatus = 1`), permanently freezing the document. `VendorTierGovernanceService` immediately updates `tabSupplier.custom_vendor_tier` and rolling performance metrics.
   - **Action 2: Reject Scorecard (`admin_reject_vendor_rating`):**  
     Admin rejects the scorecard due to administrative invalidity or procedural defect. The document transitions to `Rejected`, requiring mandatory rejection remarks ($\ge 15$ chars). Supplier tier remains untouched.
   - **Action 3: Ask for Reason & Re-Rate (`admin_return_for_rerating`):**  
     Admin challenges the ratings (e.g. _“Verify why transit delay was attributed to supplier when port congestion was documented”_). The Admin inputs mandatory inquiry notes. The document state reverts to `Returned for Re-Rating`, `re_rating_count` increments by 1, and an urgent notification is dispatched to the Purchase Manager to adjust scores and resubmit.

---

### 4. Enforced Server-Side Verification Gates

To prevent manipulation and guarantee governance integrity, the system enforces three hard gates:

- **Gate 1 (Transaction Linkage & Immutability Gate):**  
  Asserts that a transactional scorecard links to submitted, non-cancelled ERPNext transactions (`Purchase Order`, `Purchase Receipt`, or `Purchase Invoice`). Prevents speculative or duplicate rating generation.
- **Gate 2 (Mandatory Qualitative Review & Service Gate):**  
  Prevents transitioning to `Pending Admin Approval` if the Purchase Manager has not completed all 4 service evaluation criteria or left qualitative commentary blank ($\ge 20$ characters required).
- **Gate 3 (Admin Supreme Decision & Authority Gate):**  
  Only users holding the **`Admin`** role (Project Supreme Command) or Frappe's **`System Manager`** are permitted to execute `approve`, `reject`, or `return_for_rerating`. If a standard Purchase Manager attempts to directly submit or finalize a scorecard, the system raises a strict `frappe.PermissionError`.

---

## Alternatives Considered

### 1. Purchase Manager Direct Submission Without Admin Approval

- **Pros:** Faster execution cycle; reduces administrative overhead for executive leadership.
- **Cons:** Leaves high-stakes supplier tiering vulnerable to buyer bias, conflicts of interest, or unverified penalties that could sever relationships with critical solar manufacturers (Waaree, Adani, Sungrow); lacks executive check-and-balance.
- **Rejected:** Fails the enterprise governance standard required for utility and C&I solar procurement.

### 2. Standard Out-of-the-Box ERPNext Supplier Scorecard

- **Pros:** Native feature; zero custom schema.
- **Cons:** Rigid criteria; lacks solar EPC domain parameters; offers zero tri-action Admin decision mechanism (no "Ask for Reason & Re-Rate" capability).
- **Rejected:** Lacks the required domain intelligence and collaborative workflow.

---

## Consequences

### Positive Consequences

- **Executive Alignment & Audit Integrity:** Guarantees that all supplier promotions, demotions, and blacklisting decisions are formally authorized by project leadership (`Admin`).
- **Constructive Review Loop:** The "Ask for Reason & Re-Rate" mechanism enables productive dialogue between executive leadership and procurement teams without cancelling transactions.
- **Zero Rogue Allocations:** Synchronized supplier tiers protect projects from unapproved or underperforming vendors.
- **Complete Role Accountability:** Preserves the `Purchase Manager` as the operational evaluator while enshrining the `Admin` as the supreme approval authority.

### Negative / Trade-Off Consequences

- **Turnaround Latency:** Introducing an Admin approval step adds a secondary review window (governed by the 48-hour SLA).
- **Notification Discipline:** Requires executive leadership (`Admin`) to process approval notifications promptly to keep supplier registers current.

---

## Traceability Matrix

| Architectural Dimension | Specification Target         | Code Implementation Reference                                                                                                                   |
| :---------------------- | :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| **BRD Requirements**    | `BR-016`, `BR-017`, `BR-018` | [`planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md`](../planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md)                           |
| **FRS Specifications**  | `FR-016`, `FR-017`, `FR-018` | [`planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md`](../planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md)             |
| **Step Specification**  | `STEP_19`                    | [`step_plans/STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.md`](../step_plans/STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.md)                 |
| **Domain Services**     | Service Layer                | `VendorRatingCalculationService`, `VendorTierGovernanceService`, `VendorScorecardSyncService`, `VendorRatingNotificationService`                |
| **Database Entities**   | 3NF Schema                   | `tabVendor Performance Rating`, `tabVendor Rating Item Breakdown`, `tabVendor Rating Service Checklist`, `tabSupplier`, `tabSolar SCM Settings` |
| **Automated Testing**   | Quality Assurance            | `solar_module/tests/test_step_19_vendor_rating_scorecard.py` (Zero DB commits)                                                                  |

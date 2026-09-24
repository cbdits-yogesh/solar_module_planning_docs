# STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.md

# Enterprise Lifecycle Step Specification: Supplier Quotation & Comparative Evaluation Matrix

**Document ID:** `STEP-14-QUOTATION-COMPARISON-MATRIX`  
**Lifecycle Flow:** Flow 2: SCM, Store, Purchase & Vendor Procurement Lifecycle (Step 03 of 08 / Global Step 14)  
**Governing Architecture:** [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md)  
**Architecture Decision Record:** [`docs/decisions/ADR-014-SUPPLIER-QUOTATION-COMPARATIVE-EVALUATION-MATRIX.md`](../docs/decisions/ADR-014-SUPPLIER-QUOTATION-COMPARATIVE-EVALUATION-MATRIX.md)  
**PRD / FRS Traceability:** [`planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md`](../planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md) (`BC-13`), [`planning_ref_docs/04_GAP_ANALYSIS_FIT_GAP.md`](../planning_ref_docs/04_GAP_ANALYSIS_FIT_GAP.md) (`Gap #06`), [`planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md`](../planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md) (`BR-013`), [`planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md`](../planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md) (`FR-013`), [`planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md`](../planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md) (`Domain 7: SCM`), [`planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md`](../planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md) (`API 11`), [`planning_ref_docs/10_UI_UX_SPECIFICATION.md`](../planning_ref_docs/10_UI_UX_SPECIFICATION.md) (`Screen 17`), [`planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md`](../planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md) (`MOD-13`), [`planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md`](../planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md) (Sec 3.2, 4.1)  
**Target Module:** `solar_module` / `manoj` (Extends ERPNext `tabSupplier Quotation`, introduces standalone submittable `tabQuotation Comparison Matrix`, child tables `tabQuotation Comparison Item`, `tabQuotation Comparison Supplier Summary`, and reuses `tabRemark-Delay Log`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Implementation

---

## 1. Step Scope, Objectives & Context Traceability

### 1.1 Lifecycle Positioning & Context

Step 14 (**Supplier Quotation & Comparative Evaluation Matrix**) serves as the core commercial evaluation, landed cost normalization, and procurement award gateway within the **Solar EPC Procurement & Vendor Governance Lifecycle (Flow 2)**. It ingests supplier quotations resulting from Step 13 ([`STEP_13_SUPPLIER_RFQ_SPECIFICATION.md`](./STEP_13_SUPPLIER_RFQ_SPECIFICATION.md)), normalizes divergent commercial and logistics terms into an objective side-by-side matrix, executes a multi-factor scoring algorithm, enforces managerial anti-favoritism governance gates, and programmatically spawns the formal commercial contract in Step 15 ([`STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md`](./STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md)).

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                FLOW 2: SCM PROCUREMENT PIPELINE                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Step 12: Store Material Request] ──▶ Requisitions from Site Indents / Low-Stock Buffer        │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 13: Supplier RFQ Dispatch]  ──▶ Multi-vendor solicitation (≥ 3 Suppliers or Justified)   │
│                 │                                                                                │
│                 ▼                                                                                │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │               STEP 14: SUPPLIER QUOTATION & COMPARATIVE EVALUATION MATRIX                │   │
│   ├──────────────────────────────────────────────────────────────────────────────────────────┤   │
│   │ 1. Quotation Ingestion: Ingest via Tokenized Portal (/solar/rfq-portal/:token) or Desk   │   │
│   │ 2. Unsealing Verification Gate: Verify unsealing ceremony executed for sealed bids (>₹10L)│  │
│   │ 3. Landed Cost Normalization: Basic + P&F + Freight + Insurance + Tax - Net ITC          │   │
│   │ 4. 100-Point Scoring Engine: Cost (50%) + Lead Time (25%) + Rating (15%) + Terms (10%)  │   │
│   │ 5. Side-by-Side Evaluation Matrix: L1/L2/L3 Auto-Rank & Spec Deviation Highlighting      │   │
│   │ 6. Non-L1 Selection Gate: Mandatory justification (≥40 chars) & Purchase Manager sign-off│   │
│   │ 7. 48-Hour Turnaround SLA: Automated evaluation clock & Overdue delay audit tracking     │   │
│   └──────────────────────────────────────────────────────────────────────────────────────────┘   │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 15: Purchase Order Placement] ──▶ Programmatic PO creation, locking rates & terms        │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Predecessors:** Step 13 Supplier Request for Quotation (Dispatched RFQs and received vendor quotations).
- **Successors:** Step 15 Purchase Order Authorization & Placement (`tabPurchase Order`).

### 1.2 Core Business Objectives & Target KPIs

1. **100% Landed Cost Transparency:** Eliminate false L1 selections by mathematically normalizing raw Ex-Factory, Ex-Works, and FOR-Site quotes with accurate freight, transit insurance, packing & forwarding, and GST Input Tax Credit (ITC) treatment, preventing 4–7% gross procurement leakage.
2. **Sub-48-Hour Commercial Award Turnaround:** Enforce an automated 48-hour evaluation turnaround SLA from quotation deadline closure/unsealing, reducing procurement award cycle times by 65%.
3. **Eradication of Maverick Sourcing & Buyer Bias:** Hard-block procurement awards where non-L1 suppliers are chosen unless accompanied by an auditable, system-enforced managerial justification and formal approval from the `Purchase Manager` or `Admin`.
4. **Project Schedule & COD Protection:** Multi-factor scoring factors in supplier lead times, ensuring critical solar equipment (modules, inverters, HT cables) is awarded to vendors who can meet project milestone delivery schedules, eliminating DISCOM liquidated damages.
5. **Zero Data Re-Entry Latency:** One-click programmatic instantiation of ERPNext `Purchase Order` records directly from the awarded comparison line items, completely eliminating manual clerk re-typing errors.

### 1.3 Context Traceability Matrix

| Reference Document                 | Section / ID                                     | Requirement Traceability in Step 14                                                                             |
| :--------------------------------- | :----------------------------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| **Project Foundation Model**       | `BC-13` (RFQ & Quotation Matrix)                 | Multi-quote comparative evaluation analyzing landed rates, delivery lead times, and vendor scorecard ratings.   |
| **Business Requirements Document** | `BR-013` (Supplier Quotation SCM)                | Centralized comparative sheet, ranking bidders across total cost, lead times, and supplier performance tiers.   |
| **Functional Requirements Spec**   | `FR-013` (Quotation Comparison Sheet)            | Side-by-side matrix evaluating $\ge 2-3$ quotes, non-L1 justification gate, and PO placement pre-authorization. |
| **Gap Analysis & Fit-Gap**         | `Gap #06` (Quotation Comparison Sheet)           | Replaces manual and subjective spreadsheet purchasing with an auditable, submittable ERP comparative matrix.    |
| **Database Design Document**       | `Domain 7: SCM` (`tabSupplier Quotation`)        | Data model for supplier line rates, logistics surcharges, warranty conditions, and comparison audit containers. |
| **API Design & Integrations**      | `API 11` (`solar_module.api.procurement`)        | `compare_quotations`, `evaluate_and_score_quotations`, and `award_purchase_order` whitelisted endpoints.        |
| **UI/UX Specification**            | `Screen 17` (Quotation Comparison Matrix)        | Side-by-side multi-vendor comparison layout, dynamic best-rate badges, and non-L1 exception dialog.             |
| **Module SOP Suite**               | `MOD-13` (Supplier Quotation Comparative Matrix) | Standard operating procedure for quote evaluation, technical deviation review, and commercial award sign-off.   |

### 1.4 Failure Modes Eliminated

- **The "False L1" Ex-Factory Trap:** A buyer selects Vendor A whose basic price is ₹0.20/Wp cheaper, ignoring that Vendor A charges ₹0.65/Wp for freight while Vendor B's slightly higher quote was FOR Site (freight inclusive).
- **Subjective Buyer Favoritism:** Purchasing personnel silently award orders to preferred vendors without documenting why higher-priced or longer-lead-time bids were accepted over lower market quotes.
- **Project Commissioning Stalls:** Purchasing modules with a 6-week lead time to save 0.5% in purchase cost, causing civil and electrical installation teams on site to idle for 20 days and incurring heavy DISCOM LD penalties.
- **Unverified Sealed Bid Tampering:** Prematurely viewing competitive prices before tender deadline expiry, leading to leaked competitor rates and corrupted bidding.
- **Missing Audit Trails for Financial Compliance:** Using non-submittable, ephemeral desk reports that allow post-award modifications, failing ISO 9001 and internal corporate financial audits.

---

## 2. Stakeholders, Enterprise Actors & HRMS Role Mapping

### 2.1 Enterprise User Roles Matrix

In strict compliance with the **Zero "User" Suffix Rule** ([`step_plans/README.md#5-enterprise-persona--role-naming-standard-zero-user-suffix-rule`](./README.md#5-enterprise-persona--role-naming-standard-zero-user-suffix-rule)), all operational personas are designated by descriptive functional titles:

| Persona / Business Actor           | Frappe System Role   | HRMS Department        | HRMS Designation              | Operational Responsibilities                                                                                                         |
| :--------------------------------- | :------------------- | :--------------------- | :---------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| **Procurement Line Executive**     | `Purchase Assistant` | Purchase & SCM         | `Purchase Executive`          | Verifies received quotes, inputs logistics surcharges, runs landed cost normalization, initiates scoring, drafts comparison matrix.  |
| **Head of Procurement**            | `Purchase Manager`   | Purchase & SCM         | `Purchase Manager`            | Reviews comparative matrix, authorizes Non-L1 justification exceptions, signs off on commercial award decision, releases PO.         |
| **Site Technical Requisitioner**   | `Project Engineer`   | Engineering Operations | `Site Supervisor`             | Reviews technical deviations in supplier quotes (datasheets, cable ratings, inverter warranties) against design specs.               |
| **Warehouse Storekeeper**          | `Store Assistant`    | Store & Inventory      | `Store Assistant`             | Checks proposed delivery lead times against central store safety stock depletion projections.                                        |
| **Inventory & Logistics Head**     | `Store Manager`      | Store & Inventory      | `Warehouse Manager`           | Verifies proposed delivery location feasibility (Central Store vs Direct-to-Site delivery terms).                                    |
| **External Vendor Representative** | `Supplier`           | External Entity        | `Vendor Sales Representative` | Submits quote rates, freight, lead time, and warranty terms via passwordless portal link (`/solar/rfq-portal/:token`).               |
| **Solar EPC Director / Admin**     | `Admin`              | Executive Management   | `Managing Director`           | Project supreme operational command; manages `Solar SLA Settings`, `Solar Notification Settings`, delay approvals, and award audits. |
| **Framework Supreme / Developer**  | `System Manager`     | Information Technology | `DevOps Engineer / Architect` | Bench CLI administration, custom DocType schema migrations, Redis worker sizing, and developer mode debugging. Supreme over `Admin`. |

### 2.2 Permission Hierarchy Matrix

| DocType / Action                         | Purchase Assistant |  Purchase Manager  | Project Engineer |  Store Manager  |      Admin\*      | External Supplier |
| :--------------------------------------- | :----------------: | :----------------: | :--------------: | :-------------: | :---------------: | :---------------: |
| **Supplier Quotation (Read)**            |     All Active     |     All Active     | Assigned Project | Requisition Ref |    All Records    |  Own Quote Only   |
| **Supplier Quotation (Create/Edit)**     |    Yes (Draft)     |        Yes         |        No        |       No        |    All Records    | Portal Form Only  |
| **Supplier Quotation (Submit)**          |        Yes         |        Yes         |        No        |       No        |        Yes        |        No         |
| **Quotation Comparison Matrix (Read)**   |     All Active     |     All Active     |  Project Linked  | Requisition Ref |    All Records    |     No Access     |
| **Quotation Comparison Matrix (Create)** |        Yes         |        Yes         |        No        |       No        |        Yes        |        No         |
| **Quotation Comparison Matrix (Submit)** |         No         | **Yes (Sign-off)** |        No        |       No        | **Yes (Supreme)** |        No         |
| **Non-L1 Selection Override Gate**       |         No         |   **Authorized**   |        No        |       No        |   **Permitted**   |        No         |
| **Award Purchase Order (Trigger)**       |         No         |      **Yes**       |        No        |       No        |      **Yes**      |        No         |
| **Remark-Delay Log (Write)**             |        Own         |        Own         |       Own        |       Own       |    Full Access    |     No Access     |
| **Solar SLA Settings (Write)**           |         No         |         No         |        No        |       No        |  **Yes (Only)**   |     No Access     |

_\*Note: Frappe `Administrator` and `System Manager` sit at the apex of system hierarchy and inherit all operational permissions plus technical code/schema access._

---

## 3. Relational Schema & 3NF Data Dictionary

### 3.1 Core DocType Extensions: `tabSupplier Quotation`

Standard ERPNext `Supplier Quotation` is extended with enterprise solar logistics and verification attributes isolated under the `custom_*` prefix:

| Fieldname                     | Label                     | Fieldtype    | Options / Target                             | Mandatory |    Index     | Description & Validation Rules                             |
| :---------------------------- | :------------------------ | :----------- | :------------------------------------------- | :-------: | :----------: | :--------------------------------------------------------- |
| `custom_rfq_reference`        | Originating RFQ           | `Link`       | `Request for Quotation`                      |    No     | **Index: 1** | Links upstream RFQ dispatch document.                      |
| `custom_project_reference`    | Project Reference         | `Link`       | `Project`                                    |    No     | **Index: 1** | Foreign key linking solar EPC project container.           |
| `custom_material_request_ref` | Material Request Ref      | `Link`       | `Material Request`                           |    No     | **Index: 1** | Links original requisition indent.                         |
| `custom_is_sealed`            | Is Sealed Bid?            | `Check`      | -                                            |    No     |      -       | Inherited from RFQ; if 1, rates masked until unsealing.    |
| `custom_portal_token`         | Portal Submission Token   | `Data`       | -                                            |    No     | **Index: 1** | 256-bit UUID token used for passwordless portal entry.     |
| `custom_packaging_forwarding` | Packaging & Forwarding    | `Currency`   | `Company:currency`                           |    No     |      -       | Total packaging, crating, and palletizing charges.         |
| `custom_freight_charges`      | Freight Charges           | `Currency`   | `Company:currency`                           |    No     |      -       | Total logistics/transport freight to destination.          |
| `custom_transit_insurance`    | Transit Insurance         | `Currency`   | `Company:currency`                           |    No     |      -       | Marine/road transit insurance coverage charge.             |
| `custom_unloading_charges`    | Site Unloading Charges    | `Currency`   | `Company:currency`                           |    No     |      -       | Heavy equipment crane/labor unloading charges at site.     |
| `custom_landed_cost_unit`     | Landed Cost per Unit      | `Currency`   | `Company:currency`                           |  **Yes**  |      -       | Algorithmic landed rate per unit including all surcharges. |
| `custom_net_effective_total`  | Net Effective Total       | `Currency`   | `Company:currency`                           |  **Yes**  |      -       | Net payable after netting out eligible GST ITC.            |
| `custom_promised_lead_days`   | Promised Lead Time (Days) | `Int`        | -                                            |  **Yes**  |      -       | Guaranteed dispatch/delivery days from PO date.            |
| `custom_warranty_months`      | Equipment Warranty (M)    | `Int`        | -                                            |  **Yes**  |      -       | Manufacturer warranty period in months (e.g. 120 or 300).  |
| `custom_datasheet_attached`   | Technical Datasheet       | `Attach`     | -                                            |    No     |      -       | Manufacturer specification datasheet PDF.                  |
| `custom_technical_compliant`  | Technical Compliance      | `Select`     | `Compliant\nDeviations Noted\nNon-Compliant` |  **Yes**  |      -       | Technical review status by Project Engineer.               |
| `custom_payment_terms_desc`   | Commercial Payment Terms  | `Small Text` | -                                            |    No     |      -       | e.g. "20% Advance, 80% Against Dispatch Inspection".       |

### 3.2 Standalone Governance DocType: `tabQuotation Comparison Matrix`

A dedicated, submittable enterprise DocType (`is_submittable = 1`) capturing the immutable comparative snapshot:

- **DocType Name:** `Quotation Comparison Matrix`
- **Module:** `solar_module`
- **Naming Pattern:** `naming_series: QCM-.YYYY.-.#####` (e.g. `QCM-2026-00042`)
- **Submittable Semantics:** `is_submittable = 1` (Freezes award decision, scores, rankings, and notes permanently upon submission).

| Fieldname               | Label                    | Fieldtype    | Options / Target                                                     | Mandatory |    Index     | Description & Validation Rules                             |
| :---------------------- | :----------------------- | :----------- | :------------------------------------------------------------------- | :-------: | :----------: | :--------------------------------------------------------- |
| `naming_series`         | Series                   | `Select`     | `QCM-.YYYY.-.#####`                                                  |  **Yes**  |      -       | Primary autonaming rule.                                   |
| `rfq_reference`         | RFQ Reference            | `Link`       | `Request for Quotation`                                              |  **Yes**  | **Index: 1** | Target RFQ being evaluated.                                |
| `project_reference`     | Project Reference        | `Link`       | `Project`                                                            |    No     | **Index: 1** | Solar EPC project container.                               |
| `material_request_ref`  | Material Request Ref     | `Link`       | `Material Request`                                                   |    No     |      -       | Upstream requisition indent.                               |
| `evaluation_date`       | Evaluation Date          | `Date`       | -                                                                    |  **Yes**  |      -       | Date comparison matrix generated. Defaults to today.       |
| `evaluation_status`     | Status                   | `Select`     | `Draft\nUnder Review\nAward Approved\nRejected\nPO Created\nOverdue` |  **Yes**  | **Index: 1** | State machine attribute. Defaults to `Draft`.              |
| `target_delivery_date`  | Project Target Delivery  | `Date`       | -                                                                    |    No     |      -       | Site milestone required-by delivery date.                  |
| `sealed_bids_verified`  | Sealed Bids Verified     | `Check`      | -                                                                    |    No     |      -       | System flag confirming tender unsealing sign-off.          |
| `awarded_supplier`      | Awarded Supplier         | `Link`       | `Supplier`                                                           |    No     | **Index: 1** | Vendor selected for commercial purchase award.             |
| `awarded_quotation`     | Awarded Quotation        | `Link`       | `Supplier Quotation`                                                 |    No     |      -       | Winning quotation document reference.                      |
| `awarded_landed_amount` | Awarded Landed Amount    | `Currency`   | `Company:currency`                                                   |    No     |      -       | Total net landed commercial commitment.                    |
| `is_l1_selected`        | Is L1 Vendor Selected?   | `Check`      | -                                                                    |    No     |      -       | Evaluated as 1 if awarded supplier has lowest landed cost. |
| `non_l1_justification`  | Non-L1 Justification     | `Small Text` | -                                                                    |    No     |      -       | **Mandatory** (min 40 chars) if `is_l1_selected == 0`.     |
| `authorized_by`         | Award Authorized By      | `Link`       | `User`                                                               |    No     |      -       | Approver ID (Role: `Purchase Manager` or `Admin`).         |
| `authorization_date`    | Authorized On            | `Datetime`   | -                                                                    |    No     |      -       | Digital sign-off timestamp.                                |
| `purchase_order_ref`    | Generated Purchase Order | `Link`       | `Purchase Order`                                                     |    No     | **Index: 1** | Downstream PO instantiated upon award.                     |
| `sla_deadline`          | Evaluation SLA Deadline  | `Datetime`   | -                                                                    |  **Yes**  | **Index: 1** | Target completion datetime (`evaluation_date + 48h`).      |
| `sla_status`            | SLA Status               | `Select`     | `\nOn Time\nOverdue`                                                 |    No     |      -       | Managed by background SLA daemon.                          |
| `comparison_items`      | Comparison Line Items    | `Table`      | `Quotation Comparison Item`                                          |  **Yes**  |      -       | Side-by-side line-item comparison child table.             |
| `supplier_summaries`    | Supplier Summary Matrix  | `Table`      | `Quotation Comparison Supplier Summary`                              |  **Yes**  |      -       | High-level supplier ranking and scoring table.             |
| `delay_reason_table`    | Delay Audit Log          | `Table`      | `Remark-Delay Log`                                                   |    No     |      -       | Required if submitting while `sla_status == 'Overdue'`.    |

### 3.3 Child DocType: `tabQuotation Comparison Item`

Captures item-level rates, logistics additions, and technical compliance per bidder:

| Fieldname              | Label                   | Fieldtype  | Options / Target                             | Mandatory | Description & Calculation Rules                                                                   |
| :--------------------- | :---------------------- | :--------- | :------------------------------------------- | :-------: | :------------------------------------------------------------------------------------------------ |
| `item_code`            | Item Code               | `Link`     | `Item`                                       |  **Yes**  | Component identifier (e.g. `PV-MOD-545W`).                                                        |
| `item_name`            | Item Name               | `Data`     | -                                            |    No     | Component description.                                                                            |
| `qty`                  | Required Quantity       | `Float`    | -                                            |  **Yes**  | Requisitioned quantity.                                                                           |
| `uom`                  | UOM                     | `Link`     | `UOM`                                        |  **Yes**  | Unit of Measure (Nos, Mtr, Set).                                                                  |
| `supplier`             | Supplier                | `Link`     | `Supplier`                                   |  **Yes**  | Bidding vendor.                                                                                   |
| `supplier_quotation`   | Supplier Quotation      | `Link`     | `Supplier Quotation`                         |  **Yes**  | Source quote document.                                                                            |
| `basic_rate`           | Basic Unit Rate         | `Currency` | `Company:currency`                           |  **Yes**  | Quoted base rate per unit before logistics & tax.                                                 |
| `packaging_forwarding` | Packaging & Forwarding  | `Currency` | `Company:currency`                           |    No     | Allocated P&F charges per unit.                                                                   |
| `freight_rate_unit`    | Freight per Unit        | `Currency` | `Company:currency`                           |    No     | Allocated freight per unit to target location.                                                    |
| `insurance_rate_unit`  | Insurance per Unit      | `Currency` | `Company:currency`                           |    No     | Transit insurance per unit.                                                                       |
| `unloading_rate_unit`  | Unloading per Unit      | `Currency` | `Company:currency`                           |    No     | Site labor/crane unloading charge per unit.                                                       |
| `tax_rate_unit`        | Non-Creditable Tax/Unit | `Currency` | `Company:currency`                           |    No     | Any non-refundable statutory tax or duty.                                                         |
| `landed_rate_unit`     | Landed Rate per Unit    | `Currency` | `Company:currency`                           |  **Yes**  | $\text{Basic} + \text{P\&F} + \text{Freight} + \text{Insurance} + \text{Unloading} + \text{Tax}$. |
| `total_landed_amount`  | Total Landed Amount     | `Currency` | `Company:currency`                           |  **Yes**  | $\text{Landed Rate per Unit} \times \text{Quantity}$.                                             |
| `promised_lead_days`   | Promised Lead Time      | `Int`      | -                                            |  **Yes**  | Days to deliver to target destination.                                                            |
| `technical_compliant`  | Spec Compliance         | `Select`   | `Compliant\nDeviations Noted\nNon-Compliant` |  **Yes**  | Technical engineering clearance.                                                                  |
| `item_rank`            | Line Rank               | `Select`   | `L1\nL2\nL3\nL4\nL5`                         |  **Yes**  | Item-level cost ranking.                                                                          |

### 3.4 Child DocType: `tabQuotation Comparison Supplier Summary`

Consolidates supplier-level metrics, multi-factor scoring, and award recommendations:

| Fieldname                 | Label                  | Fieldtype    | Options / Target     | Mandatory | Description & Scoring Math                                                              |
| :------------------------ | :--------------------- | :----------- | :------------------- | :-------: | :-------------------------------------------------------------------------------------- |
| `supplier`                | Supplier               | `Link`       | `Supplier`           |  **Yes**  | Vendor identifier.                                                                      |
| `supplier_quotation`      | Supplier Quotation     | `Link`       | `Supplier Quotation` |  **Yes**  | Bidding document reference.                                                             |
| `total_basic_amount`      | Total Basic Amount     | `Currency`   | `Company:currency`   |  **Yes**  | Sum of raw basic item amounts.                                                          |
| `total_freight_logistics` | Total Logistics & P&F  | `Currency`   | `Company:currency`   |  **Yes**  | Total freight, insurance, and unloading charges.                                        |
| `total_tax_amount`        | Total Tax Amount       | `Currency`   | `Company:currency`   |  **Yes**  | Total statutory taxes (GST).                                                            |
| `total_landed_amount`     | Total Landed Cost      | `Currency`   | `Company:currency`   |  **Yes**  | Sum of total landed line amounts.                                                       |
| `max_lead_time_days`      | Max Lead Time (Days)   | `Int`        | -                    |  **Yes**  | Longest delivery lead time across quoted lines.                                         |
| `vendor_rating_score`     | Vendor Rating Score    | `Percent`    | -                    |    No     | Score pulled directly from Step 19 Scorecard ($0-100\%$).                               |
| `commercial_score`        | Commercial Score (50%) | `Float`      | -                    |  **Yes**  | Cost score: $(\text{Landed Cost}_{L1} / \text{Landed Cost}_{\text{vendor}}) \times 50$. |
| `lead_time_score`         | Lead Time Score (25%)  | `Float`      | -                    |  **Yes**  | Time score: Delivery feasibility relative to target.                                    |
| `rating_score`            | Rating Score (15%)     | `Float`      | -                    |  **Yes**  | Quality score: $\text{Vendor Rating Score} \times 0.15$.                                |
| `terms_score`             | Terms Score (10%)      | `Float`      | -                    |  **Yes**  | Credit terms and warranty duration score.                                               |
| `composite_score`         | Composite Score (100)  | `Float`      | -                    |  **Yes**  | $\text{Commercial} + \text{Lead Time} + \text{Rating} + \text{Terms}$.                  |
| `overall_rank`            | Overall Rank           | `Select`     | `L1\nL2\nL3\nL4\nL5` |  **Yes**  | Landed cost rank.                                                                       |
| `composite_rank`          | Composite Rank         | `Int`        | -                    |  **Yes**  | Overall multi-factor rank ($1 = \text{Highest Score}$).                                 |
| `is_recommended`          | System Recommended     | `Check`      | -                    |    No     | 1 if vendor holds highest composite evaluation score.                                   |
| `evaluator_notes`         | Evaluator Remarks      | `Small Text` | -                    |    No     | Commercial justification notes.                                                         |

---

## 4. State Machine, Verification Gates & SLA Engine

### 4.1 State Machine Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: Generate Comparison Matrix
    Draft --> Quotes_Aggregated: Quotes Ingested & Normalized
    Quotes_Aggregated --> Scoring_Evaluated: 100-Point Scoring Computed

    state Scoring_Evaluated {
        [*] --> In_Review
        In_Review --> SLA_Overdue: Elapsed Time > 48h
        SLA_Overdue --> In_Review: Delay Reason Appended
    }

    Scoring_Evaluated --> Pending_Approval: Submit for Award Sign-off

    state Pending_Approval {
        [*] --> Check_L1
        Check_L1 --> L1_Standard_Signoff: Awarded Supplier == L1
        Check_L1 --> Non_L1_Gate: Awarded Supplier != L1
        Non_L1_Gate --> L1_Rejected: Justification < 40 chars
        Non_L1_Gate --> Non_L1_Authorized: Valid Justification + Manager Sign-off
    }

    Pending_Approval --> Award_Approved: docstatus = 1 (Submission Frozen)
    Pending_Approval --> Rejected: Award Disapproved / Retender

    Award_Approved --> PO_Created: Programmatic PO Instantiation (Step 15)
    PO_Created --> [*]
    Rejected --> [*]
```

### 4.2 Enforced Verification Gates

The controller and domain services enforce five hard verification gates:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             STEP 14 ENFORCED VERIFICATION GATES                                  │
├───────┬───────────────────────────────┬──────────────────────────────────────────┬───────────────┤
│ Gate  │ Verification Check            │ Controller Validation Invariant          │ Failure Action│
├───────┼───────────────────────────────┼──────────────────────────────────────────┼───────────────┤
│ **1** │ Minimum Quotes Quota          │ `count(quotes) >= 2` (or Single Source)  │ Throw Error   │
│ **2** │ Sealed Bid Unmasking Check    │ If sealed: `custom_bids_unsealed == 1`   │ Block Action  │
│ **3** │ Quote Validity Gate           │ For all quotes: `today <= valid_till`    │ Alert / Throw │
│ **4** │ Non-L1 Selection Gate         │ If non-L1: Justification ≥ 40 chars + PM │ Block Submit  │
│ **5** │ Downstream PO Duplicate Gate  │ `len(purchase_order_ref) == 0`           │ Prevent Re-PO │
└───────┴───────────────────────────────┴──────────────────────────────────────────┴───────────────┘
```

1. **Gate 1: Minimum Quotes Quota:**
   - Evaluates that at least two (recommended $\ge 3$) independent valid supplier quotations are included in the comparison.
   - Exception: Bypassed only if upstream RFQ was formally authorized as Single-Source (`custom_is_single_source = 1`).
2. **Gate 2: Sealed Bid Unmasking Check:**
   - If upstream RFQ enforced sealed bids (`custom_sealed_bids = 1`), asserts that the bid closure deadline has passed and the formal unsealing ceremony was signed off (`custom_bids_unsealed = 1`). Prevents unmasking data during active tender phases.
3. **Gate 3: Quotation Validity Gate:**
   - Asserts that all included quotations remain within their valid quotation window (`today <= doc.valid_till`). Expired quotes must either be refreshed via supplier confirmation or formally flagged in the matrix.
4. **Gate 4: Non-L1 Selection Governance Gate:**
   - If the `awarded_supplier` does not match the supplier identified as `L1` (lowest landed cost):
     - Controller asserts `is_l1_selected == 0`.
     - Controller strictly asserts `len(doc.non_l1_justification.strip()) >= 40`.
     - Controller asserts current user possesses role `Purchase Manager` or `Admin`. Attempting to submit by `Purchase Assistant` throws an immediate `PermissionError`.
5. **Gate 5: Downstream PO Duplicate Prevention Gate:**
   - Asserts that no active `Purchase Order` already references this comparison matrix or RFQ line items, preventing duplicate procurement commitments.

### 4.3 Turnaround Time (TAT) SLA Engine & Delay Governance

```
                                  48-HOUR EVALUATION SLA WINDOW
                      ┌────────────────────────────────────────────────────┐
                      │                                                    │
Quotation Ingestion ──▶ [Active Countdown: T-48h] ─────────────────────────▶ [Matrix Submission]
   / Tender Unseal    │                                                    │    (docstatus = 1)
                      │  T-12h: Warning alert to Purchase Assistant        │
                      │  T-0h:  Transition to Overdue                      │
                      │         Alert to Purchase Manager                  │
                      │         Mandatory Entry in tabRemark-Delay Log     │
                      └────────────────────────────────────────────────────┘
```

- **SLA Duration:** 48 Hours from quotation deadline expiry or tender unsealing timestamp.
- **Background SLA Runner:** `solar_module.tasks.monitor_quotation_evaluation_sla` runs every 15 minutes in Redis worker queue (`short`).
- **Overdue Transition:** If current time exceeds `sla_deadline` and `evaluation_status != 'Award Approved'`, status transitions to `Overdue`.
- **Delay Logging Invariant:** When `sla_status == 'Overdue'`, the system blocks document submission until at least one structured delay entry is recorded in `delay_reason_table` (`tabRemark-Delay Log`), specifying delay category, root cause, and mitigation action.

---

## 5. Controller Logic, Domain Services & Whitelisted APIs

### 5.1 Domain Architecture: SOLID Decoupled Services

In accordance with [`architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md`](../architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md), all mathematical calculations, normalization algorithms, scoring rules, and PO creation routines are isolated in dedicated domain services:

```
solar_module/
└── services/
    └── procurement/
        ├── __init__.py
        ├── landed_cost_service.py       # True landed cost normalization
        ├── weighted_scoring_service.py   # 100-Point multi-factor evaluation engine
        ├── comparison_matrix_service.py  # Matrix aggregation, ranking & validation
        └── po_award_service.py           # Downstream PO instantiation & quote closure
```

### 5.2 Mathematical Formulation & Service Implementation

#### 1. Landed Cost Normalization (`LandedCostCalculationService`):

$$\text{Freight Unit} = \frac{\text{Total Freight Charges}}{\text{Quantity}}$$
$$\text{Insurance Unit} = \frac{\text{Total Transit Insurance}}{\text{Quantity}}$$
$$\text{P\&F Unit} = \frac{\text{Total Packaging \& Forwarding}}{\text{Quantity}}$$
$$\text{Unloading Unit} = \frac{\text{Total Site Unloading}}{\text{Quantity}}$$
$$\text{Landed Rate} = \text{Basic Rate} + \text{P\&F Unit} + \text{Freight Unit} + \text{Insurance Unit} + \text{Unloading Unit} + \text{Non-Creditable Tax}$$

```python
# File: solar_module/services/procurement/landed_cost_service.py
from decimal import Decimal, ROUND_HALF_UP

class LandedCostCalculationService:
    @staticmethod
    def calculate_item_landed_cost(
        basic_rate: float,
        qty: float,
        freight: float = 0.0,
        insurance: float = 0.0,
        packaging: float = 0.0,
        unloading: float = 0.0,
        non_creditable_tax: float = 0.0
    ) -> dict:
        q = Decimal(str(max(qty, 1.0)))
        b_rate = Decimal(str(basic_rate))
        f_unit = (Decimal(str(freight)) / q).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        i_unit = (Decimal(str(insurance)) / q).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        p_unit = (Decimal(str(packaging)) / q).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        u_unit = (Decimal(str(unloading)) / q).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        t_unit = (Decimal(str(non_creditable_tax)) / q).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        landed_unit = b_rate + f_unit + i_unit + p_unit + u_unit + t_unit
        total_landed = (landed_unit * q).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "basic_rate": float(b_rate),
            "freight_unit": float(f_unit),
            "insurance_unit": float(i_unit),
            "packaging_unit": float(p_unit),
            "unloading_unit": float(u_unit),
            "tax_unit": float(t_unit),
            "landed_rate_unit": float(landed_unit),
            "total_landed_amount": float(total_landed)
        }
```

#### 2. 100-Point Multi-Factor Scoring Engine (`WeightedScoringEngineService`):

```python
# File: solar_module/services/procurement/weighted_scoring_service.py
from decimal import Decimal

class WeightedScoringEngineService:
    WEIGHT_COMMERCIAL = 50.0
    WEIGHT_LEAD_TIME = 25.0
    WEIGHT_VENDOR_RATING = 15.0
    WEIGHT_TERMS = 10.0

    @classmethod
    def compute_composite_score(
        cls,
        vendor_landed_cost: float,
        l1_landed_cost: float,
        vendor_lead_days: int,
        min_lead_days: int,
        target_max_lead_days: int,
        vendor_rating_score: float, # 0 to 100
        payment_terms_rating: float # 0 to 10
    ) -> dict:
        # 1. Commercial Cost Score (50%)
        if vendor_landed_cost > 0:
            comm_score = (l1_landed_cost / vendor_landed_cost) * cls.WEIGHT_COMMERCIAL
        else:
            comm_score = 0.0
        comm_score = min(cls.WEIGHT_COMMERCIAL, max(0.0, comm_score))

        # 2. Delivery Lead Time Score (25%)
        # Penalty formula: scales down as lead time exceeds fastest bidder
        target_span = max(1, target_max_lead_days - min_lead_days)
        excess_days = max(0, vendor_lead_days - min_lead_days)
        time_ratio = 1.0 - (excess_days / target_span)
        lead_score = max(0.0, time_ratio * cls.WEIGHT_LEAD_TIME)

        # 3. Vendor Rating Score (15%) - from Step 19
        v_rating = max(0.0, min(100.0, vendor_rating_score or 70.0)) # Default 70% if new
        rating_score = (v_rating / 100.0) * cls.WEIGHT_VENDOR_RATING

        # 4. Terms & Warranty Score (10%)
        terms_score = max(0.0, min(cls.WEIGHT_TERMS, payment_terms_rating))

        composite = round(comm_score + lead_score + rating_score + terms_score, 2)

        return {
            "commercial_score": round(comm_score, 2),
            "lead_time_score": round(lead_score, 2),
            "rating_score": round(rating_score, 2),
            "terms_score": round(terms_score, 2),
            "composite_score": composite
        }
```

### 5.3 Controller Implementation: `QuotationComparisonMatrix`

```python
# File: solar_module/solar_module/doctype/quotation_comparison_matrix/quotation_comparison_matrix.py
import frappe
from frappe import _
from frappe.model.document import Document
from solar_module.services.procurement.comparison_matrix_service import QuotationComparisonMatrixService
from solar_module.services.procurement.po_award_service import POAwardInstantiationService

class QuotationComparisonMatrix(Document):
    def validate(self):
        QuotationComparisonMatrixService.validate_matrix_invariants(self)

    def on_submit(self):
        # 1. Enforce Non-L1 selection authorization gate
        QuotationComparisonMatrixService.validate_award_gates(self)
        # 2. Freeze snapshot & close SLA clock
        self.evaluation_status = "Award Approved"
        self.db_set("evaluation_status", "Award Approved")

    def on_cancel(self):
        if self.purchase_order_ref:
            po_doc = frappe.get_doc("Purchase Order", self.purchase_order_ref)
            if po_doc.docstatus == 1:
                frappe.throw(
                    _("Cannot cancel comparison matrix linked to submitted Purchase Order {0}. Cancel PO first.")
                    .format(self.purchase_order_ref)
                )
        self.evaluation_status = "Rejected"
        self.db_set("evaluation_status", "Rejected")
```

### 5.4 Whitelisted REST API Endpoints

All endpoints are strictly annotated with `@frappe.whitelist(methods=["POST"])` and execute explicit in-method IDOR permission validation:

```python
# File: solar_module/api/procurement.py
import json
import frappe
from frappe import _
from solar_module.services.procurement.comparison_matrix_service import QuotationComparisonMatrixService
from solar_module.services.procurement.po_award_service import POAwardInstantiationService

@frappe.whitelist(methods=["POST"])
def generate_quotation_comparison(rfq_name: str) -> dict:
    """Compiles side-by-side comparison matrix from all quotes submitted for an RFQ."""
    if not rfq_name:
        frappe.throw(_("RFQ name is required"), frappe.ValidationError)

    rfq_doc = frappe.get_doc("Request for Quotation", rfq_name)
    rfq_doc.check_permission("read")

    # Check sealed bids unmasking gate
    if getattr(rfq_doc, "custom_sealed_bids", 0) and not getattr(rfq_doc, "custom_bids_unsealed", 0):
        frappe.throw(_("Cannot generate comparison: Bids for RFQ {0} are sealed and unsealing ceremony has not been executed.").format(rfq_name), frappe.PermissionError)

    matrix_name = QuotationComparisonMatrixService.create_from_rfq(rfq_doc)
    return {"status": "success", "comparison_matrix": matrix_name}

@frappe.whitelist(methods=["POST"])
def authorize_quotation_award(
    matrix_name: str,
    awarded_supplier: str,
    non_l1_justification: str = None
) -> dict:
    """Validates selection, checks Non-L1 gates, and records award approval."""
    doc = frappe.get_doc("Quotation Comparison Matrix", matrix_name)
    doc.check_permission("write")

    # Assert Role Authority
    user_roles = frappe.get_roles()
    if "Purchase Manager" not in user_roles and "Admin" not in user_roles and "System Manager" not in user_roles:
        frappe.throw(_("Only Purchase Manager or Admin can authorize quotation awards"), frappe.PermissionError)

    updated_doc = QuotationComparisonMatrixService.apply_award_decision(
        matrix_doc=doc,
        awarded_supplier=awarded_supplier,
        justification=non_l1_justification,
        authorizer=frappe.session.user
    )
    return {"status": "success", "matrix": updated_doc.name, "evaluation_status": updated_doc.evaluation_status}

@frappe.whitelist(methods=["POST"])
def spawn_purchase_order_from_award(matrix_name: str) -> dict:
    """Spawns standard ERPNext Purchase Order from approved comparison award."""
    doc = frappe.get_doc("Quotation Comparison Matrix", matrix_name)
    doc.check_permission("write")

    if doc.docstatus != 1:
        frappe.throw(_("Quotation Comparison Matrix must be submitted before spawning Purchase Order"), frappe.ValidationError)

    po_name = POAwardInstantiationService.instantiate_purchase_order(doc)
    return {"status": "success", "purchase_order": po_name}
```

---

## 6. Frontend UI/UX Specification (Desk & Vue 3 / Frappe UI)

### 6.1 Unified SPA Architecture (`/solar/procurement/comparison/:id`)

In accordance with [`planning_ref_docs/10_UI_UX_SPECIFICATION.md`](../planning_ref_docs/10_UI_UX_SPECIFICATION.md) (`Screen 17`), the comparison matrix operates primarily within the decoupled Vue 3 / Frappe UI SPA wrapper hosted at `/solar`:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  VUE 3 / FRAPPE UI SPA: /solar/procurement/comparison/QCM-2026-00042                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ◀ Back to RFQs   |  RFQ: RFQ-2026-00108 (545W Monocrystalline PV Modules)   | Status: IN REVIEW │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [KPI 1: 4 Active Bids]  [KPI 2: L1 Landed: ₹18.42/Wp]  [KPI 3: Fast Lead: 7 Days] [SLA: 26h Left]│
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SIDE-BY-SIDE SUPPLIER COMPARISON MATRIX                                                          │
│  ┌──────────────────────┬────────────────────────┬───────────────────────┬──────────────────────┐ │
│  │ Metric / Line Item   │ Adani Solar (L1)       │ Waaree Energies (L2)  │ Goldi Solar (L3)     │ │
│  ├──────────────────────┼────────────────────────┼───────────────────────┼──────────────────────┤ │
│  │ Basic Quoted Rate    │ ₹17.80 / Wp            │ ₹18.10 / Wp           │ ₹18.50 / Wp          │ │
│  │ Packaging & Forw.    │ ₹0.15 / Wp             │ Included              │ Included             │ │
│  │ Freight Charges      │ ₹0.65 / Wp (Ex-Works)  │ ₹0.40 / Wp            │ Included (FOR Site)  │ │
│  │ Transit Insurance    │ 0.15% (₹0.03/Wp)       │ Included              │ Included             │ │
│  │ Unloading at Site    │ Excluded (₹0.05/Wp)    │ Excluded (₹0.05/Wp)   │ Included             │ │
│  │ Total Landed Rate    │ ₹18.68 / Wp [L2 Landed]│ ₹18.55 / Wp [L1] 🏆   │ ₹18.50 / Wp [L1 Ex]  │ │
│  │ Promised Lead Time   │ 28 Days                │ 10 Days ⚡            │ 7 Days ⚡⚡          │ │
│  │ Step 19 Vendor Score │ 78% (Approved)         │ 94% (Tier 1 Strategic)│ 82% (Tier 1)         │ │
│  │ Warranty Period      │ 120 Months             │ 144 Months (12 Years) │ 120 Months           │ │
│  │ Composite Score      │ 81.4 / 100             │ 96.2 / 100 🥇         │ 91.8 / 100 🥈        │ │
│  │ Award Action         │ [ Select L2 ]          │ [ Award Winning 🥇 ]   │ [ Select L3 ]        │ │
│  └──────────────────────┴────────────────────────┴───────────────────────┴──────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  NON-L1 SELECTION MODAL (TRIGGERS IF ADANI SELECTED OVER WAAREE):                                 │
│  [!] Warning: You are selecting Adani Solar which has higher Landed Cost than L1.                 │
│  Reason Category: [ Delivery Lead Time Criticality / Site Requirement ▾ ]                        │
│  Mandatory Justification: "Site foundation complete. Requires dispatch within 48h to prevent..."  │
│  [ Sign & Authorize Award (Purchase Manager Only) ]                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Key Screen Interactions & Reactive Widgets

1. **Normalized vs Raw Cost Toggle:** Evaluators can switch between "Raw Quoted Basic Rates" and "Effective Landed Cost (All-Inclusive)", immediately exposing hidden freight and insurance charges.
2. **Best-in-Class Dynamic Badges:**
   - Green Pill: `🏆 L1 Landed Cost`
   - Purple Pill: `⚡ Fastest Lead Time`
   - Gold Star: `🥇 Recommended Award (Highest Composite Score)`
3. **Spec Deviation Highlighter:** Cells where a vendor's offer deviates from requested specifications (e.g. 540W offered instead of requested 545W, or 10-year warranty instead of 12-year) are highlighted with amber warning chips.
4. **Interactive Non-L1 Justification Drawer:** If the evaluator clicks to award a non-L1 bidder, the UI slides open a mandatory justification drawer asserting character counter ($\ge 40$ chars) and checking role elevation.

### 6.3 Controlled Frappe Desk Form View

For power users accessing via authorized deep links (`/app/quotation-comparison-matrix/:id`):

- Custom Client Script (`codes/client_script/quotation_comparison_matrix.js`) dynamically decorates the form:
  - Form status indicator reflects SLA health (`On Time` in green, `Overdue` in red).
  - Primary Action Button: "Authorize Commercial Award" triggers modal dialog.
  - Secondary Action Button: "Instantiate Purchase Order" spawns PO upon submission.

---

## 7. Cross-App Integration Touchpoints

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         CROSS-APP INTEGRATION ARCHITECTURE                                       │
├────────────────────────────────┬───────────────────────────────┬─────────────────────────────────┤
│ Target Application / Module    │ Entity / DocType              │ Data Flow & Protocol            │
├────────────────────────────────┼───────────────────────────────┼─────────────────────────────────┤
│ **ERPNext Buying Core**        │ `tabSupplier Quotation`       │ Input quotes, rates, freight    │
│ **ERPNext Buying Core**        │ `tabPurchase Order`           │ Spawned contract baseline       │
│ **ERPNext Stock Core**         │ `tabItem` / `tabMaterial Req` │ Specifications, BOM indents     │
│ **ERPNext SCM Governance**     │ `tabRequest for Quotation`    │ Upstream bidding tender link    │
│ **Solar Custom (`solar_module`)**│ `tabVendor Rating` (Step 19) │ Historical scorecard score sync │
│ **Solar SLA Daemon**           │ `solar_module.tasks` (Redis)  │ 48h SLA countdown & delay log   │
│ **Raven / WhatsApp Gateway**   │ Transactional Broker          │ Award & Regret notifications    │
└────────────────────────────────┴───────────────────────────────┴─────────────────────────────────┘
```

1. **Step 13 (RFQ Dispatch) Integration:** Bid deadline closure automatically flags the RFQ as `Responses In Progress` and queues comparison compilation.
2. **Step 19 (Vendor Rating Scorecard) Integration:** During scoring calculation, `WeightedScoringEngineService` issues a batched QueryBuilder projection to `tabVendor Rating` for each bidding supplier, fetching their current 4-factor composite performance index without N+1 query overhead.
3. **Downstream Step 15 (Purchase Order Placement) Integration:** Once submitted, `POAwardInstantiationService` constructs a complete `tabPurchase Order`, setting:
   - Supplier, Quotation Reference, Project Reference, Target Warehouse/Site.
   - Item rates frozen to the exact agreed basic and landed rates.
   - Taxes and Charges table pre-populated with freight, insurance, and GST splits.
4. **Omnichannel Vendor Communication:**
   - Winning Supplier: Automated WhatsApp & Email notification with PO draft and delivery schedule.
   - Non-Awarded Suppliers: Automated professional regret letter thanking them for tender participation, preserving supplier relationship goodwill.

---

## 8. Automated Testing & QA Criteria

### 8.1 Testing Architecture & Invariants

In strict adherence to [`architect_docs/07_AUTOMATED_TESTING_QA_CI_CD.md`](../architect_docs/07_AUTOMATED_TESTING_QA_CI_CD.md):

- **Base Class:** All test cases inherit from `frappe.tests.utils.FrappeTestCase`.
- **Zero-Commit Rule:** `frappe.db.commit()` is **strictly prohibited** in all test routines. The test runner automatically rolls back transactions at teardown, ensuring 100% test database isolation.
- **Mocking & Isolation:** External WhatsApp and email brokers are mocked using `unittest.mock.patch`.

### 8.2 Concrete Integration Test Suite

```python
# File: solar_module/tests/test_quotation_comparison_matrix.py
import unittest
from unittest.mock import patch
import frappe
from frappe.tests.utils import FrappeTestCase
from solar_module.services.procurement.landed_cost_service import LandedCostCalculationService
from solar_module.services.procurement.weighted_scoring_service import WeightedScoringEngineService
from solar_module.services.procurement.comparison_matrix_service import QuotationComparisonMatrixService

class TestQuotationComparisonMatrix(FrappeTestCase):
    def setUp(self):
        super().setUp()
        self.cleanup_records = []

    def tearDown(self):
        # Automatic rollback occurs; cleanup explicit test records if needed
        super().tearDown()

    def test_landed_cost_normalization_ex_factory_vs_for_site(self):
        """Test that Ex-Factory quote with freight calculates higher landed cost than FOR-Site quote."""
        # Vendor A: Ex-Factory Basic 100 + Freight 10 + Insurance 2 + Unloading 1 on Qty 10
        vendor_a = LandedCostCalculationService.calculate_item_landed_cost(
            basic_rate=100.0, qty=10.0, freight=100.0, insurance=20.0, packaging=0.0, unloading=10.0
        )
        self.assertEqual(vendor_a["landed_rate_unit"], 113.0)
        self.assertEqual(vendor_a["total_landed_amount"], 1130.0)

        # Vendor B: FOR-Site Basic 110 (all freight & insurance included)
        vendor_b = LandedCostCalculationService.calculate_item_landed_cost(
            basic_rate=110.0, qty=10.0, freight=0.0, insurance=0.0, packaging=0.0, unloading=0.0
        )
        self.assertEqual(vendor_b["landed_rate_unit"], 110.0)
        self.assertEqual(vendor_b["total_landed_amount"], 1100.0)

        # Assert Vendor B is true L1 despite having higher raw basic rate
        self.assertLess(vendor_b["total_landed_amount"], vendor_a["total_landed_amount"])

    def test_weighted_scoring_engine_calculation(self):
        """Test 100-point composite scoring calculation across cost, time, and vendor rating."""
        scores = WeightedScoringEngineService.compute_composite_score(
            vendor_landed_cost=1000.0,
            l1_landed_cost=1000.0,
            vendor_lead_days=7,
            min_lead_days=7,
            target_max_lead_days=21,
            vendor_rating_score=90.0,
            payment_terms_rating=10.0
        )
        # Commercial = 50.0, Lead = 25.0, Rating = 13.5 (90% of 15), Terms = 10.0 -> Total = 98.5
        self.assertEqual(scores["commercial_score"], 50.0)
        self.assertEqual(scores["lead_time_score"], 25.0)
        self.assertEqual(scores["rating_score"], 13.5)
        self.assertEqual(scores["terms_score"], 10.0)
        self.assertEqual(scores["composite_score"], 98.5)

    def test_non_l1_selection_gate_rejection_without_justification(self):
        """Assert submitting matrix with non-L1 vendor without justification raises ValidationError."""
        matrix = frappe.new_doc("Quotation Comparison Matrix")
        matrix.rfq_reference = "TEST-RFQ-001"
        matrix.is_l1_selected = 0
        matrix.non_l1_justification = "Short" # Below 40 chars

        self.assertRaises(frappe.ValidationError, matrix.on_submit)

    def test_sealed_bids_unsealing_check_gate(self):
        """Assert comparison cannot be compiled if RFQ sealed bids are not unsealed."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.custom_sealed_bids = 1
        rfq.custom_bids_unsealed = 0
        rfq.name = "TEST-SEALED-RFQ"

        with self.assertRaises(frappe.PermissionError):
            QuotationComparisonMatrixService.validate_sealed_bids_unsealed(rfq)
```

---

## 9. Operational SOP, Error Resolution & Runbook

### 9.1 Operational Standard Operating Procedure (SOP)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             PROCUREMENT COMPARISON MATRIX SOP                                    │
├───────┬──────────────────────┬─────────────────────────┬─────────────────────────────────────────┤
│ Stage │ Actor                │ Action Step             │ Operational Procedure                   │
├───────┼──────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│ **1** │ `Purchase Assistant` │ Ingest & Validate Quotes│ Ingest vendor quotes via portal or enter│
│       │                      │                         │ basic rates, freight, and lead times.   │
│ **2** │ `Purchase Assistant` │ Generate Comparison     │ Click "Create Comparison Matrix" on RFQ.│
│       │                      │                         │ Run landed cost normalization engine.   │
│ **3** │ `Project Engineer`   │ Technical Clearance     │ Verify module/inverter datasheets and   │
│       │                      │                         │ sign off technical compliance column.   │
│ **4** │ `Purchase Assistant` │ Review Scoring & Rank   │ Review 100-pt scores. Formulate purchase│
│       │                      │                         │ award recommendation (L1 vs Non-L1).    │
│ **5** │ `Purchase Manager`   │ Authorize Award Sign-off│ If Non-L1: Enter detailed justification.│
│       │                      │                         │ Review margin impact & submit matrix.   │
│ **6** │ `Purchase Assistant` │ Release Purchase Order  │ Click "Spawn Purchase Order" to release │
│       │                      │                         │ formal contract baseline to supplier.   │
└───────┴──────────────────────┴─────────────────────────┴─────────────────────────────────────────┘
```

### 9.2 Error Codes & Resolution Runbook

| Error Code    | Trigger Condition                                               | Root Cause                                                         | Operator Resolution Procedure                                                                               |
| :------------ | :-------------------------------------------------------------- | :----------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `ERR-QCM-001` | "Cannot generate comparison: Bids for RFQ are sealed"           | RFQ `custom_sealed_bids = 1` but unsealing ceremony not performed. | `Purchase Manager` must open the RFQ and click "Perform Bid Unsealing Ceremony" with password verification. |
| `ERR-QCM-002` | "At least 2 valid supplier quotations are required"             | RFQ has $< 2$ active quotes.                                       | Solicit additional supplier quotes or provide approved Single-Source justification in RFQ.                  |
| `ERR-QCM-003` | "Non-L1 selection requires minimum 40 characters justification" | Non-L1 vendor chosen with brief or empty reason.                   | Provide detailed technical or commercial justification explaining why lowest price was bypassed.            |
| `ERR-QCM-004` | "Only Purchase Manager or Admin can authorize award"            | `Purchase Assistant` attempting to submit matrix.                  | Route comparison matrix to `Purchase Manager` or `Admin` for formal digital sign-off.                       |
| `ERR-QCM-005` | "Quotation has expired (valid_till date passed)"                | Vendor quote validity expired during review.                       | Contact vendor to extend quotation validity date and update `valid_till` in `Supplier Quotation`.           |

### 9.3 L3 DevOps & System Administration Runbook

1. **Redis SLA Daemon Health Check:**
   ```bash
   # Check active background jobs for procurement SLA
   bench execute solar_module.tasks.monitor_quotation_evaluation_sla
   ```
2. **Re-calculating Landed Costs in Batch:**
   ```bash
   bench --site <site-name> execute solar_module.api.procurement.recompute_active_matrices
   ```
3. **Database Index Verification:**
   Verify foreign key indexes exist for high-frequency queries:
   ```sql
   SHOW INDEX FROM `tabQuotation Comparison Matrix` WHERE Column_name IN ('rfq_reference', 'evaluation_status', 'awarded_supplier');
   ```

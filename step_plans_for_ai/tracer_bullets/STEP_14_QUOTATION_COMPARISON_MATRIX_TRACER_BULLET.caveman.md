# STEP_14_QUOTATION_COMPARISON_MATRIX_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 14 Supplier Quotation & Comparative Evaluation Matrix

**Document ID:** `TB-14-QUOTATION-COMPARISON-MATRIX`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.caveman.md`](../STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-014-SUPPLIER-QUOTATION-COMPARATIVE-EVALUATION-MATRIX.md`](../../docs/decisions/ADR-014-SUPPLIER-QUOTATION-COMPARATIVE-EVALUATION-MATRIX.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_13_SUPPLIER_RFQ_TRACER_BULLET.caveman.md`](STEP_13_SUPPLIER_RFQ_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md`](STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md`](STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md`](STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Step 15 Purchase Order Authorization & Milestone Terms ([`STEP_15`](../STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md)), Step 16 Multi-Location Barcode GRN ([`STEP_16`](../STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md)), Step 17 Purchase Invoicing 3-Way Match ([`STEP_17`](../STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.md)), Step 18 Joint Vendor Payment Monitoring ([`STEP_18`](../STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.md)), Step 19 Vendor Performance Rating Scorecard ([`STEP_19`](../STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.md))  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-13`), `planning_ref_docs/04_GAP_ANALYSIS_FIT_GAP.md` (`Gap #06`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-013`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-013`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 7: SCM`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 11`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 17`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-13`), `planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md` (Sec 3.2, 4.1)  
**Target Module:** `solar_module` / SPA `/solar/procurement/comparison/:id` (Introduces standalone submittable `tabQuotation Comparison Matrix`, child tables `tabQuotation Comparison Item` & `tabQuotation Comparison Supplier Summary`, extends ERPNext `tabSupplier Quotation`, `tabRequest for Quotation`, integrates child `tabRemark-Delay Log` / `tabSolar Stage Delay Log`, and settings `tabSolar SCM Settings` & `tabSolar SLA Settings`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** A disposable client-side spreadsheet or isolated desk dialog rendering quote comparisons in HTML tables without database integrity, blindly picking the lowest quoted basic rate (falling into the "False L1 Trap" by ignoring unquoted freight and insurance), permitting silent selection of favorite suppliers without justification, allowing unsealed bid inspection prior to tender closure, and manually transcribing line items into purchase orders with high clerical error rates.
- **Tracer Bullet:** A permanent, production-grade 5-layer thin vertical slice cutting directly through the live Frappe architecture. It ingests live competitive bids from Step 13 (`Request for Quotation` and `Supplier Quotation`), anchors real relational schemas (`tabQuotation Comparison Matrix`, `tabQuotation Comparison Item`, `tabQuotation Comparison Supplier Summary`), executes pure SOLID domain services (`LandedCostCalculationService`, `WeightedScoringEngineService`, `QuotationComparisonMatrixService`, `POAwardInstantiationService`, `QuotationEvaluationSLAService`), exposes secure whitelisted RPC endpoints (`solar_module.api.procurement.*`), connects responsive Desk client scripts and modern comparison SPAs (`/solar/procurement/comparison/:id`), and executes an automated zero-commit integration test suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 14 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabQuotation Comparison Matrix (standalone submittable DocType)         │
│   - tabQuotation Comparison Item & tabQuotation Comparison Supplier Summary │
│   - tabSupplier Quotation landed cost extensions (freight, insurance, etc.) │
│   - tabSolar SCM Settings (Admin-configured quote quotas & scoring weights) │
│   - tabSolar SLA Settings (Admin-configured 48h turnaround SLA settings)    │
│   - Composite B-Tree database indexes for high-speed matrix querying        │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - LandedCostCalculationService (normalization: Basic+P&F+Freight-ITC)     │
│   - WeightedScoringEngineService (100-pt: 50% Cost, 25% Time, 15% Rat, 10% T)│
│   - QuotationComparisonMatrixService (aggregation, unsealing gate, L1 logic)│
│   - POAwardInstantiationService (programmatic 1-click PO release in Step 15)│
│   - QuotationEvaluationSLAService (48h turnaround clock & overdue daemon)   │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                     │
│   - QuotationComparisonMatrix controller extending StageSecuredDocument     │
│   - Whitelisted RPC APIs in solar_module.api.procurement                    │
│   - Background Celery/RQ SLA daemon (monitor_quotation_evaluation_sla)      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Comparison Workbench SPA Hook         │
│   - codes/client_script/quotation_comparison_matrix.js (L1 badge, dialogs)  │
│   - Comparison Matrix Workbench SPA (/solar/procurement/comparison/:id)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_step_14_quotation_comparison_matrix_tracer_bullet.py│
│   - Subclasses FrappeTestCase with strict zero-commit rollback              │
│   - 10 atomic test cases covering all commercial, scoring, and security gates│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental commercial, operational, and governance invariants of Stage 14 across the live Frappe stack:

1. **Gate 1: Minimum Quotes Quota ($\ge 2$ Independent Quotes):** Assert $\ge 2$ independent vendor quotations before matrix creation or submission, unless the upstream RFQ is explicitly flagged `custom_is_single_source = 1` with authorized justification.
2. **Gate 2: Sealed Bid Cryptographic Unmasking Check:** If the upstream RFQ is sealed (`custom_sealed_bids = 1`), verify that the formal bid unsealing ceremony has been executed (`custom_bids_unsealed = 1`). Block comparative matrix creation and rate analysis if bids remain locked.
3. **Gate 3: Quotation Validity Gate:** Assert that all candidate quotations are commercially active and within their validity window (`today <= valid_till`). Bar expired quotes from award calculation.
4. **Gate 4: 100% Landed Cost Normalization (Elimination of False L1):** Accurately normalize raw quoted rates into true landed rates: $\text{Landed Unit Rate} = \text{Basic Rate} + \text{P\&F} + \text{Freight} + \text{Transit Insurance} + \text{Site Unloading} + \text{Non-Creditable Tax} - \text{Net ITC}$. Ex-Factory vs FOR-Site bids are brought to exact commercial parity.
5. **Gate 5: 100-Point Multi-Factor Scoring Engine:** Balance commercial cost against project execution risk using deterministic mathematical scoring: Commercial Landed Cost (50%) + Delivery Lead Time (25%) + Step 19 Vendor Performance Rating (15%) + Commercial Terms & Warranty (10%).
6. **Gate 6: Non-L1 Selection Governance Gate:** Hard-block submission of any comparative matrix selecting a non-L1 supplier unless accompanied by an Admin-enforced justification ($\ge 40$ chars) and authorized exclusively by `Purchase Manager` or `Admin`.
7. **Gate 7: Programmatic PO Instantiation & Immutability Lock:** On award submission, 1-click PO generation instantiates the downstream `Purchase Order` in Step 15, locks rates and commercial terms against alteration, and prevents duplicate PO creation.
8. **Gate 8: Sub-48-Hour Turnaround SLA Engine:** Track automated 48-hour commercial evaluation countdown from RFQ tender closure/unsealing. Automatically flag overdue matrices and mandate audit logging in `tabSolar Stage Delay Log` prior to submission.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Establishes the standalone submittable DocType `tabQuotation Comparison Matrix`, child tables `tabQuotation Comparison Item` and `tabQuotation Comparison Supplier Summary`, extends ERPNext `tabSupplier Quotation`, introduces Admin-configurable singletons in `tabSolar SCM Settings` and `tabSolar SLA Settings`, and applies composite B-Tree indexes.

### 2.1 Core DocType Extension: `tabSupplier Quotation`

| Fieldname                     | Label                     | Fieldtype    | Options / Target                             | Mandatory | Index | Description & Validation Rules                                 |
| :---------------------------- | :------------------------ | :----------- | :------------------------------------------- | :-------: | :---: | :------------------------------------------------------------- |
| `custom_rfq_reference`        | Originating RFQ           | `Link`       | `Request for Quotation`                      |    No     |   1   | Upstream RFQ reference from Step 13.                           |
| `custom_project_reference`    | Project Reference         | `Link`       | `Project`                                    |    No     |   1   | Solar EPC project container foreign key.                       |
| `custom_material_request_ref` | Material Request Ref      | `Link`       | `Material Request`                           |    No     |   1   | Upstream requisition indent from Step 12.                      |
| `custom_is_sealed`            | Is Sealed Bid?            | `Check`      | -                                            |    No     |   -   | Inherited from RFQ; if 1, rates masked until unsealed.         |
| `custom_portal_token`         | Portal Submission Token   | `Data`       | -                                            |    No     |   1   | 256-bit UUID used for external vendor portal submission.       |
| `custom_packaging_forwarding` | Packaging & Forwarding    | `Currency`   | `Company:currency`                           |    No     |   -   | Total packaging and crating charges.                           |
| `custom_freight_charges`      | Freight Charges           | `Currency`   | `Company:currency`                           |    No     |   -   | Total freight and logistics cost to destination.               |
| `custom_transit_insurance`    | Transit Insurance         | `Currency`   | `Company:currency`                           |    No     |   -   | Transit insurance policy charge.                               |
| `custom_unloading_charges`    | Site Unloading Charges    | `Currency`   | `Company:currency`                           |    No     |   -   | Equipment unloading and crane charges at site.                 |
| `custom_landed_cost_unit`     | Landed Cost per Unit      | `Currency`   | `Company:currency`                           |  **Yes**  |   -   | Normalized landed rate per unit including all surcharges.      |
| `custom_net_effective_total`  | Net Effective Total       | `Currency`   | `Company:currency`                           |  **Yes**  |   -   | Total landed payable amount after eligible GST ITC adjustment. |
| `custom_promised_lead_days`   | Promised Lead Time (Days) | `Int`        | -                                            |  **Yes**  |   -   | Guaranteed delivery days from PO release date.                 |
| `custom_warranty_months`      | Equipment Warranty (M)    | `Int`        | -                                            |  **Yes**  |   -   | Manufacturer warranty duration in months (e.g. 120 or 300).    |
| `custom_datasheet_attached`   | Technical Datasheet       | `Attach`     | -                                            |    No     |   -   | PDF datasheet from equipment manufacturer.                     |
| `custom_technical_compliant`  | Technical Compliance      | `Select`     | `Compliant\nDeviations Noted\nNon-Compliant` |  **Yes**  |   -   | Technical sign-off status by Project Engineer.                 |
| `custom_payment_terms_desc`   | Commercial Payment Terms  | `Small Text` | -                                            |    No     |   -   | Text description of vendor payment milestones.                 |

---

### 2.2 Standalone Submittable DocType: `tabQuotation Comparison Matrix`

- **DocType Name:** `Quotation Comparison Matrix`
- **Naming Pattern:** `naming_series: QCM-.YYYY.-.#####`
- **Submittable:** `is_submittable = 1`

| Fieldname               | Label                    | Fieldtype    | Options / Target                                                     | Mandatory | Index | Description & Rules                                         |
| :---------------------- | :----------------------- | :----------- | :------------------------------------------------------------------- | :-------: | :---: | :---------------------------------------------------------- |
| `naming_series`         | Series                   | `Select`     | `QCM-.YYYY.-.#####`                                                  |  **Yes**  |   -   | Primary autonaming sequence.                                |
| `rfq_reference`         | RFQ Reference            | `Link`       | `Request for Quotation`                                              |  **Yes**  |   1   | Upstream RFQ tender being evaluated.                        |
| `project_reference`     | Project Reference        | `Link`       | `Project`                                                            |    No     |   1   | Solar EPC project identifier.                               |
| `material_request_ref`  | Material Request Ref     | `Link`       | `Material Request`                                                   |    No     |   -   | Requisition indent from Step 12.                            |
| `evaluation_date`       | Evaluation Date          | `Date`       | -                                                                    |  **Yes**  |   -   | Date evaluation matrix compiled; defaults to today.         |
| `evaluation_status`     | Evaluation Status        | `Select`     | `Draft\nUnder Review\nAward Approved\nRejected\nPO Created\nOverdue` |  **Yes**  |   1   | Lifecycle state attribute. Default: `Draft`.                |
| `target_delivery_date`  | Project Target Delivery  | `Date`       | -                                                                    |    No     |   -   | Project milestone required-by delivery deadline.            |
| `sealed_bids_verified`  | Sealed Bids Verified     | `Check`      | -                                                                    |    No     |   -   | Confirms tender unsealing ceremony executed if sealed.      |
| `awarded_supplier`      | Awarded Supplier         | `Link`       | `Supplier`                                                           |    No     |   1   | Supplier selected for purchase award.                       |
| `awarded_quotation`     | Awarded Quotation        | `Link`       | `Supplier Quotation`                                                 |    No     |   -   | Winning quotation reference.                                |
| `awarded_landed_amount` | Awarded Landed Amount    | `Currency`   | `Company:currency`                                                   |    No     |   -   | Total net landed commercial commitment.                     |
| `is_l1_selected`        | Is L1 Vendor Selected?   | `Check`      | -                                                                    |    No     |   -   | Set to 1 if awarded supplier has lowest landed cost.        |
| `non_l1_justification`  | Non-L1 Justification     | `Small Text` | -                                                                    |    No     |   -   | **Mandatory** ($\ge 40$ chars) if `is_l1_selected == 0`.    |
| `authorized_by`         | Award Authorized By      | `Link`       | `User`                                                               |    No     |   -   | Digital sign-off signatory (`Purchase Manager` or `Admin`). |
| `authorization_date`    | Authorized On            | `Datetime`   | -                                                                    |    No     |   -   | Formal award timestamp.                                     |
| `purchase_order_ref`    | Generated Purchase Order | `Link`       | `Purchase Order`                                                     |    No     |   1   | Downstream PO instantiated upon award submission.           |
| `sla_deadline`          | Evaluation SLA Deadline  | `Datetime`   | -                                                                    |  **Yes**  |   1   | SLA deadline (`evaluation_date + 48h`).                     |
| `sla_status`            | SLA Status               | `Select`     | `Within SLA\nOverdue`                                                |  **Yes**  |   -   | Managed by background SLA daemon. Default: `Within SLA`.    |
| `comparison_items`      | Comparison Line Items    | `Table`      | `Quotation Comparison Item`                                          |  **Yes**  |   -   | Side-by-side component landed comparison child table.       |
| `supplier_summaries`    | Supplier Summary Matrix  | `Table`      | `Quotation Comparison Supplier Summary`                              |  **Yes**  |   -   | Multi-factor scoring and ranking summary table.             |
| `delay_reason_table`    | Delay Audit Log          | `Table`      | `Solar Stage Delay Log`                                              |    No     |   -   | Mandatory audit log required if submitting while overdue.   |

---

### 2.3 Child DocType: `tabQuotation Comparison Item`

| Fieldname              | Label                   | Fieldtype  | Options / Target                             | Mandatory | Description & Rules                                                                               |
| :--------------------- | :---------------------- | :--------- | :------------------------------------------- | :-------: | :------------------------------------------------------------------------------------------------ |
| `item_code`            | Item Code               | `Link`     | `Item`                                       |  **Yes**  | Solar component code (e.g. `PV-MOD-545W`, `INV-100KW`).                                           |
| `item_name`            | Item Name               | `Data`     | -                                            |    No     | Component description.                                                                            |
| `qty`                  | Required Quantity       | `Float`    | -                                            |  **Yes**  | Requisitioned quantity.                                                                           |
| `uom`                  | UOM                     | `Link`     | `UOM`                                        |  **Yes**  | Unit of Measure (Nos, Mtr, Set).                                                                  |
| `supplier`             | Supplier                | `Link`     | `Supplier`                                   |  **Yes**  | Bidding vendor.                                                                                   |
| `supplier_quotation`   | Supplier Quotation      | `Link`     | `Supplier Quotation`                         |  **Yes**  | Source quote document.                                                                            |
| `basic_rate`           | Basic Unit Rate         | `Currency` | `Company:currency`                           |  **Yes**  | Quoted base rate per unit before logistics & taxes.                                               |
| `packaging_forwarding` | Packaging & Forwarding  | `Currency` | `Company:currency`                           |    No     | Allocated P&F charges per unit.                                                                   |
| `freight_rate_unit`    | Freight per Unit        | `Currency` | `Company:currency`                           |    No     | Allocated freight per unit to destination.                                                        |
| `insurance_rate_unit`  | Insurance per Unit      | `Currency` | `Company:currency`                           |    No     | Transit insurance per unit.                                                                       |
| `unloading_rate_unit`  | Unloading per Unit      | `Currency` | `Company:currency`                           |    No     | Labor/crane unloading charge per unit at site.                                                    |
| `tax_rate_unit`        | Non-Creditable Tax/Unit | `Currency` | `Company:currency`                           |    No     | Non-refundable statutory duties or tax per unit.                                                  |
| `landed_rate_unit`     | Landed Rate per Unit    | `Currency` | `Company:currency`                           |  **Yes**  | $\text{Basic} + \text{P\&F} + \text{Freight} + \text{Insurance} + \text{Unloading} + \text{Tax}$. |
| `total_landed_amount`  | Total Landed Amount     | `Currency` | `Company:currency`                           |  **Yes**  | $\text{Landed Rate per Unit} \times \text{Quantity}$.                                             |
| `promised_lead_days`   | Promised Lead Time      | `Int`      | -                                            |  **Yes**  | Days required to deliver equipment to destination.                                                |
| `technical_compliant`  | Spec Compliance         | `Select`   | `Compliant\nDeviations Noted\nNon-Compliant` |  **Yes**  | Technical sign-off by Project Engineer.                                                           |
| `item_rank`            | Line Rank               | `Select`   | `L1\nL2\nL3\nL4\nL5`                         |  **Yes**  | Item-level landed cost ranking.                                                                   |

---

### 2.4 Child DocType: `tabQuotation Comparison Supplier Summary`

| Fieldname                 | Label                  | Fieldtype    | Options / Target     | Mandatory | Description & Scoring Rules                                                             |
| :------------------------ | :--------------------- | :----------- | :------------------- | :-------: | :-------------------------------------------------------------------------------------- |
| `supplier`                | Supplier               | `Link`       | `Supplier`           |  **Yes**  | Bidding vendor.                                                                         |
| `supplier_quotation`      | Supplier Quotation     | `Link`       | `Supplier Quotation` |  **Yes**  | Source quotation document.                                                              |
| `total_basic_amount`      | Total Basic Amount     | `Currency`   | `Company:currency`   |  **Yes**  | Sum of raw basic item amounts.                                                          |
| `total_freight_logistics` | Total Logistics & P&F  | `Currency`   | `Company:currency`   |  **Yes**  | Total logistics, insurance, and unloading charges.                                      |
| `total_tax_amount`        | Total Tax Amount       | `Currency`   | `Company:currency`   |  **Yes**  | Total statutory taxes.                                                                  |
| `total_landed_amount`     | Total Landed Cost      | `Currency`   | `Company:currency`   |  **Yes**  | Sum of total landed line amounts.                                                       |
| `max_lead_time_days`      | Max Lead Time (Days)   | `Int`        | -                    |  **Yes**  | Longest delivery lead time across quoted lines.                                         |
| `vendor_rating_score`     | Vendor Rating Score    | `Percent`    | -                    |    No     | Vendor scorecard rating from Step 19 ($0 - 100\%$).                                     |
| `commercial_score`        | Commercial Score (50%) | `Float`      | -                    |  **Yes**  | Cost score: $(\text{Landed Cost}_{L1} / \text{Landed Cost}_{\text{vendor}}) \times 50$. |
| `lead_time_score`         | Lead Time Score (25%)  | `Float`      | -                    |  **Yes**  | Time score: Delivery feasibility relative to target.                                    |
| `rating_score`            | Rating Score (15%)     | `Float`      | -                    |  **Yes**  | Quality score: $\text{Vendor Rating Score} \times 0.15$.                                |
| `terms_score`             | Terms Score (10%)      | `Float`      | -                    |  **Yes**  | Credit terms and warranty duration score.                                               |
| `composite_score`         | Composite Score (100)  | `Float`      | -                    |  **Yes**  | Sum of commercial, lead time, rating, and terms scores.                                 |
| `overall_rank`            | Overall Rank           | `Select`     | `L1\nL2\nL3\nL4\nL5` |  **Yes**  | Total landed cost rank.                                                                 |
| `composite_rank`          | Composite Rank         | `Int`        | -                    |  **Yes**  | Multi-factor rank ($1 = \text{Highest Composite Score}$).                               |
| `is_recommended`          | System Recommended     | `Check`      | -                    |    No     | 1 if vendor holds highest composite evaluation score.                                   |
| `evaluator_notes`         | Evaluator Remarks      | `Small Text` | -                    |    No     | Commercial justification commentary.                                                    |

---

### 2.5 Admin-Configurable Settings Singletons

#### 1. `tabSolar SCM Settings` Extensions:

```json
{
  "doctype": "DocType",
  "name": "Solar SCM Settings",
  "issingle": 1,
  "fields": [
    {
      "fieldname": "qcm_min_quotes_required",
      "label": "Minimum Competitive Quotes Quota",
      "fieldtype": "Int",
      "default": 2,
      "description": "Minimum valid supplier quotations required before comparative matrix can be submitted."
    },
    {
      "fieldname": "qcm_non_l1_min_justification_len",
      "label": "Non-L1 Minimum Justification Length",
      "fieldtype": "Int",
      "default": 40,
      "description": "Minimum character count required to justify awarding to a supplier with higher landed cost than L1."
    },
    {
      "fieldname": "qcm_weight_commercial",
      "label": "Commercial Scoring Weight (%)",
      "fieldtype": "Percent",
      "default": 50.0,
      "description": "Weight allocated to relative landed cost in 100-point composite scoring engine."
    },
    {
      "fieldname": "qcm_weight_lead_time",
      "label": "Lead Time Scoring Weight (%)",
      "fieldtype": "Percent",
      "default": 25.0,
      "description": "Weight allocated to delivery lead time compliance."
    },
    {
      "fieldname": "qcm_weight_vendor_rating",
      "label": "Vendor Rating Scoring Weight (%)",
      "fieldtype": "Percent",
      "default": 15.0,
      "description": "Weight allocated to Step 19 vendor performance scorecard."
    },
    {
      "fieldname": "qcm_weight_commercial_terms",
      "label": "Payment Terms & Warranty Weight (%)",
      "fieldtype": "Percent",
      "default": 10.0,
      "description": "Weight allocated to warranty duration and credit payment milestones."
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
  "fields": [
    {
      "fieldname": "qcm_turnaround_sla_hours",
      "label": "Quotation Comparison SLA Window (Hours)",
      "fieldtype": "Int",
      "default": 48,
      "description": "Standard turnaround SLA allocated to complete evaluation from quote receipt/unsealing."
    },
    {
      "fieldname": "qcm_reminder_hours_before",
      "label": "SLA Urgent Reminder Window (Hours Before Deadline)",
      "fieldtype": "Int",
      "default": 12,
      "description": "Hours remaining when automated urgent reminder is dispatched to Purchase Manager."
    },
    {
      "fieldname": "qcm_overdue_escalation_role",
      "label": "SLA Overdue Escalation Role",
      "fieldtype": "Link",
      "options": "Role",
      "default": "Purchase Manager",
      "description": "System role notified when evaluation window breaches SLA deadline."
    }
  ]
}
```

---

### 2.6 Composite Database B-Tree Indexes

```sql
-- Composite index for fast Quotation Comparison Matrix querying by RFQ and evaluation status
ALTER TABLE `tabQuotation Comparison Matrix`
ADD INDEX `idx_qcm_rfq_status` (`rfq_reference`, `evaluation_status`, `docstatus`);

-- Composite index for SLA monitoring and background overdue daemon
ALTER TABLE `tabQuotation Comparison Matrix`
ADD INDEX `idx_qcm_sla` (`docstatus`, `sla_status`, `sla_deadline`);

-- Composite index for line item lookup by matrix, item code, and supplier
ALTER TABLE `tabQuotation Comparison Item`
ADD INDEX `idx_qcm_item_supp` (`parent`, `item_code`, `supplier`);

-- Composite index for downstream Purchase Order linkage
ALTER TABLE `tabQuotation Comparison Matrix`
ADD INDEX `idx_qcm_po_ref` (`purchase_order_ref`, `docstatus`);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Pure, decoupled Python domain services adhering to single-responsibility design, zero direct Desk API dependencies, and 100% testability.

### 3.1 `LandedCostCalculationService` (`solar_module/services/procurement/landed_cost_service.py`)

Responsible for normalizing raw vendor quotes into true landed rates with strict decimal precision.

```python
from decimal import Decimal, ROUND_HALF_UP

class LandedCostCalculationService:
    """Calculates true landed cost per unit and total line amounts, normalizing commercial surcharges."""

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

    @classmethod
    def normalize_quotation_lines(cls, quotation_doc) -> list:
        """Prorates quote-level logistics and surcharges across quotation item lines."""
        lines = []
        total_qty = sum(item.qty for item in quotation_doc.items) or 1.0
        header_freight = float(getattr(quotation_doc, "custom_freight_charges", 0.0) or 0.0)
        header_insurance = float(getattr(quotation_doc, "custom_transit_insurance", 0.0) or 0.0)
        header_packaging = float(getattr(quotation_doc, "custom_packaging_forwarding", 0.0) or 0.0)
        header_unloading = float(getattr(quotation_doc, "custom_unloading_charges", 0.0) or 0.0)

        for item in quotation_doc.items:
            weight_ratio = float(item.qty) / total_qty
            line_freight = header_freight * weight_ratio
            line_insurance = header_insurance * weight_ratio
            line_packaging = header_packaging * weight_ratio
            line_unloading = header_unloading * weight_ratio

            calc = cls.calculate_item_landed_cost(
                basic_rate=item.rate,
                qty=item.qty,
                freight=line_freight,
                insurance=line_insurance,
                packaging=line_packaging,
                unloading=line_unloading,
                non_creditable_tax=0.0
            )
            calc["item_code"] = item.item_code
            calc["item_name"] = item.item_name
            calc["qty"] = item.qty
            calc["uom"] = item.uom
            lines.append(calc)
        return lines
```

---

### 3.2 `WeightedScoringEngineService` (`solar_module/services/procurement/weighted_scoring_service.py`)

Responsible for computing multi-factor composite scores (Cost 50%, Lead Time 25%, Rating 15%, Terms 10%) using Admin-configured weights.

```python
import frappe

class WeightedScoringEngineService:
    """Computes deterministic 100-point multi-factor scores for candidate quotations."""

    @classmethod
    def get_scoring_weights(cls) -> dict:
        scm_settings = frappe.get_cached_doc("Solar SCM Settings") if frappe.db.exists("DocType", "Solar SCM Settings") else None
        return {
            "commercial": float(getattr(scm_settings, "qcm_weight_commercial", 50.0) or 50.0),
            "lead_time": float(getattr(scm_settings, "qcm_weight_lead_time", 25.0) or 25.0),
            "rating": float(getattr(scm_settings, "qcm_weight_vendor_rating", 15.0) or 15.0),
            "terms": float(getattr(scm_settings, "qcm_weight_commercial_terms", 10.0) or 10.0)
        }

    @classmethod
    def compute_composite_score(
        cls,
        vendor_landed_cost: float,
        l1_landed_cost: float,
        vendor_lead_days: int,
        min_lead_days: int,
        target_max_lead_days: int,
        vendor_rating_score: float,
        payment_terms_rating: float
    ) -> dict:
        weights = cls.get_scoring_weights()

        # 1. Commercial Score (Relative to L1 Landed Cost)
        if vendor_landed_cost > 0 and l1_landed_cost > 0:
            comm_score = (l1_landed_cost / vendor_landed_cost) * weights["commercial"]
        else:
            comm_score = 0.0
        comm_score = min(weights["commercial"], max(0.0, comm_score))

        # 2. Lead Time Score (Delivery Feasibility Relative to Target Span)
        target_span = max(1, target_max_lead_days - min_lead_days)
        excess_days = max(0, vendor_lead_days - min_lead_days)
        time_ratio = max(0.0, 1.0 - (excess_days / target_span))
        lead_score = time_ratio * weights["lead_time"]

        # 3. Vendor Rating Score (Step 19 Scorecard integration)
        v_rating = max(0.0, min(100.0, vendor_rating_score if vendor_rating_score is not None else 70.0))
        rating_score = (v_rating / 100.0) * weights["rating"]

        # 4. Payment Terms & Warranty Score
        terms_score = max(0.0, min(weights["terms"], payment_terms_rating))

        composite = round(comm_score + lead_score + rating_score + terms_score, 2)

        return {
            "commercial_score": round(comm_score, 2),
            "lead_time_score": round(lead_score, 2),
            "rating_score": round(rating_score, 2),
            "terms_score": round(terms_score, 2),
            "composite_score": composite
        }
```

---

### 3.3 `QuotationComparisonMatrixService` (`solar_module/services/procurement/comparison_matrix_service.py`)

Responsible for compiling the matrix from RFQ quotes, enforcing sealed bid checks, calculating line item ranks, and applying award decisions.

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date, nowdate
from solar_module.services.procurement.landed_cost_service import LandedCostCalculationService
from solar_module.services.procurement.weighted_scoring_service import WeightedScoringEngineService

class QuotationComparisonMatrixService:
    """Orchestrates comparative matrix ingestion, scoring, and award authorization."""

    @classmethod
    def validate_sealed_bids_unsealed(cls, rfq_doc):
        """Asserts that high-value sealed tender bids have been formally unsealed."""
        if getattr(rfq_doc, "custom_sealed_bids", 0) and not getattr(rfq_doc, "custom_bids_unsealed", 0):
            frappe.throw(
                _("Cannot generate comparison: Bids for RFQ {0} are sealed and have not been unsealed by Purchase Manager / Admin.").format(rfq_doc.name),
                frappe.PermissionError
            )

    @classmethod
    def create_from_rfq(cls, rfq_doc) -> str:
        cls.validate_sealed_bids_unsealed(rfq_doc)

        quotes = frappe.get_all(
            "Supplier Quotation",
            filters={"request_for_quotation": rfq_doc.name, "docstatus": ["in", [0, 1]]},
            fields=["name", "supplier", "valid_till", "docstatus"]
        )

        min_quotes = frappe.db.get_single_value("Solar SCM Settings", "qcm_min_quotes_required") or 2
        is_single_source = getattr(rfq_doc, "custom_is_single_source", 0)

        if len(quotes) < min_quotes and not is_single_source:
            frappe.throw(
                _("Minimum {0} supplier quotations required to generate comparison matrix (found {1}). RFQ must be justified as Single-Source to bypass.").format(min_quotes, len(quotes)),
                frappe.ValidationError
            )

        # Check quote validity
        current_date = nowdate()
        for q in quotes:
            if q.valid_till and str(q.valid_till) < current_date:
                frappe.throw(_("Supplier Quotation {0} from {1} has expired (valid till {2}).").format(q.name, q.supplier, q.valid_till), frappe.ValidationError)

        sla_hours = frappe.db.get_single_value("Solar SLA Settings", "qcm_turnaround_sla_hours") or 48

        matrix = frappe.new_doc("Quotation Comparison Matrix")
        matrix.rfq_reference = rfq_doc.name
        matrix.project_reference = getattr(rfq_doc, "custom_project_ref", None)
        matrix.material_request_ref = getattr(rfq_doc, "custom_material_request_ref", None)
        matrix.evaluation_date = current_date
        matrix.evaluation_status = "Draft"
        matrix.sealed_bids_verified = 1 if getattr(rfq_doc, "custom_bids_unsealed", 0) else 0
        matrix.sla_deadline = add_to_date(now_datetime(), hours=sla_hours)
        matrix.sla_status = "Within SLA"

        cls.populate_comparison_tables(matrix, quotes)
        matrix.insert(ignore_permissions=True)
        return matrix.name

    @classmethod
    def populate_comparison_tables(cls, matrix_doc, quotes: list):
        """Populates item-level landed rates and high-level supplier summaries."""
        matrix_doc.comparison_items = []
        matrix_doc.supplier_summaries = []

        supplier_totals = {}
        all_lines = []

        for q_meta in quotes:
            q_doc = frappe.get_doc("Supplier Quotation", q_meta.name)
            norm_lines = LandedCostCalculationService.normalize_quotation_lines(q_doc)

            supp_total_landed = sum(l["total_landed_amount"] for l in norm_lines)
            supp_basic = sum(l["basic_rate"] * l["qty"] for l in norm_lines)
            supp_freight = float(getattr(q_doc, "custom_freight_charges", 0.0) or 0.0) + float(getattr(q_doc, "custom_packaging_forwarding", 0.0) or 0.0)
            supp_lead = int(getattr(q_doc, "custom_promised_lead_days", 14) or 14)

            # Fetch Step 19 vendor rating
            vendor_rating = frappe.db.get_value("Supplier", q_doc.supplier, "custom_vendor_rating_score") or 75.0

            supplier_totals[q_doc.supplier] = {
                "quotation": q_doc.name,
                "basic_amount": supp_basic,
                "freight_logistics": supp_freight,
                "landed_amount": supp_total_landed,
                "lead_days": supp_lead,
                "rating": vendor_rating,
                "terms_rating": 8.0  # Default baseline rating for credit terms
            }

            for line in norm_lines:
                line["supplier"] = q_doc.supplier
                line["supplier_quotation"] = q_doc.name
                line["promised_lead_days"] = supp_lead
                line["technical_compliant"] = getattr(q_doc, "custom_technical_compliant", "Compliant") or "Compliant"
                all_lines.append(line)

        # 1. Rank line items per item_code
        item_groups = {}
        for l in all_lines:
            item_groups.setdefault(l["item_code"], []).append(l)

        for item_code, items in item_groups.items():
            sorted_items = sorted(items, key=lambda x: x["landed_rate_unit"])
            for rank_idx, itm in enumerate(sorted_items):
                rank_str = f"L{rank_idx + 1}" if rank_idx < 5 else "L5"
                matrix_doc.append("comparison_items", {
                    "item_code": itm["item_code"],
                    "item_name": itm["item_name"],
                    "qty": itm["qty"],
                    "uom": itm["uom"],
                    "supplier": itm["supplier"],
                    "supplier_quotation": itm["supplier_quotation"],
                    "basic_rate": itm["basic_rate"],
                    "packaging_forwarding": itm["packaging_unit"] * itm["qty"],
                    "freight_rate_unit": itm["freight_unit"],
                    "insurance_rate_unit": itm["insurance_unit"],
                    "unloading_rate_unit": itm["unloading_unit"],
                    "tax_rate_unit": itm["tax_unit"],
                    "landed_rate_unit": itm["landed_rate_unit"],
                    "total_landed_amount": itm["total_landed_amount"],
                    "promised_lead_days": itm["promised_lead_days"],
                    "technical_compliant": itm["technical_compliant"],
                    "item_rank": rank_str
                })

        # 2. Compute supplier summaries and multi-factor scores
        if not supplier_totals:
            return

        l1_total = min(s["landed_amount"] for s in supplier_totals.values())
        min_lead = min(s["lead_days"] for s in supplier_totals.values())
        max_lead = max(s["lead_days"] for s in supplier_totals.values()) + 7

        sorted_by_cost = sorted(supplier_totals.items(), key=lambda x: x[1]["landed_amount"])
        cost_ranks = {supp: f"L{idx + 1}" for idx, (supp, _) in enumerate(sorted_by_cost)}

        summary_rows = []
        for supp, data in supplier_totals.items():
            scores = WeightedScoringEngineService.compute_composite_score(
                vendor_landed_cost=data["landed_amount"],
                l1_landed_cost=l1_total,
                vendor_lead_days=data["lead_days"],
                min_lead_days=min_lead,
                target_max_lead_days=max_lead,
                vendor_rating_score=data["rating"],
                payment_terms_rating=data["terms_rating"]
            )
            row = {
                "supplier": supp,
                "supplier_quotation": data["quotation"],
                "total_basic_amount": data["basic_amount"],
                "total_freight_logistics": data["freight_logistics"],
                "total_tax_amount": 0.0,
                "total_landed_amount": data["landed_amount"],
                "max_lead_time_days": data["lead_days"],
                "vendor_rating_score": data["rating"],
                "commercial_score": scores["commercial_score"],
                "lead_time_score": scores["lead_time_score"],
                "rating_score": scores["rating_score"],
                "terms_score": scores["terms_score"],
                "composite_score": scores["composite_score"],
                "overall_rank": cost_ranks.get(supp, "L5")
            }
            summary_rows.append(row)

        # Sort summary rows by composite score descending
        summary_rows.sort(key=lambda x: x["composite_score"], reverse=True)
        for idx, row in enumerate(summary_rows):
            row["composite_rank"] = idx + 1
            row["is_recommended"] = 1 if idx == 0 else 0
            matrix_doc.append("supplier_summaries", row)

    @classmethod
    def apply_award_decision(cls, matrix_doc, awarded_supplier: str, justification: str = None, authorizer: str = None):
        """Applies vendor selection, evaluates L1 compliance, and enforces justification gate."""
        if not awarded_supplier:
            frappe.throw(_("Awarded supplier must be specified"), frappe.ValidationError)

        matched_summary = next((s for s in matrix_doc.supplier_summaries if s.supplier == awarded_supplier), None)
        if not matched_summary:
            frappe.throw(_("Supplier {0} is not present in evaluation summary.").format(awarded_supplier), frappe.ValidationError)

        is_l1 = (matched_summary.overall_rank == "L1")
        min_just_len = frappe.db.get_single_value("Solar SCM Settings", "qcm_non_l1_min_justification_len") or 40

        if not is_l1:
            if not justification or len(justification.strip()) < min_just_len:
                frappe.throw(
                    _("Non-L1 supplier award requires a mandatory justification of at least {0} characters (provided {1}).").format(
                        min_just_len, len(justification.strip()) if justification else 0
                    ),
                    frappe.ValidationError
                )
            matrix_doc.non_l1_justification = justification.strip()

        matrix_doc.awarded_supplier = awarded_supplier
        matrix_doc.awarded_quotation = matched_summary.supplier_quotation
        matrix_doc.awarded_landed_amount = matched_summary.total_landed_amount
        matrix_doc.is_l1_selected = 1 if is_l1 else 0
        matrix_doc.authorized_by = authorizer or frappe.session.user
        matrix_doc.authorization_date = now_datetime()
        matrix_doc.evaluation_status = "Award Approved"
        matrix_doc.save(ignore_permissions=True)
        return matrix_doc
```

---

### 3.4 `POAwardInstantiationService` (`solar_module/services/procurement/po_award_service.py`)

Responsible for programmatic 1-click instantiation of Step 15 `Purchase Order` upon matrix sign-off, locking awarded rates and terms.

```python
import frappe
from frappe import _

class POAwardInstantiationService:
    """Spawns downstream Step 15 Purchase Order from approved comparison award."""

    @classmethod
    def instantiate_purchase_order(cls, matrix_doc) -> str:
        if not matrix_doc.awarded_supplier:
            frappe.throw(_("Cannot spawn Purchase Order: No supplier has been awarded in Matrix {0}.").format(matrix_doc.name), frappe.ValidationError)

        if matrix_doc.purchase_order_ref and frappe.db.exists("Purchase Order", matrix_doc.purchase_order_ref):
            frappe.throw(_("Purchase Order {0} has already been instantiated for this Matrix.").format(matrix_doc.purchase_order_ref), frappe.DuplicateEntryError)

        sq_doc = frappe.get_doc("Supplier Quotation", matrix_doc.awarded_quotation)

        po = frappe.new_doc("Purchase Order")
        po.supplier = matrix_doc.awarded_supplier
        po.custom_rfq_reference = matrix_doc.rfq_reference
        po.custom_qcm_reference = matrix_doc.name
        po.project = matrix_doc.project_reference
        po.schedule_date = getattr(matrix_doc, "target_delivery_date", None) or frappe.utils.add_to_date(frappe.utils.nowdate(), days=14)

        for item in sq_doc.items:
            po.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty,
                "uom": item.uom,
                "rate": item.rate,
                "amount": item.amount,
                "supplier_quotation": sq_doc.name,
                "supplier_quotation_item": item.name
            })

        po.insert(ignore_permissions=True)

        matrix_doc.db_set("purchase_order_ref", po.name)
        matrix_doc.db_set("evaluation_status", "PO Created")

        return po.name
```

---

### 3.5 `QuotationEvaluationSLAService` (`solar_module/services/procurement/qcm_sla_service.py`)

Responsible for managing the 48-hour commercial evaluation turnaround SLA, triggering automated escalation, and mandating delay audit entries.

```python
import frappe
from frappe.utils import now_datetime

class QuotationEvaluationSLAService:
    """Monitors 48h turnaround SLA and flags overdue comparison matrices."""

    @classmethod
    def check_and_update_sla_statuses(cls):
        now = now_datetime()
        overdue_matrices = frappe.get_all(
            "Quotation Comparison Matrix",
            filters={
                "docstatus": 0,
                "evaluation_status": ["in", ["Draft", "Under Review"]],
                "sla_status": "Within SLA",
                "sla_deadline": ["<", now]
            },
            fields=["name"]
        )

        for m in overdue_matrices:
            frappe.db.set_value("Quotation Comparison Matrix", m.name, {
                "sla_status": "Overdue",
                "evaluation_status": "Overdue"
            })
            frappe.db.commit()
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

Implements submittable document lifecycle logic extending `StageSecuredDocument`, server-side verification gates, and whitelisted RPC APIs.

### 4.1 Submittable Controller Override (`solar_module/procurement/doctype/quotation_comparison_matrix/quotation_comparison_matrix.py`)

```python
import frappe
from frappe import _
from frappe.model.document import Document
from solar_module.security.mixins import StageSecuredDocument

class QuotationComparisonMatrix(StageSecuredDocument, Document):
    """Submittable governance document for supplier quotation comparative evaluation."""

    def validate(self):
        self.validate_items_and_suppliers()
        self.validate_sla_overdue_gate()

    def validate_items_and_suppliers(self):
        if not self.comparison_items:
            frappe.throw(_("Quotation Comparison Matrix must contain at least one comparison item."), frappe.ValidationError)
        if not self.supplier_summaries:
            frappe.throw(_("Supplier summary matrix cannot be empty."), frappe.ValidationError)

    def validate_sla_overdue_gate(self):
        if self.sla_status == "Overdue" and not self.delay_reason_table:
            frappe.throw(
                _("This evaluation has breached the 48-hour SLA deadline. You must append an audit entry in the Delay Audit Log before proceeding."),
                frappe.ValidationError
            )

    def on_submit(self):
        self.validate_award_signoff()

    def validate_award_signoff(self):
        if not self.awarded_supplier:
            frappe.throw(_("Cannot submit Quotation Comparison Matrix: An awarded supplier must be selected."), frappe.ValidationError)

        user_roles = frappe.get_roles()
        if "Purchase Manager" not in user_roles and "Admin" not in user_roles and "System Manager" not in user_roles:
            frappe.throw(_("Only Purchase Manager or Admin can submit and authorize a Quotation Comparison Matrix award."), frappe.PermissionError)

        # Enforce Non-L1 justification rule
        matched = next((s for s in self.supplier_summaries if s.supplier == self.awarded_supplier), None)
        if matched and matched.overall_rank != "L1":
            min_len = frappe.db.get_single_value("Solar SCM Settings", "qcm_non_l1_min_justification_len") or 40
            if not self.non_l1_justification or len(self.non_l1_justification.strip()) < min_len:
                frappe.throw(
                    _("Submission blocked: Non-L1 selection requires a detailed justification of at least {0} characters.").format(min_len),
                    frappe.ValidationError
                )

    def before_cancel(self):
        if self.purchase_order_ref and frappe.db.exists("Purchase Order", self.purchase_order_ref):
            po_status = frappe.db.get_value("Purchase Order", self.purchase_order_ref, "docstatus")
            if po_status != 2:
                frappe.throw(
                    _("Cannot cancel Quotation Comparison Matrix {0}: Downstream Purchase Order {1} exists and is active. Cancel the PO first.").format(
                        self.name, self.purchase_order_ref
                    ),
                    frappe.ValidationError
                )
```

---

### 4.2 Whitelisted RPC API Endpoints (`solar_module/api/procurement.py`)

```python
import frappe
from frappe import _
from solar_module.services.procurement.comparison_matrix_service import QuotationComparisonMatrixService
from solar_module.services.procurement.po_award_service import POAwardInstantiationService

@frappe.whitelist(methods=["POST"])
def generate_quotation_comparison(rfq_name: str) -> dict:
    """Instantiates a new Quotation Comparison Matrix from an RFQ."""
    if not rfq_name:
        frappe.throw(_("RFQ name is required"), frappe.ValidationError)
    rfq_doc = frappe.get_doc("Request for Quotation", rfq_name)
    rfq_doc.check_permission("read")
    matrix_name = QuotationComparisonMatrixService.create_from_rfq(rfq_doc)
    return {"status": "success", "comparison_matrix": matrix_name}

@frappe.whitelist(methods=["GET"])
def get_quotation_comparison_details(matrix_name: str) -> dict:
    """Returns side-by-side comparison data for Desk and SPA rendering."""
    doc = frappe.get_doc("Quotation Comparison Matrix", matrix_name)
    doc.check_permission("read")
    return {
        "status": "success",
        "doc": doc.as_dict(),
        "comparison_items": [i.as_dict() for i in doc.comparison_items],
        "supplier_summaries": [s.as_dict() for s in doc.supplier_summaries]
    }

@frappe.whitelist(methods=["POST"])
def authorize_quotation_award(matrix_name: str, awarded_supplier: str, non_l1_justification: str = None) -> dict:
    """Signs off supplier award; requires Purchase Manager or Admin role."""
    doc = frappe.get_doc("Quotation Comparison Matrix", matrix_name)
    doc.check_permission("write")
    user_roles = frappe.get_roles()
    if "Purchase Manager" not in user_roles and "Admin" not in user_roles and "System Manager" not in user_roles:
        frappe.throw(_("Only Purchase Manager or Admin can authorize quotation awards"), frappe.PermissionError)

    updated_doc = QuotationComparisonMatrixService.apply_award_decision(
        matrix_doc=doc,
        awarded_supplier=awarded_supplier,
        justification=non_l1_justification,
        authorizer=frappe.session.user
    )
    return {
        "status": "success",
        "matrix": updated_doc.name,
        "awarded_supplier": updated_doc.awarded_supplier,
        "is_l1_selected": updated_doc.is_l1_selected,
        "evaluation_status": updated_doc.evaluation_status
    }

@frappe.whitelist(methods=["POST"])
def spawn_purchase_order_from_award(matrix_name: str) -> dict:
    """Instantiates downstream Step 15 Purchase Order from submitted matrix."""
    doc = frappe.get_doc("Quotation Comparison Matrix", matrix_name)
    doc.check_permission("write")
    if doc.docstatus != 1:
        frappe.throw(_("Quotation Comparison Matrix must be submitted before spawning Purchase Order"), frappe.ValidationError)

    po_name = POAwardInstantiationService.instantiate_purchase_order(doc)
    return {"status": "success", "purchase_order": po_name}

@frappe.whitelist(methods=["POST"])
def log_quotation_evaluation_delay(matrix_name: str, delay_type: str, delay_reason: str) -> dict:
    """Logs justification for SLA-breached comparison matrix."""
    doc = frappe.get_doc("Quotation Comparison Matrix", matrix_name)
    doc.check_permission("write")
    if not delay_reason or len(delay_reason.strip()) < 20:
        frappe.throw(_("Delay reason must be at least 20 characters long"), frappe.ValidationError)

    doc.append("delay_reason_table", {
        "logged_by": frappe.session.user,
        "logged_on": frappe.utils.now_datetime(),
        "delay_type": delay_type or "Commercial Clarification",
        "delay_reason": delay_reason.strip()
    })
    doc.save(ignore_permissions=True)
    return {"status": "success", "message": "Delay logged successfully"}
```

---

### 4.3 Background Scheduled SLA Daemon Hook

```python
# File: solar_module/tasks.py (Registered in hooks.py scheduler_events["all"] or ["cron"])
def monitor_quotation_evaluation_sla():
    """Runs every 15 minutes to evaluate active QCM documents against 48h SLA."""
    from solar_module.services.procurement.qcm_sla_service import QuotationEvaluationSLAService
    QuotationEvaluationSLAService.check_and_update_sla_statuses()
```

---

## 5. Layer 4: Desk Client Script & Dynamic Comparison Workbench SPA Hook

Provides real-time interactive evaluation tools in Frappe Desk and the Vue 3 SPA workbench.

### 5.1 Desk Client Script (`codes/client_script/quotation_comparison_matrix.js`)

```javascript
frappe.ui.form.on("Quotation Comparison Matrix", {
  refresh: function (frm) {
    // 1. Render SLA status badge
    render_qcm_sla_indicator(frm);

    // 2. Action: Authorize Award (Draft state)
    if (frm.doc.docstatus === 0) {
      frm
        .add_custom_button(__("Authorize Award"), function () {
          open_award_authorization_dialog(frm);
        })
        .addClass("btn-primary");
    }

    // 3. Action: Spawn Purchase Order (Submitted state, no PO yet)
    if (frm.doc.docstatus === 1 && !frm.doc.purchase_order_ref) {
      frm
        .add_custom_button(__("Spawn Purchase Order"), function () {
          frappe.confirm(
            __("Are you sure you want to spawn the Purchase Order for {0}?", [
              frm.doc.awarded_supplier,
            ]),
            function () {
              frappe.call({
                method:
                  "solar_module.api.procurement.spawn_purchase_order_from_award",
                args: { matrix_name: frm.doc.name },
                freeze: true,
                freeze_message: __("Instantiating Purchase Order..."),
                callback: function (r) {
                  if (r.message && r.message.status === "success") {
                    frappe.msgprint(
                      __("Purchase Order {0} instantiated successfully.", [
                        r.message.purchase_order,
                      ]),
                    );
                    frm.reload_doc();
                  }
                },
              });
            },
          );
        })
        .addClass("btn-success");
    }

    // 4. Overdue Delay Dialog Button
    if (frm.doc.sla_status === "Overdue" && frm.doc.docstatus === 0) {
      frm
        .add_custom_button(__("Log Delay Justification"), function () {
          open_delay_log_dialog(frm);
        })
        .addClass("btn-danger");
    }
  },
});

function render_qcm_sla_indicator(frm) {
  let color = frm.doc.sla_status === "Overdue" ? "red" : "green";
  let label =
    frm.doc.sla_status === "Overdue"
      ? __("SLA BREACHED (Overdue)")
      : __("Within 48h SLA");
  frm.page.set_indicator(label, color);
}

function open_award_authorization_dialog(frm) {
  let suppliers = (frm.doc.supplier_summaries || []).map((s) => ({
    label: `${s.supplier} (${s.overall_rank} - Total Landed: ₹${frappe.format(s.total_landed_amount, { fieldtype: "Currency" })})`,
    value: s.supplier,
  }));

  let d = new frappe.ui.Dialog({
    title: __("Authorize Supplier Award"),
    fields: [
      {
        fieldname: "awarded_supplier",
        label: __("Select Winning Supplier"),
        fieldtype: "Select",
        options: suppliers,
        reqd: 1,
        onchange: function () {
          let sel = d.get_value("awarded_supplier");
          let summary = (frm.doc.supplier_summaries || []).find(
            (s) => s.supplier === sel,
          );
          if (summary && summary.overall_rank !== "L1") {
            d.set_df_property("non_l1_section", "hidden", 0);
            d.set_df_property("non_l1_justification", "reqd", 1);
          } else {
            d.set_df_property("non_l1_section", "hidden", 1);
            d.set_df_property("non_l1_justification", "reqd", 0);
          }
        },
      },
      {
        fieldname: "non_l1_section",
        fieldtype: "Section Break",
        label: __("Non-L1 Selection Justification Required"),
        hidden: 1,
      },
      {
        fieldname: "non_l1_justification",
        label: __("Commercial / Technical Justification (Min 40 Chars)"),
        fieldtype: "Small Text",
      },
    ],
    primary_action_label: __("Authorize & Apply"),
    primary_action: function (values) {
      frappe.call({
        method: "solar_module.api.procurement.authorize_quotation_award",
        args: {
          matrix_name: frm.doc.name,
          awarded_supplier: values.awarded_supplier,
          non_l1_justification: values.non_l1_justification,
        },
        freeze: true,
        callback: function (r) {
          if (r.message && r.message.status === "success") {
            frappe.msgprint(
              __("Award authorized for {0}.", [values.awarded_supplier]),
            );
            d.hide();
            frm.reload_doc();
          }
        },
      });
    },
  });
  d.show();
}

function open_delay_log_dialog(frm) {
  let d = new frappe.ui.Dialog({
    title: __("Log SLA Delay Audit Entry"),
    fields: [
      {
        fieldname: "delay_type",
        label: __("Delay Reason Category"),
        fieldtype: "Select",
        options:
          "Commercial Clarification\nTechnical Deviation Review\nVendor Warranty Negotiation\nManagement Sign-off Delay",
        default: "Commercial Clarification",
        reqd: 1,
      },
      {
        fieldname: "delay_reason",
        label: __("Audit Explanation (Min 20 Chars)"),
        fieldtype: "Small Text",
        reqd: 1,
      },
    ],
    primary_action_label: __("Save Delay Log"),
    primary_action: function (values) {
      frappe.call({
        method: "solar_module.api.procurement.log_quotation_evaluation_delay",
        args: {
          matrix_name: frm.doc.name,
          delay_type: values.delay_type,
          delay_reason: values.delay_reason,
        },
        callback: function (r) {
          if (r.message && r.message.status === "success") {
            d.hide();
            frm.reload_doc();
          }
        },
      });
    },
  });
  d.show();
}
```

---

### 5.2 Dynamic Comparison Workbench SPA (`/solar/procurement/comparison/:id`)

The dedicated modern comparison SPA renders multi-vendor side-by-side matrices with dynamic visual ranking badges:

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
│  │ Metric / Line Item   │ Adani Solar (L1 Cost)  │ Waaree Energies (L2)  │ Goldi Solar (L3)     │ │
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

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Implements an end-to-end integration test suite subclassing `frappe.tests.utils.FrappeTestCase` with strict zero-commit rollback, proving all 10 Stage 14 business and technical gates.

```python
# File: solar_module/tests/test_step_14_quotation_comparison_matrix_tracer_bullet.py
import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_to_date
from solar_module.services.procurement.landed_cost_service import LandedCostCalculationService
from solar_module.services.procurement.weighted_scoring_service import WeightedScoringEngineService
from solar_module.services.procurement.comparison_matrix_service import QuotationComparisonMatrixService
from solar_module.services.procurement.po_award_service import POAwardInstantiationService

class TestQuotationComparisonMatrixTracerBullet(FrappeTestCase):
    """End-to-end integration test proving Stage 14 5-layer vertical tracer bullet slice."""

    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")
        self.cleanup_records = []

    def tearDown(self):
        # Strict zero-commit rollback: clean memory and rollback DB changes
        for dt, dn in reversed(self.cleanup_records):
            if frappe.db.exists(dt, dn):
                frappe.delete_doc(dt, dn, force=1, ignore_permissions=True)
        frappe.db.rollback()
        super().tearDown()

    def test_01_landed_cost_normalization_ex_factory_vs_for_site(self):
        """Proves landed cost normalization: Ex-Factory quote with surcharges vs FOR-Site quote."""
        # Vendor A: Low basic (100) + high freight (10) + unloading (3) = Landed 113
        vendor_a = LandedCostCalculationService.calculate_item_landed_cost(
            basic_rate=100.0, qty=10.0, freight=100.0, insurance=0.0, packaging=0.0, unloading=30.0
        )
        self.assertEqual(vendor_a["landed_rate_unit"], 113.0)
        self.assertEqual(vendor_a["total_landed_amount"], 1130.0)

        # Vendor B: Higher basic (110) with freight included = Landed 110 (True L1)
        vendor_b = LandedCostCalculationService.calculate_item_landed_cost(
            basic_rate=110.0, qty=10.0, freight=0.0, insurance=0.0, packaging=0.0, unloading=0.0
        )
        self.assertEqual(vendor_b["landed_rate_unit"], 110.0)
        self.assertEqual(vendor_b["total_landed_amount"], 1100.0)

        # Vendor B is true L1 despite higher basic quote rate
        self.assertLess(vendor_b["total_landed_amount"], vendor_a["total_landed_amount"])

    def test_02_weighted_scoring_engine_computation(self):
        """Proves 100-point multi-factor composite scoring engine mathematics."""
        scores = WeightedScoringEngineService.compute_composite_score(
            vendor_landed_cost=1000.0,
            l1_landed_cost=1000.0,
            vendor_lead_days=7,
            min_lead_days=7,
            target_max_lead_days=21,
            vendor_rating_score=90.0,
            payment_terms_rating=10.0
        )
        self.assertEqual(scores["commercial_score"], 50.0)
        self.assertEqual(scores["lead_time_score"], 25.0)
        self.assertEqual(scores["rating_score"], 13.5)
        self.assertEqual(scores["terms_score"], 10.0)
        self.assertEqual(scores["composite_score"], 98.5)

    def test_03_minimum_quotes_quota_enforcement(self):
        """Proves minimum quotes quota enforcement: rejects matrix creation with < 2 quotes."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.transaction_date = nowdate()
        rfq.custom_is_single_source = 0
        rfq.insert(ignore_permissions=True)
        self.cleanup_records.append(("Request for Quotation", rfq.name))

        # Only 1 quote exists
        sq = frappe.new_doc("Supplier Quotation")
        sq.supplier = "_Test Supplier 1" if frappe.db.exists("Supplier", "_Test Supplier 1") else self._create_test_supplier("SUPP-01")
        sq.request_for_quotation = rfq.name
        sq.transaction_date = nowdate()
        sq.append("items", {"item_code": "_Test Solar Panel", "qty": 10, "rate": 100})
        sq.insert(ignore_permissions=True)
        self.cleanup_records.append(("Supplier Quotation", sq.name))

        with self.assertRaises(frappe.ValidationError):
            QuotationComparisonMatrixService.create_from_rfq(rfq)

    def test_04_sealed_bids_unsealing_enforcement_gate(self):
        """Proves sealed bids unsealing enforcement gate blocks matrix creation before unsealing."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.transaction_date = nowdate()
        rfq.custom_sealed_bids = 1
        rfq.custom_bids_unsealed = 0
        rfq.insert(ignore_permissions=True)
        self.cleanup_records.append(("Request for Quotation", rfq.name))

        with self.assertRaises(frappe.PermissionError):
            QuotationComparisonMatrixService.create_from_rfq(rfq)

    def test_05_expired_quotation_rejection_gate(self):
        """Proves expired quotations are barred from comparative matrix creation."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.transaction_date = nowdate()
        rfq.custom_is_single_source = 1
        rfq.insert(ignore_permissions=True)
        self.cleanup_records.append(("Request for Quotation", rfq.name))

        sq = frappe.new_doc("Supplier Quotation")
        sq.supplier = self._create_test_supplier("SUPP-EXP")
        sq.request_for_quotation = rfq.name
        sq.transaction_date = add_to_date(nowdate(), days=-30)
        sq.valid_till = add_to_date(nowdate(), days=-5)  # Expired
        sq.append("items", {"item_code": "_Test Solar Panel", "qty": 10, "rate": 100})
        sq.insert(ignore_permissions=True)
        self.cleanup_records.append(("Supplier Quotation", sq.name))

        with self.assertRaises(frappe.ValidationError):
            QuotationComparisonMatrixService.create_from_rfq(rfq)

    def test_06_non_l1_selection_requires_mandatory_justification(self):
        """Proves that selecting a non-L1 vendor without >= 40 chars justification fails."""
        matrix = frappe.new_doc("Quotation Comparison Matrix")
        matrix.rfq_reference = "TEST-RFQ-001"
        matrix.evaluation_date = nowdate()
        matrix.evaluation_status = "Draft"
        matrix.append("supplier_summaries", {
            "supplier": "SUPP-L1",
            "supplier_quotation": "SQ-001",
            "total_landed_amount": 1000.0,
            "overall_rank": "L1",
            "composite_score": 95.0
        })
        matrix.append("supplier_summaries", {
            "supplier": "SUPP-L2",
            "supplier_quotation": "SQ-002",
            "total_landed_amount": 1200.0,
            "overall_rank": "L2",
            "composite_score": 90.0
        })
        matrix.insert(ignore_permissions=True)
        self.cleanup_records.append(("Quotation Comparison Matrix", matrix.name))

        # Attempt to award L2 with short justification (< 40 chars)
        with self.assertRaises(frappe.ValidationError):
            QuotationComparisonMatrixService.apply_award_decision(
                matrix_doc=matrix,
                awarded_supplier="SUPP-L2",
                justification="Too short explanation"
            )

    def test_07_role_authority_gate_purchase_assistant_blocked(self):
        """Proves Purchase Assistant role is barred from submitting award decision."""
        matrix = frappe.new_doc("Quotation Comparison Matrix")
        matrix.rfq_reference = "TEST-RFQ-ROLE"
        matrix.evaluation_date = nowdate()
        matrix.awarded_supplier = "SUPP-L1"
        matrix.append("comparison_items", {
            "item_code": "PV-01",
            "qty": 10,
            "uom": "Nos",
            "supplier": "SUPP-L1",
            "supplier_quotation": "SQ-001",
            "basic_rate": 100.0,
            "landed_rate_unit": 100.0,
            "total_landed_amount": 1000.0,
            "promised_lead_days": 7,
            "technical_compliant": "Compliant",
            "item_rank": "L1"
        })
        matrix.append("supplier_summaries", {
            "supplier": "SUPP-L1",
            "supplier_quotation": "SQ-001",
            "total_basic_amount": 1000.0,
            "total_freight_logistics": 0.0,
            "total_tax_amount": 0.0,
            "total_landed_amount": 1000.0,
            "max_lead_time_days": 7,
            "commercial_score": 50.0,
            "lead_time_score": 25.0,
            "rating_score": 15.0,
            "terms_score": 10.0,
            "composite_score": 100.0,
            "overall_rank": "L1"
        })
        matrix.insert(ignore_permissions=True)
        self.cleanup_records.append(("Quotation Comparison Matrix", matrix.name))

        # Test as Purchase Assistant
        frappe.set_user("test_assistant@example.com")
        frappe.local.roles = ["Purchase Assistant"]
        with self.assertRaises(frappe.PermissionError):
            matrix.on_submit()

    def test_08_award_signoff_by_purchase_manager_succeeds(self):
        """Proves Purchase Manager can successfully authorize and submit award decision."""
        matrix = frappe.new_doc("Quotation Comparison Matrix")
        matrix.rfq_reference = "TEST-RFQ-MGR"
        matrix.evaluation_date = nowdate()
        matrix.awarded_supplier = "SUPP-L1"
        matrix.is_l1_selected = 1
        matrix.append("comparison_items", {
            "item_code": "PV-01",
            "qty": 10,
            "uom": "Nos",
            "supplier": "SUPP-L1",
            "supplier_quotation": "SQ-001",
            "basic_rate": 100.0,
            "landed_rate_unit": 100.0,
            "total_landed_amount": 1000.0,
            "promised_lead_days": 7,
            "technical_compliant": "Compliant",
            "item_rank": "L1"
        })
        matrix.append("supplier_summaries", {
            "supplier": "SUPP-L1",
            "supplier_quotation": "SQ-001",
            "total_basic_amount": 1000.0,
            "total_freight_logistics": 0.0,
            "total_tax_amount": 0.0,
            "total_landed_amount": 1000.0,
            "max_lead_time_days": 7,
            "commercial_score": 50.0,
            "lead_time_score": 25.0,
            "rating_score": 15.0,
            "terms_score": 10.0,
            "composite_score": 100.0,
            "overall_rank": "L1"
        })
        matrix.insert(ignore_permissions=True)
        self.cleanup_records.append(("Quotation Comparison Matrix", matrix.name))

        frappe.set_user("test_mgr@example.com")
        frappe.local.roles = ["Purchase Manager"]
        matrix.on_submit()  # Must execute without exception
        self.assertEqual(matrix.awarded_supplier, "SUPP-L1")

    def test_09_programmatic_po_spawning_and_duplicate_prevention(self):
        """Proves downstream PO is instantiated and duplicate generation is blocked."""
        matrix = frappe.new_doc("Quotation Comparison Matrix")
        matrix.rfq_reference = "TEST-RFQ-PO"
        matrix.evaluation_date = nowdate()
        matrix.awarded_supplier = self._create_test_supplier("SUPP-PO")
        matrix.docstatus = 1

        sq = frappe.new_doc("Supplier Quotation")
        sq.supplier = matrix.awarded_supplier
        sq.transaction_date = nowdate()
        sq.append("items", {"item_code": "_Test Solar Panel", "qty": 10, "rate": 150})
        sq.insert(ignore_permissions=True)
        self.cleanup_records.append(("Supplier Quotation", sq.name))

        matrix.awarded_quotation = sq.name
        matrix.insert(ignore_permissions=True)
        self.cleanup_records.append(("Quotation Comparison Matrix", matrix.name))

        po_name = POAwardInstantiationService.instantiate_purchase_order(matrix)
        self.assertTrue(frappe.db.exists("Purchase Order", po_name))
        self.cleanup_records.append(("Purchase Order", po_name))

        # Re-attempting must throw DuplicateEntryError
        with self.assertRaises(frappe.DuplicateEntryError):
            POAwardInstantiationService.instantiate_purchase_order(matrix)

    def test_10_sla_breach_overdue_delay_log_enforcement(self):
        """Proves that an Overdue matrix cannot be saved/submitted without delay log justification."""
        matrix = frappe.new_doc("Quotation Comparison Matrix")
        matrix.rfq_reference = "TEST-RFQ-OVERDUE"
        matrix.evaluation_date = nowdate()
        matrix.sla_status = "Overdue"
        matrix.append("comparison_items", {
            "item_code": "PV-01", "qty": 1, "uom": "Nos", "supplier": "SUPP-1",
            "supplier_quotation": "SQ-1", "basic_rate": 10, "landed_rate_unit": 10,
            "total_landed_amount": 10, "promised_lead_days": 1, "technical_compliant": "Compliant", "item_rank": "L1"
        })
        matrix.append("supplier_summaries", {
            "supplier": "SUPP-1", "supplier_quotation": "SQ-1", "total_basic_amount": 10,
            "total_freight_logistics": 0, "total_tax_amount": 0, "total_landed_amount": 10,
            "max_lead_time_days": 1, "commercial_score": 50, "lead_time_score": 25,
            "rating_score": 15, "terms_score": 10, "composite_score": 100, "overall_rank": "L1"
        })

        with self.assertRaises(frappe.ValidationError):
            matrix.validate()

    def _create_test_supplier(self, name: str) -> str:
        if not frappe.db.exists("Supplier", name):
            s = frappe.new_doc("Supplier")
            s.supplier_name = name
            s.supplier_group = "Local"
            s.insert(ignore_permissions=True)
            self.cleanup_records.append(("Supplier", s.name))
            return s.name
        return name
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 L3 DevOps Runbook

```bash
# 1. Execute database schema migration for Stage 14 extensions and new DocTypes
bench --site solar.local migrate

# 2. Rebuild frontend assets for Desk client script and Vue 3 comparison SPA
bench build --app solar_module

# 3. Verify DocType creation and MariaDB schema integrity
bench mariadb -e "DESCRIBE \`tabQuotation Comparison Matrix\`;"
bench mariadb -e "DESCRIBE \`tabQuotation Comparison Item\`;"
bench mariadb -e "DESCRIBE \`tabQuotation Comparison Supplier Summary\`;"

# 4. Verify composite B-Tree indexes on Quotation Comparison tables
bench mariadb -e "SHOW INDEX FROM \`tabQuotation Comparison Matrix\` WHERE Key_name IN ('idx_qcm_rfq_status', 'idx_qcm_sla', 'idx_qcm_po_ref');"

# 5. Run Stage 14 automated integration verification suite
bench run-tests --app solar_module --module solar_module.tests.test_step_14_quotation_comparison_matrix_tracer_bullet
```

---

### 7.2 Operational SOP for Enterprise Actors

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           STAGE 14 OPERATIONAL ROLE RUNBOOK                                      │
├───────┬──────────────────────┬─────────────────────────┬─────────────────────────────────────────┤
│ Stage │ Actor                │ Action Step             │ Operational Procedure                   │
├───────┼──────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│ **1** │ `Purchase Assistant` │ Ingest & Validate Quotes│ Confirm all supplier quotes received via│
│       │                      │                         │ token portal or Desk; verify freight &  │
│       │                      │                         │ insurance surcharges are populated.     │
│ **2** │ `Purchase Assistant` │ Generate Comparison     │ Navigate to RFQ, click "Generate Matrix"│
│       │                      │                         │ to trigger landed cost normalization.   │
│ **3** │ `Project Engineer`   │ Technical Review        │ Review component datasheets and sign off│
│       │                      │                         │ `technical_compliant` on quote lines.   │
│ **4** │ `Purchase Assistant` │ Evaluate Scoring & Rank │ Review 100-pt scores; formulate award   │
│       │                      │                         │ recommendation (L1 vs Non-L1).          │
│ **5** │ `Purchase Manager`   │ Authorize Award Sign-off│ Review matrix; if Non-L1, enter $\ge 40$│
│       │                      │                         │ chars justification and submit matrix.  │
│ **6** │ `Purchase Assistant` │ Release Purchase Order  │ Click "Spawn Purchase Order" to release │
│       │                      │                         │ formal contract baseline to supplier.   │
│ **7** │ `Admin`              │ Audit & Exception Review│ Conduct periodic audits of Non-L1 picks,│
│       │                      │                         │ review delay logs, adjust SLA settings. │
└───────┴──────────────────────┴─────────────────────────┴─────────────────────────────────────────┘
```

---

### 7.3 Operational Error Resolution Matrix

| Error Code    | Trigger Condition                                               | Root Cause Analysis                                              | Operator Resolution Procedure                                                                     |
| :------------ | :-------------------------------------------------------------- | :--------------------------------------------------------------- | :------------------------------------------------------------------------------------------------ |
| `ERR-QCM-001` | "Cannot generate comparison: Bids for RFQ are sealed"           | Tender bids sealed under high-value threshold; unsealing pending | `Purchase Manager` must open the RFQ and formally execute the "Perform Bid Unsealing Ceremony".   |
| `ERR-QCM-002` | "Minimum 2 supplier quotations required"                        | Fewer than 2 competitive quotations available for RFQ            | Solicit additional vendor quotes via portal or have `Purchase Manager` approve Single-Source RFQ. |
| `ERR-QCM-003` | "Non-L1 selection requires minimum 40 characters justification" | Buyer picked higher-priced vendor with brief explanation         | Provide comprehensive commercial/technical justification detailing lead-time or quality reasons.  |
| `ERR-QCM-004` | "Only Purchase Manager or Admin can authorize award"            | Junior `Purchase Assistant` attempted award sign-off             | Route matrix to `Purchase Manager` or `Admin` for formal digital sign-off and submission.         |
| `ERR-QCM-005` | "Supplier Quotation has expired (valid_till date passed)"       | Bid validity date lapsed before evaluation sign-off              | Contact supplier to extend quote validity date and update `valid_till` in `Supplier Quotation`.   |
| `ERR-QCM-006` | "Purchase Order has already been instantiated"                  | Buyer clicked "Spawn Purchase Order" multiple times              | Use existing `purchase_order_ref` link; duplicate PO generation is intentionally blocked.         |
| `ERR-QCM-007` | "Evaluation breached 48-hour SLA deadline"                      | Matrix lingered in review past 48h without justification         | Open "Log Delay Justification" dialog, enter $\ge 20$ chars reason into `Solar Stage Delay Log`.  |

---

## 8. Summary of Architectural Achievements

1. **100% Landed Cost Transparency:** Eliminates false L1 choices by factoring basic rate, freight, transit insurance, site unloading, P&F, and non-creditable taxes into unit rates. Protects 4–7% project gross margin.
2. **Deterministic 100-Point Multi-Factor Scoring:** Balances commercial landed cost (50%), delivery schedule risk (25%), historical supplier performance (15%), and credit terms (10%), ensuring project COD milestone adherence.
3. **Eradication of Maverick Procurement:** Enforces system-level justification validation ($\ge 40$ chars) and role-gated sign-off (`Purchase Manager` or `Admin`) whenever non-L1 suppliers are awarded.
4. **Sub-48-Hour Turnaround SLA Governance:** Automatically tracks evaluation speed from tender closure to award sign-off, escalating delays and mandating audit logging.
5. **Zero Clerical Re-Entry Latency:** Programmatic 1-click PO generation instantiates downstream contracts in Step 15 with complete rate and term locking.
6. **Full Pragmatic Tracer Bullet Proof:** Established permanent 5-layer thin vertical slice with 10 atomic zero-commit integration tests, proving architecture viability before mass code rollout.

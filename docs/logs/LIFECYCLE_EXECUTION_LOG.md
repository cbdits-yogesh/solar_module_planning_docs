# Solar EPC Enterprise ERP — Master Lifecycle Execution & Reconciliation Log

**Document ID:** `LOG-MASTER-LIFECYCLE`  
**Governing Standard:** [`AGENTS.md`](../../AGENTS.md)  
**Location:** `docs/logs/LIFECYCLE_EXECUTION_LOG.md`  
**Primary Repository Reference:** [`step_plans/README.md`](../../step_plans/README.md)  
**Decisions Reference:** [`docs/decisions/`](../decisions/)  
**Last Reconciled:** 2026-09-24  
**Status:** Canonical & Audited

---

## 1. Purpose & Architectural Governance

In strict compliance with [`AGENTS.md`](../../AGENTS.md), this document serves as the **single authoritative progress, audit, and reconciliation log** across the entire **Sadbhav Solar EPC Enterprise ERP platform** (`solar_module` / `manoj`).

It records:

1. **Reconciliation Traceability:** Direct cross-referencing between architectural decisions ([`docs/decisions/`](../decisions/)), master step specifications ([`step_plans/`](../../step_plans/)), token-optimized AI specifications ([`step_plans_for_ai/`](../../step_plans_for_ai/)), and implementation scripts ([`codes/`](../../codes/)).
2. **Readiness & Audit Verification:** Systematic verification of data dictionaries, 3NF schema designs, state machines, SLA engines, domain services, security gates, and automated test assertions.
3. **Enterprise Standards Enforcement:** 100% adherence to the **Zero "User" Suffix Rule** and the **Supreme Command (`Admin`) vs. Developer (`System Manager`) Role Separation Standard**.

---

## 2. Master Lifecycle Status Matrix (Stages 01–15)

| Stage # | Stage Name & Scope                                                      | Architectural Decision (Why)                                                              | Master Specification (What & How)                                                       | AI Optimized Spec (Token-Efficient)                                                                                                                                                                         | Legacy / Target Code Touchpoints                                                              | DocType & Service Entities                                                                                                                        |  Documentation Status  |
| :-----: | :---------------------------------------------------------------------- | :---------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------: |
| **01**  | **Lead Capture, Deduplication & Survey Scheduling**                     | [`ADR-001`](../decisions/ADR-001-LEAD-MANAGEMENT-DEDUPLICATION-ROUTING.md)                | [`STEP_01`](../../step_plans/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.md)                  | [`STEP_01.caveman`](../../step_plans_for_ai/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.caveman.md)<br>[`TB-01.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md) | `codes/client_script/lead.js`, `lead_listview.js`                                             | `tabLead`, `LeadValidationService`, `LeadSLAService`, `SiteSurveyBridgeService`                                                                   | **Reconciled & Ready** |
| **02**  | **Technical Site Survey & Audit (Offline Engine)**                      | [`ADR-002`](../decisions/ADR-002-TECHNICAL-SITE-SURVEY-AUDIT-OFFLINE-ENGINE.md)           | [`STEP_02`](../../step_plans/STEP_02_SITE_SURVEY_SPECIFICATION.md)                      | [`STEP_02.caveman`](../../step_plans_for_ai/STEP_02_SITE_SURVEY_SPECIFICATION.caveman.md)                                                                                                                   | `codes/client_script/site_survey.js`, `site_survey_listview.js`, `sitesurvey_to_quotation.js` | `tabSite Survey`, `tabSurvey Checklist Item`, `SurveySLAService`, `SurveySyncService`                                                             | **Reconciled & Ready** |
| **03**  | **Survey Engineering Design & Dynamic BOM Engine**                      | [`ADR-003`](../decisions/ADR-003-SURVEY-ENGINEERING-DESIGN-DYNAMIC-BOM-ENGINE.md)         | [`STEP_03`](../../step_plans/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.md)    | [`STEP_03.caveman`](../../step_plans_for_ai/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.caveman.md)                                                                                                 | `codes/client_script/so_bom_item.js`                                                          | `tabSurvey Engineering Design`, `custom_quot_bom`, `SolarEngineeringCalculationService`                                                           | **Reconciled & Ready** |
| **04**  | **Proposal & Subsidy Engine**                                           | [`ADR-004`](../decisions/ADR-004-PROPOSAL-SUBSIDY-ENGINE.md)                              | [`STEP_04`](../../step_plans/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.md)                 | [`STEP_04.caveman`](../../step_plans_for_ai/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.caveman.md)                                                                                                              | `codes/client_script/proposal_listview.js`                                                    | `tabQuotation`, 70:30 Solar GST, `SolarProposalPricingService`, `SubsidyCalculationService`                                                       | **Reconciled & Ready** |
| **05**  | **Advance Payment Clearance & Customer Master Inception**               | [`ADR-005`](../decisions/ADR-005-ADVANCE-PAYMENT-CUSTOMER-MASTER-INCEPTION.md)            | [`STEP_05`](../../step_plans/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.md)    | [`STEP_05.caveman`](../../step_plans_for_ai/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.caveman.md)                                                                                                 | `codes/client_script/account_manager.js`                                                      | `tabPayment Entry`, $\ge 20\%$ Advance Gate, `CustomerInceptionService`                                                                           | **Reconciled & Ready** |
| **06**  | **Sales Order Commercial Baseline & Downstream Spawning**               | [`ADR-006`](../decisions/ADR-006-SALES-ORDER-BASELINE-DOWNSTREAM-SPAWNING.md)             | [`STEP_06`](../../step_plans/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.md)             | [`STEP_06.caveman`](../../step_plans_for_ai/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.caveman.md)                                                                                                          | `codes/client_script/sales_order.js`, `sales_order_listview.js`, `so_script.js`               | `tabSales Order`, `tabProject`, `SalesOrderBaselineService`, `ProjectWBSInstantiationService`                                                     | **Reconciled & Ready** |
| **07**  | **Dual Progress Bar Lifecycle & SLA Engine**                            | [`ADR-007`](../decisions/ADR-007-DUAL-PROGRESS-BAR-LIFECYCLE-SLA-ENGINE.md)               | [`STEP_07`](../../step_plans/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.md)    | [`STEP_07.caveman`](../../step_plans_for_ai/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.caveman.md)                                                                                                 | `codes/client_script/task.js`, `bsh.js`                                                       | `LifecycleProgressBarService`, `EnterpriseSLADaemonService`, `tabRemark-Delay Log`                                                                | **Reconciled & Ready** |
| **08**  | **Material Dispatch Logistics & Delivery Note Serialized Tracking**     | [`ADR-008`](../decisions/ADR-008-MATERIAL-DISPATCH-DELIVERY-NOTE-SERIALIZED-LOGISTICS.md) | [`STEP_08`](../../step_plans/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.md)  | [`STEP_08.caveman`](../../step_plans_for_ai/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.caveman.md)                                                                                               | `codes/client_script/delivery_note_listview.js`                                               | `tabDelivery Note`, Frappe v15 SABB 2D Barcode Scan, 48h SLA, Digital POD                                                                         | **Reconciled & Ready** |
| **09**  | **Installation Zone WBS & Daily Progress Reports (DPR)**                | [`ADR-009`](../decisions/ADR-009-INSTALLATION-ZONE-WBS-DPR-EXECUTION.md)                  | [`STEP_09`](../../step_plans/STEP_09_INSTALLATION_ZONE_DPR_SPECIFICATION.md)            | [`STEP_09.caveman`](../../step_plans_for_ai/STEP_09_INSTALLATION_ZONE_DPR_SPECIFICATION.caveman.md)                                                                                                         | `codes/client_script/project_listview.js`                                                     | `tabDaily Progress Report`, IEC 62446-1 Testing Gate, `InstallationExecutionService`                                                              | **Reconciled & Ready** |
| **10**  | **Dual-Timing Statutory Liaisoning, Regulatory Inspection & Grid Sync** | [`ADR-010`](../decisions/ADR-010-LIAISONING-STATUTORY-INSPECTION-GRID-SYNC.md)            | [`STEP_10`](../../step_plans/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.md)             | [`STEP_10.caveman`](../../step_plans_for_ai/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.caveman.md)                                                                                                          | `codes/client_script/lns.js`, `lns_listview.js`, `sync_lias.js`                               | `tabLiaisoning And Synchronization`, CEIG/JMI, 10d SLA, COD Certificate                                                                           | **Reconciled & Ready** |
| **12**  | **Store Material Request & Automated Low-Stock Monitoring**             | [`ADR-012`](../decisions/ADR-012-STORE-MATERIAL-REQUEST-LOW-STOCK-MONITORING.md)          | [`STEP_12`](../../step_plans/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md) | [`STEP_12.caveman`](../../step_plans_for_ai/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.caveman.md)                                                                                              | `solar_module/api/store.py`, `solar_module/tasks.py`                                          | `tabMaterial Request`, `tabSolar Low Stock Incident Log`, `StoreRequisitionService`                                                               | **Reconciled & Ready** |
| **13**  | **Supplier Request for Quotation (RFQ) Multi-Vendor Governance**        | [`ADR-013`](../decisions/ADR-013-SUPPLIER-REQUEST-FOR-QUOTATION-RFQ.md)                   | [`STEP_13`](../../step_plans/STEP_13_SUPPLIER_RFQ_SPECIFICATION.md)                     | [`STEP_13.caveman`](../../step_plans_for_ai/STEP_13_SUPPLIER_RFQ_SPECIFICATION.caveman.md)                                                                                                                  | `solar_module/api/procurement.py`, `solar_module/overrides/rfq.py`                            | `tabRequest for Quotation`, `tabRequest for Quotation Supplier`, `RFQDispatchService`, `SupplierShortlistService`                                 | **Reconciled & Ready** |
| **14**  | **Supplier Quotation Comparative Evaluation Matrix & Landed Cost**      | [`ADR-014`](../decisions/ADR-014-SUPPLIER-QUOTATION-COMPARATIVE-EVALUATION-MATRIX.md)     | [`STEP_14`](../../step_plans/STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.md)      | [`STEP_14.caveman`](../../step_plans_for_ai/STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.caveman.md)                                                                                                   | `solar_module/api/procurement.py`, `codes/client_script/quotation_comparison_matrix.js`       | `tabQuotation Comparison Matrix`, `tabSupplier Quotation`, `LandedCostCalculationService`, `WeightedScoringEngineService`                         | **Reconciled & Ready** |
| **15**  | **Purchase Order Authorization, Solar Milestone Terms & Routing**       | [`ADR-015`](../decisions/ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md)         | [`STEP_15`](../../step_plans/STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md)     | [`STEP_15.caveman`](../../step_plans_for_ai/STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.caveman.md)                                                                                                  | `solar_module/api/procurement.py`, `codes/client_script/purchase_order.js`                    | `tabPurchase Order`, `tabPurchase Order Item`, `Solar SCM Settings`, `PurchaseOrderValidationService`, `POAuthorizationMatrixService`             | **Reconciled & Ready** |
| **16**  | **Multi-Location Barcode Purchase Receipt (GRN) & Custody Approval**    | [`ADR-016`](../decisions/ADR-016-MULTI-LOCATION-PURCHASE-RECEIPT-BARCODE-GRN.md)          | [`STEP_16`](../../step_plans/STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md)             | [`STEP_16.caveman`](../../step_plans_for_ai/STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.caveman.md)                                                                                                          | `solar_module/api/procurement.py`, `codes/client_script/purchase_receipt.js`                  | `tabPurchase Receipt`, `tabPurchase Receipt Item`, `Solar SCM Settings`, `PurchaseReceiptValidationService`, `GRNStockUpdateOrchestrationService` | **Reconciled & Ready** |

---

## 3. Stage-by-Stage Detailed Reconciliation Audits

### Stage 01: Lead Capture, Deduplication & Survey Scheduling

- **Document References:** [`ADR-001`](../decisions/ADR-001-LEAD-MANAGEMENT-DEDUPLICATION-ROUTING.md) | [`STEP_01`](../../step_plans/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.md) | [`STEP_01.caveman`](../../step_plans_for_ai/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.caveman.md) | [`TB-01.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md)
- **Primary DocType:** `tabLead` (extended with `custom_pincode`, `custom_address`, `custom_sanctioned_load`, `custom_monthly_bill`, `custom_proposed_kw`, `stage_status`, `complete_status`, `sla_due_date`, `for_survey_assign_on`).
- **Core Domain Services:** `LeadValidationService`, `LeadSLAService`, `SiteSurveyBridgeService`, `LeadNotificationService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Phone Normalization & Deduplication:_ Strips spaces, non-numerics, `+91`, and `0`; enforces `^[6-9]\d{9}$`. Cross-queries `tabLead`, `tabCRM Lead`, `tabCustomer`, and `tabContact` with `(mobile_no, status)` composite index.
  2. _Quarantine Boundary:_ Complete quarantine inside `tabLead` throughout Stages 01–04; zero premature `Customer` creation.
  3. _Two-Tier SLA:_ 2-hour initial contact window; 24-hour survey assignment window; automated background checks every 15 minutes.
  4. _Delay Enforcement:_ Hard blocking of state transitions when `stage_status = 'Overdue'` unless a justified record is appended to `tabRemark-Delay Log`.
  5. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-01.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestLeadTracerBullet`) across Desk script, whitelisted APIs, domain services, and `tabSite Survey` draft instantiation.
- **Role Standard:** `Lead Representative` (Inbound), `Sales Representative` (Field), `Area Sales Manager` (Territory).
- **Audit Verification:** ✔ Schema complete | ✔ State machine defined | ✔ SOLID services decoupled | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 02: Technical Site Survey & Audit (Offline Engine)

- **Document References:** [`ADR-002`](../decisions/ADR-002-TECHNICAL-SITE-SURVEY-AUDIT-OFFLINE-ENGINE.md) | [`STEP_02`](../../step_plans/STEP_02_SITE_SURVEY_SPECIFICATION.md) | [`STEP_02.caveman`](../../step_plans_for_ai/STEP_02_SITE_SURVEY_SPECIFICATION.caveman.md)
- **Primary DocType:** `tabSite Survey` (standalone submittable DocType with child table `tabSurvey Checklist Item`).
- **Core Domain Services:** `SiteSurveyValidationService`, `SurveySLAService`, `SurveySyncService`, `SurveyAuditBridgeService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Offline-First PWA Sync:_ Field engineers capture audits offline in browser IndexedDB; background synchronization upon network reconnection.
  2. _GPS Geofencing & Photo Checklist:_ 6 mandatory photo items (roof overview, electrical DB, distribution meter, structure foundation, shadow obstacles, distribution transformer).
  3. _24-Hour Survey SLA:_ Turnaround countdown from assignment timestamp (`for_survey_assign_on`); automated escalation if breached.
  4. _Automated Downstream Instantiation:_ Survey submission programmatically instantiates `Survey Engineering Design` (Stage 03) in `Draft` state.
- **Role Standard:** `Survey Engineer`, `Site Survey Auditor`, `Survey Assistant`.
- **Audit Verification:** ✔ Schema complete | ✔ Offline IndexedDB sync specified | ✔ Verification gates enforced | ✔ Tests defined.

---

### Stage 03: Survey Engineering Design & Dynamic BOM Engine

- **Document References:** [`ADR-003`](../decisions/ADR-003-SURVEY-ENGINEERING-DESIGN-DYNAMIC-BOM-ENGINE.md) | [`STEP_03`](../../step_plans/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.md) | [`STEP_03.caveman`](../../step_plans_for_ai/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.caveman.md)
- **Primary DocType:** `tabSurvey Engineering Design` (`is_submittable = 1`, child table `custom_quot_bom`).
- **Core Domain Services:** `SolarEngineeringCalculationService`, `DynamicBOMExplosionService`, `DesignValidationService`, `EngineeringAuditService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _CAD / SLD Attachment Versioning:_ AutoCAD DWG and Single Line Diagram (SLD) PDF upload with 25MB file limit and SHA-256 fingerprinting.
  2. _Parametric Voltage Drop Calculation:_ Real-time server-side electrical check asserting DC and AC voltage drops do not exceed 2% ($V_{drop} \le 2\%$).
  3. _Dynamic BOM Explosion:_ Parametrically explodes panels, inverters, structure rails, cables, ACDB/DCDB boxes, earthing kits, and lightning arrestors into `custom_quot_bom`.
  4. _Baseline Freeze:_ Document submission freezes BOM hash (`bom_hash`), preventing silent line-item alterations during commercial proposal generation.
- **Role Standard:** `Design Engineer`, `CAD Design Specialist`, `Design Manager`.
- **Audit Verification:** ✔ Schema complete | ✔ Voltage drop math validated | ✔ SHA-256 baseline freeze enforced | ✔ Tests defined.

---

### Stage 04: Proposal & Subsidy Engine

- **Document References:** [`ADR-004`](../decisions/ADR-004-PROPOSAL-SUBSIDY-ENGINE.md) | [`STEP_04`](../../step_plans/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.md) | [`STEP_04.caveman`](../../step_plans_for_ai/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.caveman.md)
- **Primary DocType:** `tabQuotation` (solar extensions, child table `tabQuotation Item`).
- **Core Domain Services:** `SolarProposalPricingService`, `SubsidyCalculationService`, `ProposalValidationService`, `ProposalPDFService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Two-Tier Pre-fill:_ Automatically pulls preliminary capacity from `Site Survey` and approved line-item BOM from `Survey Engineering Design`.
  2. _70:30 Solar GST Engine:_ Enforces Ministry of Finance statutory split: 70% Goods (taxed @ 12% GST) and 30% Services/Erection (taxed @ 18% GST), producing effective composite GST rate of 13.8%.
  3. _PM Surya Ghar Subsidy Automation:_ Applies central financial assistance (CFA) brackets: ₹30,000 for 1 kW, ₹60,000 for 2 kW, ₹78,000 for $\ge 3$ kW, plus applicable state subsidies.
  4. _Gross Margin Floor Gate:_ Hard-blocks proposal submission if project gross margin falls below 18% unless authorized via manager override.
- **Role Standard:** `Sales Representative`, `Commercial Officer`, `Area Sales Manager`.
- **Audit Verification:** ✔ Tax formulas validated | ✔ Subsidy slabs verified | ✔ Margin floor gate enforced | ✔ Tests defined.

---

### Stage 05: Advance Payment Clearance & Customer Master Inception

- **Document References:** [`ADR-005`](../decisions/ADR-005-ADVANCE-PAYMENT-CUSTOMER-MASTER-INCEPTION.md) | [`STEP_05`](../../step_plans/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.md) | [`STEP_05.caveman`](../../step_plans_for_ai/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.caveman.md)
- **Primary DocType:** `tabPayment Entry` / `tabAdvance Clearance Gate` / `tabCustomer`.
- **Core Domain Services:** `AdvancePaymentGateService`, `CustomerInceptionService`, `AccountsReconciliationBridgeService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Commercial Inception Gate:_ Enforces $\ge 20\%$ verified monetary advance (or formal bank loan sanction letter) before converting prospective lead to permanent customer.
  2. _Clean Ledger Inception:_ Programmatically instantiates `Customer`, `Address`, and `Contact` records, establishing clean financial accounting entities.
  3. _Audit Quarantine Transition:_ Unlinks prospect from lead quarantine, locking historical lead records and preventing duplicate master creation.
  4. _Downstream Sales Order Clearance:_ Advance clearance flag (`advance_cleared = 1`) acts as hard prerequisite for Stage 06 Sales Order submission.
- **Role Standard:** `Accounts Assistant`, `Finance Lead`, `Commercial Officer`.
- **Audit Verification:** ✔ Gate criteria verified | ✔ Entity migration verified | ✔ Ledger separation enforced | ✔ Tests defined.

---

### Stage 06: Sales Order Commercial Baseline & Downstream Spawning

- **Document References:** [`ADR-006`](../decisions/ADR-006-SALES-ORDER-BASELINE-DOWNSTREAM-SPAWNING.md) | [`STEP_06`](../../step_plans/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.md) | [`STEP_06.caveman`](../../step_plans_for_ai/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.caveman.md)
- **Primary DocType:** `tabSales Order` (`is_submittable = 1`, linked to `tabProject`).
- **Core Domain Services:** `SalesOrderBaselineService`, `ProjectWBSInstantiationService`, `DownstreamTaskSpawningService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Commercial & Technical Baseline Freeze:_ Locking pricing, payment milestone terms, and technical BOM hash upon submission.
  2. _Automatic Project & WBS Container Creation:_ Programmatically instantiates ERPNext `Project` record pre-configured with multi-zone WBS task templates (Civil, Structural, Electrical, Testing).
  3. _Downstream Task Spawning:_ Automatically triggers Store Manager Material Request/Delivery task (Stage 08) and Phase 1 DISCOM Early Liaisoning file (Stage 10A).
  4. _Project Stepper Handover:_ Transitions system tracking from Pre-Sales Stepper (Progress Bar 1) to Project Execution Stepper (Progress Bar 2).
- **Role Standard:** `Commercial Officer`, `Sales Operations Executive`.
- **Audit Verification:** ✔ Baseline freeze verified | ✔ WBS spawning verified | ✔ Cross-doctype linking verified | ✔ Tests defined.

---

### Stage 07: Dual Progress Bar Lifecycle & SLA Engine

- **Document References:** [`ADR-007`](../decisions/ADR-007-DUAL-PROGRESS-BAR-LIFECYCLE-SLA-ENGINE.md) | [`STEP_07`](../../step_plans/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.md) | [`STEP_07.caveman`](../../step_plans_for_ai/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.caveman.md)
- **Primary DocType:** `tabSolar EPC Progress Engine` / `tabSolar SLA Settings` / `tabRemark-Delay Log`.
- **Core Domain Services:** `LifecycleProgressBarService`, `EnterpriseSLADaemonService`, `DelayAuditService`, `EscalationNotificationService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Dual Progress Bar Architecture:_
     - **Progress Bar 1 (Pre-Sales Stepper):** Lead Ingestion $\rightarrow$ Site Survey $\rightarrow$ Engineering Design $\rightarrow$ Proposal $\rightarrow$ Advance Clearance $\rightarrow$ Sales Order.
     - **Progress Bar 2 (Project Execution Stepper):** Material Dispatch $\rightarrow$ Civil/Structural Foundation $\rightarrow$ Electrical Installation $\rightarrow$ Material Reconciliation $\rightarrow$ Statutory Inspection & Net Metering $\rightarrow$ Final Handover.
  2. _Redis SLA Daemon (`solar_module.tasks.recompute_enterprise_slas`):_ Executes every 15 minutes to evaluate active SLA countdowns across all stages.
  3. _Mandatory Delay Audit Log:_ When an SLA breaches, document stage status transitions to `Overdue`, locking document progress until a valid reason is recorded in `tabRemark-Delay Log`.
  4. _Omnichannel Escalation:_ Automated real-time alerts dispatched to Raven channels and WhatsApp Business API.
- **Role Standard:** `Project Engineer`, `Admin` (Project Supreme Command).
- **Audit Verification:** ✔ Stepper UI models specified | ✔ Redis worker logic verified | ✔ Delay log schema verified | ✔ Tests defined.

---

### Stage 08: Material Dispatch Logistics & Delivery Note Serialized Tracking

- **Document References:** [`ADR-008`](../decisions/ADR-008-MATERIAL-DISPATCH-DELIVERY-NOTE-SERIALIZED-LOGISTICS.md) | [`STEP_08`](../../step_plans/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.md) | [`STEP_08.caveman`](../../step_plans_for_ai/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.caveman.md)
- **Primary DocType:** `tabDelivery Note` (`is_submittable = 1`, linked to `tabSerial and Batch Bundle`).
- **Core Domain Services:** `MaterialDispatchValidationService`, `SerializedBarcodeTrackingService`, `LogisticsSLAService`, `PODVerificationService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _100% 2D Barcode Serial Tracking:_ Enforces Frappe v15 Serial and Batch Bundle (SABB) scanning for all critical solar assets (PV modules, solar inverters, bi-directional meters). Zero un-serialized dispatch.
  2. _Statutory Dispatch Gates:_ Submission strictly blocked without verified E-Way Bill Number, Vehicle Registration, Driver Phone, and signed Pre-Dispatch Quality Inspection Checklist.
  3. _48-Hour Dispatch SLA:_ Warehouse staging and dispatch SLA enforced from Sales Order material release timestamp.
  4. _Closed-Loop Digital POD:_ Digital Proof of Delivery signed off via customer OTP verification or digital signature on glass upon physical offloading at site.
- **Role Standard:** `Store Manager`, `Store Assistant`.
- **Audit Verification:** ✔ SABB schema verified | ✔ Statutory gates enforced | ✔ Digital POD verified | ✔ Tests defined.

---

### Stage 09: Installation Zone WBS & Daily Progress Reports (DPR)

- **Document References:** [`ADR-009`](../decisions/ADR-009-INSTALLATION-ZONE-WBS-DPR-EXECUTION.md) | [`STEP_09`](../../step_plans/STEP_09_INSTALLATION_ZONE_DPR_SPECIFICATION.md) | [`STEP_09.caveman`](../../step_plans_for_ai/STEP_09_INSTALLATION_ZONE_DPR_SPECIFICATION.caveman.md)
- **Primary DocType:** `tabDaily Progress Report` (submittable), linked to `tabProject` and `tabTask`.
- **Core Domain Services:** `InstallationExecutionService`, `DPRValidationService`, `PreCommissioningTestGateService`, `WBSMilestoneSyncService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Multi-Zone Execution Architecture:_ Supports rooftop zoning (Zone A, Zone B, Ground Array) with discrete civil, structural, and electrical milestones.
  2. _Mobile DPR Ingestion:_ Daily site submissions capturing worker muster, installed hardware quantities, and mandatory geo-tagged photographs.
  3. _IEC 62446-1 Pre-Commissioning Electrical Gate:_ Hard-blocking test certificate upload requiring Insulation Resistance (Megger $\ge 1.0\text{ M}\Omega$), String Open-Circuit Voltage ($V_{oc}$ within 5%), and Earth Pit Resistance ($R_e \le 5.0\ \Omega$).
  4. _Automated Downstream Handoff:_ Testing sign-off automatically unlocks Stage 10B Statutory Grid Synchronization countdown.
- **Role Standard:** `Project Engineer`, `Site Supervisor`, `Civil/Electrical Site Engineer`.
- **Audit Verification:** ✔ Multi-zone WBS verified | ✔ IEC 62446-1 test gate verified | ✔ Downstream trigger verified | ✔ Tests defined.

---

### Stage 10: Dual-Timing Statutory Liaisoning, Regulatory Inspection & Grid Sync

- **Document References:** [`ADR-010`](../decisions/ADR-010-LIAISONING-STATUTORY-INSPECTION-GRID-SYNC.md) | [`STEP_10`](../../step_plans/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.md) | [`STEP_10.caveman`](../../step_plans_for_ai/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.caveman.md)
- **Primary DocType:** `tabLiaisoning And Synchronization` (`is_submittable = 1`, linked to `tabSales Order`, `tabProject`, `tabCustomer`).
- **Core Domain Services:** `LiaisoningInceptionService`, `StatutoryInspectionGateService`, `NetMeteringSyncService`, `ProjectCompletionAnchorService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Dual-Timing Operational Architecture:_
     - **Phase 1 (Post-Sales Order):** Early DISCOM connectivity feasibility filing, KYC document collection, load sanctioning, and preliminary NOC.
     - **Phase 2 (Post-Installation):** CEIG electrical safety approval, bi-directional net-meter installation, Joint Meter Inspection (JMI) report, grid energization.
  2. _10-Day Statutory SLA Countdown:_ Initiated automatically upon Stage 08 electrical testing sign-off, monitoring statutory turnaround times to prevent subsidy expiry and customer disputes.
  3. _Immutable Project Completion Anchor:_ An ERPNext `Project` cannot be marked "Completed" until official grid synchronization readings and Commercial Operation Date (COD) certificate are submitted.
  4. _Downstream O&M Handoff:_ Commissioning automatically spawns Stage 11 Solar Asset Register and warranty tracking records.
- **Role Standard:** `Liaisoning Officer`, `Statutory Compliance Representative`.
- **Audit Verification:** ✔ Dual-timing state machine verified | ✔ 10-day statutory SLA verified | ✔ Immutable completion anchor verified | ✔ Tests defined.

---

### Step 12: Store Requisitions & Automated Low-Stock Monitoring (Flow 2: Step 01)

- **Document References:** [`ADR-012`](../decisions/ADR-012-STORE-MATERIAL-REQUEST-LOW-STOCK-MONITORING.md) | [`STEP_12`](../../step_plans/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md) | [`STEP_12.caveman`](../../step_plans_for_ai/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabMaterial Request` (extended with `custom_project_reference`, `custom_sales_order`, `custom_reorder_trigger_source`, `custom_urgency_level`, `custom_workflow_status`, `custom_sla_deadline`, `custom_delay_reason`), `tabSolar Low Stock Incident Log`, `tabItem`, `tabItem Reorder`, `tabBin`.
- **Core Domain Services:** `StoreRequisitionService`, `ReorderCalculationService`, `StoreNotificationBroker`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Dual-Trigger Demand Inception:_
     - **Channel A (Project Indents):** Initiated by `Project Engineer` or `Store Assistant` for active Solar EPC sites; gated against unissued Survey Engineering Design BOM (`STEP_03`).
     - **Channel B (Automated Low-Stock Replenishment):** Executed by background runner (`solar_module.tasks.monitor_low_stock`) scanning warehouse bins.
  2. _True Solvency Mathematics:_ Decouples naive ledger stock (`actual_qty`) from true pipeline availability:
     $$\text{Projected Qty} = \text{Actual Qty} + \text{Ordered Qty} + \text{Indented Qty} - \text{Reserved Qty}$$
  3. _Replenishment Quantity Algorithm:_ Computes buffer deficit factoring in supplier lead time run rates and pallet unit packaging rounding (36 modules/pallet for solar panels).
  4. _Four Enforced Verification Gates:_
     - **Gate 1:** Duplicate open requisition prevention for identical item/warehouse.
     - **Gate 2:** Lead time feasibility check (`schedule_date >= today + lead_time_days`) with emergency override justification.
     - **Gate 3:** Project BOM ceiling headroom netting preventing site over-draws.
     - **Gate 4:** Downstream SCM traceability across RFQ (`STEP_13`), Quotation Comparison (`STEP_14`), and PO (`STEP_15`).
  5. _Tiered SLA & Multi-Channel Broadcasts:_ 4h (Emergency), 24h (Project), 48h (Routine) SLA windows; automated alert dispatch to `Purchase Manager` and `Store Manager` with Class-A escalation to `Admin`.
- **Role Standard:** `Store Assistant`, `Store Manager`, `Purchase Assistant`, `Purchase Manager`.
- **Audit Verification:** ✔ Schema extensions complete | ✔ Verification gates validated | ✔ Domain services decoupled | ✔ Tests defined (zero DB commit).

---

### Step 13: Supplier Request for Quotation (RFQ) Multi-Vendor Governance (Flow 2: Step 02)

- **Document References:** [`ADR-013`](../decisions/ADR-013-SUPPLIER-REQUEST-FOR-QUOTATION-RFQ.md) | [`STEP_13`](../../step_plans/STEP_13_SUPPLIER_RFQ_SPECIFICATION.md) | [`STEP_13.caveman`](../../step_plans_for_ai/STEP_13_SUPPLIER_RFQ_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabRequest for Quotation` (extended with `custom_material_request_ref`, `custom_project_ref`, `custom_sales_order_ref`, `custom_rfq_stage`, `custom_bid_deadline`, `custom_is_single_source`, `custom_single_source_justification`, `custom_single_source_approved_by`, `custom_sealed_bids`, `custom_bids_unsealed`, `custom_unsealed_by`, `custom_unsealed_on`, `custom_sla_deadline`, `custom_sla_status`, `custom_portal_dispatch_count`, `custom_delay_reason_table`), `tabRequest for Quotation Item`, `tabRequest for Quotation Supplier`, `tabSupplier Quotation`, `tabRemark-Delay Log`.
- **Core Domain Services:** `SupplierShortlistService`, `RFQDispatchService`, `RFQSLAService`, `SealedBidSecurityService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Mandatory Multi-Supplier Bidding Gate ($\ge 3$ Vendors):_ Controller strictly asserts `len(doc.suppliers) >= 3` before allowing `docstatus = 1` submission, eliminating maverick buying and vendor favoritism.
  2. _Single-Source Exception Protocol:_ Allows bypass of the 3-vendor rule only when `custom_is_single_source = 1`, requiring mandatory justification ($\ge 30$ chars) and explicit role authorization by `Purchase Manager` or `Admin`.
  3. _Step 19 Scorecard Quality Integration:_ Dynamic candidate shortlisting queries `tabVendor Rating` to prioritize Tier 1 and Approved suppliers while strictly disqualifying Blacklisted vendors.
  4. _Passwordless Supplier Portal & Token Security:_ Submission generates cryptographically random 256-bit UUID tokens (`custom_portal_token`) allowing external vendors to enter rates, lead times, warranties, and datasheets at `/solar/rfq-portal/:token`, auto-populating ERPNext `Supplier Quotation` with zero manual transcription.
  5. _Anti-Tampering Sealed Bids Governance:_ High-value tenders ($> ₹1,000,000$) support `custom_sealed_bids = 1`, cryptographically masking submitted rates until bid deadline expiry and formal unsealing sign-off.
  6. _72-Hour Response SLA & Reminder Daemon:_ Automated background worker evaluates active RFQs, sending multi-channel reminders at T-24h and T-48h, transitioning breached tenders to `Overdue` and enforcing mandatory delay justifications in `tabRemark-Delay Log`.
- **Role Standard:** `Purchase Assistant`, `Purchase Manager`, `Store Assistant`, `Store Manager`, `Admin`.
- **Audit Verification:** ✔ Schema complete | ✔ Multi-vendor gates verified | ✔ Token portal specified | ✔ Sealed bids documented | ✔ Tests defined (zero DB commit).

---

### Step 14: Supplier Quotation Comparative Evaluation Matrix & Landed Cost (Flow 2: Step 03)

- **Document References:** [`ADR-014`](../decisions/ADR-014-SUPPLIER-QUOTATION-COMPARATIVE-EVALUATION-MATRIX.md) | [`STEP_14`](../../step_plans/STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.md) | [`STEP_14.caveman`](../../step_plans_for_ai/STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabQuotation Comparison Matrix` (submittable), `tabQuotation Comparison Item`, `tabQuotation Comparison Supplier Summary`, `tabSupplier Quotation` (extended with `custom_rfq_reference`, `custom_freight_charges`, `custom_transit_insurance`, `custom_unloading_charges`, `custom_landed_cost_unit`, `custom_net_effective_total`, `custom_promised_lead_days`, `custom_warranty_months`, `custom_technical_compliant`), `tabRemark-Delay Log`.
- **Core Domain Services:** `LandedCostCalculationService`, `WeightedScoringEngineService`, `QuotationComparisonMatrixService`, `POAwardInstantiationService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _True Landed Cost Normalization:_ Mathematically normalizes divergent vendor terms (Ex-Factory, Ex-Works, FOR Site), standardizing base price, packing & forwarding, freight, transit insurance, site unloading, and statutory GST ITC net calculations.
  2. _100-Point Multi-Factor Scoring Engine:_ Evaluates commercial cost ($50\%$), delivery lead time feasibility ($25\%$), historical quality ratings from Step 19 ($15\%$), and payment terms/warranty ($10\%$).
  3. _Enforced Non-L1 Selection Gate:_ Hard-blocks procurement awards where non-L1 suppliers are chosen unless accompanied by a mandatory justification ($\ge 40$ chars) and explicit authorization by `Purchase Manager` or `Admin`.
  4. _Sealed Bid Unmasking Protocol:_ Asserts bid deadline closure and formal unsealing sign-off before allowing comparison generation for high-value tenders ($> ₹1,000,000$).
  5. _48-Hour Evaluation Turnaround SLA:_ Automated background runner tracks evaluation time, transitioning breached matrices to `Overdue` and enforcing delay logging in `tabRemark-Delay Log`.
  6. _Downstream PO Instantiation Gate:_ One-click programmatic creation of ERPNext `tabPurchase Order` with locked rates, terms, and delivery schedules, preventing duplicate PO generation.
- **Role Standard:** `Purchase Assistant`, `Purchase Manager`, `Project Engineer`, `Store Assistant`, `Store Manager`, `Admin`.
- **Audit Verification:** ✔ Schema complete | ✔ Landed cost formulas verified | ✔ Non-L1 gate enforced | ✔ 100-pt scoring validated | ✔ Tests defined (zero DB commit).

---

### Step 15: Purchase Order Authorization, Solar Milestone Terms & Delivery Routing (Flow 2: Step 04)

- **Document References:** [`ADR-015`](../decisions/ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md) | [`STEP_15`](../../step_plans/STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md) | [`STEP_15.caveman`](../../step_plans_for_ai/STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabPurchase Order` (extended with `custom_comparison_matrix_ref`, `custom_awarded_quotation_ref`, `custom_material_request_ref`, `custom_is_single_source`, `custom_po_classification`, `custom_project_ref`, `custom_sales_order_ref`, `custom_delivery_location_type`, `custom_target_site_warehouse`, `custom_authorization_tier`, `custom_authorized_by`, `custom_authorized_on`, `custom_authorization_remarks`, `custom_advance_pct`, `custom_advance_amount`, `custom_advance_cleared`, `custom_advance_payment_ref`, `custom_retention_pct`, `custom_retention_due_event`, `custom_liquidated_damages_clause`, `custom_portal_token`, `custom_vendor_acknowledgment_status`, `custom_vendor_ack_date`, `custom_sla_deadline`, `custom_sla_status`, `custom_delay_reason_table`), `tabPurchase Order Item`, `tabPayment Schedule`, `tabSolar SCM Settings`, `tabRemark-Delay Log`.
- **Core Domain Services:** `PurchaseOrderValidationService`, `POAuthorizationMatrixService`, `POMilestoneTermsService`, `POSLAService`, `PODispatchBridgeService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Rate Lock & Upstream Matrix Linkage:_ Enforces linkage to submitted `Quotation Comparison Matrix` (`docstatus = 1`, `evaluation_status = 'Award Approved'`); prevents unit rate inflation beyond evaluated landed rate.
  2. _Multi-Tier Financial Authority Delegation Gate:_ Enforces 4 financial delegation tiers: Tier 1 ($\le ₹1\text{L}$, `Purchase Assistant` / `Purchase Manager`), Tier 2 ($₹1\text{L}-₹10\text{L}$, `Purchase Manager`), Tier 3 ($₹10\text{L}-₹50\text{L}$, `Commercial Officer`), and Tier 4 ($> ₹50\text{L}$, `Admin` / `Managing Director`).
  3. _Solar Milestone Payment Schedule & Retention:_ Capital solar purchases strictly require structured milestone tranches (Advance, In-Transit/LR, Post-GRN Inspection, COD/PBG Retention). Generic single-bullet "Immediate" terms are hard-blocked.
  4. _Configurable / Optional Project Headroom Check:_ Automatically bypassed for Central Inventory Replenishment and Consolidated Multi-Project bulk purchases. For project-linked orders, check against Commercial Proposal / Sales Order BOM is configurable via `Solar SCM Settings` (`enforce_project_bom_ceiling`).
  5. _Multi-Location Delivery Routing for Step 16 GRN:_ Enforces delivery destination routing to Central Store (`Stores - SEPC`) or Direct Site (`Site - <Project Code> - SEPC`). Serialized items flagged with `custom_requires_barcode_serials = 1` for mandatory SABB 2D barcode scan.
  6. _24h Release & 48h Vendor Acknowledgment SLA:_ Monitored by Redis daemons with passwordless token confirmation and delay logging in `tabRemark-Delay Log`.
- **Role Standard:** `Purchase Assistant`, `Purchase Manager`, `Commercial Officer`, `Accounts Assistant`, `Project Engineer`, `Store Manager`, `Admin`.
- **Audit Verification:** ✔ Schema complete | ✔ 4-tier delegation verified | ✔ Milestone schedules enforced | ✔ Configurable BOM check verified | ✔ Tests defined (zero DB commit).

---

### Step 16: Multi-Location Barcode Purchase Receipt (GRN) & Tri-Party Custody Approval Architecture (Flow 2: Step 05)

- **Document References:** [`ADR-016`](../decisions/ADR-016-MULTI-LOCATION-PURCHASE-RECEIPT-BARCODE-GRN.md) | [`STEP_16`](../../step_plans/STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md) | [`STEP_16.caveman`](../../step_plans_for_ai/STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabPurchase Receipt` (extended with `custom_received_by_team`, `custom_received_by_user`, `custom_receipt_location_type`, `custom_default_store_warehouse`, `custom_project_ref`, `custom_sales_order_ref`, `custom_transporter_name`, `custom_lr_number`, `custom_delivery_challan_file`, `custom_transporter_lr_file`, `custom_gps_latitude`, `custom_gps_longitude`, `custom_barcode_scan_enforced`, `custom_barcode_scan_bypassed`, `custom_has_store_bound_items`, `custom_has_site_bound_items`, `custom_store_stock_approval_status`, `custom_site_stock_approval_status`, `custom_rejection_warehouse`, `custom_sla_deadline`, `custom_sla_status`, `custom_delay_reason_table`), `tabPurchase Receipt Item` (extended with `custom_destination_type`, `custom_requires_barcode_serials`, `custom_serial_scan_status`, `custom_rejection_reason_code`, `custom_damage_photo_1`, `custom_damage_photo_2`), `tabSolar SCM Settings`, `tabSerial and Batch Bundle`, `tabRemark-Delay Log`.
- **Core Domain Services:** `PurchaseReceiptValidationService`, `GRNStockUpdateOrchestrationService`, `GRNSerialBarcodeService`, `GRNSLAService`, `GRNDownstreamBridgeService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Tri-Party Receiving Personas:_
     - **Store Team (`Store Assistant`, `Store Manager`):** Dock intake at Central Store (`Stores - SEPC`), warehouse re-assignable if regional store accepts stock; commits stock **automatically** to Store Warehouse on submission (`docstatus = 1`).
     - **Site Team (`Project Engineer`, `Site Supervisor`):** Direct-to-site intake (`Site - <Project Code> - SEPC`); enforces 500m GPS geofencing; commits stock **automatically** to Site Warehouse without requiring Admin store approval.
     - **Purchase Team (`Purchase Assistant`, `Purchase Manager`):** Direct procurement / factory-gate intake; supports flexible line routing (Store vs Site). Lines to Store held in `Pending Admin Approval` until `Admin` sign-off; lines to Site held in `Pending Site Approval` until `Project Manager` arrival sign-off.
  2. _Admin-Controllable Barcode Policy:_ Controlled via `Solar SCM Settings.enable_mandatory_barcode_pr` (managed strictly by `Admin`). If enabled, enforces 100% 2D barcode scan (SABB) for modules and inverters. If disabled, allows manual/lot entry without blocking field operations, logging `custom_barcode_scan_bypassed = 1`.
  3. _Quality Rejection Split & Quarantine:_ Broken/damaged units routed to `Quarantine / Rejection - SEPC` with mandatory defect code and minimum 2 attached damage photographs.
  4. _Downstream Automated Touchpoints:_ Unlocks Post-GRN milestone tranche in Step 15/18 `Payment Schedule`; dispatches OTD and quality rejection metrics to Step 19 `Vendor Rating`; enables site installation consumption for Stage 08 DPR; logs module/inverter serials into Stage 11 `Solar Asset Register`.
  5. _24h SLA Countdown & Delay Governance:_ Monitored by Redis daemon; overdue transitions enforce justification entries in `tabRemark-Delay Log`.
- **Role Standard:** `Store Assistant`, `Store Manager`, `Project Engineer`, `Project Manager`, `Purchase Assistant`, `Purchase Manager`, `Admin`.
- **Audit Verification:** ✔ Schema extensions complete | ✔ Tri-party stock posting logic verified | ✔ Admin barcode toggle verified | ✔ Custody approval gates enforced | ✔ Tests defined (zero DB commit).

---

### Step 17: Purchase Invoice 3-Way Match Verification & Admin-Governed Departmental Entry Authorization Architecture (Flow 2: Step 06)

- **Document References:** [`ADR-017`](../decisions/ADR-017-PURCHASE-INVOICE-3WAY-MATCH-ADMIN-ENTRY-GOVERNANCE.md) | [`STEP_17`](../../step_plans/STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.md) | [`STEP_17.caveman`](../../step_plans_for_ai/STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabPurchase Invoice` (extended with `custom_pi_entry_department`, `custom_po_reference`, `custom_grn_reference`, `custom_3way_match_status`, `custom_rate_variance_amount`, `custom_rate_variance_percent`, `custom_admin_price_override`, `custom_override_by`, `custom_override_reason`, `custom_sla_status`, `custom_sla_deadline`, `custom_sla_breach_hours`, `custom_delay_reason_table`), `tabPurchase Invoice Item` (extended with `custom_po_item_ref`, `custom_grn_item_ref`, `custom_po_contract_rate`, `custom_grn_accepted_qty`, `custom_qty_variance`, `custom_rate_variance`, `custom_rate_variance_pct`, `custom_item_3way_status`), `tabSolar SCM Settings` (`authorized_pi_entry_department`, `pi_3way_match_enforced`, `pi_rate_variance_tolerance_percent`, `pi_turnaround_sla_hours`, `pi_require_tds_verification`, `pi_require_gst_match`), `tabSolar SCM Policy Log`, `tabRemark-Delay Log`.
- **Core Domain Services:** `PurchaseInvoiceValidationService`, `ThreeWayMatchEngine`, `PIAuthorizationGateService`, `PISLAService`, `PIDownstreamBridgeService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Admin-Governed Departmental Entry Authorization:_ Solves the tri-department entry dilemma by empowering `Admin` to configure `Solar SCM Settings.authorized_pi_entry_department` (`Accounts`, `Store`, or `Purchase`). Unauthorized department attempts are rejected with an explicit `frappe.PermissionError`. `Admin` and `System Manager` retain supreme universal override access. All policy shifts require justification and log to `tabSolar SCM Policy Log`.
  2. _Line-Level 3-Way Match Verification:_ Billed quantity strictly capped by physical accepted quantity from linked `Purchase Receipt Item` (billing quarantined stock is barred). Unit rates verified against contracted PO rates with configurable tolerance ($\le 0.0\%$). Variances exceeding tolerance transition to `Discrepancy Hold`, requiring explicit `Admin` price override.
  3. _Duplicate Invoice Lockout:_ Database composite uniqueness constraint on `(supplier, bill_no, fiscal_year)`.
  4. _Statutory Tax Alignment:_ Enforces 70:30 Goods vs Services valuation check on composite solar EPC contracts + Section 194Q TDS / 206C(1H) TCS deduction tags.
  5. _24h SLA Countdown & Delay Governance:_ Monitored by Redis daemon; overdue transitions enforce justification entries in `tabRemark-Delay Log`.
  6. _Downstream Automated Touchpoints:_ Unlocks Post-GRN/Invoice milestone payment tranche in Step 15/18 `Payment Schedule`; dispatches price variance metrics to Step 19 `Vendor Rating` (15% commercial weighting); posts liability to General Ledger (`Creditors - SEPC`).
- **Role Standard:** `Accounts Assistant`, `Accounts Officer`, `Store Assistant`, `Store Manager`, `Purchase Assistant`, `Purchase Manager`, `Admin`, `System Manager`.
- **Audit Verification:** ✔ Schema extensions complete | ✔ Departmental entry policy gate verified | ✔ 3-Way match formulas verified | ✔ Admin price override verified | ✔ Tests defined (zero DB commit).

---

## 4. Cross-Stage Architecture Invariants & Standards Compliance

### 4.1 Enterprise Role Nomenclature (Zero "User" Suffix Rule)

All stages have been audited to ensure complete elimination of generic developer roles:

- ❌ Prohibited: `Lead User`, `Survey User`, `Sales User`, `Design User`, `Project User`, `Store User`, `Liaisoning User`, `Purchase User`.
- ✔ Approved & Reconciled:
  - `Lead Representative` (Stage 01)
  - `Survey Engineer` (Stage 02)
  - `Design Engineer` (Stage 03)
  - `Sales Representative` (Stage 04)
  - `Accounts Assistant` (Stage 05, Step 15, Step 17)
  - `Accounts Officer` (Step 17)
  - `Commercial Officer` (Stage 06, Step 15)
  - `Project Engineer` (Stage 07, 09, 14, 15)
  - `Store Manager` (Stage 08, Step 12, Step 13, Step 14, Step 15, Step 16, Step 17)
  - `Store Assistant` (Stage 08, Step 12, Step 13, Step 14, Step 16, Step 17)
  - `Liaisoning Officer` (Stage 10)
  - `Purchase Assistant` (Step 12, Step 13, Step 14, Step 15, Step 16, Step 17)
  - `Purchase Manager` (Step 12, Step 13, Step 14, Step 15, Step 16, Step 17)
  - `Project Manager` (Step 16)

### 4.2 Supreme Authority Standard (Admin vs System Manager)

Across all specifications:

- **`Administrator` & `System Manager` (Framework Supreme / Developer Realm):** Technical dev ops, bench commands, git repos, Python source code, DocType schema builders, and Redis queue workers.
- **`Admin` (Project Supreme Command):** Operational supremacy over all EPC lifecycles (Stages 01–11 and Flow 2 SCM), exclusive governance over `Solar SLA Settings`, `Solar Notification Settings`, `Solar SCM Settings`, and delay approvals. Restricted from touching source code or schema builder forms.

### 4.3 Database Schema & 3NF Data Integrity

- All child tables enforce explicit foreign keys (`parent`, `parenttype`, `parentfield`).
- High-frequency query columns (`mobile_no`, `project`, `sales_order`, `serial_no`, `status`, `rfq_reference`, `evaluation_status`, `custom_comparison_matrix_ref`, `custom_project_ref`, `custom_receipt_location_type`, `custom_po_reference`, `custom_grn_reference`, `custom_3way_match_status`) are backed by explicit B-Tree database indexes.
- Critical financial and technical state snapshots utilize SHA-256 baseline hashing (`bom_hash`).

### 4.4 Automated Testing & Zero-Commit Rule

- All unit and integration test specifications inherit from `frappe.tests.utils.FrappeTestCase` or `IntegrationTestCase`.
- In strict adherence to [`architect_docs/07_AUTOMATED_TESTING_QA_CI_CD.md`](../../architect_docs/07_AUTOMATED_TESTING_QA_CI_CD.md), zero test routines execute `frappe.db.commit()`, ensuring test database isolation and automatic rollbacks.

---

## 5. Lifecycle Roadmap & Next Implementation Horizons

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SOLAR EPC LIFECYCLE ROADMAP                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FLOW 1: CORE SOLAR EPC PROJECT EXECUTION (11 STAGES)                                             │
│  [✔] Stage 01: Lead Management, Deduplication & Routing                                          │
│  [✔] Stage 02: Technical Site Survey & Audit (Offline Engine)                                    │
│  [✔] Stage 03: Survey Engineering Design & Dynamic BOM Engine                                    │
│  [✔] Stage 04: Proposal & Subsidy Engine                                                         │
│  [✔] Stage 05: Advance Payment Clearance & Customer Master Inception                             │
│  [✔] Stage 06: Sales Order Baseline & Downstream Spawning                                        │
│  [✔] Stage 07: Dual Progress Bar Lifecycle & SLA Engine                                          │
│  [✔] Stage 08: Material Dispatch Logistics & Delivery Note Serialized Tracking                   │
│  [✔] Stage 09: Installation Zone WBS & Daily Progress Reports (DPR)                             │
│  [✔] Stage 10: Dual-Timing Statutory Liaisoning, Regulatory Inspection & Grid Sync               │
│  [ ] Stage 11: Lifecycle O&M, Solar Asset Register & Telemetry (PLANNED)                         │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FLOW 2: SCM, STORE, PURCHASE & VENDOR PROCUREMENT LIFECYCLE (8 STEPS)                           │
│  [✔] Step 12: Store Requisitions & Low Stock Monitoring                                          │
│  [✔] Step 13: Supplier Request for Quotation (RFQ)                                               │
│  [✔] Step 14: Supplier Quotation Comparative Evaluation Matrix                                   │
│  [✔] Step 15: Purchase Order Authorization & Milestone Terms                                     │
│  [✔] Step 16: Multi-Location Barcode GRN & Tri-Party Custody Approval                            │
│  [✔] Step 17: Purchase Invoicing & 3-Way Match Validation                                        │
│  [ ] Step 18: Joint Vendor Payment Monitoring Workbench                                          │
│  [ ] Step 19: Vendor Performance Rating Scorecard                                                │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Audit Sign-off

- **Audited By:** Lead AI Software Architect & System Engineer
- **Audit Timestamp:** 2026-09-24T12:30:00Z
- **Reconciliation Integrity:** 100% (All stages cross-referenced with ADRs, master step plans, AI plans, and codebase scripts; Step 17 reconciled with Admin-Governed Departmental Entry Authorization [Accounts, Store, Purchase] via Solar SCM Settings, 3-Way Matching Engine [PO vs GRN vs PI], rate variance tolerance with Admin override gate, duplicate invoice prevention, 24h SLA engine, and downstream unlocks for Step 18 Payment Workbench and Step 19 Vendor Rating).
- **Next Operational Action:** Author Step 18 Specification (`STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.md`) and Decision Record (`ADR-018`), or Stage 11 Specification (`STEP_11_LIFECYCLE_OM_TELEMETRY_SPECIFICATION.md`).

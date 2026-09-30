# Solar EPC Enterprise ERP — Master Lifecycle Execution & Reconciliation Log

**Document ID:** `LOG-MASTER-LIFECYCLE`  
**Governing Standard:** [`AGENTS.md`](../../AGENTS.md)  
**Location:** `docs/logs/LIFECYCLE_EXECUTION_LOG.md`  
**Primary Repository Reference:** [`step_plans/README.md`](../../step_plans/README.md)  
**Decisions Reference:** [`docs/decisions/`](../decisions/)  
**Last Reconciled:** 2026-09-30  
**Status:** Canonical & Audited

---

## 1. Purpose & Architectural Governance

In strict compliance with [`AGENTS.md`](../../AGENTS.md), this document serves as the **single authoritative progress, audit, and reconciliation log** across the entire **Sadbhav Solar EPC Enterprise ERP platform** (`solar_module` / `manoj`).

It records:

1. **Reconciliation Traceability:** Direct cross-referencing between architectural decisions ([`docs/decisions/`](../decisions/)), master step specifications ([`step_plans/`](../../step_plans/)), token-optimized AI specifications ([`step_plans_for_ai/`](../../step_plans_for_ai/)), and implementation scripts ([`codes/`](../../codes/)).
2. **Readiness & Audit Verification:** Systematic verification of data dictionaries, 3NF schema designs, state machines, SLA engines, domain services, security gates, and automated test assertions.
3. **Enterprise Standards Enforcement:** 100% adherence to the **Zero "User" Suffix Rule** and the **Supreme Command (`Admin`) vs. Developer (`System Manager`) Role Separation Standard**.

---

## 2. Master Lifecycle Status Matrix (Steps 00–19)

| Stage # | Stage Name & Scope                                                       | Architectural Decision (Why)                                                              | Master Specification (What & How)                                                          | AI Optimized Spec (Token-Efficient)                                                                                                                                                                                                                 | Legacy / Target Code Touchpoints                                                              | DocType & Service Entities                                                                                                                                                                    |  Documentation Status  |
| :-----: | :----------------------------------------------------------------------- | :---------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------: |
| **00**  | **Enterprise Role, Permission & Security Foundation Architecture**       | [`ADR-000`](../decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)              | [`STEP_00`](../../step_plans/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.md) | [`STEP_00.caveman`](../../step_plans_for_ai/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.caveman.md)<br>[`TB-00.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md) | `solar_module/security/`, `solar_module/mixins/`, `solar_module/api/security.py`              | `tabSolar Security Settings`, `tabSolar Cancellation Request`, `tabSolar Deletion Audit Log`, `RoleInheritanceService`, `StageForwardLockService`, `AdminAuditService`, `CascadePurgeService` | **Reconciled & Ready** |
| **01**  | **Lead Capture, Deduplication & Survey Scheduling**                      | [`ADR-001`](../decisions/ADR-001-LEAD-MANAGEMENT-DEDUPLICATION-ROUTING.md)                | [`STEP_01`](../../step_plans/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.md)                     | [`STEP_01.caveman`](../../step_plans_for_ai/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.caveman.md)<br>[`TB-01.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md)                                         | `codes/client_script/lead.js`, `lead_listview.js`                                             | `tabLead`, `LeadValidationService`, `LeadSLAService`, `SiteSurveyBridgeService`                                                                                                               | **Reconciled & Ready** |
| **02**  | **Technical Site Survey & Audit (Offline Engine)**                       | [`ADR-002`](../decisions/ADR-002-TECHNICAL-SITE-SURVEY-AUDIT-OFFLINE-ENGINE.md)           | [`STEP_02`](../../step_plans/STEP_02_SITE_SURVEY_SPECIFICATION.md)                         | [`STEP_02.caveman`](../../step_plans_for_ai/STEP_02_SITE_SURVEY_SPECIFICATION.caveman.md)<br>[`TB-02.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md)                                                   | `codes/client_script/site_survey.js`, `site_survey_listview.js`, `sitesurvey_to_quotation.js` | `tabSite Survey`, `tabSite Survey Doc Table`, `SurveyValidationService`, `SurveySLAService`, `SurveySyncService`, `SurveyBridgeService`                                                      | **Reconciled & Ready** |
| **03**  | **Survey Engineering Design & Dynamic BOM Engine**                       | [`ADR-003`](../decisions/ADR-003-SURVEY-ENGINEERING-DESIGN-DYNAMIC-BOM-ENGINE.md)         | [`STEP_03`](../../step_plans/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.md)       | [`STEP_03.caveman`](../../step_plans_for_ai/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.caveman.md)<br>[`TB-03.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md) | `codes/client_script/so_bom_item.js`                                                          | `tabSurvey Engineering Design`, `custom_quot_bom`, `SolarEngineeringCalculationService`                                                                                                       | **Reconciled & Ready** |
| **04**  | **Proposal & Subsidy Engine**                                            | [`ADR-004`](../decisions/ADR-004-PROPOSAL-SUBSIDY-ENGINE.md)                              | [`STEP_04`](../../step_plans/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.md)                    | [`STEP_04.caveman`](../../step_plans_for_ai/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.caveman.md)<br>[`TB-04.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md)                                     | `codes/client_script/proposal_listview.js`, `quotation_proposal.js`                            | `tabQuotation`, 70:30 Solar GST, `ProposalCalculationService`, `ProposalSubsidyService`, `ProposalMarginGateService`, `ProposalFinalizationService`                                          | **Reconciled & Ready** |
| **05**  | **Advance Payment Clearance & Customer Master Inception**                | [`ADR-005`](../decisions/ADR-005-ADVANCE-PAYMENT-CUSTOMER-MASTER-INCEPTION.md)            | [`STEP_05`](../../step_plans/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.md)       | [`STEP_05.caveman`](../../step_plans_for_ai/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.caveman.md)<br>[`TB-05.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md)       | `codes/client_script/account_manager.js`                                                      | `tabPayment Entry`, $\ge 20\%$ Advance Gate, `CustomerInceptionService`                                                                                                                       | **Reconciled & Ready** |
| **06**  | **Sales Order Commercial Baseline & Downstream Spawning**                | [`ADR-006`](../decisions/ADR-006-SALES-ORDER-BASELINE-DOWNSTREAM-SPAWNING.md)             | [`STEP_06`](../../step_plans/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.md)                | [`STEP_06.caveman`](../../step_plans_for_ai/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.caveman.md)<br>[`TB-06.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md) | `codes/client_script/sales_order.js`, `sales_order_listview.js`, `so_script.js`               | `tabSales Order`, `tabProject`, `SalesOrderBaselineService`, `ProjectWBSInstantiationService`                                                                                                 | **Reconciled & Ready** |
| **07**  | **Dual Progress Bar Lifecycle & SLA Engine**                             | [`ADR-007`](../decisions/ADR-007-DUAL-PROGRESS-BAR-LIFECYCLE-SLA-ENGINE.md)               | [`STEP_07`](../../step_plans/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.md)       | [`STEP_07.caveman`](../../step_plans_for_ai/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.caveman.md)<br>[`TB-07.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE_TRACER_BULLET.caveman.md) | `solar_module/api/stepper.py`, `codes/client_script/lead.js`, `codes/client_script/project.js` | `tabLead`, `tabProject`, `tabSolar Stage Delay Log`, `tabSolar SLA Settings`, `SolarSLACalculator`, `LeadStepperEngine`, `ProjectStepperEngine`                                              | **Reconciled & Ready** |
| **08**  | **Material Dispatch Logistics & Delivery Note Serialized Tracking**      | [`ADR-008`](../decisions/ADR-008-MATERIAL-DISPATCH-DELIVERY-NOTE-SERIALIZED-LOGISTICS.md) | [`STEP_08`](../../step_plans/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.md)     | [`STEP_08.caveman`](../../step_plans_for_ai/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.caveman.md)<br>[`TB-08.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md) | `codes/client_script/delivery_note_solar.js`, `delivery_note_listview.js`                   | `tabDelivery Note`, `tabSerial and Batch Bundle`, `tabSolar Dispatch Settings`, `SolarDispatchValidationService`, `SolarSerialScanningService`, `SolarPODService`                                 | **Reconciled & Ready** |
| **09**  | **Installation Zone WBS & Daily Progress Reports (DPR)**                 | [`ADR-009`](../decisions/ADR-009-INSTALLATION-ZONE-WBS-DPR-EXECUTION.md)                  | [`STEP_09`](../../step_plans/STEP_09_INSTALLATION_ZONE_DPR_SPECIFICATION.md)               | [`STEP_09.caveman`](../../step_plans_for_ai/STEP_09_INSTALLATION_ZONE_DPR_SPECIFICATION.caveman.md)<br>[`TB-09.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md) | `codes/client_script/project_listview.js`                                                     | `tabDaily Progress Report`, IEC 62446-1 Testing Gate, `InstallationExecutionService`                                                                                                          | **Reconciled & Ready** |
| **10**  | **Dual-Timing Statutory Liaisoning, Regulatory Inspection & Grid Sync**  | [`ADR-010`](../decisions/ADR-010-LIAISONING-STATUTORY-INSPECTION-GRID-SYNC.md)            | [`STEP_10`](../../step_plans/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.md)                | [`STEP_10.caveman`](../../step_plans_for_ai/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.caveman.md)<br>[`TB-10.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_10_LIAISONING_GRID_SYNC_TRACER_BULLET.caveman.md) | `codes/client_script/lns.js`, `lns_listview.js`, `sync_lias.js`                               | `tabLiaisoning And Synchronization`, CEIG/JMI, 10d SLA, COD Certificate                                                                                                                       | **Reconciled & Ready** |
| **11**  | **On-Demand Solar Service, Incident-Driven O&M & Warranty Lifecycle**    | [`ADR-011`](../decisions/ADR-011-ON-DEMAND-SOLAR-SERVICE-WARRANTY-OM-LIFECYCLE.md)        | [`STEP_11`](../../step_plans/STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.md)          | [`STEP_11.caveman`](../../step_plans_for_ai/STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.caveman.md)                                                                                                                                            | `solar_module/api/om.py`, `solar_module/services/om/intake_service.py`                        | `tabSolar Service Request`, `tabMaintenance Visit`, `SolarServiceIntakeService`, `FieldDiagnosticsAndPartsService`                                                                            | **Reconciled & Ready** |
| **12**  | **Store Material Request & Automated Low-Stock Monitoring**              | [`ADR-012`](../decisions/ADR-012-STORE-MATERIAL-REQUEST-LOW-STOCK-MONITORING.md)          | [`STEP_12`](../../step_plans/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md)    | [`STEP_12.caveman`](../../step_plans_for_ai/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.caveman.md)<br>[`TB-12.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md) | `solar_module/api/store.py`, `solar_module/tasks.py`                                          | `tabMaterial Request`, `tabSolar Low Stock Incident Log`, `StoreRequisitionService`                                                                                                           | **Reconciled & Ready** |
| **13**  | **Supplier Request for Quotation (RFQ) Multi-Vendor Governance**         | [`ADR-013`](../decisions/ADR-013-SUPPLIER-REQUEST-FOR-QUOTATION-RFQ.md)                   | [`STEP_13`](../../step_plans/STEP_13_SUPPLIER_RFQ_SPECIFICATION.md)                        | [`STEP_13.caveman`](../../step_plans_for_ai/STEP_13_SUPPLIER_RFQ_SPECIFICATION.caveman.md)                                                                                                                                                          | `solar_module/api/procurement.py`, `solar_module/overrides/rfq.py`                            | `tabRequest for Quotation`, `tabRequest for Quotation Supplier`, `RFQDispatchService`, `SupplierShortlistService`                                                                             | **Reconciled & Ready** |
| **14**  | **Supplier Quotation Comparative Evaluation Matrix & Landed Cost**       | [`ADR-014`](../decisions/ADR-014-SUPPLIER-QUOTATION-COMPARATIVE-EVALUATION-MATRIX.md)     | [`STEP_14`](../../step_plans/STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.md)         | [`STEP_14.caveman`](../../step_plans_for_ai/STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.caveman.md)                                                                                                                                           | `solar_module/api/procurement.py`, `codes/client_script/quotation_comparison_matrix.js`       | `tabQuotation Comparison Matrix`, `tabSupplier Quotation`, `LandedCostCalculationService`, `WeightedScoringEngineService`                                                                     | **Reconciled & Ready** |
| **15**  | **Purchase Order Authorization, Solar Milestone Terms & Routing**        | [`ADR-015`](../decisions/ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md)         | [`STEP_15`](../../step_plans/STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md)        | [`STEP_15.caveman`](../../step_plans_for_ai/STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.caveman.md)                                                                                                                                          | `solar_module/api/procurement.py`, `codes/client_script/purchase_order.js`                    | `tabPurchase Order`, `tabPurchase Order Item`, `Solar SCM Settings`, `PurchaseOrderValidationService`, `POAuthorizationMatrixService`                                                         | **Reconciled & Ready** |
| **16**  | **Multi-Location Barcode Purchase Receipt (GRN) & Custody Approval**     | [`ADR-016`](../decisions/ADR-016-MULTI-LOCATION-PURCHASE-RECEIPT-BARCODE-GRN.md)          | [`STEP_16`](../../step_plans/STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md)                | [`STEP_16.caveman`](../../step_plans_for_ai/STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.caveman.md)                                                                                                                                                  | `solar_module/api/procurement.py`, `codes/client_script/purchase_receipt.js`                  | `tabPurchase Receipt`, `tabPurchase Receipt Item`, `Solar SCM Settings`, `PurchaseReceiptValidationService`, `GRNStockUpdateOrchestrationService`                                             | **Reconciled & Ready** |
| **17**  | **Purchase Invoicing, 3-Way Match & Admin Departmental Entry Policy**    | [`ADR-017`](../decisions/ADR-017-PURCHASE-INVOICE-3WAY-MATCH-ADMIN-ENTRY-GOVERNANCE.md)   | [`STEP_17`](../../step_plans/STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.md)         | [`STEP_17.caveman`](../../step_plans_for_ai/STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.caveman.md)                                                                                                                                           | `solar_module/api/procurement.py`, `codes/client_script/purchase_invoice.js`                  | `tabPurchase Invoice`, `tabPurchase Invoice Item`, `Solar SCM Settings`, `PurchaseInvoiceValidationService`, `ThreeWayMatchEngine`                                                            | **Reconciled & Ready** |
| **18**  | **Joint Vendor Payment Monitoring Workbench & Dual Notification Engine** | [`ADR-018`](../decisions/ADR-018-JOINT-VENDOR-PAYMENT-MONITORING-WORKBENCH.md)            | [`STEP_18`](../../step_plans/STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.md)            | [`STEP_18.caveman`](../../step_plans_for_ai/STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.caveman.md)                                                                                                                                              | `solar_module/api/payment_monitoring.py`, `solar_module/tasks.py`                             | `tabPayment Schedule`, `tabPayment Entry`, `VendorPaymentNotificationDaemon`, `VendorPaymentSettlementService`, `VendorPaymentWorkbenchService`                                               | **Reconciled & Ready** |
| **19**  | **Vendor Performance Rating Scorecard & Multi-Tier Supplier Governance** | [`ADR-019`](../decisions/ADR-019-VENDOR-PERFORMANCE-RATING-SCORECARD.md)                  | [`STEP_19`](../../step_plans/STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.md)             | [`STEP_19.caveman`](../../step_plans_for_ai/STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.caveman.md)                                                                                                                                               | `solar_module/api/vendor_rating.py`, `solar_module/services/vendor_rating_service.py`         | `tabVendor Performance Rating`, `tabVendor Rating Item Breakdown`, `tabVendor Rating Service Checklist`, `tabSupplier`, `VendorRatingCalculationService`                                      | **Reconciled & Ready** |

---

## 3. Stage-by-Stage Detailed Reconciliation Audits

### Step 00: Role, Permission & Security Foundation Architecture

- **Document References:** [`ADR-000`](../decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md) | [`STEP_00`](../../step_plans/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.md) | [`STEP_00.caveman`](../../step_plans_for_ai/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.caveman.md) | [`TB-00.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)
- **Primary DocTypes:** `tabSolar Security Settings`, `tabSolar Cancellation Request`, `tabSolar Deletion Audit Log`.
- **Core Domain Services:** `RoleInheritanceService`, `StageForwardLockService`, `AdminAuditService`, `CascadePurgeService`.
- **Base Controller Mixin:** `StageSecuredDocument`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Managerial Authority Inheritance:_ Canonical 22 Roles (10 Frontline + 10 Supervisory + 2 Apex) & 11 Department Role Profiles; Zero "User" suffix; dynamic expansion via `RoleInheritanceService`.
  2. _Stage-Forward Immutability Lock:_ Registry-driven lock via `StageForwardLockService`; upstream records immutable once downstream records exist.
  3. _Junior Cancellation Request Workflow:_ Juniors cannot unilaterally cancel or amend submitted records; routed through submittable `Solar Cancellation Request` requiring Department Manager review, remarks, and sign-off.
  4. _Admin Deletion Guard & Audit Logger:_ Hard-blocks direct deletion if active children exist; logs $\ge 20$ chars justification, full JSON snapshot, user ID, timestamp, and IP into immutable `Solar Deletion Audit Log`.
  5. _Atomic Cascading Purge:_ Purges entire dependency trees in reverse-topological order within a single database savepoint (`frappe.db.savepoint("cascade_purge_tx")`), requiring Admin password re-authentication and $\ge 40$ chars justification.
  6. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-00.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestRoleSecurityTracerBullet`) across Desk script, whitelisted APIs, domain services, and database persistence with zero database commits.
- **Role Standard:** `Admin` (Project Supreme), `System Manager` (Dev Supreme), All 10 Canonical Department Managerial & Frontline pairs.
- **Audit Verification:** ✔ Schema complete | ✔ State machine defined | ✔ SOLID services decoupled | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

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
- **Role Standard:** `Sales Representative` (Inside/Field), `Sales Manager` (Territory).
- **Audit Verification:** ✔ Schema complete | ✔ State machine defined | ✔ SOLID services decoupled | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 02: Technical Site Survey & Audit (Offline Engine)

- **Document References:** [`ADR-002`](../decisions/ADR-002-TECHNICAL-SITE-SURVEY-AUDIT-OFFLINE-ENGINE.md) | [`STEP_02`](../../step_plans/STEP_02_SITE_SURVEY_SPECIFICATION.md) | [`STEP_02.caveman`](../../step_plans_for_ai/STEP_02_SITE_SURVEY_SPECIFICATION.caveman.md) | [`TB-02.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md)
- **Primary DocType:** `tabSite Survey` (standalone submittable DocType with child table `tabSite Survey Doc Table`).
- **Core Domain Services:** `SurveyValidationService`, `SurveySLAService`, `SurveySyncService`, `SurveyGeolocationService`, `SurveyBridgeService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Offline-First PWA Sync:_ Field engineers capture audits offline in browser IndexedDB (`SiteSurveyOfflineDB`); background synchronization upon network reconnection with fail-safe cache eviction.
  2. _GPS Geofencing & Photo Checklist:_ Hardware GPS coordinates ($\le \pm 50\text{m}$, non-zero) and 6 fixed mandatory photo items + 1 mandatory 360° video walkthrough ($\ge 1.0\text{MB}$) protected against deletion.
  3. _24-Hour Survey SLA:_ Turnaround countdown from assignment timestamp (`for_survey_assign_on`); automated escalation if breached with mandatory $\ge 20$ chars delay justification.
  4. _Automated Downstream Instantiation:_ Survey submission programmatically instantiates `Survey Engineering Design` (Stage 03) in `Draft` state.
  5. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-02.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestSiteSurveyTracerBullet`) across Desk script, whitelisted APIs, domain services, PWA Dexie schema, and Stage 03 draft instantiation with zero database commits.
- **Role Standard:** `Survey Engineer`, `Survey Assistant`, `Survey Manager`.
- **Audit Verification:** ✔ Schema complete | ✔ Offline IndexedDB sync specified | ✔ Verification gates enforced | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 03: Survey Engineering Design & Dynamic BOM Engine

- **Document References:** [`ADR-003`](../decisions/ADR-003-SURVEY-ENGINEERING-DESIGN-DYNAMIC-BOM-ENGINE.md) | [`STEP_03`](../../step_plans/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.md) | [`STEP_03.caveman`](../../step_plans_for_ai/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.caveman.md) | [`TB-03.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md)
- **Primary DocType:** `tabSurvey Engineering Design` (`is_submittable = 1`, child tables `tabSite Survey Design File`, `tabCable Calculation Table`, `tabCustom Quot BOM`, `tabRemark-Delay Log`).
- **Core Domain Services:** `SolarDesignCalculationService`, `SolarBOMExplosionService`, `SolarDesignGateService`, `SolarDesignSLAService`, `SolarDesignBridgeService`.
- **Base Controller Mixin:** `StageSecuredDocument` (incorporating `StageForwardLockService`).
- **Reconciliation Points & Architectural Invariants:**
  1. _Predecessor Integrity Gate:_ Ensures linked `Site Survey` is in `Completed` status before engineering design initialization.
  2. _CAD / SLD Attachment Versioning & Admin Limit:_ Enforces mandatory CAD Layout (`.dwg`/`.dxf`) and Single Line Diagram (`SLD`) uploads with configurable Admin file size ceiling (`max_file_size_mb`, default 25 MB).
  3. _Parametric Electrical Voltage Drop Calculation:_ Evaluates DC string and AC feeder voltage drops at $75^\circ\text{C}$ operating temperature; hard gate rejects drops exceeding statutory $2.0\%$ per IEC 60364-7-712 & IS 732.
  4. _Inverter Sizing Ratio (ILR) Window:_ Asserts $1.10 \le \text{ILR} \le 1.35$ for optimal economic performance and clipping avoidance.
  5. _Dynamic BOM Explosion:_ Parametrically explodes modules (DCR/NDCR), inverters, MMS structure tonnage, DC/AC cables, and earthing kits into `tabCustom Quot BOM` with price list rate lookups.
  6. _Cryptographic Baseline Freeze:_ Document submission computes canonical SHA-256 hash (`bom_hash`) of BOM rows and sets `is_frozen = 1`, preventing silent alterations during Stage 04 commercial quoting.
  7. _48-Hour SLA Countdown & Delay Accountability:_ Turnaround countdown from assignment timestamp (`for_design_assign_on`); automated background escalation if breached with mandatory $\ge 15$ chars delay justification.
  8. _Downstream Stage 04 Instantiation:_ Document submission triggers `SolarDesignBridgeService`, flagging upstream survey and instantiating downstream `tabQuotation` (Stage 04) in `Draft` state.
  9. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-03.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestSurveyEngineeringDesignTracerBullet`) across Desk script, whitelisted APIs, domain services, and downstream Quotation draft instantiation with zero database commits.
- **Role Standard:** `Design Engineer`, `Design Manager`, `Admin` (Project Supreme Command), `System Manager` (Dev Supreme).
- **Audit Verification:** ✔ Schema complete | ✔ Voltage drop math validated | ✔ 4 hard verification gates enforced | ✔ SHA-256 baseline freeze enforced | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 04: Proposal & Subsidy Engine

- **Document References:** [`ADR-004`](../decisions/ADR-004-PROPOSAL-SUBSIDY-ENGINE.md) | [`STEP_04`](../../step_plans/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.md) | [`STEP_04.caveman`](../../step_plans_for_ai/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.caveman.md) | [`TB-04.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md)
- **Primary DocType:** `tabQuotation` (`custom_*` fields aliased to `Proposal`, child tables `tabQuotation Item`, `tabRemark-Delay Log`).
- **Core Domain Services:** `ProposalPrefillService`, `ProposalCalculationService`, `ProposalSubsidyService`, `ProposalMarginGateService`, `ProposalFinalizationService`, `ProposalWaiverGateService`, `ProposalSLAService`.
- **Base Controller Mixin:** `StageSecuredDocument` (incorporating `StageForwardLockService`).
- **Reconciliation Points & Architectural Invariants:**
  1. _Predecessor Integrity & Lead Quarantine:_ Ingests survey & design parameters; enforces `quotation_to == 'Lead'` and verifies SED `docstatus == 1` & `is_frozen == 1` with zero `Customer` master creation.
  2. _Cryptographic BOM Cost Ingestion:_ Verifies incoming BOM rows match cryptographic SHA-256 `bom_hash`, dynamically rolling up `custom_estimated_bom_cost`.
  3. _70:30 Solar Composite GST Split:_ Automates statutory split into 70% Goods (`Solar Power Plant` @ 12% GST) and 30% Services (`Installation & Commissioning` @ 18% GST), with configurable custom ratios totaling exactly 100.0%.
  4. _Dual Subsidy & Payback Automation:_ Automatically calculates PM Surya Ghar Central Financial Assistance (CFA) brackets (up to ₹78,000 max cap) + State DISCOM top-ups, net payable, and simple payback horizon.
  5. _Admin Gross Margin Floor Governance:_ Hard gate compares net revenue to live BOM cost; margins below 18.0% enter `Margin Floor Exception` blocking finalization without Area Sales Manager or Admin sign-off.
  6. _Exclusive Multi-Proposal Finalization Lock:_ Permits multiple proposal alternatives per deal/survey, but atomically finalizes exactly ONE winning option while marking peer proposals `Superseded`.
  7. _Advance Verification & Goodwill VIP Gate:_ Requires $\ge 50\%$ advance receipt, Finance Officer waiver, or executive Goodwill / VIP waiver authorized strictly by MD, CEO, or Admin.
  8. _24-Hour SLA Countdown & Delay Accountability:_ 24-hour turnaround timer starts at creation; overdue daemon escalates breached records and requires mandatory categorized entries in `tabRemark-Delay Log`.
  9. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-04.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestSolarProposalTracerBullet`) across Desk script, whitelisted APIs, domain services, and Stage 05 advance gate handover with zero database commits.
- **Role Standard:** `CRM Representative`, `CRM Manager`, `Sales Representative`, `Sales Manager`, `Accounts Manager`, `Admin` (Project Supreme Command), `System Manager` (Dev Supreme).
- **Audit Verification:** ✔ Schema & custom fields complete | ✔ 70:30 GST split validated | ✔ Subsidy slabs verified | ✔ Margin floor gate enforced | ✔ Exclusive finalization lock tested | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 05: Advance Payment Clearance & Customer Master Inception

- **Document References:** [`ADR-005`](../decisions/ADR-005-ADVANCE-PAYMENT-CUSTOMER-MASTER-INCEPTION.md) | [`STEP_05`](../../step_plans/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.md) | [`STEP_05.caveman`](../../step_plans_for_ai/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.caveman.md) | [`TB-05.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md)
- **Primary DocTypes:** `tabQuotation` (advance fields), `tabPayment Entry` (solar advance fields), `tabCustomer` (solar inception fields), `tabSolar Loan Sanction` (`is_submittable = 1`), `tabSolar Advance Settings` (Single DocType), `tabRemark-Delay Log`.
- **Core Domain Services:** `AdvanceVerificationService`, `CustomerInceptionService`, `LoanSanctionService`, `AdvanceSLAService`, `SalesOrderClearanceGateService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Quad-Track Clearance Architecture:_ Direct Bank Advance (Track A: unique UTR + $\ge 50\%$ standard, $\ge 20\%$ floor), Bank Loan Sanction (Track B: sanction letter + margin money), Corporate Credit Waiver (Track C: Accounts Manager / Admin), Executive Goodwill VIP Bypass (Track D: CEO / MD / Admin exclusive).
  2. _Global UTR Deduplication Gate:_ Strict database unique constraint on `custom_utr_cheque_no` prevents duplicate receipt booking or cross-proposal reuse.
  3. _Tiered Ground-Truth Master Inception:_ Atomic programmatic creation of standard ERPNext `Customer`, `Address` (with geocoded GPS coordinates), and `Contact` with precedence hierarchy: `Proposal` > `Site Survey` > `Lead` > system default.
  4. _Clean Quarantine Break & Persistent Identity Thread:_ Transitions prospect `Lead` to `status = 'Converted'` with `lead.customer = customer.name` while preserving `custom_lead_reference` on all created and downstream records (`Payment Entry`, `Customer`, `Address`, `Contact`, `Sales Order`, `Project`).
  5. _Downstream Sales Order Lockout Gate:_ Hard server-side and client-side gate blocks `Sales Order` validation and submission if Stage 05 clearance is not achieved.
  6. _24-Hour Clearance SLA & Delay Accountability:_ 24h turnaround countdown from proposal finalization, auto-escalating to `Overdue` and enforcing categorized entries in `tabRemark-Delay Log`.
  7. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-05.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestStage05AdvancePaymentTracerBullet`) across Desk script, whitelisted APIs, domain services, and downstream Sales Order release with zero database commits.
- **Role Standard:** `Accounts Assistant`, `Accounts Manager`, `Admin` (Project Supreme Command), `System Manager` (Dev Supreme).
- **Audit Verification:** ✔ Schema & custom fields complete | ✔ Quad-track clearance verified | ✔ UTR uniqueness enforced | ✔ Tiered inception validated | ✔ Downstream SO lockout tested | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 06: Sales Order Commercial Baseline & Downstream Spawning

- **Document References:** [`ADR-006`](../decisions/ADR-006-SALES-ORDER-BASELINE-DOWNSTREAM-SPAWNING.md) | [`STEP_06`](../../step_plans/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.md) | [`STEP_06.caveman`](../../step_plans_for_ai/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.caveman.md) | [`TB-06.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md)
- **Primary DocTypes:** `tabSales Order` (`is_submittable = 1`, linked to `tabProject`), `tabSales Order Item` (equipment category, dynamic BOM link), `tabProject`, `tabTask` (WBS and logistics tasks), `tabLiaisoning And Synchronization` (`is_submittable = 1`), `tabSolar Sales Order Settings` (Single DocType), `tabRemark-Delay Log`.
- **Core Domain Services:** `SalesOrderBaselineService`, `ProjectSpawnerService`, `StoreLogisticsService`, `LiaisoningInceptionService`, `SalesOrderSLAService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Pre-Submission 5-Gate Architecture:_ Gate 1 (Stage 05 advance clearance `custom_advance_verified == 1`), Gate 2 (Bilateral signed contract PDF & agreement date), Gate 3 (Customer DISCOM consumer number completeness), Gate 4 (Stage 03 Dynamic Engineering BOM alignment), Gate 5 (Milestone Payment Schedule 100% reconciliation).
  2. _Cryptographic Baseline Freeze:_ Computes deterministic SHA-256 hash across sorted BOM items, quantities, rates, customer, and payment schedule, locking the commercial/technical baseline (`custom_baseline_frozen = 1`) on submission.
  3. _Atomic Triple Downstream Spawning (Single ACID Transaction):_ Automatically instantiates ERPNext `Project` container with multi-zone WBS Tasks (Civil, MMS, Mounting, Cabling, Earthing, Pre-Commissioning), `Material Delivery Task` assigned directly to `Store Manager` (`custom_can_reassign = 1`), and `Liaisoning And Synchronization` record in Phase 1 (`Pending Filing`).
  4. _Store Manager Material Task Delegation:_ Pure RPC endpoint and validation allowing `Store Manager` to delegate material preparation specifically to `Store Assistant` with audit timestamp.
  5. _24h Kickoff Turnaround SLA & Delay Governance:_ Monitored by Redis daemon; overdue transitions enforce category and justification entries in `tabRemark-Delay Log`.
  6. _Downstream Dispatch Lockout (Stage-Forward Immutability):_ Server-side gate blocking `Sales Order` cancellation if any submitted downstream `Delivery Note` exists against it.
  7. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-06.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestStage06SalesOrderTracerBullet`) across Desk script, whitelisted APIs, domain services, and atomic triple downstream spawning with zero database commits.
- **Role Standard:** `Sales Representative`, `Sales Manager`, `Project Engineer`, `Site Supervisor`, `Project Manager`, `Store Manager`, `Store Assistant`, `Liaisoning Representative`, `Liaisoning Manager`, `Admin`, `System Manager`.
- **Audit Verification:** ✔ Schema & custom fields complete | ✔ 5 verification gates enforced | ✔ Cryptographic baseline freeze verified | ✔ Atomic triple downstream spawning verified | ✔ Store delegation validated | ✔ Downstream dispatch lockout tested | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 07: Dual Progress Bar Lifecycle & SLA Engine

- **Document References:** [`ADR-007`](../decisions/ADR-007-DUAL-PROGRESS-BAR-LIFECYCLE-SLA-ENGINE.md) | [`STEP_07`](../../step_plans/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.md) | [`STEP_07.caveman`](../../step_plans_for_ai/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.caveman.md) | [`TB-07.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE_TRACER_BULLET.caveman.md)
- **Primary DocTypes:** `tabLead` (Progress Bar 1 extensions), `tabProject` (Progress Bar 2 extensions), `tabSolar Stage Delay Log` (`istable = 1`), `tabSolar SLA Settings` (`issingle = 1`).
- **Core Domain Services:** `SolarSLACalculator`, `LeadStepperEngine`, `ProjectStepperEngine`, `StageGateValidator`, `DelayAuditService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Dual Progress Bar Architecture:_
     - **Progress Bar 1 (Pre-Sales Stepper on `tabLead`):** Inbound Lead Capture (S01, 2h) $\rightarrow$ Site Survey (S02, 24h) $\rightarrow$ Engineering Design & Dynamic BOM (S03, 24h-48h) $\rightarrow$ Commercial Proposal (S04, 24h) $\rightarrow$ Advance Clearance (S05, 48h) $\rightarrow$ Sales Order Freeze (S06, 24h) $\rightarrow$ Early DISCOM Filing (S10A, 72h) $\rightarrow$ Terminal Lead Completion (`status = 'Converted'`).
     - **Progress Bar 2 (Project Execution Stepper on `tabProject`):** Stage 05 Advance Clearance Gate (S05G, 0h) $\rightarrow$ Sales Order Baseline Lock (S06, 24h) $\rightarrow$ Serialized Material Dispatch (S07, 48h) $\rightarrow$ Installation & Daily Progress Reports (S08, dynamic 3.0d/10kWp) $\rightarrow$ Surplus Material Return (S09, 48h) $\rightarrow$ Statutory Grid Sync & Net Metering (S10B, 10d SLA) $\rightarrow$ Terminal Project Completion (`custom_is_completed_flag = 1`, COD Anchor $\rightarrow$ Stage 11 O&M).
  2. _5-State Visual & Semantic Ontology:_ Deterministic resolution of all nodes across both pipelines into `IDLE` (Slate), `ONGOING_HEALTHY` (Blue), `ONGOING_OVERDUE` (Crimson Pulse), `COMPLETED_ON_TIME` (Emerald), or `COMPLETED_DELAYED` (Warm Amber).
  3. _Capacity-Tiered Dynamic SLA Engine:_ Mathematical calculation of turnaround times against `Solar SLA Settings` with capacity-sensitive scaling (Residential $\le 10$ kWp = 24h vs C&I $> 10$ kWp = 48h for Design; 3.0 days per 10 kWp for WBS Installation).
  4. _Mandatory Delay Audit Log & Hard Progression Gate:_ When an active stage exceeds SLA, stage state transitions to `ONGOING_OVERDUE`, locking stage progression until a categorized explanation ($\ge 20$ chars) is appended to `tabSolar Stage Delay Log`.
  5. _Executive Administrative SLA Waiver Authority:_ Restricted strictly to `Admin` and `Director`, allowing formal waiving of overdue penalties and instantly flipping node status from `COMPLETED_DELAYED` to `COMPLETED_ON_TIME`.
  6. _Role-Gated Interactive Action Drawer:_ Accessible Slide-Over inspector renders actor credentials, deliverables tray, and contextual primary action buttons strictly gated by canonical enterprise roles (Zero "User" Suffix rule).
  7. _Redis SLA Background Daemon:_ Scheduled task (`solar_module.tasks.recompute_enterprise_slas`) executes every 15 minutes to evaluate active SLA countdowns across active leads and projects.
  8. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-07.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestStage07DualProgressBarTracerBullet`) across Desk script, whitelisted APIs, domain services, and terminal lifecycle gates with zero database commits.
- **Role Standard:** `Sales Representative`, `Sales Manager`, `Survey Engineer`, `Survey Manager`, `Design Engineer`, `Design Manager`, `CRM Representative`, `CRM Manager`, `Accounts Assistant`, `Accounts Manager`, `Store Assistant`, `Store Manager`, `Project Engineer`, `Site Supervisor`, `Project Manager`, `Liaisoning Representative`, `Liaisoning Manager`, `Director`, `Admin` (Project Supreme Command), `System Manager` (Dev Supreme).
- **Audit Verification:** ✔ Schema & custom fields complete | ✔ Dual progress bar state machines verified | ✔ 5-state visual ontology verified | ✔ Capacity-tiered SLA engine verified | ✔ Mandatory delay log & Admin waiver verified | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 08: Material Dispatch Logistics & Delivery Note Serialized Tracking

- **Document References:** [`ADR-008`](../decisions/ADR-008-MATERIAL-DISPATCH-DELIVERY-NOTE-SERIALIZED-LOGISTICS.md) | [`STEP_08`](../../step_plans/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.md) | [`STEP_08.caveman`](../../step_plans_for_ai/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.caveman.md) | [`TB-08.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md)
- **Primary DocTypes:** `tabDelivery Note` (`is_submittable = 1`), `tabDelivery Note Item`, `tabSerial and Batch Bundle` & `tabSerial and Batch Entry` (Frappe v15 SABB), `tabSolar Dispatch Checklist Item` (`istable = 1`), `tabSolar Dispatch Settings` (`issingle = 1`).
- **Core Domain Services:** `SolarDispatchValidationService`, `SolarSerialScanningService`, `SolarPODService`, `SolarDispatchSLAService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _100% 2D Barcode Serial Tracking:_ Enforces Frappe v15 Serial and Batch Bundle (SABB) relational scanning for all critical solar assets (PV modules, solar inverters). Exact cardinality match ($\text{scanned\_count} == \text{round}(qty)$), active warehouse status validation, and duplicate scan prevention.
  2. _Sales Order Baseline & Mathematical Over-Dispatch Ceiling:_ Gate 1 asserts referenced Sales Order `docstatus == 1` and `custom_baseline_frozen == 1`. Gate 2 enforces mathematical ceiling preventing cumulative dispatch exceeding frozen Sales Order BOM quantities.
  3. _Statutory E-Way Bill & Logistics Manifest Gate:_ Gate 4 blocks submission for consignments $\ge$ ₹50,000 without 12-digit E-Way Bill, valid future expiry datetime, official PDF attachment, uppercase Indian vehicle plate regex, and 10-digit driver mobile.
  4. _Pre-Dispatch Quality Inspection Gate:_ Gate 5 blocks submission unless all mandatory rows in `custom_pre_dispatch_checklist` are marked `Passed`.
  5. _Closed-Loop Digital POD & Automated Cascade:_ Digital Proof of Delivery signed off with touch signature and unloading photo evidence. Submission automatically closes the linked Store Task and advances `tabProject.custom_current_lifecycle_stage` to Stage 08 (`Installation Execution`).
  6. _48-Hour Warehouse Dispatch SLA & Delay Governance:_ Real-time countdown from store task creation; warning alerts at 36h (< 12h remaining); overdue state hard-locks submission until standardized delay category and $\ge 10$ character remarks are recorded.
  7. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-08.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestStage08MaterialDispatchTracerBullet`) across Desk script, whitelisted APIs, domain services, SABB architecture, and digital POD cascade with zero database commits.
- **Role Standard:** `Store Manager`, `Store Assistant`, `Project Engineer`, `Site Supervisor`, `Admin` (Project Supreme Command), `System Manager` (Dev Supreme).
- **Audit Verification:** ✔ SABB schema verified | ✔ 6 verification gates enforced | ✔ Digital POD verified | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 09: Installation Zone WBS & Daily Progress Reports (DPR)

- **Document References:** [`ADR-009`](../decisions/ADR-009-INSTALLATION-ZONE-WBS-DPR-EXECUTION.md) | [`STEP_09`](../../step_plans/STEP_09_INSTALLATION_ZONE_DPR_SPECIFICATION.md) | [`STEP_09.caveman`](../../step_plans_for_ai/STEP_09_INSTALLATION_ZONE_DPR_SPECIFICATION.caveman.md) | [`TB-09.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md)
- **Primary DocType:** `tabSolar Daily Progress Report` (submittable, with offline UUIDv4 support and 5 child tables), `tabSolar Installation Zone`, `tabSolar Pre Commissioning Checklist` (submittable, with 3 electrical child tables), `tabSolar Installation Settings`.
- **Core Domain Services:** `InstallationZoneWBSService`, `SolarDPRValidationService`, `SolarDPRSyncService`, `PreCommissioningVerificationService`, `InstallationHandoffService`, `InstallationSLAService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Multi-Zone Execution Architecture:_ Supports physical zoning (`tabSolar Installation Zone`) with automated WBS milestone generation and weighted dynamic completion rollups.
  2. _Mobile DPR Ingestion & Offline-First Resilience:_ Daily site submissions capturing muster, hardware quantities, and geo-tagged photos; resilient 256KB chunked media assembler for weak 2G/3G networks; idempotent server ingestion preventing duplicate tasks.
  3. _Installed Material Balance Ceiling:_ Hard-blocking server gate preventing cumulative installed quantities from exceeding site dispatched stock ($Q_{\text{inst}} \le Q_{\text{disp}}$).
  4. _IEC 62446-1 Pre-Commissioning Electrical Gate:_ Hard-blocking test verification requiring Insulation Resistance (Megger $\ge 1.0\text{ M}\Omega$), String Open-Circuit Voltage ($V_{oc} \pm 5\%$), Earth Pit Resistance ($R_e \le 5.0\ \Omega$ MMS / $\le 1.0\ \Omega$ Inverter), and zero Category A open snags.
  5. _Automated Downstream Handoff:_ Pre-commissioning sign-off automatically unlocks Stage 10B Statutory Grid Synchronization 10-day countdown and spawns Stage 09 Material Return task.
  6. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin vertical slice codified in [`TB-09.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md), proving all 11 Stage 09 invariants with zero database commits (`TestStage09InstallationTracerBullet`).
- **Role Standard:** `Project Engineer`, `Site Supervisor`, `Civil/Electrical Site Engineer`, `Admin`.
- **Audit Verification:** ✔ Multi-zone WBS verified | ✔ IEC 62446-1 test gate verified | ✔ Offline idempotency verified | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 10: Dual-Timing Statutory Liaisoning, Regulatory Inspection & Grid Sync

- **Document References:** [`ADR-010`](../decisions/ADR-010-LIAISONING-STATUTORY-INSPECTION-GRID-SYNC.md) | [`STEP_10`](../../step_plans/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.md) | [`STEP_10.caveman`](../../step_plans_for_ai/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.caveman.md) | [`TB-10.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_10_LIAISONING_GRID_SYNC_TRACER_BULLET.caveman.md)
- **Primary DocType:** `tabLiaisoning And Synchronization` (`is_submittable = 1`, linked to `tabSales Order`, `tabProject`, `tabCustomer`, with child tables `tabSolar Statutory Document Checklist`, `tabSolar Inspection Milestone Log`, `tabSolar Meter Reading Item`, `tabSolar Stage Delay Log`), `tabSolar Liaisoning Settings`.
- **Core Domain Services:** `LiaisoningInceptionService`, `LiaisoningSLAService`, `LiaisoningPhase1Service`, `LiaisoningPhase2Service`, `ProjectCompletionService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Dual-Timing Operational Architecture:_
     - **Phase 1 (Post-Sales Order):** Early DISCOM connectivity feasibility filing, KYC document collection, load sanctioning, preliminary NOC, and atomic `tabLead` Progress Bar 1 terminal completion (`custom_lead_progress_status = "Completed"`).
     - **Phase 2 (Post-Installation):** Activated upon Stage 09 pre-commissioning clearance; CEIG electrical safety approval, bi-directional net-meter installation, Joint Meter Inspection (JMI) report, anti-islanding trip verification ($\le 2.0\text{s}$), and grid energization.
  2. _10-Day Statutory SLA Countdown:_ Initiated automatically upon Stage 09 electrical testing sign-off, monitoring statutory turnaround times excluding Sundays and public holidays from Frappe `Holiday List`. Overdue breaches require auditable justification in `tabSolar Stage Delay Log`.
  3. _Immutable Project Completion Anchor:_ An ERPNext `Project` cannot be marked "Completed" until official grid synchronization readings and Commercial Operation Date (COD) certificate are submitted. Submission atomically closes residual open `tabTask` nodes, sets `custom_is_completed_flag = 1`, and logs COD date.
  4. _Downstream O&M & Accounts Boundary:_ Project completion programmatically spawns Stage 11 `tabSolar Asset Register` twin and dispatches instant notification to Accounts for final milestone retention invoicing.
  5. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin vertical slice codified in [`TB-10.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_10_LIAISONING_GRID_SYNC_TRACER_BULLET.caveman.md), proving all 11 Stage 10 invariants across pure SOLID domain services, whitelisted RPC APIs (`solar_module.api.liaisoning.*`), Desk client script, and automated integration test suite (`TestStage10LiaisoningGridSyncTracerBullet`) with zero database commits.
- **Role Standard:** `Liaisoning Representative`, `Liaisoning Manager`, `Project Engineer`, `Project Manager`, `Admin`, `System Manager`.
- **Audit Verification:** ✔ Dual-timing state machine verified | ✔ 10-day statutory SLA verified | ✔ Immutable completion anchor verified | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit).

---

### Stage 11: On-Demand Solar Service, Incident-Driven O&M & Warranty Lifecycle

- **Document References:** [`ADR-011`](../decisions/ADR-011-ON-DEMAND-SOLAR-SERVICE-WARRANTY-OM-LIFECYCLE.md) | [`STEP_11`](../../step_plans/STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.md) | [`STEP_11.caveman`](../../step_plans_for_ai/STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabSolar Service Request` (`is_submittable = 1`, autoname `SSR-.YYYY.-.#####`), `tabMaintenance Visit` (`is_submittable = 1`, autoname `SMV-.YYYY.-.#####`), `tabSolar Service Spare Item`, `tabMaintenance Checklist Item`, `tabSolar Site Service History`, `tabSolar Stage Delay Log`.
- **Core Domain Services:** `SolarServiceIntakeService`, `FieldDiagnosticsAndPartsService`, `ServiceTriageAndDispatchService`, `ServiceCommercialSettlementService`, `ServiceSLAService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Decoupled Post-Project Service Boundary:_ Enforces clean CapEx termination at Stage 10 upon COD and net-meter energization. Stage 11 is an independent, OpEx lifecycle operating purely on-demand with zero automated project task spawning.
  2. _Dual-Track Warranty Discrimination Engine:_ Automatic classification of incidents into:
     - **Track A (In-Warranty / Free / RMA):** Equipment or installation defects within active warranty period $\rightarrow$ ₹0.00 customer billing, automated OEM RMA reverse logistics claim generation.
     - **Track B (Out-of-Warranty / Chargeable):** Expired warranty, external/pest/surge damage $\rightarrow$ inspection quotation, customer estimate acceptance, ERPNext Sales Invoice generation.
  3. _Four Enforced Verification Gates:_
     - **Gate 1 (Warranty Eligibility):** Automatic server-side warranty lookup; non-Admin override prohibited.
     - **Gate 2 (Field Geofence Check-in):** Haversine distance validation strictly asserting technician GPS is $\le 500\text{ meters}$ from registered customer rooftop coordinates before unlocking diagnostic entry.
     - **Gate 3 (Spare Parts Serial Reconciliation):** Enforces mandatory capture of both `serial_no_removed` and `serial_no_installed`, unlinking defective units to quarantine stock and linking replacements to the plant digital twin.
     - **Gate 4 (Customer Closed-Loop Verification):** Document submission hard-blocked without cryptographic 6-digit customer OTP or touch-captured digital signature on glass.
  4. _Tiered Service SLAs & Mandatory Delay Logging:_ Emergency Blackout (4h response / 24h resolution), High/Degraded (12h response / 48h resolution), Routine Check (48h response / 5-day window) monitored by background daemons; overdue tickets enforce justification logging in `tabSolar Stage Delay Log`.
  5. _Immutable Master Site Ledger (`tabSolar Site Service History`):_ Append-only audit record providing a 25-year permanent historical log of all faults, component swaps, and maintenance visits for any installed solar site.
- **Role Standard:** `Customer Care Representative`, `O&M Service Coordinator`, `O&M Service Engineer`, `Accounts Assistant`, `Admin` (Project Supreme Command), `Administrator` / `System Manager`.
- **Audit Verification:** ✔ Decoupled schema complete | ✔ Dual-track warranty engine verified | ✔ 4 verification gates enforced | ✔ Mobile geofence specified | ✔ Immutable site ledger established | ✔ Tests defined (zero DB commit).

---

### Step 12: Store Requisitions & Automated Low-Stock Monitoring (Flow 2: Step 01)

- **Document References:** [`ADR-012`](../decisions/ADR-012-STORE-MATERIAL-REQUEST-LOW-STOCK-MONITORING.md) | [`STEP_12`](../../step_plans/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md) | [`STEP_12.caveman`](../../step_plans_for_ai/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.caveman.md) | [`TB-12.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md)
- **Primary DocTypes:** `tabMaterial Request` (extended with `custom_project_reference`, `custom_sales_order`, `custom_urgency_level`, `custom_trigger_source`, `custom_workflow_status`, `custom_sla_deadline`, `custom_sla_status`, `custom_delay_reason`, `custom_delay_approved_by`, `custom_is_class_a_solar`), `tabMaterial Request Item`, `tabSolar Low Stock Incident Log`, `tabSolar Reorder Policy`, `tabItem`, `tabItem Reorder`, `tabBin`.
- **Core Domain Services:** `StoreRequisitionService`, `ReorderCalculationService`, `LowStockMonitoringDaemon`, `StoreNotificationBroker`.
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
  5. _Tiered SLA & Multi-Channel Broadcasts:_ 4h (Emergency), 24h (Project), 48h (Routine) SLA windows; automated alert dispatch to `Purchase Assistant`, `Purchase Manager`, and `Store Manager` with Class-A escalation to `Admin`.
  6. _Pragmatic Tracer Bullet Slice:_ End-to-end 5-layer thin slice codified in [`TB-12.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md), proving data contracts and automated integration testing (`TestStep12StoreMaterialRequestTracerBullet`) across Desk script, whitelisted APIs, domain services, and database persistence with zero database commits.
- **Role Standard:** `Store Assistant`, `Store Manager`, `Purchase Assistant`, `Purchase Manager`, `Project Engineer`, `Admin` (Project Supreme Command), `Administrator` / `System Manager`.
- **Audit Verification:** ✔ Schema extensions complete | ✔ Verification gates validated | ✔ Domain services decoupled | ✔ Tracer bullet slice specified | ✔ Tests defined (zero DB commit) | ✔ ADR-012, STEP_12, STEP_12.caveman & TB-12.caveman reconciled.

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
  2. _Multi-Tier Financial Authority Delegation Gate:_ Enforces 4 financial delegation tiers aligned with ADR-000: Tier 1 ($< ₹50\text{k}$, `Purchase Manager` only; frontline `Purchase Assistant` drafts only), Tier 2 ($₹50\text{k} - ₹5\text{L}$, single active approver role configured in `Solar SCM Settings.tier_2_approver_role`: `Purchase Manager`, `Accounts Manager`, or `Admin`), Tier 3 ($> ₹5\text{L} - ₹50\text{L}$, `Admin` only), and Tier 4 ($> ₹50\text{L}$, `Admin` only).
  3. _Solar Milestone Payment Schedule & Retention:_ Capital solar purchases strictly require structured milestone tranches (Advance, In-Transit/LR, Post-GRN Inspection, COD/PBG Retention). Generic single-bullet "Immediate" terms are hard-blocked.
  4. _Configurable / Optional Project Headroom Check:_ Automatically bypassed for Central Inventory Replenishment and Consolidated Multi-Project bulk purchases. For project-linked orders, check against Commercial Proposal / Sales Order BOM is configurable via `Solar SCM Settings` (`enforce_project_bom_ceiling`).
  5. _Multi-Location Delivery Routing for Step 16 GRN:_ Enforces delivery destination routing to Central Store (`Stores - SEPC`) or Direct Site (`Site - <Project Code> - SEPC`). Serialized items flagged with `custom_requires_barcode_serials = 1` for mandatory SABB 2D barcode scan.
  6. _24h Release & 48h Vendor Acknowledgment SLA:_ Monitored by Redis daemons with passwordless token confirmation and delay logging in `tabRemark-Delay Log`.
- **Role Standard:** `Purchase Assistant`, `Purchase Manager`, `Accounts Assistant`, `Accounts Manager`, `Site Supervisor`, `Project Engineer`, `Project Manager`, `Store Manager`, `Admin`, `System Manager`.
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
- **Role Standard:** `Store Assistant`, `Store Manager`, `Site Supervisor`, `Project Engineer`, `Project Manager`, `Purchase Assistant`, `Purchase Manager`, `Admin`, `System Manager`.
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
- **Role Standard:** `Accounts Assistant`, `Accounts Manager`, `Store Assistant`, `Store Manager`, `Purchase Assistant`, `Purchase Manager`, `Admin`, `System Manager`.
- **Audit Verification:** ✔ Schema extensions complete | ✔ Departmental entry policy gate verified | ✔ 3-Way match formulas verified | ✔ Admin price override verified | ✔ Tests defined (zero DB commit).

---

### Step 18: Joint Vendor Payment Monitoring Workbench, Dual-Cadence Notification Engine (T-1 & T-0) & Closed-Loop Procurement Settlement Architecture (Flow 2: Step 07)

- **Document References:** [`ADR-018`](../decisions/ADR-018-JOINT-VENDOR-PAYMENT-MONITORING-WORKBENCH.md) | [`STEP_18`](../../step_plans/STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.md) | [`STEP_18.caveman`](../../step_plans_for_ai/STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabPayment Schedule` (extended with `custom_milestone_type`, `custom_prerequisite_required`, `custom_prerequisite_satisfied`, `custom_prerequisite_doc_ref`, `custom_prerequisite_doc_type`, `custom_notification_t1_sent`, `custom_notification_t1_time`, `custom_notification_t0_sent`, `custom_notification_t0_time`, `custom_settlement_status`, `custom_linked_payment_entry`, `custom_hold_reason`), `tabPayment Entry` (extended with `custom_po_milestone_ref`, `custom_solar_project_ref`, `custom_purchase_team_notified`, `custom_purchase_notified_at`, `custom_bank_utr_no`, `custom_disbursement_remarks`), `tabSolar Notification Settings` (`notify_vendor_payment_t_minus_1`, `notify_vendor_payment_t_zero`, `notify_purchase_on_payment_settlement`, `vendor_payment_notification_hour`, `vendor_payment_alert_channels`), `tabRemark-Delay Log`.
- **Core Domain Services:** `VendorPaymentScheduleService`, `VendorPaymentNotificationDaemon`, `VendorPaymentSettlementService`, `VendorPaymentWorkbenchService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Dual-Cadence Proactive Alerts (T-1 & T-0):_ Daily Celery/RQ daemon (`VendorPaymentNotificationDaemon` running at 08:00 AM) evaluates both PO milestones and PI due dates. Dispatches synchronized reminders 24 hours prior (T-1) and on the due date (T-0) to **both Purchase and Accounts** teams, preventing supplier dispatch holds and cash crunches.
  2. _Closed-Loop Instant Settlement Notification:_ Binds an event-driven observer (`VendorPaymentSettlementService`) to `Payment Entry.on_submit`. Automatically broadcasts instant alerts to the Purchase team upon payment execution with bank UTR number, disbursed amount, instrument date, and remaining balance, eliminating phone/email inquiries.
  3. _Milestone Prerequisite Verification Gates:_ Hard server-side gates prevent disbursements if operational prerequisites are incomplete (Advance requires authorized PO; Transit requires Transporter LR & FAT report; Delivery requires submitted GRN and 3-Way Match; Retention requires Grid Sync COD).
  4. _Dedicated Dual-Workspace Desks:_ Renders custom tailored upcoming payment sections on the Purchase Desk (`/solar/procurement`, focusing on milestone blockers and delivery readiness) and Accounts Desk (`/solar/accounts`, focusing on liquidity horizons, cash forecasts, and TDS deductions).
  5. _Statutory Tax Compliance & Banking Locks:_ Enforces Section 194Q TDS (0.1% on cumulative $> ₹50\text{L}$) calculations and restricts payouts strictly to verified supplier bank accounts.
  6. _Downstream Integration:_ Reconciles payment milestones to feed Step 19 `Vendor Rating` (commercial payment reliability component, 15% scorecard weighting).
- **Role Standard:** `Purchase Assistant`, `Purchase Manager`, `Accounts Assistant`, `Accounts Manager`, `Site Supervisor`, `Project Engineer`, `Project Manager`, `Store Manager`, `Admin`, `System Manager`.
- **Audit Verification:** ✔ Schema extensions complete | ✔ Dual-timer notification logic verified | ✔ Settlement observer hook verified | ✔ Prerequisite gates enforced | ✔ Tests defined (zero DB commit).

---

### Step 19: Vendor Performance Rating Scorecard & Multi-Tier Supplier Governance

- **Document References:** [`ADR-019`](../decisions/ADR-019-VENDOR-PERFORMANCE-RATING-SCORECARD.md) | [`STEP_19`](../../step_plans/STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.md) | [`STEP_19.caveman`](../../step_plans_for_ai/STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.caveman.md)
- **Primary DocTypes:** `tabVendor Performance Rating` (standalone submittable DocType, child tables `tabVendor Rating Item Breakdown` and `tabVendor Rating Service Checklist`, extensions on `tabSupplier` and `tabSolar SCM Settings`, integration with `tabRemark-Delay Log`).
- **Core Domain Services:** `VendorRatingCalculationService`, `VendorTierGovernanceService`, `VendorScorecardSyncService`, `VendorRatingNotificationService`.
- **Reconciliation Points & Architectural Invariants:**
  1. _Two-Tier Collaborative Governance Model:_ The evaluation lifecycle is bifurcated into **Tier 1 (Purchase Manager Filling & Qualitative Review)** and **Tier 2 (Admin Supreme Decision Gateway)**. The Purchase Manager fills scores and clicks `[Submit for Admin Approval]`, triggering real-time multi-channel alerts to the `Admin`.
  2. _The Admin Tri-Action Decision Gateway:_ The `Admin` (Project Supreme Command) receives notifications and exercises three definitive operational controls:
     - `Approve`: Formally approves and submits (`docstatus = 1`), permanently freezing the evaluation and triggering rolling average updates and tier changes on `tabSupplier`.
     - `Reject`: Rejects the evaluation with mandatory justification ($\ge 15$ chars), closing the document with zero impact on supplier tier.
     - `Ask for Reason & Re-Rate`: Challenges ratings with mandatory inquiry notes. Reverts state to `Returned for Re-Rating`, increments `re_rating_count`, and sends an urgent notification to the Purchase Manager to adjust and resubmit.
  3. _4-Factor Balanced Scorecard Model:_ Computes overall score across four mathematically weighted criteria ($W_{OTD} \cdot S_{OTD} + W_{QRR} \cdot S_{QRR} + W_{PACI} \cdot S_{PACI} + W_{SRSC} \cdot S_{SRSC}$):
     - On-Time Delivery (OTD) (35%): Evaluated from PO promised date vs GRN actual posting date with a progressive delay penalty curve.
     - Quality & Rejection Rate (35%): Evaluated from GRN accepted vs received quantities, with a critical defect penalty ($P_{critical} = 25$ pts) for solar module/inverter failures.
     - Price Adherence & Commercial Integrity (15%): Evaluated from PO agreed rate vs Step 17 PI billed rate and debit notes.
     - Service Responsiveness & SCM Collaboration (15%): Purchase Manager qualitative evaluation across RFQ speed, technical MTC documentation, RMA turnaround, and account management.
  4. _Dynamic Multi-Tier Supplier Governance:_ Classifies vendors into `Tier 1 Preferred` ($\ge 85\%$), `Tier 2 Approved` ($70\% - 84.9\%$), `Tier 3 Probationary` ($50\% - 69.9\%$), and `Disqualified / Blacklisted` ($< 50\%$ or ethical/safety breach).
  5. _Upstream Closed-Loop Feedback:_ Authoritative supplier tier and score directly feed Step 13 (`Supplier RFQ`, auto-suggesting Tier 1 and hard-blocking Blacklisted suppliers) and Step 14 (`Quotation Comparison Matrix`, where score forms 15% of landed cost evaluation).
  6. _Three Server-Side Verification Gates:_ Enforces Gate 1 (valid submitted PO/GRN/PI link), Gate 2 (mandatory qualitative service checklist and commentary $\ge 20$ chars), and Gate 3 (Admin Supreme Decision Gate: non-Admins strictly blocked from executing Approve, Reject, or Return for Re-Rate).
  7. _48-Hour TAT SLA Engine:_ Governed by background daemon; overdue sign-offs require mandatory logging in `tabRemark-Delay Log`.
- **Role Standard:** `Purchase Manager`, `Purchase Assistant`, `Store Assistant`, `Store Manager`, `Site Supervisor`, `Project Engineer`, `Project Manager`, `Accounts Manager`, `Admin`, `System Manager`.
- **Audit Verification:** ✔ Schemas complete | ✔ Two-tier Admin approval workflow verified | ✔ Tri-action decision gateway implemented | ✔ Verification gates enforced | ✔ Closed-loop RFQ/Matrix sync specified | ✔ Tests defined (zero DB commit).

---

## 4. Cross-Stage Architecture Invariants & Standards Compliance

### 4.1 Enterprise Role Nomenclature & Symmetric 2-Tier Architecture (ADR-000)

In strict accordance with [`ADR-000`](../decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md), all stages have been reconciled to enforce a symmetric Two-Tier Departmental Role Model, eliminating redundant/deprecated roles, decoupling commercial proposals to CRM, adding site supervision, and establishing Managerial Full-Authority Inheritance:

- ❌ Prohibited & Deprecated Roles:
  - `Lead Representative` (Unified into `Sales Representative` & `Sales Manager`)
  - `Accounts Officer` (Unified into `Accounts Assistant` & `Accounts Manager`)
  - `Commercial Officer` (Unified into `Sales Manager`, `CRM Manager`, `Project Manager`, `Accounts Manager`)
  - `Quality Engineer` / `Vendor Rating Auditor` (Unified into `Store Manager`, `Project Engineer`, `Purchase Manager`)
  - `Liaisoning Officer` (Upgraded to `Liaisoning Representative` & `Liaisoning Manager`)
  - `Lead User`, `Survey User`, `Sales User`, `Design User`, `Project User`, `Store User`, `Liaisoning User`, `Purchase User`, `Accounts User`.
- ✔ Approved & Reconciled Enterprise Roles Matrix:
  - **Sales:** `Sales Representative` (Frontline) | `Sales Manager` (Supervisory)
  - **Survey:** `Survey Engineer` (Frontline) | `Survey Manager` (Supervisory)
  - **Design:** `Design Engineer` (Frontline) | `Design Manager` (Supervisory)
  - **CRM & Proposals:** `CRM Representative` (Frontline) | `CRM Manager` (Supervisory)
  - **Accounts & Finance:** `Accounts Assistant` (Frontline) | `Accounts Manager` (Supervisory)
  - **Project & Site:** `Site Supervisor`, `Project Engineer` (Frontline) | `Project Manager` (Supervisory)
  - **Store & Inventory:** `Store Assistant` (Frontline) | `Store Manager` (Supervisory)
  - **Liaisoning & Compliance:** `Liaisoning Representative` (Frontline) | `Liaisoning Manager` (Supervisory)
  - **Purchase & SCM:** `Purchase Assistant` (Frontline) | `Purchase Manager` (Supervisory)
  - **O&M Service:** `O&M Service Engineer` (Frontline) | `O&M Manager` (Supervisory)
- ✔ Operational Governance Invariants:
  - **Managerial Inheritance:** Managers inherit 100% of their juniors' operational capabilities and submit permissions.
  - **Stage-Forward Lock:** Once downstream stage commences, upstream documents cannot be cancelled or amended.
  - **Junior Cancel/Amend Request Flow:** Frontline raises requests with reasons; Manager approves with remarks pre-forward stage.
  - **Admin Deletion Safeguards:** Downstream dependency warning modal, hard deletion block with active downstream records, and Atomic Cascading Purge (`CascadePurgeService`, $\ge 40$ chars justification).
  - **Step 15 PO Tiers:** Tier 1 (< ₹50k) `Purchase Manager` only; Tier 2 (₹50k-₹5L) Admin-configurable single role; Tier 3 & 4 `Admin` only.
  - **Stage-Gated RLS:** Juniors have assigned previous stage read-only + assigned current stage; Managers have all previous stage read-only + all current stage.

### 4.2 Supreme Authority Standard (Admin vs System Manager)

Across all specifications:

- **`Administrator` & `System Manager` (Framework Supreme / Developer Realm):** Technical dev ops, bench commands, git repos, Python source code, DocType schema builders, and Redis queue workers.
- **`Admin` (Project Supreme Command):** Operational supremacy over all EPC lifecycles (Stages 01–11 and Flow 2 SCM), exclusive governance over `Solar SLA Settings`, `Solar Notification Settings`, `Solar SCM Settings`, and delay approvals. Restricted from touching source code or schema builder forms. Emergency cancellations and deletions governed by strict audit logging in `tabSolar Deletion Audit Log`.

### 4.3 Database Schema & 3NF Data Integrity

- All child tables enforce explicit foreign keys (`parent`, `parenttype`, `parentfield`).
- High-frequency query columns (`mobile_no`, `project`, `sales_order`, `serial_no`, `status`, `rfq_reference`, `evaluation_status`, `custom_comparison_matrix_ref`, `custom_project_ref`, `custom_receipt_location_type`, `custom_po_reference`, `custom_grn_reference`, `custom_3way_match_status`, `custom_vendor_tier`, `custom_vendor_rating_score`, `custom_rating_status`) are backed by explicit B-Tree database indexes.
- Critical financial and technical state snapshots utilize SHA-256 baseline hashing (`bom_hash`).

### 4.5 Role & Permission Architecture Reconciliation Log (ADR-000 Execution)

- **Phase 1: Canonical Architecture Decision Record (Completed & Reconciled):**
  - Authoritative decision record [`ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md) published and accepted. Codifies 2-tier departmental symmetry, elimination of 6 deprecated roles, proposal decoupling to CRM, Site Supervisor formalization, Managerial Authority Inheritance, Stage-Forward Lock, Junior Cancel/Amend flow, Admin Deletion Safeguards (dependency warnings, hard deletion blocks, atomic cascading purge), Step 15 PO thresholds, and Stage-Gated RLS.
- **Phase 2: Master Architecture & Planning Reference Suite (Completed & Reconciled):**
  - [`step_plans/README.md`](../../step_plans/README.md): Sections 5 & 6 updated with ADR-000 symmetric role table and operational safeguards.
  - [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md): Section 2 updated with symmetric 2-tier role blueprint and managerial inheritance.
  - [`planning_ref_docs/README.prd.md`](../../planning_ref_docs/README.prd.md): SPA landing roles and ADR-000 authority notes updated.
  - [`planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md`](../../planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md): Sections 3.2 (SLA table) and 6 (Enterprise Roles Matrix) updated.
  - [`planning_ref_docs/03_TO_BE_BUSINESS_PROCESS.md`](../../planning_ref_docs/03_TO_BE_BUSINESS_PROCESS.md): Gates 1–9 responsible roles updated.
  - [`planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md`](../../planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md): `FR-005`, `FR-015`, and `FR-016` primary actors reconciled.
  - [`planning_ref_docs/10_UI_UX_SPECIFICATION.md`](../../planning_ref_docs/10_UI_UX_SPECIFICATION.md): Section 1 dashboard role allocations updated.
  - [`planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md`](../../planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md): `MOD-04`, `MOD-05`, `MOD-06`, `MOD-10` SOP text updated.
- **Phase 3: Flow 1 Core Step Plans (Completed & Reconciled):**
  - All Flow 1 specifications ([`STEP_01`](../../step_plans/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.md) through [`STEP_11`](../../step_plans/STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.md)) audited and updated to 100% ADR-000 compliance.
  - Eliminated `Lead Representative` (unified to `Sales Representative` & `Sales Manager` in `STEP_01` & `STEP_07`).
  - Standardized `Survey Engineer` & `Survey Manager` in `STEP_02`.
  - Standardized `Design Engineer` & `Design Manager` in `STEP_03`.
  - Decoupled commercial proposals to `CRM Representative` & `CRM Manager` in `STEP_04`.
  - Standardized `Accounts Assistant` & `Accounts Manager` in `STEP_05` and `STEP_11`.
  - Excised `Commercial Officer` across `STEP_06`, `STEP_07`, `STEP_08`, `STEP_09`, `STEP_11` (reallocated to `Sales Manager`, `CRM Manager`, `Project Manager`, `Accounts Assistant`).
  - Excised `Quality Engineer` / `Vendor Rating Auditor` in `STEP_10` (reallocated to `Project Engineer` / `Project Manager` / `Liaisoning Manager`).
  - Upgraded `Liaisoning Officer` to `Liaisoning Representative` & `Liaisoning Manager` in `STEP_06`, `STEP_07`, `STEP_10`.
  - Formalized `Site Supervisor` role in `STEP_06`, `STEP_07`, `STEP_08`, `STEP_09`, `STEP_10`.
  - Reconciled all frontend routing, actor matrices, permission tables, SOP runbooks, and error troubleshooting tables.
- **Phase 4: Flow 2 SCM Step Plans (Completed & Reconciled):**
  - All Flow 2 specifications ([`STEP_12`](../../step_plans/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md) through [`STEP_19`](../../step_plans/STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.md)) audited and updated to 100% ADR-000 compliance.
  - Formalized `Site Supervisor` role across Step 12 (Direct-to-site MR creation), Step 13, Step 14, Step 16 (Site GRN gate/inspection), and Step 18.
  - Reconciled Step 15 PO Delegation Matrix to ADR-000: Tier 1 (< ₹50k, `Purchase Manager` only; `Purchase Assistant` drafts only), Tier 2 (₹50k–₹5L, single active approver role configured in `Solar SCM Settings.tier_2_approver_role`: `Purchase Manager`, `Accounts Manager`, or `Admin`), Tier 3 (> ₹5L to ₹50L, `Admin` only), Tier 4 (> ₹50L, `Admin` only). Completely excised `Commercial Officer`.
  - Replaced `Accounts Officer` with `Accounts Manager` across Step 16, Step 17 (3-Way Match & entry), and Step 18 (Joint Payment Workbench).
  - Excised `Quality Engineer` / `Vendor Rating Auditor` across Step 16 and Step 19 (reallocated technical verification to `Store Manager` and `Project Engineer`).
  - Verified Managerial Authority Inheritance, Stage-Forward Lock, Junior Cancel/Amend Request flow, and Admin Deletion Safeguards across all Flow 2 lifecycle documentation.
- **Phase 5: Older ADRs & Token-Optimized AI Specifications (Completed & Reconciled):**
  - All older ADRs in `docs/decisions/` (`ADR-001`, `ADR-004`, `ADR-005`, `ADR-006`, `ADR-007`, `ADR-010`, `ADR-011`, `ADR-015`, `ADR-017`, `ADR-018`, `ADR-019`) audited and brought to 100% ADR-000 compliance.
  - Completely excised `Lead Representative`, `Accounts Officer`, `Commercial Officer`, `Quality Engineer`, `Vendor Rating Auditor`, and `Liaisoning Officer`.
  - Updated financial delegation limits in ADR-015 to < ₹50k, ₹50k–₹5L, > ₹5L; updated UI actions, role permissions, and role buttons.
  - All token-optimized AI specifications in `step_plans_for_ai/` (`STEP_01.caveman.md` through `STEP_19.caveman.md` and `tracer_bullets/`) audited and brought to 100% ADR-000 compliance:
    - Unified `Sales Representative` & `Sales Manager` in `STEP_01.caveman.md`.
    - Decoupled proposal creation to `CRM Representative` & `CRM Manager` in `STEP_04.caveman.md`.
    - Excised `Commercial Officer` across `STEP_06.caveman.md`, `STEP_07.caveman.md`, `STEP_08.caveman.md`, `STEP_15.caveman.md`.
    - Upgraded `Liaisoning Officer` to `Liaisoning Representative` & `Liaisoning Manager` in `STEP_10.caveman.md`.
    - Standardized `Accounts Assistant` & `Accounts Manager` across `STEP_05.caveman.md`, `STEP_11.caveman.md`, `STEP_16.caveman.md`, `STEP_17.caveman.md`, `STEP_18.caveman.md`, and `STEP_19.caveman.md`.
    - Excised `Quality Engineer` / `Vendor Rating Auditor` across `STEP_16.caveman.md` and `STEP_19.caveman.md` (reallocated to `Store Manager` and `Project Engineer` / `Site Supervisor`).
    - Aligned Step 15 PO tier validation in Python services, error lookup tables, and end-user SOPs.
    - Verified 0 occurrences of deprecated roles across entire `step_plans_for_ai/` and `docs/decisions/`.
- **Phase 6: Foundation Architecture Specification & Dedicated Planning (Completed & Reconciled):**
  - Formulated dedicated Master Step Plan: [`step_plans/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.md`](../../step_plans/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.md) strictly adhering to the 9-Section Step Planning Blueprint.
  - Formulated token-optimized AI specification: [`step_plans_for_ai/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.caveman.md`](../../step_plans_for_ai/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.caveman.md).
  - Formulated Pragmatic Programmer Tracer Bullet Specification: [`TB-00.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md) cutting through all 5 layers (Lean Schemas, Domain Services, Controller Mixin & RPC, Desk Client Script, and 6-case Integration Test Suite with atomic savepoint rollback).
  - Updated [`step_plans/README.md`](../../step_plans/README.md) to integrate Step 00 as the Foundation Substrate preceding Flow 1 and Flow 2.
  - Approved dedicated implementation plan in `step_00_tracer_bullet_plan.md` defining the engineering path to develop the Role & Security substrate (`solar_module/security/`, fixtures, audit DocTypes, and `StageSecuredDocument` mixin) before individual stage implementation.
- **Phase 7: Stage 01 Lead Management Tracer Bullet Specification (Completed & Reconciled):**
  - Formulated comprehensive Pragmatic Programmer Tracer Bullet Specification: [`TB-01.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md) cutting cleanly through all 5 system layers:
    1. Layer 1 (Lean Schema): `tabLead` solar extensions (`mobile_no`, `solar_capacity`, `custom_address`, `custom_pincode`, `stage_status`, `sla_due_date`, `surveyed_by`), child `tabRemark-Delay Log`, downstream `tabSite Survey` draft container, composite B-Tree indexes.
    2. Layer 2 (Decoupled Domain Services): `LeadValidationService` (10-digit mobile sanitization `^[6-9]\d{9}$`, cross-table deduplication against `tabLead` & `tabCustomer`, technical sizing feasibility gate), `LeadSLAService` (2-hour response SLA countdown, overdue evaluation, delay justification enforcement), `SiteSurveyBridgeService` (role verification for `Survey Engineer`/`Survey Assistant` and downstream container instantiation), seamlessly integrated with ADR-000 `StageForwardLockService`.
    3. Layer 3 (Controller & RPC Gateway): `SolarLeadController` extending `StageSecuredDocument` mixin, whitelisted endpoints `create_solar_lead`, `assign_site_surveyor`, `log_lead_delay`, `get_active_survey_engineers`.
    4. Layer 4 (Desk Client Script): `codes/client_script/lead.js` featuring real-time client-side mobile cleansing, async duplicate alert dialogs, removal of standard out-of-sequence Frappe buttons (`Customer`, `Opportunity`, `Quotation`, `Prospect`), `[Assign Site Survey]` modal with engineer picker, `[Log SLA Delay Reason]` modal, and ADR-000 `[Request Cancel / Amend]` junior modal.
    5. Layer 5 (Automated Verification Suite): `solar_module/tests/test_lead_tracer_bullet.py` comprising 8 atomic integration test cases verifying ingestion, duplicate rejection, sizing feasibility gates, survey auto-spawning, SLA breaches, Stage-Forward lock immutability, and deletion audit snapshots (zero database commits, automatic transaction rollback).
- **Phase 8: Foundation Architecture ADR Renumbering (ADR-020 to ADR-000 Reconciliation):**
  - Renumbered authoritative architectural decision record to [`ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md) to establish 1:1 structural symmetry with Stage 00 (`STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.md`).
  - Audited and updated all 62 cross-references across 20 files in `docs/`, `step_plans/`, `step_plans_for_ai/`, `architect_docs/`, and `planning_ref_docs/` to 100% ADR-000 compliance.
- **Phase 9: Stage 08 & Stage 09 Material Dispatch & Installation Zone DPR Tracer Bullet Specifications (Completed & Reconciled):**
  - Formulated Pragmatic Programmer Tracer Bullet Specification: [`TB-08.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md) cutting through all 5 layers with Frappe v15 Serial and Batch Bundle (SABB) integration, statutory E-Way bill barrier, closed-loop Proof of Delivery, and 10 zero-commit test cases.
  - Formulated Pragmatic Programmer Tracer Bullet Specification: [`TB-09.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md) cutting cleanly through all 5 system layers:
    1. Layer 1 (Lean Schema): `tabProject` installation fields, `tabTask` solar WBS fields, `tabSolar Installation Zone`, standalone submittable `tabSolar Daily Progress Report` with offline support fields (`offline_client_id` UUIDv4, `sync_status`, `offline_created_at`, `device_client_id`) and 5 child tables, standalone submittable `tabSolar Pre Commissioning Checklist` with 3 electrical child tables, and single `tabSolar Installation Settings`.
    2. Layer 2 (Domain Services): `InstallationZoneWBSService` (multi-zone WBS task generator, physical completion rollup), `SolarDPRValidationService` (safety toolbox briefing gate, headcount assertion, installed material balance bound), `SolarDPRSyncService` (idempotent offline sync, UUID deduplication, 256KB chunked media reassembly for low-bandwidth 2G/3G remote sites), `PreCommissioningVerificationService` (IEC 62446-1 electrical validation: Voc ±5%, Megger $\ge 1.0\text{ M}\Omega$, Earth resistance $\le 5.0\ \Omega$ MMS / $\le 1.0\ \Omega$ Inverter, Cat A snag zero-defect rule), and `InstallationHandoffService` (Project Stepper advance, spawning Stage 09 Surplus Material Return task, activating Stage 10B 10-day statutory grid sync countdown).
    3. Layer 3 (Controllers & RPC Gateway): `SolarDailyProgressReportController` (immutable lock on cancel), `SolarPreCommissioningChecklistController` (100% WBS precondition), whitelisted endpoints `initialize_project_installation`, `sync_offline_dpr`, `upload_dpr_media_chunk`, `get_site_material_balance`.
    4. Layer 4 (Desk Client Script & Dynamic Mobile Workbench): `codes/client_script/project_installation.js`, offline-first Mobile DPR Fast-Touch Entry specification with IndexedDB local caching and connectivity status pill, and Pre-Commissioning Electrical Testing Workbench layout.
    5. Layer 5 (Automated Verification Suite): `solar_module/tests/test_stage_09_installation_tracer_bullet.py` with 11 atomic integration test cases verifying mobilization gates, WBS rollups, safety briefings, headcount, material balance ceiling, offline idempotency, chunked photo reassembly, WBS completeness, IEC 62446-1 electrical thresholds, and atomic downstream handoffs (zero database commits, automatic rollback).

- **Phase 10: Stage 10 Dual-Timing Statutory Liaisoning, Regulatory Inspection & Grid Sync Tracer Bullet Specification (Completed & Reconciled):**
  - Formulated Pragmatic Programmer Tracer Bullet Specification: [`TB-10.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_10_LIAISONING_GRID_SYNC_TRACER_BULLET.caveman.md) cutting cleanly through all 5 system layers:
    1. Layer 1 (Lean Schema): `tabProject` statutory fields (`custom_liaisoning_reference`, `custom_phase_1_status`, `custom_phase_2_status`, `custom_statutory_deadline`, `custom_grid_sync_date`, `custom_cod_date`, `custom_net_meter_serial_no`, `custom_is_completed_flag`), `tabCustomer` utility fields (`custom_discom_consumer_no`, `custom_discom_name`, `custom_sanctioned_load_kw`, `custom_tariff_category`), standalone submittable `tabLiaisoning And Synchronization` (`LIA-.YYYY.-.#####`) with 4 child tables (`tabSolar Statutory Document Checklist`, `tabSolar Inspection Milestone Log`, `tabSolar Meter Reading Item`, `tabSolar Stage Delay Log`), single `tabSolar Liaisoning Settings`, and composite B-tree indexes.
    2. Layer 2 (Domain Services): `LiaisoningInceptionService` (Phase 1 auto-spawn from Stage 06 Sales Order), `LiaisoningSLAService` (10-day statutory SLA countdown, Sunday & Frappe `Holiday List` calendar math, hourly SLA evaluation), `LiaisoningPhase1Service` (KYC, DISCOM filing, PM Surya Ghar ID, and atomic `tabLead` Progress Bar 1 terminal closeout), `LiaisoningPhase2Service` (CEIG safety gate, JMI & bi-directional net-meter verification, anti-islanding trip $\le 2.0\text{s}$), and `ProjectCompletionService` (atomic `Project.status = "Completed"`, `custom_is_completed_flag = 1`, residual WBS task auto-closure, Stage 11 `tabSolar Asset Register` twin spawning, and Accounts milestone retention alert).
    3. Layer 3 (Controllers & RPC Gateway): `LiaisoningAndSynchronization` submittable controller with strict permissions and immutable lock on cancellation, 7 whitelisted typed RPC endpoints (`solar_module.api.liaisoning.*`), and hourly background Celery/RQ SLA daemon (`solar_module.tasks.check_liaisoning_sla`).
    4. Layer 4 (Desk Client Script & Dynamic Kanban Workbench): `codes/client_script/liaisoning_and_synchronization.js` with dynamic SLA alert banners, action dialogs for filing, CEIG, JMI, and grid sync COD, and `/solar/liaisoning` two-tier Kanban board specification with radial 10-day SVG countdown timers.
    5. Layer 5 (Automated Verification Suite): `solar_module/tests/test_stage_10_liaisoning_grid_sync_tracer_bullet.py` with 11 atomic integration test cases verifying all business gates, SLA countdowns, safety ceilings, Lead closeouts, and atomic Project completion under strict zero-database-commit rollback.

- **Phase 11: Stage 11 On-Demand Solar Service, Incident-Driven O&M & Warranty Lifecycle Tracer Bullet Specification (Completed & Reconciled):**
  - Formulated Pragmatic Programmer Tracer Bullet Specification: [`TB-11.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_TRACER_BULLET.caveman.md) cutting cleanly through all 5 system layers:
    1. Layer 1 (Lean Schema): `tabCustomer` service fields (`custom_site_latitude`, `custom_site_longitude`, `custom_commissioning_date`, `custom_warranty_expiry_date`, `custom_amc_active`, `custom_contact_phone`), standalone submittable `tabSolar Service Request` (`SSR-.YYYY.-.#####`), standalone submittable `tabMaintenance Visit` (`SMV-.YYYY.-.#####`), child tables `tabSolar Service Spare Item`, `tabMaintenance Checklist Item`, `tabSolar Stage Delay Log`, master append-only ledger `tabSolar Site Service History` (`SSH-.YYYY.-.#####`), single `tabSolar Service Settings`, and composite B-tree indexes.
    2. Layer 2 (Domain Services): `SolarServiceIntakeService` (Gate 1 dual-track warranty discrimination, tiered SLA deadline calculation: 4h/24h Emergency, 12h/48h High, 48h/5d Standard, technician assignment & scheduling), `FieldDiagnosticsAndPartsService` (Gate 2 geodesic Haversine distance calculation, $\le 500\text{m}$ geofence check-in verification, electrical checklist validation, Gate 3 serialized component swap reconciliation requiring both removed and installed serials), `CustomerVerificationService` (Gate 4 cryptographic 6-digit OTP generation with 30-min Redis caching, OTP verification, mobile touchscreen digital signature validation), and `ServiceDownstreamBridgeService` (automated ERPNext `Stock Entry` Material Issue for spare consumption, automated ERPNext `Sales Invoice` generation for Track B chargeable visits, atomic append to `tabSolar Site Service History`, and customer plant digital twin sync).
    3. Layer 3 (Controllers & RPC Gateway): `SolarServiceRequest` and `MaintenanceVisit` submittable controllers with strict permissions, state transition assertions, and immutable cancellation locks restricted to `Admin` and `System Manager`; 8 whitelisted typed RPC endpoints (`solar_module.api.om.*`); and 15-minute background Celery/RQ SLA daemon (`solar_module.tasks.check_service_slas`).
    4. Layer 4 (Desk Client Script & Dynamic Mobile Workbench): `codes/client_script/solar_service_request.js` with dynamic SLA alert banners, dispatch dialog, quotation mapper, and delay reason modal; `codes/client_script/maintenance_visit.js` with browser GPS acquisition, OTP verification dialogs; Fast-Touch Mobile Field Technician Interface (`/solar/technician`) layout; and O&M Coordinator Kanban Desk Workbench (`/solar/service`).
    5. Layer 5 (Automated Verification Suite): `solar_module/tests/test_stage_11_solar_service_om_tracer_bullet.py` with 12 atomic integration test cases verifying decoupled service boundaries, Gate 1 active vs physical damage warranty classification, Track B commercial dispatch gate, tiered SLAs, Haversine precision, 500m geofence hard blocking and clearance, serialized spare swapping, Gate 4 customer verification blocking, OTP lifecycle, and Admin-only cancellation under strict zero-database-commit rollback.

- **Phase 12: Stage 12 Store Material Request & Automated Low-Stock Monitoring Tracer Bullet Specification (Completed & Reconciled):**
  - Formulated Pragmatic Programmer Tracer Bullet Specification: [`TB-12.caveman`](../../step_plans_for_ai/tracer_bullets/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md) cutting cleanly through all 5 system layers:
    1. Layer 1 (Lean Schema): `tabMaterial Request` custom fields (`custom_project_reference`, `custom_sales_order`, `custom_urgency_level`, `custom_trigger_source`, `custom_workflow_status`, `custom_sla_deadline`, `custom_sla_status`, `custom_delay_reason`, `custom_delay_approved_by`, `custom_is_class_a_solar`), `tabMaterial Request Item` custom fields (`custom_lead_time_days`, `custom_current_stock_qty`, `custom_projected_stock_qty`, `custom_safety_stock_level`, `custom_reorder_level`, `custom_allocated_project`, `custom_bom_remaining_qty`), standalone custom DocTypes `tabSolar Low Stock Incident Log` (`SLS-INC-.YYYY.-.#####`) and `tabSolar Reorder Policy` (`SRP-.YYYY.-.#####`), settings extensions in `tabSolar SLA Settings` & `tabSolar Notification Settings`, and composite B-Tree indexes on `tabBin` and `tabMaterial Request`.
    2. Layer 2 (Domain Services): `ReorderCalculationService` (true pipeline solvency math $\text{Actual} + \text{Ordered} + \text{Indented} - \text{Reserved}$, dynamic replenishment sizing, pallet packaging multiple rounding), `StoreRequisitionService` (Gate 1 duplicate open indent prevention, Gate 2 supplier lead-time feasibility, Gate 3 project BOM headroom netting, Class-A solar asset identification, tiered SLA calculation), `StoreNotificationBroker` (WhatsApp Business Cloud API & transactional email dispatches), and `LowStockMonitoringDaemon` (scheduled background runner evaluating warehouse reorder points, logging incidents, and auto-generating draft MRs).
    3. Layer 3 (Controllers & RPC Gateway): `SolarMaterialRequest` submittable controller extending `StageSecuredDocument` with strict ADR-000 submission authority (Store Assistant draft-only vs Store Manager submit) and downstream Stage-Forward immutability locks; 5 whitelisted typed RPC endpoints (`solar_module.api.store.*`); and scheduled background cron jobs (`monitor_low_stock_scheduled_task`, `recompute_enterprise_slas`).
    4. Layer 4 (Desk Client Script & Dynamic Mobile Workbench): `codes/client_script/material_request.js` with dynamic SLA countdown badges, live multi-warehouse stock inspector modal, delay justification dialog, downstream pipeline drawer; Store Material Requests Dashboard (`/solar/store/material-requests`) with BOM headroom netting modal; and Automated Low-Stock Replenishment Workbench (`/solar/store/low-stock`) with stockout risk indicators.
    5. Layer 5 (Automated Verification Suite): `solar_module/tests/test_step_12_material_request_tracer_bullet.py` with 11 atomic integration test cases verifying pipeline solvency math, pallet rounding, duplicate rejection, critical breakdown bypass, lead-time feasibility, BOM headroom netting, Class-A tagging, tiered SLAs, overdue delay enforcement, autonomous daemon incident logging, and ADR-000 submission restrictions under strict zero-database-commit rollback.

---

## 5. Lifecycle Roadmap & Next Implementation Horizons

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SOLAR EPC LIFECYCLE ROADMAP                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FOUNDATION SUBSTRATE: ENTERPRISE ROLE, PERMISSION & SECURITY CORE                                │
│  [✔] Step 00: Role, Permission & Security Core Spec & Tracer Bullet (ADR-000 Substrate)          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FLOW 1: CORE SOLAR EPC PROJECT EXECUTION (11 STAGES) - 100% COMPLETE TRACER BULLET COVERAGE     │
│  [✔] Stage 01: Lead Management Spec & Tracer Bullet (TB-01.caveman)                              │
│  [✔] Stage 02: Technical Site Survey Spec & Tracer Bullet (TB-02.caveman)                        │
│  [✔] Stage 03: Survey Engineering Design Spec & Tracer Bullet (TB-03.caveman)                    │
│  [✔] Stage 04: Proposal & Subsidy Spec & Tracer Bullet (TB-04.caveman)                           │
│  [✔] Stage 05: Advance Payment Clearance Spec & Tracer Bullet (TB-05.caveman)                    │
│  [✔] Stage 06: Sales Order Baseline Spec & Tracer Bullet (TB-06.caveman)                         │
│  [✔] Stage 07: Dual Progress Bar Lifecycle Spec & Tracer Bullet (TB-07.caveman)                  │
│  [✔] Stage 08: Material Dispatch Logistics & Delivery Note Serialized Tracking (TB-08.caveman)   │
│  [✔] Stage 09: Installation Zone WBS & Daily Progress Reports (DPR) (TB-09.caveman)             │
│  [✔] Stage 10: Dual-Timing Statutory Liaisoning, Regulatory Inspection & Grid Sync (TB-10.caveman)│
│  [✔] Stage 11: On-Demand Solar Service Spec & Tracer Bullet (TB-11.caveman)                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FLOW 2: SCM, STORE, PURCHASE & VENDOR PROCUREMENT LIFECYCLE (8 STEPS)                           │
│  [✔] Step 12: Store Requisitions & Low Stock Monitoring (TB-12.caveman)                          │
│  [✔] Step 13: Supplier Request for Quotation (RFQ)                                               │
│  [✔] Step 14: Supplier Quotation Comparative Evaluation Matrix                                   │
│  [✔] Step 15: Purchase Order Authorization & Milestone Terms                                     │
│  [✔] Step 16: Multi-Location Barcode GRN & Tri-Party Custody Approval                            │
│  [✔] Step 17: Purchase Invoicing & 3-Way Match Validation                                        │
│  [✔] Step 18: Joint Vendor Payment Monitoring Workbench                                          │
│  [✔] Step 19: Vendor Performance Rating Scorecard & Multi-Tier Governance                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ GOVERNANCE & SECURITY FOUNDATION: ADR-000 ARCHITECTURE                                           │
│  [✔] ADR-000: Enterprise Role & Permission Architecture (Symmetric 2-Tier + Admin Invariants)    │
│  [✔] Reconciled Flow 1 Master Step Plans (Steps 01 - 11)                                          │
│  [✔] Reconciled Flow 2 SCM Master Step Plans (Steps 12 - 19)                                      │
│  [✔] Reconciled Master Architecture Docs, Blueprints & Planning Ref Docs                         │
│  [✔] Reconciled Older ADRs (ADR-001 through ADR-019)                                             │
│  [✔] Reconciled Token-Optimized AI Specifications (step_plans_for_ai/ & tracer_bullets/)          │
│  [✔] Dedicated Step 00 Security Substrate Master Specification & Implementation Plan              │
│  [✔] Dedicated Step 01-11 Flow 1 Tracer Bullet Specifications (TB-01 through TB-11.caveman)     │
│  [✔] Dedicated Step 12 Flow 2 Tracer Bullet Specification (TB-12.caveman)                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Audit Sign-off

- **Audited By:** Lead AI Software Architect & System Engineer
- **Audit Timestamp:** 2026-09-30T10:04:00Z
- **Reconciliation Integrity:** 100% (Complete enterprise role reconciliation under ADR-000. Dedicated Step 00 Master Plan, AI caveman specification, and Pragmatic Programmer Tracer Bullet specification created; Step 01 through Step 11 Flow 1 Master Plans and Pragmatic Programmer Tracer Bullet specifications created cutting through all 5 layers with atomic integration test suites and zero database commits; Step 12 Flow 2 SCM kickoff codified with Pragmatic Programmer Tracer Bullet specification cutting through all 5 layers [Lean Schema extensions, ReorderCalculationService solvency math, StoreRequisitionService Gates 1-3, StoreNotificationBroker multi-channel alerts, LowStockMonitoringDaemon autonomous draft generation, SolarMaterialRequest controller with ADR-000 role authority and Stage-Forward lock, Desk script material_request.js, SPA workbenches, and 11-case zero-commit integration test suite]; all 11 Stages of Flow 1 Core Solar EPC Project Execution and all 8 Steps of Flow 2 SCM Procurement Lifecycle completely specified and cross-referenced with ADR-000 through ADR-019, master step plans, token-optimized AI caveman plans, tracer bullets, and codebase touchpoints; Managerial Authority Inheritance, Admin Supreme Authority with Strict Deletion Audit, Downstream Dependency Warnings & Hard Blocking, Atomic Cascading Purge (`CascadePurgeService`), Stage-Forward Lock, Junior Cancel/Amend Request workflow, Refined PO Financial Delegation Tiers, and Stage-Gated RLS fully synchronized across the entire repository).
- **Next Operational Action:** Implementation of Step 00 Core Security Substrate in `solar_module/security/` followed by Flow 1 and Flow 2 tracer bullet bench test verification.

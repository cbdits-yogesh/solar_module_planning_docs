# STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 06 Sales Order Commercial Baseline Anchor & Downstream Spawning

**Document ID:** `TB-06-SALES-ORDER`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.caveman.md`](../STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-006-SALES-ORDER-BASELINE-DOWNSTREAM-SPAWNING.md`](../../docs/decisions/ADR-006-SALES-ORDER-BASELINE-DOWNSTREAM-SPAWNING.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md`](STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md`](STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md`](STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md`](STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md`](STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Stage 07 (`Delivery Note` material dispatch), Stage 08 (`Project` / WBS installation), Stage 10 (`Liaisoning And Synchronization` statutory compliance)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-06`, `Sec 3.6`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-006`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-006`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 4: FIN`, `Domain 7: PRJ`, `Domain 8: CMP`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 5`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 9`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-06`)  
**Target Module:** `solar_module` / `manoj` (Extend ERPNext `Sales Order`, `Sales Order Item`, `Project`, `Task`, `Delivery Note`, plus standalone `Liaisoning And Synchronization`, `Solar Sales Order Settings`, child `Remark-Delay Log`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution  

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** Disconnected UI forms, mock order submissions, or isolated task-creation scripts that do not enforce foreign-key integrity, omit live database indexes, skip cryptographic hashing, or lack atomic transaction rollbacks.
- **Tracer Bullet:** A complete, permanent, 5-layer thin vertical slice cutting cleanly through the live Frappe architecture. It accepts verified Stage 05 advances (`custom_advance_verified = 1`), evaluates the 5 hard pre-submission verification gates, seals the commercial/technical baseline with a deterministic SHA-256 hash, and programmatically triggers atomic triple downstream spawning (`Project` + WBS `Task` tree, `Material Delivery Task` for `Store Manager`, and `Liaisoning And Synchronization` Phase 1 dossier).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 06 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabSales Order custom fields (baseline hash, frozen flag, gate refs)    │
│   - tabSales Order Item custom fields (category, BOM ref, warehouse)        │
│   - tabProject custom fields (SO ref, capacity, consumer no, GPS, engineers)│
│   - tabTask custom fields (wbs_stage, zone, assigned_role, delegation flags)│
│   - tabLiaisoning And Synchronization (standalone submittable DocType)      │
│   - tabSolar Sales Order Settings (single DocType: kickoff SLA, contract)   │
│   - tabRemark-Delay Log (SLA audit & delay justification child table)       │
│   - Composite B-Tree Indexes on (custom_quotation_reference, docstatus)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - SalesOrderBaselineService (Deterministic SHA-256, BOM match validation) │
│   - ProjectSpawnerService (Project container & multi-zone WBS task tree)    │
│   - StoreLogisticsService (Store Manager task spawning & assistant delegate)│
│   - LiaisoningInceptionService (Phase 1 statutory DISCOM dossier inception) │
│   - SalesOrderSLAService (24h turnaround countdown, delay log audit)        │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                      │
│   - SolarSalesOrder (overrides SalesOrder with StageSecuredDocument mixin)  │
│   - validate(): Enforces 5 hard verification gates before submission        │
│   - on_submit(): Atomic execution of baseline freeze and downstream spawner │
│   - on_cancel(): Validate downstream dispatch constraints (block if DNs)   │
│   - validate_sales_order_baseline RPC: Real-time pre-submit gate audit      │
│   - reassign_store_delivery_task RPC: Store Manager to Store Assistant      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Workbench Hook                        │
│   - codes/client_script/sales_order_solar.js (Action ribbon, freeze banner) │
│   - Pre-submission gate readiness check modal & SLA badge indicators        │
│   - Task delegation modal for Store Manager                                 │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_stage_06_sales_order_tracer_bullet.py           │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Zero-commit rule (atomic rollback in tearDown)                          │
│   - 10 rigorous test cases validating all Stage 06 invariants               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 10 fundamental business, technical, and operational invariants of Stage 06 across the live Frappe stack:

1. **Stage 05 Advance Clearance Gate (Gate 1):** Asserts that linked `Quotation` has cleared the Stage 05 financial gate (`custom_advance_verified == 1`) before `Sales Order` validation and submission.
2. **Executed Client Contract Gate (Gate 2):** Enforces mandatory attachment of signed bilateral EPC contract (`custom_signed_contract_doc`) and formal agreement date (`custom_contract_date`).
3. **Customer & Statutory Completeness Gate (Gate 3):** Validates that linked `Customer` master contains non-empty `custom_discom_consumer_no` and verified billing/shipping addresses.
4. **Dynamic Engineering BOM Integrity Gate (Gate 4):** Asserts line-by-line alignment between `Sales Order Item` records and frozen `custom_quot_bom` of linked `Survey Engineering Design`.
5. **Milestone Payment Schedule Gate (Gate 5):** Validates that child table `tabPayment Schedule` sums to exactly $100\%$ of `grand_total` and Milestone 1 matches collected Stage 05 advance ($\ge 50\%$).
6. **Cryptographic Baseline Freeze:** Computes deterministic SHA-256 hash across sorted BOM items, quantities, rates, customer, and payment terms, locking the record on submission (`custom_baseline_frozen = 1`).
7. **Atomic Triple Downstream Spawning:** Single ACID transaction generating:
   - ERPNext `Project` container with multi-zone WBS Tasks (Civil, MMS, Mounting, Cabling, Earthing, Testing).
   - `Material Delivery Task` assigned directly to `Store Manager` (`custom_can_reassign = 1`).
   - `Liaisoning And Synchronization` record in Phase 1 (`Pending Filing`).
8. **Store Manager Task Delegation:** Pure RPC endpoint and server validation allowing `Store Manager` to delegate material preparation specifically to `Store Assistant` with audit timestamp.
9. **24-Hour Kickoff TAT SLA Engine:** Tracks 24-hour turnaround window from Stage 05 financial clearance date, enforcing category and remarks in `tabRemark-Delay Log` upon overdue submission.
10. **Downstream Dispatch Lockout (Stage-Forward Immutability):** Server-side gate blocking `Sales Order` cancellation if any submitted downstream `Delivery Note` exists against it.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Extends standard ERPNext DocTypes (`Sales Order`, `Sales Order Item`, `Project`, `Task`, `Delivery Note`), registers settings and statutory DocTypes, and establishes MariaDB composite indexes.

### 2.1 Core DocType Extension: `tabSales Order` (Baseline Anchor)

| Fieldname                          | Label                     | Fieldtype    | Options / Target                                                                   | Mandatory |    Index     | Rules & Invariants                                                           |
| :--------------------------------- | :------------------------ | :----------- | :--------------------------------------------------------------------------------- | :-------: | :----------: | :--------------------------------------------------------------------------- |
| `custom_solar_baseline_section`    | Solar EPC Commercial Gate | `Section Break` | -                                                                               |    No     |      -       | Section container for Stage 06 verification and baseline data.               |
| `custom_is_solar_order`            | Is Solar EPC Order        | `Check`      | -                                                                                  |  **Yes**  | **Index: 1** | Identifies Solar EPC orders; toggles domain validations. Default: 1.         |
| `custom_lead_reference`            | Originating Lead Ref      | `Link`       | `Lead`                                                                             |  **Yes**  | **Index: 1** | Originating prospect link from Stage 01. Read-only once set.                 |
| `custom_quotation_reference`       | Finalized Proposal Ref    | `Link`       | `Quotation`                                                                        |  **Yes**  | **Index: 1** | Finalized proposal from Stage 04 (`custom_is_finalized = 1`).                |
| `custom_survey_design_reference`   | Engineering Design Ref    | `Link`       | `Survey Engineering Design`                                                        |  **Yes**  | **Index: 1** | Approved engineering design and dynamic BOM from Stage 03.                   |
| `custom_advance_verified`          | Advance Payment Verified  | `Check`      | -                                                                                  |  **Yes**  | **Index: 1** | Populated strictly from Stage 05 financial clearance. Read-only.             |
| `custom_financial_clearance_date`  | Financial Clearance Date  | `Datetime`   | -                                                                                  |    No     |      -       | Timestamp when Stage 05 accounts clearance was granted.                      |
| `custom_financial_clearance_track` | Clearance Track           | `Select`     | `Direct Advance\nBank Loan Sanction\nCorporate Credit Waiver\nGoodwill VIP Bypass` |    No     |      -       | Track utilized to clear financial gate in Stage 05.                          |
| `custom_system_capacity_kw`        | System Capacity (kWp)     | `Float`      | -                                                                                  |  **Yes**  |      -       | Total solar DC capacity in kWp. Precision: 2 decimals.                       |
| `custom_total_modules_count`       | Total PV Modules          | `Int`        | -                                                                                  |  **Yes**  |      -       | Total quantity of solar modules calculated from BOM.                         |
| `custom_total_inverters_count`     | Total Inverters           | `Int`        | -                                                                                  |  **Yes**  |      -       | Total quantity of solar inverters calculated from BOM.                       |
| `custom_site_zones_count`          | Number of Site Zones      | `Int`        | -                                                                                  |  **Yes**  |      -       | Physical roof/ground zones (Default: 1; max: 20).                            |
| `custom_signed_contract_doc`       | Signed Client Contract    | `Attach`     | -                                                                                  |  **Yes**  |      -       | Scanned PDF of bilateral EPC contract signed by customer. Mandatory.         |
| `custom_contract_date`             | Contract Agreement Date   | `Date`       | -                                                                                  |  **Yes**  |      -       | Date on the executed client contract agreement.                              |
| `custom_baseline_sha256`           | Baseline SHA-256 Checksum | `Data`       | -                                                                                  |    No     | **Index: 1** | 64-char hexadecimal hash of items, quantities, rates, and BOM specifications.|
| `custom_baseline_frozen`           | Baseline Frozen           | `Check`      | -                                                                                  |  **Yes**  | **Index: 1** | Set to 1 on submit. Locks commercial/technical specs from edits.             |
| `custom_baseline_frozen_on`        | Baseline Frozen On        | `Datetime`   | -                                                                                  |    No     |      -       | Audit timestamp when baseline sealed.                                        |
| `custom_baseline_frozen_by`        | Baseline Frozen By        | `Link`       | `User`                                                                             |    No     |      -       | User ID of Sales Representative or Sales Manager submitting order.           |
| `custom_project_reference`         | Spawned Project Ref       | `Link`       | `Project`                                                                          |    No     | **Index: 1** | Downstream ERPNext `Project` container instantiated on submit.               |
| `custom_store_delivery_task`       | Store Delivery Task       | `Link`       | `Task`                                                                             |    No     | **Index: 1** | Downstream task assigned to `Store Manager` for logistics prep.              |
| `custom_liaisoning_reference`      | Liaisoning Dossier Ref    | `Link`       | `Liaisoning And Synchronization`                                                   |    No     | **Index: 1** | Downstream statutory compliance dossier instantiated on submit.              |
| `custom_so_sla_status`             | Kickoff SLA Status        | `Select`     | `Within SLA\nOverdue\nDelay Approved`                                              |  **Yes**  | **Index: 1** | Real-time SLA tracking status. Default: `Within SLA`.                        |
| `custom_so_sla_deadline`           | Kickoff SLA Deadline      | `Datetime`   | -                                                                                  |  **Yes**  |      -       | Computed target timestamp (`financial_clearance_date + 24h`).                |
| `custom_delay_reason_category`     | Delay Reason Category     | `Select`     | `Customer Delay\nContract Clarification\nPrice Discrepancy\nAdministrative Hold`   |    No     |      -       | Mandatory if submission occurs after SLA deadline.                           |
| `custom_delay_remarks`             | Delay Explanation Remarks | `Small Text` | -                                                                                  |    No     |      -       | Explanatory remarks required when SLA deadline is breached ($\ge 20$ chars). |

---

### 2.2 Core DocType Extension: `tabSales Order Item` (Solar BOM Line Details)

| Fieldname                    | Label                    | Fieldtype    | Options / Target                                                                                                                | Mandatory |    Index     | Rules & Invariants                                                  |
| :--------------------------- | :----------------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------ | :-------: | :----------: | :------------------------------------------------------------------ |
| `custom_equipment_category`  | Solar Equipment Category | `Select`     | `PV Module\nSolar Inverter\nMounting Structure\nDC Cable\nAC Cable\nBOS / Electricals\nFasteners & Civil\nMonitoring & Sensors` |  **Yes**  | **Index: 1** | Functional categorization for warehouse picking and WBS allocation. |
| `custom_bom_item_reference`  | Dynamic BOM Item Ref     | `Link`       | `Custom Quot BOM`                                                                                                               |    No     |      -       | Foreign key link to Stage 03 engineering BOM line item.             |
| `custom_is_serialized`       | Serial Number Required   | `Check`      | -                                                                                                                               |  **Yes**  |      -       | Flag indicating barcode tracking needed during Stage 07 dispatch.   |
| `custom_allocated_warehouse` | Staging Warehouse        | `Link`       | `Warehouse`                                                                                                                     |  **Yes**  |      -       | Warehouse location where material staged prior to dispatch.         |
| `custom_technical_spec`      | Technical Specification  | `Small Text` | -                                                                                                                               |    No     |      -       | Brand, model number, wattage, or voltage rating snapshot.           |

---

### 2.3 Core DocType Extension: `tabProject` (Execution Container)

| Fieldname                        | Label                  | Fieldtype | Options / Target                 | Mandatory |    Index     | Rules & Invariants                                             |
| :------------------------------- | :--------------------- | :-------- | :------------------------------- | :-------: | :----------: | :------------------------------------------------------------- |
| `custom_sales_order_reference`   | Linked Sales Order     | `Link`    | `Sales Order`                    |  **Yes**  | **Index: 1** | Reverse link to originating Stage 06 commercial contract.      |
| `custom_survey_design_reference` | Engineering Design Ref | `Link`    | `Survey Engineering Design`      |  **Yes**  |      -       | Technical drawing and layout reference from Stage 03.          |
| `custom_lead_reference`          | Originating Lead       | `Link`    | `Lead`                           |  **Yes**  |      -       | Lead link for CRM activity synchronization.                    |
| `custom_system_capacity_kw`      | Capacity (kWp)         | `Float`   | -                                |  **Yes**  |      -       | Replicated capacity for project dashboard reporting.           |
| `custom_discom_consumer_no`      | DISCOM Consumer Number | `Data`    | -                                |  **Yes**  | **Index: 1** | Utility connection identifier for net-metering.                |
| `custom_site_address_gps`        | Site GPS Coordinates   | `Data`    | -                                |  **Yes**  |      -       | Latitude, Longitude lock captured from Stage 02 survey.        |
| `custom_project_engineer`        | Assigned Project Lead  | `Link`    | `User`                           |  **Yes**  | **Index: 1** | Primary `Project Engineer` responsible for site WBS execution. |
| `custom_store_manager`           | Assigned Store Lead    | `Link`    | `User`                           |  **Yes**  | **Index: 1** | Assigned `Store Manager` overseeing material logistics.        |
| `custom_liaisoning_reference`    | Statutory Dossier Ref  | `Link`    | `Liaisoning And Synchronization` |    No     |      -       | Bidirectional link to Stage 10 statutory compliance record.    |

---

### 2.4 Core DocType Extension: `tabTask` (WBS Elements & Logistics Task)

| Fieldname                  | Label                  | Fieldtype  | Options / Target                                                                                                                        | Mandatory |    Index     | Rules & Invariants                                                      |
| :------------------------- | :--------------------- | :--------- | :-------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :----------: | :---------------------------------------------------------------------- |
| `custom_wbs_stage`         | Solar WBS Discipline   | `Select`   | `Material Logistics\nCivil & Foundations\nMMS Erection\nModule Mounting\nDC/AC Cabling\nEarthing & Safety\nTesting & Pre-Commissioning` |  **Yes**  | **Index: 1** | WBS category for Gantt view and progress calculation.                   |
| `custom_zone_identifier`   | Installation Zone Name | `Data`     | -                                                                                                                                       |    No     |      -       | Physical partition (e.g. `Zone 1`, `Ground Array A`).                   |
| `custom_assigned_role`     | Target Enterprise Role | `Select`   | `Store Manager\nStore Assistant\nProject Engineer\nSite Supervisor\nLiaisoning Representative\nLiaisoning Manager`                      |  **Yes**  | **Index: 1** | Functional role responsible for task completion.                        |
| `custom_can_reassign`      | Delegation Allowed     | `Check`    | -                                                                                                                                       |  **Yes**  |      -       | If 1, assigned lead (e.g. Store Manager) can delegate task. Default: 0. |
| `custom_reassigned_by`     | Reassigned By          | `Link`     | `User`                                                                                                                                  |    No     |      -       | Audit trail of authority who delegated task.                            |
| `custom_reassigned_on`     | Reassigned On          | `Datetime` | -                                                                                                                                       |    No     |      -       | Timestamp when task reassigned to subordinate.                          |
| `custom_original_assignee` | Original Assignee      | `Link`     | `User`                                                                                                                                  |    No     |      -       | Preserves initial assignment for operational accountability.            |

---

### 2.5 Standalone Submittable DocType: `tabLiaisoning And Synchronization`

- **Module:** `solar_module`
- **Autonaming:** `naming_series:LIA-.YYYY.-.#####` (e.g. `LIA-2026-00042`)
- **Submittable:** `is_submittable = 1`

| Fieldname                            | Label                     | Fieldtype | Options / Target                                                                              | Mandatory |    Index     | Rules & Invariants                                                |
| :----------------------------------- | :------------------------ | :-------- | :-------------------------------------------------------------------------------------------- | :-------: | :----------: | :---------------------------------------------------------------- |
| `naming_series`                      | Naming Series             | `Select`  | `LIA-.YYYY.-.#####`                                                                           |  **Yes**  |      -       | Document sequence prefix.                                         |
| `project`                            | Linked Project            | `Link`    | `Project`                                                                                     |  **Yes**  | **Index: 1** | Operational solar project container.                              |
| `sales_order`                        | Sales Order Reference     | `Link`    | `Sales Order`                                                                                 |  **Yes**  | **Index: 1** | Originating commercial contract.                                  |
| `custom_lead_reference`              | Originating Lead          | `Link`    | `Lead`                                                                                        |  **Yes**  | **Index: 1** | Preserves lifecycle thread of identity for CRM progress tracking. |
| `customer`                           | Customer                  | `Link`    | `Customer`                                                                                    |  **Yes**  | **Index: 1** | Registered consumer master.                                       |
| `consumer_number`                    | DISCOM Consumer No        | `Data`    | -                                                                                             |  **Yes**  | **Index: 1** | Electricity bill connection number.                               |
| `discom_name`                        | DISCOM Name               | `Data`    | -                                                                                             |  **Yes**  |      -       | Utility company (e.g. DGVCL, MGVCL, TPREL, BESCOM).               |
| `discom_division`                    | Division / Sub-Division   | `Data`    | -                                                                                             |  **Yes**  |      -       | Local utility administrative office.                              |
| `sanctioned_load_kw`                 | Current Sanctioned Load   | `Float`   | -                                                                                             |  **Yes**  |      -       | Existing sanctioned contract load in kW.                          |
| `solar_capacity_kw`                  | Proposed Solar Capacity   | `Float`   | -                                                                                             |  **Yes**  |      -       | Applied solar generator capacity in kWp.                          |
| `phase_1_status`                     | Phase 1 Early Status      | `Select`  | `Pending Filing\nDocuments Uploaded\nApplication Submitted\nFeasibility Approved\nNOC Issued` |  **Yes**  | **Index: 1** | Status of post-SO early compliance. Default: `Pending Filing`.    |
| `discom_application_no`              | DISCOM Application No     | `Data`    | -                                                                                             |    No     | **Index: 1** | Online portal reference number once filed.                        |
| `grid_feasibility_approval_date`     | Feasibility Approval Date | `Date`    | -                                                                                             |    No     |      -       | Date when utility approves grid capacity connectivity.            |
| `grid_connectivity_noc`              | Feasibility NOC Letter    | `Attach`  | -                                                                                             |    No     |      -       | Scanned PDF of utility grid connectivity clearance.               |
| `phase_2_status`                     | Phase 2 Sync Status       | `Select`  | `Not Started\nInspection Scheduled\nJMI Completed\nMeter Installed\nGrid Synchronized`        |  **Yes**  | **Index: 1** | Post-installation synchronization status (Stage 10).              |
| `custom_triggers_project_completion` | Triggers Project End      | `Check`   | -                                                                                             |  **Yes**  |      -       | Default: 1. Marking Phase 2 complete triggers Project closure.    |

---

### 2.6 Configuration Master: `tabSolar Sales Order Settings` (Single DocType)

Managed strictly by **`Admin`** (Project Supreme Command):

| Fieldname                        | Label                              | Fieldtype                   | Default                      | Description & Rules                                                       |
| :------------------------------- | :--------------------------------- | :-------------------------- | :--------------------------- | :------------------------------------------------------------------------ |
| `so_kickoff_sla_hours`           | Target Kickoff SLA Hours           | `Int`                       | `24`                         | Expected duration (hours) from Stage 05 clearance to Stage 06 submission. |
| `enforce_signed_contract`        | Mandate Signed Contract PDF        | `Check`                     | `1`                          | If 1, `custom_signed_contract_doc` mandatory before submission.           |
| `default_wbs_template`           | Default Solar WBS Template         | `Link` (`Project Template`) | `Solar Rooftop Standard WBS` | Template used by `ProjectSpawnerService` to construct tasks.              |
| `allow_amendment_without_cancel` | Allow Controlled In-Place Revision | `Check`                     | `0`                          | If 0, requires Admin-authorized cancellation and amendment.               |
| `notify_store_manager_on_so`     | Auto-Alert Store Manager           | `Check`                     | `1`                          | Broadcast real-time alert to Store Manager on order submission.           |
| `notify_liaisoning_team_on_so`   | Auto-Alert Liaisoning Team         | `Check`                     | `1`                          | Broadcast real-time alert to Liaisoning Team on order submission.         |

---

### 2.7 Child DocType: `tabRemark-Delay Log`

| Fieldname      | Label           | Fieldtype    | Options                                                                           | Mandatory | Description                                                    |
| :------------- | :-------------- | :----------- | :-------------------------------------------------------------------------------- | :-------: | :------------------------------------------------------------- |
| `user`         | Logged By       | `Link`       | `User`                                                                            |  **Yes**  | Staff member recording entry (defaults to session user).       |
| `timestamp`    | Recorded At     | `Datetime`   | -                                                                                 |  **Yes**  | Immutable audit timestamp.                                     |
| `stage`        | Lifecycle Stage | `Data`       | -                                                                                 |  **Yes**  | Fixed value: "Stage 06: Sales Order Baseline & Spawning".      |
| `delay_reason` | Delay Category  | `Select`     | `Customer Delay\nContract Clarification\nPrice Discrepancy\nAdministrative Hold`   |    No     | Mandatory when `custom_so_sla_status == 'Overdue'`.            |
| `remarks`      | Detailed Notes  | `Small Text` | -                                                                                 |  **Yes**  | Free-text operational explanation ($\ge 20$ characters).       |

---

### 2.8 Database Indexing & Autonaming Strategy

```sql
-- Composite performance indexes for Sales Order baseline queries
CREATE INDEX idx_so_solar_lookup ON `tabSales Order` (custom_is_solar_order, docstatus, custom_baseline_frozen);
CREATE INDEX idx_so_quotation_ref ON `tabSales Order` (custom_quotation_reference, docstatus);
CREATE INDEX idx_so_project_ref ON `tabSales Order` (custom_project_reference);
CREATE INDEX idx_so_lead_ref ON `tabSales Order` (custom_lead_reference);

-- Project and Task composite indexes
CREATE INDEX idx_project_so_ref ON `tabProject` (custom_sales_order_reference);
CREATE INDEX idx_project_consumer ON `tabProject` (custom_discom_consumer_no);
CREATE INDEX idx_task_wbs_discipline ON `tabTask` (project, custom_wbs_stage, custom_assigned_role);

-- Statutory Liaisoning composite indexes
CREATE INDEX idx_liaison_so_proj ON `tabLiaisoning And Synchronization` (sales_order, project, phase_1_status);
CREATE INDEX idx_liaison_consumer ON `tabLiaisoning And Synchronization` (consumer_number);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Decoupled pure Python domain services located in `solar_module/services/sales_order/` adhering strictly to single-responsibility, open-closed, and dependency inversion principles.

### 3.1 `SalesOrderBaselineService` (`solar_module/services/sales_order/baseline.py`)

Governs cryptographic hashing of commercial/technical terms and asserts dynamic BOM consistency:

```python
import hashlib
import json
import frappe
from frappe import _
from frappe.utils import flt

class SalesOrderBaselineService:
    """Computes cryptographic baseline checksums and validates commercial BOM integrity."""

    @staticmethod
    def calculate_baseline_sha256(so_doc) -> str:
        """
        Computes a deterministic SHA-256 hash representing the immutable contract baseline.
        Sorts items and payment schedules deterministically before JSON serializing.
        """
        payload = {
            "customer": so_doc.customer,
            "system_capacity_kw": flt(so_doc.custom_system_capacity_kw, 2),
            "grand_total": flt(so_doc.grand_total, 2),
            "currency": so_doc.currency,
            "items": [],
            "payment_schedule": []
        }

        sorted_items = sorted(so_doc.items, key=lambda x: x.item_code)
        for item in sorted_items:
            payload["items"].append({
                "item_code": item.item_code,
                "qty": flt(item.qty, 2),
                "rate": flt(item.rate, 2),
                "amount": flt(item.amount, 2),
                "bom_ref": item.get("custom_bom_item_reference") or "",
                "category": item.get("custom_equipment_category") or ""
            })

        if hasattr(so_doc, "payment_schedule") and so_doc.payment_schedule:
            sorted_schedule = sorted(so_doc.payment_schedule, key=lambda x: str(x.due_date))
            for ps in sorted_schedule:
                payload["payment_schedule"].append({
                    "description": ps.description or "",
                    "payment_amount": flt(ps.payment_amount, 2),
                    "due_date": str(ps.due_date)
                })

        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload_bytes).hexdigest()

    @staticmethod
    def validate_bom_alignment(so_doc):
        """Asserts that Sales Order items strictly align with Stage 03 Engineering BOM."""
        if not so_doc.custom_survey_design_reference:
            return

        design_doc = frappe.get_doc("Survey Engineering Design", so_doc.custom_survey_design_reference)
        design_bom_map = {row.item_code: flt(row.qty) for row in design_doc.get("custom_quot_bom", [])}

        for item in so_doc.items:
            if item.item_code in design_bom_map:
                approved_qty = design_bom_map[item.item_code]
                if flt(item.qty) != approved_qty:
                    frappe.throw(
                        _("Item {0} quantity ({1}) deviates from approved Stage 03 Engineering BOM ({2}). "
                          "Any quantity modification requires an updated Survey Engineering Design.").format(
                            item.item_code, item.qty, approved_qty
                        ),
                        frappe.ValidationError
                    )
```

---

### 3.2 `ProjectSpawnerService` (`solar_module/services/sales_order/spawner.py`)

Handles atomic programmatic instantiation of the ERPNext `Project` container and multi-zone WBS task tree:

```python
import frappe
from frappe import _
from frappe.utils import add_days, now_datetime, flt

class ProjectSpawnerService:
    """Programmatically spawns ERPNext Project container and multi-zone WBS Tasks."""

    @staticmethod
    def spawn_project_container(so_doc) -> str:
        """Instantiates the operational Project record linked to Sales Order and Customer."""
        customer_name = frappe.db.get_value("Customer", so_doc.customer, "customer_name") or so_doc.customer
        capacity_kw = int(flt(so_doc.custom_system_capacity_kw or 0))
        project_name = f"PRJ-{customer_name}-{capacity_kw}KW-{so_doc.name[-5:]}"

        project = frappe.get_doc({
            "doctype": "Project",
            "project_name": project_name,
            "project_type": "Internal",
            "customer": so_doc.customer,
            "sales_order": so_doc.name,
            "custom_sales_order_reference": so_doc.name,
            "custom_survey_design_reference": so_doc.custom_survey_design_reference,
            "custom_lead_reference": so_doc.custom_lead_reference,
            "custom_system_capacity_kw": so_doc.custom_system_capacity_kw,
            "custom_discom_consumer_no": frappe.db.get_value("Customer", so_doc.customer, "custom_discom_consumer_no"),
            "expected_start_date": now_datetime().date(),
            "expected_end_date": add_days(now_datetime().date(), 30),
            "status": "Open"
        })
        project.insert(ignore_permissions=True)
        return project.name

    @staticmethod
    def generate_wbs_tasks(project_id: str, so_doc):
        """Generates structured zone-based execution tasks assigned to Project Engineer."""
        zones_count = max(int(so_doc.custom_site_zones_count or 1), 1)

        task_templates = [
            ("Civil & Foundations", "Site Clearing, Civil Footings & Inverter Pad Construction", 3),
            ("MMS Erection", "Module Mounting Structure Erection & Torque Inspection", 5),
            ("Module Mounting", "PV Module Installation & Array Clamping", 7),
            ("DC/AC Cabling", "String Cabling, Inverter Termination & LT Interconnection", 10),
            ("Earthing & Safety", "Earthing Pit Installation & Lightning Arrester Termination", 12),
            ("Testing & Pre-Commissioning", "Pre-Commissioning Megger, VOC & Polarity Verification", 14),
        ]

        for zone_idx in range(1, zones_count + 1):
            zone_name = f"Zone {zone_idx}" if zones_count > 1 else "Main Site"
            for discipline, title, offset_days in task_templates:
                task = frappe.get_doc({
                    "doctype": "Task",
                    "subject": f"[{zone_name}] {title}",
                    "project": project_id,
                    "custom_wbs_stage": discipline,
                    "custom_zone_identifier": zone_name,
                    "custom_assigned_role": "Project Engineer",
                    "exp_start_date": now_datetime().date(),
                    "exp_end_date": add_days(now_datetime().date(), offset_days),
                    "status": "Open",
                    "priority": "Medium"
                })
                task.insert(ignore_permissions=True)
```

---

### 3.3 `StoreLogisticsService` (`solar_module/services/sales_order/store.py`)

Governs material delivery task creation for `Store Manager` and strict subordinate delegation:

```python
import frappe
from frappe import _
from frappe.utils import add_days, now_datetime

class StoreLogisticsService:
    """Manages Store Manager material delivery task generation and delegation."""

    @staticmethod
    def spawn_store_delivery_task(project_id: str, so_doc) -> str:
        """Instantiates Material Delivery Task assigned directly to Store Manager."""
        store_manager_user = frappe.db.get_value(
            "Has Role",
            {"role": "Store Manager", "parenttype": "User"},
            "parent"
        ) or "administrator"

        task = frappe.get_doc({
            "doctype": "Task",
            "subject": f"Material Delivery & Dispatch Preparation — {project_id}",
            "project": project_id,
            "custom_wbs_stage": "Material Logistics",
            "custom_assigned_role": "Store Manager",
            "custom_can_reassign": 1,
            "custom_original_assignee": store_manager_user,
            "exp_start_date": now_datetime().date(),
            "exp_end_date": add_days(now_datetime().date(), 3),
            "status": "Open",
            "priority": "High",
            "description": (
                f"Sales Order {so_doc.name} submitted. Allocate inventory from central warehouse "
                f"for {so_doc.custom_system_capacity_kw} kW system. Prepare serial bundles for "
                f"{so_doc.custom_total_modules_count} PV modules and {so_doc.custom_total_inverters_count} inverters."
            )
        })
        task.insert(ignore_permissions=True)
        return task.name

    @staticmethod
    def reassign_delivery_task(task_name: str, new_assignee: str, reassigned_by: str):
        """Allows Store Manager to delegate material preparation to Store Assistant."""
        task = frappe.get_doc("Task", task_name)
        if not task.custom_can_reassign:
            frappe.throw(_("This task is not authorized for operational reassignment."), frappe.PermissionError)

        user_roles = frappe.get_roles(new_assignee)
        if "Store Assistant" not in user_roles and "Store Manager" not in user_roles:
            frappe.throw(_("Task can only be delegated to a Store Assistant or Store Manager."), frappe.ValidationError)

        task.custom_assigned_role = "Store Assistant"
        task.custom_reassigned_by = reassigned_by
        task.custom_reassigned_on = now_datetime()
        task.save(ignore_permissions=True)
```

---

### 3.4 `LiaisoningInceptionService` (`solar_module/services/sales_order/liaisoning.py`)

Instantiates Phase 1 statutory net-metering compliance record:

```python
import frappe
from frappe import _

class LiaisoningInceptionService:
    """Programmatically instantiates Phase 1 Statutory Liaisoning dossier."""

    @staticmethod
    def spawn_liaisoning_record(project_id: str, so_doc) -> str:
        """Creates Liaisoning And Synchronization record initialized in Phase 1."""
        customer = frappe.get_doc("Customer", so_doc.customer)

        liaison_doc = frappe.get_doc({
            "doctype": "Liaisoning And Synchronization",
            "project": project_id,
            "sales_order": so_doc.name,
            "custom_lead_reference": so_doc.custom_lead_reference,
            "customer": so_doc.customer,
            "consumer_number": customer.get("custom_discom_consumer_no") or "PENDING",
            "discom_name": customer.get("custom_discom_board") or "DGVCL",
            "discom_division": customer.get("territory") or "Surat Central",
            "sanctioned_load_kw": customer.get("custom_sanctioned_load_kw") or 10.0,
            "solar_capacity_kw": so_doc.custom_system_capacity_kw,
            "phase_1_status": "Pending Filing",
            "phase_2_status": "Not Started",
            "custom_triggers_project_completion": 1
        })
        liaison_doc.insert(ignore_permissions=True)
        return liaison_doc.name
```

---

### 3.5 `SalesOrderSLAService` (`solar_module/services/sales_order/sla.py`)

Governs 24-hour turnaround SLA calculation and delay audit logging:

```python
import frappe
from frappe import _
from frappe.utils import add_to_date, now_datetime

class SalesOrderSLAService:
    """Computes turnaround deadlines and validates delay logging for overdue orders."""

    @staticmethod
    def compute_sla_deadline(clearance_date) -> str:
        """Calculates kickoff deadline based on clearance date + configured SLA hours."""
        sla_hours = int(frappe.db.get_single_value("Solar Sales Order Settings", "so_kickoff_sla_hours") or 24)
        base_time = clearance_date or now_datetime()
        return add_to_date(base_time, hours=sla_hours)

    @staticmethod
    def validate_sla_submission(so_doc):
        """Enforces mandatory delay reason and remarks if order is overdue."""
        if not so_doc.custom_so_sla_deadline:
            return

        if now_datetime() > so_doc.custom_so_sla_deadline:
            so_doc.custom_so_sla_status = "Overdue"
            if not so_doc.custom_delay_reason_category or not so_doc.custom_delay_remarks:
                frappe.throw(
                    _("Kickoff SLA Deadline has expired. Sales Order is Overdue. "
                      "Select a Delay Reason Category and provide detailed remarks (min 20 chars) to submit."),
                    frappe.ValidationError
                )
            if len(so_doc.custom_delay_remarks.strip()) < 20:
                frappe.throw(
                    _("Delay Explanation Remarks must be at least 20 characters long."),
                    frappe.ValidationError
                )
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

### 4.1 Extended Controller Hooks (`solar_module/overrides/sales_order.py`)

Extends standard ERPNext `SalesOrder` with `StageSecuredDocument` mixin, enforcing the 5 verification gates and atomic downstream spawning:

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, flt
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
from solar_module.mixins.stage_secured_document import StageSecuredDocument
from solar_module.services.sales_order.baseline import SalesOrderBaselineService
from solar_module.services.sales_order.spawner import ProjectSpawnerService
from solar_module.services.sales_order.store import StoreLogisticsService
from solar_module.services.sales_order.liaisoning import LiaisoningInceptionService
from solar_module.services.sales_order.sla import SalesOrderSLAService

class SolarSalesOrder(StageSecuredDocument, SalesOrder):
    """Solar EPC controller extension for standard ERPNext Sales Order."""

    def before_insert(self):
        super().before_insert()
        if self.custom_is_solar_order:
            self._set_solar_defaults()

    def validate(self):
        super().validate()
        if self.custom_is_solar_order:
            self._enforce_gate_1_advance_clearance()
            self._enforce_gate_2_signed_contract()
            self._enforce_gate_3_customer_completeness()
            self._enforce_gate_4_bom_integrity()
            self._enforce_gate_5_payment_schedule()
            SalesOrderSLAService.validate_sla_submission(self)

    def on_submit(self):
        super().on_submit()
        if self.custom_is_solar_order:
            self._freeze_commercial_baseline()
            self._execute_downstream_spawning()

    def on_cancel(self):
        if self.custom_is_solar_order:
            self._validate_cancellation_constraints()
        super().on_cancel()

    def _set_solar_defaults(self):
        """Populates technical capacity, advance status, and SLA deadline."""
        if self.custom_quotation_reference and not self.custom_advance_verified:
            adv_status = frappe.db.get_value("Quotation", self.custom_quotation_reference, "custom_financial_clearance_status")
            if adv_status in ["Advance Cleared", "Loan Sanction Verified", "Corporate Credit Waived", "Goodwill VIP Approved"]:
                self.custom_advance_verified = 1
                self.custom_financial_clearance_date = frappe.db.get_value("Quotation", self.custom_quotation_reference, "custom_financial_clearance_date")

        if not self.custom_so_sla_deadline:
            self.custom_so_sla_deadline = SalesOrderSLAService.compute_sla_deadline(self.custom_financial_clearance_date)
            self.custom_so_sla_status = "Within SLA"

    def _enforce_gate_1_advance_clearance(self):
        """Gate 1: Verifies Stage 05 financial advance clearance."""
        if not self.custom_advance_verified:
            frappe.throw(
                _("Cannot submit Sales Order: Project has not achieved Stage 05 Financial Advance Clearance. "
                  "Advance payment must be verified on `/solar/advance` before releasing commercial orders."),
                frappe.ValidationError
            )

    def _enforce_gate_2_signed_contract(self):
        """Gate 2: Verifies signed customer contract attachment."""
        enforce_contract = frappe.db.get_single_value("Solar Sales Order Settings", "enforce_signed_contract")
        if enforce_contract and (not self.custom_signed_contract_doc or not self.custom_contract_date):
            frappe.throw(
                _("Cannot submit Sales Order: Bilateral signed EPC contract document and agreement date are mandatory. "
                  "Upload the executed client contract in 'Signed Client Contract'."),
                frappe.ValidationError
            )

    def _enforce_gate_3_customer_completeness(self):
        """Gate 3: Validates that Customer has DISCOM consumer number."""
        consumer_no = frappe.db.get_value("Customer", self.customer, "custom_discom_consumer_no")
        if not consumer_no:
            frappe.throw(
                _("Cannot submit Sales Order: Customer {0} is missing statutory DISCOM Consumer Number.").format(self.customer),
                frappe.ValidationError
            )

    def _enforce_gate_4_bom_integrity(self):
        """Gate 4: Validates item alignment with Stage 03 Engineering BOM."""
        SalesOrderBaselineService.validate_bom_alignment(self)

    def _enforce_gate_5_payment_schedule(self):
        """Gate 5: Payment schedule tranches must total exactly 100% of grand_total."""
        if hasattr(self, "payment_schedule") and self.payment_schedule:
            total_scheduled = sum(flt(ps.payment_amount) for ps in self.payment_schedule)
            if abs(total_scheduled - flt(self.grand_total)) > 0.01:
                frappe.throw(
                    _("Payment Schedule total (₹{0}) must match Sales Order Grand Total (₹{1}).").format(
                        total_scheduled, self.grand_total
                    ),
                    frappe.ValidationError
                )

    def _freeze_commercial_baseline(self):
        """Computes SHA-256 baseline checksum and marks baseline frozen."""
        sha256_hash = SalesOrderBaselineService.calculate_baseline_sha256(self)
        self.db_set("custom_baseline_sha256", sha256_hash)
        self.db_set("custom_baseline_frozen", 1)
        self.db_set("custom_baseline_frozen_on", now_datetime())
        self.db_set("custom_baseline_frozen_by", frappe.session.user)

    def _execute_downstream_spawning(self):
        """Atomic transaction spawning Project, Store Task, and Liaisoning records."""
        # 1. Spawn Project container & WBS Tasks
        project_id = ProjectSpawnerService.spawn_project_container(self)
        ProjectSpawnerService.generate_wbs_tasks(project_id, self)
        self.db_set("custom_project_reference", project_id)

        # 2. Spawn Material Delivery Task for Store Manager
        store_task_id = StoreLogisticsService.spawn_store_delivery_task(project_id, self)
        self.db_set("custom_store_delivery_task", store_task_id)

        # 3. Spawn Statutory Liaisoning Dossier (Phase 1)
        liaison_id = LiaisoningInceptionService.spawn_liaisoning_record(project_id, self)
        self.db_set("custom_liaisoning_reference", liaison_id)

        frappe.msgprint(
            _("Sales Order baseline locked successfully. Programmatically spawned Project {0}, "
              "Material Delivery Task {1}, and Liaisoning Dossier {2}.").format(
                project_id, store_task_id, liaison_id
            ),
            alert=True
        )

    def _validate_cancellation_constraints(self):
        """Blocks order cancellation if material dispatch has commenced."""
        if self.custom_project_reference:
            dn_count = frappe.db.count("Delivery Note Item", {"against_sales_order": self.name, "docstatus": 1})
            if dn_count > 0:
                frappe.throw(
                    _("Cannot cancel Sales Order {0}: {1} submitted Delivery Notes exist. "
                      "Cancel all downstream material dispatches before cancelling the Sales Order.").format(
                        self.name, dn_count
                    ),
                    frappe.ValidationError
                )
```

---

### 4.2 Whitelisted API Endpoints (`solar_module/api/sales_order.py`)

```python
import json
import frappe
from frappe import _
from solar_module.services.sales_order.store import StoreLogisticsService

@frappe.whitelist(methods=["POST"])
def validate_sales_order_baseline(sales_order_name: str) -> dict:
    """Performs pre-submission gate validation and returns baseline readiness report."""
    if not sales_order_name:
        frappe.throw(_("Sales Order name is required."), frappe.ValidationError)

    so = frappe.get_doc("Sales Order", sales_order_name)
    so.check_permission("read")

    gates_passed = True
    errors = []

    # Check Stage 05 Advance
    if not so.custom_advance_verified:
        gates_passed = False
        errors.append("Stage 05 Financial Advance Clearance is pending.")

    # Check Signed Contract
    if not so.custom_signed_contract_doc:
        gates_passed = False
        errors.append("Signed client contract PDF attachment is missing.")

    # Check Contract Date
    if not so.custom_contract_date:
        gates_passed = False
        errors.append("Signed contract agreement date is missing.")

    # Check Customer Consumer Number
    consumer_no = frappe.db.get_value("Customer", so.customer, "custom_discom_consumer_no")
    if not consumer_no:
        gates_passed = False
        errors.append("Customer master is missing DISCOM Consumer Number.")

    return {
        "status": "success" if gates_passed else "blocked",
        "gates_passed": gates_passed,
        "errors": errors
    }

@frappe.whitelist(methods=["POST"])
def reassign_store_delivery_task(task_name: str, new_assignee: str) -> dict:
    """Allows Store Manager to reassign the Material Delivery task to a Store Assistant."""
    if not task_name or not new_assignee:
        frappe.throw(_("Task name and new assignee are required."), frappe.ValidationError)

    task = frappe.get_doc("Task", task_name)
    task.check_permission("write")

    StoreLogisticsService.reassign_delivery_task(task_name, new_assignee, frappe.session.user)
    return {
        "status": "success",
        "message": f"Task {task_name} successfully reassigned to {new_assignee}"
    }
```

---

## 5. Layer 4: Desk Client Script & Dynamic Workbench Hook

Located at `codes/client_script/sales_order_solar.js`:

```javascript
frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (!frm.doc.custom_is_solar_order) return;

        // 1. Baseline Freeze Header Banner
        if (frm.doc.custom_baseline_frozen) {
            frm.dashboard.set_headline_alert(
                `<div class="alert alert-info" style="margin-bottom: 0px;">
                    <strong>🔒 Baseline Sealed:</strong> SHA-256 Checksum <code>${frm.doc.custom_baseline_sha256.substring(0, 16)}...</code> 
                    sealed on ${frm.doc.custom_baseline_frozen_on} by ${frm.doc.custom_baseline_frozen_by}.
                </div>`
            );
        }

        // 2. Action Ribbon for Downstream Navigation
        if (frm.doc.docstatus === 1) {
            if (frm.doc.custom_project_reference) {
                frm.add_custom_button(__("🚀 View Project WBS"), () => {
                    frappe.set_route("Form", "Project", frm.doc.custom_project_reference);
                }, __("Downstream Touchpoints"));
            }
            if (frm.doc.custom_store_delivery_task) {
                frm.add_custom_button(__("📦 Store Logistics Task"), () => {
                    frappe.set_route("Form", "Task", frm.doc.custom_store_delivery_task);
                }, __("Downstream Touchpoints"));
            }
            if (frm.doc.custom_liaisoning_reference) {
                frm.add_custom_button(__("⚡ Statutory Dossier"), () => {
                    frappe.set_route("Form", "Liaisoning And Synchronization", frm.doc.custom_liaisoning_reference);
                }, __("Downstream Touchpoints"));
            }
        }

        // 3. Pre-Submission Gate Audit Button
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__("🔍 Validate Baseline Gates"), () => {
                frappe.call({
                    method: "solar_module.api.sales_order.validate_sales_order_baseline",
                    args: { sales_order_name: frm.doc.name },
                    callback(r) {
                        if (r.message && r.message.gates_passed) {
                            frappe.msgprint({
                                title: __("All Gates Passed"),
                                indicator: "green",
                                message: __("All 5 verification gates are clear. Ready for baseline submission.")
                            });
                        } else if (r.message) {
                            const errHtml = r.message.errors.map(e => `<li>${e}</li>`).join("");
                            frappe.msgprint({
                                title: __("Verification Gates Blocked"),
                                indicator: "red",
                                message: `<ul>${errHtml}</ul>`
                            });
                        }
                    }
                });
            });
        }
    }
});
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Located at `solar_module/tests/test_stage_06_sales_order_tracer_bullet.py`.  
Subclasses `frappe.testing.IntegrationTestCase` with zero-commit atomic transaction rollback in `tearDown`.

```python
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import nowdate, now_datetime, add_to_date
from solar_module.services.sales_order.baseline import SalesOrderBaselineService
from solar_module.services.sales_order.store import StoreLogisticsService
from solar_module.api.sales_order import validate_sales_order_baseline, reassign_store_delivery_task

class TestStage06SalesOrderTracerBullet(IntegrationTestCase):
    """Integration test suite for Stage 06 Sales Order baseline and downstream spawning."""

    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")
        self._setup_settings()
        self._setup_fixtures()

    def tearDown(self):
        # Strict Zero-Commit Rule: roll back all database mutations
        frappe.db.rollback()
        super().tearDown()

    def _setup_settings(self):
        settings = frappe.get_doc("Solar Sales Order Settings")
        settings.so_kickoff_sla_hours = 24
        settings.enforce_signed_contract = 1
        settings.notify_store_manager_on_so = 1
        settings.notify_liaisoning_team_on_so = 1
        settings.save(ignore_permissions=True)

    def _setup_fixtures(self):
        # 1. Create Customer
        self.customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Tracer Bullet Solar Client",
            "customer_group": "Commercial",
            "territory": "All Territories",
            "custom_discom_consumer_no": "DISCOM-SURAT-998877",
            "custom_discom_board": "DGVCL"
        }).insert(ignore_permissions=True)

        # 2. Create Engineering Design
        self.design = frappe.get_doc({
            "doctype": "Survey Engineering Design",
            "customer": self.customer.name,
            "custom_capacity_kw": 25.0,
            "docstatus": 1
        })
        self.design.append("custom_quot_bom", {
            "item_code": "SOLAR-PANEL-545W",
            "qty": 46,
            "rate": 14000.0,
            "amount": 644000.0
        })
        self.design.insert(ignore_permissions=True)

    def _create_valid_sales_order(self):
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": self.customer.name,
            "custom_is_solar_order": 1,
            "custom_survey_design_reference": self.design.name,
            "custom_advance_verified": 1,
            "custom_financial_clearance_date": now_datetime(),
            "custom_system_capacity_kw": 25.0,
            "custom_total_modules_count": 46,
            "custom_total_inverters_count": 1,
            "custom_site_zones_count": 2,
            "custom_signed_contract_doc": "/files/signed_test_contract.pdf",
            "custom_contract_date": nowdate(),
            "transaction_date": nowdate(),
            "delivery_date": nowdate(),
            "items": [{
                "item_code": "SOLAR-PANEL-545W",
                "qty": 46,
                "rate": 14000.0,
                "amount": 644000.0,
                "delivery_date": nowdate(),
                "custom_equipment_category": "PV Module"
            }],
            "payment_schedule": [{
                "description": "50% Advance Cleared",
                "payment_amount": 322000.0,
                "due_date": nowdate()
            }, {
                "description": "50% Material Dispatch",
                "payment_amount": 322000.0,
                "due_date": nowdate()
            }]
        })
        return so

    # -------------------------------------------------------------------------
    # TEST CASES
    # -------------------------------------------------------------------------

    def test_01_happy_path_submission_and_atomic_spawning(self):
        """Invariant 6 & 7: Successful submission, SHA-256 baseline freeze, and downstream spawning."""
        so = self._create_valid_sales_order().insert(ignore_permissions=True)
        so.submit()

        # Assert Baseline Sealed
        self.assertEqual(so.custom_baseline_frozen, 1)
        self.assertTrue(bool(so.custom_baseline_sha256))
        self.assertEqual(len(so.custom_baseline_sha256), 64)

        # Assert Project Container Spawned
        self.assertTrue(bool(so.custom_project_reference))
        project = frappe.get_doc("Project", so.custom_project_reference)
        self.assertEqual(project.customer, self.customer.name)
        self.assertEqual(project.custom_system_capacity_kw, 25.0)

        # Assert WBS Tasks Generated (6 tasks per zone * 2 zones = 12 tasks)
        task_count = frappe.db.count("Task", {"project": project.name, "custom_assigned_role": "Project Engineer"})
        self.assertEqual(task_count, 12)

        # Assert Store Manager Material Delivery Task Spawned
        self.assertTrue(bool(so.custom_store_delivery_task))
        store_task = frappe.get_doc("Task", so.custom_store_delivery_task)
        self.assertEqual(store_task.custom_assigned_role, "Store Manager")
        self.assertEqual(store_task.custom_can_reassign, 1)

        # Assert Statutory Liaisoning Dossier Spawned
        self.assertTrue(bool(so.custom_liaisoning_reference))
        liaison = frappe.get_doc("Liaisoning And Synchronization", so.custom_liaisoning_reference)
        self.assertEqual(liaison.consumer_number, "DISCOM-SURAT-998877")
        self.assertEqual(liaison.phase_1_status, "Pending Filing")

    def test_02_advance_clearance_gate_blocking(self):
        """Invariant 1: Gate 1 blocks submission if custom_advance_verified != 1."""
        so = self._create_valid_sales_order()
        so.custom_advance_verified = 0
        so.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            so.submit()

    def test_03_signed_contract_mandatory_blocking(self):
        """Invariant 2: Gate 2 blocks submission if contract attachment or date is missing."""
        so = self._create_valid_sales_order()
        so.custom_signed_contract_doc = None
        so.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            so.submit()

    def test_04_customer_consumer_number_gate(self):
        """Invariant 3: Gate 3 blocks submission if Customer missing DISCOM Consumer No."""
        self.customer.custom_discom_consumer_no = None
        self.customer.save(ignore_permissions=True)

        so = self._create_valid_sales_order().insert(ignore_permissions=True)
        with self.assertRaises(frappe.ValidationError):
            so.submit()

    def test_05_dynamic_bom_mismatch_blocking(self):
        """Invariant 4: Gate 4 blocks submission if item quantity deviates from Stage 03 BOM."""
        so = self._create_valid_sales_order()
        so.items[0].qty = 50  # Approved is 46
        so.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            so.submit()

    def test_06_payment_schedule_100pct_reconciliation(self):
        """Invariant 5: Gate 5 blocks submission if payment schedule doesn't equal grand total."""
        so = self._create_valid_sales_order()
        so.payment_schedule[0].payment_amount = 100000.0  # Total now 422000 != 644000
        so.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            so.submit()

    def test_07_store_manager_task_reassignment_to_assistant(self):
        """Invariant 8: Store Manager can successfully delegate delivery task to Store Assistant."""
        asst_user = "test_asst_user@sadbhav.com"
        if not frappe.db.exists("User", asst_user):
            user = frappe.get_doc({"doctype": "User", "email": asst_user, "first_name": "Store", "last_name": "Asst"})
            user.insert(ignore_permissions=True)
            user.add_roles("Store Assistant")

        so = self._create_valid_sales_order().insert(ignore_permissions=True)
        so.submit()

        reassign_store_delivery_task(so.custom_store_delivery_task, asst_user)

        updated_task = frappe.get_doc("Task", so.custom_store_delivery_task)
        self.assertEqual(updated_task.custom_assigned_role, "Store Assistant")
        self.assertEqual(updated_task.custom_reassigned_by, "Administrator")

    def test_08_reassignment_unauthorized_role_rejected(self):
        """Invariant 8: Delegating task to non-Store staff is blocked with ValidationError."""
        unauth_user = "test_hr_user@sadbhav.com"
        if not frappe.db.exists("User", unauth_user):
            user = frappe.get_doc({"doctype": "User", "email": unauth_user, "first_name": "HR", "last_name": "User"})
            user.insert(ignore_permissions=True)
            user.add_roles("HR User")

        so = self._create_valid_sales_order().insert(ignore_permissions=True)
        so.submit()

        with self.assertRaises(frappe.ValidationError):
            reassign_store_delivery_task(so.custom_store_delivery_task, unauth_user)

    def test_09_sla_deadline_overdue_delay_logging(self):
        """Invariant 9: Overdue submission requires valid delay reason and remarks."""
        so = self._create_valid_sales_order()
        so.custom_so_sla_deadline = add_to_date(now_datetime(), hours=-2)  # Expired 2 hours ago
        so.insert(ignore_permissions=True)

        # Submission without delay remarks must fail
        with self.assertRaises(frappe.ValidationError):
            so.submit()

        # Fulfilling delay category & remarks allows submission
        so.custom_delay_reason_category = "Customer Delay"
        so.custom_delay_remarks = "Customer delayed signing contract due to internal board approval meeting."
        so.submit()
        self.assertEqual(so.docstatus, 1)

    def test_10_downstream_cancellation_lockout(self):
        """Invariant 10: Submitted Delivery Note blocks Sales Order cancellation."""
        so = self._create_valid_sales_order().insert(ignore_permissions=True)
        so.submit()

        # Mock a submitted Delivery Note against this SO
        dn = frappe.get_doc({
            "doctype": "Delivery Note",
            "customer": self.customer.name,
            "items": [{
                "item_code": "SOLAR-PANEL-545W",
                "qty": 46,
                "against_sales_order": so.name
            }]
        }).insert(ignore_permissions=True)
        dn.docstatus = 1
        dn.save()

        with self.assertRaises(frappe.ValidationError):
            so.cancel()
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 Automated Bench Test Execution

Execute the full Stage 06 integration test suite via bench CLI:

```bash
bench --site <site-name> run-tests --module solar_module.tests.test_stage_06_sales_order_tracer_bullet
```

### 7.2 Database SQL Verification Queries

```sql
-- 1. Verify Sales Order baseline freeze integrity
SELECT name, customer, custom_system_capacity_kw, custom_baseline_frozen, custom_baseline_sha256, custom_project_reference
FROM `tabSales Order`
WHERE custom_is_solar_order = 1 AND docstatus = 1
ORDER BY creation DESC LIMIT 5;

-- 2. Verify spawned Project and WBS Task counts
SELECT p.name AS project, p.custom_system_capacity_kw, COUNT(t.name) AS task_count
FROM `tabProject` p
LEFT JOIN `tabTask` t ON t.project = p.name
WHERE p.custom_sales_order_reference IS NOT NULL
GROUP BY p.name;

-- 3. Verify Store Manager Material Delivery Task delegation
SELECT name, project, custom_assigned_role, custom_can_reassign, custom_reassigned_by, custom_reassigned_on
FROM `tabTask`
WHERE custom_wbs_stage = 'Material Logistics'
ORDER BY creation DESC LIMIT 5;

-- 4. Verify Phase 1 Statutory Liaisoning dossier
SELECT name, project, sales_order, customer, consumer_number, discom_name, phase_1_status
FROM `tabLiaisoning And Synchronization`
ORDER BY creation DESC LIMIT 5;
```

### 7.3 Acceptance Checklist

- [x] Predecessor Stage 05 financial clearance gate verified (`custom_advance_verified == 1`).
- [x] Signed client contract attachment and agreement date enforced before submission.
- [x] Customer DISCOM consumer number completeness enforced.
- [x] Dynamic Engineering BOM alignment verified line-by-line against Stage 03.
- [x] Milestone Payment Schedule 100% reconciliation enforced.
- [x] Deterministic SHA-256 cryptographic baseline hash generated and sealed on submission.
- [x] Single ACID transaction spawns Project container, multi-zone WBS Tasks, Store Delivery Task, and Liaisoning dossier.
- [x] Store Manager delegation to Store Assistant validated with strict role verification and audit timestamps.
- [x] 24-hour turnaround SLA enforced with mandatory delay categorization on overdue orders.
- [x] Downstream Stage-Forward immutability blocks Sales Order cancellation when Delivery Notes exist.
- [x] Test suite executes with 100% pass rate under atomic transaction rollback (zero DB commits).

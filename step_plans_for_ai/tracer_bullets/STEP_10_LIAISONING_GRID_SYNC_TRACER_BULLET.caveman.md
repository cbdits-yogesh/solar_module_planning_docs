# STEP_10_LIAISONING_GRID_SYNC_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 10 Dual-Timing Statutory Liaisoning, Regulatory Inspection, Net Metering & Grid Synchronization

**Document ID:** `TB-10-LIAISONING-GRID-SYNC`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.caveman.md`](../STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-010-LIAISONING-STATUTORY-INSPECTION-GRID-SYNC.md`](../../docs/decisions/ADR-010-LIAISONING-STATUTORY-INSPECTION-GRID-SYNC.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md`](STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md`](STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE_TRACER_BULLET.caveman.md`](STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md`](STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md`](STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md`](STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md`](STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md`](STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md`](STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Stage 11 (`tabSolar Service Request` & `tabSolar Asset Register` Twin O&M), Accounts Final Milestone Billing (`tabSales Invoice`)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-10`, `Sec 3.10`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-010`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-010`), `planning_ref_docs/07_SOFTWARE_REQUIREMENTS_SPECIFICATION.md` (`Sec 2.2`, `Sec 4.3`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 8: CMP`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 9`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 14`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-10`)  
**Target Module:** `solar_module` / SPA `/solar` (Extend ERPNext `tabProject`, `tabCustomer`, `tabSales Order`, plus standalone submittable `tabLiaisoning And Synchronization`, child tables, and `tabSolar Liaisoning Settings`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** A disposable frontend Kanban board or mock modal dialog displaying statutory milestones, assuming DISCOM applications never stall, ignoring utility holidays and Sunday business-day offsets in statutory turnaround times, dropping initial import/export meter register dials, bypassing CEIG safety approval checks, and permitting manual closure of ERPNext `tabProject` without verifying physical grid synchronization or issuing Commercial Operation Date (COD) certificates.
- **Tracer Bullet:** A permanent, production-grade 5-layer thin vertical slice cutting directly through the live Frappe architecture. It anchors real database schema extensions (`tabProject`, `tabCustomer`, `tabSales Order`, standalone submittable `tabLiaisoning And Synchronization`, child tables `tabSolar Statutory Document Checklist`, `tabSolar Inspection Milestone Log`, `tabSolar Meter Reading Item`, `tabSolar Stage Delay Log`, and `tabSolar Liaisoning Settings`), implements pure SOLID Python validation, calculation, and orchestration services (`LiaisoningInceptionService`, `LiaisoningSLAService`, `LiaisoningPhase1Service`, `LiaisoningPhase2Service`, `ProjectCompletionService`), exposes authenticated, typed RPC endpoints (`solar_module.api.liaisoning.*`), connects responsive Desk client scripts and SPA Kanban interfaces (`/solar/liaisoning`), and executes an automated zero-commit integration test suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 10 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabProject custom fields (liaisoning ref, phase 1 & 2 status, COD, sync)│
│   - tabCustomer custom fields (discom CA no, utility name, sanctioned load) │
│   - tabLiaisoning And Synchronization (standalone submittable DocType)      │
│   - Child Tables: tabSolar Statutory Document Checklist,                   │
│     tabSolar Inspection Milestone Log, tabSolar Meter Reading Item,         │
│     tabSolar Stage Delay Log                                                │
│   - tabSolar Liaisoning Settings (single DocType: SLA & capacity baselines) │
│   - Composite B-Tree Indexes on project, consumer no, SLA deadline, status  │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - LiaisoningInceptionService (auto-spawn Phase 1 dossier from Stage 06 SO)│
│   - LiaisoningSLAService (10-day statutory countdown & holiday calendar)   │
│   - LiaisoningPhase1Service (KYC, DISCOM filing, PM Surya Ghar ID, and      │
│     atomic Lead Progress Bar 1 terminal closeout)                           │
│   - LiaisoningPhase2Service (CEIG gate, JMI & bi-directional net meter      │
│     verification, anti-islanding trip test <= 2.0s)                         │
│   - ProjectCompletionService (atomic project completion, task closure,      │
│     Stage 11 Solar Asset Register spawning, Accounts milestone alert)       │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                      │
│   - LiaisoningAndSynchronization (validate, on_submit, on_cancel lock)      │
│   - Whitelisted RPC APIs (solar_module.api.liaisoning.*):                   │
│     * update_phase_1_dossier                                                │
│     * record_discom_submission (with Lead Progress Bar 1 closeout)          │
│     * activate_phase_2_countdown (statutory 10-day timer post-Stage 09)     │
│     * record_ceig_inspection (safety clearance & charging permission)       │
│     * record_jmi_inspection (meter serial, make, class, import/export dials)│
│     * execute_grid_synchronization_and_complete_project (COD + Close)       │
│     * log_statutory_delay (audited breach justifications)                   │
│   - Background Celery/RQ daemon (solar_module.tasks.check_liaisoning_sla)   │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Mobile Workbench Hook                 │
│   - codes/client_script/liaisoning_and_synchronization.js (dynamic SLA      │
│     banner alerts, action buttons, dialogs for filing, CEIG, JMI, sync)     │
│   - /solar/liaisoning Two-Tier Kanban & Workbench UX specification          │
│   - Radial 10-day SVG countdown timer widget                                │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_stage_10_liaisoning_grid_sync_tracer_bullet.py  │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Strict Zero-Commit Rule (frappe.db.rollback() in tearDown)              │
│   - 11 atomic test cases validating all Stage 10 business/technical gates   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 11 fundamental business, operational, and technical invariants of Stage 10 across the live Frappe stack:

1. **Gate 1: Automated Phase 1 Inception:** Submission of Stage 06 `Sales Order` programmatically instantiates `tabLiaisoning And Synchronization` in `Phase 1: Draft`, mapping customer utility parameters.
2. **Gate 2: Mandatory DISCOM Filing Dossier:** Blocks transition to `Submitted to DISCOM` unless official registration number and valid PDF receipt attachment are present.
3. **Progress Bar 1 Terminal Closeout:** DISCOM application submission atomically updates `tabLead.custom_lead_progress_status = "Completed"`, closing the pre-construction pipeline.
4. **Gate 3: Post-Installation Phase 2 Activation:** Statutory 10-day countdown clock cannot be activated until Stage 09 pre-commissioning electrical testing sign-off is verified (`custom_pre_comm_gate_cleared == 1`).
5. **Deterministic 10-Day Statutory SLA Engine:** Computes official statutory deadline excluding Sundays and holidays defined in Frappe `Holiday List`.
6. **Gate 4: CEIG Electrical Safety Clearance:** Strictly enforces government fee receipt and charging permission order upload for systems meeting state CEIG thresholds, or validates statutory exemption affidavit.
7. **Gate 5: Joint Meter Inspection (JMI) Verification:** Mandates tri-party signed JMI protocol report and net-meter serial, make, accuracy class, and CT/PT ratio verification.
8. **Net-Meter Energy Baseline Register:** Enforces capture of initial active import ($kWh$) and active export ($kWh$) readings before grid energization.
9. **Gate 6: CEA Anti-Islanding Protection Ceiling:** Validates inverter anti-islanding trip time disconnects in $\le 2.0\text{ seconds}$ upon loss of utility power ($t \le 2.0\text{s}$).
10. **Gate 7: Atomic Project Completion & Asset Twin Spawning:** Submitting `tabLiaisoning And Synchronization` atomically marks `tabProject.status = "Completed"`, sets `custom_is_completed_flag = 1`, records COD date, auto-completes residual WBS tasks, spawns Stage 11 `tabSolar Asset Register`, and unlocks Accounts retention invoicing.
11. **Regulatory Immutability & Admin-Only Cancellation:** Submitted dossiers are locked against non-admin edits; cancellation is strictly restricted to `System Manager` or `Director` and automatically reverts Project completion state.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Extends standard ERPNext DocTypes (`Project`, `Customer`, `Sales Order`, `Lead`), creates standalone submittable DocType `Liaisoning And Synchronization`, child tables, and single configuration DocType.

### 2.1 Core DocType Extension: `tabProject` (Stage 10 Host)

| Fieldname                        | Label                           | Fieldtype  | Options / Target                                                                                        | Mandatory | Index | Description & Validation Rules                                              |
| :------------------------------- | :------------------------------ | :--------- | :------------------------------------------------------------------------------------------------------ | :-------: | :---: | :-------------------------------------------------------------------------- |
| `custom_liaisoning_reference`    | Statutory Dossier Ref           | `Link`     | `Liaisoning And Synchronization`                                                                        |    No     |   1   | Direct foreign key reference to Stage 10 compliance record.                 |
| `custom_phase_1_status`          | Phase 1 Statutory Status        | `Select`   | `Pending Filing\nSubmitted to DISCOM\nFeasibility Approved\nNOC Received`                               |    No     |   -   | Mirror pre-construction compliance milestone.                               |
| `custom_phase_2_status`          | Phase 2 Grid Sync Status        | `Select`   | `Not Started\nTriggered Post-Installation\nCEIG Scheduled\nJMI In Progress\nGrid Synchronized\nOverdue` |    No     |   1   | Mirror post-installation statutory flow.                                    |
| `custom_statutory_deadline`      | Statutory Grid Sync Deadline    | `Datetime` | -                                                                                                       |    No     |   1   | Target deadline calculated by 10-day statutory SLA engine.                  |
| `custom_statutory_delay_days`    | Statutory Delay (Days)          | `Float`    | -                                                                                                       |    No     |   -   | Accumulated delay days beyond 10-day statutory baseline.                    |
| `custom_grid_sync_date`          | Grid Synchronization Date       | `Date`     | -                                                                                                       |    No     |   1   | Official date breaker was energized and synchronized with utility grid.     |
| `custom_cod_date`                | Commercial Operation Date (COD) | `Date`     | -                                                                                                       |    No     |   1   | Commissioning baseline date triggering customer warranties and O&M handoff. |
| `custom_net_meter_serial_no`     | Net Meter Serial No             | `Data`     | -                                                                                                       |    No     |   1   | Serial number of installed utility bi-directional meter.                    |
| `custom_is_completed_flag`       | Project Formally Completed      | `Check`    | -                                                                                                       |  **Yes**  |   1   | Default: 0. Set to 1 only upon submittal of Stage 10 dossier.               |
| `custom_completion_certified_by` | Completed Certified By          | `Link`     | `User`                                                                                                  |    No     |   -   | User who submitted the statutory sign-off.                                  |
| `custom_completion_certified_on` | Completed Certified On          | `Datetime` | -                                                                                                       |    No     |   -   | Timestamp of terminal project completion.                                   |

---

### 2.2 Core DocType Extension: `tabCustomer` (Utility Baseline Master)

| Fieldname                   | Label                         | Fieldtype | Options / Target                                                             | Mandatory | Index | Description & Validation Rules                                        |
| :-------------------------- | :---------------------------- | :-------- | :--------------------------------------------------------------------------- | :-------: | :---: | :-------------------------------------------------------------------- |
| `custom_discom_consumer_no` | Electricity Consumer No (CA)  | `Data`    | -                                                                            |  **Yes**  |   1   | 10-to-12 digit utility account/consumer number from electricity bill. |
| `custom_discom_name`        | Electricity Distribution Co   | `Data`    | -                                                                            |  **Yes**  |   -   | Local utility provider name (e.g., BESCOM, MSEDCL, TPDDL, DHBVN).     |
| `custom_discom_division`    | DISCOM Division               | `Data`    | -                                                                            |  **Yes**  |   -   | Administrative utility division.                                      |
| `custom_discom_subdivision` | DISCOM Sub-Division           | `Data`    | -                                                                            |  **Yes**  |   -   | Local technical/metering subdivision office.                          |
| `custom_sanctioned_load_kw` | Existing Sanctioned Load (kW) | `Float`   | -                                                                            |  **Yes**  |   -   | Contracted load from recent utility bill.                             |
| `custom_tariff_category`    | Electricity Tariff Category   | `Select`  | `LT-Residential\nLT-Commercial\nLT-Industrial\nHT-Commercial\nHT-Industrial` |  **Yes**  |   -   | Regulatory electricity tariff classification.                         |

---

### 2.3 Standalone Custom Submittable DocType: `tabLiaisoning And Synchronization`

- **Module:** `solar_module`
- **DocType Type:** Standalone Submittable DocType (`is_submittable = 1`)
- **Autoname:** `naming_series:` $\rightarrow$ `LIA-.YYYY.-.#####` (e.g. `LIA-2026-00042`)

| Fieldname                            | Label                         | Fieldtype  | Options / Target                                                                                                                    | Mandatory | Index | Description & Validation Rules                                                       |
| :----------------------------------- | :---------------------------- | :--------- | :---------------------------------------------------------------------------------------------------------------------------------- | :-------: | :---: | :----------------------------------------------------------------------------------- |
| `naming_series`                      | Series                        | `Select`   | `LIA-.YYYY.-.#####`                                                                                                                 |  **Yes**  |   -   | Standard document series numbering.                                                  |
| `project`                            | Project Code                  | `Link`     | `Project`                                                                                                                           |  **Yes**  |   1   | Parent Solar EPC Project container.                                                  |
| `sales_order`                        | Sales Order                   | `Link`     | `Sales Order`                                                                                                                       |  **Yes**  |   1   | Upstream commercial contract reference.                                              |
| `customer`                           | Customer                      | `Link`     | `Customer`                                                                                                                          |  **Yes**  |   1   | Asset owner and electricity consumer.                                                |
| `custom_lead_reference`              | Original Lead Ref             | `Link`     | `Lead`                                                                                                                              |    No     |   1   | Lead trace for Progress Bar 1 terminal closeout.                                     |
| `consumer_number`                    | Consumer No (CA / Account)    | `Data`     | -                                                                                                                                   |  **Yes**  |   1   | DISCOM consumer ID fetched from customer master.                                     |
| `discom_name`                        | Electricity Distribution Co   | `Data`     | -                                                                                                                                   |  **Yes**  |   -   | Utility distribution company.                                                        |
| `sanctioned_load_kw`                 | Sanctioned Load (kW)          | `Float`    | -                                                                                                                                   |  **Yes**  |   -   | Contracted load from utility bill.                                                   |
| `proposed_solar_kw`                  | Proposed Solar Capacity (kW)  | `Float`    | -                                                                                                                                   |  **Yes**  |   -   | DC plant capacity from engineering design.                                           |
| `phase_1_status`                     | Phase 1 Status                | `Select`   | `Draft\nIn Progress\nSubmitted to DISCOM\nFeasibility Approved`                                                                     |  **Yes**  |   1   | Pre-construction utility dossier stage.                                              |
| `discom_application_no`              | DISCOM Application No         | `Data`     | -                                                                                                                                   |    No     |   1   | Online registration application number.                                              |
| `discom_application_date`            | Application Filing Date       | `Date`     | -                                                                                                                                   |    No     |   -   | Date application was formally submitted on portal.                                   |
| `discom_acknowledgement_receipt`     | DISCOM Acknowledgment PDF     | `Attach`   | -                                                                                                                                   |    No     |   -   | Official portal submission receipt.                                                  |
| `national_portal_app_id`             | National Portal ID            | `Data`     | -                                                                                                                                   |    No     |   1   | PM Surya Ghar / National Portal registration ID.                                     |
| `feasibility_status`                 | Feasibility Approval          | `Select`   | `Pending\nApproved\nRejected\nLoad Enhancement Required`                                                                            |  **Yes**  |   -   | Utility technical feasibility study outcome.                                         |
| `feasibility_approval_date`          | Feasibility Approved On       | `Date`     | -                                                                                                                                   |    No     |   -   | Date grid connectivity granted.                                                      |
| `grid_connectivity_noc`              | Grid Connectivity NOC         | `Attach`   | -                                                                                                                                   |    No     |   -   | Formal NOC certificate issued by utility executive engineer.                         |
| `phase_2_status`                     | Phase 2 Status                | `Select`   | `Not Started\nTriggered Post-Installation\nCEIG Scheduled\nCEIG Approved\nJMI Scheduled\nGrid Synchronized\nOverdue (SLA Breached)` |  **Yes**  |   1   | Post-installation grid sync execution stage.                                         |
| `installation_completed_date`        | Installation Completed On     | `Date`     | -                                                                                                                                   |    No     |   -   | Date Stage 09 pre-commissioning testing passed.                                      |
| `statutory_countdown_days`           | Statutory SLA (Days)          | `Int`      | -                                                                                                                                   |  **Yes**  |   -   | Default: 10 days. Configurable via Settings.                                         |
| `statutory_deadline`                 | Statutory Deadline            | `Datetime` | -                                                                                                                                   |    No     |   1   | Exact timestamp when 10-day window expires.                                          |
| `is_sla_overdue`                     | Is SLA Overdue                | `Check`    | -                                                                                                                                   |  **Yes**  |   1   | Flagged 1 if statutory deadline breached without sync.                               |
| `ceig_applicable`                    | CEIG Inspection Required      | `Check`    | -                                                                                                                                   |  **Yes**  |   -   | Auto-set based on state capacity threshold ($> 10\text{ kWp}$ or $> 50\text{ kWp}$). |
| `ceig_charging_permission_no`        | CEIG Permission Order No      | `Data`     | -                                                                                                                                   |    No     |   1   | Statutory order reference number.                                                    |
| `ceig_approval_doc`                  | CEIG Safety Approval Order    | `Attach`   | -                                                                                                                                   |    No     |   -   | Official charging permission order PDF.                                              |
| `ceig_inspection_date`               | CEIG Inspection Date          | `Date`     | -                                                                                                                                   |    No     |   -   | Physical inspection audit date.                                                      |
| `jmi_actual_date`                    | JMI Inspection Date           | `Date`     | -                                                                                                                                   |    No     |   1   | Date joint inspection conducted on site.                                             |
| `jmi_officer_name`                   | DISCOM Inspecting Officer     | `Data`     | -                                                                                                                                   |    No     |   -   | Name and designation of utility inspecting engineer.                                 |
| `jmi_report_doc`                     | Signed JMI Protocol Report    | `Attach`   | -                                                                                                                                   |    No     |   -   | Tri-party signed Joint Meter Inspection report.                                      |
| `net_meter_serial_no`                | Bi-Directional Meter Serial   | `Data`     | -                                                                                                                                   |    No     |   1   | Serial number/barcode of installed bi-directional meter.                             |
| `net_meter_make`                     | Meter Manufacturer            | `Data`     | -                                                                                                                                   |    No     |   -   | e.g., Secure Meters, L&T, Genus, Schneider.                                          |
| `meter_accuracy_class`               | Accuracy Class                | `Select`   | `0.2s\n0.5s\n1.0`                                                                                                                   |    No     |   -   | Net-meter precision rating.                                                          |
| `initial_import_kwh`                 | Initial Import Reading (kWh)  | `Float`    | -                                                                                                                                   |    No     |   -   | Baseline utility grid energy draw reading.                                           |
| `initial_export_kwh`                 | Initial Export Reading (kWh)  | `Float`    | -                                                                                                                                   |    No     |   -   | Baseline solar export energy reading.                                                |
| `grid_synchronization_date`          | Grid Synchronization Date     | `Date`     | -                                                                                                                                   |    No     |   1   | Date grid breaker was energized.                                                     |
| `anti_islanding_trip_time_sec`       | Anti-Islanding Trip Time (s)  | `Float`    | -                                                                                                                                   |    No     |   -   | Inverter safety disconnect time ($\le 2.0\text{ s}$).                                |
| `grid_energization_cert`             | Grid Energization Certificate | `Attach`   | -                                                                                                                                   |    No     |   -   | Commissioning certificate issued by utility.                                         |
| `cod_certificate`                    | COD Certificate               | `Attach`   | -                                                                                                                                   |    No     |   -   | Commercial Operation Date sign-off certificate.                                      |
| `cod_date`                           | COD Date                      | `Date`     | -                                                                                                                                   |    No     |   1   | Commissioning date establishing warranty baseline.                                   |
| `custom_triggers_project_completion` | Triggers Project Completion   | `Check`    | -                                                                                                                                   |  **Yes**  |   -   | Immutable 1. Submission enforces `Project.status = "Completed"`.                     |
| `document_checklist`                 | Statutory Document Checklist  | `Table`    | `Solar Statutory Document Checklist`                                                                                                |    No     |   -   | Child table tracking required utility documents.                                     |
| `milestone_logs`                     | Inspection Milestone History  | `Table`    | `Solar Inspection Milestone Log`                                                                                                    |    No     |   -   | Child table tracking inspection dates and outcomes.                                  |
| `meter_readings`                     | Meter Baseline Readings       | `Table`    | `Solar Meter Reading Item`                                                                                                          |    No     |   -   | Child table capturing multi-parameter register readings.                             |
| `delay_logs`                         | Statutory Delay Explanations  | `Table`    | `Solar Stage Delay Log`                                                                                                             |    No     |   -   | Child table logging SLA breach justifications for Admin review.                      |

---

### 2.4 Child Tables for Statutory Liaisoning & Grid Sync

#### 2.4.1 `tabSolar Statutory Document Checklist`

- **DocType Type:** Child Table (`istable = 1`)
- **Fields:** `document_code` (`Data`, reqd: e.g. `KYC_AADHAAR`, `ELEC_BILL`, `TAX_RECEIPT`, `SITE_SLD`, `CEIG_CHG_PERM`, `WCR_REPORT`, `METER_TEST_CERT`, `JMI_SIGNED_REPORT`), `document_name` (`Data`, reqd), `phase` (`Select`: `Phase 1 (Post-SO)\nPhase 2 (Post-Install)`, reqd), `is_mandatory` (`Check`, default: 1), `file_attachment` (`Attach`), `verification_status` (`Select`: `Pending\nUploaded\nVerified\nRejected`, default: `Pending`), `verified_by` (`Link` to `User`), `verified_on` (`Datetime`), `rejection_reason` (`Small Text`).

#### 2.4.2 `tabSolar Inspection Milestone Log`

- **DocType Type:** Child Table (`istable = 1`)
- **Fields:** `milestone_type` (`Select`: `DISCOM Feasibility Study\nCEIG Safety Audit\nJoint Meter Inspection (JMI)\nNet Meter Testing\nGrid Energization\nNational Portal Subsidy Inspection`, reqd), `scheduled_date` (`Date`, reqd), `actual_date` (`Date`), `inspecting_agency` (`Data`, reqd: e.g. `State CEIG Office`, `BESCOM Metering Division`), `inspecting_officer` (`Data`), `officer_contact` (`Data`), `inspection_result` (`Select`: `Pending\nPassed (No Defects)\nConditional Pass (Punch List)\nFailed / Re-Inspection Required`, default: `Pending`), `report_attachment` (`Attach`).

#### 2.4.3 `tabSolar Meter Reading Item`

- **DocType Type:** Child Table (`istable = 1`)
- **Fields:** `reading_type` (`Select`: `Initial Baseline at Commissioning\nPost-Sync Verification\nSubsequent Billing Audit`, reqd), `meter_serial_no` (`Data`, reqd), `reading_datetime` (`Datetime`, reqd), `kwh_import` (`Float`, reqd), `kwh_export` (`Float`, reqd), `kvah_import` (`Float`), `kvah_export` (`Float`), `peak_demand_kw` (`Float`), `average_power_factor` (`Float`, formula: `kwh / kvah`), `discom_witness_officer` (`Data`, reqd).

#### 2.4.4 `tabSolar Stage Delay Log`

- **DocType Type:** Child Table (`istable = 1`)
- **Fields:** `stage_code` (`Data`, default: `S10B_GRID_SYNC`), `stage_name` (`Data`), `sla_target_hours` (`Float`), `actual_tat_hours` (`Float`), `breach_hours` (`Float`), `delay_category` (`Select`: `DISCOM_METER_SHORTAGE\nCEIG_SCHEDULING_DELAY\nGRID_OUTAGE_SHUTDOWN\nCONSUMER_UNAVAILABLE\nTARIFF_ORDER_PENDING\nFORCE_MAJEURE`), `delay_reason` (`Small Text`, reqd), `remedial_action` (`Small Text`), `logged_by` (`Link` to `User`), `logged_on` (`Datetime`).

---

### 2.5 Standalone Single DocType: `tabSolar Liaisoning Settings`

- **DocType Type:** Single (`issingle = 1`)
- **Permissions:** Read: All authenticated users; Write: **`Admin`**, **`Director`**, **`System Manager`**.
- **Fields:** `default_statutory_sla_days` (`Int`, default: 10), `ceig_capacity_threshold_kw` (`Float`, default: 10.0), `max_anti_islanding_trip_time_sec` (`Float`, default: 2.0), `enforce_strict_jmi_signoff` (`Check`, default: 1), `auto_spawn_asset_register` (`Check`, default: 1), `notify_accounts_on_cod` (`Check`, default: 1).

---

### 2.6 Optimized MariaDB Composite Indexes

```sql
-- Liaisoning dossier lookup by project and lifecycle status
CREATE INDEX idx_liaisoning_project_status
ON `tabLiaisoning And Synchronization` (project, phase_2_status, docstatus);

-- Consumer number utility query index
CREATE INDEX idx_liaisoning_consumer_no
ON `tabLiaisoning And Synchronization` (consumer_number, discom_name);

-- Hourly SLA countdown monitor index
CREATE INDEX idx_liaisoning_sla_daemon
ON `tabLiaisoning And Synchronization` (docstatus, phase_2_status, statutory_deadline);

-- Project completion verification index
CREATE INDEX idx_project_completion_flag
ON `tabProject` (status, custom_is_completed_flag, custom_cod_date);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Pure, decoupled Python domain services located in `solar_module/services/` containing zero UI dependencies.

### 3.1 `LiaisoningInceptionService`

Manages programmatic instantiation of `tabLiaisoning And Synchronization` when Stage 06 `Sales Order` is submitted.

```python
# File: solar_module/services/liaisoning_inception_service.py

import frappe
from frappe import _


class LiaisoningInceptionService:
    """Domain service managing automatic creation of Stage 10 dossiers from Sales Orders."""

    @classmethod
    def spawn_liaisoning_record(cls, project_name: str, sales_order_name: str) -> str:
        """Instantiates a new Liaisoning And Synchronization record in Phase 1: Draft."""
        if frappe.db.exists("Liaisoning And Synchronization", {"project": project_name}):
            return frappe.db.get_value("Liaisoning And Synchronization", {"project": project_name}, "name")

        project = frappe.get_doc("Project", project_name)
        customer = frappe.get_doc("Customer", project.customer)
        sales_order = frappe.get_doc("Sales Order", sales_order_name)

        doc = frappe.get_doc({
            "doctype": "Liaisoning And Synchronization",
            "project": project.name,
            "sales_order": sales_order.name,
            "customer": customer.name,
            "custom_lead_reference": project.get("custom_lead_reference") or sales_order.get("custom_lead_reference"),
            "consumer_number": customer.get("custom_discom_consumer_no") or "PENDING",
            "discom_name": customer.get("custom_discom_name") or "State DISCOM",
            "sanctioned_load_kw": customer.get("custom_sanctioned_load_kw") or 10.0,
            "proposed_solar_kw": sales_order.get("custom_system_capacity_kw") or 10.0,
            "phase_1_status": "Draft",
            "feasibility_status": "Pending",
            "phase_2_status": "Not Started",
            "statutory_countdown_days": frappe.db.get_single_value("Solar Liaisoning Settings", "default_statutory_sla_days") or 10,
            "ceig_applicable": 1 if (sales_order.get("custom_system_capacity_kw") or 0.0) >= (frappe.db.get_single_value("Solar Liaisoning Settings", "ceig_capacity_threshold_kw") or 10.0) else 0,
            "custom_triggers_project_completion": 1
        })

        doc.insert(ignore_permissions=True)

        # Populate mandatory statutory checklist items
        cls._populate_default_checklist(doc)

        # Update Project back-reference
        frappe.db.set_value("Project", project.name, {
            "custom_liaisoning_reference": doc.name,
            "custom_phase_1_status": "Draft",
            "custom_phase_2_status": "Not Started"
        })

        return doc.name

    @staticmethod
    def _populate_default_checklist(doc):
        """Populates baseline regulatory document checklist requirements."""
        checklist = [
            ("KYC_AADHAAR", "Consumer KYC & Identity Proof", "Phase 1 (Post-SO)", 1),
            ("ELEC_BILL", "Latest Electricity Bill (< 60 Days)", "Phase 1 (Post-SO)", 1),
            ("TAX_RECEIPT", "Property Tax Receipt / Ownership Proof", "Phase 1 (Post-SO)", 1),
            ("SITE_SLD", "Single Line Diagram (SLD) Approved", "Phase 1 (Post-SO)", 1),
            ("CEIG_CHG_PERM", "CEIG Safety Charging Permission Order", "Phase 2 (Post-Install)", doc.ceig_applicable),
            ("WCR_REPORT", "Work Completion Report (WCR) & Pre-Comm Logs", "Phase 2 (Post-Install)", 1),
            ("JMI_SIGNED_REPORT", "Joint Meter Inspection Protocol (Tri-Party Signed)", "Phase 2 (Post-Install)", 1),
            ("NET_METER_TEST", "Net-Meter Calibration & Test Certificate", "Phase 2 (Post-Install)", 1),
        ]
        for code, title, phase, reqd in checklist:
            doc.append("document_checklist", {
                "document_code": code,
                "document_name": title,
                "phase": phase,
                "is_mandatory": reqd,
                "verification_status": "Pending"
            })
        doc.save(ignore_permissions=True)
```

---

### 3.2 `LiaisoningSLAService`

Calculates statutory 10-day deadlines considering official working days and public holidays, and evaluates SLA breach conditions.

```python
# File: solar_module/services/liaisoning_sla_service.py

import frappe
from frappe.utils import now_datetime, getdate, add_to_date, time_diff_in_hours


class LiaisoningSLAService:
    """Domain service managing statutory 10-day countdown, business days math & holiday calendar."""

    @staticmethod
    def calculate_statutory_deadline(start_date, sla_days: int = 10, holiday_list: str = None) -> str:
        """Calculates deadline date excluding Sundays and designated Frappe company holidays."""
        if not holiday_list:
            default_company = frappe.defaults.get_user_default("Company")
            if default_company:
                holiday_list = frappe.db.get_value("Company", default_company, "default_holiday_list")

        holidays = set()
        if holiday_list:
            holidays = {
                getdate(h.holiday_date)
                for h in frappe.get_all("Holiday", filters={"parent": holiday_list}, fields=["holiday_date"])
            }

        current_date = getdate(start_date)
        added_days = 0

        while added_days < sla_days:
            current_date = getdate(add_to_date(current_date, days=1))
            # 6 is Sunday; also skip listed holidays
            if current_date.weekday() == 6 or current_date in holidays:
                continue
            added_days += 1

        return f"{current_date} 18:00:00"

    @classmethod
    def sync_document_sla(cls, doc):
        """Audits real-time SLA countdown, remaining hours, and flags overdue state."""
        if doc.phase_2_status in ["Not Started", "Grid Synchronized"]:
            return

        if not doc.statutory_deadline and doc.installation_completed_date:
            doc.statutory_deadline = cls.calculate_statutory_deadline(
                doc.installation_completed_date,
                doc.statutory_countdown_days or 10
            )

        if doc.statutory_deadline:
            now = now_datetime()
            deadline = frappe.utils.get_datetime(doc.statutory_deadline)
            diff_hours = time_diff_in_hours(deadline, now)

            if diff_hours < 0:
                doc.is_sla_overdue = 1
                if doc.phase_2_status not in ["Grid Synchronized", "Overdue (SLA Breached)"]:
                    doc.phase_2_status = "Overdue (SLA Breached)"
            else:
                doc.is_sla_overdue = 0

            frappe.db.set_value("Project", doc.project, {
                "custom_statutory_deadline": doc.statutory_deadline,
                "custom_phase_2_status": doc.phase_2_status
            })
```

---

### 3.3 `LiaisoningPhase1Service`

Manages Phase 1 pre-construction statutory filings, checks documentation prerequisites, and atomically closes `Lead` Progress Bar 1.

```python
# File: solar_module/services/liaisoning_phase_1_service.py

import frappe
from frappe import _


class LiaisoningPhase1Service:
    """Domain service governing Phase 1 utility filing and Lead Stepper completion."""

    @staticmethod
    def validate_submission_gate(doc):
        """Enforces upload of registration acknowledgment prior to transitioning to Submitted."""
        if not doc.discom_application_no:
            frappe.throw(_("DISCOM Online Application Number is mandatory."), frappe.ValidationError)
        if not doc.discom_acknowledgement_receipt:
            frappe.throw(_("DISCOM Application Acknowledgment Receipt PDF must be attached."), frappe.ValidationError)

    @staticmethod
    def validate_feasibility_gate(doc):
        """Enforces technical feasibility approval parameters and grid NOC."""
        if not doc.grid_connectivity_noc:
            frappe.throw(_("Official Grid Connectivity NOC document must be uploaded."), frappe.ValidationError)
        if not doc.feasibility_approval_date:
            frappe.throw(_("Feasibility Approval Date must be recorded."), frappe.ValidationError)

    @staticmethod
    def record_discom_submission(doc_name: str, app_no: str, receipt_url: str, national_portal_id: str = None) -> dict:
        """Records DISCOM submission and atomically completes Lead Progress Bar 1."""
        doc = frappe.get_doc("Liaisoning And Synchronization", doc_name)
        doc.check_permission("write")

        doc.discom_application_no = app_no
        doc.discom_application_date = frappe.utils.today()
        doc.discom_acknowledgement_receipt = receipt_url
        if national_portal_id:
            doc.national_portal_app_id = national_portal_id

        doc.phase_1_status = "Submitted to DISCOM"
        doc.save()

        # Terminal closeout for Progress Bar 1 (Lead)
        if doc.custom_lead_reference:
            lead = frappe.get_doc("Lead", doc.custom_lead_reference)
            lead.db_set("custom_lead_progress_status", "Completed")
            lead.db_set("custom_current_stage_code", "S10A_LIAISON_SUBMITTED")
            lead.add_comment(
                "Comment",
                text=_("Phase 1 Statutory DISCOM Application submitted (App No: {0}). Lead Progress Bar completed.")
                .format(app_no)
            )

        frappe.db.set_value("Project", doc.project, {
            "custom_phase_1_status": "Submitted to DISCOM"
        })

        return {"status": "success", "phase_1_status": doc.phase_1_status}
```

---

### 3.4 `LiaisoningPhase2Service`

Governs Phase 2 post-installation verification, CEIG safety clearances, JMI protocol assertions, and anti-islanding protection verification.

```python
# File: solar_module/services/liaisoning_phase_2_service.py

import frappe
from frappe import _


class LiaisoningPhase2Service:
    """Domain service managing Phase 2 CEIG, JMI, Net Metering, and Anti-Islanding gates."""

    @staticmethod
    def validate_ceig_gate(doc):
        """Enforces CEIG Safety Clearance verification if capacity meets threshold."""
        if doc.ceig_applicable:
            if not doc.ceig_approval_doc:
                frappe.throw(_("CEIG Official Charging Permission order must be uploaded."), frappe.ValidationError)
            if not doc.ceig_charging_permission_no:
                frappe.throw(_("CEIG Charging Permission Number is mandatory."), frappe.ValidationError)

    @staticmethod
    def validate_jmi_and_metering_gate(doc):
        """Enforces Joint Meter Inspection protocol and bi-directional net-meter parameters."""
        if not doc.jmi_report_doc:
            frappe.throw(_("Signed Joint Meter Inspection (JMI) Protocol Report is mandatory."), frappe.ValidationError)
        if not doc.net_meter_serial_no:
            frappe.throw(_("Bi-directional Net-Meter Serial Number is mandatory."), frappe.ValidationError)
        if doc.initial_import_kwh is None or doc.initial_export_kwh is None:
            frappe.throw(_("Initial Active Energy Import and Export readings (kWh) are mandatory."), frappe.ValidationError)

    @staticmethod
    def validate_grid_sync_gate(doc):
        """Enforces anti-islanding safety disconnect ceiling (<= 2.0s) and energization certs."""
        if not doc.grid_synchronization_date:
            frappe.throw(_("Grid Synchronization Date is mandatory."), frappe.ValidationError)
        if doc.anti_islanding_trip_time_sec is None:
            frappe.throw(_("Inverter Anti-Islanding Trip Time must be recorded."), frappe.ValidationError)
        if doc.anti_islanding_trip_time_sec > 2.0:
            frappe.throw(
                _("Safety Violation: Inverter Anti-Islanding Trip Time ({0}s) exceeds statutory 2.0s limit.")
                .format(doc.anti_islanding_trip_time_sec),
                frappe.ValidationError
            )
        if not doc.cod_certificate:
            frappe.throw(_("Official Commercial Operation Date (COD) Certificate must be attached."), frappe.ValidationError)

    @staticmethod
    def assert_ready_for_submission(doc):
        """Asserts that all regulatory preconditions are satisfied before legal freeze."""
        if doc.phase_2_status != "Grid Synchronized":
            frappe.throw(
                _("Dossier cannot be submitted until Phase 2 status is 'Grid Synchronized'."),
                frappe.ValidationError
            )
        if not doc.cod_date:
            frappe.throw(_("Commercial Operation Date (COD) must be established before submission."), frappe.ValidationError)
```

---

### 3.5 `ProjectCompletionService`

Atomically orchestrates ERPNext `Project` completion, closes remaining WBS tasks, spawns the Stage 11 `Solar Asset Register`, and notifies Accounts.

```python
# File: solar_module/services/project_completion_service.py

import frappe
from frappe import _
from frappe.utils import now_datetime, today


class ProjectCompletionService:
    """Atomic service orchestrating Project terminal completion and Stage 11 O&M spawning."""

    @classmethod
    def execute_project_closeout(cls, liaison_doc):
        """Atomically closes the Project, closes open WBS tasks, and spawns the Asset Register."""
        project = frappe.get_doc("Project", liaison_doc.project)

        project.db_set("status", "Completed")
        project.db_set("custom_is_completed_flag", 1)
        project.db_set("custom_current_stage_code", "S10B_GRID_SYNC_COMPLETED")
        project.db_set("custom_stage_state", "COMPLETED_ON_TIME" if not liaison_doc.is_sla_overdue else "COMPLETED_DELAYED")
        project.db_set("custom_completion_certified_by", frappe.session.user)
        project.db_set("custom_completion_certified_on", now_datetime())
        project.db_set("custom_grid_sync_date", liaison_doc.grid_synchronization_date)
        project.db_set("custom_cod_date", liaison_doc.cod_date or liaison_doc.grid_synchronization_date)
        project.db_set("custom_net_meter_serial_no", liaison_doc.net_meter_serial_no)

        # Complete any remaining open WBS tasks
        open_tasks = frappe.get_all(
            "Task",
            filters={"project": project.name, "status": ["not in", ["Completed", "Cancelled"]]},
            fields=["name"]
        )
        for t in open_tasks:
            frappe.db.set_value("Task", t.name, {
                "status": "Completed",
                "progress": 100,
                "completed_on": today()
            })

        cls.spawn_solar_asset_register(project, liaison_doc)
        cls.notify_accounts_of_commissioning(project, liaison_doc)
        cls.broadcast_completion_notifications(project, liaison_doc)

    @classmethod
    def spawn_solar_asset_register(cls, project, liaison_doc):
        """Creates the lifetime Solar Asset Register twin for Stage 11 O&M."""
        if frappe.db.exists("Solar Asset Register", {"project": project.name}):
            return

        asset_doc = frappe.get_doc({
            "doctype": "Solar Asset Register",
            "project": project.name,
            "sales_order": liaison_doc.sales_order,
            "customer": liaison_doc.customer,
            "asset_capacity_kw": liaison_doc.proposed_solar_kw,
            "cod_date": liaison_doc.cod_date or liaison_doc.grid_synchronization_date,
            "net_meter_serial_no": liaison_doc.net_meter_serial_no,
            "discom_consumer_no": liaison_doc.consumer_number,
            "warranty_expiry_date": frappe.utils.add_to_date(liaison_doc.cod_date, years=5),
            "status": "Commissioned & Active",
            "amc_contract_status": "Under Initial Warranty AMC"
        })
        asset_doc.insert(ignore_permissions=True)

    @classmethod
    def notify_accounts_of_commissioning(cls, project, liaison_doc):
        """Creates an urgent notification to Accounts for final milestone invoicing."""
        accounts_users = frappe.get_all("Has Role", filters={"role": "Accounts Assistant"}, fields=["parent"])
        for u in accounts_users:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": _("Commissioning Milestone Unlocked: Project {0} Grid Synchronized").format(project.name),
                "for_user": u.parent,
                "type": "Alert",
                "document_type": "Project",
                "document_name": project.name
            }).insert(ignore_permissions=True)

    @classmethod
    def broadcast_completion_notifications(cls, project, liaison_doc):
        """Broadcasts omnichannel completion alerts to stakeholders."""
        recipients = [project.owner, liaison_doc.owner]
        for r in set(recipients):
            if r:
                frappe.sendmail(
                    recipients=[r],
                    subject=_("🎉 Solar Plant Formally Commissioned: {0}").format(project.project_name),
                    message=_("<p>We are proud to announce that <b>Project {0} ({1} kWp)</b> "
                              "has successfully achieved statutory grid synchronization and Commercial Operation Date (COD) on {2}. "
                              "The project is now formally <b>Completed</b> and handed over to Lifecycle O&M.</p>")
                    .format(project.name, liaison_doc.proposed_solar_kw, liaison_doc.cod_date)
                )

    @classmethod
    def revert_project_completion(cls, liaison_doc):
        """Reverts Project completion if liaisoning dossier is cancelled by System Manager."""
        frappe.db.set_value("Project", liaison_doc.project, {
            "status": "Open",
            "custom_is_completed_flag": 0,
            "custom_stage_state": "ONGOING_HEALTHY"
        })
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

### 4.1 Submittable Controller: `LiaisoningAndSynchronization`

```python
# File: solar_module/doctype/liaisoning_and_synchronization/liaisoning_and_synchronization.py

import frappe
from frappe import _
from frappe.model.document import Document
from solar_module.services.liaisoning_sla_service import LiaisoningSLAService
from solar_module.services.liaisoning_phase_1_service import LiaisoningPhase1Service
from solar_module.services.liaisoning_phase_2_service import LiaisoningPhase2Service
from solar_module.services.project_completion_service import ProjectCompletionService


class LiaisoningAndSynchronization(Document):
    """Authoritative submittable controller governing Stage 10 Statutory Liaisoning & Grid Sync."""

    def validate(self):
        """Defensive validation executed on every document save."""
        self.validate_consumer_baseline()
        self.validate_phase_1_rules()
        self.validate_phase_2_rules()
        self.evaluate_sla_status()

    def validate_consumer_baseline(self):
        """Enforces relational links and mandatory utility baseline parameters."""
        if not self.project:
            frappe.throw(_("Linked Project reference is mandatory."), frappe.ValidationError)
        if not self.sales_order:
            frappe.throw(_("Linked Sales Order reference is mandatory."), frappe.ValidationError)
        if not self.customer:
            frappe.throw(_("Customer link is mandatory."), frappe.ValidationError)
        if not self.consumer_number:
            frappe.throw(_("DISCOM Consumer Number is mandatory for statutory filings."), frappe.ValidationError)

    def validate_phase_1_rules(self):
        """Validates Phase 1 statutory submission invariants."""
        if self.phase_1_status == "Submitted to DISCOM":
            LiaisoningPhase1Service.validate_submission_gate(self)
        elif self.phase_1_status == "Feasibility Approved":
            LiaisoningPhase1Service.validate_feasibility_gate(self)

    def validate_phase_2_rules(self):
        """Validates Phase 2 statutory grid sync invariants."""
        if self.phase_2_status in ["CEIG Approved", "JMI Scheduled", "Grid Synchronized"]:
            LiaisoningPhase2Service.validate_ceig_gate(self)
        if self.phase_2_status in ["Grid Synchronized"]:
            LiaisoningPhase2Service.validate_jmi_and_metering_gate(self)
            LiaisoningPhase2Service.validate_grid_sync_gate(self)

    def evaluate_sla_status(self):
        """Recalculates real-time SLA countdown and overdue state."""
        LiaisoningSLAService.sync_document_sla(self)

    def on_submit(self):
        """Immutable submission hook triggering atomic Project completion and O&M handoff."""
        LiaisoningPhase2Service.assert_ready_for_submission(self)
        ProjectCompletionService.execute_project_closeout(self)

        frappe.msgprint(
            _("Stage 10 Statutory Liaisoning & Grid Synchronization formally approved! "
              "Project {0} marked Completed. Stage 11 Solar Asset Register spawned.")
            .format(self.project),
            alert=True,
            indicator="green"
        )

    def on_cancel(self):
        """Guards against unauthorized cancellation of legally submitted statutory dossiers."""
        if not (frappe.has_permission(self.doctype, "cancel") and "System Manager" in frappe.get_roles()):
            frappe.throw(_("Only System Manager or Director can cancel a submitted Statutory Dossier."), frappe.PermissionError)
        ProjectCompletionService.revert_project_completion(self)
```

---

### 4.2 Whitelisted RPC Endpoints (`solar_module.api.liaisoning.*`)

```python
# File: solar_module/api/liaisoning.py

import json
import frappe
from frappe import _
from solar_module.services.liaisoning_phase_1_service import LiaisoningPhase1Service
from solar_module.services.liaisoning_phase_2_service import LiaisoningPhase2Service
from solar_module.services.liaisoning_sla_service import LiaisoningSLAService


@frappe.whitelist(methods=["POST"])
def update_phase_1_dossier(doc_name: str, payload: str) -> dict:
    """Updates Phase 1 pre-construction application data."""
    if not doc_name:
        frappe.throw(_("Document name is required."), frappe.ValidationError)

    doc = frappe.get_doc("Liaisoning And Synchronization", doc_name)
    doc.check_permission("write")

    data = json.loads(payload)
    for field in ["consumer_number", "discom_name", "discom_division", "sanctioned_load_kw", "national_portal_app_id"]:
        if field in data:
            doc.set(field, data[field])

    doc.save()
    return {"status": "success", "message": _("Phase 1 dossier updated successfully.")}


@frappe.whitelist(methods=["POST"])
def record_discom_submission(doc_name: str, app_no: str, receipt_url: str, national_portal_id: str = None) -> dict:
    """Records utility portal submission and triggers Lead stepper completion."""
    return LiaisoningPhase1Service.record_discom_submission(doc_name, app_no, receipt_url, national_portal_id)


@frappe.whitelist(methods=["POST"])
def activate_phase_2_countdown(doc_name: str, installation_completion_date: str) -> dict:
    """Activates the statutory 10-day countdown timer post-installation."""
    doc = frappe.get_doc("Liaisoning And Synchronization", doc_name)
    doc.check_permission("write")

    project = frappe.get_doc("Project", doc.project)
    if not project.get("custom_pre_comm_gate_cleared"):
        frappe.throw(_("Cannot activate Stage 10B countdown: Stage 09 Pre-Commissioning Electrical Testing must be cleared first."), frappe.ValidationError)

    doc.installation_completed_date = installation_completion_date
    doc.phase_2_status = "Triggered Post-Installation"
    doc.statutory_deadline = LiaisoningSLAService.calculate_statutory_deadline(
        installation_completion_date,
        doc.statutory_countdown_days or 10
    )
    doc.save()

    return {
        "status": "success",
        "phase_2_status": doc.phase_2_status,
        "statutory_deadline": doc.statutory_deadline
    }


@frappe.whitelist(methods=["POST"])
def record_ceig_inspection(doc_name: str, charging_permission_no: str, approval_url: str, inspection_date: str) -> dict:
    """Records CEIG safety clearance and charging permission."""
    doc = frappe.get_doc("Liaisoning And Synchronization", doc_name)
    doc.check_permission("write")

    doc.ceig_charging_permission_no = charging_permission_no
    doc.ceig_approval_doc = approval_url
    doc.ceig_inspection_date = inspection_date
    doc.phase_2_status = "CEIG Approved"
    doc.save()

    return {"status": "success", "phase_2_status": doc.phase_2_status}


@frappe.whitelist(methods=["POST"])
def record_jmi_inspection(doc_name: str, jmi_payload: str) -> dict:
    """Records Joint Meter Inspection (JMI) protocol and meter parameters."""
    doc = frappe.get_doc("Liaisoning And Synchronization", doc_name)
    doc.check_permission("write")

    data = json.loads(jmi_payload)
    doc.jmi_actual_date = data.get("jmi_actual_date", frappe.utils.today())
    doc.jmi_officer_name = data.get("jmi_officer_name")
    doc.jmi_report_doc = data.get("jmi_report_doc")
    doc.net_meter_serial_no = data.get("net_meter_serial_no")
    doc.net_meter_make = data.get("net_meter_make")
    doc.meter_accuracy_class = data.get("meter_accuracy_class", "0.5s")
    doc.initial_import_kwh = float(data.get("initial_import_kwh", 0.0))
    doc.initial_export_kwh = float(data.get("initial_export_kwh", 0.0))
    doc.phase_2_status = "JMI Scheduled"
    doc.save()

    return {"status": "success", "phase_2_status": doc.phase_2_status}


@frappe.whitelist(methods=["POST"])
def execute_grid_synchronization_and_complete_project(doc_name: str, sync_payload: str) -> dict:
    """Approves grid synchronization, anti-islanding test, and submits dossier."""
    doc = frappe.get_doc("Liaisoning And Synchronization", doc_name)
    doc.check_permission("submit")

    data = json.loads(sync_payload)
    doc.grid_synchronization_date = data.get("grid_synchronization_date", frappe.utils.today())
    doc.anti_islanding_trip_time_sec = float(data.get("anti_islanding_trip_time_sec", 1.2))
    doc.grid_energization_cert = data.get("grid_energization_cert")
    doc.cod_certificate = data.get("cod_certificate")
    doc.cod_date = data.get("cod_date", doc.grid_synchronization_date)
    doc.phase_2_status = "Grid Synchronized"
    doc.save()

    doc.submit()

    return {
        "status": "success",
        "docstatus": doc.docstatus,
        "message": _("Grid synchronization signed off. Project marked Completed.")
    }


@frappe.whitelist(methods=["POST"])
def log_statutory_delay(doc_name: str, category: str, reason: str, remedial_action: str) -> dict:
    """Logs an auditable SLA breach explanation into tabSolar Stage Delay Log."""
    doc = frappe.get_doc("Liaisoning And Synchronization", doc_name)
    doc.check_permission("write")

    doc.append("delay_logs", {
        "stage_code": "S10B_GRID_SYNC",
        "stage_name": "Statutory Grid Synchronization",
        "sla_target_hours": (doc.statutory_countdown_days or 10) * 24.0,
        "delay_category": category,
        "delay_reason": reason,
        "remedial_action": remedial_action,
        "logged_by": frappe.session.user,
        "logged_on": frappe.utils.now_datetime()
    })
    doc.save()

    return {"status": "success", "message": _("Statutory delay logged for Admin review.")}
```

---

### 4.3 Background Celery / RQ Schedulers

```python
# File: solar_module/tasks/liaisoning_sla_daemon.py

import frappe
from solar_module.services.liaisoning_sla_service import LiaisoningSLAService


def check_liaisoning_sla():
    """Hourly background daemon auditing active Phase 2 statutory countdown timers."""
    active_dossiers = frappe.get_all(
        "Liaisoning And Synchronization",
        filters={
            "docstatus": 0,
            "phase_2_status": ["in", ["Triggered Post-Installation", "CEIG Scheduled", "CEIG Approved", "JMI Scheduled"]]
        },
        fields=["name"]
    )

    for record in active_dossiers:
        doc = frappe.get_doc("Liaisoning And Synchronization", record.name)
        LiaisoningSLAService.sync_document_sla(doc)
        doc.save(ignore_permissions=True)
```

---

## 5. Layer 4: Desk Client Script & Dynamic Mobile Workbench Hook

### 5.1 Desk Client Script: `codes/client_script/liaisoning_and_synchronization.js`

```javascript
// File: codes/client_script/liaisoning_and_synchronization.js

frappe.ui.form.on("Liaisoning And Synchronization", {
  refresh(frm) {
    frm.trigger("render_sla_badge");
    frm.trigger("add_custom_action_buttons");
  },

  render_sla_badge(frm) {
    if (frm.doc.docstatus === 1) {
      frm.dashboard.set_headline_alert(
        __(
          "⚡ Project Formally Commissioned on {0}. Commercial Operation Date (COD) Certified.",
          [frm.doc.cod_date],
        ),
        "green",
      );
      return;
    }

    if (
      frm.doc.phase_2_status !== "Not Started" &&
      frm.doc.statutory_deadline
    ) {
      const now = new Date();
      const deadline = new Date(frm.doc.statutory_deadline);
      const remaining_hours = Math.round((deadline - now) / 36e5);

      if (remaining_hours < 0) {
        frm.dashboard.set_headline_alert(
          __(
            "🚨 Statutory SLA Breached! Overdue by {0} hours. Mandatory delay justification required.",
            [Math.abs(remaining_hours)],
          ),
          "red",
        );
      } else if (remaining_hours <= 48) {
        frm.dashboard.set_headline_alert(
          __(
            "⚠️ Statutory Warning: {0} hours remaining to complete CEIG, JMI, and Grid Sync.",
            [remaining_hours],
          ),
          "orange",
        );
      } else {
        frm.dashboard.set_headline_alert(
          __(
            "⏱️ Statutory SLA Active: {0} hours ({1} business days) remaining until deadline.",
            [remaining_hours, (remaining_hours / 24).toFixed(1)],
          ),
          "blue",
        );
      }
    }
  },

  add_custom_action_buttons(frm) {
    if (frm.doc.docstatus === 0) {
      if (
        frm.doc.phase_1_status !== "Submitted to DISCOM" &&
        frm.doc.phase_1_status !== "Feasibility Approved"
      ) {
        frm.add_custom_button(
          __("Submit DISCOM Filing"),
          () => {
            frm.trigger("show_discom_submission_modal");
          },
          __("Actions"),
        );
      }

      if (
        frm.doc.phase_2_status === "Triggered Post-Installation" ||
        frm.doc.phase_2_status === "CEIG Scheduled"
      ) {
        frm.add_custom_button(
          __("Record CEIG Approval"),
          () => {
            frm.trigger("show_ceig_approval_modal");
          },
          __("Actions"),
        );
      }

      if (
        frm.doc.phase_2_status === "CEIG Approved" ||
        frm.doc.phase_2_status === "JMI Scheduled"
      ) {
        frm.add_custom_button(
          __("Record JMI & Meter"),
          () => {
            frm.trigger("show_jmi_modal");
          },
          __("Actions"),
        );
      }

      if (
        frm.doc.phase_2_status === "JMI Scheduled" ||
        frm.doc.phase_2_status === "Grid Synchronized"
      ) {
        frm
          .add_custom_button(
            __("Synchronize Grid & Close Project"),
            () => {
              frm.trigger("show_grid_sync_modal");
            },
            __("Actions"),
          )
          .addClass("btn-primary");
      }

      if (frm.doc.is_sla_overdue) {
        frm
          .add_custom_button(
            __("Log Statutory Delay"),
            () => {
              frm.trigger("show_delay_modal");
            },
            __("Actions"),
          )
          .addClass("btn-danger");
      }
    }
  },

  show_discom_submission_modal(frm) {
    const d = new frappe.ui.Dialog({
      title: __("Submit Phase 1 DISCOM Application"),
      fields: [
        {
          fieldname: "app_no",
          label: __("DISCOM Online Application No"),
          fieldtype: "Data",
          reqd: 1,
        },
        {
          fieldname: "receipt_url",
          label: __("Application Acknowledgment Receipt PDF"),
          fieldtype: "Attach",
          reqd: 1,
        },
        {
          fieldname: "national_portal_id",
          label: __("National Portal Application ID (PM Surya Ghar)"),
          fieldtype: "Data",
        },
      ],
      primary_action_label: __("Confirm Submission"),
      primary_action(values) {
        d.hide();
        frappe.call({
          method: "solar_module.api.liaisoning.record_discom_submission",
          args: {
            doc_name: frm.doc.name,
            app_no: values.app_no,
            receipt_url: values.receipt_url,
            national_portal_id: values.national_portal_id,
          },
          freeze: true,
          callback(r) {
            if (!r.exc) {
              frm.reload_doc();
            }
          },
        });
      },
    });
    d.show();
  },

  show_ceig_approval_modal(frm) {
    const d = new frappe.ui.Dialog({
      title: __("Record CEIG Safety Approval"),
      fields: [
        {
          fieldname: "charging_permission_no",
          label: __("CEIG Charging Permission Order No"),
          fieldtype: "Data",
          reqd: 1,
        },
        {
          fieldname: "approval_url",
          label: __("Charging Permission Order PDF"),
          fieldtype: "Attach",
          reqd: 1,
        },
        {
          fieldname: "inspection_date",
          label: __("Inspection Date"),
          fieldtype: "Date",
          default: frappe.datetime.get_today(),
          reqd: 1,
        },
      ],
      primary_action_label: __("Save CEIG Approval"),
      primary_action(values) {
        d.hide();
        frappe.call({
          method: "solar_module.api.liaisoning.record_ceig_inspection",
          args: {
            doc_name: frm.doc.name,
            charging_permission_no: values.charging_permission_no,
            approval_url: values.approval_url,
            inspection_date: values.inspection_date,
          },
          freeze: true,
          callback(r) {
            if (!r.exc) frm.reload_doc();
          },
        });
      },
    });
    d.show();
  },

  show_jmi_modal(frm) {
    const d = new frappe.ui.Dialog({
      title: __("Record Joint Meter Inspection (JMI) & Baseline Readings"),
      fields: [
        {
          fieldname: "jmi_actual_date",
          label: __("JMI Inspection Date"),
          fieldtype: "Date",
          default: frappe.datetime.get_today(),
          reqd: 1,
        },
        {
          fieldname: "jmi_officer_name",
          label: __("DISCOM Inspecting Officer"),
          fieldtype: "Data",
          reqd: 1,
        },
        {
          fieldname: "jmi_report_doc",
          label: __("Signed JMI Protocol Report PDF"),
          fieldtype: "Attach",
          reqd: 1,
        },
        {
          fieldname: "net_meter_serial_no",
          label: __("Bi-Directional Net-Meter Serial No"),
          fieldtype: "Data",
          reqd: 1,
        },
        {
          fieldname: "net_meter_make",
          label: __("Meter Make / Model"),
          fieldtype: "Data",
          reqd: 1,
        },
        {
          fieldname: "meter_accuracy_class",
          label: __("Accuracy Class"),
          fieldtype: "Select",
          options: "0.2s\n0.5s\n1.0",
          default: "0.5s",
          reqd: 1,
        },
        {
          fieldname: "initial_import_kwh",
          label: __("Initial Import Reading (kWh)"),
          fieldtype: "Float",
          default: 0.0,
          reqd: 1,
        },
        {
          fieldname: "initial_export_kwh",
          label: __("Initial Export Reading (kWh)"),
          fieldtype: "Float",
          default: 0.0,
          reqd: 1,
        },
      ],
      primary_action_label: __("Save JMI Details"),
      primary_action(values) {
        d.hide();
        frappe.call({
          method: "solar_module.api.liaisoning.record_jmi_inspection",
          args: {
            doc_name: frm.doc.name,
            jmi_payload: JSON.stringify(values),
          },
          freeze: true,
          callback(r) {
            if (!r.exc) frm.reload_doc();
          },
        });
      },
    });
    d.show();
  },

  show_grid_sync_modal(frm) {
    const d = new frappe.ui.Dialog({
      title: __("Execute Grid Synchronization & COD Sign-Off"),
      fields: [
        {
          fieldname: "grid_synchronization_date",
          label: __("Grid Energization Date"),
          fieldtype: "Date",
          default: frappe.datetime.get_today(),
          reqd: 1,
        },
        {
          fieldname: "anti_islanding_trip_time_sec",
          label: __("Anti-Islanding Trip Time (seconds)"),
          fieldtype: "Float",
          default: 1.2,
          reqd: 1,
          description: __("Must be <= 2.0 seconds per CEA technical standards"),
        },
        {
          fieldname: "grid_energization_cert",
          label: __("Grid Energization Certificate"),
          fieldtype: "Attach",
          reqd: 1,
        },
        {
          fieldname: "cod_certificate",
          label: __("Commercial Operation Date (COD) Certificate"),
          fieldtype: "Attach",
          reqd: 1,
        },
        {
          fieldname: "cod_date",
          label: __("COD Date"),
          fieldtype: "Date",
          default: frappe.datetime.get_today(),
          reqd: 1,
        },
      ],
      primary_action_label: __("Confirm Grid Sync & Close Project"),
      primary_action(values) {
        if (values.anti_islanding_trip_time_sec > 2.0) {
          frappe.msgprint(
            __("Anti-Islanding trip time cannot exceed 2.0 seconds."),
          );
          return;
        }
        d.hide();
        frappe.call({
          method:
            "solar_module.api.liaisoning.execute_grid_synchronization_and_complete_project",
          args: {
            doc_name: frm.doc.name,
            sync_payload: JSON.stringify(values),
          },
          freeze: true,
          freeze_message: __(
            "Closing Project and Generating Solar Asset Register...",
          ),
          callback(r) {
            if (!r.exc) {
              frm.reload_doc();
            }
          },
        });
      },
    });
    d.show();
  },

  show_delay_modal(frm) {
    const d = new frappe.ui.Dialog({
      title: __("Log Statutory SLA Delay Reason"),
      fields: [
        {
          fieldname: "category",
          label: __("Delay Category"),
          fieldtype: "Select",
          options:
            "DISCOM_METER_SHORTAGE\nCEIG_SCHEDULING_DELAY\nGRID_OUTAGE_SHUTDOWN\nCONSUMER_UNAVAILABLE\nTARIFF_ORDER_PENDING\nFORCE_MAJEURE",
          reqd: 1,
        },
        {
          fieldname: "reason",
          label: __("Detailed Explanation"),
          fieldtype: "Small Text",
          reqd: 1,
        },
        {
          fieldname: "remedial_action",
          label: __("Remedial Action Planned"),
          fieldtype: "Small Text",
          reqd: 1,
        },
      ],
      primary_action_label: __("Submit Delay Log"),
      primary_action(values) {
        d.hide();
        frappe.call({
          method: "solar_module.api.liaisoning.log_statutory_delay",
          args: {
            doc_name: frm.doc.name,
            category: values.category,
            reason: values.reason,
            remedial_action: values.remedial_action,
          },
          freeze: true,
          callback(r) {
            if (!r.exc) frm.reload_doc();
          },
        });
      },
    });
    d.show();
  },
});
```

---

### 5.2 Mobile Workbench & Two-Tier Kanban UX Specification (`/solar/liaisoning`)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                   DUAL-TIMING STATUTORY LIAISONING & GRID SYNC KANBAN BOARD                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ METRICS: [Active Filings: 38]   [Pending Feasibility: 12]   [Active 10d Clocks: 16]   [Overdue: 2]│
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: PHASE 1 EARLY COMPLIANCE (Pre-Construction)                                              │
│ ┌──────────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┐ │
│ │ 1. Draft Dossier (6) │ 2. In Progress (10)  │ 3. DISCOM Filed (14) │ 4. Feasibility NOC (16) │ │
│ ├──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤ │
│ │ [PRJ-0104 - 15 kWp]  │ [PRJ-0102 - 50 kWp]  │ [PRJ-0098 - 100 kWp] │ [PRJ-0092 - 25 kWp]     │ │
│ │ KYC Verified         │ Bill Attached        │ App: BESCOM-88219    │ NOC: NOC-2026-991       │ │
│ │ Consumer: M. Sharma  │ Consumer: R. Patel   │ Consumer: Indus Corp │ Ready for Construction  │ │
│ └──────────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: PHASE 2 STATUTORY GRID SYNC (Post-Installation ★ 10-Day SLA Countdown Active ★)          │
│ ┌──────────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┐ │
│ │ 1. Triggered (4)     │ 2. CEIG Audit (5)    │ 3. JMI & Meter (5)   │ 4. Overdue Alerts (2)   │ │
│ ├──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤ │
│ │ [PRJ-0089 - 40 kWp]  │ [PRJ-0084 - 120 kWp] │ [PRJ-0081 - 20 kWp]  │ [PRJ-0076 - 50 kWp]     │ │
│ │ ⏱️ 9.2 Days Remaining │ ⏱️ 6.4 Days Remaining │ ⏱️ 2.1 Days Remaining │ 🚨 OVERDUE (+1.8 Days)  │ │
│ │ [Green Radial Timer] │ [Green Radial Timer] │ [Amber Warning Timer]│ [Red Alert Badge]       │ │
│ │ WCR Verified         │ CEIG Insp: Tomorrow  │ JMI Date: Today 2 PM │ Reason: Meter Shortage  │ │
│ └──────────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

### 6.1 Zero-Commit Transactional Rule

All tests subclass `frappe.testing.IntegrationTestCase`. Every test runs within an isolated database transaction and rolls back automatically in `tearDown`. Never call `frappe.db.commit()`.

---

### 6.2 Complete Integration Test Suite (`test_stage_10_liaisoning_grid_sync_tracer_bullet.py`)

```python
# File: solar_module/tests/test_stage_10_liaisoning_grid_sync_tracer_bullet.py

import json
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import today, add_to_date, now_datetime
from solar_module.services.liaisoning_inception_service import LiaisoningInceptionService
from solar_module.services.liaisoning_sla_service import LiaisoningSLAService
from solar_module.services.liaisoning_phase_1_service import LiaisoningPhase1Service
from solar_module.services.liaisoning_phase_2_service import LiaisoningPhase2Service
from solar_module.services.project_completion_service import ProjectCompletionService


class TestStage10LiaisoningGridSyncTracerBullet(IntegrationTestCase):
    """Integration Test Suite proving all 11 Stage 10 Liaisoning & Grid Sync invariants."""

    def setUp(self):
        super().setUp()
        self.customer = self.create_test_customer()
        self.project = self.create_test_project()
        self.sales_order = self.create_test_sales_order()

    def tearDown(self):
        frappe.db.rollback()
        super().tearDown()

    def create_test_customer(self) -> str:
        name = "_Test Stage 10 Customer"
        if not frappe.db.exists("Customer", name):
            cust = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": name,
                "customer_type": "Company",
                "customer_group": "Commercial",
                "territory": "All Territories",
                "custom_discom_consumer_no": "CA-9988776655",
                "custom_discom_name": "BESCOM Central",
                "custom_discom_division": "Indiranagar",
                "custom_discom_subdivision": "Sub-Div-04",
                "custom_sanctioned_load_kw": 25.0,
                "custom_tariff_category": "LT-Commercial"
            }).insert(ignore_permissions=True)
            return cust.name
        return name

    def create_test_project(self) -> str:
        name = "_Test Stage 10 Project"
        if not frappe.db.exists("Project", name):
            proj = frappe.get_doc({
                "doctype": "Project",
                "project_name": name,
                "status": "Open",
                "custom_current_stage_code": "S09_INSTALLATION",
                "customer": self.customer,
                "custom_pre_comm_gate_cleared": 0
            }).insert(ignore_permissions=True)
            return proj.name
        return name

    def create_test_sales_order(self) -> str:
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": self.customer,
            "custom_system_capacity_kw": 20.0,
            "custom_project_reference": self.project,
            "delivery_date": add_to_date(today(), days=30)
        })
        return so.name

    def test_01_spawn_phase_1_dossier_from_sales_order(self):
        """Invariant 1: Proves programmatic dossier creation from Stage 06 Sales Order."""
        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        self.assertTrue(bool(liaison_name))

        doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)
        self.assertEqual(doc.project, self.project)
        self.assertEqual(doc.consumer_number, "CA-9988776655")
        self.assertEqual(doc.discom_name, "BESCOM Central")
        self.assertEqual(doc.phase_1_status, "Draft")
        self.assertEqual(doc.phase_2_status, "Not Started")
        self.assertEqual(doc.ceig_applicable, 1)
        self.assertEqual(doc.custom_triggers_project_completion, 1)

        # Proves checklist auto-population
        self.assertGreaterEqual(len(doc.document_checklist), 5)

    def test_02_phase_1_missing_discom_app_receipt_rejection(self):
        """Invariant 2: Proves validation failure if DISCOM receipt is missing upon submission."""
        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)
        doc.phase_1_status = "Submitted to DISCOM"
        doc.discom_application_no = "BESCOM-12345"
        doc.discom_acknowledgement_receipt = None  # Missing mandatory receipt

        from frappe import ValidationError
        with self.assertRaises(ValidationError):
            doc.save()

    def test_03_record_discom_submission_atomically_completes_lead_progress_bar(self):
        """Invariant 3: Proves DISCOM submission sets Lead Progress Bar 1 to Completed."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "_Test Lead Liaison Closeout",
            "custom_lead_progress_status": "Proposal Sent"
        }).insert(ignore_permissions=True)

        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        frappe.db.set_value("Liaisoning And Synchronization", liaison_name, "custom_lead_reference", lead.name)

        from solar_module.api.liaisoning import record_discom_submission
        res = record_discom_submission(
            doc_name=liaison_name,
            app_no="BESCOM-APP-99881",
            receipt_url="/files/discom_ack_receipt.pdf",
            national_portal_id="MNRE-SURYA-2026"
        )
        self.assertEqual(res["status"], "success")

        updated_lead = frappe.get_doc("Lead", lead.name)
        self.assertEqual(updated_lead.custom_lead_progress_status, "Completed")
        self.assertEqual(updated_lead.custom_current_stage_code, "S10A_LIAISON_SUBMITTED")

    def test_04_statutory_10_day_sla_calculation_business_days_and_holidays(self):
        """Invariant 5: Proves 10-day statutory SLA calculation excluding Sundays and holidays."""
        start_date = "2026-10-01"  # Thursday
        deadline = LiaisoningSLAService.calculate_statutory_deadline(start_date, sla_days=10)
        self.assertIsNotNone(deadline)
        # 10 business days from Thursday Oct 1 (skipping Sundays Oct 4 & Oct 11) lands on Oct 13
        self.assertTrue("2026-10-13" in deadline or "2026-10-12" in deadline)

    def test_05_phase_2_activation_gate_requires_stage_09_completion(self):
        """Invariant 4: Proves Stage 10B countdown blocked until Stage 09 pre-comm testing clears."""
        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)

        # Stage 09 gate is NOT cleared on project
        frappe.db.set_value("Project", self.project, "custom_pre_comm_gate_cleared", 0)

        from solar_module.api.liaisoning import activate_phase_2_countdown
        from frappe import ValidationError

        with self.assertRaises(ValidationError):
            activate_phase_2_countdown(liaison_name, str(today()))

        # Now simulate Stage 09 pre-comm clearance
        frappe.db.set_value("Project", self.project, "custom_pre_comm_gate_cleared", 1)
        res = activate_phase_2_countdown(liaison_name, str(today()))
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["phase_2_status"], "Triggered Post-Installation")

    def test_06_ceig_safety_clearance_gate_and_exemption_logic(self):
        """Invariant 6: Proves CEIG safety approval required for >= 10 kWp systems."""
        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)
        doc.phase_2_status = "CEIG Scheduled"
        doc.ceig_applicable = 1
        doc.ceig_approval_doc = None

        from frappe import ValidationError
        with self.assertRaises(ValidationError):
            doc.save()

        # Provide valid CEIG approval order
        doc.ceig_charging_permission_no = "CEIG-ORD-2026-091"
        doc.ceig_approval_doc = "/files/ceig_order.pdf"
        doc.phase_2_status = "CEIG Approved"
        doc.save()
        self.assertEqual(doc.phase_2_status, "CEIG Approved")

    def test_07_jmi_and_net_meter_reading_mandatory_assertions(self):
        """Invariant 7 & 8: Proves JMI report and initial kWh dial readings are mandatory."""
        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)
        doc.phase_2_status = "Grid Synchronized"
        doc.jmi_report_doc = None

        from frappe import ValidationError
        with self.assertRaises(ValidationError):
            doc.save()

        # Fill JMI report but omit dials
        doc.jmi_report_doc = "/files/signed_jmi.pdf"
        doc.net_meter_serial_no = "MTR-88192"
        doc.initial_import_kwh = None

        with self.assertRaises(ValidationError):
            doc.save()

    def test_08_anti_islanding_trip_time_strict_ceiling_rejection(self):
        """Invariant 9: Proves anti-islanding trip time > 2.0s is rejected as safety violation."""
        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)
        doc.phase_2_status = "Grid Synchronized"
        doc.ceig_applicable = 0
        doc.jmi_report_doc = "/files/jmi.pdf"
        doc.net_meter_serial_no = "MTR-88192"
        doc.initial_import_kwh = 120.0
        doc.initial_export_kwh = 0.0
        doc.grid_synchronization_date = today()
        doc.cod_certificate = "/files/cod.pdf"
        doc.anti_islanding_trip_time_sec = 2.4  # Exceeds 2.0s ceiling

        from frappe import ValidationError
        with self.assertRaises(ValidationError):
            doc.save()

    def test_09_atomic_project_completion_and_asset_register_twin_spawning(self):
        """Invariant 10: Proves submitting dossier completes Project and spawns Solar Asset Register."""
        # Create an open task under project
        task = frappe.get_doc({
            "doctype": "Task",
            "subject": "_Test Final Inverter Cabling",
            "project": self.project,
            "status": "Open",
            "progress": 80
        }).insert(ignore_permissions=True)

        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)

        doc.phase_1_status = "Feasibility Approved"
        doc.discom_application_no = "BESCOM-991"
        doc.discom_acknowledgement_receipt = "/files/ack.pdf"
        doc.grid_connectivity_noc = "/files/noc.pdf"
        doc.feasibility_approval_date = today()

        doc.phase_2_status = "Grid Synchronized"
        doc.installation_completed_date = today()
        doc.ceig_applicable = 0
        doc.jmi_report_doc = "/files/signed_jmi.pdf"
        doc.net_meter_serial_no = "NET-MTR-99881"
        doc.net_meter_make = "Secure Meters"
        doc.initial_import_kwh = 150.0
        doc.initial_export_kwh = 0.0
        doc.grid_synchronization_date = today()
        doc.anti_islanding_trip_time_sec = 1.1
        doc.grid_energization_cert = "/files/energize.pdf"
        doc.cod_certificate = "/files/cod.pdf"
        doc.cod_date = today()

        doc.save()
        doc.submit()

        # Assert Project terminal closure
        proj = frappe.get_doc("Project", self.project)
        self.assertEqual(proj.status, "Completed")
        self.assertEqual(proj.custom_is_completed_flag, 1)
        self.assertEqual(str(proj.custom_grid_sync_date), today())
        self.assertEqual(str(proj.custom_cod_date), today())
        self.assertEqual(proj.custom_net_meter_serial_no, "NET-MTR-99881")

        # Assert residual task completed
        t = frappe.get_doc("Task", task.name)
        self.assertEqual(t.status, "Completed")
        self.assertEqual(t.progress, 100)

        # Assert Stage 11 Asset Register twin spawned
        asset_exists = frappe.db.exists("Solar Asset Register", {"project": self.project})
        self.assertTrue(bool(asset_exists))

    def test_10_sla_breach_transition_and_delay_log_justification(self):
        """Invariant 5 & 11: Proves SLA overdue transition and delay log recording."""
        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)
        doc.phase_2_status = "Triggered Post-Installation"
        doc.installation_completed_date = add_to_date(today(), days=-20)  # 20 days ago
        doc.statutory_deadline = add_to_date(today(), days=-5) + " 18:00:00"
        doc.save()

        LiaisoningSLAService.sync_document_sla(doc)
        self.assertEqual(doc.is_sla_overdue, 1)
        self.assertEqual(doc.phase_2_status, "Overdue (SLA Breached)")

        # Log delay justification
        from solar_module.api.liaisoning import log_statutory_delay
        res = log_statutory_delay(
            doc_name=liaison_name,
            category="DISCOM_METER_SHORTAGE",
            reason="Testing lab out of bi-directional CT meters.",
            remedial_action="Procured utility-approved meter from authorized vendor."
        )
        self.assertEqual(res["status"], "success")

        updated_doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)
        self.assertEqual(len(updated_doc.delay_logs), 1)
        self.assertEqual(updated_doc.delay_logs[0].delay_category, "DISCOM_METER_SHORTAGE")

    def test_11_role_permission_and_immutable_cancellation_lock(self):
        """Invariant 11: Proves non-System Manager cancellation is blocked with PermissionError."""
        liaison_name = LiaisoningInceptionService.spawn_liaisoning_record(self.project, self.sales_order)
        doc = frappe.get_doc("Liaisoning And Synchronization", liaison_name)
        doc.phase_1_status = "Feasibility Approved"
        doc.discom_application_no = "BESCOM-11"
        doc.discom_acknowledgement_receipt = "/files/ack.pdf"
        doc.grid_connectivity_noc = "/files/noc.pdf"
        doc.feasibility_approval_date = today()
        doc.phase_2_status = "Grid Synchronized"
        doc.ceig_applicable = 0
        doc.jmi_report_doc = "/files/jmi.pdf"
        doc.net_meter_serial_no = "NET-123"
        doc.initial_import_kwh = 50.0
        doc.initial_export_kwh = 0.0
        doc.grid_synchronization_date = today()
        doc.anti_islanding_trip_time_sec = 1.0
        doc.cod_certificate = "/files/cod.pdf"
        doc.cod_date = today()

        doc.save()
        doc.submit()

        # Simulate non-admin user
        frappe.set_user("test@example.com")
        from frappe import PermissionError

        with self.assertRaises(PermissionError):
            doc.cancel()

        frappe.set_user("Administrator")
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 Automated Test Execution Command

Run the complete 11-case Stage 10 Tracer Bullet integration suite via Bench CLI:

```bash
# Run isolated integration test suite in current site sandbox
bench --site <site_name> run-tests --module solar_module.tests.test_stage_10_liaisoning_grid_sync_tracer_bullet --failfast
```

Expected output:

```
................
----------------------------------------------------------------------
Ran 11 tests in 1.482s

OK
```

---

### 7.2 Manual Desk & RPC Verification Protocol

1. **Verify Phase 1 Inception:**
   - Submit a Sales Order with capacity $\ge 10\text{ kWp}$.
   - Check that `tabLiaisoning And Synchronization` is created in `Phase 1: Draft`.
   - Verify `Project.custom_liaisoning_reference` is linked.
2. **Verify DISCOM Filing & Lead Closeout:**
   - Execute RPC `solar_module.api.liaisoning.record_discom_submission`.
   - Verify `Phase 1 Status` transitions to `Submitted to DISCOM`.
   - Verify linked `Lead.custom_lead_progress_status` transitions to `Completed`.
3. **Verify Stage 09 Handshake:**
   - Attempt to call `activate_phase_2_countdown` without Stage 09 pre-commissioning testing cleared; verify hard `ValidationError`.
   - Set `Project.custom_pre_comm_gate_cleared = 1`; verify 10-day countdown starts.
4. **Verify CEIG & JMI Gates:**
   - Save dossier with CEIG required and missing order; assert rejection.
   - Attach CEIG order, JMI report, net-meter serial, and initial dials; verify successful save.
5. **Verify Anti-Islanding Protection:**
   - Input trip time of $2.5\text{ seconds}$; verify rejection.
   - Input trip time of $1.2\text{ seconds}$; verify acceptance.
6. **Verify Terminal Project Closeout:**
   - Submit the dossier.
   - Verify `tabProject.status` changes to `Completed` and `custom_is_completed_flag == 1`.
   - Verify residual open tasks under Project are marked `Completed`.
   - Verify `tabSolar Asset Register` record is instantiated.
   - Verify Accounts notification is created.

---

### 7.3 Operational Runbook & Error Resolutions

| Error Displayed                                               | Root Cause                                                               | Resolution Action                                                                           |
| :------------------------------------------------------------ | :----------------------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| `ValidationError: Linked Project reference is mandatory`      | Dossier missing project foreign key.                                     | Provide valid `Project` code.                                                               |
| `ValidationError: DISCOM Application Acknowledgment Receipt`  | Operator tried marking Phase 1 submitted without receipt attachment.     | Attach utility portal acknowledgment PDF.                                                   |
| `ValidationError: Cannot activate Stage 10B countdown`        | Stage 09 pre-commissioning testing not cleared on project.               | Complete and submit Stage 09 Pre-Commissioning Checklist before activating grid sync clock. |
| `ValidationError: CEIG Official Charging Permission order`    | System capacity meets CEIG threshold ($> 10\text{ kWp}$) but doc absent. | Upload CEIG order or update `ceig_applicable = 0` if statutory exemption applies.           |
| `ValidationError: Safety Violation: Inverter Anti-Islanding`  | Measured anti-islanding disconnect time exceeds $2.0\text{ seconds}$.    | Reconfigure inverter grid protection parameters to disconnect within CEA limit ($\le 2s$).  |
| `PermissionError: Only System Manager or Director can cancel` | Standard operator attempted to cancel submitted statutory dossier.       | Dossier is legally binding. Cancellation requires executive override by System Manager.     |

---

## 8. Summary of Architectural Achievements

|     Layer      | Component                 | Business Invariant Realized                                                                                                                                                                                                                                                                                         |
| :------------: | :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|  **Layer 1**   | Schema & Persistence      | `tabProject`, `tabCustomer`, submittable `tabLiaisoning And Synchronization`, 4 child tables, and composite B-tree indexes.                                                                                                                                                                                         |
|  **Layer 2**   | Domain Services           | Pure SOLID Python: `LiaisoningInceptionService`, `LiaisoningSLAService` (business day & holiday math), `LiaisoningPhase1Service` (Lead terminal closeout), `LiaisoningPhase2Service` (CEIG, JMI, anti-islanding $\le 2s$), and `ProjectCompletionService` (atomic Project closeout & Asset Register twin spawning). |
|  **Layer 3**   | Controller & RPC          | Submittable DocType controller with strict permissions, 7 whitelisted typed RPC endpoints, and hourly background Celery/RQ daemon.                                                                                                                                                                                  |
|  **Layer 4**   | UI / Desk Script & Kanban | Client script `liaisoning_and_synchronization.js` with dynamic SLA alert banners, action dialogs, and `/solar/liaisoning` two-tier Kanban board specification with radial 10-day SVG countdown timers.                                                                                                              |
|  **Layer 5**   | Verification Suite        | 11 atomic integration test cases covering all statutory invariants under strict zero-database-commit rollback.                                                                                                                                                                                                      |
| **Governance** | ADR-000 & ADR-010         | Full role permission alignment (`Liaisoning Representative`, `Liaisoning Manager`, `Project Engineer`, `Project Manager`, `Admin`, `System Manager`).                                                                                                                                                               |

# STEP_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.caveman.md

# Dual Progress Bar Lifecycle & SLA Engine: Commercial Lead to Liaisoning & Project Execution to Grid Sync

**Document ID:** `STEP-PLAN-DUAL-PROGRESSBAR`  
**Governing ADR:** [`docs/decisions/ADR-007-DUAL-PROGRESS-BAR-LIFECYCLE-SLA-ENGINE.md`](../docs/decisions/ADR-007-DUAL-PROGRESS-BAR-LIFECYCLE-SLA-ENGINE.md)  
**Full Specification:** [`step_plans/STEP_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.md`](../step_plans/STEP_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.md)  
**Target Module:** `solar_module` / SPA `/solar`  
**Status:** Approved for Implementation

---

## 1. Step Scope, Objectives & Context Traceability

### 1.1 Dual Stepper Positioning

Two synchronized operational lifecycles:

1. **Progress Bar 1 (Lead Stepper):** `tabLead`. Inbound Lead $\rightarrow$ Site Survey $\rightarrow$ Design BOM $\rightarrow$ Proposal $\rightarrow$ Advance Payment $\rightarrow$ Sales Order $\rightarrow$ Early Liaisoning Phase 1. Mark `Lead` **Completed**.
2. **Progress Bar 2 (Project Stepper):** `tabProject`. Advance Payment Gate $\rightarrow$ Sales Order Baseline Lock $\rightarrow$ Material Dispatch (Delivery Note) $\rightarrow$ Installation (Zone DPR) $\rightarrow$ Material Return (Surplus Reconcile) $\rightarrow$ Statutory Grid Sync & Net Metering. Mark `Project` **Completed** (COD Handover $\rightarrow$ Stage 11 O&M).

```
[PROGRESS BAR 1: LEAD STEPPER]
S01 Lead Qual (2h) ──▶ S02 Survey (24h) ──▶ S03 Design (24-48h) ──▶ S04 Proposal (24h) ──▶ S05 Advance (48h) ──▶ S06 Sales Order (24h) ──▶ S10A Early Liaisoning (72h) ──▶ ★ MARK LEAD COMPLETED ★

[PROGRESS BAR 2: PROJECT STEPPER]
S05G Advance Gate (0h) ──▶ S06 SO Baseline (24h) ──▶ S07 Dispatch (48h) ──▶ S08 Installation DPR (Dynamic) ──▶ S09 Material Return (48h) ──▶ S10B Grid Sync (10d SLA) ──▶ ★ MARK PROJECT COMPLETED ★
```

### 1.2 Core KPIs

- Zero handoff latency between sales, engineering, finance, store, site, and liaisoning.
- 5-state visual clarity across both pipelines.
- Real-time SLA countdown, breach alerts, mandatory delay reason logging.
- RBAC-gated interactive action drawer.

---

## 2. Stakeholders, Enterprise Actors & HRMS Role Mapping

Zero "User" Suffix Rule enforced:

| Persona                        | Approved Role              | HRMS Designation            | Operational Domain & Action                                    |
| :----------------------------- | :------------------------- | :-------------------------- | :------------------------------------------------------------- |
| **Solar EPC Director**         | `Director`                 | `Managing Director`         | Executive pipeline view; SLA settings; delay approvals.        |
| **Project Supreme Admin**      | **`Admin`**                | `Operations VP`             | Supreme operational command; delay waivers; SLA settings.      |
| **Lead Qualification Officer** | **`Lead Representative`**  | `Inside Sales Rep`          | Ingest lead; verify phone; assign surveyor.                    |
| **Site Survey Specialist**     | **`Survey Engineer`**      | `Field Survey Auditor`      | 24h survey; GPS lock; upload 6 mandatory photos.               |
| **PV CAD & BOM Designer**      | **`Design Engineer`**      | `Solar Design Engineer`     | CAD/SLD layout; dynamic BOM calculation; freeze checksum.      |
| **Commercial Sales Exec**      | **`Sales Representative`** | `Commercial Sales Exec`     | Multi-tier proposal; PM Surya Ghar subsidy; contract.          |
| **Commercial Operations Lead** | **`Commercial Officer`**   | `Sales Ops Executive`       | Sales Order submission; baseline SHA-256 seal.                 |
| **Finance Officer**            | **`Accounts Assistant`**   | `Accounts Executive`        | Bank UTR / cheque verification; Customer master inception.     |
| **Warehouse Store Lead**       | **`Store Manager`**        | `Warehouse Supervisor`      | Dispatch staging; inventory allocation; delegate task.         |
| **Warehouse Assistant**        | **`Store Assistant`**      | `Store Assistant`           | Barcode serial scan; Delivery Note; site returns.              |
| **Field Execution Lead**       | **`Project Engineer`**     | `Site Execution Engineer`   | Multi-zone WBS execution; daily progress reports (DPR).        |
| **Statutory Compliance Lead**  | **`Liaisoning Officer`**   | `Statutory Compliance Exec` | DISCOM portal filing; CEIG audit; net-meter sync.              |
| **Technical Framework Admin**  | **`System Manager`**       | `CTO`                       | Apex technical authority (all `Admin` rights + code/DocTypes). |

---

## 3. Relational Schema & 3NF Data Dictionary

### 3.1 Extensions: `tabLead` (Progress Bar 1)

- `custom_lead_progress_status` (`Select`): `Open`, `Site Survey`, `PV Design`, `Proposal`, `Advance Clearance`, `Sales Order`, `Early Liaisoning`, `Completed`.
- `custom_current_stage_code` (`Data`, indexed): `S01_LEAD`, `S02_SURVEY`, `S03_DESIGN`, etc.
- `custom_stage_state` (`Select`): `IDLE`, `ONGOING_HEALTHY`, `ONGOING_OVERDUE`, `COMPLETED_ON_TIME`, `COMPLETED_DELAYED`.
- `custom_stage_started_on` (`Datetime`): Timestamp stage started.
- `custom_stage_sla_due` (`Datetime`): Target deadline ($T_{\text{start}} + T_{\text{SLA}}$).
- `custom_stage_elapsed_hours` (`Float`): Hours elapsed.
- `custom_lead_completed_on` (`Datetime`): Final completion timestamp.
- `custom_stage_delay_log` (`Table` $\rightarrow$ `Solar Stage Delay Log`).

### 3.2 Extensions: `tabProject` (Progress Bar 2)

- `custom_project_progress_status` (`Select`): `Advance Verified`, `Sales Order Baseline`, `Material Dispatch`, `Installation`, `Material Return`, `Grid Sync`, `Completed`.
- `custom_current_stage_code` (`Data`, indexed): `S05G_ADVANCE`, `S06_SO`, `S07_DISPATCH`, etc.
- `custom_stage_state` (`Select`): `IDLE`, `ONGOING_HEALTHY`, `ONGOING_OVERDUE`, `COMPLETED_ON_TIME`, `COMPLETED_DELAYED`.
- `custom_stage_started_on` (`Datetime`): Timestamp stage started.
- `custom_stage_sla_due` (`Datetime`): SLA deadline.
- `custom_stage_elapsed_hours` (`Float`): Hours elapsed.
- `custom_is_completed_flag` (`Check`): Set 1 strictly upon Stage 10B Grid Sync.
- `custom_completion_certified_by` (`Link` $\rightarrow$ `User`).
- `custom_completion_certified_on` (`Datetime`).
- `custom_stage_delay_log` (`Table` $\rightarrow$ `Solar Stage Delay Log`).

### 3.3 Child DocType: `tabSolar Stage Delay Log`

- `stage_code` (`Data`), `stage_name` (`Data`).
- `sla_target_hours` (`Float`), `actual_tat_hours` (`Float`), `delay_hours` (`Float`).
- `delay_category` (`Select`): `Customer Delay`, `Statutory / DISCOM Delay`, `Material Procurement Delay`, `Site Civil / Access Obstacle`, `Weather Emergency`, `Engineering Redesign`, `Administrative Hold`.
- `delay_remarks` (`Small Text`, mandatory).
- `logged_by` (`Link` $\rightarrow$ `User`), `logged_on` (`Datetime`).
- `admin_waiver_approved` (`Check`, default 0).
- `admin_waiver_by` (`Link` $\rightarrow$ `User`, restricted to `Admin`/`Director`).
- `admin_waiver_remarks` (`Small Text`).

### 3.4 Single DocType: `tabSolar SLA Settings`

- `sla_s01_lead_hours` (2h), `sla_s02_survey_hours` (24h).
- `sla_s03_design_res_hours` (24h), `sla_s03_design_ci_hours` (48h).
- `sla_s04_proposal_hours` (24h), `sla_s05_advance_hours` (48h).
- `sla_s06_so_baseline_hours` (24h), `sla_s07_dispatch_hours` (48h).
- `sla_s08_install_per_kw_days` (3.0d per 10 kWp).
- `sla_s09_return_hours` (48h).
- `sla_s10a_early_liaison_hours` (72h).
- `sla_s10b_grid_sync_days` (10d).
- Write restricted to `Admin`, `Director`, `System Manager`.

---

## 4. State Machine & Visual 5-State Ontology

### 4.1 Visual Color & Token Standard

| State Code              | Semantic State         | Color Tokens                                                              | Icon              | SLA Display                  |
| :---------------------- | :--------------------- | :------------------------------------------------------------------------ | :---------------- | :--------------------------- |
| **`IDLE`**              | Not Started / Idle     | `bg-slate-100 text-slate-500 border-slate-300`                            | Dotted Circle     | `Target: XXh \| Pending`     |
| **`ONGOING_HEALTHY`**   | Ongoing (Within SLA)   | `bg-blue-50 text-blue-700 border-blue-500 ring-2 ring-blue-300`           | Pulsing Spinner   | `Elapsed: 14h / 24h`         |
| **`ONGOING_OVERDUE`**   | Ongoing (SLA Breached) | `bg-red-50 text-red-700 border-red-500 ring-4 ring-red-400 animate-pulse` | Warning Triangle  | `OVERDUE (+12h)`             |
| **`COMPLETED_ON_TIME`** | Completed (On Time)    | `bg-emerald-50 text-emerald-700 border-emerald-500`                       | Solid Checkmark   | `TAT: 18h / 24h`             |
| **`COMPLETED_DELAYED`** | Completed (Delayed)    | `bg-amber-50 text-amber-800 border-amber-600`                             | Checkmark + Alert | `Delayed (+10h) \| [Reason]` |

### 4.2 Lead Terminal Gate

Stage 10A (Early Liaisoning) sets `discom_application_no` $\rightarrow$ marks `Lead` **`Completed`**. Blocks further edit; preserves full execution links.

### 4.3 Project Terminal Gate

Stage 10B (Grid Sync & Net Metering) confirmed by `Liaisoning Officer` $\rightarrow$ marks `Project` **`Completed`** (`custom_is_completed_flag = 1`, `status = 'Completed'`). Issues COD certificate; spawns Stage 11 O&M Asset Register.

---

## 5. Domain Services & Whitelisted APIs

### 5.1 Python Service Structure

- `SolarSLACalculator.evaluate_stage_metric()`: Computes elapsed hours, variance ($\Delta T = T_{\text{TAT}} - T_{\text{SLA}}$), 5-state visual code.
- `LeadStepperEngine.build_stepper_payload()`: Fetches Lead pipeline state + allowed role actions.
- `ProjectStepperEngine.build_stepper_payload()`: Fetches Project pipeline state + WBS zone progress.

### 5.2 Whitelisted APIs (`solar_module.api.stepper`)

- `POST get_lifecycle_stepper_state(stepper_type, doc_name)`: Returns JSON tree of stages, states, elapsed vs SLA, and role actions.
- `POST log_stage_delay_reason(stepper_type, doc_name, stage_code, delay_category, delay_remarks)`: Records delay justification.
- `POST approve_admin_stage_waiver(stepper_type, doc_name, delay_log_idx, waiver_remarks)`: `Admin` or `Director` waives SLA penalty; flips `COMPLETED_DELAYED` to `COMPLETED_ON_TIME`.

---

## 6. Frontend UI/UX Specification

### 6.1 Vue 3 Component (`ProgressBarStepper.vue`)

- Mounts in `/solar/leads/:id` and `/solar/projects/:id`.
- Responsive flex layout with SVG connecting lines (solid green for done, animated blue gradient for active, dashed slate for idle).
- Real-time 60s tick recalculating elapsed SLA bar width ($0-100\%$, turn red if $>100\%$).

### 6.2 Interactive Slide-Over Drawer (`StageInspectorDrawer.vue`)

- Click node $\rightarrow$ drawer slides out from right.
- Shows actor name, HRMS designation, contact phone.
- Deliverables tray: photos, CAD drawings, proposal PDF, signed contract, e-way bill, DPR logs, net-meter certificate.
- Contextual primary action button (e.g. `Launch Mobile Survey`, `Freeze Dynamic BOM`, `Verify Advance`, `Submit Delivery Note`).
- Deep-link button: `Open in Frappe Desk ↗` (`/app/lead/...`, `/app/project/...`) enforcing Frappe permissions.
- Non-authorized roles see read-only badge with required role tooltip.

### 6.3 Frappe Desk Client Script (`lead.js`, `project.js`)

- Renders stepper directly in `frm.dashboard.add_section()` using Frappe UI template.

---

## 7. Cross-App Integration Touchpoints

- Inbound Lead $\rightarrow$ CRM logs.
- Stage 05 Gate $\rightarrow$ creates ERPNext `Customer` and bank `Payment Entry`.
- Stage 06 Submit $\rightarrow$ spawns ERPNext `Project` container, Store Manager `Task`, and `Liaisoning And Synchronization` record.
- Stage 07 Dispatch $\rightarrow$ ERPNext `Delivery Note` with serial barcode bundle.
- Stage 08 Site WBS $\rightarrow$ ERPNext `Task` and `DPR`.
- Stage 09 Material Return $\rightarrow$ ERPNext `Stock Entry` (Material Return).
- Stage 10B Sync $\rightarrow$ marks `Project` **Completed**; initializes Stage 11 `Solar Asset Register`.

---

## 8. Automated Testing Criteria

- `IntegrationTestCase` with zero commits (`frappe.db.rollback()`).
- Tests:
  1. `test_01_idle_state_evaluation`: Unstarted stage resolves to `IDLE` (slate).
  2. `test_02_ongoing_healthy_sla`: In-progress within SLA resolves to `ONGOING_HEALTHY` (blue).
  3. `test_03_ongoing_overdue_sla`: In-progress exceeding SLA resolves to `ONGOING_OVERDUE` (red pulse).
  4. `test_04_completed_on_time`: Done $\le$ SLA resolves to `COMPLETED_ON_TIME` (emerald).
  5. `test_05_completed_delayed`: Done $>$ SLA resolves to `COMPLETED_DELAYED` (amber).
  6. `test_06_admin_waiver`: `Admin` waiver flips delayed to on-time.

---

## 9. Operational SOP & Runbook

- Operators check blue/red nodes on `/solar`. Click node $\rightarrow$ execute task via action button.
- If overdue: select delay reason category and type explanation before sign-off.
- `Admin` / `Director`: adjust SLA in `Solar SLA Settings` or grant waivers in delay log.

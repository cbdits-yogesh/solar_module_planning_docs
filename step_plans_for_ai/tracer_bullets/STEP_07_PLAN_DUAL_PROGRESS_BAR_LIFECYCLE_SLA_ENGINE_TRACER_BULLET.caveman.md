# STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 07 Dual Progress Bar Lifecycle & SLA Engine

**Document ID:** `TB-07-DUAL-PROGRESSBAR`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.caveman.md`](../STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-007-DUAL-PROGRESS-BAR-LIFECYCLE-SLA-ENGINE.md`](../../docs/decisions/ADR-007-DUAL-PROGRESS-BAR-LIFECYCLE-SLA-ENGINE.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md`](STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md`](STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md`](STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md`](STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md`](STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md`](STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Stage 08 (`Delivery Note` serialized dispatch), Stage 09 (`Project` / WBS installation & DPR), Stage 10 (`Liaisoning And Synchronization` statutory compliance), Stage 11 (`Solar Service Request` & O&M lifecycle)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`Dual Lifecycles`, `Task SLA Engine`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-001`, `BR-005`, `BR-006`, `BR-010`, `BR-017`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-001` to `FR-010`, `FR-017`, `FR-018`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 1: CRM`, `Domain 7: PRJ`, `Domain 8: CMP`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 7`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 3: Lead Detail Stepper`, `Screen 11: Project Execution Stepper`, `Screen 14: Dual-Timing Liaisoning`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-07`)  
**Target Module:** `solar_module` / SPA `/solar` (Extend ERPNext `Lead` and `Project`, register child `Solar Stage Delay Log`, single `Solar SLA Settings`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution  

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** A disposable frontend mockup or isolated Vue animation that renders hardcoded stepper bubbles, ignores underlying DocType lifecycle state transitions, bypasses Redis SLA calculation workers, omits database audit logs, and is discarded without validating end-to-end operational viability.
- **Tracer Bullet:** A permanent, production-grade 5-layer thin vertical slice cutting directly through the live Frappe architecture. It anchors real database schema extensions (`tabLead`, `tabProject`, `tabSolar Stage Delay Log`, `tabSolar SLA Settings`), implements pure SOLID Python calculation engines (`SolarSLACalculator`, `LeadStepperEngine`, `ProjectStepperEngine`), exposes authenticated, typed RPC endpoints (`solar_module.api.stepper`), connects responsive Desk client scripts and Vue 3 drawer components, and executes an automated zero-commit integration test suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 07 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabLead custom fields (progress status, stage code, 5-state visual)     │
│   - tabProject custom fields (progress status, completion flag, certified)  │
│   - tabSolar Stage Delay Log (child table: categories, remarks, waivers)   │
│   - tabSolar SLA Settings (single DocType: stage hours, capacity baselines) │
│   - Composite B-Tree Indexes on stage codes, states, and SLA deadlines      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - SolarSLACalculator (TAT calculation, SLA resolution, 5-state ontology)  │
│   - LeadStepperEngine (Lead pipeline payload generator, role actions)       │
│   - ProjectStepperEngine (Project pipeline payload generator, WBS sync)     │
│   - StageGateValidator (Prerequisite gate checks & terminal transitions)    │
│   - DelayAuditService (Delay categorization, audit trail, waiver logic)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                      │
│   - get_lifecycle_stepper_state RPC (Reactive pipeline tree & permissions)  │
│   - log_stage_delay_reason RPC (Mandatory delay justification recording)    │
│   - approve_admin_stage_waiver RPC (Admin/Director waiver authorization)    │
│   - recompute_enterprise_slas (Redis background daemon worker hook)         │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Workbench Hook                        │
│   - codes/client_script/lead.js & project.js (Dashboard section injector)  │
│   - ProgressBarStepper.vue & StageInspectorDrawer.vue (SPA/Desk UI specs)   │
│   - Tailwind CSS visual token bindings (slate, blue, red, emerald, amber)   │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_stage_07_tracer_bullet.py                       │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Atomic transaction rollback in tearDown (zero DB commits)               │
│   - 10 rigorous test cases validating all Stage 07 invariants               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 10 fundamental business, operational, and technical invariants of Stage 07 across the live Frappe stack:

1. **Dual Stepper Separation & Synchronization:** Progress Bar 1 governs pre-sales and commercial execution on `tabLead` (Stages 01–10A); Progress Bar 2 governs physical construction and utility handover on `tabProject` (Stages 05G–10B).
2. **Canonical 5-State Visual Ontology:** Every single node across both pipelines resolves deterministically to `IDLE` (Slate), `ONGOING_HEALTHY` (Blue), `ONGOING_OVERDUE` (Crimson Pulse), `COMPLETED_ON_TIME` (Emerald), or `COMPLETED_DELAYED` (Warm Amber).
3. **Capacity-Tiered SLA Resolution:** Dynamic TAT deadline resolution from `Solar SLA Settings` based on solar system capacity (e.g., Residential $\le 10$ kWp = 24h design vs C&I $> 10$ kWp = 48h design; 3.0 days per 10 kWp for installation).
4. **Real-Time Variance & TAT Tracking:** Continuous computation of Turnaround Time ($T_{\text{TAT}} = T_{\text{end}} - T_{\text{start}}$) and duration variance ($\Delta T = T_{\text{TAT}} - T_{\text{SLA}}$) with sub-minute precision.
5. **Mandatory Delay Audit Log & Hard Progression Gate:** Overdue stages enforce mandatory selection of standardized delay categories and detailed remarks in `tabSolar Stage Delay Log` before forward progression is unlocked.
6. **Administrative SLA Waiver Authority:** Restricts waiver approvals strictly to `Admin` and `Director`, allowing formal waiving of overdue penalties and instantly flipping node status from `COMPLETED_DELAYED` to `COMPLETED_ON_TIME`.
7. **Role-Gated Interactive Action Drawer:** Frontend Slide-Over inspector renders actor credentials, deliverables tray, and contextual primary action buttons strictly gated by canonical enterprise roles (Zero "User" Suffix rule).
8. **Terminal Lifecycles & Immutability:** Stage 10A early liaisoning filing locks and marks `Lead` as `Completed`; Stage 10B net-meter synchronization marks `Project` as `Completed` (`custom_is_completed_flag = 1`), establishing the immutable baseline for Stage 11 O&M.
9. **Asynchronous SLA Daemon Integration:** Decoupled calculation engine capable of running both synchronously via whitelisted RPC and asynchronously via Redis scheduled daemon (`solar_module.tasks.recompute_enterprise_slas`).
10. **Supreme Authority Hierarchy Standard:** Enforces strict role boundary where Developer Supreme (`System Manager`) manages schemas/code, while Project Supreme (`Admin`) commands operational waivers, SLA thresholds, and executive overrides.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Extends standard ERPNext DocTypes (`Lead`, `Project`), defines the child table `Solar Stage Delay Log`, configures the single DocType `Solar SLA Settings`, and establishes optimized MariaDB composite indexes.

### 2.1 Core DocType Extension: `tabLead` (Progress Bar 1 Host)

Host entity for the Commercial & Pre-Sales Lifecycle Stepper (Stages 01 through 10A).

| Fieldname                     | Label                       | Fieldtype  | Options / Target                                                                                      | Mandatory |    Index     | Rules & Validation Invariants                                                |
| :---------------------------- | :-------------------------- | :--------- | :---------------------------------------------------------------------------------------------------- | :-------: | :----------: | :--------------------------------------------------------------------------- |
| `custom_stepper_section`      | Lifecycle & SLA Stepper     | `Section Break` | -                                                                                                |    No     |      -       | Dashboard container section for Progress Bar 1 visual rendering.             |
| `custom_lead_progress_status` | Stepper Progress Status     | `Select`   | `Open\nSite Survey\nPV Design\nProposal\nAdvance Clearance\nSales Order\nEarly Liaisoning\nCompleted` |  **Yes**  | **Index: 1** | Macro stage pointer. Updated deterministically by state transitions.         |
| `custom_current_stage_code`   | Active Stage Code           | `Data`     | -                                                                                                     |  **Yes**  | **Index: 1** | Canonical stage code: `S01_LEAD`, `S02_SURVEY`, `S03_DESIGN`, etc.           |
| `custom_stage_state`          | Active Stage State          | `Select`   | `IDLE\nONGOING_HEALTHY\nONGOING_OVERDUE\nCOMPLETED_ON_TIME\nCOMPLETED_DELAYED`                        |  **Yes**  | **Index: 1** | Real-time 5-state visual indicator for the active stage.                     |
| `custom_stage_started_on`     | Current Stage Started On    | `Datetime` | -                                                                                                     |    No     |      -       | Audit timestamp when active stage transitioned to ongoing.                   |
| `custom_stage_sla_due`        | Current Stage SLA Deadline  | `Datetime` | -                                                                                                     |    No     | **Index: 1** | Target completion deadline derived from `Solar SLA Settings`.                |
| `custom_stage_elapsed_hours`  | Current Stage Elapsed Hours | `Float`    | -                                                                                                     |    No     |      -       | Real-time computed hours elapsed in current stage. Precision: 2 decimals.    |
| `custom_lead_completed_on`    | Lead Formal Completed On    | `Datetime` | -                                                                                                     |    No     |      -       | Timestamp when Stage 10A early liaisoning marked the lead completed.         |
| `custom_stage_delay_log`      | Stage Delay Audit Log       | `Table`    | `Solar Stage Delay Log`                                                                               |    No     |      -       | Child table storing delay reasons, operator remarks, and Admin waivers.      |

### 2.2 Core DocType Extension: `tabProject` (Progress Bar 2 Host)

Host entity for the Physical Execution, Procurement & Grid Sync Lifecycle Stepper (Stages 05G through 10B).

| Fieldname                        | Label                       | Fieldtype  | Options / Target                                                                                                 | Mandatory |    Index     | Rules & Validation Invariants                                                |
| :------------------------------- | :-------------------------- | :--------- | :--------------------------------------------------------------------------------------------------------------- | :-------: | :----------: | :--------------------------------------------------------------------------- |
| `custom_project_stepper_section` | Execution Lifecycle Stepper | `Section Break` | -                                                                                                           |    No     |      -       | Dashboard container section for Progress Bar 2 visual rendering.             |
| `custom_project_progress_status` | Stepper Progress Status     | `Select`   | `Advance Verified\nSales Order Baseline\nMaterial Dispatch\nInstallation\nMaterial Return\nGrid Sync\nCompleted` |  **Yes**  | **Index: 1** | Macro stage pointer for execution tracking.                                  |
| `custom_current_stage_code`      | Active Stage Code           | `Data`     | -                                                                                                                |  **Yes**  | **Index: 1** | Canonical stage code: `S05G_ADVANCE`, `S06_SO`, `S07_DISPATCH`, etc.         |
| `custom_stage_state`             | Active Stage State          | `Select`   | `IDLE\nONGOING_HEALTHY\nONGOING_OVERDUE\nCOMPLETED_ON_TIME\nCOMPLETED_DELAYED`                                   |  **Yes**  | **Index: 1** | Real-time 5-state visual indicator for the active stage.                     |
| `custom_stage_started_on`        | Current Stage Started On    | `Datetime` | -                                                                                                                |    No     |      -       | Audit timestamp when active execution stage commenced.                       |
| `custom_stage_sla_due`           | Current Stage SLA Deadline  | `Datetime` | -                                                                                                                |    No     | **Index: 1** | Target deadline computed dynamically from capacity and settings.             |
| `custom_stage_elapsed_hours`     | Current Stage Elapsed Hours | `Float`    | -                                                                                                                |    No     |      -       | Real-time computed hours elapsed in current stage. Precision: 2 decimals.    |
| `custom_is_completed_flag`       | Project Formally Completed  | `Check`    | -                                                                                                                |  **Yes**  | **Index: 1** | Default: 0. Set to 1 strictly upon Stage 10B Grid Sync sign-off.             |
| `custom_completion_certified_by` | Completed Certified By      | `Link`     | `User`                                                                                                           |    No     |      -       | `Liaisoning Representative`, `Liaisoning Manager`, or `Admin` certifier.     |
| `custom_completion_certified_on` | Completed Certified On      | `Datetime` | -                                                                                                                |    No     |      -       | Timestamp of formal Commercial Operation Date (COD) commissioning.           |
| `custom_stage_delay_log`         | Stage Delay Audit Log       | `Table`    | `Solar Stage Delay Log`                                                                                          |    No     |      -       | Child table storing execution delay explanations and executive waivers.      |

### 2.3 Standalone Child DocType: `tabSolar Stage Delay Log`

- **DocType Type:** Child Table (`istable = 1`)  
- **Target Module:** `solar_module`  
- **Governance:** Immutable once written; waiver fields writable only by `Admin` or `Director`.

| Fieldname               | Label                         | Fieldtype    | Options / Target                                                                                                                                                   | Mandatory |    Index     | Rules & Validation Invariants                                                |
| :---------------------- | :---------------------------- | :----------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :----------: | :--------------------------------------------------------------------------- |
| `stage_code`            | Stage Code                    | `Data`       | -                                                                                                                                                                  |  **Yes**  | **Index: 1** | Canonical stage identifier (e.g. `S02_SURVEY`, `S07_DISPATCH`).              |
| `stage_name`            | Stage Name                    | `Data`       | -                                                                                                                                                                  |  **Yes**  |      -       | Human-readable stage title.                                                  |
| `sla_target_hours`      | Target SLA (Hours)            | `Float`      | -                                                                                                                                                                  |  **Yes**  |      -       | Baseline target SLA duration configured at stage start.                      |
| `actual_tat_hours`      | Actual TAT (Hours)            | `Float`      | -                                                                                                                                                                  |  **Yes**  |      -       | Total duration spent in stage.                                               |
| `delay_hours`           | Delay Duration (Hours)        | `Float`      | -                                                                                                                                                                  |  **Yes**  |      -       | Positive duration variance ($\Delta T = T_{\text{actual}} - T_{\text{SLA}}$). |
| `delay_category`        | Delay Reason Category         | `Select`     | `Customer Delay\nStatutory / DISCOM Delay\nMaterial Procurement Delay\nSite Civil / Access Obstacle\nWeather Emergency\nEngineering Redesign\nAdministrative Hold` |  **Yes**  | **Index: 1** | Standardized category taxonomy for bottleneck analytics.                     |
| `delay_remarks`         | Operational Delay Explanation | `Small Text` | -                                                                                                                                                                  |  **Yes**  |      -       | Detailed operational justification ($\ge 20$ characters enforced).           |
| `logged_by`             | Logged By Operator            | `Link`       | `User`                                                                                                                                                             |  **Yes**  |      -       | Assignee responsible for logging delay justification.                        |
| `logged_on`             | Logged On Timestamp           | `Datetime`   | -                                                                                                                                                                  |  **Yes**  |      -       | Audit timestamp when delay reason was submitted.                             |
| `admin_waiver_approved` | Admin Waiver Approved         | `Check`      | -                                                                                                                                                                  |  **Yes**  | **Index: 1** | Default: 0. Set to 1 if `Admin` or `Director` grants formal penalty waiver. |
| `admin_waiver_by`       | Waiver Authorized By          | `Link`       | `User`                                                                                                                                                             |    No     |      -       | Restricted strictly to `Admin` or `Director`.                                |
| `admin_waiver_remarks`  | Waiver Authorization Remarks  | `Small Text` | -                                                                                                                                                                  |    No     |      -       | Executive rationale for granting penalty waiver ($\ge 20$ chars).            |

### 2.4 Standalone Single DocType: `tabSolar SLA Settings`

- **DocType Type:** Single (`issingle = 1`)  
- **Target Module:** `solar_module`  
- **Permissions:** Read accessible to all authenticated ERP actors; Write strictly restricted to **`Admin`**, **`Director`**, and **`System Manager`**.

| Fieldname                      | Label                                  | Fieldtype | Default | Description & Operational Impact                                                      |
| :----------------------------- | :------------------------------------- | :-------- | :------ | :------------------------------------------------------------------------------------ |
| `sla_s01_lead_hours`           | S01 Lead Response SLA (Hours)          | `Int`     | `2`     | Maximum time from lead creation to initial qualification and surveyor booking.        |
| `sla_s02_survey_hours`         | S02 Technical Survey SLA (Hours)       | `Int`     | `24`    | Maximum time to complete site survey, lock GPS, and upload 6 mandatory photos.        |
| `sla_s03_design_res_hours`     | S03 PV Design Residential SLA (Hours)  | `Int`     | `24`    | Sizing, CAD layout, and BOM freeze for systems $\le 10$ kWp.                          |
| `sla_s03_design_ci_hours`      | S03 PV Design C&I SLA (Hours)          | `Int`     | `48`    | Sizing, CAD layout, and BOM freeze for systems $> 10$ kWp.                            |
| `sla_s04_proposal_hours`       | S04 Commercial Proposal SLA (Hours)    | `Int`     | `24`    | Multi-scenario pricing, tariff calculation, and proposal delivery.                    |
| `sla_s05_advance_hours`        | S05 Advance Payment Gate SLA (Hours)   | `Int`     | `48`    | Customer advance receipt collection, bank UTR verification, and master inception.     |
| `sla_s06_so_baseline_hours`    | S06 Sales Order Baseline SLA (Hours)   | `Int`     | `24`    | Contract bilateral execution and cryptographic baseline freeze.                       |
| `sla_s07_dispatch_hours`       | S07 Material Dispatch SLA (Hours)      | `Int`     | `48`    | Warehouse staging, SABB serial scanning, vehicle loading, and Delivery Note submit.   |
| `sla_s08_install_per_kw_days`  | S08 Installation Speed (Days / 10 kWp) | `Float`   | `3.0`   | Algorithmic WBS baseline execution speed ($\text{Days} = 3.0 \times \text{kWp} / 10$). |
| `sla_s09_return_hours`         | S09 Material Return SLA (Hours)        | `Int`     | `48`    | Site surplus reconciliation and Stock Entry (Material Return) submission.             |
| `sla_s10a_early_liaison_hours` | S10A Early DISCOM Filing SLA (Hours)   | `Int`     | `72`    | Post-SO KYC collection and grid connectivity portal registration.                     |
| `sla_s10b_grid_sync_days`      | S10B Statutory Grid Sync SLA (Days)    | `Int`     | `10`    | Post-installation CEIG clearance, net-meter installation, and grid synchronization.   |
| `sla_refresh_interval_sec`     | Frontend Stepper Refresh Poll (Sec)    | `Int`     | `60`    | Client-side reactive polling / WebSocket interval for live progress bars.             |

### 2.5 MariaDB Composite Indexes & DDL Optimization

```sql
-- Progress Bar 1 (Lead Stepper) Lookups & Background Daemon Filtering
ALTER TABLE `tabLead`
    ADD INDEX `idx_solar_lead_stepper` (`custom_current_stage_code`, `custom_stage_state`),
    ADD INDEX `idx_solar_lead_sla_due` (`custom_stage_sla_due`, `status`);

-- Progress Bar 2 (Project Stepper) Lookups & Execution Tracking
ALTER TABLE `tabProject`
    ADD INDEX `idx_solar_project_stepper` (`custom_current_stage_code`, `custom_stage_state`),
    ADD INDEX `idx_solar_project_completion` (`custom_is_completed_flag`, `status`),
    ADD INDEX `idx_solar_project_sla_due` (`custom_stage_sla_due`);

-- Stage Delay Log Audit Trail Lookups & Category Analytics
ALTER TABLE `tabSolar Stage Delay Log`
    ADD INDEX `idx_solar_delay_audit` (`parent`, `stage_code`, `delay_category`),
    ADD INDEX `idx_solar_delay_waiver` (`admin_waiver_approved`);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Decoupled, framework-independent Python domain services implementing high-precision SLA mathematics, stage progression rules, role permission validations, and delay logging.

### 3.1 SLA Calculation Engine (`solar_module/services/stepper/sla_calculator.py`)

```python
# Copyright (c) 2026, Sadbhav Solar and contributors
# For license information, please see license.txt

from typing import Dict, Any, Optional
import frappe
from frappe.utils import now_datetime, get_datetime, time_diff_in_hours

class SolarSLACalculator:
    """Pure domain service for SLA duration resolution, elapsed tracking, and 5-state visual evaluation."""

    @staticmethod
    def get_stage_sla_hours(stage_code: str, capacity_kw: float = 0.0) -> float:
        """Fetch configured SLA duration in hours from tabSolar SLA Settings with capacity tiers."""
        settings = frappe.get_cached_doc("Solar SLA Settings")

        # Capacity-dependent dynamic calculations
        if stage_code == "S03_DESIGN":
            return float(settings.sla_s03_design_res_hours or 24) if capacity_kw <= 10.0 else float(settings.sla_s03_design_ci_hours or 48)

        if stage_code == "S08_INSTALLATION":
            rate = float(settings.sla_s08_install_per_kw_days or 3.0)
            if capacity_kw <= 0.0:
                return 72.0  # Default 3 days if capacity unknown
            total_days = max(1.0, round(rate * (capacity_kw / 10.0), 1))
            return float(total_days * 24.0)

        sla_mapping = {
            "S01_LEAD": float(settings.sla_s01_lead_hours or 2),
            "S02_SURVEY": float(settings.sla_s02_survey_hours or 24),
            "S04_PROPOSAL": float(settings.sla_s04_proposal_hours or 24),
            "S05_ADVANCE": float(settings.sla_s05_advance_hours or 48),
            "S05G_ADVANCE": 0.0,  # Zero-duration gate in Project Stepper (inherits Stage 05)
            "S06_SO_BASELINE": float(settings.sla_s06_so_baseline_hours or 24),
            "S07_DISPATCH": float(settings.sla_s07_dispatch_hours or 48),
            "S09_MATERIAL_RETURN": float(settings.sla_s09_return_hours or 48),
            "S10A_EARLY_LIAISON": float(settings.sla_s10a_early_liaison_hours or 72),
            "S10B_GRID_SYNC": float((settings.sla_s10b_grid_sync_days or 10) * 24.0),
        }
        return sla_mapping.get(stage_code, 24.0)

    @classmethod
    def evaluate_stage_metric(
        cls,
        stage_code: str,
        started_on: Optional[str] = None,
        completed_on: Optional[str] = None,
        capacity_kw: float = 0.0,
        has_admin_waiver: bool = False
    ) -> Dict[str, Any]:
        """Compute exact turnaround time, SLA deadline, variance, and 5-state visual code.
        
        5-State Standard:
        1. IDLE: Stage not yet started.
        2. ONGOING_HEALTHY: Active stage within configured SLA window.
        3. ONGOING_OVERDUE: Active stage exceeding configured SLA window.
        4. COMPLETED_ON_TIME: Finished within SLA window (or waiver granted).
        5. COMPLETED_DELAYED: Finished after SLA breach without waiver.
        """
        sla_hours = cls.get_stage_sla_hours(stage_code, capacity_kw)

        if not started_on:
            return {
                "state": "IDLE",
                "target_sla_hours": sla_hours,
                "elapsed_hours": 0.0,
                "variance_hours": 0.0,
                "progress_percent": 0.0,
                "is_overdue": False,
                "badge_label": f"SLA: {int(sla_hours)}h",
                "badge_class": "bg-slate-100 text-slate-600 border-slate-300",
                "icon": "circle-outline"
            }

        start_dt = get_datetime(started_on)
        now_dt = now_datetime()

        if completed_on:
            end_dt = get_datetime(completed_on)
            tat_hours = round(time_diff_in_hours(end_dt, start_dt), 2)
            variance = round(tat_hours - sla_hours, 2)
            is_delayed = (variance > 0.0) and not has_admin_waiver

            return {
                "state": "COMPLETED_DELAYED" if is_delayed else "COMPLETED_ON_TIME",
                "target_sla_hours": sla_hours,
                "elapsed_hours": tat_hours,
                "variance_hours": variance,
                "progress_percent": 100.0,
                "is_overdue": False,
                "badge_label": f"Delayed (+{variance}h)" if is_delayed else f"TAT: {tat_hours}h / {int(sla_hours)}h",
                "badge_class": "bg-amber-100 text-amber-800 border-amber-500" if is_delayed else "bg-emerald-100 text-emerald-800 border-emerald-500",
                "icon": "alert-circle" if is_delayed else "check-circle-solid"
            }

        # Ongoing stage evaluation
        elapsed_hours = round(time_diff_in_hours(now_dt, start_dt), 2)
        variance = round(elapsed_hours - sla_hours, 2)
        is_overdue = (variance > 0.0) and not has_admin_waiver
        progress_pct = min(round((elapsed_hours / max(1.0, sla_hours)) * 100, 1), 100.0) if sla_hours > 0 else 100.0

        return {
            "state": "ONGOING_OVERDUE" if is_overdue else "ONGOING_HEALTHY",
            "target_sla_hours": sla_hours,
            "elapsed_hours": elapsed_hours,
            "variance_hours": variance,
            "progress_percent": progress_pct,
            "is_overdue": is_overdue,
            "badge_label": f"OVERDUE (+{variance}h)" if is_overdue else f"Elapsed: {elapsed_hours}h / {int(sla_hours)}h",
            "badge_class": "bg-red-100 text-red-800 border-red-500 animate-pulse" if is_overdue else "bg-blue-100 text-blue-800 border-blue-500",
            "icon": "alert-triangle-pulse" if is_overdue else "spinner-pulse"
        }
```

### 3.2 Lead Stepper Engine (`solar_module/services/stepper/lead_stepper.py`)

```python
# Copyright (c) 2026, Sadbhav Solar and contributors
# For license information, please see license.txt

from typing import Dict, Any, List
import frappe
from frappe import _
from solar_module.services.stepper.sla_calculator import SolarSLACalculator

class LeadStepperEngine:
    """Constructs the complete Progress Bar 1 pipeline payload for Lead records."""

    LEAD_STAGES = [
        {"code": "S01_LEAD", "name": "Lead Qualification", "role": "Sales Representative"},
        {"code": "S02_SURVEY", "name": "Technical Site Survey", "role": "Survey Engineer"},
        {"code": "S03_DESIGN", "name": "PV CAD & Dynamic BOM", "role": "Design Engineer"},
        {"code": "S04_PROPOSAL", "name": "Quotation & Subsidy", "role": "CRM Representative"},
        {"code": "S05_ADVANCE", "name": "Advance Payment Clearance", "role": "Accounts Assistant"},
        {"code": "S06_SALES_ORDER", "name": "Sales Order Contract Freeze", "role": "Sales Manager"},
        {"code": "S10A_EARLY_LIAISON", "name": "Early DISCOM Filing", "role": "Liaisoning Representative"},
    ]

    @classmethod
    def build_stepper_payload(cls, lead_doc: Any, user: str) -> Dict[str, Any]:
        """Generate structured JSON tree for Progress Bar 1 UI and Slide-Over Drawer."""
        user_roles = set(frappe.get_roles(user))
        is_admin = bool({"Admin", "Director", "System Manager"} & user_roles)
        capacity_kw = float(getattr(lead_doc, "custom_proposed_kw", 0.0) or 0.0)

        # Map delay log waivers
        waiver_map = {}
        for row in getattr(lead_doc, "custom_stage_delay_log", []):
            if row.admin_waiver_approved:
                waiver_map[row.stage_code] = True

        stages_payload: List[Dict[str, Any]] = []
        current_stage = getattr(lead_doc, "custom_current_stage_code", "S01_LEAD")
        lead_completed = bool(getattr(lead_doc, "custom_lead_completed_on", None))

        for idx, stage in enumerate(cls.LEAD_STAGES):
            code = stage["code"]
            has_waiver = waiver_map.get(code, False)

            # Determine stage chronological state
            started_on = None
            completed_on = None

            if lead_completed:
                started_on = lead_doc.creation
                completed_on = lead_doc.custom_lead_completed_on
            elif code == current_stage:
                started_on = getattr(lead_doc, "custom_stage_started_on", lead_doc.creation)
                completed_on = None
            elif cls._is_prior_stage(code, current_stage):
                started_on = lead_doc.creation
                completed_on = getattr(lead_doc, "custom_stage_started_on", lead_doc.creation)
            else:
                started_on = None
                completed_on = None

            metric = SolarSLACalculator.evaluate_stage_metric(
                stage_code=code,
                started_on=str(started_on) if started_on else None,
                completed_on=str(completed_on) if completed_on else None,
                capacity_kw=capacity_kw,
                has_admin_waiver=has_waiver
            )

            # Check role-based operational permissions
            required_role = stage["role"]
            can_execute = (required_role in user_roles) or is_admin

            stages_payload.append({
                "sequence": idx + 1,
                "stage_code": code,
                "stage_name": stage["name"],
                "required_role": required_role,
                "can_execute": can_execute,
                "metric": metric,
                "deliverables": cls._get_stage_deliverables(lead_doc, code)
            })

        return {
            "stepper_type": "lead",
            "doc_name": lead_doc.name,
            "title": f"Lead Commercial Lifecycle ({lead_doc.name})",
            "capacity_kw": capacity_kw,
            "current_stage_code": current_stage,
            "is_terminal_completed": lead_completed,
            "completed_on": lead_doc.custom_lead_completed_on if lead_completed else None,
            "stages": stages_payload
        }

    @classmethod
    def _is_prior_stage(cls, stage_code: str, current_stage_code: str) -> bool:
        codes = [s["code"] for s in cls.LEAD_STAGES]
        try:
            return codes.index(stage_code) < codes.index(current_stage_code)
        except ValueError:
            return False

    @classmethod
    def _get_stage_deliverables(cls, lead_doc: Any, stage_code: str) -> Dict[str, Any]:
        """Fetch linked documents and deliverables for drawer rendering."""
        if stage_code == "S01_LEAD":
            return {
                "mobile_verified": bool(lead_doc.mobile_no and len(lead_doc.mobile_no) == 10),
                "proposed_kw": getattr(lead_doc, "custom_proposed_kw", None),
                "surveyor_assigned": getattr(lead_doc, "custom_survey_assigned_to", None)
            }
        elif stage_code == "S02_SURVEY":
            survey_name = frappe.db.get_value("Site Survey", {"lead": lead_doc.name}, "name")
            return {
                "site_survey_doc": survey_name,
                "has_gps": bool(survey_name and frappe.db.get_value("Site Survey", survey_name, "custom_latitude")),
                "photos_count": frappe.db.count("Site Survey Doc Table", {"parent": survey_name}) if survey_name else 0
            }
        elif stage_code == "S03_DESIGN":
            design_name = frappe.db.get_value("Survey Engineering Design", {"lead": lead_doc.name}, "name")
            return {
                "design_doc": design_name,
                "bom_items_count": frappe.db.count("Quotation BOM Item", {"parent": design_name}) if design_name else 0
            }
        elif stage_code == "S04_PROPOSAL":
            quotation = frappe.db.get_value("Quotation", {"lead": lead_doc.name, "custom_is_finalized": 1}, ["name", "grand_total"], as_dict=True)
            return quotation or {}
        elif stage_code == "S05_ADVANCE":
            return {
                "advance_verified": bool(getattr(lead_doc, "custom_advance_verified", 0)),
                "customer": getattr(lead_doc, "customer", None)
            }
        elif stage_code == "S06_SALES_ORDER":
            so = frappe.db.get_value("Sales Order", {"custom_lead_reference": lead_doc.name, "docstatus": 1}, ["name", "custom_baseline_sha256"], as_dict=True)
            return so or {}
        elif stage_code == "S10A_EARLY_LIAISON":
            liaison = frappe.db.get_value("Liaisoning And Synchronization", {"custom_lead_reference": lead_doc.name}, ["name", "custom_discom_application_no"], as_dict=True)
            return liaison or {}
        return {}
```

### 3.3 Project Stepper Engine (`solar_module/services/stepper/project_stepper.py`)

```python
# Copyright (c) 2026, Sadbhav Solar and contributors
# For license information, please see license.txt

from typing import Dict, Any, List
import frappe
from frappe import _
from solar_module.services.stepper.sla_calculator import SolarSLACalculator

class ProjectStepperEngine:
    """Constructs the complete Progress Bar 2 pipeline payload for Project execution records."""

    PROJECT_STAGES = [
        {"code": "S05G_ADVANCE", "name": "Advance Clearance Gate", "role": "Accounts Manager"},
        {"code": "S06_SO_BASELINE", "name": "Commercial Baseline Lock", "role": "Sales Manager"},
        {"code": "S07_DISPATCH", "name": "Material Dispatch (SABB)", "role": "Store Manager"},
        {"code": "S08_INSTALLATION", "name": "Multi-Zone Installation (DPR)", "role": "Project Engineer"},
        {"code": "S09_MATERIAL_RETURN", "name": "Surplus Material Reconciliation", "role": "Store Assistant"},
        {"code": "S10B_GRID_SYNC", "name": "Statutory Grid Synchronization", "role": "Liaisoning Manager"},
    ]

    @classmethod
    def build_stepper_payload(cls, project_doc: Any, user: str) -> Dict[str, Any]:
        """Generate structured JSON tree for Progress Bar 2 UI, WBS progress, and Slide-Over Drawer."""
        user_roles = set(frappe.get_roles(user))
        is_admin = bool({"Admin", "Director", "System Manager"} & user_roles)
        capacity_kw = float(getattr(project_doc, "custom_system_capacity_kw", 0.0) or 0.0)

        # Map delay log waivers
        waiver_map = {}
        for row in getattr(project_doc, "custom_stage_delay_log", []):
            if row.admin_waiver_approved:
                waiver_map[row.stage_code] = True

        stages_payload: List[Dict[str, Any]] = []
        current_stage = getattr(project_doc, "custom_current_stage_code", "S05G_ADVANCE")
        project_completed = bool(getattr(project_doc, "custom_is_completed_flag", 0))

        for idx, stage in enumerate(cls.PROJECT_STAGES):
            code = stage["code"]
            has_waiver = waiver_map.get(code, False)

            # Determine stage chronological state
            started_on = None
            completed_on = None

            if project_completed:
                started_on = project_doc.creation
                completed_on = project_doc.custom_completion_certified_on or project_doc.modified
            elif code == "S05G_ADVANCE":
                # Pre-cleared financial gate in Project Stepper
                started_on = project_doc.creation
                completed_on = project_doc.creation
            elif code == current_stage:
                started_on = getattr(project_doc, "custom_stage_started_on", project_doc.creation)
                completed_on = None
            elif cls._is_prior_stage(code, current_stage):
                started_on = project_doc.creation
                completed_on = getattr(project_doc, "custom_stage_started_on", project_doc.creation)
            else:
                started_on = None
                completed_on = None

            metric = SolarSLACalculator.evaluate_stage_metric(
                stage_code=code,
                started_on=str(started_on) if started_on else None,
                completed_on=str(completed_on) if completed_on else None,
                capacity_kw=capacity_kw,
                has_admin_waiver=has_waiver
            )

            required_role = stage["role"]
            can_execute = (required_role in user_roles) or is_admin

            stages_payload.append({
                "sequence": idx + 1,
                "stage_code": code,
                "stage_name": stage["name"],
                "required_role": required_role,
                "can_execute": can_execute,
                "metric": metric,
                "deliverables": cls._get_stage_deliverables(project_doc, code)
            })

        return {
            "stepper_type": "project",
            "doc_name": project_doc.name,
            "title": f"Project Execution Lifecycle ({project_doc.name})",
            "capacity_kw": capacity_kw,
            "current_stage_code": current_stage,
            "is_terminal_completed": project_completed,
            "completed_on": project_doc.custom_completion_certified_on if project_completed else None,
            "completed_by": getattr(project_doc, "custom_completion_certified_by", None),
            "stages": stages_payload
        }

    @classmethod
    def _is_prior_stage(cls, stage_code: str, current_stage_code: str) -> bool:
        codes = [s["code"] for s in cls.PROJECT_STAGES]
        try:
            return codes.index(stage_code) < codes.index(current_stage_code)
        except ValueError:
            return False

    @classmethod
    def _get_stage_deliverables(cls, project_doc: Any, stage_code: str) -> Dict[str, Any]:
        """Fetch linked documents and physical execution artifacts."""
        if stage_code == "S05G_ADVANCE":
            return {"gate_cleared": True, "source": "Stage 05 Financial Clearance"}
        elif stage_code == "S06_SO_BASELINE":
            return {
                "sales_order": getattr(project_doc, "sales_order", None),
                "baseline_hash": getattr(project_doc, "custom_baseline_sha256", None)
            }
        elif stage_code == "S07_DISPATCH":
            dn = frappe.db.get_value("Delivery Note", {"project": project_doc.name, "docstatus": 1}, ["name", "posting_date"], as_dict=True)
            return dn or {}
        elif stage_code == "S08_INSTALLATION":
            tasks_total = frappe.db.count("Task", {"project": project_doc.name})
            tasks_closed = frappe.db.count("Task", {"project": project_doc.name, "status": "Completed"})
            return {
                "tasks_total": tasks_total,
                "tasks_closed": tasks_closed,
                "wbs_completion_pct": round((tasks_closed / max(1, tasks_total)) * 100, 1)
            }
        elif stage_code == "S09_MATERIAL_RETURN":
            stock_entry = frappe.db.get_value("Stock Entry", {"project": project_doc.name, "purpose": "Material Return", "docstatus": 1}, "name")
            return {"stock_entry_return": stock_entry}
        elif stage_code == "S10B_GRID_SYNC":
            liaison = frappe.db.get_value("Liaisoning And Synchronization", {"custom_project_reference": project_doc.name, "docstatus": 1}, ["name", "custom_cod_certificate_ref", "custom_bi_meter_no"], as_dict=True)
            return liaison or {}
        return {}
```

### 3.4 Stage Gate Validator (`solar_module/services/stepper/stage_gate_validator.py`)

```python
# Copyright (c) 2026, Sadbhav Solar and contributors
# For license information, please see license.txt

from typing import Any
import frappe
from frappe import _
from frappe.utils import now_datetime

class StageGateValidator:
    """Enforces strict server-side verification gates and terminal lifecycle locks."""

    @staticmethod
    def validate_delay_logging_before_progression(doc: Any, target_stage_code: str) -> None:
        """Assert that if current stage is OVERDUE, a categorized delay justification is present."""
        if getattr(doc, "custom_stage_state", None) == "ONGOING_OVERDUE":
            current_stage = getattr(doc, "custom_current_stage_code", "")
            has_log = False
            for row in getattr(doc, "custom_stage_delay_log", []):
                if row.stage_code == current_stage and row.delay_category and len(row.delay_remarks or "") >= 20:
                    has_log = True
                    break

            if not has_log:
                frappe.throw(
                    _("Cannot progress from stage {0} to {1}: SLA is overdue. A mandatory delay explanation "
                      "(minimum 20 characters) must be logged in the Stage Delay Log.").format(current_stage, target_stage_code),
                    frappe.ValidationError
                )

    @staticmethod
    def execute_terminal_lead_completion(lead_doc: Any, discom_application_no: str) -> None:
        """Mark tabLead as formally COMPLETED upon Stage 10A early liaisoning completion."""
        if not discom_application_no:
            frappe.throw(_("Cannot complete Lead lifecycle: DISCOM Application Number is mandatory."), frappe.ValidationError)

        lead_doc.custom_lead_progress_status = "Completed"
        lead_doc.custom_current_stage_code = "S10A_EARLY_LIAISON"
        lead_doc.custom_stage_state = "COMPLETED_ON_TIME"
        lead_doc.custom_lead_completed_on = now_datetime()
        lead_doc.status = "Converted"
        lead_doc.save(ignore_permissions=True)

    @staticmethod
    def execute_terminal_project_completion(project_doc: Any, cod_certificate_ref: str, certifier_user: str) -> None:
        """Mark tabProject as formally COMPLETED upon Stage 10B statutory grid sync."""
        if not cod_certificate_ref:
            frappe.throw(_("Cannot complete Project: COD (Commercial Operation Date) Certificate reference is mandatory."), frappe.ValidationError)

        project_doc.custom_project_progress_status = "Completed"
        project_doc.custom_current_stage_code = "S10B_GRID_SYNC"
        project_doc.custom_stage_state = "COMPLETED_ON_TIME"
        project_doc.custom_is_completed_flag = 1
        project_doc.custom_completion_certified_by = certifier_user
        project_doc.custom_completion_certified_on = now_datetime()
        project_doc.status = "Completed"
        project_doc.save(ignore_permissions=True)
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

Exposes authenticated, typed RPC endpoints for frontend stepper queries, delay justification logging, executive SLA waiver authorization, and Redis background daemon evaluation.

### 4.1 Whitelisted Stepper RPC Endpoints (`solar_module/api/stepper.py`)

```python
# Copyright (c) 2026, Sadbhav Solar and contributors
# For license information, please see license.txt

from typing import Dict, Any
import frappe
from frappe import _
from frappe.utils import now_datetime
from solar_module.services.stepper.lead_stepper import LeadStepperEngine
from solar_module.services.stepper.project_stepper import ProjectStepperEngine

@frappe.whitelist(methods=["POST"])
def get_lifecycle_stepper_state(stepper_type: str, doc_name: str) -> Dict[str, Any]:
    """Fetch complete reactive lifecycle stepper JSON tree with role action permissions."""
    if not stepper_type or not doc_name:
        frappe.throw(_("Missing required arguments: stepper_type and doc_name"), frappe.ValidationError)

    if stepper_type == "lead":
        doc = frappe.get_doc("Lead", doc_name)
        doc.check_permission("read")
        return LeadStepperEngine.build_stepper_payload(doc, frappe.session.user)

    elif stepper_type == "project":
        doc = frappe.get_doc("Project", doc_name)
        doc.check_permission("read")
        return ProjectStepperEngine.build_stepper_payload(doc, frappe.session.user)

    else:
        frappe.throw(_("Invalid stepper_type: '{0}'. Expected 'lead' or 'project'").format(stepper_type), frappe.ValidationError)

@frappe.whitelist(methods=["POST"])
def log_stage_delay_reason(
    stepper_type: str,
    doc_name: str,
    stage_code: str,
    delay_category: str,
    delay_remarks: str
) -> Dict[str, Any]:
    """Append validated delay explanation to document's custom_stage_delay_log."""
    if not delay_category or not delay_remarks:
        frappe.throw(_("Delay Category and Operational Remarks are strictly mandatory."), frappe.ValidationError)

    if len(delay_remarks.strip()) < 20:
        frappe.throw(_("Delay Remarks must contain at least 20 characters of detailed operational rationale."), frappe.ValidationError)

    doctype = "Lead" if stepper_type == "lead" else "Project"
    doc = frappe.get_doc(doctype, doc_name)
    doc.check_permission("write")

    doc.append("custom_stage_delay_log", {
        "stage_code": stage_code,
        "stage_name": stage_code.replace("_", " ").title(),
        "delay_category": delay_category,
        "delay_remarks": delay_remarks.strip(),
        "logged_by": frappe.session.user,
        "logged_on": now_datetime(),
        "admin_waiver_approved": 0
    })
    doc.save(ignore_permissions=True)

    return {"status": "success", "message": _("Operational delay justification recorded successfully.")}

@frappe.whitelist(methods=["POST"])
def approve_admin_stage_waiver(
    stepper_type: str,
    doc_name: str,
    delay_log_idx: int,
    waiver_remarks: str
) -> Dict[str, Any]:
    """Allow Admin or Director to grant formal waiver for overdue stage penalty.
    
    Supreme Authority Enforcement:
    Restricted strictly to Admin, Director, or System Manager. Frontline operators cannot approve waivers.
    """
    user_roles = set(frappe.get_roles(frappe.session.user))
    if not ({"Admin", "Director", "System Manager"} & user_roles):
        frappe.throw(_("Permission Denied: Only Admin, Director, or System Manager can authorize SLA waivers."), frappe.PermissionError)

    if not waiver_remarks or len(waiver_remarks.strip()) < 20:
        frappe.throw(_("Executive Waiver Remarks must contain at least 20 characters of justification."), frappe.ValidationError)

    doctype = "Lead" if stepper_type == "lead" else "Project"
    doc = frappe.get_doc(doctype, doc_name)

    try:
        row = doc.custom_stage_delay_log[int(delay_log_idx) - 1]
    except (IndexError, TypeError):
        frappe.throw(_("Invalid delay log row reference: {0}").format(delay_log_idx), frappe.ValidationError)

    row.admin_waiver_approved = 1
    row.admin_waiver_by = frappe.session.user
    row.admin_waiver_remarks = waiver_remarks.strip()
    doc.save(ignore_permissions=True)

    return {"status": "success", "message": _("Administrative SLA waiver granted successfully.")}
```

### 4.2 Redis Background Daemon Hook (`solar_module/tasks.py`)

```python
# Copyright (c) 2026, Sadbhav Solar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime
from solar_module.services.stepper.sla_calculator import SolarSLACalculator

def recompute_enterprise_slas():
    """Background cron executed every 15 minutes to evaluate active SLA countdowns across active leads & projects."""
    now_dt = now_datetime()

    # 1. Evaluate Active Leads
    active_leads = frappe.get_all(
        "Lead",
        filters={"status": ["not in", ["Converted", "Lost", "Do Not Contact"]], "custom_current_stage_code": ["is", "set"]},
        fields=["name", "custom_current_stage_code", "custom_stage_started_on", "custom_proposed_kw", "custom_stage_state"]
    )

    for lead in active_leads:
        metric = SolarSLACalculator.evaluate_stage_metric(
            stage_code=lead.custom_current_stage_code,
            started_on=lead.custom_stage_started_on,
            completed_on=None,
            capacity_kw=float(lead.custom_proposed_kw or 0.0)
        )
        if metric["state"] != lead.custom_stage_state:
            frappe.db.set_value("Lead", lead.name, {
                "custom_stage_state": metric["state"],
                "custom_stage_elapsed_hours": metric["elapsed_hours"]
            }, update_modified=False)

    # 2. Evaluate Active Projects
    active_projects = frappe.get_all(
        "Project",
        filters={"custom_is_completed_flag": 0, "status": ["not in", ["Completed", "Cancelled"]], "custom_current_stage_code": ["is", "set"]},
        fields=["name", "custom_current_stage_code", "custom_stage_started_on", "custom_system_capacity_kw", "custom_stage_state"]
    )

    for project in active_projects:
        metric = SolarSLACalculator.evaluate_stage_metric(
            stage_code=project.custom_current_stage_code,
            started_on=project.custom_stage_started_on,
            completed_on=None,
            capacity_kw=float(project.custom_system_capacity_kw or 0.0)
        )
        if metric["state"] != project.custom_stage_state:
            frappe.db.set_value("Project", project.name, {
                "custom_stage_state": metric["state"],
                "custom_stage_elapsed_hours": metric["elapsed_hours"]
            }, update_modified=False)
```

---

## 5. Layer 4: Desk Client Script & Dynamic Workbench Hook

Provides real-time interactive lifecycle progress bars in Frappe Desk and responsive SPA Drawer components.

### 5.1 Desk Dashboard Injection Script (`codes/client_script/lead.js` & `project.js`)

```javascript
// Copyright (c) 2026, Sadbhav Solar and contributors
// Desk Client Script: Inject Interactive Lifecycle Progress Bar into Form Dashboard

frappe.ui.form.on("Lead", {
  refresh(frm) {
    if (!frm.is_new()) {
      render_lifecycle_stepper(frm, "lead");
    }
  },
});

frappe.ui.form.on("Project", {
  refresh(frm) {
    if (!frm.is_new()) {
      render_lifecycle_stepper(frm, "project");
    }
  },
});

function render_lifecycle_stepper(frm, stepper_type) {
  frappe.call({
    method: "solar_module.api.stepper.get_lifecycle_stepper_state",
    args: { stepper_type: stepper_type, doc_name: frm.doc.name },
    freeze: false,
    callback(r) {
      if (r.message && r.message.stages) {
        frm.dashboard.clear_headline();
        const html = build_stepper_html(r.message);
        const section = frm.dashboard.add_section(
          html,
          __("Solar Lifecycle & SLA Engine Tracker"),
        );
        bind_stepper_interaction_events(section, frm, r.message);
      }
    },
  });
}

function build_stepper_html(data) {
  let html = `<div class="solar-stepper-container" style="display:flex; align-items:center; justify-content:space-between; padding:12px; background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0; overflow-x:auto;">`;

  data.stages.forEach((st, idx) => {
    const isLast = idx === data.stages.length - 1;
    const badgeColor = st.metric.badge_class || "bg-slate-100";

    html += `
            <div class="stepper-node-item" data-stage="${st.stage_code}" style="display:flex; flex-direction:column; align-items:center; cursor:pointer; min-width:120px;">
                <div class="stepper-bubble ${badgeColor}" style="width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:12px; margin-bottom:6px;">
                    ${st.sequence}
                </div>
                <div style="font-size:11px; font-weight:600; text-align:center; color:#1e293b;">${st.stage_name}</div>
                <div style="font-size:10px; color:#64748b; margin-top:2px;">${st.metric.badge_label}</div>
            </div>
        `;

    if (!isLast) {
      const lineClass =
        st.metric.state.indexOf("COMPLETED") >= 0
          ? "border-emerald-500"
          : "border-slate-300";
      html += `<div style="flex:1; height:2px; border-top:2px dashed; margin:0 8px; margin-bottom:24px;" class="${lineClass}"></div>`;
    }
  });

  html += `</div>`;
  return html;
}

function bind_stepper_interaction_events(section, frm, data) {
  $(section)
    .find(".stepper-node-item")
    .on("click", function () {
      const stageCode = $(this).attr("data-stage");
      const stageData = data.stages.find((s) => s.stage_code === stageCode);
      if (!stageData) return;

      open_stage_inspector_dialog(frm, data.stepper_type, stageData);
    });
}

function open_stage_inspector_dialog(frm, stepper_type, stageData) {
  const d = new frappe.ui.Dialog({
    title: `${stageData.sequence}. ${stageData.stage_name}`,
    fields: [
      {
        fieldtype: "HTML",
        fieldname: "inspector_html",
        options: `
                <div style="padding:10px;">
                    <p><strong>Required Role:</strong> ${stageData.required_role}</p>
                    <p><strong>Current State:</strong> <span class="badge ${stageData.metric.badge_class}">${stageData.metric.state}</span></p>
                    <p><strong>Target SLA:</strong> ${stageData.metric.target_sla_hours}h</p>
                    <p><strong>Elapsed Hours:</strong> ${stageData.metric.elapsed_hours}h</p>
                    <p><strong>Variance:</strong> ${stageData.metric.variance_hours}h</p>
                </div>
            `,
      },
    ],
  });

  if (
    stageData.metric.state === "ONGOING_OVERDUE" &&
    stageData.stage_code === frm.doc.custom_current_stage_code
  ) {
    d.add_custom_action(__("Log Delay Explanation"), () => {
      prompt_delay_reason_modal(
        frm,
        stepper_type,
        stageData.stage_code,
        () => d.hide(),
      );
    });
  }

  d.show();
}

function prompt_delay_reason_modal(frm, stepper_type, stageCode, callback) {
  frappe.prompt(
    [
      {
        fieldname: "category",
        label: __("Delay Category"),
        fieldtype: "Select",
        options:
          "Customer Delay\nStatutory / DISCOM Delay\nMaterial Procurement Delay\nSite Civil / Access Obstacle\nWeather Emergency\nEngineering Redesign\nAdministrative Hold",
        reqd: 1,
      },
      {
        fieldname: "remarks",
        label: __("Detailed Explanation (min 20 chars)"),
        fieldtype: "Small Text",
        reqd: 1,
      },
    ],
    (values) => {
      frappe.call({
        method: "solar_module.api.stepper.log_stage_delay_reason",
        args: {
          stepper_type: stepper_type,
          doc_name: frm.doc.name,
          stage_code: stageCode,
          delay_category: values.category,
          delay_remarks: values.remarks,
        },
        callback(r) {
          if (!r.exc) {
            frappe.show_alert({
              message: __("Delay reason recorded"),
              indicator: "green",
            });
            frm.reload_doc();
            if (callback) callback();
          }
        },
      });
    },
    __("Mandatory SLA Delay Justification"),
  );
}
```

### 5.2 Vue 3 Visual Stepper Specification (`ProgressBarStepper.vue`)

- **Component Standard:** Vue 3 Composition API (`<script setup>`) with Tailwind CSS classes.
- **Visual State Bindings:**
  - `IDLE`: `bg-slate-100 text-slate-500 border-slate-300`
  - `ONGOING_HEALTHY`: `bg-blue-50 text-blue-700 border-blue-500 ring-2 ring-blue-300`
  - `ONGOING_OVERDUE`: `bg-red-50 text-red-700 border-red-500 ring-4 ring-red-400 animate-pulse`
  - `COMPLETED_ON_TIME`: `bg-emerald-50 text-emerald-700 border-emerald-500`
  - `COMPLETED_DELAYED`: `bg-amber-50 text-amber-800 border-amber-600`
- **Slide-Over Inspector (`StageInspectorDrawer.vue`):** Right-hand flyout showing stage actor, deliverables checklist, action buttons, and delay waiver triggers.

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

A complete, executable Python integration test suite subclassing `frappe.testing.IntegrationTestCase` with zero commits, proving all 10 invariants.

### 6.1 Integration Test Suite (`solar_module/tests/test_stage_07_tracer_bullet.py`)

```python
# Copyright (c) 2026, Sadbhav Solar and contributors
# For license information, please see license.txt

import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import now_datetime, add_to_date, today
from solar_module.services.stepper.sla_calculator import SolarSLACalculator
from solar_module.services.stepper.lead_stepper import LeadStepperEngine
from solar_module.services.stepper.project_stepper import ProjectStepperEngine
from solar_module.services.stepper.stage_gate_validator import StageGateValidator
from solar_module.api.stepper import get_lifecycle_stepper_state, log_stage_delay_reason, approve_admin_stage_waiver

class TestStage07DualProgressBarTracerBullet(IntegrationTestCase):
    """Pragmatic Programmer 5-Layer Integration Test Suite for Stage 07 Dual Progress Bar & SLA Engine."""

    def setUp(self):
        super().setUp()
        self.cleanup_records()
        self.setup_test_prerequisites()

    def tearDown(self):
        self.cleanup_records()
        frappe.db.rollback()
        super().tearDown()

    def cleanup_records(self):
        """Zero-commit cleanup enforcing clean test isolation."""
        test_leads = ["TEST-LEAD-TB07-001", "TEST-LEAD-TB07-002"]
        test_projects = ["TEST-PROJ-TB07-001"]

        for l in test_leads:
            frappe.db.delete("Solar Stage Delay Log", {"parent": l})
            frappe.db.delete("Lead", {"name": l})

        for p in test_projects:
            frappe.db.delete("Solar Stage Delay Log", {"parent": p})
            frappe.db.delete("Project", {"name": p})

    def setup_test_prerequisites(self):
        """Ensure Solar SLA Settings exists with standardized defaults."""
        settings = frappe.get_single("Solar SLA Settings")
        settings.sla_s01_lead_hours = 2
        settings.sla_s02_survey_hours = 24
        settings.sla_s03_design_res_hours = 24
        settings.sla_s03_design_ci_hours = 48
        settings.sla_s04_proposal_hours = 24
        settings.sla_s05_advance_hours = 48
        settings.sla_s06_so_baseline_hours = 24
        settings.sla_s07_dispatch_hours = 48
        settings.sla_s08_install_per_kw_days = 3.0
        settings.sla_s09_return_hours = 48
        settings.sla_s10a_early_liaison_hours = 72
        settings.sla_s10b_grid_sync_days = 10
        settings.save(ignore_permissions=True)

    def test_01_idle_state_evaluation(self):
        """Invariant 1: Unstarted stage resolves to IDLE with slate visual tokens."""
        metric = SolarSLACalculator.evaluate_stage_metric(
            stage_code="S02_SURVEY",
            started_on=None,
            completed_on=None,
            capacity_kw=5.0
        )
        self.assertEqual(metric["state"], "IDLE")
        self.assertEqual(metric["progress_percent"], 0.0)
        self.assertFalse(metric["is_overdue"])
        self.assertIn("slate", metric["badge_class"])

    def test_02_ongoing_healthy_sla_evaluation(self):
        """Invariant 2: Active stage within configured SLA resolves to ONGOING_HEALTHY."""
        started_3h_ago = add_to_date(now_datetime(), hours=-3)
        metric = SolarSLACalculator.evaluate_stage_metric(
            stage_code="S02_SURVEY",  # SLA is 24h
            started_on=str(started_3h_ago),
            completed_on=None,
            capacity_kw=5.0
        )
        self.assertEqual(metric["state"], "ONGOING_HEALTHY")
        self.assertFalse(metric["is_overdue"])
        self.assertIn("blue", metric["badge_class"])
        self.assertGreater(metric["elapsed_hours"], 2.9)

    def test_03_ongoing_overdue_sla_evaluation(self):
        """Invariant 3: Active stage exceeding configured SLA resolves to ONGOING_OVERDUE with red pulse."""
        started_30h_ago = add_to_date(now_datetime(), hours=-30)
        metric = SolarSLACalculator.evaluate_stage_metric(
            stage_code="S02_SURVEY",  # SLA is 24h
            started_on=str(started_30h_ago),
            completed_on=None,
            capacity_kw=5.0
        )
        self.assertEqual(metric["state"], "ONGOING_OVERDUE")
        self.assertTrue(metric["is_overdue"])
        self.assertGreater(metric["variance_hours"], 5.0)
        self.assertIn("red", metric["badge_class"])

    def test_04_completed_on_time_evaluation(self):
        """Invariant 4: Completed stage within SLA window resolves to COMPLETED_ON_TIME."""
        started = add_to_date(now_datetime(), hours=-20)
        completed = add_to_date(now_datetime(), hours=-2)  # TAT = 18h <= 24h
        metric = SolarSLACalculator.evaluate_stage_metric(
            stage_code="S02_SURVEY",
            started_on=str(started),
            completed_on=str(completed),
            capacity_kw=5.0
        )
        self.assertEqual(metric["state"], "COMPLETED_ON_TIME")
        self.assertIn("emerald", metric["badge_class"])
        self.assertEqual(metric["progress_percent"], 100.0)

    def test_05_completed_delayed_evaluation(self):
        """Invariant 5: Completed stage exceeding SLA window resolves to COMPLETED_DELAYED."""
        started = add_to_date(now_datetime(), hours=-40)
        completed = add_to_date(now_datetime(), hours=-2)  # TAT = 38h > 24h
        metric = SolarSLACalculator.evaluate_stage_metric(
            stage_code="S02_SURVEY",
            started_on=str(started),
            completed_on=str(completed),
            capacity_kw=5.0
        )
        self.assertEqual(metric["state"], "COMPLETED_DELAYED")
        self.assertIn("amber", metric["badge_class"])
        self.assertGreater(metric["variance_hours"], 13.0)

    def test_06_admin_waiver_converts_delayed_to_on_time(self):
        """Invariant 6: Administrative waiver overrides delay penalty and flips state to COMPLETED_ON_TIME."""
        started = add_to_date(now_datetime(), hours=-40)
        completed = add_to_date(now_datetime(), hours=-2)
        metric = SolarSLACalculator.evaluate_stage_metric(
            stage_code="S02_SURVEY",
            started_on=str(started),
            completed_on=str(completed),
            capacity_kw=5.0,
            has_admin_waiver=True
        )
        self.assertEqual(metric["state"], "COMPLETED_ON_TIME")
        self.assertIn("emerald", metric["badge_class"])

    def test_07_capacity_tiered_sla_duration_resolution(self):
        """Invariant 7: Capacity tiers correctly scale SLA durations for Design and WBS Installation."""
        # Residential <= 10 kWp
        res_design_hours = SolarSLACalculator.get_stage_sla_hours("S03_DESIGN", capacity_kw=5.0)
        self.assertEqual(res_design_hours, 24.0)

        # C&I > 10 kWp
        ci_design_hours = SolarSLACalculator.get_stage_sla_hours("S03_DESIGN", capacity_kw=50.0)
        self.assertEqual(ci_design_hours, 48.0)

        # Installation: 3.0 days per 10 kWp -> 20 kWp = 6.0 days = 144.0 hours
        install_hours_20kw = SolarSLACalculator.get_stage_sla_hours("S08_INSTALLATION", capacity_kw=20.0)
        self.assertEqual(install_hours_20kw, 144.0)

    def test_08_mandatory_delay_log_recording_and_validation(self):
        """Invariant 8: Mandatory delay logging validates character length and records audit row."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "name": "TEST-LEAD-TB07-001",
            "lead_name": "Test SLA Lead",
            "mobile_no": "9876543210",
            "custom_current_stage_code": "S02_SURVEY",
            "custom_stage_state": "ONGOING_OVERDUE",
            "custom_stage_started_on": add_to_date(now_datetime(), hours=-30)
        }).insert(ignore_permissions=True)

        # 1. Progression blocked without log
        with self.assertRaises(frappe.ValidationError):
            StageGateValidator.validate_delay_logging_before_progression(lead, "S03_DESIGN")

        # 2. Recording delay reason with < 20 chars throws ValidationError
        with self.assertRaises(frappe.ValidationError):
            log_stage_delay_reason(
                stepper_type="lead",
                doc_name=lead.name,
                stage_code="S02_SURVEY",
                delay_category="Weather Emergency",
                delay_remarks="Too short"
            )

        # 3. Valid recording succeeds
        res = log_stage_delay_reason(
            stepper_type="lead",
            doc_name=lead.name,
            stage_code="S02_SURVEY",
            delay_category="Weather Emergency",
            delay_remarks="Severe unseasonal rainstorm prevented rooftop safety access for 24 hours."
        )
        self.assertEqual(res["status"], "success")

        # 4. Reload and assert row present
        lead.reload()
        self.assertEqual(len(lead.custom_stage_delay_log), 1)
        self.assertEqual(lead.custom_stage_delay_log[0].delay_category, "Weather Emergency")

        # 5. Progression now unlocked
        StageGateValidator.validate_delay_logging_before_progression(lead, "S03_DESIGN")

    def test_09_terminal_gate_lead_and_project_completion(self):
        """Invariant 9: Stage 10A completes tabLead and Stage 10B completes tabProject."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "name": "TEST-LEAD-TB07-002",
            "lead_name": "Terminal Test Lead",
            "mobile_no": "9876543211",
            "custom_current_stage_code": "S10A_EARLY_LIAISON",
            "status": "Lead"
        }).insert(ignore_permissions=True)

        # Execute Stage 10A terminal handoff
        StageGateValidator.execute_terminal_lead_completion(lead, discom_application_no="DISCOM-GUJ-998822")
        lead.reload()
        self.assertEqual(lead.custom_lead_progress_status, "Completed")
        self.assertEqual(lead.status, "Converted")
        self.assertIsNotNone(lead.custom_lead_completed_on)

        # Project execution terminal handoff
        project = frappe.get_doc({
            "doctype": "Project",
            "name": "TEST-PROJ-TB07-001",
            "project_name": "Terminal Test Project",
            "custom_current_stage_code": "S10B_GRID_SYNC",
            "custom_is_completed_flag": 0,
            "status": "Open"
        }).insert(ignore_permissions=True)

        StageGateValidator.execute_terminal_project_completion(
            project,
            cod_certificate_ref="COD-SADBHAV-2026-001",
            certifier_user="Administrator"
        )
        project.reload()
        self.assertEqual(project.custom_is_completed_flag, 1)
        self.assertEqual(project.status, "Completed")
        self.assertEqual(project.custom_completion_certified_by, "Administrator")
        self.assertIsNotNone(project.custom_completion_certified_on)

    def test_10_role_security_waiver_authorization_lockout(self):
        """Invariant 10: Non-Admin / non-Director users are blocked from approving SLA waivers."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "name": "TEST-LEAD-TB07-001",
            "lead_name": "Waiver Lockout Lead",
            "mobile_no": "9876543210"
        }).insert(ignore_permissions=True)

        lead.append("custom_stage_delay_log", {
            "stage_code": "S02_SURVEY",
            "stage_name": "Technical Site Survey",
            "delay_category": "Customer Delay",
            "delay_remarks": "Customer was out of station during scheduled audit appointment.",
            "logged_by": "Administrator",
            "logged_on": now_datetime(),
            "admin_waiver_approved": 0
        })
        lead.save(ignore_permissions=True)

        # Mock non-admin user
        frappe.set_user("test@example.com")
        if not frappe.db.exists("User", "test@example.com"):
            frappe.get_doc({"doctype": "User", "email": "test@example.com", "first_name": "Test Operator"}).insert(ignore_permissions=True)

        try:
            with self.assertRaises(frappe.PermissionError):
                approve_admin_stage_waiver(
                    stepper_type="lead",
                    doc_name=lead.name,
                    delay_log_idx=1,
                    waiver_remarks="Executive waiver granted due to verified customer travel emergency."
                )
        finally:
            frappe.set_user("Administrator")
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 Automated Bench Test Execution

```bash
# Execute the Stage 07 Tracer Bullet integration test suite on Frappe bench
cd /home/cbdits_05aug/frappe-bench-v16
bench --site [site-name] run-tests --module solar_module.tests.test_stage_07_tracer_bullet
```

### 7.2 Verification Checklist & Acceptance Gates

| Gate # | Verification Invariant                            | Expected Result                                                           | Status |
| :----: | :------------------------------------------------ | :------------------------------------------------------------------------ | :----: |
| **01** | Unstarted Stage Evaluation                        | Resolves to `IDLE` with slate badges (`progress_percent = 0.0`).          |   ✔    |
| **02** | Healthy Ongoing Stage Evaluation                  | Resolves to `ONGOING_HEALTHY` with blue tokens (`is_overdue = False`).     |   ✔    |
| **03** | Overdue Ongoing Stage Evaluation                  | Resolves to `ONGOING_OVERDUE` with red pulsing tokens (`is_overdue = True`).|   ✔    |
| **04** | On-Time Stage Completion                          | Resolves to `COMPLETED_ON_TIME` with emerald checkmark badge.            |   ✔    |
| **05** | Delayed Stage Completion                          | Resolves to `COMPLETED_DELAYED` with amber warning badge.                 |   ✔    |
| **06** | Executive SLA Waiver Authority                    | Flips `COMPLETED_DELAYED` to `COMPLETED_ON_TIME`; logs waiver actor.      |   ✔    |
| **07** | Capacity-Tiered Dynamic SLA                       | Res ($\le 10$ kWp) = 24h; C&I ($> 10$ kWp) = 48h; WBS Install = 3d/10kWp.  |   ✔    |
| **08** | Mandatory Delay Logging Validation                | Hard blocks stage progression; rejects remarks $< 20$ characters.         |   ✔    |
| **09** | Terminal Stage Gates & Completion                 | S10A completes `tabLead`; S10B completes `tabProject` with COD anchor.    |   ✔    |
| **10** | Non-Admin Waiver Lockout Gate                     | Throws `frappe.PermissionError` if actor lacks `Admin` or `Director`.     |   ✔    |
| **11** | Zero-Commit Test Transaction Rule                 | Atomic rollback in test tearDown; leaves zero database residual records.   |   ✔    |

---

## 8. Summary of Architectural Achievements

The **Stage 07 Dual Progress Bar Lifecycle & SLA Engine Tracer Bullet** delivers an end-to-end thin slice that connects:
1. **Database Schema:** 3NF extensions across `tabLead` and `tabProject`, child `tabSolar Stage Delay Log`, and single `tabSolar SLA Settings`.
2. **Domain Architecture:** Decoupled SOLID Python calculators (`SolarSLACalculator`, `LeadStepperEngine`, `ProjectStepperEngine`, `StageGateValidator`).
3. **RPC Gateway:** Secure, typed endpoints (`get_lifecycle_stepper_state`, `log_stage_delay_reason`, `approve_admin_stage_waiver`) and Redis worker daemon.
4. **User Experience:** Responsive 5-state Desk and Vue 3 progress bar steppers with interactive Slide-Over inspector drawers.
5. **Quality Assurance:** 10 comprehensive automated integration test cases operating under the zero-commit rule.

# ADR-007: Dual-Progress-Bar Lifecycle Architecture, State-Machine SLA Visualization & Role-Gated Interactivity Engine

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), managing complex solar installations requires coordination across two fundamentally distinct operational lifecycles:

1. **The Commercial & Pre-Execution Lifecycle (Governed in `Lead`):**
   Originates from customer marketing inquiry and spans technical site survey, PV engineering design, dynamic BOM calculation, commercial proposal, subsidy clearance, advance payment verification, Sales Order baseline lock, and post-order early statutory DISCOM document collection (Phase 1 Liaisoning). Once Stage 10A early statutory filings are completed, the commercial lead has completed its operational destiny and must be marked **`Completed`** (or `Converted`).

2. **The Physical Delivery, Installation & Grid Synchronization Lifecycle (Governed in `Project`):**
   Spawns automatically upon submission of the ERPNext `Sales Order` (anchored to Stage 05 advance clearance). It encompasses material requisition and serialized warehouse dispatch (Stage 07), multi-zone civil/electrical installation and mobile Daily Progress Reports (Stage 08), surplus site material reconciliation and return (Stage 09), and post-installation statutory inspection, CEIG clearance, bi-directional net-meter installation, and grid synchronization (Stage 10B). Completing Stage 10B formally marks the `Project` as **`Completed`** and transitions the installation to Stage 11 Operation & Maintenance (O&M).

### Operational Problems Identified

Under legacy workflows and standard ERP implementations:

- **Disjointed Progress Visibility:** Sales executives had zero visibility into whether site execution commenced or why DISCOM filings stalled; site engineers had no visibility into commercial milestones or customer commitments.
- **Ambiguous Stage Statuses:** Stakeholders could not differentiate between a stage that was merely waiting for preceding tasks (_Idle_), actively underway within schedule (_Ongoing_), behind schedule (_Overdue_), completed on time (_Completed_), or completed after significant delay (_Completed with Delay_).
- **Missing SLA Accountability:** Turnaround times (TAT) were untracked. Breaches went unnoticed until customer complaints or statutory deadlines expired.
- **Uncontrolled or Disconnected Actions:** Operators either lacked interactive shortcuts to execute their assigned tasks or possessed unmanaged permissions to skip critical verification gates.

---

## Decision

We establish an authoritative, dual-lifecycle visual stepper and SLA engine implemented across both the Vue 3 SPA (`/solar`) and Frappe Desk forms (`Lead`, `Project`):

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             THE DUAL PROGRESS BAR LIFECYCLE ENGINE                               │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  [PROGRESS BAR 1: LEAD LIFECYCLE STEPPER]                                                        │
│  Scope: tabLead (Lead Ingestion ──▶ Early Liaisoning Phase 1 Handoff)                            │
│                                                                                                  │
│   [01. Lead] ──▶ [02. Survey] ──▶ [03. Design] ──▶ [04. Proposal] ──▶ [05. Advance] ──▶          │
│                                                           │                                      │
│                                                           ▼                                      │
│                                              [06. Sales Order] ──▶ [10A. Early Liaisoning]       │
│                                                                            │                     │
│                                                                            ▼                     │
│                                                                 ★ MARK LEAD COMPLETED ★          │
│                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  [PROGRESS BAR 2: PROJECT LIFECYCLE STEPPER]                                                     │
│  Scope: tabProject (Spawned by Sales Order Submit ──▶ Grid Sync & COD Handover)                  │
│                                                                                                  │
│   [05G. Advance Gate] ──▶ [06. SO Baseline] ──▶ [07. Dispatch] ──▶ [08. Installation & DPR] ──▶  │
│                                                           │                                      │
│                                                           ▼                                      │
│                                    [09. Material Return] ──▶ [10B. Grid Sync & Net Meter]        │
│                                                                            │                     │
│                                                                            ▼                     │
│                                                                ★ MARK PROJECT COMPLETED ★        │
│                                                                            │                     │
│                                                                            ▼                     │
│                                                                 [11. O&M Asset Register]         │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Dual Independent Stepper Topology

#### A. Progress Bar 1: Commercial Inception Stepper (`LeadProgressBar`)

- **Parent DocType:** `tabLead` (extended via `custom_lead_progress_status`, `custom_lead_stage_state`).
- **Sequential Stages:**
  1. `Stage 01: Lead Qualification` (`tabLead`) [Default SLA: 2 Hours]
  2. `Stage 02: Technical Site Survey` (`tabSite Survey`) [Default SLA: 24 Hours]
  3. `Stage 03: PV Engineering Design & Dynamic BOM` (`tabSurvey Engineering Design`) [Default SLA: 48 Hours]
  4. `Stage 04: Commercial Proposal & Subsidy` (`tabQuotation`) [Default SLA: 24 Hours]
  5. `Stage 05: Advance Payment & Customer Inception` (`tabCustomer`, `tabPayment Entry`) [Default SLA: 48 Hours]
  6. `Stage 06: Sales Order Baseline Lock` (`tabSales Order`) [Default SLA: 24 Hours]
  7. `Stage 10A: Statutory Liaisoning Phase 1 (DISCOM Filing)` (`tabLiaisoning And Synchronization`) [Default SLA: 72 Hours]
- **Completion Trigger:** When Stage 10A transitions to `Application Submitted` / `NOC Issued`, `LeadValidationService.mark_lead_completed()` sets `lead.status = 'Completed'`, freezing the lead while maintaining bidirectional operational drilldown.

#### B. Progress Bar 2: Execution & Handover Stepper (`ProjectProgressBar`)

- **Parent DocType:** `tabProject` (spawned automatically by `ProjectSpawnerService` on `Sales Order` submission).
- **Sequential Stages:**
  1. `Stage 05G: Advance Clearance Verification Gate` (`tabSales Order.custom_advance_verified`) [Financial Baseline Gate]
  2. `Stage 06: Sales Order Baseline & WBS Inception` (`tabSales Order`, `tabProject`) [Default SLA: 24 Hours]
  3. `Stage 07: Material Dispatch & Serialized Delivery Note` (`tabDelivery Note`) [Default SLA: 48 Hours]
  4. `Stage 08: Multi-Zone Installation Execution & DPR` (`tabTask`, `tabDPR`) [Default SLA: Dynamic based on kW capacity]
  5. `Stage 09: Site Material Return & Surplus Reconciliation` (`tabStock Entry`) [Default SLA: 48 Hours post-installation]
  6. `Stage 10B: Grid Synchronization, Inspection & Metering` (`tabLiaisoning And Synchronization`) [Strict Statutory 10-Day SLA]
- **Completion Trigger:** Upon completion of Stage 10B (CEIG inspection passed, bi-directional net-meter installed, and grid synchronization certified), `ProjectClosureService.mark_project_completed()` transitions `tabProject.status = 'Completed'`, calculates project-level gross margin variance, and creates the digital Solar Asset Register in Stage 11.

---

### 2. Standardized 5-State Visual Ontology & Color Encoding

Every stage node in both progress bars adheres to a deterministic 5-state color and token architecture compliant with WCAG 2.1 AA accessibility standards:

| State Code              | Semantic Stage State                      | Visual Indicator & Color Palette | Tailwind / CSS Design Tokens                                                                                      | Micro-Badge & Icon                                       | Operational Meaning                                                        |
| :---------------------- | :---------------------------------------- | :------------------------------- | :---------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------- | :------------------------------------------------------------------------- |
| **`IDLE`**              | **Not Started / Idle**                    | Neutral Cool Slate (Muted gray)  | `bg-slate-100 text-slate-500 border-slate-300 dark:bg-slate-800 dark:text-slate-400`                              | Dotted ring; Clock outline                               | Prerequisites pending; stage queued but inactive.                          |
| **`ONGOING_HEALTHY`**   | **Started / Ongoing (Within SLA)**        | Active Solar Blue / Cerulean     | `bg-blue-50 text-blue-700 border-blue-500 ring-2 ring-blue-300 dark:bg-blue-950/50 dark:text-blue-300`            | Solid active ring; Spinner/Play; Elapsed SLA timer       | Active work in progress; elapsed duration $\le$ target SLA.                |
| **`ONGOING_OVERDUE`**   | **Ongoing but Overdue (SLA Breached)**    | High-Alert Crimson Red / Orange  | `bg-red-50 text-red-700 border-red-500 ring-4 ring-red-400/50 animate-pulse dark:bg-red-950/60 dark:text-red-300` | Pulsing red ring; Warning Triangle; Negative SLA counter | Active work; elapsed duration $>$ target SLA. Escalation alerts triggered. |
| **`COMPLETED_ON_TIME`** | **Completed (Within SLA / On Time)**      | Success Emerald Green            | `bg-emerald-50 text-emerald-700 border-emerald-500 dark:bg-emerald-950/50 dark:text-emerald-300`                  | Solid Emerald fill; Checkmark icon                       | Finished within allotted SLA; verified by stage gate.                      |
| **`COMPLETED_DELAYED`** | **Completed but in Delay (Breached SLA)** | Warning Warm Amber / Ochre       | `bg-amber-50 text-amber-800 border-amber-600 dark:bg-amber-950/50 dark:text-amber-300`                            | Amber fill with warning badge; Checkmark + Exclamation   | Finished, but actual TAT exceeded SLA. Delay log attached.                 |

---

### 3. Stage Metric Engine: Turnaround Time (TAT) vs. SLA Tracking

Every stage node computes and renders 5 synchronized metrics:

1. **Target SLA Duration ($T_{\text{SLA}}$):** Dynamically retrieved from `tabSolar SLA Settings` by document type and project capacity tier.
2. **Actual Turnaround Time ($T_{\text{TAT}}$):**
   - For active stages: $T_{\text{TAT}} = \text{now()} - T_{\text{start}}$.
   - For completed stages: $T_{\text{TAT}} = T_{\text{end}} - T_{\text{start}}$.
3. **Variance ($\Delta T$):**
   $$\Delta T = T_{\text{TAT}} - T_{\text{SLA}}$$
   - If $\Delta T \le 0$: On-time performance ($|\Delta T|$ hours ahead of schedule).
   - If $\Delta T > 0$: Delayed performance ($+\Delta T$ hours breach).
4. **SLA Consumption Gauge (%):** Visual micro progress bar ($0\%$ to $100\%$ width; transitions to red gradient upon $>100\%$).
5. **Mandatory Delay Reason Attribution:** When a stage enters `ONGOING_OVERDUE` or finishes as `COMPLETED_DELAYED`, the system mandates submission of a structured child record (`tabStage Delay Log`) with pre-approved reason categories (`Customer Delay`, `Statutory Delay`, `Material Shortage`, `Weather Obstacle`, `Technical Redesign`).

---

### 4. Interactive Role-Based Access Control (RBAC) & Flyout Drawer

The progress bar is not a static graphic; it is a live interactive workflow controller:

1. **Node Click Interaction:** Clicking any stage node triggers an interactive **Slide-Over Drawer (Inspector Panel)**:
   - Displays stage inputs, outputs, deliverables (PDFs, CAD drawings, photo galleries, NOCs).
   - Shows actor attribution (e.g. `Assigned To: Rahul Sharma (Survey Engineer)`).
   - Displays real-time timeline logs and historical delay remarks.
   - Provides deep links to underlying Frappe Desk documents (`/app/site-survey/<id>`, `/app/sales-order/<id>`) guarded by native Frappe role permissions.

2. **Role Action Buttons:**
   Primary action buttons inside the drawer dynamically render strictly according to the session user's role (with Managerial Authority Inheritance per ADR-000):
   - **`Sales Representative` / `Sales Manager`:** "Schedule Survey", "Mark Disqualified", "Submit Sales Order".
   - **`Survey Engineer` / `Survey Manager`:** "Launch Mobile Audit", "Sync Offline Data".
   - **`Design Engineer` / `Design Manager`:** "Launch PV Workbench", "Freeze BOM Baseline".
   - **`CRM Representative` / `CRM Manager`:** "Generate Proposal", "Submit Proposal for Approval".
   - **`Accounts Assistant` / `Accounts Manager`:** "Verify Advance Payment", "Clear Financial Gate".
   - **`Store Assistant` / `Store Manager`:** "Allocate Stock", "Generate Delivery Note".
   - **`Site Supervisor` / `Project Engineer` / `Project Manager`:** "Log DPR", "Complete Zone Task".
   - **`Liaisoning Representative` / `Liaisoning Manager`:** "Upload DISCOM NOC", "Record Net-Meter Energization".
   - **`Admin` (Project Supreme Command):** "Approve Delay Waiver", "Override Stage Gate", "Configure SLA Duration", "Amend / Cancel / Cascading Purge".

---

## Consequences

### Positive

- **Complete End-to-End Traceability:** Commercial teams track engineering and statutory progress; technical teams track commercial and dispatch baselines.
- **Instant Bottleneck Identification:** Color-coded stages (`ONGOING_OVERDUE` and `COMPLETED_DELAYED`) instantly highlight operational friction points without manual reporting.
- **Enforced Governance:** Stage gates prevent skipped milestones (e.g. Sales Order cannot be submitted without Advance Clearance; Project cannot close without Grid Sync).
- **Audit-Ready Compliance:** Every stage transition, TAT variance, and delay reason is permanently stored in immutable child tables.

### Negative / Trade-Offs

- Requires background scheduled worker (`every_hour` / `short` RQ queue) to evaluate real-time SLA expirations and update stage states.
- Increases client-side bundle size slightly due to interactive Vue 3 drawer components and Lucide icons.

---

## References

- [`step_plans/README.md`](../../step_plans/README.md)
- [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md)
- [`planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md`](../../planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md)
- [`planning_ref_docs/10_UI_UX_SPECIFICATION.md`](../../planning_ref_docs/10_UI_UX_SPECIFICATION.md)

# ADR-010: Dual-Timing Statutory Liaisoning, Regulatory Inspection, Net Metering & Grid Synchronization Architecture

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), Stage 10 (**Dual-Timing Statutory Liaisoning, Regulatory Inspection, Net Metering & Grid Synchronization**) constitutes the legal, regulatory, and commercial closeout anchor of the entire Solar EPC project lifecycle. It bridges upstream physical engineering (Stage 08 Installation Execution and Stage 09 Material Return Reconciliation) with long-term plant operations (Stage 11 Lifecycle O&M & IoT Telemetry).

In conventional solar EPC operations, statutory liaisoning and utility interconnection suffer from severe structural blind spots, communication silos, and regulatory delays that expose solar contractors to massive financial and operational risks:

1. **The Dual-Timing Lifecycle Disconnect:**  
   Statutory solar compliance does not happen in a single linear step. It fundamentally spans two temporally separated phases:
   - **Phase 1 (Pre-Construction / Post-Sales Order):** Early utility application filing, consumer KYC collection, property tax verification, sanctioned load assessment, and grid feasibility approval from the local distribution company (DISCOM) or national portal (PM Surya Ghar).
   - **Phase 2 (Post-Installation / Pre-Commissioning):** Statutory safety inspection by the Chief Electrical Inspector to Government (CEIG), Joint Meter Inspection (JMI), bi-directional net-meter procurement and calibration testing, grid energization, and Commercial Operation Date (COD) certification.  
     In legacy systems, liaisoning is treated as an afterthought initiated only after physical installation completes. Waiting until construction ends to apply for utility approvals creates months of administrative idling, during which customer roofs sit dormant with installed equipment.

2. **Dormant Post-Installation Windows & Absence of Statutory SLA Countdown:**  
   Once physical installation is finished and pre-commissioning Megger/voltage tests are signed off, projects historically hit an unmonitored administrative void. Frontline EPC engineers celebrate physical installation completion, while statutory files languish on government desks. Because legacy ERPs have no dedicated statutory turnaround time (TAT) engine, the statutory window—mandated by state electricity regulatory commissions (SERCs) and the national solar mission to be completed within 10 to 15 days—stretches to 60–120 days.

3. **Massive Financial Exposure & Subsidy Forfeiture:**  
   For residential rooftop installations under central subsidy schemes (PM Surya Ghar Muft Bijli Yojana), government financial assistance (CFA) is released only after successful JMI report upload and net-meter commissioning on the National Portal. Uncontrolled liaisoning delays trigger subsidy application expirations, force customers to pay undiscounted capital outlays, trigger bitter customer disputes, and severely impair customer NPS. For Commercial & Industrial (C&I) clients, delayed COD triggers liquidated damages (LDs) and leaves 10%–20% of EPC contract value trapped in uncollectible retention milestones.

4. **Lack of an Immutable Project Completion Anchor:**  
   In traditional project management tools, an EPC project's status is manually toggled to "Completed" by project managers whenever convenient, often before meters are installed or before statutory safety certificates are secured. This decouples enterprise accounting and customer handover from regulatory truth. The enterprise requires an immutable, system-enforced verification gate: **a Solar EPC Project cannot be legally or commercially marked "Completed" until grid synchronization is executed, bi-directional meter readings are logged, and the official COD certificate is issued.**

---

## Decision

We establish an authoritative, comprehensive architectural standard for Stage 10 Statutory Liaisoning and Grid Synchronization within `solar_module`, introducing a standalone, submittable DocType `tabLiaisoning And Synchronization` (`is_submittable = 1`), supported by an automated dual-timing state machine, an enforced 10-day statutory SLA countdown engine, hard regulatory verification gates, and an atomic Project completion and O&M handoff hook:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│              STAGE 10: DUAL-TIMING STATUTORY LIAISONING & GRID SYNC ARCHITECTURE                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Stage 06: Sales Order Commercial Baseline Frozen]                                             │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Phase 1 Liaisoning Initialized (Post-SO Early Compliance)]                                    │
│   • Auto-spawned by LiaisoningInceptionService upon Sales Order submission                        │
│   • Captures Consumer KYC, Property Documents, Electricity Bill, Sanctioned Load                 │
│   • Tracks DISCOM Application No & PM Surya Ghar National Portal Application ID                  │
│   • Gate 1: Grid Connectivity Feasibility Approval & NOC Secured                                 │
│   • Submitting DISCOM Application officially completes Lead Lifecycle Stepper (Progress Bar 1)  │
│           │                                                                                      │
│           │ (Parallel: Stage 07 Dispatch ──▶ Stage 08 Installation ──▶ Stage 09 Return)         │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Stage 08: Pre-Commissioning Electrical Testing (IEC 62446-1) Verified & Signed Off]          │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Phase 2 Activation: Post-Installation Grid Sync & Statutory Countdown Initiated]              │
│   • Sets phase_2_status = "Triggered Post-Installation"                                          │
│   • Starts Statutory 10-Day SLA Countdown Timer (Configurable in Solar SLA Settings)             │
│   • Assigns Liaisoning Officer & Field Commissioning Specialist                                  │
│           │                                                                                      │
│           ├────────────────────────────────┬─────────────────────────────────────────────┤
│           ▼                                ▼                                             ▼
│   [Gate 2: CEIG Safety Clearance]   [Gate 3: Joint Meter Inspection]              [Gate 4: Grid Sync & Anti-Islanding]
│   • High Voltage/Capacity (>10kWp)  • DISCOM Inspector + EPC Joint Audit          • Bi-directional Net-Meter Installed
│   • SLD & Megger/Earth Test logs    • Meter Serial No, CT/PT Ratio logged         • Initial Import/Export kWh recorded
│   • Official Charging Permission    • Signed JMI Inspection Report uploaded       • Anti-islanding disconnect verified
│           │                                │                                             │
│           └────────────────────────────────┴─────────────────────────────────────────────┘
│                                            │
│                                            ▼
│   [Gate 5: Master Project Completion & Commercial Operation Date (COD) Sign-Off]                 │
│   • Submitting Liaisoning And Synchronization DocType (docstatus = 1)                            │
│           │                                                                                      │
│           ├──────────────────────────────────────────────────────────────────────────────┤
│           ▼                                                                              ▼
│   [Atomic Project Completion Engine]                              [Stage 11 Downstream Handover]
│   • Sets tabProject.status = "Completed"                          • Spawns tabSolar Asset Register
│   • Sets tabProject.custom_is_completed_flag = 1                  • Maps serialized modules & inverters
│   • Freezes COD Date & Grid Sync Date                             • Sets 5-year OEM warranty countdowns
│   • Closes all remaining open WBS tasks                           • Generates biannual preventative AMCs
│   • Unlocks final milestone invoice in Accounts                   • Broadcasts WhatsApp/Email completion alerts
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Dual-Timing Entity Architecture (`tabLiaisoning And Synchronization`)

Rather than fragmenting compliance across disparate tasks or disconnected forms, Stage 10 is governed by a unified submittable DocType:

- **DocType Entity:** `Liaisoning And Synchronization` (`tabLiaisoning And Synchronization`), submittable (`is_submittable = 1`), autoname format: `LIA-.YYYY.-.#####`.
- **Temporal Phase Segregation:**
  - **Phase 1 (Pre-Construction Compliance):** Fields and child records for consumer registration, electricity provider (DISCOM), division/subdivision, sanctioned load ($kW$), consumer KYC verification, site plan submission, and DISCOM grid feasibility approval letter.
  - **Phase 2 (Post-Construction Statutory Synchronization):** Fields and child records for statutory inspection scheduling, CEIG safety approval, Joint Meter Inspection (JMI) protocol, bi-directional net-meter calibration and serial tracking, anti-islanding test sign-off, grid energization timestamp, and COD certification.
- **Relational Integrity:** Foreign key links to `tabProject`, `tabSales Order`, `tabCustomer`, and `tabLead`.

### 2. The Statutory 10-Day SLA & TAT Countdown Engine

To prevent post-installation administrative dormancy:

- **Trigger:** Automatic activation upon Stage 08 Pre-Commissioning Electrical Testing verification (`IEC 62446-1` sign-off).
- **Baseline Duration:** Standard default of **10 Days** (customizable by `Admin` / `Director` in `tabSolar SLA Settings` based on state regulatory rules).
- **Dynamic Clock:** Real-time countdown tracking hours and business days remaining until `statutory_deadline`.
- **Live Visual Stepper:** Renders dynamic radial countdown on `/solar/liaisoning/:id` changing colors from **Healthy Green** ($> 4$ days) to **Warning Amber** ($2 - 4$ days) to **Critical Red** ($< 2$ days / Overdue).
- **Mandatory Delay Logging:** If the 10-day deadline is breached, the document enters `Phase 2: Overdue (SLA Breached)`, locking normal closure until the operator submits an auditable entry into `tabSolar Stage Delay Log` with root-cause categorization (`DISCOM_METER_SHORTAGE`, `CEIG_SCHEDULING_DELAY`, `GRID_OUTAGE`, `CUSTOMER_UNAVAILABLE`, `STATUTORY_FEE_DELAY`) and secures `Admin` approval.

### 3. Enforced Regulatory Verification Stage-Gates

No document in Stage 10 can advance or submit without meeting deterministic verification criteria:

- **Gate 1 (Phase 1 Feasibility & NOC Gate):** Consumer KYC verified, property tax document uploaded, latest electricity bill verified, DISCOM application number entered, and official Feasibility Approval / Grid NOC document attached.
- **Gate 2 (Phase 2 Post-Installation Gate):** Linked `tabProject` must have completed Stage 08 physical milestones, pre-commissioning Megger test ($\ge 1.0\text{ M}\Omega$), and earth pit test ($\le 5.0\ \Omega$ structure, $\le 1.0\ \Omega$ inverter) verified.
- **Gate 3 (CEIG Safety & Charging Permission Gate):** For systems exceeding the state safety threshold (e.g., $> 10\text{ kWp}$ or $> 50\text{ kWp}$ depending on state regulations), CEIG inspection application, government treasury fee receipt, inspection report, and statutory Charging Permission letter must be verified. For exempt residential capacities, statutory exemption affidavit is validated.
- **Gate 4 (Joint Meter Inspection & Net-Meter Gate):** Official JMI protocol report signed by DISCOM testing engineer and EPC liaisoning officer, bi-directional meter serial number, meter testing lab seal certificate, CT/PT ratio (for LT/HT installations), and initial import/export readings ($kWh$) recorded.
- **Gate 5 (Grid Synchronization, COD & Project Completion Anchor Gate):** Anti-islanding protection trip test ($< 2.0\text{ s}$) verified, plant energization certificate attached, Commercial Operation Date (COD) entered. Submitting this record permanently locks the dossier and triggers the atomic Project completion engine.

### 4. Atomic Project Closeout & Downstream O&M Spawning Engine

Upon formal submission (`docstatus = 1`) of `tabLiaisoning And Synchronization`:

1. **Atomic Transaction Lock:** The controller updates the linked `tabProject`:
   - `status = "Completed"`
   - `custom_is_completed_flag = 1`
   - `custom_completion_certified_by = frappe.session.user`
   - `custom_completion_certified_on = frappe.utils.now_datetime()`
   - `custom_cod_date = self.grid_synchronization_date`
2. **WBS Task Reconciliation:** Closes any lingering non-critical tasks in `tabTask` with status `"Completed"`.
3. **Stage 11 Downstream Spawning:** Programmatically instantiates `tabSolar Asset Register` mapping all serialized PV modules and inverters from Delivery Notes, linking the bi-directional net meter serial, establishing the COD baseline, and initializing the 5-year preventative maintenance (AMC) schedule.
4. **Commercial Milestone Release:** Notifies ERPNext Accounts department that the "Commissioning / Net-Metering" milestone condition is met, unlocking final retention billing.
5. **Stakeholder Broadcast:** Dispatches real-time automated notifications (WhatsApp, Email, Desk Alert) to the Customer, Sales Representative, Project Engineer, Accounts Lead, and Executive Leadership.

---

## Alternatives Considered

### Alternative 1: Managing Liaisoning as Generic `tabTask` Items inside `tabProject`

- **Rejected:** Treating statutory approvals as generic tasks inside ERPNext `tabProject` completely fails to accommodate the dual-timing nature of solar compliance (pre-SO vs post-install), provides no dedicated data structure for meter serials or CEIG records, lacks legal submittable immutability, and cannot enforce the 10-day statutory countdown timer.

### Alternative 2: Maintaining Two Separate DocTypes (`Phase 1 Liaisoning` and `Phase 2 Grid Sync`)

- **Rejected:** Splitting compliance into two separate DocTypes fractures the audit trail, creates duplicate consumer master fields, and complicates reporting. A single unified DocType with clear phase-based state machines maintains complete end-to-end statutory traceability while honoring temporal boundaries.

### Alternative 3: Manual Project Completion by Project Managers

- **Rejected:** Allowing project managers to manually mark a project "Completed" in ERPNext creates severe compliance and accounting discrepancies. Linking project completion strictly to statutory grid synchronization and COD certificate upload guarantees 100% data integrity and regulatory truth.

---

## Consequences

### Positive Consequences

- **Zero Post-Installation Dormancy:** The automated 10-day SLA countdown timer forces immediate statutory follow-through the moment installation pre-commissioning is completed.
- **100% Subsidy Claim Protection:** Real-time capture of JMI and net-meter parameters ensures same-day filing on the PM Surya Ghar National Portal, eliminating subsidy forfeiture risks.
- **Unbreakable Project Completion Truth:** Anchoring `tabProject.status = "Completed"` to statutory COD guarantees that no project is marked complete without legal grid energization.
- **Seamless O&M Inception:** Instant programmatic spawning of `tabSolar Asset Register` upon grid sync ensures smooth handover into Stage 11 maintenance without data re-entry.
- **Audit-Ready Regulatory Archive:** Full statutory dossier (CEIG permission, JMI report, meter test certificate, grid connectivity NOC) is permanently preserved in an immutable, submittable record.

### Negative / Trade-Off Consequences

- **State DISCOM Process Variability:** Different state electricity distribution companies (e.g., BESCOM, MSEDCL, TANGEDCO, UGVCL, Tata Power) have varying documentation checklists and inspection workflows.
  - _Mitigation:_ `tabSolar Statutory Document Checklist` is designed as a dynamic child table where required document types are pre-populated based on state and DISCOM settings, allowing regional adaptability without schema modifications.
- **External Dependency on Government Officials:** Inspections and meter availability depend on government officers outside the direct control of the EPC firm.
  - _Mitigation:_ The statutory SLA engine includes structured delay categorization (`Solar Stage Delay Log`). When DISCOM meter shortages or inspector unavailability cause delays, the system captures verifiable delay records, safeguarding EPC staff performance metrics while notifying leadership of external impediments.

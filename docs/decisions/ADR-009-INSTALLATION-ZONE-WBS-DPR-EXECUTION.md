# ADR-009: Zone-Based Installation Execution, Mobile Daily Progress Reports (DPR), Pre-Commissioning Electrical Testing & Downstream Handoff Architecture

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), Stage 08 (**Zone-Based Installation Execution & Mobile DPR**) represents the core physical engineering phase of the project lifecycle. It bridges upstream logistics (Stage 07 Material Dispatch via Delivery Note and site Proof of Delivery sign-off) with site material reconciliation (Stage 09) and statutory grid synchronization (Stage 10B).

Under conventional solar EPC operational practices, site installation is historically plagued by severe operational blind spots, budget overruns, undocumented delays, and technical quality failures:

1. **Monolithic, Unstructured Task Tracking (No Work Breakdown Structure or Zone Segmentation):**  
   Solar installations—whether 20 kWp multi-roof residential installations, 500 kWp commercial sheds, or ground-mounted arrays—consist of distinct geographic zones (e.g., Roof 1, Roof 2, Carport, Inverter Room). Treating installation as a single monolithic ERP task ("Install Solar Plant") provides zero visibility into real progress across the discrete engineering phases: civil foundation casting, Module Mounting Structure (MMS) erection, PV panel placement and clamping, DC string cabling, AC inverter termination, and earthing protection.

2. **Informal, Unverified Daily Progress Reporting (WhatsApp / Verbal Silos):**  
   Site supervisors routinely communicated daily updates via informal text messages, spreadsheets, or verbal phone calls ("Mounted 50 panels today, raining in afternoon"). These reports lacked tamper-proof audit trails, verifiable labor headcounts, geolocated photographic evidence, or standardized recording of weather delays. When projects suffered 30-day schedule slippages, project management had no auditable records to identify root causes or enforce contractor accountability.

3. **Untracked On-Site Material Consumption & Shrinkage:**  
   Materials delivered to the site via `Delivery Note` were not tracked as they were physically installed day-by-day. Site teams had no mechanism to record daily consumption of critical Bill of Materials (BOM) components (modules, inverters, cables, clamps, connectors). Consequently, material damage, theft, and scrap during installation remained invisible until final commissioning, making Stage 09 (`Material Return to Store`) impossible to reconcile accurately.

4. **Electrical Safety & Pre-Commissioning Quality Neglect:**  
   Crucial quality and safety benchmarks defined by international standards (IEC 62446-1 for PV system documentation, verification, and commissioning) were routinely compromised. String open-circuit voltage ($V_{oc}$), short-circuit current ($I_{sc}$), polarity alignment, insulation resistance (Megger test $\ge 1.0\text{ M}\Omega$), and dedicated earth pit resistance ($\le 5.0\ \Omega$ for structure/DC and $\le 1.0\ \Omega$ for inverters) were either faked on paper or entirely skipped. This led to catastrophic inverter ground faults, cable fires, premature equipment degradation, and statutory rejection during government electrical inspectorate (CEIG) audits.

5. **Missing Downstream Handover Automation:**  
   When physical installation was finished, site supervisors rarely notified storekeepers or liaisoning teams in a timely manner. As a result, surplus materials remained abandoned on site for weeks without returning to inventory, and statutory DISCOM liaisoning (Joint Meter Inspection and bidirectional net-meter installation) sat dormant instead of triggering the mandatory 10-day countdown timer.

---

## Decision

We establish an authoritative, comprehensive architectural standard for Stage 08 Installation Execution within `solar_module`, extending ERPNext's native `tabProject` and `tabTask` models with a multi-zone Work Breakdown Structure (WBS), an offline-first mobile `tabSolar Daily Progress Report` (DPR) engine, a strict pre-commissioning electrical testing gate, and an automated dual downstream spawning engine:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         STAGE 08: INSTALLATION EXECUTION ARCHITECTURE OVERVIEW                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Stage 07: Material Dispatch & Site POD Signed]                                                │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Stage 08 Unlocked on Project Lifecycle Stepper]                                               │
│   • Sets custom_current_lifecycle_stage = "Stage 08: Installation"                               │
│   • Project Engineer & Site Supervisor Assigned                                                  │
│   • Auto-generates Zone WBS Tasks (Civil, MMS, PV Modules, DC/AC Cabling, Earthing, Inverters)   │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Daily Mobile DPR Execution Loop (tabSolar Daily Progress Report - is_submittable = 1)]        │
│   ├────────────────────────────────┬───────────────────────────────┬─────────────────────────────┤
│   │ 1. Labor & Weather Log:        │ 2. Quantitative Progress:     │ 3. Material Consumption:    │
│   │ • Headcount by trade           │ • Physical units completed    │ • Dispatched vs Installed   │
│   │ • Weather conditions & hours   │ • Real-time WBS % sync        │ • Daily site balance tally  │
│   ├────────────────────────────────┼───────────────────────────────┴─────────────────────────────┤
│   │ 4. Site Blockers & Delays:     │ 5. Geotagged Photo Evidence:                                │
│   │ • Categorized delay logging    │ • GPS & timestamp stamped photos for MMS, modules, crimping │
│   └────────────────────────────────┴─────────────────────────────────────────────────────────────┘
│           │ (Submitted daily by Site Supervisor ──▶ Verified by Project Engineer)                │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Installation Physical Completion Reached (100% WBS Tasks Complete)]                           │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Mandatory Pre-Commissioning Electrical Verification Gate (IEC 62446-1)]                       │
│   • String Voltage ($V_{oc}$) within ±5% of design math                                         │
│   • Polarity verified positive to pin 1                                                          │
│   • Insulation Resistance (Megger Test): DC+/PE, DC-/PE, AC/PE ≥ 1.0 MΩ                         │
│   • Earth Pit Resistance: DC/MMS ≤ 5.0 Ω, Inverter/Transformer ≤ 1.0 Ω                           │
│   • Photographic pre-commissioning punch list signed off with 0 open critical defects           │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Quality Sign-Off by Quality & Commissioning Engineer / Project Engineer]                     │
│           │                                                                                      │
│           ├──────────────────────────────────────────────────────────────────────┐               │
│           ▼                                                                      ▼               │
│   [Dual Downstream Handoff Trigger 1: Stage 09]           [Dual Downstream Handoff Trigger 2: 10B]│
│   • Auto-creates Stage 09 Material Reconciliation Task   • Automatically triggers Phase 2 Liaison│
│   • Reconciles Delivery Note vs Installed materials      • Starts statutory 10-day SLA countdown │
│   • Flags surplus items for Stock Entry Return to store  • Prepares CEIG & Joint Meter Inspection│
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Hierarchical Multi-Zone Work Breakdown Structure (WBS)

Rather than maintaining a flat list of generic tasks, Stage 08 partitions each project into structured engineering zones:

- **Zone Entity (`tabSolar Installation Zone`):** Captures individual physical rooftop surfaces, shed bays, or ground plots (e.g., `Zone A - Main Admin Roof (120 kWp)`, `Zone B - Warehouse Shed (180 kWp)`). Defines surface tilt, azimuth, module count, and string layout.
- **Hierarchical Task Templates:** Each zone automatically inherits standard ERPNext `Task` nodes with clear parent-child dependencies:
  1. `Milestone 1: Site Mobilization & Safety Briefing` (Toolbox talks, barricading, lifelines).
  2. `Milestone 2: Civil Works & Foundation Casting` (Piling, ballast pedestals, chemical anchoring, curing).
  3. `Milestone 3: Module Mounting Structure (MMS) Erection` (Strut channels, purlins, torque tightening).
  4. `Milestone 4: Solar PV Module Mounting & Clamping` (Mid-clamps, end-clamps, string alignment).
  5. `Milestone 5: DC Electrical String Cabling & Conduit` (UV conduit, MC4 crimping, DCDB/combiner boxes).
  6. `Milestone 6: Inverter Installation & ACDB Termination` (Inverter wall mounting, LT panel terminations).
  7. `Milestone 7: Earthing Grid & Lightning Protection` (Chemical earth pits, copper/GI strip routing, LA).
  8. `Milestone 8: Pre-Commissioning Electrical Testing & Punch List` (Megger, $V_{oc}$, $I_{sc}$, earth pits).
- **Automated WBS Aggregation:** Submitting daily DPR records automatically rolls up quantitative physical progress percentages into the linked `tabTask.progress` and `tabProject.custom_cumulative_dpr_completion_pct`.

### 2. Standalone Submittable Daily Progress Report (`tabSolar Daily Progress Report`)

The daily field log is modeled as a standalone, submittable DocType (`is_submittable = 1`) with autoname `DPR-.YYYY.-.#####`:

- **Submittable Legal Audit Record:** Once submitted by the `Site Supervisor` and approved by the `Project Engineer`, the daily report is frozen (`docstatus = 1`) to provide an immutable evidentiary record for client billing, contractor milestone payments, and statutory compliance.
- **Daily Operational Log Components:**
  - **Workforce Headcount (`tabSolar DPR Labor Attendance`):** Segregates headcount by trade (Civil Masons, Structural Riggers, Certified Electricians, Helpers, Safety Officers) and tracks billable contractor hours.
  - **Weather & Environmental Disruption:** Logs sky conditions, rainfall, ambient temperature, and specific hours lost to adverse weather.
  - **Physical Task Progress (`tabSolar DPR Activity Progress`):** Quantifies daily output (e.g., 24 pedestals cast, 40 MMS tables erected, 96 panels mounted, 350 meters of DC cable routed) against total planned quantities.
  - **Geotagged Photo Evidence (`tabSolar DPR Photo`):** Requires mandatory photos with GPS coordinates and timestamps for critical milestones.
  - **Site Blockers & Delay Logs (`tabSolar DPR Blocker Log`):** Enforces structured capture of site impediments (grid outages, client access denial, crane breakdown).

### 3. Closed-Loop On-Site Material Consumption Ledger

To eliminate inventory shrinkage and seamlessly power Stage 09 (`Material Return to Store`):

- **Dispatched vs. Installed Synchronization (`tabSolar DPR Material Consumed`):**  
  Every DPR item is bound to the materials issued in Stage 07 (`Delivery Note` items).
- **Daily Site Balance Math:**
  $$\text{Site Balance Remaining} = Q_{\text{Dispatched}} - \sum Q_{\text{Installed Cumulative}}$$
  The system computes live remaining balances on site. Site engineers cannot record cumulative installation quantities exceeding total dispatched goods without an approved anomaly escalation.
- **Direct Feeder to Stage 09:** Upon reaching 100% installation progress, all residual positive balances automatically populate the Stage 09 Surplus Reconciliation workbench for physical return to the central warehouse.

### 4. Mandatory Pre-Commissioning Quality & Electrical Testing Gate (IEC 62446-1)

Physical installation cannot transition to `Completed` until the site passes a mandatory pre-commissioning electrical verification gate:

- **String Electrical Test Log (`tabSolar String Electrical Test Log`):**  
  Measures open-circuit voltage ($V_{oc}$) and short-circuit current ($I_{sc}$) for every DC string:
  $$|V_{oc,\text{measured}} - V_{oc,\text{theoretical}}| \le 0.05 \times V_{oc,\text{theoretical}}$$
  The system calculates theoretical $V_{oc}$ based on module count and STC ratings from Stage 03 engineering design and asserts a $\pm 5\%$ tolerance window.
- **Insulation Resistance (Megger Test):**  
  Records test voltages ($500\text{V} / 1000\text{V DC}$) and asserts insulation resistance $\ge 1.0\text{ M}\Omega$ between:
  1. DC Positive and Protective Earth (PE).
  2. DC Negative and Protective Earth (PE).
  3. AC Phases and Protective Earth (PE).
- **Earth Pit Resistance Test (`tabSolar Earth Pit Test Log`):**  
  Validates earth electrode resistance:
  - DC Array & MMS Structure Earth: $\le 5.0\ \Omega$.
  - Inverter Body & Lightning Arrester: $\le 1.0\ \Omega$.
- **Punch List Zero-Defect Rule:** All category "A" (critical safety/functional) punch list items must be resolved before sign-off.

### 5. Automated Dual Downstream Spawning Engine

Upon formal submission of the Pre-Commissioning sign-off:

1. **Stage 09 Activation (Surplus Material Return):**  
   The platform automatically updates `tabProject.custom_current_lifecycle_stage` to `"Stage 09: Material Return to Store"` and spawns the Stage 09 Reconciliation Task for the Store Assistant and Project Engineer.
2. **Stage 10B Activation (Statutory Grid Synchronization Countdown):**  
   The platform automatically triggers Phase 2 of `tabLiaisoning And Synchronization`, activating the statutory **10-Day SLA countdown timer** for CEIG safety inspection, Joint Meter Inspection (JMI), and bidirectional net-meter energization.

### 6. Installation SLA & Daily DPR Submission Clock

- **Overall Installation SLA:** Configurable in `Solar SLA Settings` based on capacity tier (e.g., Residential $\le 10\text{ kW}$: 3 days; Commercial 10–50 kW: 7 days; Industrial 50–250 kW: 15 days; Utility > 250 kW: 30–45 days).
- **Daily DPR Cutoff SLA:** DPR for work executed on Day $T$ must be submitted before **10:00 AM on Day $T+1$**. Failure to submit triggers an automated notification to the `Project Engineer` and escalates to the `Area Operations Lead`.

---

## Consequences

### Positive Consequences

- **Granular Progress Visibility:** Multi-zone WBS gives management real-time visibility into exact physical percentages across all civil, structural, and electrical milestones.
- **Unbreakable Material Accountability:** Real-time tracking of installed vs. dispatched items eliminates site shrinkage and directly feeds Stage 09 material return reconciliation.
- **Audit-Proof Quality & Safety:** Mandatory IEC 62446-1 testing (Megger, $V_{oc}$, earth pits) guarantees electrical integrity, dramatically reduces inverter breakdown rates, and guarantees first-time pass rates during DISCOM inspections.
- **Seamless Downstream Handoff:** Instant automated triggers activate Stage 09 surplus return and Stage 10B statutory grid sync without human coordination lag.
- **Contractor & Labor Performance Auditing:** Daily labor headcount and trade breakdown data enables precise productivity analysis across civil, structural, and electrical contractors.

### Negative / Trade-Off Consequences

- **Field Data Entry Friction:** Mandating daily mobile DPRs with photos and headcount creates operational overhead for frontline site supervisors.
  - _Mitigation:_ The `/solar` Vue 3 mobile interface is engineered as an offline-first, high-speed touch workflow with smart defaults (carrying forward yesterday's labor headcount and weather), voice-to-text notes, and quick multi-photo uploads.
- **Rigid Pre-Commissioning Gate:** Project completion cannot be falsified or rushed without completing real electrical test logs.
  - _Mitigation:_ Test logs are organized into streamlined digital forms with auto-calculating pass/fail thresholds, empowering field engineers to record string voltages and Megger readings rapidly via digital multimeter and Megger testers.

# Phase 4: Gap Analysis (Fit-Gap Matrix)

**Operational Gaps & ERP Treatment Strategies Across Dual-Flow Lifecycles & Governance Engine**  
_Source: Sadbhav Solar EPC Enterprise Architecture Suite_

---

## 1. Executive Summary

The Gap Analysis evaluates standard generic ERP capabilities against specialized Solar EPC requirements across both operational lifecycles: **Flow 1 (Core Project Delivery Lifecycle)** and **Flow 2 (Store, Purchase & Vendor Governance Lifecycle)**.

It identifies key operational deficiencies in standard ERP software and details custom architectural treatments within `solar_module` to achieve deterministic, upgrade-safe operations.

---

## 2. Fit-Gap Classification Summary Across Enterprise Domains

| Lifecycle Domain                      | Relevant Stages / Steps | Total Gaps | Standard Config | Custom Enhancement (`solar_module`)                                                                   |
| :------------------------------------ | :---------------------: | :--------: | :-------------: | :---------------------------------------------------------------------------------------------------- |
| **Sales & Lead Ingestion**            |    Flow 1: Stage 01     |     4      |        2        | 2 (Deduplication engine, visual lifecycle stepper)                                                    |
| **Technical Site Survey**             |    Flow 1: Stage 02     |     4      |        1        | 3 (24h SLA timer, 6-row mandatory photo table, GPS validation)                                        |
| **Solar Design & Dynamic BOM**        |    Flow 1: Stage 03     |     3      |        0        | 3 (CAD/PVsyst repository, cable math calculation, dynamic BOM explosion)                              |
| **Commercial Proposal & Subsidies**   |    Flow 1: Stage 04     |     3      |        1        | 2 (Real-time subsidy calculation [PM Surya Ghar], gross margin floor governor)                        |
| **Advance Gate & Customer Master**    |    Flow 1: Stage 05     |     3      |        1        | 2 (>20% advance verification gate, **automated Customer creation upon confirmation**)                 |
| **Sales Order Baseline Anchor**       |    Flow 1: Stage 06     |     3      |        1        | 2 (Engineering baseline lock, parallel downstream triggering)                                         |
| **Material Dispatch & Delivery Note** |    Flow 1: Stage 07     |     4      |        2        | 2 (Project-specific Delivery Note gate, serialized panel/inverter scan)                               |
| **Installation & Mobile DPR**         |    Flow 1: Stage 08     |     4      |        1        | 3 (Zone-based WBS, mobile DPR with labor/weather logs, pre-comm punch list)                           |
| **Site Material Return & Surplus**    |    Flow 1: Stage 09     |     3      |        1        | 2 (Issued vs installed reconciliation, mandatory Stock Entry Material Return)                         |
| **Dual-Timing Liaisoning & Closeout** |    Flow 1: Stage 10     |     5      |        0        | 5 (Phase 1 post-SO doc filing, Phase 2 post-install 10-day countdown, **Project Completion trigger**) |
| **Post-Commissioning O&M**            |    Flow 1: Stage 11     |     4      |        1        | 3 (Automated Solar Asset Register from GRN, inverter IoT telemetry, AMC scheduler)                    |
| **Store Requisition & Low Stock**     |     Flow 2: Step 01     |     3      |        2        | 1 (Store-to-Purchase MR notification, automated low-stock broadcast)                                  |
| **RFQ & Supplier Comparison**         |   Flow 2: Steps 02-03   |     4      |        1        | 3 (Multi-vendor RFQ dispatch, **Quotation Comparison Sheet**, decision scoring)                       |
| **Multi-Location GRN (Store / Site)** |   Flow 2: Steps 04-05   |     4      |        2        | 2 (Flexible Store OR Working Site GRN by Store/Site/Purchase, barcode scan)                           |
| **Joint Vendor Payment Tracking**     |   Flow 2: Steps 06-07   |     3      |        1        | 2 (Collaborative Purchase + Accounts payment tracking workbench, milestone aging)                     |
| **Vendor Rating Governance**          |     Flow 2: Step 08     |     3      |        0        | 3 (Objective multi-criteria Vendor Rating Scorecard feeding future RFQs)                              |
| **Task SLA/TAT & Admin Controls**     |  Cross-Flow Governance  |     4      |        0        | 4 (Per-task SLA countdown upon assignment, `Solar SLA Settings` Admin customization)                  |
| **Notification & Alert Matrix**       |  Cross-Flow Governance  |     5      |        1        | 4 (Multi-recipient alerts, low stock/overdue escalation, `Solar Notification Settings` toggles)       |

---

## 3. High-Priority Gaps & Custom ERP Treatments

### Gap #01: Customer Master Inception Timing (Flow 1: Stage 05)

- **Problem:** Generic ERPs either create a Customer prematurely at the lead stage (cluttering accounts ledgers with non-converting prospects) or require manual customer re-keying after deal confirmation.
- **ERP Treatment:** Custom controller hook in `Proposal` / `Sales Order` checks for customer confirmation and advance clearance. Upon approval, it programmatically converts the prospect into a formal ERPNext `Customer` master with contact details, billing/shipping addresses, and DISCOM consumer number.

### Gap #02: Task-Level SLA / TAT Activation Upon Assignment (Flow 1 & Flow 2)

- **Problem:** Standard ERP tasks lack dynamic countdown timers tied directly to user assignment, causing tasks to linger unnoticed.
- **ERP Treatment:** Custom SLA engine calculates `due_date = assignment_timestamp + sla_hours`. Tracks active countdowns; if breached, automatically marks task as `Overdue` and dispatches escalation alerts. Admins / Directors can customize all default SLA durations via `Solar SLA Settings`.

### Gap #03: Material Dispatch Logistics via Delivery Note (Flow 1: Stage 07)

- **Problem:** Materials are sent to sites on ad-hoc trucks without official dispatch documentation, creating transit disputes and loss of component serial traceability.
- **ERP Treatment:** Delivery Note stage-gate verifies project allocation against frozen BOM, enforces serial scanning for panels/inverters, and validates transporter vehicle and e-way bill details before physical dispatch.

### Gap #04: Post-Installation Surplus Site Material Return (Flow 1: Stage 09)

- **Problem:** Standard ERPs assume 100% of dispatched materials are consumed, ignoring site surplus (cables, leftover panels, hardware) which gets lost, scrapped, or stolen.
- **ERP Treatment:** Mandatory reconciliation screen compares `Delivery Note` quantities against installed quantities per BOM and DPR logs. Automatically generates a `Stock Entry` (Purpose: **Material Return**) to return unused materials to the store warehouse before project closure is permitted.

### Gap #05: Dual-Timing Liaisoning & Project Completion Trigger (Flow 1: Stage 10)

- **Problem:** Standard ERPs have no concept of regulatory utility liaisoning that starts document prep at Sales Order but performs actual statutory inspection and grid energization countdowns only after installation finishes. Furthermore, project completion is manually marked rather than tied to statutory grid synchronization.
- **ERP Treatment:** Custom DocType `Liaisoning And Synchronization` bifurcates into:
  1. **Phase 1 (Post-SO):** Collects customer KYC and submits DISCOM portal applications.
  2. **Phase 2 (Post-Install):** Enforces a 10-day SLA countdown for CEIG safety audit, JMI inspection, and net-meter testing.
  3. **Project Completion Hook:** Submission of the official commissioning / grid energization report automatically transitions the linked `Project` status to **Completed**.

### Gap #06: Supplier Quotation Comparative Evaluation Sheet (Flow 2: Step 03)

- **Problem:** Procurement buyers place orders with preferred vendors without objective comparison across submitted quotes.
- **ERP Treatment:** Custom **Quotation Comparison Sheet** compiles multiple supplier quotations side-by-side, analyzing unit prices, freight, warranty terms, delivery lead times, and historical vendor ratings to recommend the optimal purchase decision.

### Gap #07: Flexible Multi-Location GRN (Store Warehouse vs. Working Site) (Flow 2: Step 05)

- **Problem:** Heavy equipment (mounting structures, modules) delivered directly to remote sites cannot be received in standard ERP systems without a storekeeper on site.
- **ERP Treatment:** Flexible `Purchase Receipt` configuration allows goods receipt to be executed either at the **Central Store** OR at the **Working Site directly**, with authorized role permissions granted to Store Managers, Site Supervisors, or Purchase Team members.

### Gap #08: Collaborative Vendor Payment Tracking (Purchase + Accounts) (Flow 2: Step 07)

- **Problem:** Purchase teams promise milestone payments (advance, dispatch, post-GRN) while accounts pays based on ledger cycles, causing vendor friction and site shipment freezes.
- **ERP Treatment:** Centralized **Vendor Payment Tracking Workbench** provides shared real-time visibility to both Purchase and Accounts teams into milestone payment obligations, aging schedules, and invoice 3-way match verification.

### Gap #09: Objective Vendor Performance Rating System (Flow 2: Step 08)

- **Problem:** Generic ERPs lack automated post-delivery supplier scorecards, leading to repeat purchases from unreliable vendors.
- **ERP Treatment:** Custom `Vendor Rating` DocType evaluates suppliers upon GRN/invoice completion on On-Time Delivery (OTD), Quality/Rejection Rate, Price Adherence, and Service Responsiveness. Overall rating score dynamically influences future RFQ selections.

### Gap #10: Multi-Tier Alert Matrix with Admin/Director Toggle Controls

- **Problem:** Standard notification systems send either too many irrelevant emails or fail to alert executive leadership on critical operational bottlenecks.
- **ERP Treatment:** Dedicated `Solar Notification Settings` allows Admins and Directors to toggle notifications on/off per process, flow, or step. Enforces automatic alerts to Purchase Managers on Material Requests, to Purchase and Store Managers on Low Stock, and broadcasts assignments, overdue tasks, and purchase milestones to Admin/Director.

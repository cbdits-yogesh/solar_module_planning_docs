# Phase 5: Business Requirements Document (BRD)

**Strategic Management Objectives & Master Business Requirements (`BR-001` to `BR-018`)**  
_Source: Sadbhav Solar EPC Enterprise Architecture Suite_

---

## 1. Strategic Management Objectives

1. **Capacity Scaling:** Double annual solar EPC commissioning capacity from 25 MW to 50+ MW without a linear overhead increase in sales, design, or administrative headcount.
2. **Cycle Time Reduction:** Accelerate customer order-to-grid synchronization turnaround times by 35% through automated pipeline handoffs across all 11 project stages and 8 procurement steps.
3. **Margin Protection & Scrap Elimination:** Prevent working capital leakage via financial advance gates ($> 20\%$) and eliminate site scrap/theft by enforcing post-installation surplus material returns to store.
4. **100% Statutory Compliance & Subsidy Protection:** Ensure zero subsidy forfeitures under national portals (PM Surya Ghar / PM KUSUM) by synchronizing post-installation CEIG and JMI net-meter testing within an enforced 10-day SLA.
5. **Procurement Excellence & Vendor Quality:** Eliminate single-vendor bias through mandatory Quotation Comparison Sheets, ensure seamless store/site receipts, and evaluate suppliers via an objective Vendor Rating System.
6. **Executive Governance & SLA Discipline:** Enforce SLA/TAT countdowns upon task assignment, empower Admins/Directors to customize timelines, and provide real-time notification alerts for low stock, overdue tasks, and procurement milestones.

---

## 2. Master Business Requirements Catalog (`BR-001` to `BR-018`)

| Requirement ID | Requirement Name                         |    Lifecycle Scope    | Strategic Objective & Business Justification                                                                                                             | Target KPI / Impact                                     |
| :------------- | :--------------------------------------- | :-------------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------ |
| **`BR-001`**   | **Lead Ingestion & Deduplication**       |   Flow 1: Stage 01    | Centralize multi-channel prospect capture, block duplicate phone/emails, and auto-assign leads with 2h response SLA.                                     | Zero lost leads; < 2h initial response time.            |
| **`BR-002`**   | **Standardized 24h Site Survey**         |   Flow 1: Stage 02    | Enforce mandatory 10 technical fields, 6 fixed photo checklist items, and GPS stamping within a default 24h SLA.                                         | Zero survey revisits; 100% survey data accuracy.        |
| **`BR-003`**   | **Solar PV Design & Dynamic BOM**        |   Flow 1: Stage 03    | Provide CAD/PVsyst repositories, automated cable sizing calculations, and dynamic BOM explosion (`custom_quot_bom`).                                     | Zero engineering rework; 100% BOM accuracy.             |
| **`BR-004`**   | **Dynamic Proposals & Subsidies**        |   Flow 1: Stage 04    | Compute real-time component costs, PM Surya Ghar central/state subsidies, customer payback, and enforce margin floor.                                    | Proposal generation time reduced to < 15 mins.          |
| **`BR-005`**   | **Advance Gate & Customer Master**       |   Flow 1: Stage 05    | Block project execution until customer advance ($> 20\%$) or bank loan clears. **Formally instantiate Customer master & contacts upon confirmation.**    | 100% cash flow protection; clean ledger master.         |
| **`BR-006`**   | **Sales Order Master Baseline Lock**     |   Flow 1: Stage 06    | Lock commercial pricing, payment terms, and approved BOM specifications; programmatically spawn WBS and early Liaisoning doc prep.                       | Single source of truth; 100% auditability.              |
| **`BR-007`**   | **Material Dispatch via Delivery Note**  |   Flow 1: Stage 07    | Issue materials from store to site via ERPNext `Delivery Note` with transporter details, e-way bill, and asset serial scanning (modules, inverters).     | 100% transit accountability; zero missing serials.      |
| **`BR-008`**   | **Zone Installation & Mobile DPR**       |   Flow 1: Stage 08    | Track multi-zone installations with daily mobile DPRs capturing labor headcount, weather disruptions, civil progress, and Megger test logs.              | Real-time schedule visibility; < 5% budget variance.    |
| **`BR-009`**   | **Site Material Return to Store**        |   Flow 1: Stage 09    | Reconcile materials dispatched vs materials installed. Enforce return of unused/surplus items back to store via `Stock Entry` (Material Return).         | Site inventory shrinkage reduced from 4% to < 0.2%.     |
| **`BR-010`**   | **Liaisoning & Project Completion**      |   Flow 1: Stage 10    | Start document prep post-SO; activate actual 10-day SLA countdown post-installation for CEIG/JMI/Net-metering. **Completion formally closes Project.**   | 100% on-time net-metering; 0% subsidy lapse.            |
| **`BR-011`**   | **Solar Asset Register & O&M**           |   Flow 1: Stage 11    | Auto-populate Solar Asset Register from GRN serials; integrate inverter cloud telemetry; automate biannual preventative AMC visits.                      | < 24h warranty claim processing; > 98% plant uptime.    |
| **`BR-012`**   | **Store Requisition & Low-Stock Alerts** |    Flow 2: Step 01    | Enable Store to raise Material Requests to Purchase; auto-dispatch urgent alerts to Purchase and Store Managers when items drop below reorder levels.    | Zero stock-outs; proactive replenishment.               |
| **`BR-013`**   | **RFQ & Quotation Comparison**           |  Flow 2: Steps 02-03  | Dispatch RFQs to multiple suppliers; compile comparative evaluation sheet analyzing unit prices, lead times, warranties, and vendor ratings.             | 5-8% procurement savings; 100% purchase transparency.   |
| **`BR-014`**   | **Flexible Store / Site GRN**            |  Flow 2: Steps 04-05  | Allow Goods Receipt (GRN) at central store OR directly at project sites by authorized Store, Site, or Purchase personnel with serial capture.            | Eliminates receipt bottlenecks; enables 3-way matching. |
| **`BR-015`**   | **Joint Vendor Payment Tracking**        |  Flow 2: Steps 06-07  | Provide a shared payment workbench for Purchase and Accounts to monitor vendor payment milestones, credit terms, and cash flow obligations.              | Zero supplier shipment holds; 100% credit compliance.   |
| **`BR-016`**   | **Vendor Performance Rating**            |    Flow 2: Step 08    | Automatically evaluate suppliers upon GRN/invoice closure on On-Time Delivery, Quality, Price Adherence, and Service to govern future RFQ awards.        | Tier 1 supplier retention; quality issue reduction.     |
| **`BR-017`**   | **Task SLA / TAT Engine & Settings**     | Cross-Flow Governance | Enforce SLA countdown timers on every task upon assignment. Provide `Solar SLA Settings` for Admin / Director to customize durations per step.           | Eliminates operational delays; complete accountability. |
| **`BR-018`**   | **Multi-Tier Notification Engine**       | Cross-Flow Governance | Real-time alerts for assignment, overdue tasks, low stock, MRs, and purchase milestones with Admin / Director toggles via `Solar Notification Settings`. | 100% executive visibility; instantaneous escalation.    |

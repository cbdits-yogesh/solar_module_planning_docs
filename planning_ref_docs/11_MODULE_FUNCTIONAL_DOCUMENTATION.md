# Phase 11: Module Functional Documentation

**Standard Operating Procedures (SOPs) Across Dual Lifecycles & Governance Engine (`MOD-01` to `MOD-19`)**  
_Source: Sadbhav Solar EPC Enterprise Architecture Suite_

---

## 1. Flow 1: Solar EPC Project Execution SOPs

### `MOD-01`: CRM & Lead Management (Stage 01)

- **Objective:** Systematic prospect capture, qualification, deduplication, and immediate regional assignment.
- **SOP:** Lead ingested from web/walk-in $\rightarrow$ Server-side validator checks phone/email uniqueness $\rightarrow$ Lead auto-assigned to regional sales executive $\rightarrow$ Initial contact logged within 2 hours $\rightarrow$ Site Survey requested upon qualification.

### `MOD-02`: Technical Site Survey & Audit (Stage 02)

- **Objective:** Standardized on-site technical metrics and photo evidence captured within a strict 24-hour turnaround time.
- **SOP:** Survey Engineer assigned $\rightarrow$ 24h SLA countdown timer activates $\rightarrow$ Engineer visits site $\rightarrow$ Records 10 technical metrics $\rightarrow$ Captures 6 mandatory photo checklist rows with GPS lock $\rightarrow$ Survey marked `Completed` (or escalates to `Overdue` past 24h).

### `MOD-03`: Solar PV Engineering Design & Dynamic BOM (Stage 03)

- **Objective:** Integrated CAD/SLD drafting, parametric cable sizing, and automated dynamic BOM generation.
- **SOP:** Design Engineer assigned $\rightarrow$ Reviews completed survey $\rightarrow$ Uploads CAD layouts, SLDs, and PVsyst simulations $\rightarrow$ Enters string lengths in `cable_calculation_table` $\rightarrow$ Executes dynamic BOM explosion into `custom_quot_bom` $\rightarrow$ Signs off to freeze technical baseline.

### `MOD-04`: Dynamic Commercial Proposal & Subsidies (Stage 04)

- **Objective:** Rapid quotation generation incorporating real-time component costs and government subsidies.
- **SOP:** Sales/Commercial initiates `Proposal` from approved survey $\rightarrow$ System pulls component pricing and BOM quantities $\rightarrow$ Computes state/central subsidy deductions (PM Surya Ghar) $\rightarrow$ Margin floor validator confirms gross margin threshold $\rightarrow$ Client proposal PDF generated and dispatched.

### `MOD-05`: Advance Verification, Financial Gate & Customer Inception (Stage 05)

- **Objective:** Working capital protection, formal customer master instantiation, and strict financial gatekeeping.
- **SOP:** Customer confirms proposal $\rightarrow$ Advance payment collected ($> 20\%$) or bank loan sanction secured $\rightarrow$ Accounts Officer verifies UTR/Cheque reference $\rightarrow$ **System automatically creates the official ERPNext `Customer` master and linked contacts** $\rightarrow$ Financial clearance gate unlocked $\rightarrow$ Releases Sales Order for submission.

### `MOD-06`: Sales Order Master Baseline Anchor & Downstream Kickoff (Stage 06)

- **Objective:** Contractual baseline freeze and synchronized operational kickoff.
- **SOP:** CRM Team submits `Sales Order` $\rightarrow$ System permanently locks commercial pricing and approved BOM $\rightarrow$ Programmatically spawns `Project` container with templated zone WBS tasks $\rightarrow$ Concurrently instantiates `Liaisoning And Synchronization` record for Phase 1 document preparation.

### `MOD-07`: Material Dispatch Logistics via Delivery Note (Stage 07)

- **Objective:** Authorized physical dispatch of materials from central store to installation site with asset serial tracking.
- **SOP:** Store Manager reviews project BOM $\rightarrow$ Creates ERPNext `Delivery Note` $\rightarrow$ Scans individual barcodes for PV modules and inverters $\rightarrow$ Records transporter details, vehicle number, and e-way bill $\rightarrow$ Submits Delivery Note $\rightarrow$ Stock deducted from central warehouse $\rightarrow$ Goods in transit to site.

### `MOD-08`: Zone-Based Installation Execution & Mobile DPR (Stage 08)

- **Objective:** Structured site mobilization, milestone execution, and daily progress logging.
- **SOP:** Site team mobilized under Project Manager $\rightarrow$ Site Supervisor submits daily mobile DPRs (weather conditions, labor headcount, civil foundations, modules mounted, cabling running meters) $\rightarrow$ Pre-commissioning quality punch list and Megger insulation resistance test logs executed and verified upon physical completion.

### `MOD-09`: Site Material Reconciliation & Surplus Return to Store (Stage 09)

- **Objective:** Eliminate site scrap and inventory leakage through mandatory material return reconciliation.
- **SOP:** Installation marked physically complete $\rightarrow$ System compares materials issued in Delivery Note against materials installed per engineering BOM $\rightarrow$ Identifies residual items (panels, cable remnants, structural fasteners) $\rightarrow$ Generates `Stock Entry` (Purpose: **Material Return**) $\rightarrow$ Materials transported back to central store $\rightarrow$ Store Manager acknowledges receipt $\rightarrow$ Site balance reconciled to zero.

### `MOD-10`: Statutory Liaisoning & Automated Project Completion (Stage 10)

- **Objective:** Utility net-metering governance, statutory grid synchronization, and formal project closeout.
- **SOP:**
  - **Phase 1 (Post-SO):** Liaisoning Officer submits DISCOM application with consumer KYC, property documents, and drawings $\rightarrow$ Tracks feasibility study and obtains grid connectivity NOC.
  - **Phase 2 (Post-Installation):** Triggered immediately upon installation completion $\rightarrow$ **Starts 10-day statutory SLA countdown timer** $\rightarrow$ Coordinates CEIG electrical safety inspection $\rightarrow$ Conducts Joint Meter Inspection (JMI) $\rightarrow$ Bi-directional net-meter installed and grid energized $\rightarrow$ **Approval of this phase automatically transitions the `Project` status to "Completed", logs COD certificate, and unlocks O&M.**

### `MOD-11`: Digital Handover & Lifecycle O&M (Stage 11)

- **Objective:** Plant asset management, IoT performance monitoring, and automated preventative maintenance.
- **SOP:** Grid synchronization triggers automatic generation of `Solar Asset Register` populated with barcode serials from GRN/Delivery Notes $\rightarrow$ Inverter IoT telemetry connected $\rightarrow$ Daily generation tracked against simulated yield $\rightarrow$ Biannual preventative AMC visits automatically scheduled.

---

## 2. Flow 2: SCM, Store, Purchase & Vendor Procurement SOPs

### `MOD-12`: Store Requisition & Low-Stock Monitoring (Step 01)

- **Objective:** Proactive inventory replenishment and automated shortage alerts.
- **SOP:** Store Manager identifies stock need or system detects stock $\le$ reorder level $\rightarrow$ Store generates `Material Request` (Purpose: Purchase) $\rightarrow$ System automatically dispatches alert to **Purchase Manager** $\rightarrow$ If stock is critically low, alert is broadcast to **both Purchase Manager and Store Manager** (+ Admin/Director).

### `MOD-13`: RFQ Management & Quotation Comparative Evaluation (Steps 02-03)

- **Objective:** Competitive multi-vendor sourcing and transparent purchase decision-making.
- **SOP:** Purchase Manager reviews Material Request $\rightarrow$ Dispatches `Request for Quotation` (RFQ) to 2-3 approved suppliers $\rightarrow$ Ingests submitted rates, taxes, freight, warranties, and lead times into `Supplier Quotation` $\rightarrow$ Generates **Quotation Comparison Sheet** $\rightarrow$ Evaluates suppliers across cost, lead time, and vendor rating score $\rightarrow$ Secures approval for winning quote.

### `MOD-14`: Purchase Order & Multi-Location Goods Receipt (Steps 04-05)

- **Objective:** Accurate contract placement and flexible goods receipt at store or site.
- **SOP:** Purchase issues PO to winning supplier $\rightarrow$ Supplier delivers goods $\rightarrow$ **Goods Receipt (GRN) can be executed at the Central Store warehouse OR directly at the Working Site** by authorized Store, Site, or Purchase personnel $\rightarrow$ Individual panel/inverter barcodes scanned $\rightarrow$ Physical inspection completed and GRN submitted.

### `MOD-15`: 3-Way Match Invoicing & Joint Vendor Payment Tracking (Steps 06-07)

- **Objective:** Cash flow predictability, milestone compliance, and seamless accounts collaboration.
- **SOP:** Supplier submits bill $\rightarrow$ Account or Purchase team books `Purchase Invoice` $\rightarrow$ System verifies 3-way match against PO and GRN $\rightarrow$ Invoice mapped to **Vendor Payment Tracking Workbench** $\rightarrow$ Purchase and Accounts teams jointly track payment milestones (advance, on-dispatch, against GRN, retention) $\rightarrow$ Payment released on time without vendor friction.

### `MOD-16`: Vendor Performance Rating Governance (Step 08)

- **Objective:** Objective supplier accountability and data-driven future procurement.
- **SOP:** Upon GRN/invoice completion, system generates `Vendor Rating` scorecard $\rightarrow$ Evaluates supplier across On-Time Delivery (35%), Quality/Rejections (35%), Price Adherence (15%), and Service Responsiveness (15%) $\rightarrow$ Updates supplier's cumulative rating $\rightarrow$ Feeds directly into subsequent RFQ shortlists.

---

## 3. Cross-Flow Governance SOPs

### `MOD-17`: Task SLA / TAT Engine & Admin Customization

- **Objective:** Continuous operational turnaround tracking with full administrative flexibility.
- **SOP:** Task assigned to team member in Flow 1 $\rightarrow$ SLA timer starts based on `Solar SLA Settings` $\rightarrow$ Dynamic countdown badge displayed $\rightarrow$ If uncompleted past deadline, daemon marks task `Overdue` $\rightarrow$ Delay audit log created $\rightarrow$ Escalation alerts dispatched. Admin / Director can adjust baseline SLA durations per step via `Solar SLA Settings`.

### `MOD-18`: Multi-Tier Notification Engine & Granular Admin Toggles

- **Objective:** Targeted operational alerts with complete executive oversight and toggle governance.
- **SOP:** System detects event (Assignment, Creation, Overdue, Low Stock, MR, Purchase milestone) $\rightarrow$ Inspects `Solar Notification Settings` $\rightarrow$ If enabled by Admin/Director, dispatches notifications via Socket.IO, Desk notifications, Email, and WhatsApp to designated primary/secondary recipients and Admin/Director.

### `MOD-19`: Master Data Governance & Timings

- **Objective:** Strict data hygiene across Customer, Supplier, and Item masters.
- **SOP:**
  - **Customer Master:** Created strictly when customer confirms for solar installation (Flow 1: Stage 05).
  - **Supplier Master:** Onboarded with GST, bank details, equipment categories, and dynamic Vendor Rating scores.
  - **Item Master:** Standardized across **Stock** (valuation, serials, reorder levels), **Store** (bin location, storage conditions), and **Purchase** (lead times, preferred suppliers, UOMs, inspection criteria).

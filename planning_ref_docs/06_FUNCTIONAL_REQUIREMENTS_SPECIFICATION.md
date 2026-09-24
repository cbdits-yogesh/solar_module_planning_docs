# Phase 6: Functional Requirements Specification (FRS)

**Screen Controls, Field Rules, Actors, Stage-Gates & Validations Across Dual Lifecycles (`FR-001` to `FR-019`)**  
_Source: Sadbhav Solar EPC Enterprise Architecture Suite_

---

## 1. Flow 1: Core Solar EPC Project Execution Lifecycle

### `FR-001`: Lead Onboarding & Deduplication Pipeline (Stage 01)

- **Primary Actors:** Sales Executive, BD Manager.
- **Functional Screens:** `/solar/leads` and Frappe Desk `Lead` / `CRM Lead`.
- **Core Controls & Validations:**
  - Mandatory Fields: `first_name`, `mobile_no`, `custom_lead_organization_name`, `status`, `custom_territory`.
  - Server-Side Deduplication: Intercepts mobile numbers and emails across both `Lead` and `CRM Lead`. Prevents duplicate prospect creation.
  - Assignment & SLA Clock: Auto-assigns lead to regional sales executive; triggers 2h initial contact SLA timer.
  - Lifecycle Stepper: 11-stage progress bar showing timestamps, active badges, and linked document drawer.

### `FR-002`: Technical Audit & Mandatory Document Checklist (Stage 02)

- **Primary Actors:** Survey Engineers.
- **Functional Screen:** `Site Survey` DocType (Mobile Touch UI & Desk).
- **Core Controls & Validations:**
  - Mandatory Technical Fields: Capacity (kW), System Type (On-Grid/Hybrid/Off-Grid), Site Classification, Sanctioned Connected Load, Mounting Type, Roof Height, Storage Space, Geocoded Coordinates, Utility Bill Name Match.
  - Mandatory Photo Checklist Table: Enforces 6 mandatory rows (`Inverter/ACDB/DCDB`, `Earthing 1-3`, `LT Panel`, `Meter Board`, `Roof Panorama`, `Obstacle/Shadow Area`) with file attachment validators.
  - 24h SLA / TAT Countdown: Countdown begins upon survey assignment. Computes `due_date = assignment + 24h`. If unsubmitted past deadline, status transitions to `Overdue` and escalates. (Configurable by Admin/Director via `Solar SLA Settings`).

### `FR-003`: Solar PV Engineering Design & Dynamic BOM Freeze (Stage 03)

- **Primary Actors:** Solar Design Engineers.
- **Functional Screens:** `site_survey_design_file`, `cable_calculation_table`, and `custom_quot_bom` child tables inside `Site Survey`.
- **Core Controls & Validations:**
  - Design File Repository: Multi-file versioned upload for AutoCAD DWG/DXF drawings, SLD diagrams, and PVsyst yield simulations.
  - Parametric Cable Math: Computes DC and AC cable cross-sections and allowable voltage drop ($\le 2\%$) based on string lengths and inverter capacity.
  - Dynamic BOM Explosion: Programmatically calculates modules, inverters, structure tonnage, and BOS items into `custom_quot_bom`. Design sign-off permanently freezes the engineering baseline.

### `FR-004`: Dynamic Commercial Proposal & Subsidy Engine (Stage 04)

- **Primary Actors:** Sales Executive, Commercial Manager.
- **Functional Screens:** `Proposal` and `Quotation` DocTypes.
- **Core Controls & Validations:**
  - Dynamic Pricing: Automatically pulls pricing from frozen BOM quantities and current Item master rates.
  - Subsidy Calculation: Computes central and state government subsidy deductions (PM Surya Ghar / PM KUSUM), net customer investment, and estimated payback period.
  - Margin Floor Governor: Validates quote margin against minimum standard gross margin. Quotations falling below threshold trigger mandatory Commercial Manager approval before client dispatch.

### `FR-005`: Order Confirmation, Advance Clearance & Customer Master Inception Gate (Stage 05)

- **Primary Actors:** Finance & Accounts Officer, Commercial Manager.
- **Functional Screen:** `Sales Order` (Financial Clearance Modal & `Payment Entry`).
- **Core Controls & Validations:**
  - Financial Verification Gate: Blocks project execution until customer advance payment ($> 20\%$) or bank loan sanction disbursement letter is verified in the system.
  - **Automated Customer Master Creation:** Validated customer confirmation triggers programmatic creation of the official ERPNext `Customer` master, generating linked billing/shipping addresses, contact records, and DISCOM consumer profile.
  - Locks procurement release and site dispatch until financial clearance is recorded.

### `FR-006`: Sales Order Master Baseline Anchor & Downstream Spawning (Stage 06)

- **Primary Actors:** CRM Team, Project Operations.
- **Functional Screen:** `Sales Order` DocType.
- **Core Controls & Validations:**
  - Baseline Freeze: Permanently locks commercial pricing, payment terms, and approved BOM specifications.
  - Dual Downstream Trigger:
    1. Instantiates the operational `Project` container with templated zone WBS tasks.
    2. Instantiates `Liaisoning And Synchronization` record for Phase 1 document preparation.

### `FR-007`: Material Dispatch Logistics via Delivery Note (Stage 07)

- **Primary Actors:** Store Manager, Store Assistant.
- **Functional Screen:** ERPNext `Delivery Note` DocType.
- **Core Controls & Validations:**
  - Dispatch Authorization: Validates dispatched item quantities against frozen project BOM and free store warehouse inventory.
  - Serial Scanning: Enforces 2D/barcode scanning for all serialized items (PV modules, solar inverters) linking serials to the project.
  - Logistics Manifest: Mandatory fields for Transporter Name, Vehicle Registration Number, Driver Phone, and E-Way Bill Number before status can become `Submitted`.
  - Auto-updates inventory ledger, deducting materials from the central warehouse.

### `FR-008`: Zone-Based Installation Execution & Mobile DPR (Stage 08)

- **Primary Actors:** Site Supervisor, Field Engineer, Project Manager.
- **Functional Screens:** `Project`, `Task`, and `Daily Progress Report (DPR)` DocTypes.
- **Core Controls & Validations:**
  - Zone Segmentation: Segregates large roofs or fields into discrete execution zones.
  - Daily Mobile DPR: Captures daily weather conditions, labor headcount, civil footings completed, structures erected, modules mounted, and cabling running meters.
  - Pre-Commissioning Quality Punch List: Validates string open-circuit voltage ($V_{oc}$), operating current ($I_{sc}$), and insulation resistance (Megger) test logs before marking installation complete.

### `FR-009`: Site Material Reconciliation & Surplus Return to Store (Stage 09)

- **Primary Actors:** Site Supervisor, Store / Inventory Manager.
- **Functional Screen:** `Stock Entry` (Purpose: **Material Return**) & Site Reconciliation Report.
- **Core Controls & Validations:**
  - Automated Reconciliation: Compares materials issued via `Delivery Note` against materials installed per engineering BOM and DPR logs.
  - Mandatory Surplus Return: If surplus, unused, or residual materials remain at site (panels, cable remnants, structural fasteners), system requires creation and submission of a `Stock Entry` (Material Return) to transfer items back to central store.
  - Completion Gate: Project handover cannot proceed until site material balance is reconciled to zero variance.

### `FR-010`: Dual-Timing Statutory Liaisoning & Project Completion Trigger (Stage 10)

- **Primary Actors:** Liaisoning & Compliance Officer, Quality & Commissioning Engineer.
- **Functional Screen:** `Liaisoning And Synchronization` DocType.
- **Core Controls & Validations:**
  - **Phase 1 (Post-SO Early Compliance):** Tracks consumer KYC, property documents, DISCOM application number, and grid feasibility NOC.
  - **Phase 2 (Post-Installation Grid Sync):** Triggered immediately upon installation completion. Starts the **statutory countdown timer (Default 10 Days; customizable by Admin/Director)** for CEIG electrical safety approval, Joint Meter Inspection (JMI) date, bi-directional net-meter serial number, and grid energization certificate.
  - **Project Completion Gate:** Approval of this phase **automatically sets the linked `Project` status to "Completed"**, logs the Commercial Operation Date (COD), and triggers the digital handover.

### `FR-011`: Digital Solar Asset Register & Lifecycle O&M (Stage 11)

- **Primary Actors:** O&M Service Engineer, Helpdesk Agent.
- **Functional Screens:** `Solar Asset Register` and `Maintenance Visit` DocTypes.
- **Core Controls & Validations:**
  - Automatic Asset Generation: Grid synchronization instantiates the `Solar Asset Register`, populated with serialized module and inverter mappings from GRN/Delivery Notes.
  - Telemetry Ingestion: Ingests daily energy generation ($kWh$), peak power ($kW$), and inverter fault codes via cloud APIs.
  - Automated Preventative AMC: Automatically generates biannual preventative maintenance schedules and manages warranty claims against OEM serials.

---

## 2. Flow 2: SCM, Store, Purchase & Vendor Procurement Lifecycle

### `FR-012`: Store Requisition & Automated Low-Stock Monitoring (Step 01)

- **Primary Actors:** Store / Inventory Manager, Purchase Manager.
- **Functional Screen:** `Material Request` DocType.
- **Core Controls & Validations:**
  - Store-to-Purchase Requisition: Stores raise `Material Request` (Purpose: Purchase) specifying required items, project references, and required-by dates.
  - Automated Low-Stock Alert: Real-time daemon evaluates warehouse balance against item reorder points. When stock $\le$ reorder level, automatically dispatches urgent alerts to **both Purchase Manager and Store Manager**.
  - Auto-notifies Purchase Manager upon MR submission.

### `FR-013`: RFQ Management & Supplier Quotation Comparison Sheet (Steps 02-03)

- **Primary Actors:** Procurement / Purchase Manager.
- **Functional Screens:** `Request for Quotation` and **`Quotation Comparison Sheet`**.
- **Core Controls & Validations:**
  - RFQ Dispatch: Multi-vendor RFQ dispatch to approved suppliers for specified items and quantities.
  - Supplier Quote Ingestion: Captures unit rates, taxes, freight, warranty terms, and promised delivery lead times in `Supplier Quotation`.
  - **Quotation Comparison Sheet:** Side-by-side comparison matrix evaluating at least 2-3 supplier quotations. Ranks vendors by total landed cost, delivery lead time, and historical vendor performance rating score. PO placement requires an authorized comparison decision.

### `FR-014`: Purchase Order & Multi-Location Goods Receipt (Steps 04-05)

- **Primary Actors:** Purchase Manager, Store Manager, Site Supervisor.
- **Functional Screens:** `Purchase Order` and `Purchase Receipt` (GRN).
- **Core Controls & Validations:**
  - PO Release: Formal PO released to winning supplier locking commercial terms and delivery schedule.
  - **Flexible Store OR Working Site GRN:** Goods receipt can be booked at the **Central Store warehouse OR directly at the Working Site**. Authorized role permissions are granted to Store Managers, Site Supervisors, or Purchase Team members.
  - Serial/Barcode Ingestion: Mobile and scanner-assisted capture of PV module serials, inverter serials, and cable drum batch numbers with physical inspection sign-off.

### `FR-015`: Purchase Invoicing 3-Way Match & Joint Vendor Payment Tracking (Steps 06-07)

- **Primary Actors:** Accounts Officer, Purchase Manager.
- **Functional Screens:** `Purchase Invoice` and **`Vendor Payment Tracking Workbench`**.
- **Core Controls & Validations:**
  - 3-Way Matching: Validates that `Purchase Invoice` matches quantities and rates in `Purchase Order` and received quantities in `Purchase Receipt`.
  - **Collaborative Payment Workbench:** Shared dashboard providing real-time visibility to both Purchase and Accounts teams into milestone payment obligations (advance, dispatch, post-GRN, retention), credit aging, and cash flow projections. Prevents supplier disputes and shipment freezes.

### `FR-016`: Vendor Performance Rating Governance (Step 08)

- **Primary Actors:** Purchase Manager, Quality Engineer.
- **Functional Screen:** `Vendor Rating` DocType & Supplier Scorecard.
- **Core Controls & Validations:**
  - Automatic Rating Engine: Evaluates vendors on 4 weighted criteria upon GRN/invoice completion:
    1. On-Time Delivery (OTD) (35%)
    2. Quality & Rejection Rate (35%)
    3. Price Adherence & Commercial Terms (15%)
    4. Service & Response Time (15%)
  - Scorecard Feedback: Updates supplier's overall rating score ($0 - 100\%$) and classifies them as Tier 1, Approved, or Probationary, directly influencing future RFQ shortlists.

---

## 3. Cross-Flow Governance, SLA Engine & Notification Matrix

### `FR-017`: Task SLA / TAT Engine & Administrative Customization

- **Primary Actors:** Admin (Project Supreme), Director, System Manager, All Assignees.
- **Functional Screen:** `Solar SLA Settings` (Single DocType).
- **Core Controls & Validations:**
  - Task Assignment Trigger: Clock starts immediately when any task in Flow 1 is assigned to a user or team.
  - Dynamic Countdown: Live visual badge showing hours/days remaining before deadline.
  - Overdue Escalation: Automatically marks task as `Overdue` past deadline, logs an entry in `tabRemark Delay Log`, and sends escalation alerts to the assignee, department manager, and Admin/Director.
  - Admin/Director Authority: Users with `Admin` (Project Supreme) or `Director` roles customize default SLA durations for any step without touching code/doctypes. (Frappe's `System Manager` and `Administrator` retain framework supremacy and inherit this authority).

### `FR-018`: Multi-Stakeholder Notification Engine & Granular Toggles

- **Primary Actors:** Admin (Project Supreme), Director, System Manager.
- **Functional Screen:** `Solar Notification Settings` (Single DocType).
- **Core Controls & Validations:**
  - Granular Toggle Controls: Checkbox toggles enabling or disabling notifications individually per process, flow, step, and event type.
  - Multi-Recipient Rules:
    - Task Assignment $\rightarrow$ Assignee + Department Manager.
    - Task Overdue $\rightarrow$ Assignee + Department Manager + Admin / Director.
    - Material Request $\rightarrow$ Purchase Manager + Admin / Director.
    - Low Stock $\le$ Reorder Point $\rightarrow$ Purchase Manager + Store Manager + Admin / Director.
    - Purchase Milestones $\rightarrow$ Store / Accounts + Admin / Director.
    - Executive Oversight: Real-time broadcast to Admin/Director on all key events when toggled on.

### `FR-019`: Master Data Timings & Configurations

- **Primary Actors:** System Admin, Sales, Purchase, Store.
- **Core Controls & Validations:**
  - **Customer Master Timing:** Created strictly upon customer confirmation (Order Confirmation / Advance Payment / Sales Order creation).
  - **Supplier Master:** Maintains tax IDs, bank accounts, equipment categories, and dynamic Vendor Rating scores.
  - **Item Master:** Separated into dedicated tabs for **Stock** (valuation, serials, reorder levels), **Store** (bin location, handling), and **Purchase** (lead times, preferred suppliers, UOMs, inspection criteria).

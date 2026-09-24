# Phase 12: Sadbhav Solar EPC Technical Whitepaper

**Solar Project Archetypes, Dual-Flow Lifecycle Execution & Upgrade-Safe Architecture**  
_Source: Sadbhav Solar EPC Enterprise Architecture Suite_

---

## 1. Solar Project Archetypes & Tailored Dual-Flow Workflows

The `solar_module` ERP architecture accommodates diverse solar EPC operating models by dynamically adapting the dual-flow lifecycles:

### 1. Residential Rooftop (1 kW to 20 kW)

- **Velocity:** Fast-track 14-day cycle from Lead to Grid Synchronization.
- **Workflow Adaptations:**
  - **Stage 02 (Survey):** Mobile touch survey executed within 24h SLA capturing 6 mandatory photos and GPS coordinates.
  - **Stage 04 & 05 (Proposal & Advance):** Automated PM Surya Ghar central and state subsidy calculations; customer confirms with $> 20\%$ advance $\rightarrow$ **Instant creation of official Customer master**.
  - **Stage 07 & 08 (Dispatch & Installation):** Immediate material dispatch via Delivery Note from central store; 1-2 day rooftop installation tracked via mobile DPR.
  - **Stage 09 (Material Return):** Rapid post-installation reconciliation returning leftover cables and brackets to central store.
  - **Stage 10 (Liaisoning & Project Completion):** Fast-track DISCOM portal filing; 10-day post-install statutory countdown for bidirectional meter energization $\rightarrow$ **Grid sync marks formal Project Completion**.
  - **Stage 11 (O&M):** App-based generation monitoring and automated annual maintenance warranty alerts.

### 2. Commercial & Industrial (C&I) Rooftop (50 kW to 1000 kW)

- **Velocity:** 30 to 60-day execution cycle.
- **Workflow Adaptations:**
  - **Survey & Design:** Structural load audit, 3D shadow analysis, and high-voltage SLDs.
  - **Flow 2 Procurement:** Store raises Material Request; Purchase issues multi-vendor RFQs evaluated via the **Quotation Comparison Sheet**; **flexible GRN allows direct-to-site delivery** of mounting structures and high-power inverters.
  - **Dispatch & Zone Execution:** Phased Delivery Notes; multi-roof zone WBS with daily labor/civil DPRs and Megger test logs.
  - **Site Material Return:** Mandatory site inventory audit reconciling hundreds of items; surplus returned via `Stock Entry` (Material Return) before site sign-off.
  - **Liaisoning & Project Completion:** Phase 1 post-SO feasibility NOC; Phase 2 post-installation 10-day statutory CEIG safety inspection and Joint Meter Inspection (JMI) $\rightarrow$ **Completion formally closes Project**.
  - **Vendor Governance:** Collaborative payment monitoring by Purchase and Accounts; post-delivery Vendor Rating scorecard.

### 3. Ground-Mounted Utility Scale (1 MW to 50+ MW)

- **Velocity:** 3 to 9-month phased delivery.
- **Workflow Adaptations:**
  - **Flow 2 Procurement:** High-volume procurement with RFQ comparison sheets; **100% direct-to-site GRN** executed by site supervisors and purchase engineers with high-speed barcode scanning.
  - **Collaborative Payments:** Milestone-based vendor payment tracking (LC, advance, dispatch, site receipt, retention) co-managed by Purchase and Accounts.
  - **Execution & Reconciliation:** Granular block-by-block zone WBS; multi-stage site material returns reconciling structural steel, cables, and module spares.
  - **Liaisoning & Project Completion:** State transmission utility (STU) clearances, CEIG safety sign-off, bay charging, and COD certificate $\rightarrow$ **Transitions multi-crore Project to Completed**.
  - **O&M:** SCADA and cloud telemetry integration with string-level monitoring and predictive maintenance.

### 4. Floating Solar & Specialized Projects

- **Velocity:** Specialized multi-agency engineering and execution.
- **Workflow Adaptations:**
  - **Design & Procurement:** Bathymetric surveys, anchoring tension calculations, and pontoon layouts; specialized supplier quotations and rating.
  - **Liaisoning & Completion:** Water resource clearances, environmental NOCs, and grid evacuation sign-off marking project completion.

---

## 2. Upgrade-Safe Customization Architecture

To ensure the Sadbhav Solar EPC solution remains 100% upgrade-safe across future Frappe Framework and ERPNext releases:

1. **Zero Core Modifications:** All custom DocTypes, hooks, and services live exclusively within the custom app (`solar_module`). Core files in `frappe/`, `erpnext/`, and `hrms/` are never modified.
2. **Extensions via Version-Controlled Hooks:** Core DocTypes (`Lead`, `Sales Order`, `Delivery Note`, `Project`, `Purchase Order`, `Purchase Receipt`, `Item`) are cleanly extended using `custom_*` fields, doc_events hooks, and override classes.
3. **Decoupled Governance Engines:** The `Solar SLA Settings` and `Solar Notification Settings` single DocTypes provide declarative, no-code customization for Admins and Directors without requiring code deployments.
4. **Isolated REST/RPC API Namespace:** All custom endpoints are registered under `solar_module.api.*` with method whitelisting, CSRF protection, and IDOR permission checks.
5. **Decoupled Modern Frontend:** The Vue 3 Single Page Application builds into hashed static assets mounted cleanly via standard Frappe Web Templates (`/solar`), ensuring complete independence from Frappe Desk UI core changes.

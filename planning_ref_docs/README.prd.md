# Solar EPC Enterprise ERP — Master Blueprint & Specification Suite

This directory contains the authoritative 12-document architecture and specification suite for the **Sadbhav Solar EPC Enterprise ERP** platform (`solar_module`), aligned with the enterprise guidelines in [`architect_docs/`](../architect_docs).

The entire suite is standardized around **two synchronized enterprise lifecycles**, an enforced task-level SLA/TAT engine, a real-time notification matrix, and strict master data controls:

1. **Flow 1: Core Solar EPC Project Execution Lifecycle (11 Stages):**  
   `Lead` $\rightarrow$ `Survey` $\rightarrow$ `Design` $\rightarrow$ `Proposal` $\rightarrow$ `Advance Payment` $\rightarrow$ `Sales Order` (Customer creation & Early Liaisoning doc collection) $\rightarrow$ `Material Dispatch (Delivery Note)` $\rightarrow$ `Installation` $\rightarrow$ `Material Return to Store (Surplus Reconciliation)` $\rightarrow$ `Liaisoning & Synchronization (Actual Flow Countdown & Project Completion)` $\rightarrow$ `Operation & Maintenance (O&M)`.

2. **Flow 2: SCM, Store, Purchase & Vendor Procurement Lifecycle (8 Steps):**  
   `Material Request by Store to Purchase` $\rightarrow$ `Request for Quotation (RFQ) by Purchase to Supplier` $\rightarrow$ `Supplier Quotation (Comparative Evaluation Sheet)` $\rightarrow$ `Purchase Order (PO)` $\rightarrow$ `Purchase Receipt (GRN at Store OR Working Site by Store/Site/Purchase)` $\rightarrow$ `Purchase Invoice (3-Way Match by Account/Purchase)` $\rightarrow$ `Payment to Vendor Tracking/Monitoring (Joint Purchase & Accounts)` $\rightarrow$ `Vendor Rating System`.

---

## 🖥️ Unified Frontend Landing Architecture & Desk Access Governance

The platform implements a **decoupled Vue 3 / Frappe UI SPA wrapper** hosted at `/solar` as the universal operational entry point for all authenticated users, replacing standard Frappe Desk workspaces with an enterprise role-customized interface:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                AUTHENTICATED USER SESSION                                        │
└───────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
   [Root Desk Navigation]                     [Role-Based Application Entry]
   URL: `/desk` or `/app`                     URL: `/solar` (Vue 3 / Frappe UI SPA)
               │                                         │
               ▼                                         ▼
   ┌───────────────────────┐                  ┌─────────────────────────────────────────┐
   │ 403 REDIRECT GATEWAY  │                  │  UNIVERSAL DEFAULT LANDING WRAPPER     │
   │ Direct root /desk or  │ ──── Redirect ──▶│  Dynamically tailored by Frappe Role:   │
   │ /app is STRICTLY      │                  │  - Director: Executive Command Center   │
   │ RESTRICTED            │                  │  - Sales Rep: Lead & Survey Pipeline    │
   └───────────────────────┘                  │  - Surveyor: 24h Mobile Audit Queue     │
               │                              │  - Designer: PV Design & Dynamic BOM    │
               │ Deep Links                   │  - Store: Dispatch & Low Stock Reorder  │
               │ (Authorized Only)            │  - Accounts: Milestone & Payment Desk   │
               ▼                              └─────────────────────────────────────────┘
   ┌───────────────────────────────────┐
   │ PERMISSION-GATED DEEP ACCESS      │
   │ Access to `/desk/...` or          │
   │ `/app/...` permitted ONLY for     │
   │ specific doc/report deep links    │
   │ where user has explicit role perm │
   └───────────────────────────────────┘
```

### Core Architecture & Routing Rules:

1. **Universal Default Landing Wrapper (`/solar`):**
   - After authentication, **every user lands by default on `/solar`**.
   - The landing page is a **responsive Vue 3 + Frappe UI Single Page Application (SPA)** that dynamically adapts its layout, widgets, KPI tiles, and action drawers to the logged-in user's active role (`Director`, `Sales Executive`, `Site Survey User`, `Design Engineer`, `Store Manager`, `Accounts Officer`, etc.).
   - Role home pages in `hooks.py` (`role_home_page = {"*": "solar"}`) map all roles to `/solar`.

2. **Direct Root `/desk` and `/app` Access Restriction:**
   - **No direct access to generic `/desk` or `/app` workspaces.** Direct visits to `https://<domain>/desk` or `https://<domain>/app` are intercepted and automatically redirected to `/solar`.
   - Prevents cognitive overload, bypassing of domain verification stage-gates, and unstructured navigation through core Frappe modules.

3. **Role-Gated Deep-Link Access Permitted:**
   - Users **CAN access deep links** like `/desk/...` or `/app/...` (e.g. `/app/lead/<lead_name>`, `/app/site-survey/<id>`, `/app/quotation/<id>`, report builders, print formats, or document timelines) **as per their operational need and explicit Frappe role permissions only**.
   - If an unauthorized user attempts to open a deep link, Frappe's native Document Permission Controller (`doc.check_permission()`) intercepts and displays a standard `PermissionError`, safely guarding sensitive transactions.

4. **Technical Enforcement Stack:**
   - **Backend Hook (`before_request` / `website_route_rules`):** Intercepts top-level `/app` and `/desk` HTTP requests without document path arguments and returns a 302 redirect to `/solar`.
   - **Desk Client-Side Interceptor (`app_include_js`):** Intercepts client-side hash routing at the root level (`window.location.pathname === '/app'` or `window.location.pathname === '/desk'`) and redirects to `/solar`.
   - **Seamless Deep Links:** Quick-action buttons in the `/solar` Vue SPA provide deep links (e.g., `window.open('/app/lead/' + lead.name)`) enabling power users to perform advanced desk operations seamlessly when permitted.

---

## 📚 Master Document Catalog

|   #    | Specification Document                                                                           | Focus Area & Description                                                                                                                                                                       |
| :----: | :----------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **01** | [**01_PROJECT_FOUNDATION_MODEL.md**](./01_PROJECT_FOUNDATION_MODEL.md)                           | **Phase 1: PFM** — Dual-flow lifecycle definitions, 16 Business Capabilities (`BC-01` to `BC-16`), 15 Enterprise User Roles, Task SLA engine, Notification matrix, and Master Data lifecycles. |
| **02** | [**02_AS_IS_BUSINESS_PROCESS.md**](./02_AS_IS_BUSINESS_PROCESS.md)                               | **Phase 2: As-Is BPD** — Current operational baseline, dispatch/return scrap risks, informal procurement silos, vendor disputes, missing SLA countdowns, and management alert blindspots.      |
| **03** | [**03_TO_BE_BUSINESS_PROCESS.md**](./03_TO_BE_BUSINESS_PROCESS.md)                               | **Phase 3: To-Be BPD** — Target operating model, 11-stage project pipeline, 8-step procurement cycle, 9 enforced verification stage-gates, and end-to-end document transformation.             |
| **04** | [**04_GAP_ANALYSIS_FIT_GAP.md**](./04_GAP_ANALYSIS_FIT_GAP.md)                                   | **Phase 4: Gap Analysis** — Fit-gap matrix across 18 enterprise domains, high-priority gaps, and custom ERP treatment strategies for dispatch, site returns, RFQ comparison, and SLA timers.   |
| **05** | [**05_BUSINESS_REQUIREMENTS_DOCUMENT.md**](./05_BUSINESS_REQUIREMENTS_DOCUMENT.md)               | **Phase 5: BRD** — Strategic scaling goals and 18 Master Business Requirements (`BR-001` to `BR-018`) encompassing both operational lifecycles and administrative governance.                  |
| **06** | [**06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md**](./06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md) | **Phase 6: FRS** — Screen controls, field rules, actors, stage-gates, and validations across 19 functional specifications (`FR-001` to `FR-019`).                                              |
| **07** | [**07_SOFTWARE_REQUIREMENTS_SPECIFICATION.md**](./07_SOFTWARE_REQUIREMENTS_SPECIFICATION.md)     | **Phase 7: SRS** — Multi-tier system architecture, background lifecycle daemons (SLA, Low Stock, Liaisoning, Telemetry), notification broker, and non-functional specifications.               |
| **08** | [**08_DATABASE_DESIGN_DOCUMENT.md**](./08_DATABASE_DESIGN_DOCUMENT.md)                           | **Phase 8: Database Design (3NF)** — Relational entity schema across 9 enterprise domains (`COR`, `CRM`, `ENG`, `FIN`, `LOG`, `PRJ`, `SCM`, `CMP`, `OM`).                                      |
| **09** | [**09_API_DESIGN_AND_INTEGRATIONS.md**](./09_API_DESIGN_AND_INTEGRATIONS.md)                     | **Phase 9: API Design** — Whitelisted REST/RPC endpoints (`solar_module.api.*`) and 6 third-party integration pipelines (DISCOM, IoT Inverter, Banking, WhatsApp, GIS, PM Surya Ghar).         |
| **10** | [**10_UI_UX_SPECIFICATION.md**](./10_UI_UX_SPECIFICATION.md)                                     | **Phase 10: UI/UX Spec** — Layout blueprints, component standards, and 21 responsive application screens across Flow 1, Flow 2, and Admin governance.                                          |
| **11** | [**11_MODULE_FUNCTIONAL_DOCUMENTATION.md**](./11_MODULE_FUNCTIONAL_DOCUMENTATION.md)             | **Phase 11: Module SOPs** — Detailed standard operating procedures for modules `MOD-01` through `MOD-19`.                                                                                      |
| **12** | [**12_GETMYERP_SOLAR_EPC_WHITEPAPER.md**](./12_GETMYERP_SOLAR_EPC_WHITEPAPER.md)                 | **Phase 12: Whitepaper** — Solar project archetypes (Residential Rooftop, C&I, Utility, Floating), site material return discipline, and upgrade-safe design principles.                        |

---

## 🎯 Master Traceability Matrix

### Flow 1: Core Solar EPC Project Execution Lifecycle

```
[Lifecycle Stage]             [BRD Requirement]            [FRS Specification]            [Database 3NF Entities]               [UI / Custom Screens]
01. Lead Capture              BR-001 (Lead Ingestion)       FR-001 (Pipeline & Dedup)      tabLead / tabCRM Lead                 /solar/leads & /new
02. Technical Site Survey     BR-002 (24h Technical Audit)  FR-002 (Audit & 6 Photos)      tabSite Survey & Doc Table            Site Survey Mobile UI (24h SLA)
03. Solar PV Engineering      BR-003 (Design & BOM)         FR-003 (CAD, SLD & BOM)        tabSite Survey Design File / BOM      Design Workbench
04. Commercial Proposal       BR-004 (Proposal & Subsidy)   FR-004 (Dynamic Proposal)      tabProposal / tabProposal Item        Proposal Builder (PM Surya Ghar)
05. Advance & Customer Gate   BR-005 (Advance Gate)         FR-005 (Financial Clearance)   tabSales Order / tabCustomer          Advance Clear & Customer Modal
06. Sales Order Anchor        BR-006 (Project Inception)    FR-006 (SO Baseline Lock)      tabSales Order                        Sales Order Hub
07. Material Dispatch         BR-007 (Delivery Note)        FR-007 (Serialized Dispatch)   tabDelivery Note / tabSerial Bundle   Delivery Note Screen
08. Installation Execution    BR-008 (Zone Execution)       FR-008 (Zone DPR Logs)         tabProject / tabTask / tabDPR         Mobile DPR Entry
09. Material Return to Store  BR-009 (Surplus Return)       FR-009 (Site Reconciliation)   tabStock Entry (Material Return)      Site Return & Reconcile Screen
10. Liaisoning & Grid Sync    BR-010 (Dual-Timing Sync)     FR-010 (10d SLA & Project End) tabLiaisoning And Synchronization     Dual-Timing Kanban (Project End)
11. Lifecycle O&M             BR-011 (Asset Register)       FR-011 (Asset & Telemetry)     tabSolar Asset Register / Maint Visit O&M Asset Portal & IoT View
```

### Flow 2: SCM, Store, Purchase & Vendor Governance Lifecycle

```
[Procurement Step]            [BRD Requirement]            [FRS Specification]            [Database 3NF Entities]               [UI / Custom Screens]
01. Material Request by Store BR-012 (Store Requisitions)  FR-012 (MR & Low Stock Alert)  tabMaterial Request                   Store Material Request Desk
02. Request for Quotation     BR-013 (Supplier RFQ)         FR-013 (RFQ Dispatch)          tabRequest for Quotation              RFQ Creation Screen
03. Supplier Quote Comparison BR-013 (Comparative Matrix)   FR-013 (Quote Comparison Sheet)tabSupplier Quotation / tabComparison Quotation Comparison Matrix
04. Purchase Order Placement  BR-013 (PO Authorization)     FR-014 (PO Release)            tabPurchase Order                     Purchase Order Screen
05. Purchase Receipt (GRN)    BR-014 (Store/Site GRN)       FR-014 (Flexible GRN Location) tabPurchase Receipt (Store/Site)     Multi-Location GRN Scanner
06. Purchase Invoice 3-Way    BR-015 (3-Way Matching)       FR-015 (PI Verification)       tabPurchase Invoice                   Purchase Invoice Screen
07. Joint Payment Tracking    BR-015 (Payment Monitoring)   FR-015 (Collaborative Desk)    tabPayment Entry / Workbench          Vendor Payment Workbench
08. Vendor Performance Rating BR-016 (Vendor Rating)        FR-016 (Supplier Scorecard)    tabVendor Rating                      Vendor Rating Scorecard
```

### Cross-Flow Governance & Administration

```
[Governance Dimension]        [BRD Requirement]            [FRS Specification]            [Database 3NF Entities]               [UI / Custom Screens]
Task SLA / TAT Engine         BR-017 (Task SLA Clock)       FR-017 (SLA & Overdue Log)     tabSolar SLA Settings / Task SLA Log  Admin SLA Customization Screen
Multi-Tier Notification EngineBR-018 (Notification Matrix)  FR-018 (Toggle Alerts Engine)  tabSolar Notification Settings / Log  Admin Notification Toggle Screen
Master Data Timings           BR-005, BR-013, BR-014        FR-019 (Master Timings)        tabCustomer, tabSupplier, tabItem     Customer/Supplier/Item Desks
```

---

## 🚀 Enterprise Step Implementation Plans

For engineering execution, each lifecycle stage from Flow 1 and Flow 2 is deconstructed into a standalone, exhaustive specification adhering to the **Canonical 9-Section Step Planning Blueprint** defined in [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md).

All lifecycle specifications reside in the dedicated [`step_plans/`](../step_plans/) directory:

- [**Step Plans Directory Index (`step_plans/README.md`)**](../step_plans/README.md)
- [**Stage 01: Lead Management Implementation Specification (`step_plans/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.md`)**](../step_plans/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.md)

> [!NOTE]
> **Enterprise Role Nomenclature & Authority Hierarchy Standards:**
>
> 1. In accordance with the enterprise naming convention established in [`step_plans/README.md`](../step_plans/README.md#5-enterprise-persona--role-naming-standard-zero-user-suffix-rule) and [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md), all specifications strictly avoid generic `User` suffixes (e.g. `Lead User`, `Sales User`, `Survey User`) in favor of descriptive functional titles such as `Lead Representative`, `Sales Representative`, `Survey Engineer`, `Survey Assistant`, `Solar Design Engineer`, `Project Engineer`, and `Store Assistant`.
> 2. **Supreme Authority Hierarchy:** Frappe Framework's native `Administrator` and `System Manager` sit at the apex of system authority (supreme over `Admin`, possessing all developer tools and code/schema access plus whatever access `Admin` has). **`Admin`** is the dedicated **Project-level supreme operational command role**, possessing complete business operational command across all lifecycles and governance settings (`Solar SLA Settings`, `Solar Notification Settings`), but strictly restricted from code, DocTypes, and server scripts.

# Solar EPC Enterprise ERP — Master Step Planning Suite

**Directory:** `step_plans/`  
**Governing Architecture:** [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md)  
**Enterprise Reference:** [`planning_ref_docs/README.prd.md`](../planning_ref_docs/README.prd.md)

---

## 1. Directory Purpose & Architectural Governance

This directory houses the **canonical, production-ready implementation plans** for every discrete lifecycle stage of the **Sadbhav Solar EPC Enterprise ERP** platform (`solar_module`).

In strict alignment with **"The Architect Mind"** ([`architect_docs/`](../architect_docs)), every specification in this directory adheres without exception to the **Canonical 9-Section Step Planning Blueprint**:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             THE CANONICAL 9-SECTION STEP BLUEPRINT                               │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Section 1: Step Scope, Objectives & Context Traceability (BRD/FRS/PFM Cross-Reference)          │
│ Section 2: Stakeholders, Enterprise Actors & HRMS Role Mapping (Role Hierarchy & Permissions)    │
│ Section 3: Relational Schema & 3NF Data Dictionary (Core Extensions, DocTypes, Child Tables)    │
│ Section 4: State Machine, Verification Gates & SLA Engine (Mermaid Flow, TAT, Delay Logs)        │
│ Section 5: Controller Logic, Domain Services & Whitelisted APIs (SOLID Decoupled Architecture)   │
│ Section 6: Frontend UI/UX Specification (Vue 3 / Frappe UI SPA `/solar` + Controlled Desk View)  │
│ Section 7: Cross-App Integration Touchpoints (ERPNext Core, CRM, HRMS, External Portals)        │
│ Section 8: Automated Testing & QA Criteria (IntegrationTestCase, Zero-Commit Rule)              │
│ Section 9: Operational SOP, Error Resolution & Runbook (User SOP & L3 DevOps Runbook)            │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Universal Frontend Landing & Routing Contract

All step specifications documented in this directory operate under the **Unified Frontend Landing Architecture**:

1. **Universal Landing Wrapper (`/solar`):**  
   Every authenticated user lands by default on `/solar` (Vue 3 + Frappe UI SPA), customized dynamically by role.
2. **Direct Root `/desk` and `/app` Lockout:**  
   Direct access to top-level Frappe Desk workspaces (`/desk` or `/app`) is intercepted and redirected to `/solar`.
3. **Permission-Gated Deep Linking:**  
   Users access granular Frappe Desk forms and reports (e.g. `/app/lead/<id>`, `/app/site-survey/<id>`, `/desk/...`) exclusively via deep links and strictly within their authorized Frappe role permissions.

---

## 3. Master Lifecycle Planning Catalog

### Flow 1: Core Solar EPC Project Execution Lifecycle (11 Stages)

| Stage # | Specification Document                                                                                                       | Stage Name & Scope                                                                                                                                                                                                                                                                                                                                 |         Status          |
| :-----: | :--------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------: |
| **01**  | [**`STEP_01_LEAD_MANAGEMENT_SPECIFICATION.md`**](./STEP_01_LEAD_MANAGEMENT_SPECIFICATION.md)                                 | **Lead Capture, Deduplication & Survey Scheduling:** Omnichannel ingestion, 10-digit mobile verification, cross-DocType deduplication, 2h response SLA, automatic `Site Survey` link.                                                                                                                                                              | **Ready for Execution** |
| **02**  | [**`STEP_02_SITE_SURVEY_SPECIFICATION.md`**](./STEP_02_SITE_SURVEY_SPECIFICATION.md)                                         | **Technical Site Survey & Audit:** Mobile touch capture, GPS lock, 6 mandatory photo checklist rows, 24h survey completion SLA, offline-first IndexedDB sync.                                                                                                                                                                                      | **Ready for Execution** |
| **03**  | [**`STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.md`**](./STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.md)     | **Survey Engineering Design & Dynamic BOM Freeze:** Standalone submittable DocType (`Survey Engineering Design`), AutoCAD/SLD versioning (25MB limit), parametric cable voltage drop math (≤ 2%), `custom_quot_bom` explosion & SHA-256 baseline freeze.                                                                                           | **Ready for Execution** |
| **04**  | [**`STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.md`**](./STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.md)                               | **Proposal & Subsidy Engine:** Repetitive multi-proposal modeling, two-tier pre-fill from Survey & Design, configurable 70:30 solar GST, PM Surya Ghar central/state subsidies, gross margin floor governance, and advance clearance gate.                                                                                                         | **Ready for Execution** |
| **05**  | [**`STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.md`**](./STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.md)     | **Advance Clearance & Customer Master Inception:** Admin-governed $\ge 50\%$ advance verification gate, programmatic `Customer` master creation.                                                                                                                                                                                                   | **Ready for Execution** |
| **06**  | [**`STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.md`**](./STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.md)                       | **Sales Order Anchor & Downstream Spawning:** Commercial baseline freeze, automatic `Project` WBS container, Store Manager delivery task & Phase 1 Liaisoning creation.                                                                                                                                                                            | **Ready for Execution** |
| **07**  | [**`STEP_07_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.md`**](./STEP_07_MATERIAL_DISPATCH_DELIVERY_NOTE_SPECIFICATION.md) | **Material Dispatch Logistics:** ERPNext `Delivery Note`, 100% 2D barcode serial tracking via Frappe v15 SABB, vehicle & E-Way Bill enforcement, pre-dispatch quality checklist, 48h store dispatch SLA, and closed-loop digital Proof of Delivery (POD).                                                                                          | **Ready for Execution** |
| **08**  | [**`STEP_08_INSTALLATION_ZONE_DPR_SPECIFICATION.md`**](./STEP_08_INSTALLATION_ZONE_DPR_SPECIFICATION.md)                     | **Installation Execution & Zone DPR:** Multi-zone structural/civil/electrical tasks, mobile Daily Progress Reports (DPR), IEC 62446-1 pre-commissioning Megger/Voc testing gate, and downstream Stage 09 / 10B automated handoff.                                                                                                                  | **Ready for Execution** |
| **09**  | `STEP_09_MATERIAL_RETURN_RECONCILIATION_SPECIFICATION.md`                                                                    | **Site Material Return & Surplus Reconciliation:** Dispatched vs installed balance audit, automated `Stock Entry` (Material Return).                                                                                                                                                                                                               |         Planned         |
| **10**  | [**`STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.md`**](./STEP_10_LIAISONING_GRID_SYNC_SPECIFICATION.md)                       | **Liaisoning, Statutory Inspection & Grid Sync:** Phase 1 DISCOM filings, Phase 2 post-install 10-day SLA countdown, CEIG/JMI, formal Project Completion.                                                                                                                                                                                          | **Ready for Execution** |
| **11**  | [**`STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.md`**](./STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.md)           | **On-Demand Solar Service, Incident-Driven O&M & Warranty Lifecycle:** Independent post-project lifecycle, omnichannel service intake, two-track warranty governance (In-Warranty / Free vs Out-of-Warranty / Chargeable), mobile technician GPS check-in, closed-loop resolution, ERPNext spare parts stock/billing, and lifetime service ledger. | **Ready for Execution** |

---

### Flow 2: SCM, Store, Purchase & Vendor Procurement Lifecycle (8 Steps)

| Step # | Specification Document                                                                                                         | Step Name & Scope                                                                                                                                                                             |         Status          |
| :----: | :----------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------: | --- |
| **01** | [**`STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md`**](./STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md) | **Store Requisitions & Low Stock Monitoring:** Material Request creation, safety stock reorder point monitoring, dual-trigger demand model, true pipeline solvency math, and tiered SLA.      | **Ready for Execution** |
| **02** | [**`STEP_13_SUPPLIER_RFQ_SPECIFICATION.md`**](./STEP_13_SUPPLIER_RFQ_SPECIFICATION.md)                                         | **Supplier Request for Quotation (RFQ):** Multi-supplier dispatch, item specification attachment, tokenized portal submission, sealed bids.                                                   | **Ready for Execution** |
| **03** | [**`STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.md`**](./STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.md)           | **Supplier Quotation Comparative Evaluation:** Side-by-side comparative sheet, landed cost normalization, rate/lead-time/rating scoring, Non-L1 governance gate.                              | **Ready for Execution** |
| **04** | [**`STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md`**](./STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md)         | **Purchase Order Placement:** 4-tier authorization gates, solar milestone terms, multi-location delivery routing, and 24h/48h SLA engine.                                                     | **Ready for Execution** |
| **05** | [**`STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md`**](./STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md)                         | **Multi-Location Barcode GRN:** Tri-party receipt (Store, Site, Purchase), Admin-controllable barcode toggle, automatic Store/Site stock update & custody gates.                              | **Ready for Execution** |
| **06** | [**`STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.md`**](./STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.md)           | **Purchase Invoicing & 3-Way Match:** PO vs GRN vs PI rate/qty validation, Admin-governed entry authorization (Account, Store, Purchase).                                                     | **Ready for Execution** |
| **07** | [**`STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.md`**](./STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.md)                 | **Joint Vendor Payment Monitoring:** Collaborative Purchase & Accounts workbench, dual-cadence notifications (T-1 & T-0), instant settlement alert to Purchase, milestone disbursement gates. | **Ready for Execution** |     |
| **08** | [**`STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.md`**](./STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.md)                   | **Vendor Performance Rating Governance:** 4-factor scorecard (OTD, Quality, Price, Service) updating vendor tiers, upstream RFQ/Matrix feedback.                                              | **Ready for Execution** |

---

## 4. Authoring & Contribution Guidelines

When creating specifications for subsequent stages:

1. Follow the file naming convention: `STEP_<NN>_<UPPERCASE_STAGE_NAME>_SPECIFICATION.md`.
2. Do not omit any of the 9 mandatory sections.
3. Keep business math and domain logic decoupled into domain service classes.
4. Ensure all database extensions use explicit fieldtypes and index declarations.
5. Guarantee 100% test coverage with zero database commits in unit tests.
6. Enforce the **Zero "User" Suffix Rule** across all role, persona, and permission specifications.
7. Enforce the **Supreme Command (`Admin`) vs. Developer (`System Manager`) Role Separation Standard**.

---

## 5. Enterprise Persona & Role Naming Standard (Zero "User" Suffix Rule)

To maintain rigorous enterprise engineering standards and eliminate ambiguous, developer-centric nomenclature, **never use the generic `User` suffix** (such as `Lead User`, `Sales User`, `Survey User`, `Site User`, `Project User`, `Store User`) when specifying personas, Frappe system roles, or operational designations across any lifecycle step.

### Mandatory Role Naming Nomenclature:

| Operational Domain          | Deprecated Role Pattern (Prohibited) | Approved Enterprise Role Standard | Approved Functional Variants                                  |
| :-------------------------- | :----------------------------------- | :-------------------------------- | :------------------------------------------------------------ |
| **Lead Management**         | `Lead User`                          | **`Lead Representative`**         | `Inside Sales Representative`, `Lead Assistant`               |
| **Sales & Commercial**      | `Sales User`                         | **`Sales Representative`**        | `Sales Executive`, `Area Sales Manager`, `Commercial Officer` |
| **Site Survey & Audit**     | `Site Survey User` / `Survey User`   | **`Survey Engineer`**             | `Site Survey Auditor`, `Survey Assistant`                     |
| **PV Engineering & Design** | `Design User`                        | **`Design Engineer`**             | `Design Manager`, `CAD Design Specialist`                     |
| **Order & Baseline**        | `Sales Order User`                   | **`Commercial Officer`**          | `Sales Operations Executive`                                  |
| **Material Dispatch**       | -                                    | **`Store Manager`**               | `Store Assistant`                                             |
| **Site Execution (WBS)**    | `Project User` / `Site User`         | **`Project Engineer`**            | `Site Supervisor`, `Civil/Electrical Site Engineer`           |
| **Material Return**         | `Reconciliation User`                | **`Store Assistant`**             | `Site Auditor`, `Inventory Reconciler`                        |
| **Liaisoning & Grid Sync**  | `Liaisoning User`                    | **`Liaisoning Officer`**          | `Statutory Compliance Representative`                         |
| **O&M & Telemetry**         | `O&M User`                           | **`O&M Service Engineer`**        | `Solar Telemetry Specialist`, `AMC Technician`                |
| **Store & Inventory**       | `Store User`                         | **`Store Assistant`**             | `Store Manager`, `Warehouse Supervisor`                       |
| **Procurement & SCM**       | `Purchase User`                      | **`Procurement Representative`**  | `Purchase Executive`, `Purchase Manager`                      |
| **Finance & Accounts**      | `Accounts User`                      | **`Accounts Assistant`**          | `Accounts Officer`, `Finance Lead`                            |
| **Supplier Evaluation**     | `Vendor User`                        | **`Vendor Rating Auditor`**       | `Quality & SCM Auditor`                                       |

All subsequent step specifications (`STEP_02` through `STEP_19`) and any future planning documents must strictly adopt this nomenclature.

---

## 6. Enterprise Authority Hierarchy: Administrator $\rightarrow$ System Manager $\rightarrow$ Admin (Project Supreme)

To guarantee clean separation between enterprise business governance and technical software plumbing while preserving Frappe Framework's intended core architecture:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             ENTERPRISE AUTHORITY HIERARCHY ARCHITECTURE                          │
├──────────────────────────────────────────────────┬───────────────────────────────────────────────┤
│    `System Manager` (Framework Supreme / Dev)    │       `Admin` (Project / Solar Supreme)       │
│           [Technical & Root Realm]               │       [Business & Operational Realm]          │
├──────────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ ✔ Supreme over `Admin` (Frappe native hierarchy) │ ✔ Supreme command over all Project operations │
│ ✔ Possesses WHATEVER access `Admin` has          │ ✔ Access to all business documents/workflows  │
│ ✔ Access to Python source code & git repos       │ ✔ Manage `Solar SLA Settings` (hours/days)    │
│ ✔ Manage DocType schemas & Custom Fields         │ ✔ Manage `Solar Notification Settings`        │
│ ✔ Access to Server Scripts & Client Scripts      │ ✔ Authorize stage overrides & delay reasons   │
│ ✔ Frappe Developer Mode & System Console         │ ✔ Executive command dashboards & audits       │
│ ✔ Bench CLI, migrations & Redis worker queues    │ ✖ RESTRICTED from source code & server scripts│
│ ✔ Root superuser / developer administration      │ ✖ RESTRICTED from DocType schema modifications│
└──────────────────────────────────────────────────┴───────────────────────────────────────────────┘
```

1. **`Administrator` & `System Manager` (Framework Supreme / Technical Development Realm):**
   - Frappe's native `Administrator` and `System Manager` sit at the apex of the system hierarchy.
   - **Supreme over `Admin`:** Possesses whatever operational and settings access `Admin` has, **plus** full technical control over DocType builders, source code, Server Scripts, Client Scripts, Custom Fields, Frappe Developer Mode, Bench CLI commands, and database administration.
   - Reserved strictly for developers, technical architects, and infrastructure DevOps engineers.

2. **`Admin` (Project / Solar EPC Level Supreme Command):**
   - Introduced specifically for **project-level operational supremacy**.
   - Holds supreme authority over all business operations across Flow 1 (Stages 01–11) and Flow 2 (Steps 01–08), encompassing everything accessible to any or all operational roles (`Lead Representative`, `Sales Representative`, `Survey Engineer`, `Solar Design Engineer`, `Store Assistant`, `Accounts Assistant`, `Project Engineer`, `Liaisoning Officer`).
   - Holds exclusive business authority to customize and manage operational governance: `Solar SLA Settings`, `Solar Notification Settings`, delay approvals, and escalation overrides.
   - **Clean Business Boundary:** Because operational leadership does not require technical code or schema maintenance, `Admin` is strictly restricted from editing DocTypes, writing server/client scripts, and accessing underlying code.

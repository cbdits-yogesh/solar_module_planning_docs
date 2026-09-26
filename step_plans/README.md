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

### Foundation Layer: Enterprise Role, Permission & Security Substrate (Step 00)

| Step # | Specification Document                                                                                                               | Scope & Objectives                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |         Status          |
| :----: | :----------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------: |
| **00** | [**`STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.md`**](./STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.md) | **Enterprise Role, Permission & Security Foundation:** Canonical 22 Roles (10 Frontline + 10 Supervisory + 2 Apex), 11 Department Role Profiles, Managerial Authority Inheritance (`RoleInheritanceService`), Stage-Forward Immutability Lock (`StageForwardLockService`), Junior Cancel/Amend Workflow (`Solar Cancellation Request`), Admin Deletion Guard (`AdminAuditService` -> `Solar Deletion Audit Log`), Atomic Cascading Purge (`CascadePurgeService`), Stage-Gated RLS (`StageGatedRLSService`), and Base Controller Mixin (`StageSecuredDocument`). | **Ready for Execution** |

---

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

## 5. Enterprise Persona & Role Naming Standard (Symmetric Two-Tier Architecture — ADR-020)

In strict accordance with [`ADR-020`](../docs/decisions/ADR-020-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md) and the **Zero "User" Suffix Rule**, all personas, Frappe system roles, and operational designations are standardized around a **Symmetric Two-Tier Departmental Hierarchy** (Frontline Operational Role + Supervisory Managerial Role), with complete elimination of redundant and deprecated roles.

### Mandatory Role Naming Nomenclature & Departmental Mapping:

| Operational Domain          | Deprecated Role Pattern (Prohibited)                         | Approved Frontline Role(s)                    | Approved Managerial Role | Core Operational Scope                                                          |
| :-------------------------- | :----------------------------------------------------------- | :-------------------------------------------- | :----------------------- | :------------------------------------------------------------------------------ |
| **Sales & Lead Ingestion**  | `Lead Representative`, `Lead User`, `Inside Sales Rep`       | **`Sales Representative`**                    | **`Sales Manager`**      | Stage 01 Lead ingestion, 10-digit mobile deduplication, 2h SLA, survey booking. |
| **Site Survey & Audit**     | `Site Survey User`, `Survey User`, `Site Survey Auditor`     | **`Survey Engineer`**                         | **`Survey Manager`**     | Stage 02 Mobile technical audit, GPS lock, 6 mandatory photos, feasibility.     |
| **PV Engineering & Design** | `Design User`, `CAD Design Specialist`                       | **`Design Engineer`**                         | **`Design Manager`**     | Stage 03 PV sizing, CAD/SLD, voltage drop math ($\le 2\%$), dynamic BOM freeze. |
| **CRM & Proposals**         | `Sales Representative` (for quotes), `Commercial Officer`    | **`CRM Representative`**                      | **`CRM Manager`**        | Stage 04 Dynamic quotation modeling, 70:30 GST, PM Surya Ghar subsidy pre-fill. |
| **Finance & Accounts**      | `Accounts Officer`, `Accounts User`, `Commercial Officer`    | **`Accounts Assistant`**                      | **`Accounts Manager`**   | Stage 05 Advance clearance ($\ge 20\%$), Step 15/17 3-way match, Step 18 pay.   |
| **Site Execution (WBS)**    | `Commercial Officer`, `Project User`, `Site User`            | **`Site Supervisor`**, **`Project Engineer`** | **`Project Manager`**    | Stages 06–09 WBS baseline, mobile DPR, pre-comm Megger testing, site returns.   |
| **Store & Logistics**       | `Store User`, `Inventory Reconciler`                         | **`Store Assistant`**                         | **`Store Manager`**      | Stage 08 2D barcode dispatch, Step 12 MRs, Step 16 central warehouse GRN.       |
| **Liaisoning & Grid Sync**  | `Liaisoning Officer`, `Liaisoning User`                      | **`Liaisoning Representative`**               | **`Liaisoning Manager`** | Stage 10 DISCOM filings, CEIG/JMI statutory audit, net meter sync, COD closure. |
| **Procurement & SCM**       | `Purchase User`, `Vendor Rating Auditor`, `Quality Engineer` | **`Purchase Assistant`**                      | **`Purchase Manager`**   | Steps 12–19 RFQ dispatch, comparison matrix, PO release, vendor rating.         |
| **O&M & Telemetry**         | `O&M User`, `AMC Technician`                                 | **`O&M Service Engineer`**                    | **`O&M Manager`**        | Stage 11 Incident intake, mobile GPS check-in, warranty claims, asset ledger.   |

All subsequent step specifications (`STEP_01` through `STEP_19`) strictly adhere to this nomenclature.

---

## 6. Enterprise Authority Hierarchy & Operational Safeguards (ADR-020)

To guarantee clean separation between enterprise business governance and technical software plumbing while preserving Frappe Framework's native architecture:

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
│ ✔ Bench CLI, migrations & Redis worker queues    │ ✔ Atomic Cascading Purge (`CascadePurgeService`│
│ ✔ Root superuser / developer administration      │ ✖ RESTRICTED from source code & server scripts│
│                                                  │ ✖ RESTRICTED from DocType schema modifications│
└──────────────────────────────────────────────────┴───────────────────────────────────────────────┘
```

### Core Operational Governance Rules:

1. **Managerial Full-Authority Inheritance:**  
   Department **`Managers`** strictly inherit 100% of the operational capabilities, permissions, and submit actions of their frontline subordinates (`Representative`, `Engineer`, `Assistant`, `Supervisor`).

2. **Stage-Forward Lock & Two-Phase Amend/Cancel Protocol:**
   - **The Lock:** Once a transaction has progressed to the next downstream stage/step, upstream documents are **permanently locked against cancel and amend**.
   - **Manager Direct Action (Pre-Forward):** Department Managers can cancel or amend their department's documents prior to downstream progression with a mandatory written justification remark.
   - **Junior Request-for-Approval Flow:** Frontline staff cannot unilaterally cancel or amend; they submit an Amendment/Cancellation Request with a reason to their Manager. If the process has already moved to the next step, raising the request is blocked entirely.

3. **Admin Deletion Safeguards & Atomic Cascading Purge:**
   - **Downstream Dependency Warning:** System warns Admin when dependencies exist. Direct deletion is restricted until active downstream records are resolved.
   - **Atomic Cascading Purge (`CascadePurgeService`):** For total aborts, Admin can trigger a cascading purge requiring password re-authentication, $\ge 40$ chars justification, reverse-topological deletion, and full snapshot logging in `tabSolar Deletion Audit Log`.

4. **Step 15 Refined Purchase Order Authorization Matrix:**
   - Tier 1 (< ₹50,000): `Purchase Manager` ONLY.
   - Tier 2 (₹50,000 to ₹5,00,000): Single active role configured by `Admin` in `Solar SCM Settings` (`Purchase Manager`, `Accounts Manager`, or `Admin`).
   - Tier 3 (₹5,00,000 to ₹25,00,000) & Tier 4 (> ₹25,00,000): Exclusive authority of `Admin`.

5. **Stage-Gated Row-Level Security (RLS):**
   - Frontline juniors access assigned previous stage records (**Read-Only**) + assigned current stage records (**Read/Write/Create**).
   - Department Managers access all previous stage records (**Read-Only**) + all current stage records across their department (**Read/Write/Submit/Approve**).

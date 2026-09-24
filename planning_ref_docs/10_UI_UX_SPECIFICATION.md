# Phase 10: UI/UX Specification Document

**Layout Blueprints, Component Standards & Responsive Screen Rules Across Dual Lifecycles**  
_Source: Sadbhav Solar EPC Enterprise Architecture Suite_

---

## 1. Design System & Frontend Architecture

- **Framework:** Vue 3.4+ (Composition API `<script setup lang="ts">`), Vite, Tailwind CSS.
- **Tokens:** Frappe UI design tokens (Slate neutral palette, Solar Primary Amber `#F59E0B`/`#D97706`, Emerald success `#10B981`, Red alert `#EF4444`, Indigo secondary `#6366F1`).
- **Visual Standards:** Glassmorphism cards (`backdrop-blur-md`, 1px subtle border `border-slate-200/80`), high-contrast accessible typography, touch-friendly hit areas ($\ge 44 \times 44$ px), and responsive flex grids.

### 1.1 Universal Landing Page Wrapper (`/solar`) & Routing Governance

- **Default Application Destination:** The Vue 3 SPA at `/solar` serves as the universal landing destination for **all** authenticated users upon login, replacing Frappe Desk workspaces.
- **Dynamic Role-Based Customization:** The `/solar` landing shell inspects `frappe.session.user` roles and mounts a customized dashboard layout:
  - _Director / Executive:_ Strategic MW pipeline, high-level SLA health, financial collections, and procurement bottlenecks.
  - _Sales Executive:_ My leads, 2h response SLA countdowns, rapid lead onboarding drawer, quotation statuses.
  - _Survey Engineer:_ Assigned site surveys, GPS-assisted route map, 24h technical audit countdown.
  - _Design Engineer:_ Pending engineering sizing queue, dynamic BOM generators, CAD repository.
  - _Store Manager:_ Dispatch backlog, pending material requests, low-stock reorder warnings, GRN scanner launcher.
  - _Accounts Officer:_ Advance payment clearance queue, joint vendor payment workbench, 3-way match verification.
- **Root Desk/App Access Boundary:**
  - Direct root access to `/desk` or `/app` is strictly disabled. Requests to `https://<domain>/desk` or `https://<domain>/app` automatically 302-redirect to `/solar`.
  - **Permission-Gated Deep Linking:** Deep links (e.g. `/app/lead/<lead-id>`, `/app/site-survey/<id>`, `/desk/...`) remain accessible only when a user possesses explicit read/write permissions for that specific entity. Any attempt to navigate to unauthorized deep links triggers a standard `PermissionError`.

---

## 2. Core Application Screens (21 Screen Blueprints Across Dual Lifecycles)

### Flow 1: Solar EPC Project Execution Screens

1. **Portal Home Dashboard (`/solar`):** Central command dashboard with KPI metrics for Pipeline MW, Active Surveys, Pending Proposals, Work in Progress (WIP), Dispatched Deliveries, Overdue Tasks, and Commissioned Assets.
2. **Lead Directory & Search (`/solar/leads`):** Searchable, filterable directory with real-time stage badges, SLA countdown badges, territory filters, and one-click New Lead modal.
3. **Lead Detail & 11-Stage Lifecycle Stepper (`/solar/leads/:id`):** Visual `LeadProgressBar` stepper displaying completion timestamps and active badges across all 11 stages with linked document drawer.
4. **Lead Onboarding Form (`/solar/leads/new`):** Clean sales entry form with real-time phone number deduplication checks.
5. **Site Survey Mobile Touch Form:** Touch-optimized field entry with GPS lock button, 24h SLA countdown timer, and inline camera triggers with completion indicators for the 6 mandatory photo checklist rows (`Inverter`, `Earthing 1-3`, `LT Panel`, `Meter Board`, `Roof Panorama`, `Shadow Obstacles`).
6. **Solar PV Engineering Design Workbench:** Split-pane CAD/SLD repository, parametric cable math sliders, and dynamic BOM explosion table (`custom_quot_bom`).
7. **Dynamic Proposal & Subsidy Builder:** Interactive capacity slider, live component pricing, PM Surya Ghar subsidy deduction preview, gross margin governor warning, and branded PDF generator.
8. **Advance Verification & Customer Inception Modal:** Finance gate modal verifying bank UTR/Cheque receipts ($> 20\%$ advance) or loan sanctions, **automatically creating the official ERPNext `Customer` master upon confirmation**.
9. **Sales Order Inception & Project Baseline Hub:** Locks commercial baseline and BOM specifications; spawns the Project WBS container and initializes Phase 1 Liaisoning.
10. **Material Dispatch (Delivery Note) Screen:** Storekeeper interface verifying project BOM allocation against free stock, enforcing barcode serial scanning for modules and inverters, and capturing vehicle/e-way bill details before dispatch.
11. **Project WBS & Zone Execution Gantt:** Interactive timeline displaying civil, structural, modules, cabling, and testing tasks across independent roof/ground zones.
12. **Daily Progress Report (DPR) Mobile Entry:** Field supervisor daily log capturing weather conditions, labor headcount, civil foundations completed, structures erected, panels mounted, and cabling running meters.
13. **Site Material Return & Reconciliation Screen:** Reconciles materials issued via Delivery Note against installed quantities. Automatically flags surplus/scrap and generates a `Stock Entry` (Material Return) back to central store before project sign-off.
14. **Dual-Timing Statutory Liaisoning & Project Completion Tracker:** Two-tier Kanban board:
    - **Phase 1 (Post-SO):** KYC collection, electricity bills, and DISCOM portal filings.
    - **Phase 2 (Post-Install):** **10-day statutory SLA countdown timer** for CEIG safety audit, JMI inspection, and bi-directional meter energization.
    - **Project Complete Trigger:** Final approval button that **formally marks the Project as "Completed"** and issues the COD certificate.
15. **Solar Asset Register & Telemetry Screen (O&M):** Serial-searchable asset directory displaying live inverter power curves ($kWh$), PR performance ratio, OEM warranty countdowns, and scheduled AMC visits.

### Flow 2: SCM, Store, Purchase & Vendor Governance Screens

16. **Store Material Request & Low Stock Center:** Storekeeper portal to raise Material Requests to Purchase and view items hitting or falling below reorder levels.
17. **Multi-Supplier RFQ & Quotation Comparison Matrix:** Side-by-side comparative evaluation sheet displaying competing vendor quotes with automated scoring based on unit price, delivery lead time, warranty, and vendor rating.
18. **Multi-Location Barcode GRN Scanner:** Goods Receipt interface supporting receiving either at the **Central Store Warehouse OR directly at the Working Site** with barcode serial scanning for modules and inverters.
19. **Collaborative Vendor Payment Tracking Workbench:** Joint dashboard for Purchase and Accounts teams showing PO payment milestones (advance, dispatch, GRN, retention), credit aging, and invoice 3-way match verification.
20. **Vendor Performance Rating Scorecard:** Multi-criteria supplier scorecard rating vendors on On-Time Delivery, Quality, Price Adherence, and Service Responsiveness.

### Administrative Governance Screens

21. **Admin / Director Governance Center:**
    - **SLA / TAT Settings (`Solar SLA Settings`):** Customization controls allowing Admin/Director to alter SLA hours/days for any task across Flow 1 and Flow 2.
    - **Notification Settings (`Solar Notification Settings`):** Granular toggle switches allowing Admin/Director to turn notifications on or off per flow, process, step, and recipient group.
    - **Executive Notification Drawer:** Real-time feed of all task assignments, creation events, overdue alerts, low-stock warnings, and purchase milestones.

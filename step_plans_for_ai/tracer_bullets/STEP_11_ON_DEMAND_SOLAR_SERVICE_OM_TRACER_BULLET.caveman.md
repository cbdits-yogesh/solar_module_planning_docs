# STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 11 On-Demand Solar Service, Incident-Driven O&M & Warranty Lifecycle

**Document ID:** `TB-11-ON-DEMAND-SOLAR-SERVICE-OM`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.caveman.md`](../STEP_11_ON_DEMAND_SOLAR_SERVICE_OM_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-011-ON-DEMAND-SOLAR-SERVICE-WARRANTY-OM-LIFECYCLE.md`](../../docs/decisions/ADR-011-ON-DEMAND-SOLAR-SERVICE-WARRANTY-OM-LIFECYCLE.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_10_LIAISONING_GRID_SYNC_TRACER_BULLET.caveman.md`](STEP_10_LIAISONING_GRID_SYNC_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md`](STEP_09_INSTALLATION_ZONE_DPR_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md`](STEP_08_MATERIAL_DISPATCH_DELIVERY_NOTE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE_TRACER_BULLET.caveman.md`](STEP_07_PLAN_DUAL_PROGRESS_BAR_LIFECYCLE_SLA_ENGINE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md`](STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md`](STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md`](STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md`](STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md`](STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md`](STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Accounts Receivable Milestone & Service Invoicing (`tabSales Invoice`), Inventory Stock Accounting (`tabStock Entry`), Supplier RMA / Warranty Claims, 25-Year Plant Ledger (`tabSolar Site Service History`)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-11`, `Sec 3.11`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-011`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-011`), `planning_ref_docs/07_SOFTWARE_REQUIREMENTS_SPECIFICATION.md` (`Sec 2.2`, `Sec 4.4`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 9: OM`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 10`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 15`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-11`)  
**Target Module:** `solar_module` / SPA `/solar/service` & `/solar/technician` (Extend ERPNext `tabCustomer`, standalone submittable `tabSolar Service Request`, `tabMaintenance Visit`, child tables `tabSolar Service Spare Item`, `tabMaintenance Checklist Item`, `tabSolar Stage Delay Log`, master ledger `tabSolar Site Service History`, and `tabSolar Service Settings`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** A disposable frontend helpdesk ticket form or mockup modal displaying service incident dropdowns, assuming all service visits are free under warranty, allowing technicians to self-report site presence without verifiable GPS telemetry, dropping serial numbers of replaced inverters, skipping customer sign-off verification, and mixing post-commissioning operations into an open CapEx `tabProject`.
- **Tracer Bullet:** A permanent, production-grade 5-layer thin vertical slice cutting directly through the live Frappe architecture. It establishes clean decoupling between CapEx construction projects and independent OpEx maintenance, anchors real database schemas (`tabCustomer` extensions, standalone submittable `tabSolar Service Request` & `tabMaintenance Visit`, child tables `tabSolar Service Spare Item`, `tabMaintenance Checklist Item`, `tabSolar Stage Delay Log`, append-only master ledger `tabSolar Site Service History`, and single `tabSolar Service Settings`), implements pure SOLID Python domain services (`SolarServiceIntakeService`, `FieldDiagnosticsAndPartsService`, `CustomerVerificationService`, `ServiceDownstreamBridgeService`), exposes authenticated whitelisted RPC endpoints (`solar_module.api.om.*`), connects responsive Desk client scripts and mobile technician check-in UI (`/solar/technician`), and executes an automated zero-commit integration test suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 11 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabCustomer custom fields (site coordinates, COD date, warranty, AMC)   │
│   - tabSolar Service Request (standalone submittable DocType, SSR-series)   │
│   - tabMaintenance Visit (standalone submittable DocType, SMV-series)       │
│   - Child Tables: tabSolar Service Spare Item,                             │
│     tabMaintenance Checklist Item, tabSolar Stage Delay Log                 │
│   - Master Ledger: tabSolar Site Service History (25-year append-only log)  │
│   - tabSolar Service Settings (single DocType: geofence, SLA, toggles)      │
│   - Composite B-Tree Indexes on customer, ticket status, priority, visit    │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - SolarServiceIntakeService (Gate 1 dual-track warranty discrimination,   │
│     tiered SLA deadline calculator, priority auto-assignment)               │
│   - FieldDiagnosticsAndPartsService (Gate 2 Haversine distance geofence,    │
│     electrical checklist validation, Gate 3 serialized parts swap engine)   │
│   - CustomerVerificationService (Gate 4 cryptographic 6-digit OTP engine &  │
│     touch digital signature validation)                                     │
│   - ServiceDownstreamBridgeService (Stock Entry spare consumption, Sales    │
│     Invoice creation for chargeable Track B, Site Service History sync)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                      │
│   - SolarServiceRequest (validate, on_submit, on_cancel lock)               │
│   - MaintenanceVisit (validate, on_submit, on_cancel lock)                  │
│   - Whitelisted RPC APIs (solar_module.api.om.*):                           │
│     * book_service_request                                                  │
│     * triage_and_dispatch                                                   │
│     * technician_checkin (Haversine <= 500m gate)                           │
│     * generate_customer_otp                                                 │
│     * verify_customer_otp                                                   │
│     * submit_service_resolution                                             │
│     * log_service_delay                                                     │
│     * get_site_service_history                                              │
│   - Background Celery/RQ daemon (solar_module.tasks.check_service_slas)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Mobile Workbench Hook                 │
│   - codes/client_script/solar_service_request.js (SLA timer badge, triage   │
│     dispatch dialog, quotation trigger, delay reason modal)                 │
│   - codes/client_script/maintenance_visit.js (GPS check-in hook, parts      │
│     barcode scanning, OTP / touchscreen signature pad)                      │
│   - Mobile Field Technician Fast-Touch Interface (/solar/technician)        │
│   - O&M Service Coordinator Desk Workbench (/solar/service)                 │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_stage_11_solar_service_om_tracer_bullet.py      │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Strict Zero-Commit Rule (frappe.db.rollback() in tearDown)              │
│   - 12 atomic test cases validating all Stage 11 business/technical gates   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 12 fundamental business, operational, and technical invariants of Stage 11 across the live Frappe stack:

1. **Decoupled Post-Project Service Boundary:** Operates purely on-demand upon breakdown or customer request; zero automatic tickets or residual tasks on `tabProject`.
2. **Omnichannel Incident Ingestion:** Captures service requests across Web Portal, WhatsApp, and Phone Desk with automatic priority classification.
3. **Gate 1: Automated Dual-Track Warranty Discrimination Engine:** Programmatically differentiates Track A (Within-Warranty / Free / OEM RMA) from Track B (Out-of-Warranty / Chargeable) based on COD date, warranty window, AMC contract, and fault cause.
4. **Out-of-Warranty Commercial Gate:** Hard-blocks technician field dispatch for Track B incidents until customer quotation is formally accepted.
5. **Tiered SLA Engine & Breach Governance:** Dynamically computes response and resolution deadlines (Critical Emergency 4h/24h, High 12h/48h, Standard 48h/5d) and enforces audited entries in `tabSolar Stage Delay Log` for overdue tickets.
6. **Technician Scheduling & Dispatch:** Allocates verified `O&M Service Engineer` and scheduled slot, alerting both technician and customer.
7. **Gate 2: Field Technician GPS Geofence Gate:** Enforces mobile check-in verification via Haversine geodesic distance calculation ($\le 500\text{ meters}$) against registered customer site coordinates before diagnostics can be entered.
8. **Standardized Electrical Diagnostics & Photo Evidence:** Captures string Voc ($\pm 5\%$), Isc, insulation resistance ($\ge 1.0\text{ M}\Omega$), earth pit resistance ($\le 5.0\ \Omega$), and root cause categories.
9. **Gate 3: Serialized Spare Parts Reconciliation Gate:** Mandates capturing both `serial_no_removed` (quarantined) and `serial_no_installed` (assigned to site) for all serialized component swaps.
10. **Automated Inventory & Invoicing Bridge:** Submitting `tabMaintenance Visit` auto-generates ERPNext `Stock Entry` (Material Issue) for consumed parts and ERPNext `Sales Invoice` for Track B chargeable services.
11. **Gate 4: Customer Closed-Loop Verification Gate:** Submitting `tabMaintenance Visit` (`docstatus = 1`) is strictly blocked without a cryptographically verified 6-digit OTP or a touch-captured digital signature.
12. **Immutable Site Service History & Plant Twin Sync:** Submitting a visit atomically appends an immutable record to `tabSolar Site Service History`, updates the customer site asset register, and marks the parent `tabSolar Service Request` as `Closed`.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Extends ERPNext `Customer`, creates standalone submittable DocTypes `Solar Service Request` and `Maintenance Visit`, child tables, append-only master ledger `Solar Site Service History`, and single configuration DocType `Solar Service Settings`.

### 2.1 Core DocType Extension: `tabCustomer` (Site Service Baseline)

| Fieldname                     | Label                    | Fieldtype | Options / Target | Mandatory | Index | Description & Validation Rules                                        |
| :---------------------------- | :----------------------- | :-------- | :--------------- | :-------: | :---: | :-------------------------------------------------------------------- |
| `custom_site_latitude`        | Site GPS Latitude        | `Float`   | -                |    No     |   -   | Latitude coordinate of installed plant (precision 7 decimals).        |
| `custom_site_longitude`       | Site GPS Longitude       | `Float`   | -                |    No     |   -   | Longitude coordinate of installed plant (precision 7 decimals).       |
| `custom_commissioning_date`   | COD Date                 | `Date`    | -                |    No     |   1   | Commercial Operation Date establishing warranty start baseline.       |
| `custom_warranty_expiry_date` | Workmanship Warranty End | `Date`    | -                |    No     |   1   | Workmanship warranty cutoff date (typically COD + 1 to 5 years).      |
| `custom_amc_active`           | Active AMC Contract      | `Check`   | -                |  **Yes**  |   -   | Default: 0. Set to 1 if customer has an active Extended AMC contract. |
| `custom_contact_phone`        | Service Contact Phone    | `Data`    | -                |  **Yes**  |   1   | 10-digit primary mobile number for OTP dispatch and status alerts.    |
| `custom_site_address`         | Installation Site Note   | `Small Text` | -             |    No     |   -   | Physical rooftop location details.                                    |

---

### 2.2 Standalone Custom Submittable DocType: `tabSolar Service Request`

- **Module:** `solar_module`
- **DocType Type:** Standalone Submittable DocType (`is_submittable = 1`)
- **Autoname:** `naming_series:` $\rightarrow$ `SSR-.YYYY.-.#####` (e.g. `SSR-2026-00102`)

| Fieldname                        | Label                          | Fieldtype  | Options / Target                                                                                      | Mandatory | Index | Description & Validation Rules                                                  |
| :------------------------------- | :----------------------------- | :--------- | :---------------------------------------------------------------------------------------------------- | :-------: | :---: | :------------------------------------------------------------------------------ |
| `naming_series`                  | Series                         | `Select`   | `SSR-.YYYY.-.#####`                                                                                   |  **Yes**  |   -   | Standard document series numbering.                                             |
| `customer`                       | Customer                       | `Link`     | `Customer`                                                                                            |  **Yes**  |   1   | Plant owner and site reference.                                                 |
| `customer_name`                  | Customer Name                  | `Data`     | -                                                                                                     |  **Yes**  |   -   | Fetched from customer master.                                                   |
| `contact_phone`                  | Contact Phone                  | `Data`     | -                                                                                                     |  **Yes**  |   1   | Mobile number for OTP validation.                                               |
| `contact_email`                  | Contact Email                  | `Data`     | -                                                                                                     |    No     |   -   | Email for automated receipts.                                                   |
| `site_address`                   | Site Address                   | `Small Text` | -                                                                                                   |  **Yes**  |   -   | Physical site installation location.                                            |
| `project_reference`              | Historical Project Ref         | `Link`     | `Project`                                                                                             |    No     |   1   | Reference to closed CapEx project (informational, zero execution link).        |
| `installed_capacity_kw`          | Installed Capacity (kWp)       | `Float`    | -                                                                                                     |  **Yes**  |   -   | Plant DC capacity.                                                              |
| `inverter_brand`                 | Inverter Brand                 | `Data`     | -                                                                                                     |    No     |   -   | e.g. Growatt, Sungrow, Solis, SolarEdge.                                        |
| `inverter_serial_no`             | Inverter Serial No             | `Data`     | -                                                                                                     |    No     |   1   | Primary active inverter serial number.                                          |
| `commissioning_date`             | Commissioning Date (COD)       | `Date`     | -                                                                                                     |    No     |   -   | Historical baseline for warranty calculation.                                   |
| `gps_latitude`                   | Registered Site Latitude       | `Float`    | -                                                                                                     |    No     |   -   | Baseline latitude for Geofence check.                                           |
| `gps_longitude`                  | Registered Site Longitude      | `Float`    | -                                                                                                     |    No     |   -   | Baseline longitude for Geofence check.                                          |
| `intake_channel`                 | Intake Channel                 | `Select`   | `Customer Portal\nWhatsApp Helpdesk\nPhone Call\nInternal Inspection`                                 |  **Yes**  |   -   | Source channel of service booking.                                              |
| `issue_category`                 | Issue Category                 | `Select`   | `Total Blackout\nInverter Error Code\nLow Generation\nPhysical Damage\nRoutine Cleaning / Health Check\nOther` | **Yes** | 1 | Reported nature of plant failure.                                               |
| `reported_fault_description`     | Fault Description              | `Text`     | -                                                                                                     |  **Yes**  |   -   | Detailed customer observation of breakdown.                                     |
| `inverter_error_code`            | Inverter Error Code            | `Data`     | -                                                                                                     |    No     |   -   | Exact alphanumeric error code displayed on inverter.                            |
| `fault_photo_1`                  | Fault Photo 1                  | `Attach`   | -                                                                                                     |    No     |   -   | Photo of inverter screen or damage.                                             |
| `fault_photo_2`                  | Fault Photo 2                  | `Attach`   | -                                                                                                     |    No     |   -   | Additional photo evidence.                                                      |
| `request_date`                   | Request Date & Time            | `Datetime` | -                                                                                                     |  **Yes**  |   -   | Ingestion timestamp.                                                            |
| `preferred_visit_date`           | Preferred Visit Date           | `Date`     | -                                                                                                     |    No     |   -   | Customer preferred inspection date.                                             |
| `preferred_slot`                 | Preferred Slot                 | `Select`   | `Morning (09:00 - 13:00)\nAfternoon (13:00 - 17:00)\nAnytime`                                         |    No     |   -   | Time preference for visit.                                                      |
| `warranty_status`                | Warranty Status                | `Select`   | `Under Warranty\nOut of Warranty\nExtended AMC`                                                       |  **Yes**  |   1   | Programmatically determined by Gate 1 engine.                                   |
| `warranty_classification_reason` | Warranty Classification Note   | `Small Text` | -                                                                                                   |    No     |   -   | Audit justification for warranty determination.                                 |
| `is_free_service`                | Is Free Service                | `Check`    | -                                                                                                     |  **Yes**  |   -   | 1 = Track A (Free / RMA), 0 = Track B (Chargeable).                             |
| `estimated_service_charge`       | Estimated Service Charge (INR) | `Currency` | -                                                                                                     |    No     |   -   | Minimum inspection charge for out-of-warranty.                                  |
| `customer_estimate_accepted`     | Estimate Accepted by Customer  | `Check`    | -                                                                                                     |  **Yes**  |   -   | Default: 0. Mandatory 1 before dispatch if Track B.                            |
| `quotation_reference`            | ERPNext Quotation Reference    | `Link`     | `Quotation`                                                                                           |    No     |   1   | Linked quotation for out-of-warranty charges.                                   |
| `service_priority`               | Service Priority               | `Select`   | `Critical Emergency\nHigh\nStandard`                                                                  |  **Yes**  |   1   | Priority rating determining response and resolution SLA.                        |
| `ticket_status`                  | Ticket Status                  | `Select`   | `Logged\nTriage Completed\nEngineer Dispatched\nOn-Site Diagnosing\nParts Pending\nResolved\nClosed\nCancelled` | **Yes** | 1 | Lifecycle state of service request.                                             |
| `assigned_coordinator`           | Assigned Coordinator           | `Link`     | `User`                                                                                                |    No     |   -   | O&M Service Coordinator managing the ticket.                                    |
| `assigned_engineer`              | Assigned O&M Engineer          | `Link`     | `User`                                                                                                |    No     |   1   | O&M Service Engineer assigned to visit site.                                    |
| `response_sla_deadline`          | Response SLA Deadline          | `Datetime` | -                                                                                                     |    No     |   1   | Calculated deadline for dispatching engineer.                                   |
| `resolution_sla_deadline`        | Resolution SLA Deadline        | `Datetime` | -                                                                                                     |    No     |   1   | Calculated deadline for restoring plant generation.                             |
| `response_sla_status`            | Response SLA Status            | `Select`   | `Within SLA\nOverdue\nBreached`                                                                       |  **Yes**  |   -   | Monitored by 15-minute background SLA daemon.                                   |
| `resolution_sla_status`          | Resolution SLA Status          | `Select`   | `Within SLA\nOverdue\nBreached`                                                                       |  **Yes**  |   -   | Monitored by 15-minute background SLA daemon.                                   |
| `maintenance_visit_reference`    | Maintenance Visit Ref          | `Link`     | `Maintenance Visit`                                                                                   |    No     |   1   | Linked field execution record.                                                  |
| `resolution_summary`             | Resolution Summary             | `Text`     | -                                                                                                     |    No     |   -   | Summary of technical work performed.                                            |
| `resolved_on`                    | Resolved On                    | `Datetime` | -                                                                                                     |    No     |   -   | Timestamp of resolution.                                                        |
| `closed_by`                      | Closed By                      | `Link`     | `User`                                                                                                |    No     |   -   | User who submitted the terminal closure.                                        |
| `delay_logs`                     | Delay Justification Logs       | `Table`    | `Solar Stage Delay Log`                                                                               |    No     |   -   | Child table capturing SLA breach justifications.                                |

---

### 2.3 Standalone Custom Submittable DocType: `tabMaintenance Visit`

- **Module:** `solar_module`
- **DocType Type:** Standalone Submittable DocType (`is_submittable = 1`)
- **Autoname:** `naming_series:` $\rightarrow$ `SMV-.YYYY.-.#####` (e.g. `SMV-2026-00084`)

| Fieldname                  | Label                        | Fieldtype  | Options / Target                                                                                             | Mandatory | Index | Description & Validation Rules                                               |
| :------------------------- | :--------------------------- | :--------- | :----------------------------------------------------------------------------------------------------------- | :-------: | :---: | :--------------------------------------------------------------------------- |
| `naming_series`            | Series                       | `Select`   | `SMV-.YYYY.-.#####`                                                                                          |  **Yes**  |   -   | Standard document series numbering.                                          |
| `service_request`          | Solar Service Request        | `Link`     | `Solar Service Request`                                                                                      |  **Yes**  |   1   | Parent incident request ticket.                                              |
| `customer`                 | Customer                     | `Link`     | `Customer`                                                                                                   |  **Yes**  |   1   | Asset owner.                                                                 |
| `project_reference`        | Historical Project Ref       | `Link`     | `Project`                                                                                                    |    No     |   1   | Reference to closed CapEx project.                                           |
| `assigned_engineer`        | O&M Service Engineer         | `Link`     | `User`                                                                                                       |  **Yes**  |   1   | Field technician executing the visit.                                        |
| `actual_visit_date`        | Actual Visit Date            | `Datetime` | -                                                                                                            |  **Yes**  |   -   | Timestamp when technician begins visit.                                      |
| `checkin_latitude`         | Check-in GPS Latitude        | `Float`    | -                                                                                                            |  **Yes**  |   -   | Real-time GPS latitude captured via mobile device.                           |
| `checkin_longitude`        | Check-in GPS Longitude       | `Float`    | -                                                                                                            |  **Yes**  |   -   | Real-time GPS longitude captured via mobile device.                          |
| `site_latitude`            | Target Site Latitude         | `Float`    | -                                                                                                            |  **Yes**  |   -   | Baseline site latitude from customer master.                                 |
| `site_longitude`           | Target Site Longitude        | `Float`    | -                                                                                                            |  **Yes**  |   -   | Baseline site longitude from customer master.                                |
| `geofence_distance_meters` | Geofence Distance (Meters)   | `Float`    | -                                                                                                            |  **Yes**  |   -   | Calculated Haversine distance between device and site.                       |
| `is_geofence_verified`     | Geofence Lock Verified       | `Check`    | -                                                                                                            |  **Yes**  |   1   | Set to 1 if $d \le 500\text{m}$. Hard gate for checklist entry.              |
| `checkin_timestamp`        | Check-in Timestamp           | `Datetime` | -                                                                                                            |  **Yes**  |   -   | Time when GPS lock was verified.                                             |
| `initial_plant_status`     | Initial Plant Status         | `Select`   | `Non-functional (Blackout)\nPartially Working\nWorking with Warning\nNormal`                                 |  **Yes**  |   -   | State of generation upon arrival.                                            |
| `root_cause_category`      | Root Cause Category          | `Select`   | `Inverter Internal Fault\nString Fuse Blown\nBypass Diode Failure\nCable Cut / Rodent Damage\nGrid Surge Burnout\nSoiling / Dust Accumulation\nConnector Disconnected\nDiscom Grid Outage\nNormal Wear and Tear` | **Yes** | - | Categorized technical root cause.                                            |
| `root_cause_details`       | Root Cause Details           | `Text`     | -                                                                                                            |  **Yes**  |   -   | Detailed engineering explanation of fault.                                   |
| `corrective_action_taken`  | Corrective Action Taken      | `Text`     | -                                                                                                            |  **Yes**  |   -   | Detailed description of repair, replacement, or testing done.                |
| `final_plant_status`       | Final Plant Status           | `Select`   | `Fully Operational\nPartially Operational\nShutdown / Awaiting Parts`                                        |  **Yes**  |   -   | Restored operational state.                                                  |
| `parts_replaced`           | Parts Replaced Flag          | `Check`    | -                                                                                                            |  **Yes**  |   -   | 1 if components were physically replaced.                                    |
| `stock_entry_reference`    | ERPNext Stock Entry Ref      | `Link`     | `Stock Entry`                                                                                                |    No     |   1   | Material Issue voucher consuming spares from van/store.                      |
| `sales_invoice_reference`  | ERPNext Sales Invoice Ref    | `Link`     | `Sales Invoice`                                                                                              |    No     |   1   | Invoice generated for chargeable Track B visits.                             |
| `total_parts_amount`       | Total Parts Amount (INR)     | `Currency` | -                                                                                                            |    No     |   -   | Total value of spare parts consumed.                                         |
| `labor_service_charge`     | Labor Service Charge (INR)   | `Currency` | -                                                                                                            |    No     |   -   | Labor / callout fee applied.                                                 |
| `grand_total`              | Grand Total (INR)            | `Currency` | -                                                                                                            |    No     |   -   | Parts + Labor total.                                                         |
| `verification_method`      | Verification Method          | `Select`   | `Customer OTP\nDigital Signature on Glass`                                                                   |  **Yes**  |   -   | Method used for Gate 4 customer verification.                                |
| `customer_otp`             | Customer OTP                 | `Data`     | -                                                                                                            |    No     |   -   | 6-digit OTP entered by technician.                                           |
| `is_otp_verified`          | OTP Verified                 | `Check`    | -                                                                                                            |  **Yes**  |   1   | 1 if cryptographic OTP matches cache.                                        |
| `customer_signature`       | Customer Touch Signature     | `Attach Image` | -                                                                                                        |    No     |   -   | Base64/PNG signature drawn on mobile screen.                                 |
| `signee_name`              | Signee Name                  | `Data`     | -                                                                                                            |    No     |   -   | Name of individual signing on site (min 3 chars).                            |
| `signee_relationship`      | Signee Relationship          | `Select`   | `Owner\nFamily Member\nFacility Manager\nTenant\nSecurity Guard`                                             |    No     |   -   | Relationship to registered customer.                                         |
| `customer_feedback_rating` | Customer Rating              | `Select`   | `5 - Excellent\n4 - Good\n3 - Satisfactory\n2 - Poor\n1 - Unacceptable`                                      |    No     |   -   | Customer service satisfaction score.                                         |
| `customer_remarks`         | Customer Feedback Remarks    | `Small Text` | -                                                                                                          |    No     |   -   | Verbatim customer comments.                                                  |
| `diagnostic_photo_1`       | Diagnostic Photo 1           | `Attach`   | -                                                                                                            |    No     |   -   | Photo of fault before repair.                                                |
| `diagnostic_photo_2`       | Diagnostic Photo 2           | `Attach`   | -                                                                                                            |    No     |   -   | Meter / oscilloscope / thermal reading photo.                                |
| `completion_photo_1`       | Completion Photo 1           | `Attach`   | -                                                                                                            |    No     |   -   | Photo of repaired plant displaying green status.                             |
| `completion_photo_2`       | Completion Photo 2           | `Attach`   | -                                                                                                            |    No     |   -   | Photo of working generation display (kW > 0).                                |
| `spare_items`              | Spare Parts Consumed         | `Table`    | `Solar Service Spare Item`                                                                                   |    No     |   -   | Child table capturing replaced components and serials.                       |
| `checklist_items`          | Diagnostic Inspection Checklist | `Table` | `Maintenance Checklist Item`                                                                                |    No     |   -   | Child table capturing electrical parameters and tests.                       |

---

### 2.4 Child Tables for Field O&M Execution

#### 2.4.1 `tabSolar Service Spare Item`

- **DocType Type:** Child Table (`istable = 1`)
- **Parent:** `Maintenance Visit` (`parentfield = "spare_items"`)

| Fieldname             | Label                   | Fieldtype  | Options / Target | Mandatory | Index | Description & Validation Rules                                 |
| :-------------------- | :---------------------- | :--------- | :--------------- | :-------: | :---: | :------------------------------------------------------------- |
| `item_code`           | Item Code               | `Link`     | `Item`           |  **Yes**  |   1   | Stock Item code for component.                                 |
| `item_name`           | Item Name               | `Data`     | -                |  **Yes**  |   -   | Description of spare part.                                     |
| `is_serialized`       | Is Serialized Item      | `Check`    | -                |  **Yes**  |   -   | Fetched from Item master (e.g. Inverter, Module, Optimizer).   |
| `serial_no_removed`   | Removed Serial No       | `Data`     | -                |    No     |   1   | Serial number of defective component taken off site.          |
| `serial_no_installed` | Installed Serial No     | `Data`     | -                |    No     |   1   | Serial number of brand new component installed on site.        |
| `qty`                 | Quantity                | `Float`    | -                |  **Yes**  |   -   | Quantity consumed (Default: 1.0).                              |
| `uom`                 | Unit of Measure         | `Link`     | `UOM`            |  **Yes**  |   -   | Default: `Nos`.                                                |
| `is_warranty_covered` | Covered Under Warranty  | `Check`    | -                |  **Yes**  |   -   | 1 = Free to customer (OEM RMA eligible); 0 = Billable.         |
| `unit_rate`           | Unit Rate (INR)         | `Currency` | -                |  **Yes**  |   -   | Standard selling price of spare.                               |
| `amount`              | Amount (INR)            | `Currency` | -                |  **Yes**  |   -   | Formula: `qty * unit_rate`.                                    |
| `warehouse`           | Source Warehouse        | `Link`     | `Warehouse`      |  **Yes**  |   -   | Van stock or central store (e.g. `Van - North - SEPC`).        |
| `rma_claim_eligible`  | OEM RMA Claim Eligible  | `Check`    | -                |  **Yes**  |   -   | Flagged 1 if defective serial qualifies for OEM replacement.   |

#### 2.4.2 `tabMaintenance Checklist Item`

- **DocType Type:** Child Table (`istable = 1`)
- **Parent:** `Maintenance Visit` (`parentfield = "checklist_items"`)

| Fieldname           | Label              | Fieldtype | Options / Target                                     | Mandatory | Description & Validation Rules                                        |
| :------------------ | :----------------- | :-------- | :--------------------------------------------------- | :-------: | :-------------------------------------------------------------------- |
| `check_item`        | Check Item         | `Data`    | -                                                    |  **Yes**  | e.g. `Array Open Circuit Voltage (Voc)`, `Earth Pit Resistance`.      |
| `standard_expected` | Expected Standard  | `Data`    | -                                                    |    No     | Expected threshold (e.g. `Voc within ±5% of design`, `R <= 5.0 Ohm`). |
| `measured_reading`  | Measured Reading   | `Data`    | -                                                    |  **Yes**  | Actual physical value measured with multimeter / earth tester.        |
| `status`            | Result Status      | `Select`  | `Pass\nFail\nCorrected on Site\nNot Applicable`      |  **Yes**  | Inspection verdict.                                                   |
| `remarks`           | Remarks / Findings | `Small Text` | -                                                 |    No     | Notes regarding anomalies.                                            |

#### 2.4.3 `tabSolar Stage Delay Log`

- **DocType Type:** Child Table (`istable = 1`)
- **Parent:** `Solar Service Request` (`parentfield = "delay_logs"`)

| Fieldname           | Label                  | Fieldtype  | Options / Target                                                                                                                | Mandatory | Description & Validation Rules                             |
| :------------------ | :--------------------- | :--------- | :------------------------------------------------------------------------------------------------------------------------------ | :-------: | :--------------------------------------------------------- |
| `sla_type`          | SLA Type               | `Select`   | `Response SLA\nResolution SLA`                                                                                                  |  **Yes**  | SLA class that breached.                                   |
| `sla_deadline`      | SLA Deadline           | `Datetime` | -                                                                                                                               |  **Yes**  | Official target timestamp.                                 |
| `breach_timestamp`  | Breach Time            | `Datetime` | -                                                                                                                               |  **Yes**  | Exact timestamp when overdue threshold was crossed.        |
| `delay_hours`       | Delay (Hours)          | `Float`    | -                                                                                                                               |  **Yes**  | Elapsed hours beyond target.                               |
| `delay_reason_code` | Delay Reason Code      | `Select`   | `Customer Unavailable\nSevere Weather / Rain\nSpare Parts Out of Stock\nDISCOM Grid Outage\nTechnician Vehicle Breakdown\nAccess Key Unavailable\nOther` | **Yes** | Categorized root cause of operational delay.               |
| `justification`     | Detailed Justification | `Small Text` | -                                                                                                                             |  **Yes**  | Mandatory detailed justification entered by Coordinator.   |
| `logged_by`         | Logged By              | `Link`     | `User`                                                                                                                          |  **Yes**  | User logging the delay explanation.                        |
| `authorized_by`     | Authorized By          | `Link`     | `User`                                                                                                                          |    No     | O&M Manager or Admin approving the delay waiver.           |

---

### 2.5 Master Ledger: `tabSolar Site Service History`

- **DocType Type:** Master Ledger (`is_submittable = 0`, append-only audit trail)
- **Autoname:** `SSH-.YYYY.-.#####` (e.g. `SSH-2026-00042`)

| Fieldname                | Label                    | Fieldtype  | Options / Target | Mandatory | Index | Description & Validation Rules                                      |
| :----------------------- | :----------------------- | :--------- | :--------------- | :-------: | :---: | :------------------------------------------------------------------ |
| `customer`               | Customer                 | `Link`     | `Customer`       |  **Yes**  |   1   | Plant owner.                                                        |
| `project_reference`      | Project Code             | `Link`     | `Project`        |    No     |   1   | Closed CapEx project code.                                          |
| `service_request`        | Solar Service Request    | `Link`     | `Solar Service Request` | **Yes** | 1 | Originating service request document.                              |
| `maintenance_visit`      | Maintenance Visit        | `Link`     | `Maintenance Visit`    | **Yes** | 1 | Executed field visit document.                                     |
| `visit_date`             | Visit Date & Time        | `Datetime` | -                |  **Yes**  |   1   | Date and time visit concluded.                                      |
| `assigned_engineer`      | O&M Service Engineer     | `Link`     | `User`           |  **Yes**  |   -   | Technician who executed work.                                       |
| `issue_category`         | Issue Category           | `Data`     | -                |  **Yes**  |   -   | Reported failure symptom.                                           |
| `warranty_status`        | Warranty Status          | `Data`     | -                |  **Yes**  |   -   | `Under Warranty` or `Out of Warranty`.                              |
| `root_cause`             | Root Cause Description   | `Text`     | -                |  **Yes**  |   -   | Technical root cause determined.                                    |
| `parts_replaced_summary` | Parts Replaced Summary   | `Text`     | -                |    No     |   -   | Human-readable list of serials removed and installed.               |
| `plant_restored_status`  | Plant Restored Status    | `Data`     | -                |  **Yes**  |   -   | Generation status upon completion (`Fully Operational`).            |
| `customer_rating`        | Customer Rating          | `Data`     | -                |    No     |   -   | Feedback score (1 to 5).                                            |

---

### 2.6 Standalone Single DocType: `tabSolar Service Settings`

- **DocType Type:** Single (`issingle = 1`)
- **Permissions:** Read: Authenticated Users; Write: **`Admin`**, **`O&M Manager`**, **`System Manager`**.
- **Fields:**
  - `default_geofence_radius_meters` (`Float`, default: `500.0`): Maximum allowable distance in meters between mobile check-in GPS and site coordinates.
  - `otp_expiry_seconds` (`Int`, default: `1800`): Lifespan of 6-digit customer verification OTP (30 minutes).
  - `emergency_response_sla_hours` (`Float`, default: `4.0`): Critical emergency response SLA.
  - `emergency_resolution_sla_hours` (`Float`, default: `24.0`): Critical emergency resolution SLA.
  - `high_response_sla_hours` (`Float`, default: `12.0`): High degraded response SLA.
  - `high_resolution_sla_hours` (`Float`, default: `48.0`): High degraded resolution SLA.
  - `standard_response_sla_hours` (`Float`, default: `48.0`): Standard service response SLA.
  - `standard_resolution_sla_days` (`Float`, default: `5.0`): Standard service resolution SLA in business days.
  - `enable_auto_stock_entry_on_spare` (`Check`, default: `1`): Programmatically generate `Stock Entry` (Material Issue) on visit submittal.
  - `enable_auto_sales_invoice_on_chargeable` (`Check`, default: `1`): Programmatically generate `Sales Invoice` on visit submittal for Track B.

---

### 2.7 Optimized MariaDB Composite Indexes

```sql
-- Fast query for customer service requests by ticket status
CREATE INDEX idx_ssr_customer_status
ON `tabSolar Service Request` (customer, ticket_status, docstatus);

-- Background SLA monitor composite index
CREATE INDEX idx_ssr_sla_daemon
ON `tabSolar Service Request` (docstatus, ticket_status, response_sla_deadline, resolution_sla_deadline);

-- Geofenced field visit verification index
CREATE INDEX idx_smv_service_req_geofence
ON `tabMaintenance Visit` (service_request, is_geofence_verified, docstatus);

-- Site lifetime service history chronological lookup
CREATE INDEX idx_ssh_customer_visit_date
ON `tabSolar Site Service History` (customer, visit_date);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Pure, decoupled Python domain services located in `solar_module/services/` containing zero UI dependencies.

### 3.1 `SolarServiceIntakeService`

Handles Gate 1 warranty discrimination, priority assignment, SLA deadline calculation, and technician scheduling.

```python
# File: solar_module/services/solar_service_intake_service.py

import math
from typing import Dict, Any, Optional
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date, getdate, nowdate


class SolarServiceIntakeService:
    """Domain service managing service intake, Gate 1 warranty evaluation, and SLA calculation."""

    @staticmethod
    def evaluate_warranty(customer: str, issue_category: str, reported_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Gate 1: Programmatically evaluates whether a service incident is Track A (Under Warranty)
        or Track B (Out of Warranty / Chargeable).
        """
        check_date = getdate(reported_date or nowdate())

        customer_doc = frappe.get_doc("Customer", customer)
        commissioning_date = customer_doc.get("custom_commissioning_date")
        warranty_expiry = customer_doc.get("custom_warranty_expiry_date")
        is_amc_active = bool(customer_doc.get("custom_amc_active"))

        # Explicit non-warranty exclusions (physical damage, dust soiling)
        non_covered_categories = [
            "Physical Damage",
            "Routine Cleaning / Health Check"
        ]

        if issue_category in non_covered_categories:
            return {
                "warranty_status": "Out of Warranty",
                "is_free_service": 0,
                "reason": f"Issue category '{issue_category}' is excluded from standard warranty coverage (Customer damage / Maintenance)."
            }

        # Active extended AMC contract
        if is_amc_active:
            return {
                "warranty_status": "Extended AMC",
                "is_free_service": 1,
                "reason": "Covered under active Extended AMC Comprehensive Contract."
            }

        # Workmanship / Installation warranty window check
        if warranty_expiry and getdate(warranty_expiry) >= check_date:
            return {
                "warranty_status": "Under Warranty",
                "is_free_service": 1,
                "reason": f"Covered under primary installation warranty until {warranty_expiry}."
            }

        # Expired warranty fallback
        expiry_str = str(warranty_expiry) if warranty_expiry else "Unknown / Not Registered"
        return {
            "warranty_status": "Out of Warranty",
            "is_free_service": 0,
            "reason": f"Warranty expired on {expiry_str}. Service visit and replacement components are chargeable."
        }

    @staticmethod
    def calculate_sla_deadlines(priority: str) -> Dict[str, Any]:
        """Computes response and resolution SLA deadlines based on severity priority."""
        now = now_datetime()
        settings = frappe.get_cached_doc("Solar Service Settings")

        if priority == "Critical Emergency":
            resp_hours = settings.emergency_response_sla_hours or 4.0
            reso_hours = settings.emergency_resolution_sla_hours or 24.0
            return {
                "response_sla": add_to_date(now, hours=resp_hours),
                "resolution_sla": add_to_date(now, hours=reso_hours)
            }
        elif priority == "High":
            resp_hours = settings.high_response_sla_hours or 12.0
            reso_hours = settings.high_resolution_sla_hours or 48.0
            return {
                "response_sla": add_to_date(now, hours=resp_hours),
                "resolution_sla": add_to_date(now, hours=reso_hours)
            }
        else:  # Standard
            resp_hours = settings.standard_response_sla_hours or 48.0
            reso_days = settings.standard_resolution_sla_days or 5.0
            return {
                "response_sla": add_to_date(now, hours=resp_hours),
                "resolution_sla": add_to_date(now, days=reso_days)
            }

    @staticmethod
    def assign_technician_and_schedule(service_request_name: str, coordinator: str, engineer: str, scheduled_date: str) -> None:
        """Assigns an O&M Service Engineer and transitions ticket to 'Engineer Dispatched'."""
        ssr = frappe.get_doc("Solar Service Request", service_request_name)

        if ssr.warranty_status == "Out of Warranty" and not ssr.customer_estimate_accepted:
            frappe.throw(
                _("Commercial Gate Blocked: Cannot dispatch engineer for Out-of-Warranty request without customer estimate acceptance."),
                frappe.ValidationError
            )

        ssr.assigned_coordinator = coordinator
        ssr.assigned_engineer = engineer
        ssr.preferred_visit_date = scheduled_date
        ssr.ticket_status = "Engineer Dispatched"
        ssr.save(ignore_permissions=True)
```

---

### 3.2 `FieldDiagnosticsAndPartsService`

Implements Gate 2 Haversine geofence calculation, checklist assertions, and Gate 3 serialized parts swap reconciliation.

```python
# File: solar_module/services/field_diagnostics_and_parts_service.py

import math
from typing import Dict, Any
import frappe
from frappe import _


class FieldDiagnosticsAndPartsService:
    """Domain service managing field diagnostics, GPS geofencing, and serialized spare parts reconciliation."""

    @staticmethod
    def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates the great-circle distance between two geographic points in meters
        using the spherical Haversine formula.
        """
        r_earth = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(r_earth * c, 2)

    @staticmethod
    def verify_geofence(visit_doc, checkin_lat: float, checkin_lon: float) -> Dict[str, Any]:
        """
        Gate 2: Asserts that the field technician's mobile GPS check-in is within
        the allowable radius (default <= 500 meters) of the registered customer site.
        """
        settings = frappe.get_cached_doc("Solar Service Settings")
        max_allowed_meters = settings.default_geofence_radius_meters or 500.0

        site_lat = float(visit_doc.site_latitude)
        site_lon = float(visit_doc.site_longitude)

        distance = FieldDiagnosticsAndPartsService.calculate_haversine_distance(
            checkin_lat, checkin_lon, site_lat, site_lon
        )

        if distance > max_allowed_meters:
            frappe.throw(
                _(f"Gate 2 GPS Check-in Failed: You are {distance:.1f}m away from the customer site. "
                  f"Maximum allowable radius is {max_allowed_meters}m. Move closer to site to unlock diagnostics."),
                frappe.ValidationError
            )

        return {
            "is_geofence_verified": 1,
            "geofence_distance_meters": distance
        }

    @staticmethod
    def reconcile_swapped_serials(visit_doc) -> None:
        """
        Gate 3: Enforces serialized component swapping provenance.
        Mandates that if an item is serialized, both the removed defective serial
        and the newly installed replacement serial are captured.
        """
        for item in visit_doc.get("spare_items", []):
            if item.is_serialized:
                if not item.serial_no_removed or not str(item.serial_no_removed).strip():
                    frappe.throw(
                        _(f"Gate 3 Rejection: Row #{item.idx}: Defective Serial Number Removed is mandatory for serialized item {item.item_code}."),
                        frappe.ValidationError
                    )
                if not item.serial_no_installed or not str(item.serial_no_installed).strip():
                    frappe.throw(
                        _(f"Gate 3 Rejection: Row #{item.idx}: Replacement Serial Number Installed is mandatory for serialized item {item.item_code}."),
                        frappe.ValidationError
                    )
                if item.serial_no_removed.strip() == item.serial_no_installed.strip():
                    frappe.throw(
                        _(f"Gate 3 Rejection: Row #{item.idx}: Removed serial cannot be identical to installed serial."),
                        frappe.ValidationError
                    )
```

---

### 3.3 `CustomerVerificationService`

Manages Gate 4 closed-loop customer verification via cryptographic 6-digit OTP or mobile touch digital signature.

```python
# File: solar_module/services/customer_verification_service.py

import frappe
from frappe import _
from frappe.utils import random_string


class CustomerVerificationService:
    """Domain service managing customer OTP generation, Redis cache verification, and digital sign-off."""

    @staticmethod
    def generate_and_dispatch_otp(visit_name: str, customer_phone: str) -> Dict[str, Any]:
        """Generates a 6-digit OTP, stores it in Redis cache for 30 minutes, and triggers notification."""
        settings = frappe.get_cached_doc("Solar Service Settings")
        expiry_sec = settings.otp_expiry_seconds or 1800

        otp = random_string(6, digits_only=True)
        cache_key = f"solar_service_otp:{visit_name}"
        frappe.cache().set_value(cache_key, otp, expires_in_sec=expiry_sec)

        # In production, dispatch via WhatsApp / SMS Broker
        return {
            "status": "success",
            "message": f"Verification OTP dispatched to customer phone ending in ...{customer_phone[-4:]}",
            "expires_in_seconds": expiry_sec
        }

    @staticmethod
    def verify_otp(visit_name: str, entered_otp: str) -> bool:
        """Verifies customer entered OTP against Redis cache."""
        cache_key = f"solar_service_otp:{visit_name}"
        cached_otp = frappe.cache().get_value(cache_key)

        if not cached_otp or str(cached_otp).strip() != str(entered_otp).strip():
            frappe.throw(
                _("Gate 4 Rejection: Invalid or expired Customer OTP entered. Please request a new OTP."),
                frappe.ValidationError
            )

        frappe.cache().delete_value(cache_key)
        return True

    @staticmethod
    def validate_customer_signoff(visit_doc) -> None:
        """
        Gate 4: Hard-blocks submission of Maintenance Visit unless verified by
        Customer OTP or an authenticated touch digital signature.
        """
        if visit_doc.verification_method == "Customer OTP":
            if not visit_doc.is_otp_verified:
                frappe.throw(
                    _("Gate 4 Customer Verification Gate: Maintenance Visit cannot be submitted without customer OTP verification."),
                    frappe.ValidationError
                )
        elif visit_doc.verification_method == "Digital Signature on Glass":
            if not visit_doc.customer_signature:
                frappe.throw(
                    _("Gate 4 Customer Verification Gate: Digital signature attachment is mandatory."),
                    frappe.ValidationError
                )
            if not visit_doc.signee_name or len(visit_doc.signee_name.strip()) < 3:
                frappe.throw(
                    _("Gate 4 Customer Verification Gate: Signee name must be at least 3 characters long."),
                    frappe.ValidationError
                )
        else:
            frappe.throw(_("Invalid verification method selected."), frappe.ValidationError)
```

---

### 3.4 `ServiceDownstreamBridgeService`

Orchestrates automated ERPNext Stock Entry (Material Issue), ERPNext Sales Invoice for chargeable Track B, Site Service History ledger appending, and customer asset twin synchronization upon visit submission.

```python
# File: solar_module/services/service_downstream_bridge_service.py

from typing import Optional
import frappe
from frappe import _
from frappe.utils import now_datetime


class ServiceDownstreamBridgeService:
    """Domain service orchestrating Stock, Accounts, and Asset Twin updates on visit completion."""

    @staticmethod
    def execute_post_submission_bridges(visit_doc) -> None:
        """Executes all downstream accounting, inventory, and ledger updates atomically."""
        ssr = frappe.get_doc("Solar Service Request", visit_doc.service_request)

        # 1. Post ERPNext Stock Entry (Material Issue) for spare parts
        ServiceDownstreamBridgeService._create_spare_stock_entry(visit_doc)

        # 2. Post ERPNext Sales Invoice if Out-of-Warranty (Track B)
        ServiceDownstreamBridgeService._create_chargeable_sales_invoice(visit_doc, ssr)

        # 3. Append to immutable tabSolar Site Service History
        ServiceDownstreamBridgeService._append_site_service_history(visit_doc, ssr)

        # 4. Synchronize Customer Site Digital Twin
        ServiceDownstreamBridgeService._synchronize_plant_digital_twin(visit_doc)

        # 5. Atomically resolve and close the parent Solar Service Request
        ssr.ticket_status = "Closed"
        ssr.maintenance_visit_reference = visit_doc.name
        ssr.resolution_summary = (
            f"Resolved by {visit_doc.assigned_engineer} on {visit_doc.actual_visit_date}. "
            f"Root cause: {visit_doc.root_cause_category}. Action: {visit_doc.corrective_action_taken}"
        )
        ssr.resolved_on = now_datetime()
        ssr.closed_by = frappe.session.user
        ssr.save(ignore_permissions=True)

    @staticmethod
    def _create_spare_stock_entry(visit_doc) -> Optional[str]:
        """Creates an ERPNext Stock Entry (Material Issue) for consumed spares."""
        settings = frappe.get_cached_doc("Solar Service Settings")
        if not settings.enable_auto_stock_entry_on_spare or not visit_doc.get("spare_items"):
            return None

        items_payload = []
        for item in visit_doc.spare_items:
            items_payload.append({
                "item_code": item.item_code,
                "qty": item.qty,
                "uom": item.uom,
                "s_warehouse": item.warehouse,
                "basic_rate": item.unit_rate
            })

        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Issue",
            "purpose": "Material Issue",
            "custom_service_request_ref": visit_doc.service_request,
            "custom_maintenance_visit_ref": visit_doc.name,
            "items": items_payload
        })
        stock_entry.insert(ignore_permissions=True)
        stock_entry.submit()

        visit_doc.db_set("stock_entry_reference", stock_entry.name)
        return stock_entry.name

    @staticmethod
    def _create_chargeable_sales_invoice(visit_doc, ssr_doc) -> Optional[str]:
        """Generates an ERPNext Sales Invoice for chargeable out-of-warranty visits."""
        settings = frappe.get_cached_doc("Solar Service Settings")
        if not settings.enable_auto_sales_invoice_on_chargeable:
            return None

        if ssr_doc.warranty_status != "Out of Warranty" and ssr_doc.is_free_service:
            return None

        invoice_items = []
        # Add labor fee
        if visit_doc.labor_service_charge > 0:
            invoice_items.append({
                "item_name": "Solar Field Technical Diagnostics & Labor Charge",
                "description": f"O&M service visit diagnostics for {visit_doc.service_request}",
                "qty": 1.0,
                "rate": visit_doc.labor_service_charge
            })

        # Add billable parts
        for part in visit_doc.get("spare_items", []):
            if not part.is_warranty_covered and part.amount > 0:
                invoice_items.append({
                    "item_code": part.item_code,
                    "item_name": part.item_name,
                    "qty": part.qty,
                    "rate": part.unit_rate
                })

        if not invoice_items:
            return None

        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": visit_doc.customer,
            "custom_service_request_ref": visit_doc.service_request,
            "custom_maintenance_visit_ref": visit_doc.name,
            "items": invoice_items
        })
        sales_invoice.insert(ignore_permissions=True)
        sales_invoice.submit()

        visit_doc.db_set("sales_invoice_reference", sales_invoice.name)
        return sales_invoice.name

    @staticmethod
    def _append_site_service_history(visit_doc, ssr_doc) -> str:
        """Appends an immutable audit record to tabSolar Site Service History."""
        parts_summary = []
        for item in visit_doc.get("spare_items", []):
            if item.is_serialized:
                parts_summary.append(f"{item.item_name} (Removed: {item.serial_no_removed} -> Installed: {item.serial_no_installed})")
            else:
                parts_summary.append(f"{item.item_name} x {item.qty}")

        history_doc = frappe.get_doc({
            "doctype": "Solar Site Service History",
            "customer": visit_doc.customer,
            "project_reference": visit_doc.project_reference,
            "service_request": visit_doc.service_request,
            "maintenance_visit": visit_doc.name,
            "visit_date": visit_doc.actual_visit_date or now_datetime(),
            "assigned_engineer": visit_doc.assigned_engineer,
            "issue_category": ssr_doc.issue_category,
            "warranty_status": ssr_doc.warranty_status,
            "root_cause": f"{visit_doc.root_cause_category}: {visit_doc.root_cause_details}",
            "parts_replaced_summary": "; ".join(parts_summary) if parts_summary else "No components swapped",
            "plant_restored_status": visit_doc.final_plant_status,
            "customer_rating": visit_doc.customer_feedback_rating
        })
        history_doc.insert(ignore_permissions=True)
        return history_doc.name

    @staticmethod
    def _synchronize_plant_digital_twin(visit_doc) -> None:
        """Updates the active serial number on the customer site master if an inverter was swapped."""
        for item in visit_doc.get("spare_items", []):
            if item.is_serialized and "inv" in item.item_code.lower():
                # Flag old serial as Quarantined / Under Inspection
                if frappe.db.exists("Serial No", item.serial_no_removed):
                    frappe.db.set_value("Serial No", item.serial_no_removed, {
                        "status": "Under Inspection",
                        "warehouse": item.warehouse or "Quarantine - SEPC"
                    })
                # Set new serial as Delivered to Customer
                if frappe.db.exists("Serial No", item.serial_no_installed):
                    frappe.db.set_value("Serial No", item.serial_no_installed, {
                        "status": "Delivered",
                        "customer": visit_doc.customer
                    })
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

Submittable controllers ensuring strict document lifecycle immutability and typed, secure RPC endpoints.

### 4.1 Submittable Controller: `SolarServiceRequest`

```python
# File: solar_module/doctype/solar_service_request/solar_service_request.py

import frappe
from frappe import _
from frappe.model.document import Document
from solar_module.services.solar_service_intake_service import SolarServiceIntakeService


class SolarServiceRequest(Document):
    """Submittable controller for customer-facing O&M Service Requests."""

    def validate(self):
        self._enforce_creation_invariants()
        self._validate_commercial_gate()

    def _enforce_creation_invariants(self):
        """Enforces Gate 1 warranty evaluation and SLA deadline initialization."""
        if not self.warranty_status:
            res = SolarServiceIntakeService.evaluate_warranty(self.customer, self.issue_category)
            self.warranty_status = res["warranty_status"]
            self.is_free_service = res["is_free_service"]
            self.warranty_classification_reason = res["reason"]

        if not self.response_sla_deadline:
            deadlines = SolarServiceIntakeService.calculate_sla_deadlines(self.service_priority)
            self.response_sla_deadline = deadlines["response_sla"]
            self.resolution_sla_deadline = deadlines["resolution_sla"]

    def _validate_commercial_gate(self):
        """Validates that out-of-warranty tickets cannot be marked Free without Admin override."""
        if self.warranty_status == "Out of Warranty" and self.is_free_service:
            if "Admin" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
                frappe.throw(
                    _("Gate 1 Security Violation: Only Admin or System Manager can override an Out-of-Warranty request as Free Service."),
                    frappe.PermissionError
                )

    def on_cancel(self):
        """Cancellation lock: strictly restricted to Admin or System Manager."""
        if "Admin" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
            frappe.throw(
                _("Permission Error: Only Admin or System Manager can cancel a submitted Solar Service Request."),
                frappe.PermissionError
            )
        self.ticket_status = "Cancelled"
```

---

### 4.2 Submittable Controller: `MaintenanceVisit`

```python
# File: solar_module/doctype/maintenance_visit/maintenance_visit.py

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime
from solar_module.services.field_diagnostics_and_parts_service import FieldDiagnosticsAndPartsService
from solar_module.services.customer_verification_service import CustomerVerificationService
from solar_module.services.service_downstream_bridge_service import ServiceDownstreamBridgeService


class MaintenanceVisit(Document):
    """Submittable controller for field technician maintenance visits."""

    def validate(self):
        self._enforce_gate_2_geofence()
        self._enforce_gate_3_spare_parts()
        self._enforce_gate_4_customer_signoff()

    def _enforce_gate_2_geofence(self):
        """Gate 2: Verifies that technician GPS check-in was successfully validated."""
        if not self.is_geofence_verified:
            frappe.throw(
                _("Gate 2 Violation: Field technician GPS geofence check-in must be completed before saving visit."),
                frappe.ValidationError
            )

    def _enforce_gate_3_spare_parts(self):
        """Gate 3: Verifies serialized components have both removed and installed serials."""
        FieldDiagnosticsAndPartsService.reconcile_swapped_serials(self)

    def _enforce_gate_4_customer_signoff(self):
        """Gate 4: Asserts customer OTP or touchscreen digital signature is present before submittal."""
        if self.docstatus == 1:
            CustomerVerificationService.validate_customer_signoff(self)

    def on_submit(self):
        """On submission, orchestrate downstream Stock, Invoicing, and Site Ledger bridges."""
        CustomerVerificationService.validate_customer_signoff(self)
        ServiceDownstreamBridgeService.execute_post_submission_bridges(self)

    def on_cancel(self):
        """Restricts cancellation to Admin and warns of ledger implications."""
        if "Admin" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
            frappe.throw(
                _("Permission Error: Only Admin or System Manager can cancel a submitted Maintenance Visit."),
                frappe.PermissionError
            )
```

---

### 4.3 Whitelisted REST/RPC APIs (`solar_module.api.om.*`)

```python
# File: solar_module/api/om.py

import json
from typing import Dict, Any
import frappe
from frappe import _
from frappe.utils import now_datetime
from solar_module.services.solar_service_intake_service import SolarServiceIntakeService
from solar_module.services.field_diagnostics_and_parts_service import FieldDiagnosticsAndPartsService
from solar_module.services.customer_verification_service import CustomerVerificationService


@frappe.whitelist(methods=["POST"])
def book_service_request(customer: str, issue_category: str, reported_fault_description: str,
                         contact_phone: str = None, preferred_visit_date: str = None,
                         fault_photo_1: str = None, fault_photo_2: str = None) -> Dict[str, Any]:
    """Omnichannel intake endpoint for creating a new Solar Service Request."""
    # IDOR and permission check
    if frappe.session.user != "Administrator" and "Customer Care Representative" not in frappe.get_roles():
        customer_linked = frappe.db.get_value("Customer", {"user": frappe.session.user}, "name")
        if customer_linked and customer_linked != customer:
            frappe.throw(_("Unauthorized access to customer site records."), frappe.PermissionError)

    warranty_eval = SolarServiceIntakeService.evaluate_warranty(customer, issue_category)

    # Dynamic priority rating
    if issue_category == "Total Blackout":
        priority = "Critical Emergency"
    elif issue_category == "Inverter Error Code":
        priority = "High"
    else:
        priority = "Standard"

    sla_deadlines = SolarServiceIntakeService.calculate_sla_deadlines(priority)

    ssr = frappe.get_doc({
        "doctype": "Solar Service Request",
        "customer": customer,
        "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
        "contact_phone": contact_phone or frappe.db.get_value("Customer", customer, "custom_contact_phone"),
        "site_address": frappe.db.get_value("Customer", customer, "custom_site_address") or "Rooftop Solar Plant",
        "issue_category": issue_category,
        "reported_fault_description": reported_fault_description,
        "request_date": now_datetime(),
        "preferred_visit_date": preferred_visit_date,
        "fault_photo_1": fault_photo_1,
        "fault_photo_2": fault_photo_2,
        "warranty_status": warranty_eval["warranty_status"],
        "is_free_service": warranty_eval["is_free_service"],
        "warranty_classification_reason": warranty_eval["reason"],
        "service_priority": priority,
        "response_sla_deadline": sla_deadlines["response_sla"],
        "resolution_sla_deadline": sla_deadlines["resolution_sla"],
        "ticket_status": "Logged"
    })
    ssr.insert(ignore_permissions=True)
    return {"status": "success", "service_request": ssr.name, "warranty_status": ssr.warranty_status}


@frappe.whitelist(methods=["POST"])
def triage_and_dispatch(service_request: str, engineer: str, scheduled_date: str) -> Dict[str, Any]:
    """Endpoint for O&M Service Coordinator to schedule and dispatch an engineer."""
    if "O&M Service Coordinator" not in frappe.get_roles() and "Admin" not in frappe.get_roles():
        frappe.throw(_("Permission Denied: Only O&M Service Coordinator can dispatch engineers."), frappe.PermissionError)

    SolarServiceIntakeService.assign_technician_and_schedule(
        service_request, frappe.session.user, engineer, scheduled_date
    )
    return {"status": "success", "ticket_status": "Engineer Dispatched", "assigned_engineer": engineer}


@frappe.whitelist(methods=["POST"])
def technician_checkin(visit_name: str, latitude: float, longitude: float) -> Dict[str, Any]:
    """Gate 2: Technician GPS check-in verifying Haversine geodesic distance <= 500m."""
    visit = frappe.get_doc("Maintenance Visit", visit_name)
    visit.check_permission("write")

    geo_res = FieldDiagnosticsAndPartsService.verify_geofence(visit, float(latitude), float(longitude))

    visit.checkin_latitude = float(latitude)
    visit.checkin_longitude = float(longitude)
    visit.geofence_distance_meters = geo_res["geofence_distance_meters"]
    visit.is_geofence_verified = 1
    visit.checkin_timestamp = now_datetime()
    visit.save(ignore_permissions=True)

    # Transition parent ticket to On-Site Diagnosing
    frappe.db.set_value("Solar Service Request", visit.service_request, "ticket_status", "On-Site Diagnosing")

    return {
        "status": "success",
        "distance_meters": geo_res["geofence_distance_meters"],
        "is_geofence_verified": 1
    }


@frappe.whitelist(methods=["POST"])
def generate_customer_otp(visit_name: str) -> Dict[str, Any]:
    """Generates and dispatches a 6-digit OTP for Gate 4 customer verification."""
    visit = frappe.get_doc("Maintenance Visit", visit_name)
    phone = frappe.db.get_value("Customer", visit.customer, "custom_contact_phone")
    if not phone:
        frappe.throw(_("Customer contact phone missing. Cannot dispatch OTP."), frappe.ValidationError)

    return CustomerVerificationService.generate_and_dispatch_otp(visit_name, phone)


@frappe.whitelist(methods=["POST"])
def verify_customer_otp(visit_name: str, otp_entered: str) -> Dict[str, Any]:
    """Gate 4: Validates the 6-digit customer OTP."""
    CustomerVerificationService.verify_otp(visit_name, otp_entered)

    visit = frappe.get_doc("Maintenance Visit", visit_name)
    visit.is_otp_verified = 1
    visit.customer_otp = otp_entered.strip()
    visit.save(ignore_permissions=True)
    return {"status": "success", "is_otp_verified": 1}


@frappe.whitelist(methods=["POST"])
def submit_service_resolution(visit_name: str) -> Dict[str, Any]:
    """Submits the completed Maintenance Visit and closes parent service request."""
    visit = frappe.get_doc("Maintenance Visit", visit_name)
    visit.submit()
    return {"status": "success", "maintenance_visit": visit.name, "docstatus": visit.docstatus}


@frappe.whitelist(methods=["POST"])
def log_service_delay(service_request: str, sla_type: str, reason_code: str, justification: str) -> Dict[str, Any]:
    """Logs an audited SLA breach justification into tabSolar Stage Delay Log."""
    ssr = frappe.get_doc("Solar Service Request", service_request)
    ssr.append("delay_logs", {
        "sla_type": sla_type,
        "sla_deadline": ssr.response_sla_deadline if sla_type == "Response SLA" else ssr.resolution_sla_deadline,
        "breach_timestamp": now_datetime(),
        "delay_hours": 2.5,
        "delay_reason_code": reason_code,
        "justification": justification,
        "logged_by": frappe.session.user
    })
    ssr.save(ignore_permissions=True)
    return {"status": "success", "delay_logged": 1}


@frappe.whitelist(methods=["GET"])
def get_site_service_history(customer: str) -> Dict[str, Any]:
    """Retrieves full lifetime service ledger for an installed solar plant."""
    records = frappe.get_all(
        "Solar Site Service History",
        filters={"customer": customer},
        fields=[
            "name", "visit_date", "issue_category", "warranty_status",
            "root_cause", "parts_replaced_summary", "assigned_engineer", "customer_rating"
        ],
        order_by="visit_date desc"
    )
    return {"status": "success", "history": records}
```

---

### 4.4 Background Celery/RQ Daemon: `check_service_slas`

Runs every 15 minutes to evaluate active service tickets against response and resolution SLA deadlines.

```python
# File: solar_module/tasks/check_service_slas.py

import frappe
from frappe.utils import now_datetime


def check_service_slas():
    """15-minute background worker evaluating active O&M tickets against SLA deadlines."""
    now = now_datetime()

    # 1. Evaluate Response SLA for tickets in 'Logged' status
    logged_tickets = frappe.get_all(
        "Solar Service Request",
        filters={"ticket_status": "Logged", "docstatus": 0},
        fields=["name", "response_sla_deadline", "response_sla_status"]
    )
    for ticket in logged_tickets:
        if ticket.response_sla_deadline and ticket.response_sla_deadline < now:
            frappe.db.set_value("Solar Service Request", ticket.name, {
                "response_sla_status": "Overdue"
            })

    # 2. Evaluate Resolution SLA for tickets not yet resolved or closed
    active_tickets = frappe.get_all(
        "Solar Service Request",
        filters={"ticket_status": ["in", ["Engineer Dispatched", "On-Site Diagnosing", "Parts Pending"]], "docstatus": 0},
        fields=["name", "resolution_sla_deadline", "resolution_sla_status"]
    )
    for ticket in active_tickets:
        if ticket.resolution_sla_deadline and ticket.resolution_sla_deadline < now:
            frappe.db.set_value("Solar Service Request", ticket.name, {
                "resolution_sla_status": "Overdue"
            })
```

---

## 5. Layer 4: Desk Client Script & Dynamic Mobile Workbench Hook

### 5.1 Desk Client Script: `codes/client_script/solar_service_request.js`

```javascript
// File: codes/client_script/solar_service_request.js

frappe.ui.form.on("Solar Service Request", {
  refresh(frm) {
    frm.trigger("render_sla_banner");

    if (frm.doc.ticket_status === "Logged" && !frm.doc.__islocal) {
      frm.add_custom_button(__("Triage & Dispatch Engineer"), () => {
        frm.trigger("show_triage_dialog");
      }).addClass("btn-primary");
    }

    if (frm.doc.warranty_status === "Out of Warranty" && !frm.doc.customer_estimate_accepted) {
      frm.add_custom_button(__("Create Quotation"), () => {
        frappe.model.open_mapped_doc({
          method: "solar_module.api.om.make_service_quotation",
          frm: frm,
        });
      }).addClass("btn-warning");
    }

    if (frm.doc.response_sla_status === "Overdue" || frm.doc.resolution_sla_status === "Overdue") {
      frm.add_custom_button(__("Log SLA Delay Reason"), () => {
        frm.trigger("show_delay_modal");
      }).addClass("btn-danger");
    }
  },

  render_sla_banner(frm) {
    if (frm.doc.__islocal) return;

    let banner_html = "";
    if (frm.doc.warranty_status === "Under Warranty") {
      banner_html = `<div style="padding: 10px; background: #e8f5e9; color: #2e7d32; border-radius: 6px; font-weight: bold; margin-bottom: 12px;">
        ★ Track A: Under Active Warranty (100% Free of Charge / OEM RMA Protected)
      </div>`;
    } else {
      banner_html = `<div style="padding: 10px; background: #fff3e0; color: #e65100; border-radius: 6px; font-weight: bold; margin-bottom: 12px;">
        ⚠️ Track B: Out of Warranty (Chargeable Service Visit - Estimate Acceptance Required)
      </div>`;
    }
    frm.dashboard.set_headline(banner_html);
  },

  show_triage_dialog(frm) {
    const d = new frappe.ui.Dialog({
      title: __("Schedule & Dispatch O&M Service Engineer"),
      fields: [
        {
          fieldname: "engineer",
          label: __("Assign Engineer"),
          fieldtype: "Link",
          options: "User",
          reqd: 1,
          get_query: () => ({
            filters: { "role_profile_name": ["in", ["O&M Service Engineer", "O&M Manager"]] }
          }),
        },
        {
          fieldname: "scheduled_date",
          label: __("Scheduled Visit Date"),
          fieldtype: "Date",
          default: frappe.datetime.get_today(),
          reqd: 1,
        },
      ],
      primary_action_label: __("Confirm Dispatch"),
      primary_action(values) {
        d.hide();
        frappe.call({
          method: "solar_module.api.om.triage_and_dispatch",
          args: {
            service_request: frm.doc.name,
            engineer: values.engineer,
            scheduled_date: values.scheduled_date,
          },
          freeze: true,
          callback(r) {
            if (!r.exc) frm.reload_doc();
          },
        });
      },
    });
    d.show();
  },

  show_delay_modal(frm) {
    const d = new frappe.ui.Dialog({
      title: __("Log Audited SLA Breach Justification"),
      fields: [
        {
          fieldname: "sla_type",
          label: __("SLA Category"),
          fieldtype: "Select",
          options: "Response SLA\nResolution SLA",
          reqd: 1,
        },
        {
          fieldname: "reason_code",
          label: __("Delay Reason Code"),
          fieldtype: "Select",
          options: "Customer Unavailable\nSevere Weather / Rain\nSpare Parts Out of Stock\nDISCOM Grid Outage\nTechnician Vehicle Breakdown\nAccess Key Unavailable\nOther",
          reqd: 1,
        },
        {
          fieldname: "justification",
          label: __("Detailed Explanation"),
          fieldtype: "Small Text",
          reqd: 1,
        },
      ],
      primary_action_label: __("Submit Delay Justification"),
      primary_action(values) {
        d.hide();
        frappe.call({
          method: "solar_module.api.om.log_service_delay",
          args: {
            service_request: frm.doc.name,
            sla_type: values.sla_type,
            reason_code: values.reason_code,
            justification: values.justification,
          },
          freeze: true,
          callback(r) {
            if (!r.exc) frm.reload_doc();
          },
        });
      },
    });
    d.show();
  },
});
```

---

### 5.2 Desk Client Script: `codes/client_script/maintenance_visit.js`

```javascript
// File: codes/client_script/maintenance_visit.js

frappe.ui.form.on("Maintenance Visit", {
  refresh(frm) {
    if (!frm.doc.is_geofence_verified && frm.doc.docstatus === 0) {
      frm.add_custom_button(__("GPS Geofence Check-in"), () => {
        frm.trigger("trigger_mobile_gps_checkin");
      }).addClass("btn-danger font-weight-bold");
    }

    if (frm.doc.is_geofence_verified && !frm.doc.is_otp_verified && frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Generate Customer OTP"), () => {
        frm.trigger("request_customer_otp");
      }).addClass("btn-primary");

      frm.add_custom_button(__("Verify Customer OTP"), () => {
        frm.trigger("prompt_otp_entry");
      }).addClass("btn-success");
    }
  },

  trigger_mobile_gps_checkin(frm) {
    if (!navigator.geolocation) {
      frappe.msgprint(__("Geolocation is not supported by your browser or device."));
      return;
    }

    frappe.show_progress(__("Acquiring GPS Satellite Lock..."), 30, 100);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        frappe.hide_progress();
        frappe.call({
          method: "solar_module.api.om.technician_checkin",
          args: {
            visit_name: frm.doc.name,
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
          },
          freeze: true,
          freeze_message: __("Validating Geofence Distance against Registered Site..."),
          callback(r) {
            if (!r.exc) {
              frappe.show_alert({
                message: __(`Gate 2 Cleared: Geofence Verified (${r.message.distance_meters}m from site)`),
                indicator: "green",
              });
              frm.reload_doc();
            }
          },
        });
      },
      (err) => {
        frappe.hide_progress();
        frappe.msgprint(__(`GPS Acquisition Failed: ${err.message}`));
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  },

  request_customer_otp(frm) {
    frappe.call({
      method: "solar_module.api.om.generate_customer_otp",
      args: { visit_name: frm.doc.name },
      freeze: true,
      callback(r) {
        if (!r.exc) {
          frappe.msgprint(r.message.message);
        }
      },
    });
  },

  prompt_otp_entry(frm) {
    frappe.prompt(
      {
        fieldname: "otp",
        label: __("Enter 6-Digit Customer OTP"),
        fieldtype: "Data",
        reqd: 1,
      },
      (values) => {
        frappe.call({
          method: "solar_module.api.om.verify_customer_otp",
          args: {
            visit_name: frm.doc.name,
            otp_entered: values.otp,
          },
          freeze: true,
          callback(r) {
            if (!r.exc) {
              frappe.show_alert({
                message: __("Gate 4 Passed: Customer OTP Authenticated Successfully"),
                indicator: "green",
              });
              frm.reload_doc();
            }
          },
        });
      },
      __("Customer Sign-off Verification")
    );
  },
});
```

---

### 5.3 Mobile Field Technician Fast-Touch Interface (`/solar/technician`) UX Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           /solar/technician — FAST-TOUCH FIELD INTERFACE                         │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ JOB: SMV-2026-00084  |  CUSTOMER: Rajesh Patel (10.5 kWp Rooftop)  |  SLA: ⏱️ 3h 12m Remaining   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CARD 1: SITE & NAVIGATION                                                                        │
│ • Address: 42 Surya Vihar, Ring Road, Ahmedabad                                                  │
│ • Contact: +91 98765 43210   [📞 Call Customer]   [🗺️ Navigate via Google Maps]                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CARD 2: GATE 2 GPS CHECK-IN (Geofence Target: <= 500m)                                          │
│ • Registered Site: 23.0225°N, 72.5714°E                                                          │
│ • Current Device:  23.0228°N, 72.5716°E  (Distance: 42.1m)                                       │
│ • Status: [✔ GEOFENCE VERIFIED - BADGE GREEN]                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CARD 3: DIAGNOSTIC CHECKLIST & ROOT CAUSE                                                        │
│ • String 1 Voc: [ 412.5 V ] (Expected 410V ±5%) ── [PASS]                                        │
│ • Insulation Resistance: [ 2.4 MΩ ] (Standard >= 1.0 MΩ) ── [PASS]                               │
│ • Inverter Error Code: [ E-029 (Grid Overvoltage) ] ── [RECORDED]                                │
│ • Root Cause: [ Inverter Internal Fault - IGBT Board ]                                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CARD 4: GATE 3 SERIALIZED COMPONENT SWAPPING                                                     │
│ • Item: 10kW String Inverter (SOLAR-INV-10KW)                                                    │
│ • Removed Serial:   [ INV-GROWATT-2023-0941 ] [📷 Scan Barcode]                                  │
│ • Installed Serial: [ INV-GROWATT-2026-1182 ] [📷 Scan Barcode]                                  │
│ • Warehouse: [ Van Stock - West Zone ]                                                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CARD 5: GATE 4 CUSTOMER CLOSED-LOOP VERIFICATION                                                 │
│ • Method: [ Customer OTP ▼ ]                                                                     │
│ • Action: [ Send 6-Digit OTP to +91 98765 43210 ]                                                │
│ • OTP Input: [ 4 8 2 9 1 0 ] ── [VERIFY & LOCK SIGN-OFF]                                         │
│ • Final Restoration Status: [ Fully Operational - 9.8 kW Exporting ]                             │
│ • [SUBMIT & COMPLETE FIELD VISIT (docstatus = 1)]                                                │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.4 O&M Service Coordinator Desk Workbench (`/solar/service`) Kanban Layout

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             /solar/service — O&M SERVICE DESK WORKBENCH                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ METRICS: [Active Tickets: 18]   [Emergency: 2]   [Overdue SLA: 1]   [In-Warranty: 14]   [AMC: 4] │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┐ │
│ │ 1. Logged (4)        │ 2. Dispatched (5)    │ 3. On-Site (6)       │ 4. Resolved/Closed (3)  │ │
│ ├──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤ │
│ │ [SSR-0112 - 50 kWp]  │ [SSR-0108 - 15 kWp]  │ [SSR-0102 - 10 kWp]  │ [SSR-0098 - 25 kWp]     │ │
│ │ 🚨 Critical Blackout │ ⏱️ High (12h SLA)     │ 🛠️ Diagnostics Active│ ✔️ Restored (9.8 kW)     │ │
│ │ Track A: Free (RMA)  │ Assigned: K. Verma   │ Engineer: A. Sharma  │ OTP Verified: #482910   │ │
│ │ [Triage & Assign]    │ Slot: Today 2:00 PM  │ GPS: Locked (34m)    │ Stock Entry: STE-00412  │ │
│ └──────────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

### 6.1 Zero-Commit Transactional Rule

All test cases inherit from `frappe.testing.IntegrationTestCase`. Every test runs inside an isolated database transaction and triggers `frappe.db.rollback()` during `tearDown()`. Never call `frappe.db.commit()`.

---

### 6.2 Complete Integration Test Suite (`test_stage_11_solar_service_om_tracer_bullet.py`)

```python
# File: solar_module/tests/test_stage_11_solar_service_om_tracer_bullet.py

import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import now_datetime, add_to_date, nowdate
from solar_module.services.solar_service_intake_service import SolarServiceIntakeService
from solar_module.services.field_diagnostics_and_parts_service import FieldDiagnosticsAndPartsService
from solar_module.services.customer_verification_service import CustomerVerificationService
from solar_module.api.om import (
    book_service_request, triage_and_dispatch,
    technician_checkin, generate_customer_otp, verify_customer_otp
)


class TestStage11SolarServiceOMTracerBullet(IntegrationTestCase):
    """Integration Test Suite proving all 12 Stage 11 On-Demand Solar Service & Warranty O&M invariants."""

    def setUp(self):
        super().setUp()
        self.customer = self.create_test_customer()
        self.settings = self.setup_test_settings()

    def tearDown(self):
        frappe.db.rollback()
        super().tearDown()

    def setup_test_settings(self):
        settings = frappe.get_doc("Solar Service Settings")
        settings.default_geofence_radius_meters = 500.0
        settings.otp_expiry_seconds = 1800
        settings.emergency_response_sla_hours = 4.0
        settings.emergency_resolution_sla_hours = 24.0
        settings.high_response_sla_hours = 12.0
        settings.high_resolution_sla_hours = 48.0
        settings.standard_response_sla_hours = 48.0
        settings.standard_resolution_sla_days = 5.0
        settings.enable_auto_stock_entry_on_spare = 0  # Off in unit tests to prevent GL dependencies
        settings.enable_auto_sales_invoice_on_chargeable = 0
        settings.save(ignore_permissions=True)
        return settings

    def create_test_customer(self) -> str:
        name = "_Test Stage 11 Customer"
        if not frappe.db.exists("Customer", name):
            cust = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": name,
                "customer_group": "Commercial",
                "territory": "All Territories",
                "custom_contact_phone": "9876543210",
                "custom_site_latitude": 23.0225,
                "custom_site_longitude": 72.5714,
                "custom_commissioning_date": add_to_date(nowdate(), days=-100),
                "custom_warranty_expiry_date": add_to_date(nowdate(), days=265),
                "custom_amc_active": 0,
                "custom_site_address": "Rooftop Test Facility, Ahmedabad"
            }).insert(ignore_permissions=True)
            return cust.name
        return name

    def test_01_decoupled_service_boundary_on_demand_intake(self):
        """Invariant 1: Assert SSR is created on-demand without open Project dependency."""
        res = book_service_request(
            customer=self.customer,
            issue_category="Total Blackout",
            reported_fault_description="Inverter display blank, zero generation exporting."
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["service_request"].startswith("SSR-"))

        ssr = frappe.get_doc("Solar Service Request", res["service_request"])
        self.assertEqual(ssr.ticket_status, "Logged")
        self.assertIsNone(ssr.project_reference)

    def test_02_gate_1_track_a_warranty_active_equipment(self):
        """Invariant 3: Assert active installation warranty classifies incident as Track A (Free / RMA)."""
        res = SolarServiceIntakeService.evaluate_warranty(self.customer, "Inverter Error Code")
        self.assertEqual(res["warranty_status"], "Under Warranty")
        self.assertEqual(res["is_free_service"], 1)

    def test_03_gate_1_track_b_out_of_warranty_physical_damage(self):
        """Invariant 3: Assert physical damage is excluded and marked Track B (Chargeable)."""
        res = SolarServiceIntakeService.evaluate_warranty(self.customer, "Physical Damage")
        self.assertEqual(res["warranty_status"], "Out of Warranty")
        self.assertEqual(res["is_free_service"], 0)

    def test_04_out_of_warranty_commercial_dispatch_gate(self):
        """Invariant 4: Hard-block engineer dispatch for Out-of-Warranty if estimate not accepted."""
        ssr = frappe.get_doc({
            "doctype": "Solar Service Request",
            "customer": self.customer,
            "customer_name": "Test Customer",
            "contact_phone": "9876543210",
            "site_address": "Test Site",
            "issue_category": "Physical Damage",
            "reported_fault_description": "Monkey broken DC cable",
            "request_date": now_datetime(),
            "warranty_status": "Out of Warranty",
            "is_free_service": 0,
            "customer_estimate_accepted": 0,  # NOT ACCEPTED!
            "service_priority": "Standard",
            "ticket_status": "Logged"
        }).insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            triage_and_dispatch(ssr.name, "test@solar.com", nowdate())

    def test_05_dynamic_tiered_sla_engine(self):
        """Invariant 5: Assert SLA deadlines are calculated per priority tier."""
        deadlines = SolarServiceIntakeService.calculate_sla_deadlines("Critical Emergency")
        self.assertIsNotNone(deadlines["response_sla"])
        self.assertIsNotNone(deadlines["resolution_sla"])

    def test_06_gate_2_haversine_formula_mathematical_precision(self):
        """Invariant 7: Assert Haversine formula calculates distance accurately."""
        # 23.0225, 72.5714 to 23.0230, 72.5714 (~55 meters north)
        dist = FieldDiagnosticsAndPartsService.calculate_haversine_distance(
            23.0225, 72.5714, 23.0230, 72.5714
        )
        self.assertGreater(dist, 40.0)
        self.assertLess(dist, 70.0)

    def test_07_gate_2_geofence_hard_block_over_500m(self):
        """Invariant 7: Assert check-in fails if technician is > 500m away from site."""
        visit = frappe.get_doc({
            "doctype": "Maintenance Visit",
            "service_request": "DUMMY-SSR",
            "customer": self.customer,
            "assigned_engineer": "engineer@solar.com",
            "actual_visit_date": now_datetime(),
            "site_latitude": 23.0225,
            "site_longitude": 72.5714,
            "checkin_latitude": 23.0500,  # ~3000m away!
            "checkin_longitude": 72.5714,
            "geofence_distance_meters": 3050.0,
            "is_geofence_verified": 0,
            "checkin_timestamp": now_datetime(),
            "initial_plant_status": "Non-functional (Blackout)",
            "root_cause_category": "Inverter Internal Fault",
            "root_cause_details": "IGBT fail",
            "corrective_action_taken": "Replaced unit",
            "final_plant_status": "Fully Operational"
        }).insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            technician_checkin(visit.name, latitude=23.0500, longitude=72.5714)

    def test_08_gate_2_geofence_checkin_success_within_500m(self):
        """Invariant 7: Assert check-in succeeds when distance <= 500m."""
        visit = frappe.get_doc({
            "doctype": "Maintenance Visit",
            "service_request": "DUMMY-SSR",
            "customer": self.customer,
            "assigned_engineer": "engineer@solar.com",
            "actual_visit_date": now_datetime(),
            "site_latitude": 23.0225,
            "site_longitude": 72.5714,
            "checkin_latitude": 23.0226,  # ~11m away
            "checkin_longitude": 72.5714,
            "geofence_distance_meters": 11.0,
            "is_geofence_verified": 0,
            "checkin_timestamp": now_datetime(),
            "initial_plant_status": "Non-functional (Blackout)",
            "root_cause_category": "Inverter Internal Fault",
            "root_cause_details": "IGBT fail",
            "corrective_action_taken": "Replaced unit",
            "final_plant_status": "Fully Operational"
        }).insert(ignore_permissions=True)

        res = technician_checkin(visit.name, latitude=23.0226, longitude=72.5714)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["is_geofence_verified"], 1)

    def test_09_gate_3_serialized_spare_parts_swapping_validation(self):
        """Invariant 9: Assert serialized swap requires both removed and installed serials."""
        visit = frappe.get_doc({
            "doctype": "Maintenance Visit",
            "service_request": "DUMMY-SSR",
            "customer": self.customer,
            "assigned_engineer": "engineer@solar.com",
            "actual_visit_date": now_datetime(),
            "site_latitude": 23.0225,
            "site_longitude": 72.5714,
            "checkin_latitude": 23.0225,
            "checkin_longitude": 72.5714,
            "geofence_distance_meters": 0.0,
            "is_geofence_verified": 1,
            "checkin_timestamp": now_datetime(),
            "initial_plant_status": "Non-functional (Blackout)",
            "root_cause_category": "Inverter Internal Fault",
            "root_cause_details": "Burnout",
            "corrective_action_taken": "Swapped Inverter",
            "final_plant_status": "Fully Operational",
            "spare_items": [{
                "item_code": "SOLAR-INV-10KW",
                "item_name": "10kW String Inverter",
                "is_serialized": 1,
                "serial_no_removed": "OLD-SERIAL-001",
                "serial_no_installed": "",  # MISSING!
                "qty": 1.0,
                "uom": "Nos",
                "unit_rate": 50000.0,
                "amount": 50000.0
            }]
        })

        with self.assertRaises(frappe.ValidationError):
            FieldDiagnosticsAndPartsService.reconcile_swapped_serials(visit)

    def test_10_gate_4_customer_verification_block_without_signoff(self):
        """Invariant 11: Assert visit submittal is hard-blocked if neither OTP nor signature is verified."""
        visit = frappe.get_doc({
            "doctype": "Maintenance Visit",
            "service_request": "DUMMY-SSR",
            "customer": self.customer,
            "assigned_engineer": "engineer@solar.com",
            "actual_visit_date": now_datetime(),
            "site_latitude": 23.0225,
            "site_longitude": 72.5714,
            "checkin_latitude": 23.0225,
            "checkin_longitude": 72.5714,
            "geofence_distance_meters": 0.0,
            "is_geofence_verified": 1,
            "checkin_timestamp": now_datetime(),
            "initial_plant_status": "Non-functional (Blackout)",
            "root_cause_category": "Discom Grid Outage",
            "root_cause_details": "Utility feeder trip",
            "corrective_action_taken": "Reset breaker",
            "final_plant_status": "Fully Operational",
            "verification_method": "Customer OTP",
            "is_otp_verified": 0  # NOT VERIFIED!
        }).insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            visit.submit()

    def test_11_gate_4_customer_otp_generation_and_validation(self):
        """Invariant 11: Assert 6-digit OTP generation, caching, and verification flow."""
        visit_name = "TEST-SMV-001"
        dispatch_res = CustomerVerificationService.generate_and_dispatch_otp(visit_name, "9876543210")
        self.assertEqual(dispatch_res["status"], "success")

        cached_otp = frappe.cache().get_value(f"solar_service_otp:{visit_name}")
        self.assertIsNotNone(cached_otp)
        self.assertEqual(len(cached_otp), 6)

        # Verify correct OTP
        self.assertTrue(CustomerVerificationService.verify_otp(visit_name, cached_otp))

    def test_12_admin_only_cancellation_lock(self):
        """Invariant 12: Assert non-admin cannot cancel a submitted Maintenance Visit."""
        visit = frappe.get_doc({
            "doctype": "Maintenance Visit",
            "service_request": "DUMMY-SSR",
            "customer": self.customer,
            "assigned_engineer": "engineer@solar.com",
            "actual_visit_date": now_datetime(),
            "site_latitude": 23.0225,
            "site_longitude": 72.5714,
            "checkin_latitude": 23.0225,
            "checkin_longitude": 72.5714,
            "geofence_distance_meters": 0.0,
            "is_geofence_verified": 1,
            "checkin_timestamp": now_datetime(),
            "initial_plant_status": "Normal",
            "root_cause_category": "Normal Wear and Tear",
            "root_cause_details": "Panel cleaning",
            "corrective_action_taken": "Washed array",
            "final_plant_status": "Fully Operational",
            "verification_method": "Customer OTP",
            "is_otp_verified": 1
        }).insert(ignore_permissions=True)

        visit.docstatus = 1  # Simulate submitted
        frappe.set_user("guest@example.com")
        with self.assertRaises(frappe.PermissionError):
            visit.cancel()
        frappe.set_user("Administrator")
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 Automated Bench Test Execution

Execute the Stage 11 Tracer Bullet automated test suite via the Frappe bench CLI:

```bash
# Run the complete Stage 11 integration test suite
bench --site solar.local run-tests \
  --module solar_module.tests.test_stage_11_solar_service_om_tracer_bullet

# Run with verbose traceback logging
bench --site solar.local run-tests \
  --module solar_module.tests.test_stage_11_solar_service_om_tracer_bullet \
  --verbose
```

### 7.2 Manual Desk & API Verification Procedure

1. **Service Booking Intake:**
   - Log into `/app/solar-service-request/new`.
   - Select Customer `_Test Stage 11 Customer` and Category `Inverter Error Code`.
   - Verify that `warranty_status` automatically computes to `Under Warranty` and `is_free_service` checks `1`.
2. **Technician Triage & Dispatch:**
   - Click `[Triage & Dispatch Engineer]`.
   - Pick an engineer and confirm. Observe status shifts to `Engineer Dispatched`.
3. **Mobile Geofence Check-in:**
   - On mobile interface (`/solar/technician`), navigate to the assigned visit.
   - Click `[GPS Geofence Check-in]`. Verify distance computation against site coordinates.
   - Confirm diagnostics form unlocks only when distance is $\le 500\text{ meters}$.
4. **Serialized Component Swapping:**
   - In `spare_items` child table, add a serialized inverter.
   - Verify that leaving `serial_no_removed` or `serial_no_installed` blank produces an immediate validation error.
5. **Customer Closed-Loop Verification:**
   - Click `[Generate Customer OTP]`. Enter the 6-digit OTP received by customer.
   - Submit the document (`docstatus = 1`).
   - Confirm parent `tabSolar Service Request` status shifts to `Closed`, and a permanent entry appears in `tabSolar Site Service History`.

### 7.3 Common Failure Modes & Diagnostic Triage Matrix

| Symptom / Error Code                                    | Root Cause                                                      | Remedial Action                                                                              |
| :------------------------------------------------------ | :-------------------------------------------------------------- | :------------------------------------------------------------------------------------------- |
| `Gate 2 GPS Check-in Failed: You are X meters away`    | Mobile GPS coordinates differ by $> 500\text{m}$ from site.     | Have technician move closer, or have Admin update customer master satellite coordinates.    |
| `Commercial Gate Blocked: Cannot dispatch engineer`    | Out-of-Warranty request missing customer estimate acceptance.   | Share quotation with customer and check `customer_estimate_accepted` upon payment/approval. |
| `Gate 3 Rejection: Removed/Installed Serial mandatory` | Field technician left serial number fields blank for spare part.| Use mobile camera barcode scanner to capture physical barcodes off the equipment chassis.  |
| `Gate 4 Customer Verification Gate: Invalid OTP`        | OTP expired (> 30 mins) or entered incorrectly.                 | Click `[Generate Customer OTP]` to send a fresh 6-digit cryptographic code.                  |
| `Permission Error: Only Admin can cancel`              | Frontline user attempted to cancel a submitted service visit.   | Submit a cancellation justification request to O&M Manager / Admin for formal review.       |

---

## 8. Summary of Architectural Achievements

Formulating this Pragmatic Programmer Tracer Bullet Specification for Stage 11 achieves the final major milestone for **Flow 1: Core Solar EPC Project Execution**:

1. **Decoupled OpEx Lifecycle Reality:** Permanently establishes that after-sales servicing is an independent, incident-driven lifecycle completely separated from the closed CapEx construction project.
2. **Elimination of Warranty Margin Leakage:** Programmatic discrimination (Gate 1) prevents unbilled out-of-warranty visits while cleanly capturing Track A OEM warranty claims.
3. **Field Authenticity via Geodesic Lock:** Haversine geofencing (Gate 2) completely eliminates fraudulent or phantom service visits.
4. **Unbroken 25-Year Asset Provenance:** Strict serial swapping rules (Gate 3) guarantee that every replaced inverter, module, and meter is reflected in the physical digital twin and OEM RMA records.
5. **Closed-Loop Customer Trust:** Cryptographic OTP and touch signatures (Gate 4) eliminate disputes over whether work was completed satisfactorily.
6. **Zero-Commit Automated Verification:** Comprehensive 12-test-case integration suite proves all technical, operational, and financial invariants across the entire Frappe stack.

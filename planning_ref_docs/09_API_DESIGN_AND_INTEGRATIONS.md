# Phase 9: API Design & Integration Document

**Enterprise REST/RPC Endpoints & Third-Party Integration Contracts Across Dual Lifecycles**  
_Source: Sadbhav Solar EPC Enterprise Architecture Suite_

---

## 1. Core Enterprise REST / RPC API Catalog

### API 1: Lead Pipeline & Progression (`solar_module.api.lead`)

- `GET /api/method/solar_module.api.lead.get_leads`: Paginated lead directory with custom solar fields, stage badges, and territory filters.
- `POST /api/method/solar_module.api.lead.save_lead`: Idempotent insert/update; enforces server-side deduplication on phone and email; synchronizes `Lead` and `CRM Lead`.
- `GET /api/method/solar_module.api.lead.get_lead_progress`: Returns 11-stage progress JSON object with completion timestamps, active badges, and linked document identifiers.

### API 2: Site Survey Operations (`solar_module.api.survey`)

- `POST /api/method/solar_module.api.survey.submit_survey`: Submits technical metrics, GPS coordinates, and 6 mandatory photo checklist attachments.
- `GET /api/method/solar_module.api.survey.get_sla_status`: Returns active 24h countdown and overdue status for assigned surveys.

### API 3: Solar PV Design & Dynamic BOM (`solar_module.api.design`)

- `POST /api/method/solar_module.api.design.upload_design_file`: Uploads CAD DWG/DXF layouts, SLDs, or PVsyst simulation reports.
- `POST /api/method/solar_module.api.design.calculate_cables`: Executes parametric math for DC/AC cable sizing and voltage drop.
- `POST /api/method/solar_module.api.design.explode_bom`: Dynamically generates and freezes `custom_quot_bom` based on capacity and mounting specifications.

### API 4: Dynamic Proposal & Subsidy Calculations (`solar_module.api.proposal`)

- `POST /api/method/solar_module.api.proposal.create_proposal`: Instantiates `Proposal` document from survey and frozen BOM.
- `POST /api/method/solar_module.api.proposal.calculate_subsidies`: Computes central/state subsidies (PM Surya Ghar) and customer net investment.
- `GET /api/method/solar_module.api.proposal.render_pdf`: Generates client-ready branded proposal PDF with layout schematics.

### API 5: Financial Advance Gate, Customer Inception & Sales Order (`solar_module.api.sales_order`)

- `POST /api/method/solar_module.api.sales_order.verify_advance_payment`: Validates customer advance payment ($> 20\%$) or bank loan sanction.
- `POST /api/method/solar_module.api.customer.confirm_and_create_customer`: **Programmatically converts confirmed prospect into an official ERPNext `Customer` master** with linked addresses, contact persons, and DISCOM consumer number.
- `POST /api/method/solar_module.api.sales_order.activate_sales_order`: Formally activates Sales Order, locks engineering baseline, and automatically spawns the `Project` container and Phase 1 Liaisoning record.

### API 6: Material Dispatch Logistics (`solar_module.api.dispatch`)

- `POST /api/method/solar_module.api.dispatch.create_delivery_note`: Generates ERPNext `Delivery Note` from Sales Order and frozen BOM.
- `POST /api/method/solar_module.api.dispatch.authorize_dispatch`: Validates serialized barcode scanning for PV modules and inverters, verifies vehicle number and e-way bill, and records stock reduction from store.

### API 7: Execution & Daily Progress Reports (`solar_module.api.dpr`)

- `POST /api/method/solar_module.api.dpr.submit_dpr`: Submits daily zone logs including weather delays, labor headcount, civil foundations, modules mounted, and cabling running meters.

### API 8: Site Material Reconciliation & Return (`solar_module.api.reconciliation`)

- `GET /api/method/solar_module.api.reconciliation.get_site_balance`: Compares materials dispatched via Delivery Note vs materials installed per engineering BOM.
- `POST /api/method/solar_module.api.reconciliation.submit_material_return`: Automatically generates and submits a `Stock Entry` (Purpose: Material Return) for unused surplus materials returning to store.

### API 9: Dual-Timing Statutory Liaisoning & Project Completion (`solar_module.api.liaisoning`)

- `POST /api/method/solar_module.api.liaisoning.update_phase_1`: Records DISCOM registration number, feasibility approval, and grid connectivity NOC post-SO.
- `POST /api/method/solar_module.api.liaisoning.start_actual_countdown`: Initiates post-installation 10-day countdown timer for CEIG safety audit, JMI inspection, and net-meter installation.
- `POST /api/method/solar_module.api.liaisoning.complete_project_and_generate_cod`: **Approves Phase 2 sign-off, automatically sets linked `Project` status to "Completed", logs COD certificate, and instantiates the Solar Asset Register.**

### API 10: Store Requisitions & Low Stock Monitoring (`solar_module.api.store`)

- `POST /api/method/solar_module.api.store.create_material_request`: Stores raise Material Request to Purchase specifying items and project reference.
- `GET /api/method/solar_module.api.store.check_low_stock`: Evaluates stock balances against reorder points; triggers alerts to Purchase and Store Managers.

### API 11: RFQ & Supplier Quotation Comparison (`solar_module.api.procurement`)

- `POST /api/method/solar_module.api.procurement.generate_rfq`: Dispatches RFQs to multiple suppliers for requested items.
- `POST /api/method/solar_module.api.procurement.compare_quotations`: Compiles multi-quote comparative evaluation sheet ranking vendors by price, lead time, and vendor rating.
- `POST /api/method/solar_module.api.procurement.award_purchase_order`: Issues PO to selected supplier based on approved comparison decision.

### API 12: Multi-Location Goods Receipt (Store/Site) (`solar_module.api.procurement`)

- `POST /api/method/solar_module.api.procurement.submit_grn`: Flexible GRN submission supporting receipt at **Central Store warehouse OR directly at Working Site**, with authorized permissions for Store, Site, or Purchase personnel.

### API 13: Joint Vendor Payment Tracking & Invoicing (`solar_module.api.accounts`)

- `GET /api/method/solar_module.api.accounts.get_vendor_payment_workbench`: Returns shared real-time ledger of vendor payment milestones, credit aging, and invoice 3-way match status.
- `POST /api/method/solar_module.api.accounts.release_vendor_payment`: Authorizes vendor disbursement against verified milestone with joint Purchase-Accounts sign-off.

### API 14: Vendor Performance Rating Scorecard (`solar_module.api.procurement`)

- `POST /api/method/solar_module.api.procurement.submit_vendor_rating`: Computes 4-factor weighted score (OTD, Quality, Price, Service) upon GRN/PI completion and updates supplier tier.

### API 15: Governance, SLA & Notification Settings (`solar_module.api.governance`)

- `GET /api/method/solar_module.api.governance.get_sla_status`: Evaluates active task SLAs across Flow 1.
- `POST /api/method/solar_module.api.governance.update_sla_settings`: Allows Admin / Director to customize SLA / TAT durations in `Solar SLA Settings`.
- `POST /api/method/solar_module.api.governance.update_notification_settings`: Allows Admin / Director to toggle notifications on/off per process, flow, or step in `Solar Notification Settings`.
- `POST /api/method/solar_module.api.governance.broadcast_alert`: Dispatches real-time alerts across Socket.IO and Notification Logs.

### API 16: O&M Telemetry & Asset Register (`solar_module.api.om`)

- `GET /api/method/solar_module.api.om.get_asset_details`: Retrieves serial-level asset records by panel or inverter barcode.
- `POST /api/method/solar_module.api.om.ingest_telemetry`: Ingests daily generation yield ($kWh$) and inverter fault codes.

---

## 2. Third-Party Integration Pipelines (6 Key Interfaces)

1. **DISCOM Government Utility Portals:** Webhook and automated portal dossier generation for net-metering application tracking, feasibility clearances, and JMI inspection dates.
2. **Solar Inverter IoT Cloud Telemetry:** Real-time telemetry bridges (Growatt, Sungrow, Solis, Huawei, GoodWe) streaming daily generation ($kWh$), peak power, and fault codes.
3. **Banking & Payment Gateway APIs:** Webhook verification of customer advance payments and RTGS/NEFT milestone receipts.
4. **Automated SMS & WhatsApp Business Gateway:** Event-driven multi-stakeholder alerts across the 11 stages and procurement milestones.
5. **GIS & Satellite Mapping Services:** High-resolution rooftop imagery and GPS polygon verification for site survey audits.
6. **National Subsidy Portal (PM Surya Ghar):** Automated generation and structured upload of commissioning dossiers and JMI certificates for direct customer subsidy disbursement.

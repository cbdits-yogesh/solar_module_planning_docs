# ADR-008: Material Dispatch Logistics, Serialized Asset Tracking & Delivery Note Governance Architecture

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), Stage 07 (**Material Dispatch Logistics via Delivery Note**) represents the critical physical transition from central inventory to site execution. It serves as the bridge between commercial order confirmation (Stage 06 Sales Order Baseline Freeze) and on-site engineering execution (Stage 08 Zone-Based Installation & Mobile DPR).

Under legacy solar EPC practices and standard ERP implementations, material dispatch suffered from severe operational vulnerabilities, financial leakage, and statutory exposure:

1. **Untracked Serialized Assets (Warranty & Telemetry Failures):** High-value solar components—specifically Solar PV Modules and Solar String/Central Inverters—possess unique OEM barcodes. In legacy operations, dispatch notes recorded aggregate quantities (e.g., "50 Panels", "1 Inverter") without capturing serial numbers at the point of warehouse picking. Consequently, when field equipment malfunctioned months or years later, OEM warranty claims were systematically rejected because manufacturers could not verify whether the failed unit originated from their authorized project supply. Furthermore, Stage 11 (Solar Asset Register & IoT Telemetry) could not establish a verifiable digital twin without manually re-auditing every panel on the roof.
2. **Missing E-Way Bill & Transporter Statutory Enforcement:** In India, GST regulations mandate that any consignment of goods with a consignment value exceeding ₹50,000 must be accompanied by an electronic E-Way Bill and transport manifest (Part A & Part B). Unsystematic dispatches frequently released trucks without verifying E-Way Bill validity or recording transporter GSTIN, vehicle registration, and driver details, resulting in vehicle impoundments, seizure of goods, and severe statutory tax penalties.
3. **Uncontrolled Over-Dispatch & Inventory Leakage:** Warehouse storekeepers frequently dispatched extra cable coils, structural fasteners, or spare modules under informal site requests without verifying against the contractually frozen Sales Order Bill of Materials (BOM). This caused substantial inventory shrinkage, unbudgeted project cost overruns, and distorted project gross margins.
4. **Lack of Phased / Staged Consignment Tracking:** Solar installations rarely receive 100% of materials in a single truckload. Sites require phased delivery: Phase 1 (Civil Footings & Module Mounting Structures), Phase 2 (Solar PV Modules), and Phase 3 (Inverters, AC/DC Cabling, Combiner Boxes & BOS). Standard systems treated delivery as a single binary event, leaving project engineers blind to which specific components had reached the site versus what remained in transit.
5. **No Proof of Delivery (POD) Loop Closure:** Materials dispatched from the warehouse were assumed delivered the moment the truck left the gate. When materials arrived damaged, incomplete, or with transit shortages, store teams and site teams engaged in finger-pointing, lacking a formal digital or photographic Proof of Delivery (POD) sign-off.
6. **Absence of Warehouse Dispatch SLA Governance:** Store teams lacked turnaround time (TAT) targets. Material requests lingered in warehouse queues for days or weeks without alert escalations, directly causing installation crews to idle on site and incurring expensive labor standing costs.

---

## Decision

We establish an authoritative, comprehensive architectural standard for Stage 07 Material Dispatch, extending ERPNext's standard `tabDelivery Note` (`is_submittable = 1`) and Frappe v15's Serial and Batch Bundle architecture within `solar_module`:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         STAGE 07: MATERIAL DISPATCH ARCHITECTURE OVERVIEW                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Stage 06: Sales Order Baseline Frozen]                                                        │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Store Manager Delivery Task Spawned] ──▶ Reassignable to [Store Assistant]                    │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Create Delivery Note] ◀── Binds SO, Project, Frozen BOM & Central Warehouse                   │
│           │                                                                                      │
│           ├──────────────────────────────────────────────────────────────────────┐               │
│           ▼                                                                      ▼               │
│   [100% Serial Scanning Gate]                                     [Logistics & E-Way Gate]       │
│   • Enforces 2D Barcode Scan for Modules & Inverters              • Transporter GSTIN & Name     │
│   • Frappe v15 Serial and Batch Bundle (SABB)                     • Vehicle Registration No      │
│   • Stock Availability & Duplicate Guard                          • Driver Name & 10-digit Phone │
│           │                                                       • E-Way Bill No (Mandatory >50k)│
│           │                                                                      │               │
│           └──────────────────────────────────┬───────────────────────────────────┘               │
│                                              ▼                                                   │
│                           [Pre-Dispatch Quality Inspection Checklist]                            │
│                           • Module frame integrity & glass check                                 │
│                           • Inverter seal & accessory kit verification                           │
│                           • Cable drum seal & transit insurance check                            │
│                                              │                                                   │
│                                              ▼                                                   │
│                           [Submit Delivery Note (docstatus = 1)]                                 │
│                           • Deducts stock from Central Store Warehouse                           │
│                           • Debits Goods-in-Transit / Site Warehouse                             │
│                           • Real-time WhatsApp/SMS dispatch alert to Customer & Site             │
│                                              │                                                   │
│                                              ▼                                                   │
│                           [Digital Proof of Delivery (POD) Handover]                             │
│                           • Site Engineer / Project Engineer confirms physical receipt           │
│                           • Photographic evidence & digital signature captured                   │
│                           • Store Task Marked Completed ──▶ Stage 08 Installation Unlocked       │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Standard ERPNext `Delivery Note` as the Core Logistics Ledger

Rather than inventing a parallel custom dispatch entity, Stage 07 extends ERPNext's native `tabDelivery Note` (`is_submittable = 1`):

- **Core Ledger Mechanics:** Automatically manages stock balance deductions, item valuation, general ledger entries for inventory in transit, and currency precision.
- **Custom Solar EPC Namespace:** Cleanly separated through the `custom_*` prefix in `solar_module` (e.g. `custom_is_solar_dispatch`, `custom_sales_order_ref`, `custom_project_ref`, `custom_dispatch_stage`, `custom_eway_bill_no`, `custom_pod_status`).
- **Parent-Child Integrity:** Items in `tabDelivery Note Item` map directly back to the frozen Sales Order baseline items (`tabSales Order Item`).

### 2. High-Speed 100% Serialized Asset Tracking via Frappe v15 Serial and Batch Bundle (SABB)

To guarantee 100% traceability for warranty, insurance, and Stage 11 IoT telemetry:

- **Mandatory Serial Enforcement:** All items categorized as `Solar Module` or `Solar Inverter` (`has_serial_no = 1`) require mandatory barcode scanning before submission.
- **Native SABB Integration:** Dispatches instantiate native Frappe v15 `tabSerial and Batch Bundle` records linked to each line item, binding exact `tabSerial No` records.
- **Validation Engine (`SolarSerialScanningService`):**
  - Asserts that every scanned serial exists in the specified source warehouse (`From Warehouse`).
  - Asserts that no scanned serial is already reserved, delivered, or duplicated within the same consignment.
  - Compares the count of scanned serials strictly against line item quantity ($N_{\text{scanned}} == Q_{\text{dispatched}}$).

### 3. Phased Consignment Governance & Over-Dispatch Hard Stop

Solar EPC projects require staged deliveries tailored to site readiness:

- **Five Standard Consignment Stages (`custom_dispatch_stage`):**
  1. `Phase 1 - Civil & Structure` (Piles, base plates, MMS galvanized channels, fasteners).
  2. `Phase 2 - Solar PV Modules` (Solar panels, clamps, MC4 connectors).
  3. `Phase 3 - Inverters & BOS` (Inverters, ACDB, DCDB, AC/DC solar cables, earthing electrodes, lightning arresters).
  4. `Phase 4 - Complete Single Dispatch` (For compact residential rooftop projects $\le 10 \text{ kW}$).
  5. `Ad-hoc / Balance Dispatch` (Remedial replacements or authorized minor balance deliveries).
- **Hard Over-Dispatch Boundary:** The system automatically computes cumulative dispatched quantities per item code:
  $$\sum Q_{\text{dispatched}} + Q_{\text{current}} \le Q_{\text{sales\_order\_baseline}}$$
  Any attempt to dispatch quantities exceeding the Sales Order BOM is strictly blocked. An Admin-governed override flag (`custom_over_dispatch_approved`) is required to authorize excess quantities.

### 4. Mandatory Statutory E-Way Bill & Transporter Manifest Gate

To insulate the enterprise from GST penalties, seizures, and transport delays:

- **Statutory Enforcement Threshold:** For all consignments whose total net taxable value exceeds ₹50,000 (configurable via `Solar Dispatch Settings`), the system enforces:
  - `custom_transporter_name` & `custom_transporter_gstin` (Validated via 15-character GSTIN regex).
  - `custom_vehicle_no` (Standard Indian registration plate format uppercase alphanumeric regex).
  - `custom_driver_name` & `custom_driver_phone` (10-digit mobile number).
  - `custom_eway_bill_no` (12-digit Indian E-Way Bill number) and `custom_eway_bill_validity` (Datetime).
  - `custom_eway_bill_doc` (Mandatory attached official PDF).

### 5. Pre-Dispatch Quality Inspection Checklist

Before physical loading onto the transport vehicle:

- Store personnel must verify and pass the `Solar Dispatch Pre-Inspection Checklist`:
  - Physical inspection of PV module frames, glass integrity, and junction boxes.
  - Inverter carton seal, warranty documentation, and mounting bracket kit verification.
  - Cable drum seal, conductor cross-section, and voltage grade verification.
  - Transit insurance active cover verification.
- Submission is hard-gated until all mandatory checklist rows are signed off with `status = "Passed"`.

### 6. Digital Proof of Delivery (POD) & Site Receipt Loop Closure

To eliminate transit disputes and ensure transparent handoff to site execution:

- Upon physical arrival at the project site, the `Project Engineer` or `Site Supervisor` inspects the delivery and executes the digital POD via the `/solar` mobile portal:
  - Records recipient name, contact phone, and exact GPS delivery location.
  - Captures digital on-screen signature and unboxing / truck unloading photographs.
  - Logs item acceptance status: `Delivered in Full`, `Partially Received with Shortage`, or `Damaged in Transit`.
- Successfully recording the POD:
  1. Sets `custom_pod_status` to `Delivered at Site`.
  2. Updates `tabSales Order` overall delivery progress percentage.
  3. Automatically marks the originating Store Delivery `Task` as `Completed`.
  4. Formally unlocks Stage 08 (`Zone-Based Installation Execution & Mobile DPR`) in the Project Lifecycle Stepper.

### 7. Store Dispatch SLA Engine & Delay Accountability

- **Turnaround Time (TAT) Target:** Store dispatch SLA is established at **48 Hours** from the moment Stage 06 confirms the Sales Order and spawns the Store Delivery Task (customizable by `Admin` in `tabSolar Dispatch Settings`).
- **Real-Time Countdown:** The Store Workbench on `/solar` and the Desk form display real-time SLA countdown timers.
- **Escalation & Mandatory Delay Logging:** If the 48-hour threshold expires without Delivery Note submission, the SLA status transitions to `Overdue`, alert notifications are broadcast to the `Store Manager` and `Director`, and the operator is mandated to provide a categorized `custom_dispatch_delay_reason` and `custom_dispatch_delay_remarks` before saving.

---

## Consequences

### Positive Consequences

- **100% Asset Provenance:** Every installed module and inverter is cryptographically bound to the project site, eliminating OEM warranty rejection risks and laying the foundation for Stage 11 digital asset management.
- **Zero GST Transit Penalties:** Mandatory E-Way bill and vehicle manifest validation prevents highway impoundments and legal disputes.
- **Total Working Capital & Inventory Protection:** Hard over-dispatch barriers stop unauthorized material leakage from central warehouses.
- **Flawless Multi-Stage Logistics:** Clear separation into structured consignment phases provides transparent visibility to both warehouse and site execution teams.
- **Real-Time SLA Governance:** Automated countdowns and escalation alerts prevent store-side bottlenecks from delaying project commissioning.

### Negative / Trade-Off Consequences

- **Barcode Scanning Overhead:** Scanning 50–100 individual module barcodes per rooftop installation requires warehouse staff to utilize 2D barcode scanners or smartphones, introducing 10–15 minutes of staging labor per consignment.
  - _Mitigation:_ The system implements a rapid-fire bulk scanning station in the `/solar` Store Workbench with continuous audio feedback (chime on success, buzz on error) and allows bulk CSV/text paste ingestion for pallet-level barcode lists.
- **Strict Submission Prerequisites:** Operators cannot create casual, quick dispatches without transport and checklist data.
  - _Mitigation:_ The system supports full `Draft` saving, enabling the store team to build picklists, scan items gradually, and attach E-Way bills once generated by the store team.

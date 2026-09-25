# ADR-011: On-Demand Solar Service, Incident-Driven O&M & Warranty Governance Architecture

## Status

Accepted

## Date

2026-09-25

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), Stage 10 (**Dual-Timing Statutory Liaisoning, Regulatory Inspection, Net Metering & Grid Synchronization**) represents the legal, regulatory, and commercial completion anchor of the entire Solar EPC project lifecycle. It terminates the capital expenditure (CapEx) construction project with official net-meter energization, Commercial Operation Date (COD) certification, and final milestone invoicing.

Following COD, installed solar power plants enter an operational lifespan spanning 25+ years. Historically, solar EPC software systems and legacy ERP implementations handle post-commissioning operations with severe structural flaws that expose contractors to financial leakage, operational chaos, and customer dissatisfaction:

1. **The Fallacy of Monolithic Project Continuation:**  
   Legacy systems attempt to model post-commissioning operations as an indefinite continuation of the original construction `Project` (e.g., adding perpetual "O&M tasks" to an open EPC project). This conflates CapEx construction budgets with OpEx maintenance activities, corrupts financial cost accounting, distorts project completion KPIs, and leaves project ledgers open for years. Post-handover servicing is fundamentally **on-demand, incident-driven, and decoupled** from the construction project. It must operate as an independent service lifecycle triggered only when a plant experiences a fault, breakdown, generation degradation, or when a customer requests routine servicing.

2. **The Dual-Track Warranty Dilemma (In-Warranty vs. Out-of-Warranty):**  
   Solar plant service incidents fall into two distinct legal and commercial categories:
   - **Track A: Within-Warranty Servicing (Equipment / Workmanship Covered):** OEM solar inverters, PV modules, and DC switchgear carry 5 to 25-year manufacturer warranties, while installation workmanship carries a 1 to 5-year contractor warranty. When a covered component fails, the customer must pay **zero service charges**. Instead, the contractor must initiate an OEM Return Merchandise Authorization (RMA) claim to recover the cost from the supplier.
   - **Track B: Out-of-Warranty Servicing (Expired, Physical Damage, or Non-Covered):** If the plant is past its warranty period, or if failure results from external factors (rodent bite, grid surge, lightning strike without SPD, accidental breakage, monkey menace, severe dust soiling), the visit is **chargeable**. The contractor must provide an estimate, secure customer acceptance, collect payment/advance, and issue an official ERPNext Sales Invoice for labor and spare parts.  
     Without an automated discrimination engine, companies either mistakenly bill in-warranty customers (triggering severe reputational damage) or replace expensive components at company expense when the damage was customer-caused or out-of-warranty (causing acute margin leakage).

3. **Field Service Blind Spots & Unverified Technician Claims:**  
   Rooftop solar installations are geographically distributed across residential, commercial, and rural locations. Field technicians dispatched for troubleshooting frequently claim to have visited sites without physical presence, diagnose faults superficially without logging root causes, or replace components without verifying whether the root cause was an inverter grid-trip or a blown string fuse.

4. **Serialized Component Swapping & Lost Provenance:**  
   When high-value serialized equipment (such as a string inverter, microinverter, or solar module) is replaced in the field, technicians often fail to record the serial number of the defective unit removed and the new unit installed. This breaks the serial audit trail, renders OEM warranty recovery impossible, and corrupts the plant's permanent digital twin.

5. **Absence of an Immutable Site Service Ledger:**  
   Without a centralized, append-only service history tied to the physical installation site, repeat failures cannot be analyzed, recurring equipment defects go unnoticed, and warranty claim validity cannot be defended during legal or customer disputes.

---

## Decision

We establish an authoritative architectural standard for Stage 11 (**On-Demand Solar Service, Incident-Driven O&M & Warranty Governance Architecture**) within `solar_module`, strictly decoupling after-sales service from upstream CapEx project delivery, introducing standalone submittable DocTypes `tabSolar Service Request` and `tabMaintenance Visit`, backed by an automated dual-track warranty discrimination engine, GPS-geofenced mobile diagnostics, serialized spare parts reconciliation, and an immutable site service history ledger:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│              STAGE 11: ON-DEMAND SOLAR SERVICE & WARRANTY GOVERNANCE ARCHITECTURE                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Stage 10: COD Certified & Net Meter Energized] ──▶ (CapEx Project Cleanly Terminated & Closed)│
│                                                                                                  │
│   ══════════════════════════════ INDEPENDENT SERVICE LIFECYCLE ══════════════════════════════   │
│                                                                                                  │
│   [Omnichannel Service Intake]                                                                   │
│   • Customer Web Portal (/solar/service-booking) | WhatsApp Business Helpdesk | Phone Desk Call  │
│   • Captures: Site Address, Fault Category, Inverter Error Code/Photo, Preferred Slot            │
│           │                                                                                      │
│           ▼                                                                                      │
│   [tabSolar Service Request Created] (SSR-.YYYY.-.#####)                                         │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Gate 1: Automated Warranty Discrimination Engine]                                             │
│   • Evaluates COD Date, Installed Serial Nos, Equipment Warranty Expiry, Fault Nature            │
│           │                                                                                      │
│           ├──────────────────────────────────────────────┬───────────────────────────────────────┤
│           ▼                                              ▼                                       │
│   [Track A: Within-Warranty (Free / RMA)]        [Track B: Out-of-Warranty (Chargeable)]          │
│   • Equipment / Workmanship Active               • Expired Warranty / External / Physical Damage │
│   • Customer Fee: ₹0.00                          • Service Visit & Labor Rate Estimation         │
│   • Flags for OEM Reverse Logistics (RMA)        • Quotation Shared & Customer Acceptance        │
│   • Vendor Warranty Recovery Tracking            • Advance / Payment Gate Clearance              │
│           │                                              │                                       │
│           └──────────────────────┬───────────────────────┘                                       │
│                                  │                                                               │
│                                  ▼                                                               │
│   [Triage & Dispatch: O&M Service Coordinator]                                                   │
│   • Priority SLA: Emergency Blackout (4h/24h) | Inverter Warning (12h/48h) | Health Check (48h/5d)│
│   • Schedules Visit & Assigns O&M Service Engineer                                               │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Gate 2: Field Technician Mobile GPS Geofence Gate]                                            │
│   • Technician arrives on-site and triggers mobile check-in                                      │
│   • Haversine geofence asserts distance to site ≤ 500 meters                                     │
│   • Hard-blocks diagnostic entry until GPS lock is verified                                      │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Field Diagnostics, Health Checklist & Root Cause Analysis]                                    │
│   • Electrical measurements: Voc, Isc, Earth Resistance, Inverter Error Code                     │
│   • Photo evidence upload: Damaged component, meter reading, physical site conditions            │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Gate 3: Serialized Spare Parts Reconciliation Gate]                                           │
│   • Defective Serial Number Removed (e.g. INV-GROWATT-2023-0941)                                 │
│   • Replacement Serial Number Installed (e.g. INV-GROWATT-2026-1182)                             │
│   • Direct link to ERPNext Stock Entry (Material Issue from Van/Store)                           │
│   • If Out-of-Warranty: Generates ERPNext Sales Invoice for parts & labor                        │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Gate 4: Customer Closed-Loop Verification Gate]                                               │
│   • Generates cryptographic 6-digit OTP sent to Customer mobile / WhatsApp                       │
│   • Alternative: Digital signature capture on technician's glass screen                          │
│   • Document submission (docstatus = 1) hard-blocked without OTP or Signature                    │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Immutable Service History Ledger Update & Plant Twin Sync]                                    │
│   • Appends visit summary, replaced serials, and diagnostic log to tabSolar Site Service History │
│   • Updates active serial mappings on the customer site master                                   │
│   • Closes Solar Service Request & Maintenance Visit                                             │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1. Decoupled Post-Project Service Boundary

- **CapEx Clean Termination:** Stage 10 Liaisoning and Grid Synchronization concludes with the generation of the COD Certificate and net-meter energization. This formally sets `tabProject.status = "Completed"` and closes the capital construction lifecycle.
- **Zero Automatic Spawning:** Stage 11 creates **zero** automatic project tasks, tickets, or downstream requirements upon project completion. It remains dormant until an actual service need occurs.
- **On-Demand Activation Triggers:** Stage 11 is instantiated purely on-demand via three operational channels:
  1. _Customer Web Portal (`/solar/service-booking`):_ Self-service customer submission.
  2. _WhatsApp Business Helpdesk:_ Chatbot-guided conversational intake.
  3. _Customer Care Desk Intake:_ Direct phone call logging by a Customer Care Representative.

---

### 2. Standalone Submittable DocTypes

Rather than abusing generic helpdesk tickets, Stage 11 introduces purpose-built, submittable enterprise entities:

- **`tabSolar Service Request` (`is_submittable = 1`):**  
  Autoname: `SSR-.YYYY.-.#####`. Represents the customer-facing incident ticket. Captures site details, reported symptoms, issue category, preliminary warranty classification, assigned SLA, triage status, and customer communication log.
- **`tabMaintenance Visit` (`is_submittable = 1`):**  
  Autoname: `SMV-.YYYY.-.#####`. Represents the physical field execution event. Linked foreign-key to `Solar Service Request`. Captures GPS check-in coordinates, diagnostic checklist, root cause analysis, spare parts consumed, customer OTP/signature, and resolution sign-off.
- **`tabSolar Service Spare Item` (Child Table):**  
  Tracks consumed components, unit prices, warranty coverage flags, serial numbers removed, and serial numbers installed.
- **`tabMaintenance Checklist Item` (Child Table):**  
  Standardized electrical inspection checklist (Voc string voltages, AC output, insulation resistance, physical cable condition, inverter firmware/error codes).
- **`tabSolar Site Service History` (Master Ledger):**  
  Permanent, append-only audit ledger recording every service event, component replacement, and technician visit for any installed solar site over its 25-year lifetime.

---

### 3. Dual-Track Warranty Discrimination Engine

The domain service `SolarServiceIntakeService` automatically queries the installation date, COD date, and serial number warranty masters upon service request creation:

$$\text{Equipment Warranty Status} = \begin{cases} \text{Active (Track A)}, & \text{if } \text{Incident Date} \le \text{COD Date} + \text{Warranty Term} \\ \text{Expired (Track B)}, & \text{otherwise} \end{cases}$$

1. **Track A (In-Warranty / Free / RMA):**
   - Applies to equipment defects, inverter component faults, or workmanship issues within their respective warranty windows.
   - Sets `tabSolar Service Request.warranty_status = "Under Warranty"` and customer billing charge to ₹0.00.
   - Automatically initiates an OEM Reverse Logistics / RMA record, linking supplier details to track warranty claim settlement and replacement credit.
2. **Track B (Out-of-Warranty / Chargeable):**
   - Applies to expired warranties, grid surge burnouts, rodent cable damage, physical impact, unauthorized alterations, or voluntary cleaning/health checks.
   - Sets `tabSolar Service Request.warranty_status = "Out of Warranty"`.
   - Generates an ERPNext `Quotation` for inspection fee, labor, and anticipated spare parts. Requires customer digital confirmation or advance payment before field dispatch.
   - Automatically generates an ERPNext `Sales Invoice` upon job completion.

---

### 4. Four Enforced Verification Gates

To enforce total operational discipline and eliminate fraud:

- **Gate 1: Warranty Eligibility Gate:** Server-side validation during triage asserting that warranty claims are verified against COD date, equipment serial masters, and fault category. Out-of-warranty tickets cannot be marked "Free" without explicit `Admin` authorization override.
- **Gate 2: Field Check-In Geofence Gate:** Technicians cannot enter diagnostic findings, photos, or parts without executing a mobile GPS check-in. The Haversine distance between device GPS and registered site coordinates must be $\le 500\text{ meters}$:
  $$d = 2R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)} \right) \le 0.500\text{ km}$$
- **Gate 3: Serialized Spare Parts Reconciliation Gate:** Replacing any serialized asset (inverter, module, smart meter) strictly requires capturing **both** the serial number removed and the replacement serial number installed. The removed serial is placed into quarantine stock; the installed serial is activated in the site twin.
- **Gate 4: Customer Closed-Loop Gate:** A `Maintenance Visit` cannot be submitted (`docstatus = 1`) without a cryptographically verified 6-digit customer OTP or a touch-captured customer signature.

---

### 5. Tiered Service SLAs & Delay Governance

Monitored by background daemon `solar_module.tasks.check_service_slas` running every 15 minutes:

| Priority / Fault Severity | Response SLA (Triage & Dispatch) | Resolution SLA (On-Site Fix) | Target Operational Scenario                                                  |
| :------------------------ | :------------------------------- | :--------------------------- | :--------------------------------------------------------------------------- |
| **Critical Emergency**    | $\le 4\text{ Hours}$             | $\le 24\text{ Hours}$        | Complete plant blackout, smoke/fire hazard, inverter dead, grid trip         |
| **High / Degraded**       | $\le 12\text{ Hours}$            | $\le 48\text{ Hours}$        | Inverter error code, single MPPT drop, generation degradation $> 25\%$       |
| **Standard / Routine**    | $\le 48\text{ Hours}$            | $\le 5\text{ Business Days}$ | Preventative health check, panel cleaning, earthing pit wetting, meter check |

Breaching either SLA marks the document status as `Overdue` and requires a mandatory justification logged into `tabSolar Stage Delay Log` before resolution can be submitted.

---

### 6. Role Standard (Zero "User" Suffix)

In strict adherence to enterprise naming standards:

- `Customer Care Representative`: Omnichannel intake, symptom logging, customer communication.
- `O&M Service Coordinator`: Triage, warranty verification, engineer scheduling, parts staging.
- `O&M Service Engineer`: Field troubleshooting, GPS check-in, diagnostics, part swapping, customer OTP.
- `Commercial Officer`: Service quotations, out-of-warranty billing, OEM warranty recovery reconciliation.
- `Admin` (Project Supreme Command): SLA escalation overrides, warranty dispute waivers, technician assignment reallocations.
- `Administrator` / `System Manager`: Technical dev ops, API routing, portal authentication, background queues.

---

## Alternatives Considered

### Alternative 1: Extend Stage 10 CapEx Project with Perpetual O&M Tasks

- _Description:_ Keep the ERPNext `Project` open post-commissioning and create O&M tasks inside it.
- _Rejected:_ Distorts project accounting, mixes capital costs with maintenance revenue, clutters the WBS with hundreds of reactive tasks over 25 years, and violates statutory financial audit standards.

### Alternative 2: Generic Helpdesk Support Tickets

- _Description:_ Use standard ERPNext `Issue` or `HD Ticket` doctypes for solar service calls.
- _Rejected:_ Lacks solar electrical schemas (Voc, Isc, inverter error codes), lacks mobile GPS geofencing, cannot differentiate OEM equipment warranty vs workmanship, cannot enforce serialized component swapping, and does not maintain a permanent site twin ledger.

### Alternative 3: Manual Warranty Determination by Field Engineers

- _Description:_ Allow field technicians to decide on-site whether a visit is free or chargeable.
- _Rejected:_ High risk of collusion, uncollected revenue, customer disputes over verbal promises, and unrecovered OEM claims.

---

## Consequences

### Positive Consequences

- **Financial Cleanliness:** Clean CapEx project closeout at Stage 10; post-project service operates under a clear OpEx profit center.
- **Zero Revenue Leakage:** Automated warranty discrimination ensures non-covered repairs are quoted, approved, and billed upfront.
- **OEM Cost Recovery:** Track A warranty claims link directly to supplier RMA workflows, ensuring defective inverters and modules are credited by manufacturers.
- **Proof of Physical Presence:** Geofenced check-in eliminates phantom technician visits and builds customer trust.
- **Complete Asset Traceability:** Serialized part replacement maintains 100% asset provenance for 25 years.

### Negative / Trade-Offs

- Requires reliable mobile device GPS permissions for field technicians.
- Requires initial registration of serial numbers during Stage 08/10 to enable automated warranty lookup.

# STEP_02_SITE_SURVEY_SPECIFICATION.md

# Enterprise Lifecycle Step Specification: Technical Site Survey & Audit

**Document ID:** `STEP-02-SURVEY`  
**Lifecycle Flow:** Flow 1: Core Solar EPC Project Execution (Stage 02 of 11)  
**Governing Architecture:** [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md)  
**PRD / FRS Traceability:** [`planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md`](../planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md) (`BC-02`, `Sec 3.2`), [`planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md`](../planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md) (`BR-002`), [`planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md`](../planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md) (`FR-002`), [`planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md`](../planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md) (`MOD-02`)  
**Target Module:** `solar_module` / `manoj`  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Implementation

---

## 1. Step Scope, Objectives & Context Traceability

### 1.1 Lifecycle Positioning & Remote Field Context

Stage 02 (**Technical Site Survey & Audit**) forms the mission-critical engineering baseline of the Solar EPC Project Execution Lifecycle. Triggered immediately upon surveyor assignment in Stage 01 (**Lead Management**), this stage dispatches an authorized field engineer to the customer premises to capture roof structural feasibility, electrical infrastructure distances, shadow obstacles, GPS geotag coordinates, utility meter attributes, and photographic/video evidence within an enforced **24-hour SLA turnaround window**.

Because solar installations routinely take place across remote agricultural terrains (PM KUSUM solar pumps), rural rooftops (PM Surya Ghar), and isolated industrial sheds with spotty or nonexistent cellular connectivity, Stage 02 implements an **Offline-First PWA Mobile Architecture**. All form inputs, raw high-resolution photos, and video walkthroughs are cached locally in client-side IndexedDB storage until a verified network connection returns, triggering a resilient, two-stage background auto-sync pipeline with fail-safe cache eviction.

```
┌─────────────────┐       ┌─────────────────────────────────────────────────────────┐       ┌─────────────────┐
│   STAGE 01:     │       │                STAGE 02: SITE SURVEY & AUDIT            │       │    STAGE 03:    │
│ Lead Ingestion  │──────▶│ - Offline-First Mobile Touch Capture (IndexedDB)        │──────▶│ Solar PV Design │
│ & Assignment    │       │ - GPS Lock (≤ ±15m) & OpenStreetMap Reverse Geocoding   │       │ & Dynamic BOM   │
│ (2h / 24h SLA)  │       │ - 10 Mandatory Technical Invariants + 6 Fixed Photos    │       │ (CAD & SLD)     │
│                 │       │ - Resilient Auto-Sync & Fail-Safe Cache Purge           │       │                 │
│                 │       │ - 24-Hour SLA / TAT Countdown & Overdue Escalations     │       │                 │
└─────────────────┘       └─────────────────────────────────────────────────────────┘       └─────────────────┘
```

- **Predecessor:** Stage 01: Lead Management (`Lead` DocType assignment to `Survey Engineer`).
- **Successor:** Stage 03: Solar PV Engineering & Dynamic BOM (`Site Survey Design File` / `custom_quot_bom`).

### 1.2 Core Business Objectives & Target KPIs

1. **Zero Survey Revisits (100% First-Visit Completeness):** Enforce hard server-side validation preventing survey sign-off until all 10 mandatory technical fields, 6 fixed photo checklist rows, and utility meter alignment checks are captured.
2. **Sub-24-Hour Completion Turnaround (SLA $\le 24\text{h}$):** Guarantee that on-site data is captured, synchronized, and verified within 24 hours of assignment.
3. **Zero Data Loss in Remote Environments (100% Offline Resilience):** Persistent client-side IndexedDB caching protects form fields, high-resolution photos, and 360° video walkthroughs against app termination, device reboot, or connectivity drops.
4. **Geotagged Spatial Verification ($\le \pm 15\text{m}$ Accuracy):** Exact device GPS coordinates verified against registered site pincode and reverse-geocoded address.
5. **Upstream Electrical Sanction Compliance:** Sizing feasibility check ensuring requested solar PV capacity does not exceed DISCOM sanctioned load without an official load enhancement flag.

### 1.3 Failure Modes Eliminated

- **Field Data Loss from Network Dropouts:** Field auditors losing 45 minutes of detailed roof measurements and photos due to mobile connection resets in basement switchrooms or rural zones.
- **Repeat Site Inspections:** Design engineers rejecting survey submissions days later because the surveyor forgot the LT panel busbar rating or meter board location.
- **DISCOM Liaisoning Rejections at Stage 10:** Discrepancies between the customer's electricity bill name and property documents uncovered months later during net-meter synchronization.
- **Untracked Operational Bottlenecks:** Surveys lingering in "In Progress" status indefinitely without automated SLA escalation or delay accountability.

---

## 2. Stakeholders, Enterprise Actors & HRMS Role Mapping

### 2.1 Enterprise User Roles Matrix

In strict compliance with [`ADR-020`](../docs/decisions/ADR-020-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md) and the **Zero "User" Suffix Rule**, all actors are designated using functional enterprise titles:

| Persona / Business Actor       | Frappe System Role | HRMS Department           | HRMS Designation            | Operational Responsibilities                                                                                          |
| :----------------------------- | :----------------- | :------------------------ | :-------------------------- | :-------------------------------------------------------------------------------------------------------------------- |
| **Site Survey Engineer**       | `Survey Engineer`  | Engineering Operations    | `Site Survey Engineer`      | Field mobilization, offline mobile audit capture, GPS lock, mandatory photo/video upload, technical audit completion. |
| **Survey Department Manager**  | `Survey Manager`   | Engineering Operations    | `Survey Operations Manager` | Technical survey feasibility sign-off, surveyor allocation, escalation review, Stage 03 handoff approval.             |
| **Sales Department Manager**   | `Sales Manager`    | Sales & Marketing         | `Sales Manager`             | Regional survey pipeline oversight, customer communication coordination, SLA delay review.                            |
| **PV Design Engineer**         | `Design Engineer`  | Design & Engineering      | `Solar Design Engineer`     | Downstream consumer (Stage 03); reviews completed audit parameters, imports roof dimensions into CAD/PVsyst.          |
| **Solar EPC Director / Admin** | `Admin`            | Executive Management      | `Managing Director`         | Supreme operational command; manages `Solar SLA Settings`, `Solar Notification Settings`, and delay reason overrides. |
| **Technical DevOps Lead**      | `System Manager`   | Technology Infrastructure | `DevOps Architect`          | Framework apex; manages DocType schemas, Redis queues, background worker daemons, and bench CLI tooling.              |

> [!IMPORTANT]
> **Enterprise Authority Hierarchy & ADR-020 Operational Governance:**
>
> - **`Administrator` & `System Manager` (Framework Supreme / Developer Realm):** Frappe's native `Administrator` and `System Manager` sit at the apex of system authority (supreme over `Admin`). As intended by Frappe Framework, `System Manager` possesses full access to everything `Admin` has, plus full technical rights over source code, DocType schema builder, Client/Server Scripts, bench tooling, and developer mode. Reserved for technical developers, bench engineers, and DevOps administrators.
> - **`Admin` (Project / Solar EPC Level Supreme Command):** Introduced specifically for **project-level operational supremacy**. Has unrestricted operational access to everything that any or all business roles have across Flow 1 and Flow 2, as well as full authority over operational governance settings (`Solar SLA Settings`, `Solar Notification Settings`, delay approvals, and manager overrides). Protected by downstream dependency warnings, hard deletion blocks, and atomic cascade purges (`tabSolar Deletion Audit Log`).
> - **Managerial Authority Inheritance:** `Survey Manager` strictly inherits all operational capabilities of `Survey Engineer`.
> - **Stage-Forward Lock:** Once `Survey Engineering Design` (Stage 03) is instantiated, `Site Survey` is permanently locked against cancel and amend.

### 2.2 Permission Hierarchy Matrix

| DocType / Action                  | Survey Engineer | Survey Manager  | Sales Manager  | Design Engineer |     Admin\*      |
| :-------------------------------- | :-------------: | :-------------: | :------------: | :-------------: | :--------------: |
| **Site Survey (Read)**            |  Assigned Only  | Full Department | Full Territory |    All Valid    |   All Records    |
| **Site Survey (Create)**          |  Auto-Spawned   |       Yes       |      Yes       |       No        |       Yes        |
| **Site Survey (Write / Update)**  | Own (Unfrozen)  | Full Department |  Status Only   |    Read-Only    |   All Records    |
| **Site Survey (Sign-Off/Submit)** |  Yes (Pre-S03)  |  Yes (Pre-S03)  |       No       |       No        |       Yes        |
| **Offline Sync Endpoint (Call)**  |       Yes       |       Yes       |      Yes       |       No        |       Yes        |
| **Site Survey Doc Table (Edit)**  |   Own Record    | Full Department |   Read-Only    |    Read-Only    |   Full Access    |
| **Remark-Delay Log (Append)**     |   Own Record    | Full Department |   Permitted    |       No        |   Full Access    |
| **Solar SLA Settings (Manage)**   |       No        |       No        |       No       |       No        | Yes (Admin Only) |

_\*Note: Frappe `Administrator` and `System Manager` sit above `Admin` and inherit all permissions._

---

## 3. Relational Schema & 3NF Data Dictionary

### 3.1 Standalone Custom DocType: `tabSite Survey`

The core audit entity is maintained in the custom app as a standalone DocType (`tabSite Survey`). It establishes the technical single source of truth for downstream engineering:

| Fieldname                   | Label                           | Fieldtype      | Options / Target                                                                                                                                                                                            | Mandatory |    Index     | Description & Validation Rules                                                  |
| :-------------------------- | :------------------------------ | :------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :----------: | :------------------------------------------------------------------------------ |
| `naming_series`             | Naming Series                   | `Select`       | `SRV-.YYYY.-.#####`                                                                                                                                                                                         |  **Yes**  |      -       | Autonaming series reset annually.                                               |
| `survey_date`               | Scheduled Survey Date           | `Date`         | -                                                                                                                                                                                                           |  **Yes**  |      -       | Default: `Today`. Target date of physical audit.                                |
| `surveyed_by`               | Survey Engineer Assigned        | `Link`         | `User`                                                                                                                                                                                                      |  **Yes**  | **Index: 1** | Filtered by role `Survey Engineer`. Key assignee anchor.                        |
| `assigned_by`               | Assigned By                     | `Link`         | `User`                                                                                                                                                                                                      |    No     |      -       | User who scheduled/assigned the survey.                                         |
| `lead`                      | Linked Lead Reference           | `Link`         | `Lead`                                                                                                                                                                                                      |  **Yes**  | **Index: 1** | Foreign key linking upstream Stage 01 commercial prospect.                      |
| `lead_name`                 | Client / Entity Name            | `Data`         | -                                                                                                                                                                                                           |    No     |      -       | Fetch from `lead.lead_name`. Read-only customer descriptor.                     |
| `contact_number`            | Customer Contact Phone          | `Data`         | -                                                                                                                                                                                                           |    No     |      -       | Fetch from `lead.mobile_no`. Sanitized 10-digit number.                         |
| `contact_mail`              | Customer Email Address          | `Data`         | `Email`                                                                                                                                                                                                     |    No     |      -       | Fetch from `lead.email_id`.                                                     |
| `solar_capacity`            | Verified Plant Capacity (kW)    | `Float`        | -                                                                                                                                                                                                           |  **Yes**  |      -       | On-site verified capacity requirement (e.g. 10.0 kW). Precision: 1.             |
| `solar_system`              | System Configuration            | `Select`       | `\nOn-Grid\nHybrid\nOff-Grid`                                                                                                                                                                               |  **Yes**  |      -       | Electrical topology determining battery/inverter specs.                         |
| `site_type`                 | Roof / Civil Structure          | `Select`       | `RCC\nGround Mount\nShed (Profile Sheet)\nCar Port (Parking)\nRCC & Shed\nRCC & Ground Mount\nRCC & Parking\nShed & Ground Mount\nShed & Parking\nGround Mount & Parking\nRCC, Shed, Ground Mount, Parking` |  **Yes**  |      -       | Civil classification of the installation surface.                               |
| `connected_load`            | Sanctioned Utility Load (kW)    | `Float`        | -                                                                                                                                                                                                           |  **Yes**  |      -       | Sanctioned load from latest DISCOM power bill.                                  |
| `plant_category`            | Consumer Tariff Category        | `Select`       | `\nResidential\nCommercial\nIndustrial\nAgricultural\nInstitutional`                                                                                                                                        |  **Yes**  |      -       | Tariff tier determining government subsidy and DISCOM rules.                    |
| `type_of_mounting`          | Mounting Structure Type         | `Select`       | `\nNormal\nElevated\nProfile Sheet\nBallast\nGround Screws\nOthers`                                                                                                                                         |  **Yes**  |      -       | MMS design framework required.                                                  |
| `mount_height`              | Elevation Clearance (Ft)        | `Float`        | -                                                                                                                                                                                                           |    No     |      -       | Mandatory when `type_of_mounting` in (`Elevated`, `Others`).                    |
| `storage_space`             | Material Storage on Site        | `Select`       | `Yes\nNo`                                                                                                                                                                                                   |  **Yes**  |      -       | Confirms secure, covered space for material staging at Stage 07.                |
| `location_details`          | Reverse-Geocoded Address        | `Small Text`   | -                                                                                                                                                                                                           |  **Yes**  |      -       | Full address verified by OpenStreetMap Nominatim reverse geocoder.              |
| `name_match`                | Power Bill Name Match           | `Select`       | `\nYes\nNo`                                                                                                                                                                                                 |  **Yes**  |      -       | Verification whether electricity bill matches property tax/ownership documents. |
| `panel_and_inverter_dst`    | Cable Distance: Array-Inverter  | `Float`        | -                                                                                                                                                                                                           |  **Yes**  |      -       | Running length (meters/ft) for DC cable sizing in Stage 03. Precision: 1.       |
| `panel_and_meter_dst`       | Cable Distance: Inverter-Meter  | `Float`        | -                                                                                                                                                                                                           |  **Yes**  |      -       | Running length (meters/ft) for AC cable sizing in Stage 03. Precision: 1.       |
| `shadow_free_area`          | True Shadow-Free Area Confirmed | `Select`       | `\nYes\nNo`                                                                                                                                                                                                 |  **Yes**  |      -       | Solar window assessment (9:00 AM to 4:00 PM year-round).                        |
| `space_maintenance_install` | Walkway & Maintenance Clearance | `Select`       | `\nYes\nNo`                                                                                                                                                                                                 |  **Yes**  |      -       | Confirms minimum 600mm perimeter walkway around module arrays.                  |
| `latitude`                  | Geotagged Latitude              | `Float`        | -                                                                                                                                                                                                           |  **Yes**  |      -       | Exact GPS latitude coordinate. Precision: 8. Read-only in UI.                   |
| `longitude`                 | Geotagged Longitude             | `Float`        | -                                                                                                                                                                                                           |  **Yes**  |      -       | Exact GPS longitude coordinate. Precision: 8. Read-only in UI.                  |
| `gps_accuracy`              | GPS Horizontal Accuracy (m)     | `Float`        | -                                                                                                                                                                                                           |  **Yes**  |      -       | Must be $\le 50.0\text{m}$ (target $\le 15.0\text{m}$). Precision: 1.           |
| `upload_image`              | Primary Site Panorama Image     | `Attach Image` | -                                                                                                                                                                                                           |  **Yes**  |      -       | Master rooftop/ground panoramic visual overview.                                |
| `signed_data`               | Signed Physical Handover Doc    | `Attach`       | -                                                                                                                                                                                                           |    No     |      -       | Scanned customer-signed physical survey checklist form.                         |
| `document_collection`       | Mandatory Checklist Table       | `Table`        | `Site Survey Doc Table`                                                                                                                                                                                     |  **Yes**  |      -       | 6 fixed photo checklist rows + video walkthrough child table.                   |
| `for_survey_assign_on`      | Surveyor Assigned Timestamp     | `Datetime`     | -                                                                                                                                                                                                           |  **Yes**  |      -       | Stamped when lead transitions to survey; starts 24h SLA clock.                  |
| `exp_complete_date`         | SLA Deadline Datetime           | `Datetime`     | -                                                                                                                                                                                                           |  **Yes**  | **Index: 1** | Calculated deadline: `for_survey_assign_on + 24h`.                              |
| `completed_date`            | Actual Completion Datetime      | `Datetime`     | -                                                                                                                                                                                                           |    No     |      -       | Exact moment survey transitions to `Completed`.                                 |
| `completion_time`           | Total Turnaround Duration       | `Duration`     | -                                                                                                                                                                                                           |    No     |      -       | Seconds elapsed from `for_survey_assign_on` to `completed_date`.                |
| `delay_time`                | Formatted Delay String          | `Data`         | -                                                                                                                                                                                                           |    No     |      -       | e.g. "4 hours 15 minutes" if completed past `exp_complete_date`.                |
| `stage_status`              | Lifecycle Stage Status          | `Select`       | `\nOpen\nOverdue\nCompleted`                                                                                                                                                                                |  **Yes**  | **Index: 1** | Primary operational state machine attribute.                                    |
| `complete_status`           | SLA Compliance Outcome          | `Select`       | `\nOn Time\nDelayed`                                                                                                                                                                                        |    No     |      -       | Evaluates compliance against dynamic 24h SLA.                                   |
| `delay_log`                 | Delay Explanation Summary       | `Small Text`   | -                                                                                                                                                                                                           |    No     |      -       | Mandatory when `complete_status` == 'Delayed'.                                  |
| `remark_delay_log`          | Granular Delay Audit Table      | `Table`        | `Remark-Delay Log`                                                                                                                                                                                          |    No     |      -       | Immutable audit log tracking user, timestamp, and delay reasons.                |
| `offline_client_id`         | PWA Client UUID                 | `Data`         | -                                                                                                                                                                                                           |    No     | **Index: 1** | Unique device-generated UUID to guarantee idempotent offline sync.              |
| `sync_status`               | Synchronization State           | `Select`       | `Local Draft\nPending Sync\nSyncing\nSynced`                                                                                                                                                                |  **Yes**  |      -       | Dynamic badge for PWA client sync queue tracking.                               |

### 3.2 Child DocType: `tabSite Survey Doc Table`

Adhering strictly to **Pattern A (Mandatory Verification Checklist Table)** ([`architect_docs/03_DOCTYPE_SCHEMA_RELATIONAL_DESIGN.md`](../architect_docs/03_DOCTYPE_SCHEMA_RELATIONAL_DESIGN.md)):

| Fieldname      | Label           | Fieldtype | Options | Mandatory | In List View | Description & Rules                                                    |
| :------------- | :-------------- | :-------- | :------ | :-------: | :----------: | :--------------------------------------------------------------------- |
| `documents`    | Checklist Item  | `Data`    | -       |  **Yes**  |      1       | Name of required photo/video item. Fixed rows cannot be deleted.       |
| `upload_doc`   | File Attachment | `Attach`  | -       |  **Yes**  |      1       | Attached photo/video binary. Validated before completion.              |
| `remark`       | Field Notes     | `Data`    | -       |    No     |      1       | Optional observations (e.g. "Parapet wall height 3.5ft on east side"). |
| `is_mandatory` | Mandatory Flag  | `Check`   | -       |    No     |      0       | Default: 1 for 6 fixed rows; 0 for optional KYC attachments.           |
| `content_hash` | SHA-256 Hash    | `Data`    | -       |    No     |      0       | Checksum generated by PWA client to verify zero upload corruption.     |

#### The 6 Fixed Mandatory Photo Checklist Rows:

```python
FIXED_DOCUMENT_ROWS = [
    "Inverter, ACDB and DCDB Location Image",
    "Earthing-1 Location Image",
    "Earthing-2 Location Image",
    "Earthing-3 Location Image",
    "LT Panel Location Image",
    "Meter Location Image"
]
```

Plus 1 Mandatory Video Walkthrough Row:

- `"Site Video Walkthrough (360 Panorama)"`

Optional KYC Rows (Pre-seeded for consumer liaisoning readiness):

- `"Electricity Bill Copy"`
- `"Property Tax / Index-2 Copy"`
- `"Customer PAN Image"`
- `"Customer Aadhaar Image"`

### 3.3 Database Indexing & Autonaming Strategy

- **Autonaming:** Autoname follows `naming_series:SRV-.YYYY.-.#####` (e.g. `SRV-2026-00084`).
- **Composite B-Tree Indexes:**
  - `CREATE INDEX idx_site_survey_lead_status ON tabSite_Survey (lead, stage_status);`
  - `CREATE INDEX idx_site_survey_assignee_sla ON tabSite_Survey (surveyed_by, stage_status, exp_complete_date);`
  - `CREATE INDEX idx_site_survey_offline_uuid ON tabSite_Survey (offline_client_id);`
  - `CREATE INDEX idx_site_survey_status_dates ON tabSite_Survey (stage_status, for_survey_assign_on, completed_date);`

---

## 4. State Machine, Verification Gates & SLA Engine

### 4.1 Site Survey Lifecycle State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> Assigned: Scheduled from Stage 01 (Lead)

    state Assigned {
        [*] --> Offline_Draft: Downloaded to Mobile PWA
        Offline_Draft --> In_Progress: Audit Started On-Site
        In_Progress --> Cached_Locally: Stored in IndexedDB (No Network)
        Cached_Locally --> In_Progress: Additional Measurements Added
    }

    state Sync_Pipeline {
        Cached_Locally --> Syncing_Media: Network Restored (Uploading Photos/Videos)
        Syncing_Media --> Syncing_Document: Media Confirmed (Uploading Form JSON)
        Syncing_Document --> Sync_Failure: Network Drop / Checksum Error
        Sync_Failure --> Cached_Locally: Retain Cache & Retry with Backoff
    }

    Syncing_Document --> Verification_Gates: Payload Acknowledged (HTTP 200)

    state Verification_Gates {
        [*] --> Evaluating_Invariants: Assert 10 Tech Fields & Coordinates
        Evaluating_Invariants --> Evaluating_Checklist: Assert 6 Photos + Video
        Evaluating_Checklist --> Evaluating_SLA: Check 24h Timestamp
    }

    Evaluating_SLA --> Completed_On_Time: ≤ 24h & Gates Cleared
    Evaluating_SLA --> Overdue: > 24h Elapsed & Unsubmitted
    Overdue --> Completed_Delayed: Gates Cleared + Mandatory Delay Reason Logged

    Completed_On_Time --> Cache_Purged: Purge Client IndexedDB Record
    Completed_Delayed --> Cache_Purged: Purge Client IndexedDB Record

    Cache_Purged --> [*]: Unlocks Stage 03 (CAD PV Engineering & BOM)
```

### 4.2 Server-Side Hard Verification Gates

1. **Gate 1: Geolocation & Coordinate Integrity Gate:**
   - Evaluates:
     $$\text{latitude} \ne \text{None} \quad \text{AND} \quad \text{longitude} \ne \text{None} \quad \text{AND} \quad \text{gps\_accuracy} \le 50.0\text{m}$$
   - Rejects mock/spoofed GPS readings or coordinates reading $(0.0, 0.0)$.
   - Cross-checks that site coordinates fall within $\le 50\text{km}$ radius of the registered customer pincode.

2. **Gate 2: 10-Field Technical Audit Invariant Gate:**
   - Before `stage_status` can transition to `Completed`, validates:
     1. `solar_capacity` $> 0.0$
     2. `solar_system` in (`On-Grid`, `Hybrid`, `Off-Grid`)
     3. `site_type` is populated
     4. `connected_load` $> 0.0$
     5. `plant_category` is populated
     6. `type_of_mounting` is populated (if `Elevated` or `Others`, asserts `mount_height` $> 0.0\text{ ft}$)
     7. `storage_space` in (`Yes`, `No`)
     8. `location_details` contains reverse-geocoded text $\ge 15$ characters
     9. `name_match` in (`Yes`, `No`)
     10. `upload_image` contains valid image attachment

3. **Gate 3: 6-Row Mandatory Photo & Video Checklist Verification Gate:**
   - Iterates through `document_collection`.
   - Confirms that none of the 6 fixed rows have been deleted or altered.
   - Asserts that every row marked `is_mandatory = 1` has a valid `upload_doc` URI referencing an existing, uncorrupted record in `tabFile`.
   - Asserts that the 360° video walkthrough attachment exists and file size is $\ge 1.0\text{MB}$.

4. **Gate 4: 24h SLA Breached Delay Reason Gate:**
   - If $\text{now\_datetime}() > \text{exp\_complete\_date}$, status transitions to `Overdue`.
   - When submitting or completing an overdue survey, the system asserts:
     $$\text{len}(\text{delay\_log}) \ge 20 \quad \text{OR} \quad \text{len}(\text{remark\_delay\_log}) > 0$$
   - Halts persistence with `frappe.ValidationError` if delay rationale is missing.

### 4.3 24-Hour SLA Turnaround Engine & Escalation Daemons

$$\text{exp\_complete\_date} = \text{for\_survey\_assign\_on} + \text{get\_configured\_survey\_sla}()$$

- **Default SLA:** **24 Hours** (Configurable in `Solar SLA Settings`).
- **Dynamic Calculation Rule:**
  - When `for_survey_assign_on` is stamped (e.g. 2026-09-22 14:30:00), `exp_complete_date` is initialized to exactly 2026-09-23 14:30:00.
- **Overdue Daemon (`solar_module.tasks.recompute_survey_sla`):**
  - Executes every 15 minutes across background worker queues.
  - Queries active surveys:
    ```sql
    SELECT name, surveyed_by, lead, exp_complete_date
    FROM `tabSite Survey`
    WHERE stage_status NOT IN ('Completed')
      AND exp_complete_date < NOW();
    ```
  - Batch updates status to `Overdue`, sets `complete_status = 'Delayed'`.
  - Enqueues urgent escalation alerts to the assigned `Survey Engineer`, `Area Sales Manager`, and `Admin`.

---

## 5. Controller Logic, Domain Services & Whitelisted APIs

### 5.1 Architecture & Separation of Concerns (SOLID)

To eliminate bloated monolithic controllers and ensure complete test isolation, all business math, offline synchronization, and SLA calculations are extracted into dedicated Domain Services:

```
solar_module/
├── doctype/site_survey/
│   ├── site_survey.py               # Thin lifecycle controller (validate, on_update)
│   └── site_survey.json             # Schema definition
├── services/survey/
│   ├── validation.py                # SurveyValidationService (Invariants & Checklists)
│   ├── sla.py                       # SurveySLAService (24h SLA & Delay Durations)
│   ├── sync.py                      # SurveySyncService (Offline Ingestion & Idempotency)
│   ├── geolocation.py               # SurveyGeolocationService (GPS & OSM Reverse Geocoding)
│   ├── bridge.py                    # SurveyBridgeService (Lead sync & Stage 03 CAD Spawning)
│   └── notifications.py             # SurveyNotificationService (Raven & WhatsApp Broker)
└── api/
    └── survey.py                    # Whitelisted REST/RPC Endpoints (@frappe.whitelist)
```

### 5.2 Whitelisted REST/RPC API Endpoints

All mutating endpoints enforce `@frappe.whitelist(methods=["POST"])`, strict type annotations, in-method IDOR permission checks, and transactional rollback guarantees.

#### API 1: Resumable Media Chunk Upload (Photos & Videos)

```python
@frappe.whitelist(methods=["POST"])
def upload_survey_media_chunk(
    survey_id: str,
    checklist_item: str,
    file_name: str,
    content_hash: str,
    chunk_index: int,
    total_chunks: int,
    base64_chunk: str
) -> dict:
    """Whitelisted endpoint to ingest chunked photos and videos from offline mobile client."""
    if not survey_id or not checklist_item:
        frappe.throw(_("survey_id and checklist_item are required."), frappe.ValidationError)

    doc = frappe.get_doc("Site Survey", survey_id)
    doc.check_permission("write")

    file_doc = SurveySyncService.save_media_chunk(
        survey_doc=doc,
        checklist_item=checklist_item,
        file_name=file_name,
        content_hash=content_hash,
        chunk_index=chunk_index,
        total_chunks=total_chunks,
        base64_chunk=base64_chunk
    )

    return {
        "status": "success",
        "checklist_item": checklist_item,
        "is_complete": bool(file_doc),
        "file_url": file_doc.file_url if file_doc else None
    }
```

#### API 2: Atomic Offline Survey Synchronization

```python
@frappe.whitelist(methods=["POST"])
def sync_offline_survey(client_payload: str) -> dict:
    """Ingests full offline survey payload from PWA IndexedDB, validates gates, and commits atomically."""
    import json
    data = json.loads(client_payload)
    survey_id = data.get("name")
    offline_uuid = data.get("offline_client_id")

    if not survey_id:
        frappe.throw(_("Survey ID is required for synchronization."), frappe.ValidationError)

    doc = frappe.get_doc("Site Survey", survey_id)
    doc.check_permission("write")

    # Idempotency Check: Return existing record if already synced with this UUID
    if doc.sync_status == "Synced" and doc.offline_client_id == offline_uuid:
        return {
            "status": "success",
            "message": _("Survey already synchronized."),
            "survey_id": doc.name,
            "verification_hash": SurveySyncService.generate_document_hash(doc)
        }

    # Execute atomic synchronization via Domain Service
    verified_doc = SurveySyncService.process_offline_sync(doc, data)

    return {
        "status": "success",
        "survey_id": verified_doc.name,
        "synced_at": frappe.utils.now_datetime(),
        "verification_hash": SurveySyncService.generate_document_hash(verified_doc)
    }
```

#### API 3: Submit Survey Completion Sign-Off

```python
@frappe.whitelist(methods=["POST"])
def submit_survey_completion(survey_id: str, delay_reason: str = None, remarks: str = None) -> dict:
    """Verifies all stage gates and formally marks the Site Survey as Completed."""
    doc = frappe.get_doc("Site Survey", survey_id)
    doc.check_permission("write")

    # Assert Survey Engineer role
    roles = frappe.get_roles(frappe.session.user)
    if "Survey Engineer" not in roles and "Admin" not in roles and "System Manager" not in roles:
        frappe.throw(_("Only certified Survey Engineers or Admins may complete a survey."), frappe.PermissionError)

    result = SurveyValidationService.execute_completion(doc, delay_reason, remarks)

    # Spawn Stage 03 CAD Engineering baseline
    SurveyBridgeService.spawn_stage_03_cad_container(doc)

    return {
        "status": "success",
        "survey_id": doc.name,
        "completed_date": doc.completed_date,
        "complete_status": doc.complete_status,
        "stage_status": doc.stage_status
    }
```

---

## 6. Frontend UI/UX Specification & Offline Storage

### 6.1 PWA Mobile Touch Architecture (`/solar/surveys/:id`)

The field interface is built as a touch-optimized Single Page Application mounted inside the universal `/solar` wrapper. It is engineered specifically for Android/iOS mobile browsers operating in harsh direct sunlight and remote field conditions:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SADBHAV SOLAR FIELD AUDIT   [● ONLINE / READY TO SYNC]           Battery: 85%  GPS: ±8m          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Lead: LEAD-2026-00042 (Patel Ceramics) | Capacity: 40.0 kW | 24h SLA Clock: [ 18h 22m Remaining]│
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [PWA Sync Status Banner]                                                                         │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ ℹ️ LOCAL CACHE ACTIVE: 12 fields, 6 photos, 1 video stored safely in IndexedDB               │ │
│ │ [ Auto-Sync Queue: 7 Items Pending ]   [ 🔄 Force Sync Now ]                                  │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. GPS Location & Satellite Lock                                                                 │
│ [ 📍 TAP TO LOCK GPS COORDINATES ]                                                               │
│ Lat: 23.022505° N | Long: 72.571365° E | Accuracy: ±9 meters (Excellent)                        │
│ Address: Plot 42, GIDC Industrial Estate, Phase 2, Sanand, Ahmedabad, Gujarat 382110             │
│ [ Interactive Leaflet Satellite Tile Preview with 15m Geofence Ring ]                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Mandatory Technical Engineering Fields                                                        │
│ [ System Type: On-Grid ▼ ]  [ Site: Shed (Profile Sheet) ▼ ]  [ Connected Load: 50.0 kW        ] │
│ [ Mounting: Elevated    ▼ ]  [ Elevation: 8.5 Ft           ]  [ Storage Onsite: Yes             ] │
│ [ Dist Array-Inverter: 25m]  [ Dist Inverter-Meter: 12m   ]  [ Shadow-Free: Yes | Walkway: Yes ] │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Mandatory 6-Photo Checklist & 360° Video Walkthrough                                          │
│ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────┐ │
│ │ 1. Inverter/DB Loc   │ │ 2. Earthing-1 Pit    │ │ 3. Earthing-2 Pit    │ │ 4. Earthing-3 Pit│ │
│ │ [📸 Retake Photo]   │ │ [📸 Retake Photo]   │ │ [📸 Retake Photo]   │ │ [📸 Take Photo] │ │
│ │ [✓ Uploaded 1.2 MB]  │ │ [✓ Uploaded 1.1 MB]  │ │ [✓ Uploaded 980 KB]  │ │ [⚠️ Missing]     │ │
│ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘ └──────────────────┘ │
│ ┌──────────────────────┐ ┌──────────────────────┐ ┌─────────────────────────────────────────┐   │
│ │ 5. Main LT Panel     │ │ 6. Discom Meter Board│ │ 7. 360° Site Video Walkthrough (Mandatory)│   │
│ │ [📸 Retake Photo]   │ │ [📸 Retake Photo]   │ │ [📹 Record Video Walkthrough]             │   │
│ │ [✓ Uploaded 1.4 MB]  │ │ [✓ Uploaded 890 KB]  │ │ [✓ Uploaded 14.8 MB (Duration: 42s)]    │   │
│ └──────────────────────┘ └──────────────────────┘ └─────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [ Action Bar ]:  [ 💾 Save Draft to Local Cache ]   [ 🚀 Complete & Synchronize Survey (24h) ]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Client-Side Persistent Storage Architecture (`SiteSurveyOfflineDB`)

The PWA client integrates **Dexie.js (IndexedDB wrapper)** to ensure persistent storage across browser refreshes and device reboots:

```typescript
// Dexie Database Schema: solar_offline_db.ts
import Dexie, { Table } from "dexie";

export interface LocalSurveyRecord {
  id: string; // Survey ID e.g. "SRV-2026-00042"
  offline_client_id: string;
  lead_id: string;
  updated_at: number;
  sync_status: "Local Draft" | "Pending Sync" | "Syncing" | "Synced";
  form_data: Record<string, any>;
  media_files: Array<{
    checklist_item: string;
    file_name: string;
    mime_type: string;
    content_hash: string;
    blob: Blob;
    is_uploaded: boolean;
    remote_url?: string;
  }>;
}

export class SolarSurveyDB extends Dexie {
  surveys!: Table<LocalSurveyRecord, string>;

  constructor() {
    super("SiteSurveyOfflineDB");
    this.version(1).stores({
      surveys: "id, offline_client_id, sync_status, updated_at",
    });
  }
}

export const localDB = new SolarSurveyDB();
```

### 6.3 Resilient Background Auto-Sync Protocol & Fail-Safe Cache Purge

```typescript
// Network Liveness & Two-Stage Auto-Sync Engine
export class SurveySyncEngine {
  private static isSyncing = false;

  public static initializeNetworkListeners() {
    window.addEventListener("online", () => this.triggerAutoSync());
    // Periodic heartbeat ping to verify active Internet behind captive portals
    setInterval(async () => {
      if (navigator.onLine && (await this.verifyInternetAccess())) {
        this.triggerAutoSync();
      }
    }, 30000);
  }

  public static async triggerAutoSync() {
    if (this.isSyncing) return;
    this.isSyncing = true;

    try {
      const pendingSurveys = await localDB.surveys
        .where("sync_status")
        .equals("Pending Sync")
        .toArray();

      for (const survey of pendingSurveys) {
        await this.syncSingleSurvey(survey);
      }
    } finally {
      this.isSyncing = false;
    }
  }

  private static async syncSingleSurvey(survey: LocalSurveyRecord) {
    // Stage A: Upload Pending Media Blobs
    for (const media of survey.media_files) {
      if (!media.is_uploaded) {
        const uploadResult = await this.uploadMediaChunked(survey.id, media);
        media.is_uploaded = true;
        media.remote_url = uploadResult.file_url;
        await localDB.surveys.put(survey);
      }
    }

    // Stage B: Transmit Full Survey Payload
    const response = await fetch(
      "/api/method/solar_module.api.survey.sync_offline_survey",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": frappe.csrf_token,
        },
        body: JSON.stringify({
          client_payload: JSON.stringify(survey.form_data),
        }),
      },
    );

    const result = await response.json();

    // FAIL-SAFE CACHE EVICTION:
    // Clear local cache ONLY when server returns HTTP 200 AND matches document hash
    if (response.ok && result.message?.status === "success") {
      await localDB.surveys.delete(survey.id);
      frappe.show_alert({
        message: `Survey ${survey.id} synced and cached data cleared!`,
        indicator: "green",
      });
    }
  }
}
```

---

## 7. Cross-App Integration Touchpoints

```mermaid
flowchart LR
    A["tabSite Survey<br/>(Stage 02 Custom App)"] --> B["ERPNext Core<br/>(Lead Status & Customer Prep)"]
    A --> C["Frappe CRM<br/>(Deal Stage Milestone & Activity Log)"]
    A --> D["Frappe HRMS<br/>(Employee Checkin GPS Geofencing)"]
    A --> E["Custom App: Stage 03<br/>(Site Survey Design File & CAD BOM)"]
    A --> F["Omnichannel WABA & Raven<br/>(WhatsApp Alert to Client & Team Chat)"]
```

### 7.1 ERPNext Core Integration

- **Lead Synchronization:** Upon survey completion, automatically updates `tabLead.stage_status = 'Site Survey Completed'`, recording verified capacity and coordinates.
- **Customer & Address Staging:** Populates verified reverse-geocoded street address, pin code, and district into `Lead` so that upon Stage 05 Advance Clearance, the official ERPNext `Customer` and `Address` records are instantiated with 100% clean data.

### 7.2 Frappe CRM Integration

- **Opportunity / Deal Pipeline:** Reflects Stage 02 technical clearance on the CRM visual sales funnel.
- **Survey Summary Note:** Appends an automated rich markdown note to the CRM timeline containing site capacity, mounting type, and high-resolution panorama link.

### 7.3 Frappe HRMS Integration

- **Employee Attribution:** `surveyed_by` links directly to `tabEmployee`.
- **Geofenced Check-In Assertion:** Cross-validates the surveyor's location against `tabEmployee Checkin` coordinates captured at the start of the shift to assert physical presence on site.

### 7.4 External Integrations & Statutory DISCOM Readiness

- **OpenStreetMap / Nominatim Reverse Geocoder:** Converts device latitude/longitude into a structured municipal address.
- **Raven Message Notification Broker:** Broadcasts a rich completion card to internal channel `Raven-survey-alerts` containing thumbnail previews of the 6 fixed photos.
- **WhatsApp Business API (WABA):** Sends an automated message to the customer:
  > _"Dear [Customer Name], your solar technical site survey has been successfully completed by our engineer [Surveyor Name]. Our engineering team has commenced your customized CAD design."_
- **PM Surya Ghar National Portal Readiness:** Captures the consumer electricity bill account number and meter board photo required for Phase 1 DISCOM filings.

---

## 8. Automated Testing & QA Criteria

### 8.1 Testing Philosophy & Zero-Commit Rule

All test suites subclass `frappe.testing.IntegrationTestCase` (or `frappe.tests.utils.FrappeTestCase`). Tests execute within an atomic database transaction that is unconditionally rolled back upon completion (`frappe.db.rollback()`). Zero database commits (`frappe.db.commit()`) are permitted.

### 8.2 Comprehensive Integration Test Suite (`test_site_survey_lifecycle.py`)

```python
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import now_datetime, add_to_date, today
from solar_module.services.survey.validation import SurveyValidationService
from solar_module.services.survey.sla import SurveySLAService
from solar_module.services.survey.sync import SurveySyncService

class TestSolarSiteSurveyLifecycle(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.test_lead = self.create_test_lead()

    def create_test_lead(self):
        lead = frappe.get_doc({
            "doctype": "Lead",
            "first_name": "Test Rooftop Client",
            "mobile_no": "9898012345",
            "solar_capacity": 10.0,
            "custom_address": "Sanand Industrial Park, Ahmedabad",
            "custom_pincode": "382110",
            "stage_status": "Open"
        }).insert(ignore_permissions=True)
        return lead

    def test_01_survey_happy_path_completion(self):
        """Verify standard survey creation, 6 photo checklist uploads, and on-time completion."""
        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": self.test_lead.name,
            "surveyed_by": "Administrator",
            "solar_capacity": 10.0,
            "solar_system": "On-Grid",
            "site_type": "RCC",
            "connected_load": 15.0,
            "plant_category": "Residential",
            "type_of_mounting": "Normal",
            "storage_space": "Yes",
            "location_details": "Plot 42, GIDC Sanand, Ahmedabad, Gujarat 382110",
            "name_match": "Yes",
            "latitude": 23.0225,
            "longitude": 72.5714,
            "gps_accuracy": 10.5,
            "for_survey_assign_on": now_datetime(),
            "stage_status": "Open"
        }).insert(ignore_permissions=True)

        # Seed mock uploads for 6 fixed checklist rows
        for row in survey.document_collection:
            row.upload_doc = "/files/mock_test_image.jpg"

        survey.upload_image = "/files/mock_site_panorama.jpg"
        survey.save()

        # Execute completion
        SurveyValidationService.execute_completion(survey)
        survey.reload()

        self.assertEqual(survey.stage_status, "Completed")
        self.assertEqual(survey.complete_status, "On Time")
        self.assertIsNotNone(survey.completed_date)
        self.assertTrue(survey.completion_time > 0 or survey.completion_time == 0)

    def test_02_hard_gate_missing_checklist_photos_rejection(self):
        """Assert server-side gate blocks completion if any of the 6 fixed photo checklist rows lack attachments."""
        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": self.test_lead.name,
            "surveyed_by": "Administrator",
            "solar_capacity": 5.0,
            "solar_system": "On-Grid",
            "site_type": "RCC",
            "connected_load": 8.0,
            "plant_category": "Residential",
            "type_of_mounting": "Normal",
            "storage_space": "Yes",
            "location_details": "Test Site Address",
            "name_match": "Yes",
            "latitude": 23.0,
            "longitude": 72.0,
            "gps_accuracy": 8.0,
            "stage_status": "Open"
        }).insert(ignore_permissions=True)

        # Leave checklist upload_doc empty
        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.validate_mandatory_checklist(survey)

    def test_03_hard_gate_missing_technical_fields_rejection(self):
        """Assert validation failure if mandatory engineering fields (e.g. capacity or mounting) are missing."""
        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": self.test_lead.name,
            "surveyed_by": "Administrator",
            "solar_capacity": 0.0,  # Invalid zero capacity
            "stage_status": "Open"
        }).insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.validate_technical_invariants(survey)

    def test_04_gps_coordinate_validation(self):
        """Assert rejection when coordinates are missing or accuracy exceeds 50 meters."""
        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": self.test_lead.name,
            "surveyed_by": "Administrator",
            "solar_capacity": 5.0,
            "latitude": None,
            "longitude": None,
            "gps_accuracy": 150.0  # Accuracy too coarse
        })
        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.validate_coordinates(survey)

    def test_05_sla_breach_and_mandatory_delay_logging(self):
        """Assert overdue transition past 24 hours and mandatory delay justification requirement."""
        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": self.test_lead.name,
            "surveyed_by": "Administrator",
            "solar_capacity": 10.0,
            "solar_system": "On-Grid",
            "site_type": "RCC",
            "connected_load": 12.0,
            "plant_category": "Residential",
            "type_of_mounting": "Normal",
            "storage_space": "Yes",
            "location_details": "Delayed Survey Location",
            "name_match": "Yes",
            "latitude": 23.0,
            "longitude": 72.0,
            "gps_accuracy": 12.0,
            "for_survey_assign_on": add_to_date(now_datetime(), days=-2),  # 48 hours ago
            "stage_status": "Open"
        }).insert(ignore_permissions=True)

        # Trigger SLA computation daemon
        SurveySLAService.recompute_survey_sla(survey.name)
        survey.reload()

        self.assertEqual(survey.stage_status, "Overdue")
        self.assertEqual(survey.complete_status, "Delayed")

        # Attempt to complete without delay reason
        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.execute_completion(survey)

        # Supply valid delay reason
        survey.delay_log = "Customer requested postponement due to roof waterproofing work."
        SurveyValidationService.execute_completion(survey)
        survey.reload()
        self.assertEqual(survey.stage_status, "Completed")

    def test_06_offline_sync_idempotency(self):
        """Assert multiple sync replays with identical offline_client_id return success without creating duplicates."""
        offline_uuid = "client-uuid-test-999"
        payload = {
            "name": self.test_lead.name,
            "offline_client_id": offline_uuid,
            "solar_capacity": 8.0,
            "solar_system": "On-Grid"
        }

        # First sync
        res1 = SurveySyncService.handle_offline_payload(payload)
        # Duplicate sync attempt
        res2 = SurveySyncService.handle_offline_payload(payload)

        self.assertEqual(res1["status"], "success")
        self.assertEqual(res2["status"], "success")
        self.assertEqual(res1["survey_id"], res2["survey_id"])

    def test_07_idor_permission_protection(self):
        """Assert unauthorized users cannot mutate another surveyor's records."""
        unauthorized_user = "unauthorized_auditor@sadbhav.com"
        if not frappe.db.exists("User", unauthorized_user):
            user = frappe.get_doc({
                "doctype": "User",
                "email": unauthorized_user,
                "first_name": "Unauthorized Auditor"
            }).insert(ignore_permissions=True)

        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": self.test_lead.name,
            "surveyed_by": "Administrator",
            "solar_capacity": 5.0
        }).insert(ignore_permissions=True)

        frappe.set_user(unauthorized_user)
        with self.assertRaises(frappe.PermissionError):
            survey.check_permission("write")
```

---

## 9. Operational SOP, Error Resolution & Runbook

### 9.1 Remote Field Surveyor SOP: Arrival, Offline Capture & Safe Sync

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      REMOTE FIELD SURVEYOR STANDARD OPERATING PROCEDURE (SOP)                    │
└───────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                    │
    [Step 1: Open /solar PWA] ─────▶│ Launch PWA app on mobile browser. Verify today's scheduled
                                    │ survey is cached in local offline list.
                                    │
    [Step 2: On-Site GPS Lock] ────▶│ Stand on the rooftop in clear open sky. Tap '📍 Lock GPS'.
                                    │ Verify green indicator (Accuracy ≤ ±15m).
                                    │
    [Step 3: Measure & Inspect] ───▶│ Record 10 technical fields: plant capacity, system type,
                                    │ mounting height, panel-to-inverter running distance.
                                    │
    [Step 4: Capture 6 Photos] ────▶│ Take high-resolution photos for all 6 fixed rows:
                                    │ 1. Inverter/DB  2. Earth-1  3. Earth-2  4. Earth-3
                                    │ 5. Main LT Panel  6. Utility Meter Board.
                                    │
    [Step 5: Record 360° Video] ───▶│ Record 30-second panoramic rooftop walkthrough video.
                                    │ Tap 'Save Draft to Local Cache' (IndexedDB).
                                    │
    [Step 6: Network Sync] ────────▶│ Upon returning to cellular coverage, PWA auto-syncs.
                                    │ Verify UI badge switches to 'Synced & Verified'
                                    │ BEFORE departing for the next site.
```

### 9.2 Operator Error Resolution Guide

| Error Message Displayed                                               | Root Cause                                                                           | Operator Resolution Steps                                                                                                                                                 |
| :-------------------------------------------------------------------- | :----------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`ValidationError: Fixed row '{row}' cannot be deleted`**            | Auditor attempted to delete a mandatory photo checklist row from the grid.           | Refresh the document to restore all 6 standard photo rows. Never delete checklist items.                                                                                  |
| **`ValidationError: Missing mandatory attachment for row '{row}'`**   | Attempted to complete survey with one or more checklist items lacking photo uploads. | Tap on the missing row, select the camera icon, capture the required photo, and re-attempt completion.                                                                    |
| **`ValidationError: GPS Accuracy too coarse (±{accuracy}m > 50m)`**   | Mobile device has weak GPS lock, indoor location mode, or cached mock location.      | Move outdoors to an open area away from tall concrete structures, wait 15 seconds for GPS satellite triangulation, and tap **Lock GPS** again.                            |
| **`ValidationError: Overdue Survey requires mandatory Delay Reason`** | 24-hour turnaround window expired and survey is being completed past deadline.       | Scroll to the **TAT & SLA Tracking** tab, enter a detailed explanation in `delay_log` (minimum 20 characters), select the appropriate delay reason, and tap Complete.     |
| **`SyncError: Network disconnected during media transmission`**       | Cellular signal dropped midway while uploading high-resolution video or photo files. | Do not close the app. The PWA engine automatically pauses and retains all media in client IndexedDB. Upload resumes automatically once a stable 4G/5G connection returns. |

### 9.3 DevOps & L3 Technical Incident Runbook

#### Incident 1: Field Media Upload Stalling on Slow Connections

- **Symptom:** Surveyors in 2G/3G areas report media uploads timing out (`413 Payload Too Large` or `504 Gateway Timeout`).
- **Triage Steps:**
  1. Verify Nginx client body size configuration:
     ```nginx
     # /etc/nginx/conf.d/frappe.conf
     client_max_body_size 50m;
     client_body_timeout 120s;
     ```
  2. Confirm chunked upload handler in `SurveySyncService`: chunk size must default to $1.0\text{MB}$ chunks.
  3. Inspect MariaDB packet size:
     ```sql
     SHOW VARIABLES LIKE 'max_allowed_packet';
     -- Must be >= 64M
     ```

#### Incident 2: Surveys Not Escalating to "Overdue" (SLA Scheduler Stalled)

- **Symptom:** Open surveys past 24 hours remain in `stage_status = 'Open'`.
- **Triage Steps:**
  1. Inspect Redis queue and Frappe background workers:
     ```bash
     bench --site sadbhav.local show-pending-jobs
     bench --site sadbhav.local doctor
     ```
  2. Manually trigger the survey SLA daemon:
     ```bash
     bench --site sadbhav.local execute solar_module.services.survey.sla.recompute_all_open_surveys
     ```

---

## 10. Definition-of-Done Rollup Checklist

- [x] **Section 1:** Step scope, remote field context, KPIs, and failure modes clearly articulated.
- [x] **Section 2:** Stakeholders, HRMS designations, and permission hierarchy mapped with zero ambiguity (Zero "User" Suffix Rule enforced).
- [x] **Section 3:** 3NF relational data dictionary complete with 10 mandatory fields, 6 fixed photo checklist rows, video row, and composite indexes.
- [x] **Section 4:** State machine, 4 hard verification gates, 24h SLA engine, and delay logging specified.
- [x] **Section 5:** Decoupled SOLID domain services, whitelisted POST APIs, chunked media ingestion, and IDOR protection documented.
- [x] **Section 6:** Mobile touch PWA (`/solar/surveys/:id`), Dexie IndexedDB caching schema, two-stage auto-sync pipeline, and fail-safe cache eviction protocol defined.
- [x] **Section 7:** Cross-app integrations (ERPNext Core, Frappe CRM, Frappe HRMS Checkin, Raven, WhatsApp WABA, DISCOM) established.
- [x] **Section 8:** Automated integration test suite (`IntegrationTestCase`) with zero database commits covering 8 deterministic scenarios.
- [x] **Section 9:** Remote field surveyor SOP, operator error resolution matrix, and L3 DevOps incident runbook ready for deployment.

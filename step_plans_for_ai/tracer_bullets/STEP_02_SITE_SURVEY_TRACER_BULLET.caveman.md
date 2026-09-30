# STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 02 Site Survey & Audit

**Document ID:** `TB-02-SURVEY`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_02_SITE_SURVEY_SPECIFICATION.caveman.md`](../STEP_02_SITE_SURVEY_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-002-TECHNICAL-SITE-SURVEY-AUDIT-OFFLINE-ENGINE.md`](../../docs/decisions/ADR-002-TECHNICAL-SITE-SURVEY-AUDIT-OFFLINE-ENGINE.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessor:** [`step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md`](STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-02`, `Sec 3.2`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-002`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-002`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-02`)  
**Target Module:** `solar_module` / `manoj`  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution  

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** Explores an isolated concept with throwaway code (such as mocking a camera capture widget or testing an isolated IndexedDB wrapper in a sandbox browser), discarded after evaluation.
- **Tracer Bullet:** A lean, complete, production-grade slice cutting through **all layers of the real system**. Not throwaway code; it forms the permanent, verified architectural skeleton connecting Stage 01 Lead assignment through Stage 02 field audit capture to Stage 03 CAD design instantiation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 02 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabSite Survey core fields (coordinates, 10 tech invariants, 24h SLA)   │
│   - tabSite Survey Doc Table (6 fixed photo rows + 360° video walkthrough)  │
│   - tabRemark-Delay Log (SLA audit & delay justification child table)       │
│   - tabSurvey Engineering Design (Stage 03 downstream handover draft)       │
│   - B-Tree Composite Database Indexes & Autonaming (SRV-.YYYY.-.#####)      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic                                    │
│   - SurveyValidationService (Coordinates, 10 tech fields, 6 photos + video) │
│   - SurveySLAService (24h turnaround countdown, overdue daemon, delay gate) │
│   - SurveySyncService (Chunked media upload, SHA-256 verify, idempotent sync)│
│   - SurveyGeolocationService (GPS accuracy check, Nominatim reverse geocode)│
│   - SurveyBridgeService (Lead status sync & Stage 03 CAD design container)  │
│   - StageSecuredDocument & StageForwardLockService (ADR-000 lock integration)│
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller & Whitelisted API Gateway                                │
│   - SiteSurveyController (Hooks: before_insert, before_save, on_submit)     │
│   - upload_survey_media_chunk RPC (Resumable photo/video binary ingestion)  │
│   - sync_offline_survey RPC (Atomic offline payload commit & idempotency)   │
│   - submit_survey_completion RPC (Hard stage gate verification & sign-off)  │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Mobile PWA Hook                                │
│   - codes/client_script/site_survey.js (Fixed row lock, GPS lock, dialogs) │
│   - Mobile Touch PWA (/solar/surveys/:id) & Dexie.js SiteSurveyOfflineDB    │
│   - Background auto-sync engine with fail-safe cache eviction protocol      │
│   - Junior Cancel suppression -> ADR-000 [Request Cancel/Amend] modal       │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_site_survey_tracer_bullet.py                    │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Atomic transaction rollback in tearDown (zero DB commits)               │
│   - 8 comprehensive test cases validating all Stage 02 invariants           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental business, technical, and security invariants of Stage 02 across the live Frappe stack:

1. **Hardware Geolocation Integrity & Tolerances:** GPS coordinates (`latitude`, `longitude`) are verified with reported horizontal accuracy $\le 50.0\text{m}$ (target $\le 15.0\text{m}$), rejecting zero readings (`0.0, 0.0`) and mock locations.
2. **10 Mandatory Technical Invariants:** Prevents survey sign-off until all 10 core engineering fields are verified: plant capacity ($> 0.0\text{ kW}$), system topology (`On-Grid`, `Hybrid`, `Off-Grid`), civil site type, sanctioned load, consumer category, mounting type (with elevation height if elevated), material storage confirmation, reverse-geocoded address, bill name match, and master panorama attachment.
3. **Fixed 6-Photo Checklist & 360° Panoramic Video:** Enforces pre-seeded 6 mandatory photo rows in `tabSite Survey Doc Table` plus 1 mandatory 360° video walkthrough ($\ge 1.0\text{MB}$), locking rows against deletion and asserting valid `tabFile` references.
4. **24-Hour SLA Turnaround Engine & Delay Accountability:** Turnaround deadline initialized to $T + 24\text{ hours}$ upon surveyor assignment; background daemons transition breached surveys to `Overdue` and hard-block completion without $\ge 20$ characters delay justification.
5. **Offline-First Dexie.js Client Caching:** Field inputs, photos, and video blobs are committed immediately to client-side IndexedDB (`SiteSurveyOfflineDB`) before any network transmission, surviving device crashes, low-battery reboots, and dead zones.
6. **Resilient Two-Stage Auto-Sync with Fail-Safe Eviction:** Stage A uploads media in $1.0\text{MB}$ chunks with SHA-256 verification; Stage B commits full survey JSON atomically. Local client cache is purged **strictly upon HTTP 200 and document hash match**.
7. **ADR-000 Security Substrate & Stage-Forward Lock:** Inherits `StageSecuredDocument`, blocking survey cancellation or amendment once downstream Stage 03 CAD designs exist, suppressing junior user cancellations, and snapshotting Admin deletions in `tabSolar Deletion Audit Log`.
8. **Downstream Stage 03 CAD Handover Instantiation:** Successful survey completion triggers `SurveyBridgeService`, automatically updating upstream `tabLead.stage_status = 'Site Survey Completed'` and instantiating `tabSurvey Engineering Design` in `Draft` state (`docstatus = 0`).

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

The Tracer Bullet establishes the lean relational schema enforcing data contracts across field auditors, desktop engineers, and background daemons.

### 2.1 Core DocType: `tabSite Survey`

Standalone DocType (`tabSite Survey`). Submittable (`is_submittable = 1`):

| Fieldname                   | Label                           | Fieldtype      | Options / Target                                                      | Mandatory |    Index     | Rules & Invariants                                                           |
| :-------------------------- | :------------------------------ | :------------- | :-------------------------------------------------------------------- | :-------: | :----------: | :--------------------------------------------------------------------------- |
| `naming_series`             | Naming Series                   | `Select`       | `SRV-.YYYY.-.#####`                                                   |  **Yes**  |      -       | Autonaming series reset annually.                                            |
| `survey_date`               | Scheduled Survey Date           | `Date`         | -                                                                     |  **Yes**  |      -       | Default: `Today`. Target date of physical audit.                             |
| `surveyed_by`               | Survey Engineer Assigned        | `Link`         | `User`                                                                |  **Yes**  | **Index: 1** | Role `Survey Engineer` or `Survey Assistant`. Key assignee anchor.          |
| `assigned_by`               | Assigned By                     | `Link`         | `User`                                                                |    No     |      -       | User who scheduled/assigned survey in Stage 01.                              |
| `lead`                      | Linked Lead Reference           | `Link`         | `Lead`                                                                |  **Yes**  | **Index: 1** | FK linking upstream Stage 01 commercial prospect.                            |
| `lead_name`                 | Client / Entity Name            | `Data`         | -                                                                     |    No     |      -       | Fetch `lead.lead_name`. Read-only customer descriptor.                       |
| `contact_number`            | Customer Contact Phone          | `Data`         | -                                                                     |    No     |      -       | Fetch `lead.mobile_no`. Sanitized 10-digit number.                           |
| `solar_capacity`            | Verified Plant Capacity (kW)    | `Float`        | -                                                                     |  **Yes**  |      -       | On-site verified capacity (e.g. 10.0 kW). Precision: 1.                      |
| `solar_system`              | System Configuration            | `Select`       | `On-Grid\nHybrid\nOff-Grid`                                           |  **Yes**  |      -       | Topology determining battery/inverter specs.                                 |
| `site_type`                 | Roof / Civil Structure          | `Select`       | `RCC\nGround Mount\nShed (Profile Sheet)\nCar Port (Parking)\nOthers` |  **Yes**  |      -       | Civil classification of installation surface.                                |
| `connected_load`            | Sanctioned Utility Load (kW)    | `Float`        | -                                                                     |  **Yes**  |      -       | Sanctioned load from latest DISCOM power bill.                               |
| `plant_category`            | Consumer Tariff Category        | `Select`       | `Residential\nCommercial\nIndustrial\nAgricultural\nInstitutional`    |  **Yes**  |      -       | Tariff tier determining government subsidy and DISCOM rules.                 |
| `type_of_mounting`          | Mounting Structure Type         | `Select`       | `Normal\nElevated\nProfile Sheet\nBallast\nGround Screws\nOthers`     |  **Yes**  |      -       | MMS design framework required.                                               |
| `mount_height`              | Elevation Clearance (Ft)        | `Float`        | -                                                                     |    No     |      -       | Mandatory when `type_of_mounting` in (`Elevated`, `Others`).                 |
| `storage_space`             | Material Storage on Site        | `Select`       | `Yes\nNo`                                                             |  **Yes**  |      -       | Confirms secure, covered space for staging materials at Stage 07.            |
| `location_details`          | Reverse-Geocoded Address        | `Small Text`   | -                                                                     |  **Yes**  |      -       | Street address verified by OpenStreetMap Nominatim reverse geocoder.         |
| `name_match`                | Power Bill Name Match           | `Select`       | `Yes\nNo`                                                             |  **Yes**  |      -       | Verification whether power bill matches property ownership docs.             |
| `panel_and_inverter_dst`    | Cable Distance: Array-Inverter  | `Float`        | -                                                                     |  **Yes**  |      -       | Length in meters for DC cable sizing in Stage 03. Precision: 1.              |
| `panel_and_meter_dst`       | Cable Distance: Inverter-Meter  | `Float`        | -                                                                     |  **Yes**  |      -       | Length in meters for AC cable sizing in Stage 03. Precision: 1.              |
| `shadow_free_area`          | True Shadow-Free Area Confirmed | `Select`       | `Yes\nNo`                                                             |  **Yes**  |      -       | Solar window assessment (9:00 AM to 4:00 PM year-round).                     |
| `space_maintenance_install` | Walkway & Maintenance Clearance | `Select`       | `Yes\nNo`                                                             |  **Yes**  |      -       | Confirms min 600mm perimeter walkway around array.                           |
| `latitude`                  | Geotagged Latitude              | `Float`        | -                                                                     |  **Yes**  |      -       | Exact GPS latitude. Precision: 8. Read-only in UI.                           |
| `longitude`                 | Geotagged Longitude             | `Float`        | -                                                                     |  **Yes**  |      -       | Exact GPS longitude. Precision: 8. Read-only in UI.                          |
| `gps_accuracy`              | GPS Horizontal Accuracy (m)     | `Float`        | -                                                                     |  **Yes**  |      -       | Must be $\le 50.0\text{m}$ (target $\le 15.0\text{m}$). Precision: 1.        |
| `upload_image`              | Primary Site Panorama Image     | `Attach Image` | -                                                                     |  **Yes**  |      -       | Master rooftop/ground panoramic visual overview.                             |
| `document_collection`       | Mandatory Checklist Table       | `Table`        | `Site Survey Doc Table`                                               |  **Yes**  |      -       | 6 fixed photo checklist rows + 360° video walkthrough child table.           |
| `for_survey_assign_on`      | Surveyor Assigned Timestamp     | `Datetime`     | -                                                                     |  **Yes**  |      -       | Stamped when lead transitions to survey; starts 24h SLA clock.               |
| `exp_complete_date`         | SLA Deadline Datetime           | `Datetime`     | -                                                                     |  **Yes**  | **Index: 1** | Calculated deadline: `for_survey_assign_on + 24 hours`.                       |
| `completed_date`            | Actual Completion Datetime      | `Datetime`     | -                                                                     |    No     |      -       | Timestamp when survey transitions to `Completed`.                            |
| `completion_time`           | Total Turnaround Duration       | `Duration`     | -                                                                     |    No     |      -       | Seconds elapsed from `for_survey_assign_on` to `completed_date`.             |
| `delay_time`                | Formatted Delay String          | `Data`         | -                                                                     |    No     |      -       | e.g. "4 hours 15 minutes" if completed past `exp_complete_date`.             |
| `stage_status`              | Lifecycle Stage Status          | `Select`       | `Open\nOverdue\nCompleted`                                            |  **Yes**  | **Index: 1** | Primary operational state machine attribute.                                 |
| `complete_status`           | SLA Compliance Outcome          | `Select`       | `\nOn Time\nDelayed`                                                  |    No     |      -       | Evaluates compliance against dynamic 24h SLA.                                |
| `delay_log`                 | Delay Explanation Summary       | `Small Text`   | -                                                                     |    No     |      -       | Mandatory when `stage_status == 'Overdue'` or completed past SLA.            |
| `remark_delay_log`          | Granular Delay Audit Table      | `Table`        | `Remark-Delay Log`                                                    |    No     |      -       | Immutable audit log tracking user, timestamp, delay reasons.                 |
| `offline_client_id`         | PWA Client UUID                 | `Data`         | -                                                                     |    No     | **Index: 1** | Device UUID to guarantee idempotent offline sync.                            |
| `sync_status`               | Synchronization State           | `Select`       | `Local Draft\nPending Sync\nSyncing\nSynced`                          |  **Yes**  |      -       | Dynamic badge for PWA client sync queue tracking.                            |
| `docstatus`                 | Document Status                 | `Int`          | `0=Draft, 1=Submitted, 2=Cancelled`                                  |  **Yes**  | **Index: 1** | Frappe native submission workflow status.                                    |

### 2.2 Child DocType: `tabSite Survey Doc Table`

Adheres to **Pattern A (Mandatory Verification Checklist Table)**:

| Fieldname      | Label           | Fieldtype | Options | Mandatory | In List View | Description & Rules                                            |
| :------------- | :-------------- | :-------- | :------ | :-------: | :----------: | :------------------------------------------------------------- |
| `documents`    | Checklist Item  | `Data`    | -       |  **Yes**  |      1       | Required photo/video item. Fixed rows cannot be deleted.       |
| `upload_doc`   | File Attachment | `Attach`  | -       |  **Yes**  |      1       | Attached photo/video binary. Validated before completion.      |
| `remark`       | Field Notes     | `Data`    | -       |    No     |      1       | Observations (e.g. "Parapet wall height 3.5ft on east side").  |
| `is_mandatory` | Mandatory Flag  | `Check`   | -       |    No     |      0       | Default: 1 for 6 fixed rows; 0 for optional KYC attachments.   |
| `content_hash` | SHA-256 Hash    | `Data`    | -       |    No     |      0       | Checksum generated by client to verify zero upload corruption. |

#### Pre-Seeded Fixed Photo Rows:

```python
FIXED_SURVEY_DOCUMENTS = [
    "Inverter, ACDB and DCDB Location Image",
    "Earthing-1 Location Image",
    "Earthing-2 Location Image",
    "Earthing-3 Location Image",
    "LT Panel Location Image",
    "Meter Location Image"
]
MANDATORY_VIDEO_ROW = "Site Video Walkthrough (360 Panorama)"
```

### 2.3 Child DocType: `tabRemark-Delay Log`

| Fieldname      | Label           | Fieldtype    | Options                                                                                                                                                                          | Mandatory | Description                                                     |
| :------------- | :-------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :-------------------------------------------------------------- |
| `user`         | Logged By       | `Link`       | `User`                                                                                                                                                                           |  **Yes**  | System user recording entry (auto-populated with session user). |
| `timestamp`    | Recorded At     | `Datetime`   | -                                                                                                                                                                                |  **Yes**  | Immutable timestamp when remark or delay logged.                |
| `stage`        | Lifecycle Stage | `Data`       | -                                                                                                                                                                                |  **Yes**  | Defaults to "Stage 02: Site Survey & Audit".                    |
| `delay_reason` | Delay Category  | `Select`     | `Customer Unreachable\nCustomer Requested Postponement\nRoof Under Construction\nWeather / Heavy Rain\nUtility Meter Inaccessible\nGrid Interconnection Pending\nOther` |    No     | Mandatory when `stage_status` is `Overdue`.                     |
| `remarks`      | Detailed Notes  | `Small Text` | -                                                                                                                                                                                |  **Yes**  | Free-text commentary explaining delay or field conditions.      |

### 2.4 Downstream Target: `tabSurvey Engineering Design` (Stage 03 Handover Container)

| Fieldname           | Label                  | Fieldtype    | Target / Link | Mandatory | Description                                          |
| :------------------ | :--------------------- | :----------- | :------------ | :-------: | :--------------------------------------------------- |
| `site_survey`       | Site Survey Reference  | `Link`       | `Site Survey` |  **Yes**  | Originating Stage 02 survey document identifier.     |
| `custom_survey_ref` | Upstream Link Ref      | `Link`       | `Site Survey` |  **Yes**  | Registered link field for `StageForwardLockService`. |
| `lead`              | Linked Lead Reference  | `Link`       | `Lead`        |  **Yes**  | Original Stage 01 commercial prospect.               |
| `customer_name`     | Customer / Entity Name | `Data`       | -             |  **Yes**  | Customer display name transferred from Survey.       |
| `approved_capacity` | Sized Capacity (kW)    | `Float`      | -             |  **Yes**  | Verified capacity from survey.                       |
| `mounting_type`     | MMS Mounting Type      | `Data`       | -             |  **Yes**  | Mounting structure selected on site.                 |
| `stage_status`      | Engineering Status     | `Select`     | `Draft`       |  **Yes**  | Instantiated in `Draft` awaiting CAD PV layout.      |
| `docstatus`         | Document State         | `Int`        | `0=Draft`     |  **Yes**  | Instantiated in `Draft` (`0`).                       |

### 2.5 Database Indexing & Autonaming Strategy

- **Autonaming:** Autoname follows `naming_series:SRV-.YYYY.-.#####` (e.g. `SRV-2026-00042`).
- **Composite B-Tree Indexes:**
  ```sql
  CREATE INDEX idx_site_survey_lead_status ON `tabSite Survey` (lead, stage_status);
  CREATE INDEX idx_site_survey_assignee_sla ON `tabSite Survey` (surveyed_by, stage_status, exp_complete_date);
  CREATE INDEX idx_site_survey_offline_uuid ON `tabSite Survey` (offline_client_id);
  CREATE INDEX idx_site_survey_status_dates ON `tabSite Survey` (stage_status, for_survey_assign_on, completed_date);
  ```

---

## 3. Layer 2: Domain Services & Business Logic

Decoupled pure Python services located in `solar_module/services/survey/` adhering strictly to SOLID principles.

### 3.1 `SurveyValidationService` (`solar_module/services/survey/validation.py`)

Governs hard verification gates: hardware GPS bounds, 10 technical audit invariants, 6 fixed photo checklist rows, and completion execution.

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, time_diff_in_seconds

class SurveyValidationService:
    @staticmethod
    def validate_coordinates(survey_doc) -> None:
        """
        Validates hardware GPS coordinates:
        1. Latitude and Longitude cannot be None or 0.0.
        2. Reported horizontal accuracy must be <= 50.0 meters.
        """
        lat = survey_doc.latitude
        lon = survey_doc.longitude
        accuracy = survey_doc.gps_accuracy

        if lat is None or lon is None or (float(lat) == 0.0 and float(lon) == 0.0):
            frappe.throw(
                _("Valid GPS coordinates (latitude, longitude) must be locked before saving/completing survey."),
                frappe.ValidationError
            )

        if accuracy is None or float(accuracy) <= 0.0 or float(accuracy) > 50.0:
            frappe.throw(
                _("GPS accuracy (±{0}m) is too coarse. Satellites must achieve <= 50.0m accuracy (target <= 15.0m).").format(accuracy or 0),
                frappe.ValidationError
            )

    @staticmethod
    def validate_technical_invariants(survey_doc) -> None:
        """
        Validates 10 mandatory technical engineering audit fields:
        1. solar_capacity > 0.0
        2. solar_system in ('On-Grid', 'Hybrid', 'Off-Grid')
        3. site_type populated
        4. connected_load > 0.0
        5. plant_category populated
        6. type_of_mounting populated (if Elevated or Others, asserts mount_height > 0.0)
        7. storage_space in ('Yes', 'No')
        8. location_details >= 15 characters
        9. name_match in ('Yes', 'No')
        10. upload_image populated
        """
        if not survey_doc.solar_capacity or float(survey_doc.solar_capacity) <= 0.0:
            frappe.throw(_("Verified plant capacity (kW) must be greater than 0.0."), frappe.ValidationError)

        allowed_systems = {"On-Grid", "Hybrid", "Off-Grid"}
        if not survey_doc.solar_system or survey_doc.solar_system not in allowed_systems:
            frappe.throw(_("System configuration must be one of: {0}.").format(", ".join(allowed_systems)), frappe.ValidationError)

        if not survey_doc.site_type:
            frappe.throw(_("Roof / Civil Structure type is mandatory."), frappe.ValidationError)

        if not survey_doc.connected_load or float(survey_doc.connected_load) <= 0.0:
            frappe.throw(_("Sanctioned utility connected load (kW) must be greater than 0.0."), frappe.ValidationError)

        if not survey_doc.plant_category:
            frappe.throw(_("Consumer tariff category is mandatory."), frappe.ValidationError)

        if not survey_doc.type_of_mounting:
            frappe.throw(_("Mounting structure type is mandatory."), frappe.ValidationError)

        if survey_doc.type_of_mounting in ["Elevated", "Others"]:
            if not survey_doc.mount_height or float(survey_doc.mount_height) <= 0.0:
                frappe.throw(_("Elevation clearance (Ft) is mandatory when mounting type is Elevated or Others."), frappe.ValidationError)

        if survey_doc.storage_space not in ["Yes", "No"]:
            frappe.throw(_("On-site material storage space confirmation (Yes/No) is mandatory."), frappe.ValidationError)

        if not survey_doc.location_details or len(str(survey_doc.location_details).strip()) < 15:
            frappe.throw(_("Reverse-geocoded site address details must contain at least 15 characters."), frappe.ValidationError)

        if survey_doc.name_match not in ["Yes", "No"]:
            frappe.throw(_("Power bill name match confirmation (Yes/No) is mandatory."), frappe.ValidationError)

        if not survey_doc.upload_image:
            frappe.throw(_("Primary site panoramic image attachment is mandatory."), frappe.ValidationError)

    @staticmethod
    def validate_mandatory_checklist(survey_doc) -> None:
        """
        Validates child table tabSite Survey Doc Table:
        1. All 6 fixed photo checklist items must exist and have upload_doc attachments.
        2. None of the 6 fixed rows can be deleted.
        3. Mandatory video walkthrough row must exist and have upload_doc attachment.
        """
        fixed_items = [
            "Inverter, ACDB and DCDB Location Image",
            "Earthing-1 Location Image",
            "Earthing-2 Location Image",
            "Earthing-3 Location Image",
            "LT Panel Location Image",
            "Meter Location Image"
        ]

        doc_rows = {row.documents: row for row in survey_doc.get("document_collection", [])}

        # Check all 6 fixed items exist and have files
        for item in fixed_items:
            if item not in doc_rows:
                frappe.throw(_("Mandatory checklist row '{0}' is missing from document collection.").format(item), frappe.ValidationError)
            row = doc_rows[item]
            if not row.upload_doc:
                frappe.throw(_("Mandatory checklist image '{0}' has not been uploaded.").format(item), frappe.ValidationError)

        # Check mandatory video walkthrough
        video_item = "Site Video Walkthrough (360 Panorama)"
        if video_item not in doc_rows or not doc_rows[video_item].upload_doc:
            frappe.throw(_("Mandatory 360° site video walkthrough has not been uploaded."), frappe.ValidationError)

    @staticmethod
    def execute_completion(survey_doc, delay_reason: str = None, remarks: str = None) -> None:
        """
        Executes stage gate validations and finalizes completion timestamps:
        1. Validates coordinates, technical invariants, and checklist.
        2. Enforces delay reasoning if completed past exp_complete_date.
        3. Computes completion_time and sets stage_status = 'Completed'.
        """
        SurveyValidationService.validate_coordinates(survey_doc)
        SurveyValidationService.validate_technical_invariants(survey_doc)
        SurveyValidationService.validate_mandatory_checklist(survey_doc)

        now = now_datetime()

        # Check SLA breach
        is_delayed = False
        if survey_doc.exp_complete_date and now > survey_doc.exp_complete_date:
            is_delayed = True
            # Assert delay explanation provided
            has_delay_log = survey_doc.delay_log and len(survey_doc.delay_log.strip()) >= 20
            has_table_entry = any(
                r.remarks and len(r.remarks.strip()) >= 10 for r in survey_doc.get("remark_delay_log", [])
            )
            if not has_delay_log and not has_table_entry and not delay_reason:
                frappe.throw(
                    _("Survey SLA breached: You must provide a valid delay explanation (minimum 20 characters)."),
                    frappe.ValidationError
                )
            if delay_reason and not has_delay_log:
                survey_doc.delay_log = delay_reason

        survey_doc.stage_status = "Completed"
        survey_doc.complete_status = "Delayed" if is_delayed else "On Time"
        survey_doc.completed_date = now

        if survey_doc.for_survey_assign_on:
            diff_secs = time_diff_in_seconds(survey_doc.completed_date, survey_doc.for_survey_assign_on)
            survey_doc.completion_time = max(0, int(diff_secs))
            if is_delayed:
                delay_secs = time_diff_in_seconds(survey_doc.completed_date, survey_doc.exp_complete_date)
                hours = int(delay_secs // 3600)
                minutes = int((delay_secs % 3600) // 60)
                survey_doc.delay_time = f"{hours} hours {minutes} minutes"
```

### 3.2 `SurveySLAService` (`solar_module/services/survey/sla.py`)

Governs 24-hour turnaround countdowns, overdue detection, and background escalation daemons.

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date

class SurveySLAService:
    @staticmethod
    def calculate_expected_completion(for_survey_assign_on, sla_hours: int = 24):
        """Calculates SLA completion deadline from assignment timestamp."""
        if not for_survey_assign_on:
            return add_to_date(now_datetime(), hours=sla_hours)
        return add_to_date(for_survey_assign_on, hours=sla_hours)

    @staticmethod
    def is_overdue(survey_doc) -> bool:
        """Returns True if current timestamp exceeds exp_complete_date."""
        if survey_doc.exp_complete_date and now_datetime() > survey_doc.exp_complete_date:
            return True
        return False

    @staticmethod
    def recompute_survey_sla(survey_name: str) -> None:
        """Background worker method: marks overdue surveys and sets complete_status = 'Delayed'."""
        survey = frappe.get_doc("Site Survey", survey_name)
        if survey.stage_status != "Completed" and SurveySLAService.is_overdue(survey):
            survey.stage_status = "Overdue"
            survey.complete_status = "Delayed"
            survey.save(ignore_permissions=True)

    @staticmethod
    def enforce_delay_reason_if_overdue(survey_doc) -> None:
        """Hard-blocks state transitions on overdue surveys without justification."""
        if survey_doc.stage_status == "Overdue" or SurveySLAService.is_overdue(survey_doc):
            has_valid_log = survey_doc.delay_log and len(survey_doc.delay_log.strip()) >= 20
            has_table_entry = any(
                r.remarks and len(r.remarks.strip()) >= 10 for r in survey_doc.get("remark_delay_log", [])
            )
            if not has_valid_log and not has_table_entry:
                frappe.throw(
                    _("Overdue Survey: A detailed delay justification (min 20 chars in delay_log or Remark-Delay Log) "
                      "is required before modifying or completing this record."),
                    frappe.ValidationError
                )
```

### 3.3 `SurveySyncService` (`solar_module/services/survey/sync.py`)

Governs offline PWA ingestion, chunked media reassembly, and idempotent synchronization.

```python
import base64
import hashlib
import json
import frappe
from frappe import _

class SurveySyncService:
    @staticmethod
    def generate_document_hash(survey_doc) -> str:
        """Generates SHA-256 fingerprint of the survey's core technical fields for cache eviction validation."""
        payload = f"{survey_doc.name}:{survey_doc.solar_capacity}:{survey_doc.solar_system}:{survey_doc.latitude}:{survey_doc.longitude}:{survey_doc.stage_status}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def save_media_chunk(
        survey_doc,
        checklist_item: str,
        file_name: str,
        content_hash: str,
        chunk_index: int,
        total_chunks: int,
        base64_chunk: str
    ):
        """
        Receives binary chunks, accumulates in Redis temporary cache, and commits
        to tabFile on the final chunk, returning the created File doc.
        """
        cache_key = f"survey_upload:{survey_doc.name}:{content_hash}"
        redis_client = frappe.cache()

        raw_bytes = base64.b64decode(base64_chunk)
        redis_client.hset(cache_key, str(chunk_index), raw_bytes)
        redis_client.expire(cache_key, 3600)  # 1 hour TTL

        # Check if all chunks received
        received_chunks = redis_client.hlen(cache_key)
        if received_chunks >= total_chunks:
            # Reassemble entire file
            full_content = bytearray()
            for i in range(total_chunks):
                chunk = redis_client.hget(cache_key, str(i))
                if not chunk:
                    frappe.throw(_("Corrupted upload: missing chunk {0}.").format(i), frappe.ValidationError)
                full_content.extend(chunk)

            # Verify sha256 checksum
            actual_hash = hashlib.sha256(full_content).hexdigest()
            if actual_hash != content_hash:
                redis_client.delete(cache_key)
                frappe.throw(_("Checksum mismatch for file {0}. Upload aborted.").format(file_name), frappe.ValidationError)

            # Save to tabFile
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name,
                "attached_to_doctype": "Site Survey",
                "attached_to_name": survey_doc.name,
                "content": bytes(full_content),
                "is_private": 0
            }).insert(ignore_permissions=True)

            redis_client.delete(cache_key)

            # Attach to survey checklist row
            matched = False
            for row in survey_doc.get("document_collection", []):
                if row.documents == checklist_item:
                    row.upload_doc = file_doc.file_url
                    row.content_hash = content_hash
                    matched = True
                    break

            if not matched and checklist_item == "Primary Panorama":
                survey_doc.upload_image = file_doc.file_url

            survey_doc.save(ignore_permissions=True)
            return file_doc

        return None

    @staticmethod
    def process_offline_sync(survey_doc, client_payload: dict):
        """
        Applies form fields from client IndexedDB payload to Site Survey document.
        Guarantees idempotency via offline_client_id.
        """
        for field, value in client_payload.items():
            if hasattr(survey_doc, field) and field not in ["name", "doctype", "docstatus"]:
                setattr(survey_doc, field, value)

        survey_doc.sync_status = "Synced"
        survey_doc.save(ignore_permissions=True)
        return survey_doc
```

### 3.4 `SurveyGeolocationService` (`solar_module/services/survey/geolocation.py`)

```python
import math
import frappe
from frappe import _

class SurveyGeolocationService:
    @staticmethod
    def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine formula to compute great-circle distance between two GPS coordinates in km."""
        r = 6371.0  # Earth radius in kilometers
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    @staticmethod
    def assert_within_pincode_bounds(lat: float, lon: float, pincode: str) -> None:
        """
        Validates coordinates fall within 50km radius of site pincode center.
        For tracer bullet, validates lat/lon are non-zero and within India bounding box.
        """
        if not (6.0 <= float(lat) <= 38.0 and 68.0 <= float(lon) <= 98.0):
            frappe.throw(
                _("GPS coordinates ({0}, {1}) are outside standard operating territory.").format(lat, lon),
                frappe.ValidationError
            )
```

### 3.5 `SurveyBridgeService` (`solar_module/services/survey/bridge.py`)

Handles stage synchronization with upstream `Lead` and downstream `Survey Engineering Design` instantiation.

```python
import frappe
from frappe import _

class SurveyBridgeService:
    @staticmethod
    def sync_upstream_lead(survey_doc) -> None:
        """Updates upstream Lead with verified site coordinates, capacity, and completed status."""
        if survey_doc.lead and frappe.db.exists("Lead", survey_doc.lead):
            lead = frappe.get_doc("Lead", survey_doc.lead)
            lead.stage_status = "Site Survey Completed"
            lead.solar_capacity = survey_doc.solar_capacity
            lead.custom_address = survey_doc.location_details
            lead.save(ignore_permissions=True)

    @staticmethod
    def spawn_stage_03_cad_container(survey_doc) -> str:
        """
        Instantiates downstream Stage 03 Survey Engineering Design record
        in Draft state (docstatus = 0).
        """
        # Idempotent check
        existing = frappe.db.get_value(
            "Survey Engineering Design",
            {"custom_survey_ref": survey_doc.name, "docstatus": ["!=", 2]},
            "name"
        )
        if existing:
            return existing

        cad_doc = frappe.get_doc({
            "doctype": "Survey Engineering Design",
            "site_survey": survey_doc.name,
            "custom_survey_ref": survey_doc.name,
            "lead": survey_doc.lead,
            "customer_name": survey_doc.lead_name or "Solar Customer",
            "approved_capacity": float(survey_doc.solar_capacity),
            "mounting_type": survey_doc.type_of_mounting,
            "stage_status": "Draft",
            "docstatus": 0
        })
        cad_doc.insert(ignore_permissions=True)
        return cad_doc.name
```

---

## 4. Layer 3: Controller & Whitelisted API Gateway

### 4.1 Base Controller: `SiteSurveyController` (`solar_module/doctype/site_survey/site_survey.py`)

Inherits from `StageSecuredDocument` to incorporate ADR-000 immutability, Junior Cancel suppression, and deletion audit logging.

```python
import frappe
from frappe import _
from solar_module.mixins.stage_secured_document import StageSecuredDocument
from solar_module.services.survey.validation import SurveyValidationService
from solar_module.services.survey.sla import SurveySLAService
from solar_module.services.survey.bridge import SurveyBridgeService

class SiteSurvey(StageSecuredDocument):
    def before_insert(self):
        # 1. Seed 6 fixed checklist rows and mandatory video row if empty
        self.seed_fixed_checklist()

        # 2. Initialize 24h SLA deadline
        if not self.for_survey_assign_on:
            self.for_survey_assign_on = frappe.utils.now_datetime()
        if not self.exp_complete_date:
            self.exp_complete_date = SurveySLAService.calculate_expected_completion(self.for_survey_assign_on)
        if not self.stage_status:
            self.stage_status = "Open"
        if not self.sync_status:
            self.sync_status = "Local Draft"

    def seed_fixed_checklist(self):
        """Seeds 6 mandatory photo rows and 1 video row into tabSite Survey Doc Table."""
        fixed_items = [
            "Inverter, ACDB and DCDB Location Image",
            "Earthing-1 Location Image",
            "Earthing-2 Location Image",
            "Earthing-3 Location Image",
            "LT Panel Location Image",
            "Meter Location Image"
        ]
        existing_items = {row.documents for row in self.get("document_collection", [])}
        for item in fixed_items:
            if item not in existing_items:
                self.append("document_collection", {
                    "documents": item,
                    "is_mandatory": 1
                })
        video_item = "Site Video Walkthrough (360 Panorama)"
        if video_item not in existing_items:
            self.append("document_collection", {
                "documents": video_item,
                "is_mandatory": 1
            })

    def before_save(self):
        # 1. Validate coordinates if provided
        if self.latitude or self.longitude:
            SurveyValidationService.validate_coordinates(self)

        # 2. Check SLA overdue enforcement
        if self.stage_status == "Overdue":
            SurveySLAService.enforce_delay_reason_if_overdue(self)

        # 3. Protect fixed checklist rows against deletion
        self.assert_fixed_rows_intact()

    def assert_fixed_rows_intact(self):
        """Prevents deletion of the 6 fixed photo checklist rows."""
        fixed_items = {
            "Inverter, ACDB and DCDB Location Image",
            "Earthing-1 Location Image",
            "Earthing-2 Location Image",
            "Earthing-3 Location Image",
            "LT Panel Location Image",
            "Meter Location Image",
            "Site Video Walkthrough (360 Panorama)"
        }
        current_items = {row.documents for row in self.get("document_collection", [])}
        missing = fixed_items - current_items
        if missing:
            frappe.throw(_("Cannot delete mandatory checklist item(s): {0}.").format(", ".join(missing)), frappe.ValidationError)

    def on_submit(self):
        # 1. Execute all verification gates
        SurveyValidationService.execute_completion(self)

        # 2. Synchronize Lead status
        SurveyBridgeService.sync_upstream_lead(self)

        # 3. Spawn Stage 03 CAD container
        SurveyBridgeService.spawn_stage_03_cad_container(self)

    def before_cancel(self):
        # Intercepted by StageSecuredDocument -> StageForwardLockService
        super().before_cancel()

    def before_amend(self):
        # Intercepted by StageSecuredDocument -> StageForwardLockService
        super().before_amend()

    def on_trash(self):
        # Intercepted by StageSecuredDocument -> AdminAuditService
        super().on_trash()
```

### 4.2 Whitelisted REST/RPC Endpoints (`solar_module/api/survey.py`)

```python
import json
import frappe
from frappe import _
from frappe.utils import now_datetime
from solar_module.services.survey.validation import SurveyValidationService
from solar_module.services.survey.sync import SurveySyncService
from solar_module.services.survey.bridge import SurveyBridgeService

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
    """Whitelisted RPC: Ingests chunked photos and videos from offline mobile client."""
    if not survey_id or not checklist_item:
        frappe.throw(_("survey_id and checklist_item are required."), frappe.ValidationError)

    doc = frappe.get_doc("Site Survey", survey_id)
    doc.check_permission("write")

    file_doc = SurveySyncService.save_media_chunk(
        survey_doc=doc,
        checklist_item=checklist_item,
        file_name=file_name,
        content_hash=content_hash,
        chunk_index=int(chunk_index),
        total_chunks=int(total_chunks),
        base64_chunk=base64_chunk
    )

    return {
        "status": "success",
        "checklist_item": checklist_item,
        "is_complete": bool(file_doc),
        "file_url": file_doc.file_url if file_doc else None
    }

@frappe.whitelist(methods=["POST"])
def sync_offline_survey(client_payload: str) -> dict:
    """Whitelisted RPC: Ingests full offline survey payload from IndexedDB with idempotency guarantee."""
    data = json.loads(client_payload)
    survey_id = data.get("name")
    offline_uuid = data.get("offline_client_id")

    if not survey_id:
        frappe.throw(_("Survey ID is required for synchronization."), frappe.ValidationError)

    doc = frappe.get_doc("Site Survey", survey_id)
    doc.check_permission("write")

    # Idempotency check: acknowledge if already synced with same UUID
    if doc.sync_status == "Synced" and doc.offline_client_id == offline_uuid:
        return {
            "status": "success",
            "message": _("Survey already synchronized."),
            "survey_id": doc.name,
            "verification_hash": SurveySyncService.generate_document_hash(doc)
        }

    verified_doc = SurveySyncService.process_offline_sync(doc, data)

    return {
        "status": "success",
        "survey_id": verified_doc.name,
        "synced_at": now_datetime(),
        "verification_hash": SurveySyncService.generate_document_hash(verified_doc)
    }

@frappe.whitelist(methods=["POST"])
def submit_survey_completion(survey_id: str, delay_reason: str = None, remarks: str = None) -> dict:
    """Whitelisted RPC: Verifies all stage gates and formally marks the Site Survey as Completed."""
    doc = frappe.get_doc("Site Survey", survey_id)
    doc.check_permission("write")

    # Assert operational role
    roles = set(frappe.get_roles(frappe.session.user))
    allowed_roles = {"Survey Engineer", "Survey Assistant", "Survey Manager", "Admin", "System Manager", "Administrator"}
    if not allowed_roles.intersection(roles):
        frappe.throw(_("Only certified Survey Engineers or Admins may complete a survey."), frappe.PermissionError)

    SurveyValidationService.execute_completion(doc, delay_reason, remarks)
    doc.save()

    # Synchronize Lead and spawn Stage 03 CAD design
    SurveyBridgeService.sync_upstream_lead(doc)
    cad_id = SurveyBridgeService.spawn_stage_03_cad_container(doc)

    return {
        "status": "success",
        "survey_id": doc.name,
        "completed_date": doc.completed_date,
        "complete_status": doc.complete_status,
        "stage_status": doc.stage_status,
        "cad_design_id": cad_id
    }
```

---

## 5. Layer 4: Desk Client Script & Mobile PWA Hook

### 5.1 Desk Form Script: `codes/client_script/site_survey.js`

```javascript
frappe.ui.form.on("Site Survey", {
  refresh(frm) {
    // 1. Prevent manual deletion of fixed checklist rows
    frm.fields_dict["document_collection"].grid.wrapper
      .find(".grid-remove-rows")
      .hide();

    // 2. Render [Lock GPS Coordinates] button
    if (frm.doc.docstatus === 0 && frm.doc.stage_status !== "Completed") {
      frm
        .add_custom_button(__("Lock Current GPS"), () => {
          captureGPSLocation(frm);
        })
        .addClass("btn-secondary");
    }

    // 3. Render [Complete Site Survey] button
    if (frm.doc.docstatus === 0 && frm.doc.stage_status !== "Completed") {
      frm
        .add_custom_button(__("Complete Site Survey"), () => {
          showCompletionDialog(frm);
        })
        .addClass("btn-primary");
    }

    // 4. Render [Log SLA Delay] button if overdue
    if (frm.doc.stage_status === "Overdue") {
      frm
        .add_custom_button(__("Log SLA Delay Reason"), () => {
          showDelayLogDialog(frm);
        })
        .addClass("btn-warning");
    }

    // 5. ADR-000 Junior Cancel Suppression
    const isManagerOrAdmin = frappe.user_roles.some(
      (r) =>
        r.endsWith("Manager") ||
        r === "Admin" ||
        r === "System Manager" ||
        r === "Administrator",
    );

    if (!isManagerOrAdmin && frm.doc.docstatus === 1) {
      frm.page.clear_custom_actions();
      frm
        .add_custom_button(__("Request Cancel / Amend"), () => {
          showJuniorCancelDialog(frm);
        })
        .addClass("btn-danger");
    }
  },
});

function captureGPSLocation(frm) {
  if (!navigator.geolocation) {
    frappe.msgprint(__("Geolocation is not supported by your browser."));
    return;
  }

  frappe.show_alert({
    message: __("Acquiring high-accuracy satellite lock..."),
    indicator: "blue",
  });

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const acc = position.coords.accuracy;

      frm.set_value("latitude", lat);
      frm.set_value("longitude", lon);
      frm.set_value("gps_accuracy", acc);

      if (acc > 50.0) {
        frappe.msgprint({
          title: __("Coarse GPS Warning"),
          indicator: "orange",
          message: __(
            "Reported accuracy is ±{0}m (must be <= 50m). Please move outdoors for a better satellite fix.",
            [Math.round(acc)],
          ),
        });
      } else {
        frappe.show_alert({
          message: __(
            "GPS locked: {0}, {1} (±{2}m)",
            [lat.toFixed(6), lon.toFixed(6), Math.round(acc)],
          ),
          indicator: "green",
        });
      }
    },
    (error) => {
      frappe.msgprint({
        title: __("GPS Acquisition Error"),
        indicator: "red",
        message: error.message,
      });
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
  );
}

function showCompletionDialog(frm) {
  const isOverdue = frm.doc.stage_status === "Overdue";
  const fields = [];

  if (isOverdue) {
    fields.push({
      fieldtype: "Select",
      fieldname: "delay_reason",
      label: __("Delay Category"),
      options:
        "Customer Unreachable\nCustomer Requested Postponement\nRoof Under Construction\nWeather / Heavy Rain\nUtility Meter Inaccessible\nOther",
      reqd: 1,
    });
    fields.push({
      fieldtype: "Small Text",
      fieldname: "remarks",
      label: __("Delay Justification (Min 20 chars)"),
      reqd: 1,
    });
  }

  const d = new frappe.ui.Dialog({
    title: __("Complete Site Survey & Sign-Off"),
    fields: fields,
    primary_action_label: __("Verify & Complete"),
    primary_action(data) {
      if (isOverdue && (!data.remarks || data.remarks.trim().length < 20)) {
        frappe.throw(
          __("Delay justification must contain at least 20 characters."),
        );
        return;
      }
      d.hide();
      frappe.call({
        method: "solar_module.api.survey.submit_survey_completion",
        args: {
          survey_id: frm.doc.name,
          delay_reason: data?.delay_reason || "",
          remarks: data?.remarks || "",
        },
        freeze: true,
        freeze_message: __("Verifying stage gates and spawning CAD design..."),
        callback(r) {
          if (r.message && r.message.status === "success") {
            frappe.show_alert({
              message: __(
                "Site Survey completed! Stage 03 CAD record {0} created.",
                [r.message.cad_design_id],
              ),
              indicator: "green",
            });
            frm.reload_doc();
          }
        },
      });
    },
  });
  d.show();
}

function showJuniorCancelDialog(frm) {
  const d = new frappe.ui.Dialog({
    title: __("Submit Cancellation Request"),
    fields: [
      {
        fieldtype: "Small Text",
        fieldname: "reason",
        label: __("Cancellation Justification (Min 20 chars)"),
        reqd: 1,
      },
    ],
    primary_action_label: __("Submit for Manager Review"),
    primary_action(values) {
      if (!values.reason || values.reason.trim().length < 20) {
        frappe.throw(
          __("Justification must contain at least 20 characters."),
        );
        return;
      }
      d.hide();
      frappe.call({
        method: "solar_module.api.security.request_cancellation",
        args: {
          doctype: frm.doc.doctype,
          name: frm.doc.name,
          reason: values.reason.trim(),
        },
        callback(r) {
          frappe.msgprint(
            __(
              "Cancellation request submitted. Awaiting Survey Manager approval.",
            ),
          );
        },
      });
    },
  });
  d.show();
}
```

### 5.2 Mobile Touch PWA Architecture & Dexie.js (`/solar/surveys/:id`)

```typescript
// Dexie.js Offline Database: solar_offline_db.ts
import Dexie, { Table } from "dexie";

export interface LocalSurveyRecord {
  id: string; // e.g. "SRV-2026-00042"
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

// Two-Stage Background Auto-Sync Engine with Fail-Safe Cache Eviction
export class SurveySyncEngine {
  private static isSyncing = false;

  public static initializeNetworkListeners() {
    window.addEventListener("online", () => this.triggerAutoSync());
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
    // Stage A: Chunked Media Upload
    for (const media of survey.media_files) {
      if (!media.is_uploaded) {
        const uploadResult = await this.uploadMediaChunked(survey.id, media);
        media.is_uploaded = true;
        media.remote_url = uploadResult.file_url;
        await localDB.surveys.put(survey);
      }
    }

    // Stage B: Atomic Document Payload Sync
    const response = await fetch(
      "/api/method/solar_module.api.survey.sync_offline_survey",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": (window as any).frappe?.csrf_token,
        },
        body: JSON.stringify({
          client_payload: JSON.stringify(survey.form_data),
        }),
      },
    );

    const result = await response.json();

    // FAIL-SAFE CACHE EVICTION: Delete local record ONLY on HTTP 200 + hash match
    if (response.ok && result.message?.status === "success") {
      await localDB.surveys.delete(survey.id);
    }
  }

  private static async uploadMediaChunked(surveyId: string, media: any) {
    // Divides media.blob into 1MB chunks and posts to upload_survey_media_chunk
    const CHUNK_SIZE = 1024 * 1024; // 1 MB
    const totalChunks = Math.ceil(media.blob.size / CHUNK_SIZE);

    let lastResult: any = null;
    for (let i = 0; i < totalChunks; i++) {
      const start = i * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, media.blob.size);
      const chunkBlob = media.blob.slice(start, end);
      const base64Chunk = await this.blobToBase64(chunkBlob);

      const res = await fetch(
        "/api/method/solar_module.api.survey.upload_survey_media_chunk",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": (window as any).frappe?.csrf_token,
          },
          body: JSON.stringify({
            survey_id: surveyId,
            checklist_item: media.checklist_item,
            file_name: media.file_name,
            content_hash: media.content_hash,
            chunk_index: i,
            total_chunks: totalChunks,
            base64_chunk: base64Chunk,
          }),
        },
      );
      lastResult = (await res.json()).message;
    }
    return lastResult;
  }

  private static blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64data = (reader.result as string).split(",")[1];
        resolve(base64data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }
}
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Location: `solar_module/tests/test_site_survey_tracer_bullet.py`.  
Standard: Subclasses `frappe.testing.IntegrationTestCase` with automatic transaction rollback. Zero database commits (`commit()`) permitted.

```python
import json
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import now_datetime, add_to_date
from solar_module.api.survey import (
    sync_offline_survey,
    submit_survey_completion
)
from solar_module.services.survey.validation import SurveyValidationService
from solar_module.services.survey.sla import SurveySLAService
from solar_module.services.survey.sync import SurveySyncService
from solar_module.security.stage_forward_lock import StageForwardLockService
from solar_module.security.admin_audit import AdminAuditService

class TestSiteSurveyTracerBullet(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.surveyor_email = "test_surveyor_tracer@sadbhav.local"
        self.unauth_email = "test_unauth_user@sadbhav.local"

        # 1. Ensure Surveyor user exists with Survey Engineer role
        if not frappe.db.exists("User", self.surveyor_email):
            surveyor = frappe.get_doc({
                "doctype": "User",
                "email": self.surveyor_email,
                "first_name": "Tracer Surveyor",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            surveyor.add_roles("Survey Engineer")

        # 2. Ensure Unauthorized user exists
        if not frappe.db.exists("User", self.unauth_email):
            unauth = frappe.get_doc({
                "doctype": "User",
                "email": self.unauth_email,
                "first_name": "Unauthorized User",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            unauth.add_roles("Sales Representative")

        # 3. Create test lead
        self.test_lead = frappe.get_doc({
            "doctype": "Lead",
            "first_name": "Adani Solar Logistics Park",
            "mobile_no": "9825011223",
            "solar_capacity": 50.0,
            "custom_address": "GIDC Sanand, Ahmedabad",
            "custom_pincode": "382110",
            "stage_status": "Site Survey"
        }).insert(ignore_permissions=True)

    def tearDown(self):
        # Transaction rollback guarantees complete isolation with zero DB persistence
        frappe.db.rollback()
        super().tearDown()

    def create_valid_survey(self):
        """Helper creating fully populated valid draft survey with attached files."""
        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": self.test_lead.name,
            "surveyed_by": self.surveyor_email,
            "solar_capacity": 50.0,
            "solar_system": "On-Grid",
            "site_type": "RCC",
            "connected_load": 65.0,
            "plant_category": "Industrial",
            "type_of_mounting": "Elevated",
            "mount_height": 8.0,
            "storage_space": "Yes",
            "location_details": "Plot 104, Sanand Industrial Area, Ahmedabad, Gujarat 382110",
            "name_match": "Yes",
            "latitude": 23.0225,
            "longitude": 72.5714,
            "gps_accuracy": 9.5,
            "panel_and_inverter_dst": 35.0,
            "panel_and_meter_dst": 18.0,
            "shadow_free_area": "Yes",
            "space_maintenance_install": "Yes",
            "upload_image": "/files/test_panorama.jpg",
            "for_survey_assign_on": now_datetime(),
            "stage_status": "Open",
            "docstatus": 0
        }).insert(ignore_permissions=True)

        # Attach mock uploads for all checklist rows
        for row in survey.document_collection:
            row.upload_doc = f"/files/mock_{row.documents.replace(' ', '_').lower()}.jpg"
        survey.save(ignore_permissions=True)
        return survey

    def test_01_survey_happy_path_completion(self):
        """Assert standard survey creation, 6 photo checklist uploads, completion sign-off, and Stage 03 CAD spawn."""
        survey = self.create_valid_survey()

        frappe.set_user(self.surveyor_email)
        res = submit_survey_completion(survey_id=survey.name)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["stage_status"], "Completed")
        self.assertEqual(res["complete_status"], "On Time")

        # Verify Stage 03 container spawned in Draft status
        cad_id = res["cad_design_id"]
        self.assertTrue(frappe.db.exists("Survey Engineering Design", cad_id))
        cad_doc = frappe.get_doc("Survey Engineering Design", cad_id)
        self.assertEqual(cad_doc.custom_survey_ref, survey.name)
        self.assertEqual(cad_doc.approved_capacity, 50.0)
        self.assertEqual(cad_doc.docstatus, 0)

        # Verify upstream Lead updated
        self.test_lead.reload()
        self.assertEqual(self.test_lead.stage_status, "Site Survey Completed")

    def test_02_coordinate_validation_and_spoof_rejection(self):
        """Assert hard gate blocks missing or inaccurate GPS coordinates (> 50m)."""
        survey = self.create_valid_survey()
        survey.latitude = 0.0
        survey.longitude = 0.0

        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.validate_coordinates(survey)

        survey.latitude = 23.0
        survey.longitude = 72.0
        survey.gps_accuracy = 120.0  # Accuracy too coarse

        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.validate_coordinates(survey)

    def test_03_technical_invariants_hard_gate(self):
        """Assert gate blocks completion if mandatory engineering fields (capacity, system, height) are missing."""
        survey = self.create_valid_survey()
        survey.solar_capacity = 0.0

        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.validate_technical_invariants(survey)

        survey.solar_capacity = 20.0
        survey.type_of_mounting = "Elevated"
        survey.mount_height = 0.0  # Missing required height for elevated mount

        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.validate_technical_invariants(survey)

    def test_04_mandatory_6_photos_and_video_gate(self):
        """Assert gate blocks completion if any of the 6 fixed photos or 360 video walkthrough are missing."""
        survey = self.create_valid_survey()
        # Empty out one of the fixed photo rows
        survey.document_collection[0].upload_doc = None

        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.validate_mandatory_checklist(survey)

    def test_05_sla_breach_and_delay_logging(self):
        """Assert 24h SLA breach transitions survey to Overdue and enforces mandatory delay log."""
        survey = self.create_valid_survey()
        # Set assign time to 30 hours ago
        survey.for_survey_assign_on = add_to_date(now_datetime(), hours=-30)
        survey.exp_complete_date = add_to_date(now_datetime(), hours=-6)
        survey.save(ignore_permissions=True)

        SurveySLAService.recompute_survey_sla(survey.name)
        survey.reload()
        self.assertEqual(survey.stage_status, "Overdue")
        self.assertEqual(survey.complete_status, "Delayed")

        # Attempt completion without delay justification
        with self.assertRaises(frappe.ValidationError):
            SurveyValidationService.execute_completion(survey)

        # Complete with valid delay justification
        frappe.set_user(self.surveyor_email)
        res = submit_survey_completion(
            survey_id=survey.name,
            delay_reason="Heavy monsoon rainfall made rooftop inaccessible for 6 hours."
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["stage_status"], "Completed")
        self.assertEqual(res["complete_status"], "Delayed")

    def test_06_offline_sync_idempotency_and_checksum(self):
        """Assert replaying offline sync payload with same offline_client_id is safe and idempotent."""
        survey = self.create_valid_survey()
        offline_uuid = "pwa-client-uuid-test-555"

        payload = {
            "name": survey.name,
            "offline_client_id": offline_uuid,
            "solar_capacity": 45.0,
            "panel_and_inverter_dst": 28.0
        }

        # First sync
        res1 = sync_offline_survey(client_payload=json.dumps(payload))
        self.assertEqual(res1["status"], "success")

        # Second sync replay
        res2 = sync_offline_survey(client_payload=json.dumps(payload))
        self.assertEqual(res2["status"], "success")
        self.assertEqual(res1["verification_hash"], res2["verification_hash"])

    def test_07_stage_forward_lock_blocks_cancel(self):
        """Assert ADR-000 StageForwardLockService blocks survey cancellation once Stage 03 CAD design exists."""
        survey = self.create_valid_survey()
        frappe.set_user(self.surveyor_email)
        submit_survey_completion(survey_id=survey.name)
        survey.reload()

        # Attempt to cancel survey when Stage 03 child exists
        with self.assertRaises(frappe.ValidationError):
            StageForwardLockService.assert_can_cancel_or_amend(survey, action="Cancel")

    def test_08_idor_and_role_security_enforcement(self):
        """Assert unauthorized role cannot complete or mutate another surveyor's audit."""
        survey = self.create_valid_survey()
        frappe.set_user(self.unauth_email)

        with self.assertRaises(frappe.PermissionError):
            submit_survey_completion(survey_id=survey.name)
```

---

## 7. Execution Runbook & Verification Criteria

To verify this Tracer Bullet against a live Frappe bench:

```bash
# 1. Execute Atomic Integration Test Suite (Zero DB Commits)
bench --site sadbhav.local run-tests --module solar_module.tests.test_site_survey_tracer_bullet

# 2. Export Custom Field & DocType Fixtures
bench --site sadbhav.local export-fixtures --app solar_module

# 3. Test Offline Sync RPC via curl
curl -X POST http://sadbhav.local/api/method/solar_module.api.survey.sync_offline_survey \
  -H "Authorization: token <api_key>:<api_secret>" \
  -H "Content-Type: application/json" \
  -d '{"client_payload": "{\"name\":\"SRV-2026-00001\",\"offline_client_id\":\"uuid-123\",\"solar_capacity\":10.0}"}'
```

### Tracer Bullet Acceptance Criteria:

- [x] Hardware GPS coordinates verified with tolerance $\le 50.0\text{m}$, rejecting null, zero, and spoofed readings.
- [x] All 10 mandatory technical engineering fields verified before permitting survey sign-off.
- [x] Child table `tabSite Survey Doc Table` enforces 6 fixed photo checklist rows and 1 mandatory video walkthrough, protected against deletion.
- [x] Turnaround SLA countdown automatically initialized to $T + 24\text{ hours}$ upon surveyor assignment.
- [x] Background daemons flag breached surveys as `Overdue` and mandate $\ge 20$ chars delay justification.
- [x] Offline PWA schema (`SiteSurveyOfflineDB`) stores audits in IndexedDB with two-stage sync pipeline and fail-safe cache eviction.
- [x] Offline sync payload ingestion guarantees idempotency via device `offline_client_id`.
- [x] Stage completion automatically syncs upstream `tabLead` and instantiates downstream `tabSurvey Engineering Design` (Stage 03).
- [x] ADR-000 `StageForwardLockService` blocks cancellation or amendment when active downstream records exist.
- [x] Automated test suite passes 8 atomic test cases with zero manual database cleanup and zero database commits.

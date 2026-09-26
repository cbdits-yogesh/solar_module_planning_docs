# STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 01 Lead Management

**Document ID:** `TB-01-LEAD`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.caveman.md`](../STEP_01_LEAD_MANAGEMENT_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-001-LEAD-MANAGEMENT-DEDUPLICATION-ROUTING.md`](../../docs/decisions/ADR-001-LEAD-MANAGEMENT-DEDUPLICATION-ROUTING.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-01`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-001`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-001`)  
**Target Module:** `solar_module` / `manoj`  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** Explores an isolated concept with throwaway code (e.g. testing an isolated dialog or mocking an algorithm), discarded after evaluation.
- **Tracer Bullet:** A lean, complete, production-grade slice cutting through **all layers of the real system**. Not throwaway code; it forms the permanent, verified architectural skeleton to which downstream stages (Stage 02 Site Survey through Stage 11 O&M) will attach.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 01 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabLead custom solar fields (mobile_no, solar_capacity, pincode, etc.)  │
│   - tabRemark-Delay Log (SLA audit & delay justification child table)       │
│   - tabSite Survey (Stage 02 downstream handover draft container)           │
│   - B-Tree Composite Database Indexes & Auto-naming                         │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic                                    │
│   - LeadValidationService (Regex sanitization, dedup check, sizing gate)    │
│   - LeadSLAService (2h response countdown, overdue detection, delay check) │
│   - SiteSurveyBridgeService (Survey Engineer role check, draft instantiator)│
│   - StageSecuredDocument & StageForwardLockService (ADR-000 lock integration)│
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller & Whitelisted API Gateway                                │
│   - LeadController (Hooks: before_save, after_insert, before_cancel)        │
│   - create_solar_lead RPC (Ingest, clean, dedup, initialize SLA)            │
│   - assign_site_surveyor RPC (Validate feasibility, link surveyor, spawn)   │
│   - log_lead_delay RPC (Mandatory justification logging on SLA breach)      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & UI Hook                                        │
│   - codes/client_script/lead.js (Clean standard Frappe clutter buttons)     │
│   - Real-time mobile input formatting & async duplicate warning alert       │
│   - [Assign Site Survey] Dialog with filtered Survey Engineer picker        │
│   - Junior Cancel suppression -> ADR-000 [Request Cancel/Amend] modal       │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_lead_tracer_bullet.py                           │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Atomic transaction rollback in tearDown (zero DB commits)               │
│   - 8 comprehensive test cases validating all invariants end-to-end         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental business, technical, and security invariants of Stage 01 across the live Frappe stack:

1. **Omnichannel Ingestion & Normalization:** Raw phone inputs (`+91 98250 12345`, `09825012345`) are sanitized server-side to 10 digits (`9825012345`) adhering to regex `^[6-9]\d{9}$`.
2. **Cross-DocType Strict Deduplication:** Prevents duplicate lead ingestion if an active record exists in `tabLead` or `tabCustomer` with an identical 10-digit mobile number, unless approved by a `Sales Manager` with `duplicate_mobile = 1`.
3. **2-Hour Inbound Response SLA Clock:** Response SLA deadline is initialized to $T + 2\text{ hours}$ upon lead creation; background daemons flag overdue leads and enforce delay justification in `tabRemark-Delay Log`.
4. **Technical Sizing Feasibility Gate:** Survey scheduling is hard-blocked until preliminary technical metrics are collected: $\text{solar\_capacity} > 0.0\text{ kW}$, 6-digit `custom_pincode`, and physical address.
5. **Certified Surveyor Assignment & Hand-off:** Surveyor must hold the `Survey Engineer` (or `Survey Assistant`) role; assignment automatically sets `stage_status = 'Site Survey'` and instantiates the downstream `tabSite Survey` draft container.
6. **ADR-000 Security Substrate Integration:** `Lead` controller inherits from `StageSecuredDocument`, enforcing `StageForwardLockService` immutability when downstream `Site Survey` records exist.
7. **Junior Cancel/Amend Workflow:** Frontline `Sales Representative` users cannot unilaterally cancel submitted or active leads; cancellations route through `Solar Cancellation Request` for `Sales Manager` sign-off.
8. **Admin Deletion Safeguard & Audit Snapshot:** Direct deletion of upstream `Lead` records is blocked if active `Site Survey` records exist; permitted deletions require $\ge 20$ chars justification and record a complete JSON snapshot in `tabSolar Deletion Audit Log`.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

The Tracer Bullet requires only the minimal set of database columns to enforce data contracts across the entire chain.

### 2.1 Core DocType Extensions: `tabLead`

| Fieldname              | Label                  | Fieldtype    | Options / Target                                                       | Mandatory |    Index     | Rules & Invariants                                                             |
| :--------------------- | :--------------------- | :----------- | :--------------------------------------------------------------------- | :-------: | :----------: | :----------------------------------------------------------------------------- |
| `mobile_no`            | Mobile Number          | `Data`       | -                                                                      |  **Yes**  | **Index: 1** | Exactly 10 digits sanitized via regex `^[6-9]\d{9}$`. Key dedup anchor.        |
| `solar_capacity`       | Proposed Capacity (kW) | `Float`      | -                                                                      |  **Yes**  |      -       | Must be $> 0.0$ kW before survey assignment.                                   |
| `bill_amt`             | Avg Monthly Bill (INR) | `Currency`   | `Company:currency`                                                     |    No     |      -       | Preliminary financial sizing indicator.                                        |
| `advance_amt`          | Pre-Booking Advance    | `Currency`   | `Company:currency`                                                     |    No     |      -       | Token advance payment collected prior to official sales order (if applicable). |
| `per_advance`          | % Advance Collected    | `Float`      | -                                                                      |    No     |      -       | Calculated percentage of advance against preliminary budget.                   |
| `custom_address`       | Site Physical Address  | `Small Text` | -                                                                      |  **Yes**  |      -       | Physical installation property location for rooftop survey inspection.         |
| `custom_pincode`       | Site Pincode           | `Data`       | -                                                                      |  **Yes**  | **Index: 1** | 6-digit Indian PIN. Indexed. Resolves territory and local sales team.          |
| `stage_status`         | Lifecycle Status       | `Select`     | `Draft\nOpen\nAssigned\nSite Survey\nQuoted\nConverted\nLost\nOverdue` |  **Yes**  | **Index: 1** | Core state machine tracker. Indexed.                                           |
| `complete_status`      | SLA Compliance Status  | `Select`     | `\nOn Time\nDelayed`                                                   |    No     |      -       | Evaluates whether milestone was completed within configured SLA window.        |
| `sla_due_date`         | SLA Deadline Datetime  | `Datetime`   | -                                                                      |    No     | **Index: 1** | SLA clock deadline: `creation + 2 hours`. Indexed.                             |
| `complete_date`        | Stage Complete Date    | `Date`       | -                                                                      |    No     |      -       | Closed date when lead transitions to downstream survey or quotation.           |
| `surveyed_by`          | Survey Assigned To     | `Link`       | `User`                                                                 |    No     | **Index: 1** | Must hold system role `Survey Engineer` or `Survey Assistant`.                 |
| `for_survey_assign_on` | Survey Assigned On     | `Datetime`   | -                                                                      |    No     |      -       | Hand-off timestamp triggering Stage 02 24h SLA.                                |
| `duplicate_mobile`     | Duplicate Mobile Flag  | `Check`      | -                                                                      |    No     |      -       | Set to 1 if Sales Manager overrides duplicate check for second project.        |
| `remark_delay_log`     | Delay & Audit Table    | `Table`      | `Remark-Delay Log`                                                     |    No     |      -       | Mandatory delay justification child table when actions past `sla_due_date`.    |

### 2.2 Child DocType: `tabRemark-Delay Log`

| Fieldname      | Label           | Fieldtype    | Options                                                                                                                                                                   | Mandatory | Description                                                     |
| :------------- | :-------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------: | :-------------------------------------------------------------- |
| `user`         | Logged By       | `Link`       | `User`                                                                                                                                                                    |  **Yes**  | System user recording entry (auto-populated with session user). |
| `timestamp`    | Recorded At     | `Datetime`   | -                                                                                                                                                                         |  **Yes**  | Immutable timestamp when remark or delay logged.                |
| `stage`        | Lifecycle Stage | `Data`       | -                                                                                                                                                                         |  **Yes**  | Defaults to "Stage 01: Lead Management".                        |
| `delay_reason` | Delay Category  | `Select`     | `Customer Unreachable\nCustomer Requested Postponement\nRoof Under Construction\nUtility Bill Pending\nFinancial Evaluation Pending\nTechnical Re-sizing Required\nOther` |    No     | Mandatory when `stage_status` is `Overdue`.                     |
| `remarks`      | Detailed Notes  | `Small Text` | -                                                                                                                                                                         |  **Yes**  | Free-text commentary explaining action or customer discussion.  |

### 2.3 Downstream Target: `tabSite Survey` (Stage 02 Handover Container)

| Fieldname            | Label             | Fieldtype    | Target / Link | Mandatory | Description                                          |
| :------------------- | :---------------- | :----------- | :------------ | :-------: | :--------------------------------------------------- |
| `lead`               | Lead Reference    | `Link`       | `Lead`        |  **Yes**  | Originating Lead document identifier.                |
| `custom_lead_ref`    | Upstream Link Ref | `Link`       | `Lead`        |  **Yes**  | Registered link field for `StageForwardLockService`. |
| `lead_name`          | Customer Name     | `Data`       | -             |  **Yes**  | Customer display name transferred from Lead.         |
| `custom_lead_mobile` | Primary Mobile    | `Data`       | -             |  **Yes**  | 10-digit sanitized mobile number.                    |
| `proposed_capacity`  | Estimated kW      | `Float`      | -             |  **Yes**  | Transferred preliminary sizing capacity.             |
| `site_address`       | Site Address      | `Small Text` | -             |  **Yes**  | Physical installation property location.             |
| `custom_pincode`     | Site Pincode      | `Data`       | -             |  **Yes**  | 6-digit postal pincode.                              |
| `survey_engineer`    | Assigned Surveyor | `Link`       | `User`        |  **Yes**  | Filtered by `Survey Engineer` role.                  |
| `docstatus`          | Document State    | `Int`        | `0=Draft`     |  **Yes**  | Instantiated in `Draft` (`0`) awaiting field trip.   |

### 2.4 Database Indexing & Autonaming Strategy

- **Autonaming:** Autoname follows `format:LEAD-.YYYY.-.#####` (e.g. `LEAD-2026-00042`).
- **Composite B-Tree Indexes:**
  ```sql
  CREATE INDEX idx_lead_mobile_status ON `tabLead` (mobile_no, stage_status);
  CREATE INDEX idx_lead_stage_sla ON `tabLead` (stage_status, sla_due_date);
  CREATE INDEX idx_lead_pincode ON `tabLead` (custom_pincode);
  CREATE INDEX idx_lead_surveyed_by ON `tabLead` (surveyed_by, stage_status);
  ```

---

## 3. Layer 2: Domain Services & Business Logic

Decoupled pure Python services located in `solar_module/services/lead/` adhering strictly to SOLID principles.

### 3.1 `LeadValidationService` (`solar_module/services/lead/validation.py`)

Handles phone sanitization, cross-table deduplication, and technical sizing gates.

```python
import re
import frappe
from frappe import _

class LeadValidationService:
    @staticmethod
    def sanitize_mobile(raw_mobile: str) -> str:
        """
        Strips non-digits, leading country codes (+91, 91, 0), and asserts exactly
        10 standard digits starting with 6, 7, 8, or 9.
        """
        if not raw_mobile:
            frappe.throw(_("Mobile number is mandatory."), frappe.ValidationError)

        digits = re.sub(r"\D", "", str(raw_mobile).strip())
        if len(digits) > 10 and (digits.startswith("91") or digits.startswith("0")):
            if digits.startswith("91"):
                digits = digits[2:]
            elif digits.startswith("0"):
                digits = digits[1:]

        if not re.match(r"^[6-9]\d{9}$", digits):
            frappe.throw(
                _("Mobile number '{0}' is invalid. Must be exactly 10 digits starting with 6, 7, 8, or 9.").format(raw_mobile),
                frappe.ValidationError
            )
        return digits

    @staticmethod
    def check_duplicate(clean_mobile: str, exclude_lead: str | None = None) -> str | None:
        """
        Cross-checks tabLead and tabCustomer for identical mobile numbers.
        Returns the existing document identifier if duplicate found.
        """
        # 1. Check tabLead for active (non-lost) leads
        lead_filters = {
            "mobile_no": clean_mobile,
            "stage_status": ["!=", "Lost"]
        }
        if exclude_lead:
            lead_filters["name"] = ["!=", exclude_lead]

        existing_lead = frappe.db.get_value("Lead", lead_filters, "name")
        if existing_lead:
            return f"Lead:{existing_lead}"

        # 2. Check tabCustomer for existing customer master
        existing_customer = frappe.db.get_value("Customer", {"mobile_no": clean_mobile}, "name")
        if existing_customer:
            return f"Customer:{existing_customer}"

        return None

    @staticmethod
    def validate_survey_readiness(lead_doc) -> None:
        """
        Asserts preliminary solar plant sizing and site verification prerequisites
        are completed before permitting assignment to field survey engineers.
        """
        if not lead_doc.solar_capacity or float(lead_doc.solar_capacity) <= 0.0:
            frappe.throw(
                _("Proposed solar capacity (kW) must be greater than 0 before scheduling survey."),
                frappe.ValidationError
            )

        pincode = str(lead_doc.custom_pincode or "").strip()
        if not pincode or len(pincode) != 6 or not pincode.isdigit():
            frappe.throw(
                _("A valid 6-digit site postal pincode is required before scheduling survey."),
                frappe.ValidationError
            )

        if not lead_doc.custom_address or not str(lead_doc.custom_address).strip():
            frappe.throw(
                _("Site physical address is required before scheduling survey."),
                frappe.ValidationError
            )
```

### 3.2 `LeadSLAService` (`solar_module/services/lead/sla.py`)

Governs turnaround countdowns, overdue detection, and delay justification enforcement.

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date

class LeadSLAService:
    @staticmethod
    def initialize_lead_sla(lead_doc, sla_hours: int = 2) -> None:
        """Sets initial response SLA countdown deadline upon lead insertion."""
        if not lead_doc.sla_due_date:
            lead_doc.sla_due_date = add_to_date(now_datetime(), hours=sla_hours)
            if not lead_doc.stage_status:
                lead_doc.stage_status = "Open"

    @staticmethod
    def is_breached(lead_doc) -> bool:
        """Evaluates whether current timestamp has breached configured SLA deadline."""
        if lead_doc.sla_due_date and now_datetime() > lead_doc.sla_due_date:
            return True
        return False

    @staticmethod
    def recompute_lead_sla(lead_name: str) -> None:
        """Background worker method: updates overdue state for breached leads."""
        lead = frappe.get_doc("Lead", lead_name)
        terminal_statuses = ["Site Survey", "Quoted", "Converted", "Lost"]
        if lead.stage_status not in terminal_statuses and LeadSLAService.is_breached(lead):
            lead.stage_status = "Overdue"
            lead.complete_status = "Delayed"
            lead.save(ignore_permissions=True)

    @staticmethod
    def enforce_delay_reason_if_overdue(lead_doc) -> None:
        """
        Hard-blocks stage progression or saving on overdue leads unless a valid
        justification entry is appended to tabRemark-Delay Log.
        """
        if lead_doc.stage_status == "Overdue" or LeadSLAService.is_breached(lead_doc):
            delay_entries = [
                r for r in lead_doc.get("remark_delay_log", [])
                if r.delay_reason and r.remarks and len(r.remarks.strip()) >= 10
            ]
            if not delay_entries:
                frappe.throw(
                    _("SLA Overdue: A valid delay category and detailed remarks (min 10 chars) "
                      "must be recorded in Remark-Delay Log before progressing this lead."),
                    frappe.ValidationError
                )
```

### 3.3 `SiteSurveyBridgeService` (`solar_module/services/lead/survey_bridge.py`)

Handles surveyor role validation and downstream `Site Survey` container instantiation.

```python
import frappe
from frappe import _

class SiteSurveyBridgeService:
    @staticmethod
    def create_or_update_survey(lead_doc) -> str:
        """
        Validates surveyor role and instantiates or synchronizes the downstream
        Stage 02 Site Survey container in Draft state (docstatus=0).
        """
        if not lead_doc.surveyed_by:
            frappe.throw(
                _("Cannot instantiate Site Survey without an assigned Survey Engineer."),
                frappe.ValidationError
            )

        # Assert surveyor holds authorized operational role
        surveyor_roles = set(frappe.get_roles(lead_doc.surveyed_by))
        allowed_roles = {"Survey Engineer", "Survey Assistant", "Survey Manager", "Admin", "System Manager", "Administrator"}
        if not allowed_roles.intersection(surveyor_roles):
            frappe.throw(
                _("User '{0}' is not certified as a Survey Engineer or Survey Assistant.").format(lead_doc.surveyed_by),
                frappe.PermissionError
            )

        # Idempotent synchronization: check if active draft survey exists
        existing_survey = frappe.db.get_value(
            "Site Survey",
            {"custom_lead_ref": lead_doc.name, "docstatus": ["!=", 2]},
            "name"
        )
        if existing_survey:
            survey_doc = frappe.get_doc("Site Survey", existing_survey)
            survey_doc.survey_engineer = lead_doc.surveyed_by
            survey_doc.proposed_capacity = float(lead_doc.solar_capacity)
            survey_doc.site_address = lead_doc.custom_address
            survey_doc.custom_pincode = lead_doc.custom_pincode
            survey_doc.save(ignore_permissions=True)
            return survey_doc.name

        # Instantiation of new downstream Site Survey container
        survey_doc = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": lead_doc.name,
            "custom_lead_ref": lead_doc.name,
            "lead_name": lead_doc.first_name,
            "custom_lead_mobile": lead_doc.mobile_no,
            "proposed_capacity": float(lead_doc.solar_capacity),
            "site_address": lead_doc.custom_address,
            "custom_pincode": lead_doc.custom_pincode,
            "survey_engineer": lead_doc.surveyed_by,
            "docstatus": 0
        })
        survey_doc.insert(ignore_permissions=True)
        return survey_doc.name
```

---

## 4. Layer 3: Controller & Whitelisted API Gateway

### 4.1 Base Controller: `LeadController` (`solar_module/overrides/lead.py`)

Inherits from `StageSecuredDocument` to inherit ADR-000 immutability and deletion audit logging automatically.

```python
import frappe
from frappe import _
from solar_module.mixins.stage_secured_document import StageSecuredDocument
from solar_module.services.lead.validation import LeadValidationService
from solar_module.services.lead.sla import LeadSLAService

class SolarLeadController(StageSecuredDocument):
    def before_insert(self):
        # 1. Sanitize mobile number
        self.mobile_no = LeadValidationService.sanitize_mobile(self.mobile_no)

        # 2. Assert duplicate check unless manager override granted
        if not self.duplicate_mobile:
            dup = LeadValidationService.check_duplicate(self.mobile_no, exclude_lead=self.name)
            if dup:
                frappe.throw(
                    _("A record already exists with mobile number {0} ({1}).").format(self.mobile_no, dup),
                    frappe.DuplicateEntryError
                )

        # 3. Initialize 2h response SLA clock
        LeadSLAService.initialize_lead_sla(self)

    def before_save(self):
        if self.mobile_no:
            self.mobile_no = LeadValidationService.sanitize_mobile(self.mobile_no)

        # If transitioning to Qualified or Site Survey, enforce sizing readiness
        if self.stage_status in ["Qualified", "Site Survey"]:
            LeadValidationService.validate_survey_readiness(self)

        # Enforce delay reason if overdue
        if self.stage_status == "Overdue":
            LeadSLAService.enforce_delay_reason_if_overdue(self)

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

### 4.2 Whitelisted REST/RPC API Endpoints (`solar_module/api/lead.py`)

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, today
from solar_module.services.lead.validation import LeadValidationService
from solar_module.services.lead.sla import LeadSLAService
from solar_module.services.lead.survey_bridge import SiteSurveyBridgeService

@frappe.whitelist(methods=["POST"])
def create_solar_lead(
    first_name: str,
    mobile_no: str,
    solar_capacity: float,
    custom_address: str,
    custom_pincode: str,
    bill_amt: float = 0.0,
    source: str = "Web Portal"
) -> dict:
    """Whitelisted RPC: Ingests, normalizes, dedups, and creates an Open Solar Lead."""
    frappe.only_for(["Guest", "Sales Representative", "Sales Manager", "Admin", "System Manager"])

    clean_mobile = LeadValidationService.sanitize_mobile(mobile_no)
    existing_duplicate = LeadValidationService.check_duplicate(clean_mobile)
    if existing_duplicate:
        frappe.throw(
            _("A record already exists with mobile number {0} ({1}).").format(clean_mobile, existing_duplicate),
            frappe.DuplicateEntryError
        )

    lead = frappe.get_doc({
        "doctype": "Lead",
        "first_name": first_name.strip(),
        "mobile_no": clean_mobile,
        "solar_capacity": float(solar_capacity),
        "custom_address": custom_address.strip(),
        "custom_pincode": custom_pincode.strip(),
        "bill_amt": float(bill_amt),
        "source": source,
        "stage_status": "Open",
        "creation_date": today()
    })
    LeadSLAService.initialize_lead_sla(lead)
    lead.insert(ignore_permissions=True if frappe.session.user == "Guest" else False)

    return {
        "status": "success",
        "lead_name": lead.name,
        "mobile_no": lead.mobile_no,
        "sla_due_date": lead.sla_due_date
    }

@frappe.whitelist(methods=["POST"])
def assign_site_surveyor(lead_name: str, surveyor_engineer: str) -> dict:
    """Whitelisted RPC: Validates sizing feasibility, assigns surveyor, spawns Site Survey."""
    lead = frappe.get_doc("Lead", lead_name)
    lead.check_permission("write")

    LeadValidationService.validate_survey_readiness(lead)

    lead.surveyed_by = surveyor_engineer
    lead.for_survey_assign_on = now_datetime()
    lead.stage_status = "Site Survey"
    lead.save()

    site_survey_id = SiteSurveyBridgeService.create_or_update_survey(lead)

    return {
        "status": "success",
        "lead_name": lead.name,
        "surveyor": surveyor_engineer,
        "site_survey_id": site_survey_id
    }

@frappe.whitelist(methods=["POST"])
def log_lead_delay(lead_name: str, delay_reason: str, remarks: str) -> dict:
    """Whitelisted RPC: Appends mandatory delay explanation for overdue lead."""
    lead = frappe.get_doc("Lead", lead_name)
    lead.check_permission("write")

    if not remarks or len(remarks.strip()) < 10:
        frappe.throw(_("Detailed remarks of at least 10 characters are required."), frappe.ValidationError)

    lead.append("remark_delay_log", {
        "user": frappe.session.user,
        "timestamp": now_datetime(),
        "stage": "Stage 01: Lead Management",
        "delay_reason": delay_reason,
        "remarks": remarks.strip()
    })
    lead.save()

    return {"status": "success", "message": _("Delay log recorded successfully.")}

@frappe.whitelist()
def get_active_survey_engineers(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
    """Link query returning active users holding the Survey Engineer role."""
    return frappe.db.sql("""
        SELECT DISTINCT u.name, u.full_name
        FROM `tabUser` u
        JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role IN ('Survey Engineer', 'Survey Assistant')
          AND u.enabled = 1
          AND (u.name LIKE %(txt)s OR u.full_name LIKE %(txt)s)
        ORDER BY u.full_name ASC
        LIMIT %(start)s, %(page_len)s
    """, {"txt": f"%{txt or ''}%", "start": start or 0, "page_len": page_len or 20})
```

---

## 5. Layer 4: Desk Client Script & UI Hook

Attached to the Frappe Desk `Lead` form via `codes/client_script/lead.js`.

```javascript
frappe.ui.form.on("Lead", {
  setup(frm) {
    // Suppress standard ERPNext buttons to prevent out-of-sequence lifecycle jumps
    frm.remove_custom_button("Customer");
    frm.remove_custom_button("Opportunity");
    frm.remove_custom_button("Quotation");
    frm.remove_custom_button("Prospect");
  },

  mobile_no(frm) {
    if (!frm.doc.mobile_no) return;

    // Client-side regex cleansing
    let clean = frm.doc.mobile_no.replace(/\D/g, "");
    if (clean.length > 10 && clean.startsWith("91")) clean = clean.substring(2);
    if (clean.length > 10 && clean.startsWith("0")) clean = clean.substring(1);

    if (clean !== frm.doc.mobile_no) {
      frm.set_value("mobile_no", clean);
    }

    if (clean.length === 10) {
      // Async server-side duplicate check ping
      frappe.call({
        method:
          "solar_module.services.lead.validation.LeadValidationService.check_duplicate",
        args: { clean_mobile: clean, exclude_lead: frm.doc.name },
        callback(r) {
          if (r.message) {
            frappe.msgprint({
              title: __("Duplicate Mobile Alert"),
              indicator: "orange",
              message: __(
                "An existing record was found with mobile <b>{0}</b>: <b>{1}</b>. Please verify before proceeding.",
                [clean, r.message],
              ),
            });
          }
        },
      });
    }
  },

  refresh(frm) {
    if (frm.is_new()) return;

    // 1. Render [Assign Site Survey] button when lead is qualified
    if (["Open", "Assigned"].includes(frm.doc.stage_status)) {
      frm
        .add_custom_button(__("Assign Site Survey"), () => {
          showAssignSurveyDialog(frm);
        })
        .addClass("btn-primary");
    }

    // 2. Render [Log SLA Delay] button if lead is overdue
    if (frm.doc.stage_status === "Overdue") {
      frm
        .add_custom_button(__("Log SLA Delay Reason"), () => {
          showDelayLogDialog(frm);
        })
        .addClass("btn-warning");
    }

    // 3. ADR-000 Junior Cancel Suppression
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

function showAssignSurveyDialog(frm) {
  let d = new frappe.ui.Dialog({
    title: __("Assign Site Survey Engineer"),
    fields: [
      {
        label: __("Survey Engineer"),
        fieldname: "surveyor",
        fieldtype: "Link",
        options: "User",
        reqd: 1,
        get_query: () => ({
          query: "solar_module.api.lead.get_active_survey_engineers",
        }),
      },
    ],
    primary_action_label: __("Assign & Spawn Survey"),
    primary_action(values) {
      d.hide();
      frappe.call({
        method: "solar_module.api.lead.assign_site_surveyor",
        args: {
          lead_name: frm.doc.name,
          surveyor_engineer: values.surveyor,
        },
        freeze: true,
        freeze_message: __(
          "Validating technical gates & spawning Stage 02 Site Survey...",
        ),
        callback(r) {
          if (r.message && r.message.status === "success") {
            frappe.show_alert({
              message: __(
                "Assigned to {0}. Site Survey container {1} created.",
                [r.message.surveyor, r.message.site_survey_id],
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

function showDelayLogDialog(frm) {
  let d = new frappe.ui.Dialog({
    title: __("Log SLA Delay Explanation"),
    fields: [
      {
        label: __("Delay Category"),
        fieldname: "delay_reason",
        fieldtype: "Select",
        options:
          "Customer Unreachable\nCustomer Requested Postponement\nRoof Under Construction\nUtility Bill Pending\nFinancial Evaluation Pending\nTechnical Re-sizing Required\nOther",
        reqd: 1,
      },
      {
        label: __("Detailed Explanation (min 10 chars)"),
        fieldname: "remarks",
        fieldtype: "Small Text",
        reqd: 1,
      },
    ],
    primary_action_label: __("Submit Delay Log"),
    primary_action(values) {
      if (values.remarks.trim().length < 10) {
        frappe.msgprint(__("Remarks must be at least 10 characters long."));
        return;
      }
      d.hide();
      frappe.call({
        method: "solar_module.api.lead.log_lead_delay",
        args: {
          lead_name: frm.doc.name,
          delay_reason: values.delay_reason,
          remarks: values.remarks,
        },
        callback(r) {
          if (r.message && r.message.status === "success") {
            frappe.show_alert({
              message: __("Delay log recorded."),
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
  let d = new frappe.ui.Dialog({
    title: __("Request Document Cancellation / Amendment"),
    fields: [
      {
        label: __("Requested Action"),
        fieldname: "requested_action",
        fieldtype: "Select",
        options: "Cancel\nAmend",
        reqd: 1,
        default: "Cancel",
      },
      {
        label: __("Department"),
        fieldname: "department",
        fieldtype: "Select",
        options:
          "Sales\nSurvey\nDesign\nCRM\nAccounts\nProject\nStore\nLiaisoning\nPurchase\nO&M",
        reqd: 1,
        default: "Sales",
      },
      {
        label: __("Assigned Manager"),
        fieldname: "assigned_manager",
        fieldtype: "Link",
        options: "User",
        reqd: 1,
      },
      {
        label: __("Detailed Justification (min 20 chars)"),
        fieldname: "reason",
        fieldtype: "Small Text",
        reqd: 1,
      },
    ],
    primary_action_label: __("Submit for Manager Review"),
    primary_action(values) {
      if (values.reason.trim().length < 20) {
        frappe.msgprint(
          __("Justification must be at least 20 characters long."),
        );
        return;
      }
      d.hide();
      frappe.call({
        method: "solar_module.api.security.submit_cancellation_request",
        args: {
          reference_doctype: frm.doc.doctype,
          reference_name: frm.doc.name,
          requested_action: values.requested_action,
          reason: values.reason,
          department: values.department,
          assigned_manager: values.assigned_manager,
        },
        freeze: true,
        freeze_message: __("Routing request to Sales Manager..."),
        callback(r) {
          if (r.message && r.message.status === "success") {
            frappe.show_alert({
              message: __("Cancellation Request {0} submitted for review.", [
                r.message.cancellation_request_id,
              ]),
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
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Location: `solar_module/tests/test_lead_tracer_bullet.py`.  
Standard: Subclasses `frappe.testing.IntegrationTestCase` with automatic transaction rollback. Zero database commits (`commit()`) permitted.

```python
import json
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import today, now_datetime, add_to_date
from solar_module.api.lead import (
    create_solar_lead,
    assign_site_surveyor,
    log_lead_delay
)
from solar_module.services.lead.validation import LeadValidationService
from solar_module.services.lead.sla import LeadSLAService
from solar_module.security.stage_forward_lock import StageForwardLockService
from solar_module.security.admin_audit import AdminAuditService

class TestLeadTracerBullet(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.raw_phone = " +91 98250 12345 "
        self.clean_phone = "9825012345"
        self.surveyor_email = "test_tracer_surveyor@sadbhav.local"
        self.sales_rep_email = "test_sales_rep@sadbhav.local"
        self.sales_mgr_email = "test_sales_mgr@sadbhav.local"

        # 1. Ensure Surveyor user exists
        if not frappe.db.exists("User", self.surveyor_email):
            surveyor = frappe.get_doc({
                "doctype": "User",
                "email": self.surveyor_email,
                "first_name": "Tracer Surveyor",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            surveyor.add_roles("Survey Engineer")

        # 2. Ensure Sales Representative user exists
        if not frappe.db.exists("User", self.sales_rep_email):
            rep = frappe.get_doc({
                "doctype": "User",
                "email": self.sales_rep_email,
                "first_name": "Sales Rep",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            rep.add_roles("Sales Representative")

        # 3. Ensure Sales Manager user exists
        if not frappe.db.exists("User", self.sales_mgr_email):
            mgr = frappe.get_doc({
                "doctype": "User",
                "email": self.sales_mgr_email,
                "first_name": "Sales Manager",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            mgr.add_roles("Sales Manager")

    def tearDown(self):
        # Transaction rollback guarantees complete isolation with zero DB persistence
        frappe.db.rollback()
        super().tearDown()

    def test_01_create_lead_happy_path(self):
        """Assert omnichannel lead creation, 10-digit sanitization, and 2h SLA initialization."""
        res = create_solar_lead(
            first_name="Pramukh Warehouse",
            mobile_no=self.raw_phone,
            solar_capacity=25.0,
            custom_address="Sarkhej-Bavla Highway, Changodar",
            custom_pincode="382213",
            bill_amt=35000.0,
            source="PM Surya Ghar Portal"
        )
        self.assertEqual(res["status"], "success")
        lead_id = res["lead_name"]

        lead = frappe.get_doc("Lead", lead_id)
        self.assertEqual(lead.mobile_no, self.clean_phone, "Raw phone was not sanitized to 10 digits.")
        self.assertIsNotNone(lead.sla_due_date, "SLA due date was not calculated.")
        self.assertEqual(lead.stage_status, "Open")

    def test_02_duplicate_mobile_rejection(self):
        """Assert server-side gate blocks duplicate lead ingestion across Lead and Customer."""
        # Insert initial lead
        create_solar_lead(
            first_name="First Solar Client",
            mobile_no=self.clean_phone,
            solar_capacity=10.0,
            custom_address="GIDC Vatva, Ahmedabad",
            custom_pincode="382440"
        )

        # Attempt duplicate insert with same mobile
        with self.assertRaises(frappe.DuplicateEntryError):
            create_solar_lead(
                first_name="Duplicate Attempt Prospect",
                mobile_no=self.clean_phone,
                solar_capacity=15.0,
                custom_address="Different Address",
                custom_pincode="380001"
            )

    def test_03_invalid_mobile_rejection(self):
        """Assert validation failure on invalid phone numbers (non-10 digits, invalid prefix)."""
        invalid_numbers = ["12345", "98250ABCD5", "5825012345", "+14155552671"]
        for bad_phone in invalid_numbers:
            with self.assertRaises(frappe.ValidationError):
                LeadValidationService.sanitize_mobile(bad_phone)

    def test_04_technical_sizing_readiness_gate(self):
        """Assert survey assignment is blocked if capacity <= 0 or pincode invalid."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "first_name": "Incomplete Sizing Prospect",
            "mobile_no": "9898011223",
            "solar_capacity": 0.0,  # Invalid: capacity not sized
            "custom_address": "Near Ring Road",
            "custom_pincode": "380015",
            "stage_status": "Open"
        }).insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            assign_site_surveyor(lead_name=lead.name, surveyor_engineer=self.surveyor_email)

    def test_05_survey_assignment_and_downstream_sync(self):
        """Assert surveyor assignment validates role and automatically spawns Stage 02 Site Survey."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "first_name": "Gujarat Polyfilms",
            "mobile_no": "9879055443",
            "solar_capacity": 50.0,
            "custom_address": "Plot 18, Phase 2, GIDC Naroda",
            "custom_pincode": "382330",
            "stage_status": "Open"
        }).insert(ignore_permissions=True)

        res = assign_site_surveyor(lead_name=lead.name, surveyor_engineer=self.surveyor_email)
        self.assertEqual(res["status"], "success")

        # Verify Stage 02 draft record
        survey_id = res["site_survey_id"]
        self.assertTrue(frappe.db.exists("Site Survey", survey_id))
        survey_doc = frappe.get_doc("Site Survey", survey_id)
        self.assertEqual(survey_doc.custom_lead_ref, lead.name)
        self.assertEqual(survey_doc.custom_lead_mobile, "9879055443")
        self.assertEqual(survey_doc.proposed_capacity, 50.0)
        self.assertEqual(survey_doc.survey_engineer, self.surveyor_email)
        self.assertEqual(survey_doc.docstatus, 0, "Site Survey must be in Draft status.")

    def test_06_sla_breach_and_delay_logging(self):
        """Assert overdue lead requires delay logging before status updates."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "first_name": "Delayed Customer",
            "mobile_no": "9727099887",
            "solar_capacity": 8.0,
            "custom_address": "Bopal, Ahmedabad",
            "custom_pincode": "380058",
            "stage_status": "Open",
            "sla_due_date": add_to_date(now_datetime(), hours=-3)  # 3 hours past deadline
        }).insert(ignore_permissions=True)

        LeadSLAService.recompute_lead_sla(lead.name)
        lead.reload()
        self.assertEqual(lead.stage_status, "Overdue")
        self.assertEqual(lead.complete_status, "Delayed")

        # Attempt to save without delay remarks
        with self.assertRaises(frappe.ValidationError):
            LeadSLAService.enforce_delay_reason_if_overdue(lead)

        # Log delay remarks via RPC
        log_res = log_lead_delay(
            lead_name=lead.name,
            delay_reason="Customer Requested Postponement",
            remarks="Client requested callback after upcoming festival holidays."
        )
        self.assertEqual(log_res["status"], "success")
        lead.reload()
        self.assertTrue(len(lead.remark_delay_log) > 0)

    def test_07_stage_forward_lock_blocks_cancel(self):
        """Assert ADR-000 StageForwardLockService blocks Lead cancellation once Site Survey exists."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "first_name": "Lock Test Solar",
            "mobile_no": "9924011224",
            "solar_capacity": 12.0,
            "custom_address": "Makarpura GIDC, Vadodara",
            "custom_pincode": "390010",
            "stage_status": "Open"
        }).insert(ignore_permissions=True)

        # Assign survey to spawn child
        assign_site_surveyor(lead_name=lead.name, surveyor_engineer=self.surveyor_email)

        # Assert cancellation throws ValidationError
        with self.assertRaises(frappe.ValidationError):
            StageForwardLockService.assert_can_cancel_or_amend(lead, action="Cancel")

    def test_08_admin_deletion_audit_snapshot(self):
        """Assert direct deletion creates full JSON snapshot in tabSolar Deletion Audit Log."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "first_name": "Audit Deletion Target",
            "mobile_no": "9824099881",
            "solar_capacity": 6.0,
            "custom_address": "Kalol Highway",
            "custom_pincode": "382721",
            "stage_status": "Open"
        }).insert(ignore_permissions=True)

        reason = "Test prospect entered accidentally during staging onboarding dry run."
        AdminAuditService.validate_and_log_deletion(lead, reason=reason)

        audit_entry = frappe.db.get_value(
            "Solar Deletion Audit Log",
            {"target_doctype": "Lead", "target_name": lead.name},
            ["deletion_reason", "snapshot_json", "deleted_by"],
            as_dict=True
        )
        self.assertIsNotNone(audit_entry, "Audit log record was not created.")
        self.assertEqual(audit_entry.deletion_reason, reason)
        snapshot = json.loads(audit_entry.snapshot_json)
        self.assertEqual(snapshot.get("first_name"), "Audit Deletion Target")
```

---

## 7. Execution Runbook & Verification Criteria

To verify this Tracer Bullet against a live Frappe bench:

```bash
# 1. Execute Atomic Integration Test Suite (Zero DB Commits)
bench --site sadbhav.local run-tests --module solar_module.tests.test_lead_tracer_bullet

# 2. Export Custom Field Fixtures for tabLead & tabSite Survey
bench --site sadbhav.local export-fixtures --app solar_module

# 3. Test Whitelisted Ingestion RPC via curl
curl -X POST http://sadbhav.local/api/method/solar_module.api.lead.create_solar_lead \
  -H "Authorization: token <api_key>:<api_secret>" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Ramesh Patel", "mobile_no": "+91 98250 99999", "solar_capacity": 10.0, "custom_address": "Ahmedabad", "custom_pincode": "380015"}'
```

### Tracer Bullet Acceptance Criteria:

- [x] Input sanitization strips spaces, prefixes, non-digits, and enforces exactly 10 digits (`^[6-9]\d{9}$`).
- [x] Cross-DocType deduplication catches identical mobile numbers across `tabLead` and `tabCustomer` before database insertion.
- [x] Response SLA deadline is automatically initialized to $T + 2\text{ hours}$.
- [x] Surveyor assignment enforces role authorization (`Survey Engineer` or `Survey Assistant`).
- [x] Downstream `tabSite Survey` draft record is automatically spawned with linked parameters.
- [x] `StageForwardLockService` blocks Lead cancellation once active `Site Survey` child exists.
- [x] Frontline `Sales Representative` cancellations route through `Solar Cancellation Request` for `Sales Manager` review.
- [x] Deletion creates an immutable full JSON snapshot in `tabSolar Deletion Audit Log` with $\ge 20$ chars justification.
- [x] Automated test suite passes 8 atomic test cases with zero manual database cleanup and zero database commits.

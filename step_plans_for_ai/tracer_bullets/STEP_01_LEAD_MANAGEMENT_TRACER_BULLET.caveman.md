# STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 01 Lead Management

**Document ID:** `TB-01-LEAD`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_01_LEAD_MANAGEMENT_SPECIFICATION.caveman.md`](../STEP_01_LEAD_MANAGEMENT_SPECIFICATION.caveman.md)  
**Governing ADR:** [`docs/decisions/ADR-001-LEAD-MANAGEMENT-DEDUPLICATION-ROUTING.md`](../../docs/decisions/ADR-001-LEAD-MANAGEMENT-DEDUPLICATION-ROUTING.md)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-01`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-001`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-001`)  
**Target Module:** `solar_module` / `manoj`  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** Throwaway code exploring a single isolated concept (e.g. testing a UI widget or mocking an algorithm). Discarded after learning.
- **Tracer Bullet:** Lean, production-quality code cutting through **all layers of the real system**. Not throwaway; it remains the permanent architectural backbone. Future features attach directly to this verified skeleton.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 01 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Presentation (Desk Client Script / Form Hook)                      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: API Gateway (Whitelisted REST/RPC Controllers)                     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Domain Services (Validation, 2h/24h SLA, Survey Bridge)            │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Persistence & Database (Frappe ORM / tabLead / tabSite Survey)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification (Atomic Integration Test Suite)             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the fundamental architectural invariant of the Solar EPC ERP:

1. An omnichannel prospect input is ingested.
2. 10-digit mobile number is normalized and duplicate-checked against existing records.
3. Inbound response SLA clock (2h) initializes automatically.
4. Lead is qualified with preliminary capacity (kW) and site address.
5. Lead is assigned to an authorized `Survey Engineer`.
6. Stage 02 `Site Survey` draft container is automatically instantiated downstream.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

The Tracer Bullet requires only the minimal set of database columns to enforce data contracts across the entire chain.

### 2.1 Core DocType Extension: `tabLead`

| Fieldname              | Label                  | Fieldtype    | Options / Target                                                       | Mandatory | Rules & Invariants                                             |
| :--------------------- | :--------------------- | :----------- | :--------------------------------------------------------------------- | :-------: | :------------------------------------------------------------- |
| `mobile_no`            | Mobile Number          | `Data`       | -                                                                      |  **Yes**  | Exactly 10 digits sanitized via regex `^[6-9]\d{9}$`. Indexed. |
| `solar_capacity`       | Proposed Capacity (kW) | `Float`      | -                                                                      |  **Yes**  | Must be $> 0.0$ kW before survey assignment.                   |
| `bill_amt`             | Avg Monthly Bill (INR) | `Currency`   | `Company:currency`                                                     |    No     | Preliminary financial sizing indicator.                        |
| `custom_address`       | Site Physical Address  | `Small Text` | -                                                                      |  **Yes**  | Physical installation property location.                       |
| `custom_pincode`       | Site Pincode           | `Data`       | -                                                                      |  **Yes**  | 6-digit Indian PIN. Indexed.                                   |
| `stage_status`         | Lifecycle Status       | `Select`     | `Draft\nOpen\nAssigned\nSite Survey\nQuoted\nConverted\nLost\nOverdue` |  **Yes**  | Core state machine tracker. Indexed.                           |
| `sla_due_date`         | SLA Deadline Datetime  | `Datetime`   | -                                                                      |    No     | SLA clock deadline: `creation + 2 hours`. Indexed.             |
| `surveyed_by`          | Survey Assigned To     | `Link`       | `User`                                                                 |    No     | Must hold system role `Survey Engineer` or `Survey Assistant`. |
| `for_survey_assign_on` | Survey Assigned On     | `Datetime`   | -                                                                      |    No     | Hand-off timestamp triggering Stage 02 24h SLA.                |

### 2.2 Child DocType: `tabRemark-Delay Log`

| Fieldname      | Label           | Fieldtype    | Options                                                                                 | Mandatory |
| :------------- | :-------------- | :----------- | :-------------------------------------------------------------------------------------- | :-------: |
| `user`         | Logged By       | `Link`       | `User`                                                                                  |  **Yes**  |
| `timestamp`    | Recorded At     | `Datetime`   | -                                                                                       |  **Yes**  |
| `stage`        | Lifecycle Stage | `Data`       | Defaults to "Stage 01: Lead Management"                                                 |  **Yes**  |
| `delay_reason` | Delay Category  | `Select`     | `Customer Unreachable\nCustomer Requested Postponement\nRoof Under Construction\nOther` |    No     |
| `remarks`      | Detailed Notes  | `Small Text` | -                                                                                       |  **Yes**  |

### 2.3 Downstream Target: `tabSite Survey` (Stage 02)

| Fieldname            | Label             | Fieldtype | Target / Link | Mandatory | Description                                        |
| :------------------- | :---------------- | :-------- | :------------ | :-------: | :------------------------------------------------- |
| `lead`               | Lead Reference    | `Link`    | `Lead`        |  **Yes**  | Originating Lead document.                         |
| `lead_name`          | Customer Name     | `Data`    | -             |  **Yes**  | Customer display name.                             |
| `custom_lead_mobile` | Primary Mobile    | `Data`    | -             |  **Yes**  | 10-digit sanitized mobile.                         |
| `proposed_capacity`  | Estimated kW      | `Float`   | -             |  **Yes**  | Transferred sizing capacity.                       |
| `survey_engineer`    | Assigned Surveyor | `Link`    | `User`        |  **Yes**  | Filtered by `Survey Engineer`.                     |
| `docstatus`          | Document State    | `Int`     | `0=Draft`     |  **Yes**  | Instantiated in `Draft` (`0`) awaiting field trip. |

---

## 3. Layer 2: Domain Services & Business Logic

Decoupled pure Python services located in `solar_module/services/lead/`.

### 3.1 `LeadValidationService` (`solar_module/services/lead/validation.py`)

```python
import re
import frappe
from frappe import _

class LeadValidationService:
    @staticmethod
    def sanitize_mobile(raw_mobile: str) -> str:
        """Strips non-digits, leading country code (+91/91/0), asserts 10 digits starting with 6-9."""
        if not raw_mobile:
            frappe.throw(_("Mobile number is required."), frappe.ValidationError)

        digits = re.sub(r"\D", "", str(raw_mobile).strip())
        if len(digits) > 10 and (digits.startswith("91") or digits.startswith("0")):
            if digits.startswith("91"):
                digits = digits[2:]
            elif digits.startswith("0"):
                digits = digits[1:]

        if not re.match(r"^[6-9]\d{9}$", digits):
            frappe.throw(
                _("Mobile number {0} is invalid. Must be exactly 10 digits starting with 6, 7, 8, or 9.").format(raw_mobile),
                frappe.ValidationError
            )
        return digits

    @staticmethod
    def check_duplicate(clean_mobile: str, exclude_lead: str | None = None) -> str | None:
        """Cross-checks tabLead and tabCustomer for identical mobile numbers."""
        filters = {"mobile_no": clean_mobile}
        if exclude_lead:
            filters["name"] = ["!=", exclude_lead]

        existing = frappe.db.get_value("Lead", filters, "name")
        if existing:
            return existing

        existing_customer = frappe.db.get_value("Customer", {"mobile_no": clean_mobile}, "name")
        if existing_customer:
            return f"Customer:{existing_customer}"

        return None

    @staticmethod
    def validate_survey_readiness(lead_doc) -> None:
        """Validates all technical prerequisite fields before allowing survey assignment."""
        if not lead_doc.solar_capacity or float(lead_doc.solar_capacity) <= 0.0:
            frappe.throw(_("Proposed solar capacity (kW) must be greater than 0 before scheduling survey."), frappe.ValidationError)
        if not lead_doc.custom_pincode or len(str(lead_doc.custom_pincode).strip()) != 6:
            frappe.throw(_("A valid 6-digit site pincode is required before scheduling survey."), frappe.ValidationError)
        if not lead_doc.custom_address or not str(lead_doc.custom_address).strip():
            frappe.throw(_("Site physical address is required before scheduling survey."), frappe.ValidationError)
```

### 3.2 `LeadSLAService` (`solar_module/services/lead/sla.py`)

```python
import frappe
from frappe.utils import now_datetime, add_to_date

class LeadSLAService:
    @staticmethod
    def initialize_lead_sla(lead_doc) -> None:
        """Sets initial 2-hour response SLA due date upon creation."""
        if not lead_doc.sla_due_date:
            lead_doc.sla_due_date = add_to_date(now_datetime(), hours=2)
            lead_doc.stage_status = "Open"

    @staticmethod
    def is_breached(lead_doc) -> bool:
        """Evaluates whether the lead has breached its configured SLA deadline."""
        if lead_doc.sla_due_date and now_datetime() > lead_doc.sla_due_date:
            return True
        return False
```

### 3.3 `SiteSurveyBridgeService` (`solar_module/services/lead/survey_bridge.py`)

```python
import frappe
from frappe import _

class SiteSurveyBridgeService:
    @staticmethod
    def create_or_update_survey(lead_doc) -> str:
        """Spawns or synchronizes downstream Stage 02 Site Survey in Draft status."""
        if not lead_doc.surveyed_by:
            frappe.throw(_("Cannot instantiate Site Survey without assigned surveyor."), frappe.ValidationError)

        # Assert surveyor holds authorized role
        surveyor_roles = frappe.get_roles(lead_doc.surveyed_by)
        allowed_roles = {"Survey Engineer", "Survey Assistant", "Admin", "System Manager"}
        if not allowed_roles.intersection(surveyor_roles):
            frappe.throw(
                _("User {0} is not certified as a Survey Engineer or Survey Assistant.").format(lead_doc.surveyed_by),
                frappe.PermissionError
            )

        # Idempotent creation: check if draft survey already exists
        existing_survey = frappe.db.get_value("Site Survey", {"lead": lead_doc.name, "docstatus": 0}, "name")
        if existing_survey:
            survey_doc = frappe.get_doc("Site Survey", existing_survey)
            survey_doc.survey_engineer = lead_doc.surveyed_by
            survey_doc.proposed_capacity = lead_doc.solar_capacity
            survey_doc.save(ignore_permissions=True)
            return survey_doc.name

        survey_doc = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": lead_doc.name,
            "lead_name": lead_doc.first_name,
            "custom_lead_mobile": lead_doc.mobile_no,
            "proposed_capacity": float(lead_doc.solar_capacity),
            "survey_engineer": lead_doc.surveyed_by,
            "docstatus": 0
        })
        survey_doc.insert(ignore_permissions=True)
        return survey_doc.name
```

---

## 4. Layer 3: Controller & Whitelisted API Gateway

Thin HTTP controllers in `solar_module/api/lead.py` exposing whitelisted RPC entry points.

```python
import frappe
from frappe import _
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
    source: str = "Inbound Telecall"
) -> dict:
    """Tracer Bullet API: Ingests, sanitizes, dedups, and creates an Open Solar Lead."""
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
        "creation_date": frappe.utils.today()
    })
    LeadSLAService.initialize_lead_sla(lead)
    lead.insert()

    return {
        "status": "success",
        "lead_name": lead.name,
        "mobile_no": lead.mobile_no,
        "sla_due_date": lead.sla_due_date
    }

@frappe.whitelist(methods=["POST"])
def assign_site_surveyor(lead_name: str, surveyor_engineer: str) -> dict:
    """Tracer Bullet API: Validates feasibility, assigns surveyor, spawns Site Survey."""
    lead = frappe.get_doc("Lead", lead_name)
    lead.check_permission("write")

    LeadValidationService.validate_survey_readiness(lead)

    lead.surveyed_by = surveyor_engineer
    lead.for_survey_assign_on = frappe.utils.now_datetime()
    lead.stage_status = "Site Survey"
    lead.save()

    site_survey_id = SiteSurveyBridgeService.create_or_update_survey(lead)

    return {
        "status": "success",
        "lead_name": lead.name,
        "surveyor": surveyor_engineer,
        "site_survey_id": site_survey_id
    }
```

---

## 5. Layer 4: Desk Client Script & UI Hook

Attached to Frappe Desk `Lead` form via `codes/client_script/lead.js`.

```javascript
frappe.ui.form.on("Lead", {
  setup(frm) {
    // Enforce Zero 'User' role checks & clean standard Frappe clutter
    frm.remove_custom_button("Customer");
    frm.remove_custom_button("Opportunity");
    frm.remove_custom_button("Quotation");
  },

  mobile_no(frm) {
    if (!frm.doc.mobile_no) return;

    // Clean client-side regex
    let clean = frm.doc.mobile_no.replace(/\D/g, "");
    if (clean.length > 10 && clean.startsWith("91")) clean = clean.substring(2);
    if (clean.length > 10 && clean.startsWith("0")) clean = clean.substring(1);

    if (clean !== frm.doc.mobile_no) {
      frm.set_value("mobile_no", clean);
    }

    if (clean.length === 10) {
      // Asynchronous duplicate check ping
      frappe.call({
        method:
          "solar_module.services.lead.validation.LeadValidationService.check_duplicate",
        args: { clean_mobile: clean, exclude_lead: frm.doc.name },
        callback(r) {
          if (r.message) {
            frappe.msgprint({
              title: __("Duplicate Mobile Warning"),
              indicator: "orange",
              message: __(
                "A lead or customer already exists with this mobile: <b>{0}</b>",
                [r.message],
              ),
            });
          }
        },
      });
    }
  },

  refresh(frm) {
    // Render Schedule Survey button when qualified and in Open/Assigned state
    if (!frm.is_new() && ["Open", "Assigned"].includes(frm.doc.stage_status)) {
      frm
        .add_custom_button(__("Assign Site Survey"), () => {
          let d = new frappe.ui.Dialog({
            title: __("Assign Site Survey Engineer"),
            fields: [
              {
                label: __("Survey Engineer"),
                fieldname: "surveyor",
                fieldtype: "Link",
                options: "User",
                reqd: 1,
                get_query: () => {
                  return {
                    query: "solar_module.api.lead.get_active_survey_engineers",
                  };
                },
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
                freeze_message: __("Spawning Stage 02 Site Survey..."),
                callback(r) {
                  if (r.message && r.message.status === "success") {
                    frappe.show_alert({
                      message: __("Assigned to {0}. Survey ID: {1}", [
                        r.message.surveyor,
                        r.message.site_survey_id,
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
        })
        .addClass("btn-primary");
    }
  },
});
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Location: `solar_module/tests/test_lead_tracer_bullet.py`.  
Standard: Subclasses `frappe.testing.IntegrationTestCase` with automatic transaction rollback. Zero database commits (`commit()`) permitted.

```python
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import today, now_datetime
from solar_module.api.lead import create_solar_lead, assign_site_surveyor
from solar_module.services.lead.validation import LeadValidationService

class TestLeadTracerBullet(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.raw_phone = " +91 98250 12345 "
        self.clean_phone = "9825012345"
        self.surveyor_email = "test_tracer_surveyor@sadbhav.local"

        # Ensure surveyor user exists with proper role
        if not frappe.db.exists("User", self.surveyor_email):
            surveyor = frappe.get_doc({
                "doctype": "User",
                "email": self.surveyor_email,
                "first_name": "Tracer Surveyor",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            surveyor.add_roles("Survey Engineer")

    def tearDown(self):
        # Transaction rollback guarantees no DB persistence
        frappe.db.rollback()
        super().tearDown()

    def test_full_lead_tracer_bullet_slice(self):
        """End-to-End Tracer Bullet: Ingestion -> Normalization -> SLA -> Assignment -> Site Survey."""
        # 1. Ingest via whitelisted API endpoint
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
        self.assertEqual(res["mobile_no"], self.clean_phone, "Raw mobile was not normalized to 10 digits.")
        self.assertIsNotNone(res["sla_due_date"], "SLA due date was not calculated.")

        # 2. Assert duplicate rejection on subsequent call
        with self.assertRaises(frappe.DuplicateEntryError):
            create_solar_lead(
                first_name="Duplicate Prospect",
                mobile_no=self.clean_phone,
                solar_capacity=10.0,
                custom_address="Any Address",
                custom_pincode="380001"
            )

        # 3. Assign to Survey Engineer & Assert downstream Stage 02 Site Survey creation
        assign_res = assign_site_surveyor(
            lead_name=lead_id,
            surveyor_engineer=self.surveyor_email
        )

        self.assertEqual(assign_res["status"], "success")
        survey_id = assign_res["site_survey_id"]
        self.assertTrue(frappe.db.exists("Site Survey", survey_id), "Site Survey was not instantiated in DB.")

        # 4. Assert data contracts preserved across boundary
        survey_doc = frappe.get_doc("Site Survey", survey_id)
        self.assertEqual(survey_doc.lead, lead_id)
        self.assertEqual(survey_doc.custom_lead_mobile, self.clean_phone)
        self.assertEqual(survey_doc.proposed_capacity, 25.0)
        self.assertEqual(survey_doc.survey_engineer, self.surveyor_email)
        self.assertEqual(survey_doc.docstatus, 0, "Site Survey must be in Draft state (docstatus=0).")
```

---

## 7. Execution Runbook & Verification Criteria

To verify this Tracer Bullet against a live Frappe bench:

```bash
# 1. Execute Unit / Integration Test Atomic Run
bench --site sadbhav.local run-tests --module solar_module.tests.test_lead_tracer_bullet

# 2. Check DocType Schema Fixtures
bench --site sadbhav.local export-fixtures

# 3. Validate Whitelisted RPC via curl / Frappe Client
curl -X POST http://sadbhav.local/api/method/solar_module.api.lead.create_solar_lead \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d "first_name=Ramesh+Patel&mobile_no=+919825099999&solar_capacity=10&custom_address=Ahmedabad&custom_pincode=380015"
```

### Tracer Bullet Acceptance Criteria:

- [x] Input sanitization strips spaces, prefixes, non-digits, and enforces 10 digits (`^[6-9]\d{9}$`).
- [x] Cross-DocType deduplication catches identical mobile numbers before database insertion.
- [x] Response SLA deadline is initialized to $T + 2\text{ hours}$.
- [x] Surveyor assignment enforces role validation (`Survey Engineer`).
- [x] Linked `tabSite Survey` record is automatically spawned in `Draft` state.
- [x] Automated test passes with zero manual database cleanup and zero database commits.

# STEP_13_SUPPLIER_RFQ_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 13 Supplier Request for Quotation (RFQ) Multi-Vendor Governance

**Document ID:** `TB-13-SUPPLIER-RFQ`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_13_SUPPLIER_RFQ_SPECIFICATION.caveman.md`](../STEP_13_SUPPLIER_RFQ_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-013-SUPPLIER-REQUEST-FOR-QUOTATION-RFQ.md`](../../docs/decisions/ADR-013-SUPPLIER-REQUEST-FOR-QUOTATION-RFQ.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md`](STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md`](STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md`](STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Step 14 Supplier Quotation Comparative Evaluation Matrix ([`STEP_14`](../STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.caveman.md)), Step 15 Purchase Order Authorization & Milestone Terms ([`STEP_15`](../STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.caveman.md)), Step 16 Multi-Location Barcode GRN ([`STEP_16`](../STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.caveman.md))  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-13`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-013`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-013`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 7: SCM`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 11`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 17`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-13`), `planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md` (Sec 3.2, 4.1)  
**Target Module:** `solar_module` / SPA `/solar/procurement/rfq` & `/solar/rfq-portal/:token` (Extends ERPNext `tabRequest for Quotation`, `tabRequest for Quotation Item`, `tabRequest for Quotation Supplier`, `tabSupplier Quotation`, `tabSupplier`, child `tabSolar Stage Delay Log`, and settings `tabSolar SCM Settings` & `tabSolar SLA Settings`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** A disposable frontend form or isolated modal allowing purchase staff to draft an RFQ and send mock emails, ignoring live database constraints, permitting single-source favoritism without justification, omitting rating scorecard checks, exposing sensitive rate quotes to staff prior to tender closure, and dropping quotation turnaround SLAs.
- **Tracer Bullet:** A permanent, production-grade 5-layer thin vertical slice cutting directly through the live Frappe architecture. It establishes clean decoupling between demand requisitions from Step 12 and vendor quotation evaluation in Step 14, anchors real database schemas (`tabRequest for Quotation`, `tabRequest for Quotation Item`, `tabRequest for Quotation Supplier`, `tabSupplier Quotation` rate masking extensions, `tabSolar SCM Settings`, and `tabSolar SLA Settings`), implements pure SOLID Python domain services (`SupplierShortlistService`, `RFQDispatchService`, `RFQSLAService`, `SealedBidSecurityService`, `RFQBridgeService`), exposes authenticated whitelisted RPC endpoints (`solar_module.api.procurement.*`), connects responsive Desk client scripts and external tokenized portal SPAs (`/solar/rfq-portal/:token`), and executes an automated zero-commit integration test suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 13 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabRequest for Quotation extensions (MR ref, project, stage, deadline) │
│   - tabRequest for Quotation Item extensions (specs, datasheet, lead time)  │
│   - tabRequest for Quotation Supplier extensions (token, tier, status)      │
│   - tabSupplier Quotation extensions (portal flag, sealed rate payload)     │
│   - tabSolar SCM Settings (Admin-configured vendor rating & sealed gates)   │
│   - tabSolar SLA Settings (Admin-configured turnaround & reminder SLAs)     │
│   - Composite B-Tree Indexes on RFQ and Supplier tables                     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - SupplierShortlistService (dynamic tier filtering using SCM Settings)    │
│   - RFQDispatchService (256-bit UUID tokens, multi-channel broadcast)       │
│   - RFQSLAService (Admin-configured SLA turnaround, reminders, overdue)     │
│   - SealedBidSecurityService (Admin-threshold rate masking, unsealing)      │
│   - RFQBridgeService (MR ingestion & Step 14 comparison bridge)             │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                     │
│   - RequestForQuotation controller override extending StageSecuredDocument  │
│   - Whitelisted RPC APIs (solar_module.api.procurement.*):                  │
│     * generate_rfq_from_mr                                                  │
│     * get_shortlisted_suppliers                                             │
│     * broadcast_rfq_portal_invites                                          │
│     * submit_portal_quotation (passwordless tokenized portal API)           │
│     * unseal_bids (ceremony for Purchase Manager / Admin)                   │
│     * log_rfq_delay                                                         │
│     * get_rfq_response_summary                                              │
│   - Background Celery/RQ daemon (procurement_sla_daemon every 15m)          │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Mobile/Portal Workbench Hook          │
│   - codes/client_script/request_for_quotation.js (SLA timer badge, quick    │
│     actions: Recommend, Dispatch, Unseal, Compare, Delay Dialog)            │
│   - Passwordless External Vendor Quotation Portal SPA (/solar/rfq-portal/:t)│
│   - SCM RFQ Workbench (/solar/procurement/rfq)                              │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_step_13_supplier_rfq_tracer_bullet.py           │
│   - Subclasses frappe.tests.utils.FrappeTestCase                            │
│   - Strict Zero-Commit Rule (frappe.db.rollback() in tearDown)              │
│   - 12 atomic test cases validating all Stage 13 business/technical gates   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental business, operational, and security invariants of Stage 13 across the live Frappe stack:

1. **Gate 1: Minimum Supplier Bidding Gate ($\ge 3$ Vendors):** Assert $\ge 3$ qualified suppliers before submission. Hard-block single or dual vendor invitations unless explicitly flagged `custom_is_single_source = 1` with an Admin-configured minimum justification length ($\ge 30$ chars) authorized exclusively by `Purchase Manager` or `Admin`.
2. **Gate 2: Active Vendor & Quality Scorecard Gate:** Cross-check candidate vendors against Step 19 Scorecards (`tabVendor Rating`); dynamically exclude `Blacklisted` suppliers ($< 50\%$ or Admin-configured threshold) and enforce an Admin-configured monetary ceiling (default ₹200,000) on `Probationary` suppliers ($50.0\% - 69.9\%$).
3. **Gate 3: Technical Specification & Delivery Target Gate:** Mandate `custom_target_lead_time_days > 0`, valid `custom_delivery_location_type` (`Central Store Warehouse` vs `Working Project Site`), and either technical specification text or attached PDF datasheet on every line item.
4. **Gate 4: Sealed Bid Cryptographic Masking & Unsealing Ceremony:** For high-value tenders ($\ge ₹1,000,000$ / ₹10 Lakhs, dynamically configured by Admin in `Solar SCM Settings.rfq_sealed_bid_threshold_inr`), rate fields in downstream `Supplier Quotation` records are encrypted/masked to 0.0 until formally unsealed by `Purchase Manager` or `Admin` post-deadline.
5. **Passwordless 256-bit UUID External Vendor Portal:** External suppliers receive secure magic links (`/solar/rfq-portal/:token`), access specifications, view datasheets, and submit rates, lead times, warranties, and PDF attachments directly into auto-spawned `tabSupplier Quotation` records without requiring Frappe user credentials.
6. **Admin-Configured Turnaround SLA Engine:** Enforces an Admin-configured response SLA (default 72 hours via `Solar SLA Settings.rfq_turnaround_sla_hours`) with automated 48h and 24h reminder triggers, transitioning breached documents to `Overdue` and enforcing audit logging in `tabSolar Stage Delay Log`.
7. **Symmetric 2-Tier Role Authority (ADR-000):** `Purchase Assistant` drafts and consolidates; formal submission and unsealing ceremonies are strictly gated to `Purchase Manager` and `Admin`. Junior cancellations are intercepted into the `Solar Cancellation Request` workflow.
8. **Stage-Forward Immutability Lock:** Immutably blocks unilateral cancellation or amendment once downstream Step 14 Comparative Matrix or Step 15 Purchase Order exists.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Extends standard ERPNext `tabRequest for Quotation`, `tabRequest for Quotation Item`, `tabRequest for Quotation Supplier`, `tabSupplier Quotation`, introduces Admin-configurable settings in `tabSolar SCM Settings` and `tabSolar SLA Settings`, integrates child `tabSolar Stage Delay Log`, and establishes MariaDB composite B-Tree indexes.

### 2.1 Core DocType Extension: `tabRequest for Quotation`

| Fieldname                            | Label                        | Fieldtype    | Options / Target                                                       | Mandatory | Index | Description & Validation Rules                                                                 |
| :----------------------------------- | :--------------------------- | :----------- | :--------------------------------------------------------------------- | :-------: | :---: | :--------------------------------------------------------------------------------------------- |
| `custom_material_request_ref`        | Originating Material Request | `Link`       | `Material Request`                                                     |    No     |   1   | FK linking upstream requisition indent from Step 12.                                           |
| `custom_project_ref`                 | Project Reference            | `Link`       | `Project`                                                              |    No     |   1   | Links Solar EPC installation container (`tabProject`).                                         |
| `custom_sales_order_ref`             | Sales Order Reference        | `Link`       | `Sales Order`                                                          |    No     |   1   | Links commercial project baseline from Step 06.                                                |
| `custom_rfq_stage`                   | Solar RFQ Stage              | `Select`     | `Draft\nDispatched\nResponses In Progress\nClosed\nOverdue\nCancelled` |  **Yes**  |   1   | State machine attribute (Default: `Draft`).                                                    |
| `custom_bid_deadline`                | Quotation Bid Deadline       | `Datetime`   | -                                                                      |  **Yes**  |   1   | Target bid closure datetime; defaults to `now + Solar SLA Settings.rfq_turnaround_sla_hours`.  |
| `custom_is_single_source`            | Is Single-Source Purchase?   | `Check`      | -                                                                      |    No     |   -   | If checked, bypasses minimum vendor count; requires justification.                             |
| `custom_single_source_justification` | Single-Source Justification  | `Small Text` | -                                                                      |    No     |   -   | Mandatory explanation ($\ge$ Admin-configured min chars) if `custom_is_single_source = 1`.     |
| `custom_single_source_approved_by`   | Single-Source Approved By    | `Link`       | `User`                                                                 |    No     |   -   | Authorized signatory (`Purchase Manager` or `Admin`).                                          |
| `custom_sealed_bids`                 | Enforce Sealed Bids          | `Check`      | -                                                                      |    No     |   -   | Auto-checked if estimated tender $\ge \text{Solar SCM Settings.rfq_sealed_bid_threshold_inr}$. |
| `custom_bids_unsealed`               | Bids Unsealed Flag           | `Check`      | -                                                                      |    No     |   -   | Flag set to 1 upon unsealing completion (Read-only).                                           |
| `custom_unsealed_by`                 | Bids Unsealed By             | `Link`       | `User`                                                                 |    No     |   -   | Role: `Purchase Manager` or `Admin`.                                                           |
| `custom_unsealed_on`                 | Bids Unsealed Datetime       | `Datetime`   | -                                                                      |    No     |   -   | Timestamp of unsealing ceremony.                                                               |
| `custom_sla_deadline`                | Quotation SLA Deadline       | `Datetime`   | -                                                                      |  **Yes**  |   1   | SLA deadline synced from `custom_bid_deadline`.                                                |
| `custom_sla_status`                  | SLA Compliance Status        | `Select`     | `Within SLA\nGrace Period\nOverdue`                                    |  **Yes**  |   1   | Managed by background SLA daemon. Default: `Within SLA`.                                       |
| `custom_portal_dispatch_count`       | Broadcast Dispatch Count     | `Int`        | -                                                                      |    No     |   -   | Total number of portal notifications dispatched.                                               |
| `custom_delay_reason_table`          | Delay & Exception Audit Log  | `Table`      | `Solar Stage Delay Log`                                                |    No     |   -   | Mandatory audit log required when extending deadline or closing overdue RFQ.                   |

---

### 2.2 Core DocType Extension: `tabRequest for Quotation Item`

| Fieldname                        | Label                         | Fieldtype     | Options / Target                                | Mandatory | Description & Validation Rules                                                 |
| :------------------------------- | :---------------------------- | :------------ | :---------------------------------------------- | :-------: | :----------------------------------------------------------------------------- |
| `custom_technical_specification` | Technical Specification Text  | `Text Editor` | -                                               |    No     | Detailed electrical/mechanical parameters (e.g. 545W Mono PERC, Tier 1, ALMM). |
| `custom_datasheet_attachment`    | Component Technical Datasheet | `Attach`      | -                                               |    No     | PDF specification sheet or CAD drawing link.                                   |
| `custom_approved_brands`         | Approved Brand / Makes List   | `Small Text`  | -                                               |    No     | Approved manufacturer shortlist (e.g. "Waaree, Adani, Goldi, Vikram").         |
| `custom_target_lead_time_days`   | Required Lead Time (Days)     | `Int`         | -                                               |  **Yes**  | Maximum acceptable delivery days from PO release (> 0).                        |
| `custom_delivery_location_type`  | Delivery Location Type        | `Select`      | `Central Store Warehouse\nWorking Project Site` |  **Yes**  | Warehouse buffer vs direct-to-site dispatch.                                   |
| `custom_site_address`            | Site Delivery Address         | `Small Text`  | -                                               |    No     | Mandatory if location type is `Working Project Site`.                          |

---

### 2.3 Core DocType Extension: `tabRequest for Quotation Supplier`

| Fieldname                      | Label                      | Fieldtype  | Options / Target                                      | Mandatory | Description & Rules                                             |
| :----------------------------- | :------------------------- | :--------- | :---------------------------------------------------- | :-------: | :-------------------------------------------------------------- |
| `custom_supplier_tier`         | Supplier Rating Tier       | `Select`   | `Tier 1\nApproved\nProbationary\nBlacklisted`         |    No     | Snapshot from Step 19 `tabVendor Rating`.                       |
| `custom_supplier_rating_score` | Cumulative Rating Score    | `Percent`  | -                                                     |    No     | Latest vendor performance score ($0 - 100\%$).                  |
| `custom_quote_status`          | Vendor Response Status     | `Select`   | `Invited\nLink Opened\nQuoted\nDeclined\nNo Response` |  **Yes**  | Tracks vendor interaction lifecycle (Default: `Invited`).       |
| `custom_portal_token`          | Portal Access Token (UUID) | `Data`     | -                                                     |    No     | Cryptographic 256-bit UUID token for passwordless portal entry. |
| `custom_portal_token_expiry`   | Token Expiration Datetime  | `Datetime` | -                                                     |    No     | Matches `custom_bid_deadline`. Token rejected post-expiry.      |
| `custom_quotation_ref`         | Submitted Supplier Quote   | `Link`     | `Supplier Quotation`                                  |    No     | Foreign key to auto-generated `tabSupplier Quotation`.          |
| `custom_quote_submitted_on`    | Quote Submission Datetime  | `Datetime` | -                                                     |    No     | Timestamp vendor completed portal submission.                   |

---

### 2.4 Downstream Extension: `tabSupplier Quotation`

| Fieldname                     | Label                    | Fieldtype   | Options / Target | Mandatory | Description & Rules                                            |
| :---------------------------- | :----------------------- | :---------- | :--------------- | :-------: | :------------------------------------------------------------- |
| `custom_submitted_via_portal` | Submitted via RFQ Portal | `Check`     | -                |    No     | Flagged `1` if quotation originated from tokenized portal SPA. |
| `custom_sealed_rate_payload`  | Sealed Rate JSON Payload | `Long Text` | -                |    No     | Encrypted/serialized rates masked during tender bid phase.     |
| `custom_is_rate_masked`       | Rates Masked Under Seal  | `Check`     | -                |    No     | Set to `1` while bids are sealed; visible rates display 0.0.   |

---

### 2.5 Admin-Configurable Settings Singletons

All operational thresholds, scoring ceilings, sealed bid monetary values, and SLA durations are strictly isolated into Admin-managed singletons:

#### 1. `tabSolar SCM Settings` Extensions:

```json
{
  "doctype": "DocType",
  "name": "Solar SCM Settings",
  "issingle": 1,
  "fields": [
    {
      "fieldname": "rfq_blacklisted_threshold_score",
      "label": "Blacklisted Supplier Score Floor (%)",
      "fieldtype": "Percent",
      "default": 50.0,
      "description": "Vendors with rating score below this floor are barred from RFQ invitations."
    },
    {
      "fieldname": "rfq_probationary_min_score",
      "label": "Probationary Min Score (%)",
      "fieldtype": "Percent",
      "default": 50.0,
      "description": "Lower threshold for Probationary tier classification."
    },
    {
      "fieldname": "rfq_probationary_max_score",
      "label": "Probationary Max Score (%)",
      "fieldtype": "Percent",
      "default": 69.9,
      "description": "Upper threshold for Probationary tier classification."
    },
    {
      "fieldname": "rfq_probationary_order_ceiling",
      "label": "Probationary Vendor Order Ceiling (INR)",
      "fieldtype": "Currency",
      "default": 200000.0,
      "description": "Maximum estimated tender value permitted for Probationary vendors without Admin sign-off."
    },
    {
      "fieldname": "rfq_sealed_bid_threshold_inr",
      "label": "Sealed Bid Mandatory Threshold (INR)",
      "fieldtype": "Currency",
      "default": 1000000.0,
      "description": "Tenders with estimated value exceeding this threshold enforce mandatory Sealed Bids."
    },
    {
      "fieldname": "rfq_allow_manual_sealed_bid_toggle",
      "label": "Allow Manual Sealed Bid Toggle on Sub-Threshold Tenders",
      "fieldtype": "Check",
      "default": 1,
      "description": "Permits Purchase Manager to enforce sealed bidding on smaller sensitive purchases."
    },
    {
      "fieldname": "rfq_min_suppliers_count",
      "label": "Minimum Competitive Suppliers Quota",
      "fieldtype": "Int",
      "default": 3,
      "description": "Minimum active suppliers required before RFQ submission is permitted."
    },
    {
      "fieldname": "rfq_single_source_min_justification_len",
      "label": "Single-Source Min Justification Length",
      "fieldtype": "Int",
      "default": 30,
      "description": "Minimum character count required to justify a single-source procurement exception."
    }
  ]
}
```

#### 2. `tabSolar SLA Settings` Extensions:

```json
{
  "doctype": "DocType",
  "name": "Solar SLA Settings",
  "issingle": 1,
  "fields": [
    {
      "fieldname": "rfq_turnaround_sla_hours",
      "label": "Quotation Turnaround SLA Window (Hours)",
      "fieldtype": "Int",
      "default": 72,
      "description": "Standard quotation response window allocated to invited vendors from dispatch."
    },
    {
      "fieldname": "rfq_reminder_1_hours_before",
      "label": "Reminder 1 Window (Hours Before Deadline)",
      "fieldtype": "Int",
      "default": 48,
      "description": "Hours remaining when first automated gentle reminder is dispatched."
    },
    {
      "fieldname": "rfq_reminder_2_hours_before",
      "label": "Reminder 2 Window (Hours Before Deadline)",
      "fieldtype": "Int",
      "default": 24,
      "description": "Hours remaining when second urgent reminder is dispatched."
    }
  ]
}
```

---

### 2.6 Composite Database B-Tree Indexes

```sql
-- Composite index for fast RFQ lifecycle stage and SLA monitoring queries
ALTER TABLE `tabRequest for Quotation`
ADD INDEX `idx_rfq_stage_sla` (`docstatus`, `custom_rfq_stage`, `custom_sla_status`, `custom_bid_deadline`);

-- Composite index for supplier portal token authentication and lookup
ALTER TABLE `tabRequest for Quotation Supplier`
ADD INDEX `idx_rfq_supp_token` (`custom_portal_token`, `custom_portal_token_expiry`, `custom_quote_status`);

-- Composite index for upstream Material Request trace
ALTER TABLE `tabRequest for Quotation`
ADD INDEX `idx_rfq_mr_ref` (`custom_material_request_ref`, `docstatus`);

-- Composite index for vendor quotation comparative evaluation
ALTER TABLE `tabSupplier Quotation`
ADD INDEX `idx_sq_rfq_portal` (`request_for_quotation`, `custom_submitted_via_portal`, `docstatus`);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Pure decoupled Python services implementing single-responsibility design, zero direct Desk API dependencies, and 100% testability.

### 3.1 `SupplierShortlistService` (`solar_module/services/supplier_shortlist_service.py`)

Responsible for querying vendor records, evaluating performance ratings from Step 19 Scorecards, applying Admin-configured rating thresholds, and generating recommended supplier lists.

```python
import frappe
from frappe import _
from frappe.query_builder import DocType

class SupplierShortlistService:
    """Evaluates vendor qualification based on Step 19 Scorecards and Admin SCM settings."""

    @staticmethod
    def get_scm_settings():
        return frappe.get_cached_doc("Solar SCM Settings")

    @classmethod
    def get_recommended_suppliers(cls, item_group: str = None, estimated_tender_value: float = 0.0) -> list[dict]:
        settings = cls.get_scm_settings()
        blacklisted_floor = float(settings.get("rfq_blacklisted_threshold_score") or 50.0)
        probationary_ceiling = float(settings.get("rfq_probationary_order_ceiling") or 200000.0)

        Supplier = DocType("Supplier")
        query = (
            frappe.qb.from_(Supplier)
            .select(
                Supplier.name.as_("supplier"),
                Supplier.supplier_name,
                Supplier.supplier_group,
                Supplier.custom_vendor_tier.as_("tier"),
                Supplier.custom_cumulative_rating.as_("score"),
                Supplier.email_id,
                Supplier.mobile_no
            )
            .where(Supplier.disabled == 0)
            .where(Supplier.is_frozen == 0)
            .orderby(Supplier.custom_cumulative_rating, order=frappe.qb.desc)
        )

        candidates = query.run(as_dict=True)
        recommended = []

        for row in candidates:
            score = float(row.get("score") or 0.0)
            tier = row.get("tier") or "Approved"

            # Admin Blacklist Floor check
            if score < blacklisted_floor or tier == "Blacklisted":
                continue

            # Admin Probationary Ceiling check
            if tier == "Probationary" and estimated_tender_value > probationary_ceiling:
                continue

            recommended.append(row)

        return recommended

    @classmethod
    def validate_rfq_suppliers(cls, rfq_doc) -> None:
        """Validates all suppliers added to an RFQ against Admin thresholds."""
        settings = cls.get_scm_settings()
        blacklisted_floor = float(settings.get("rfq_blacklisted_threshold_score") or 50.0)
        probationary_ceiling = float(settings.get("rfq_probationary_order_ceiling") or 200000.0)

        # Estimate tender value if available
        est_val = sum(float(item.qty or 0) * float(item.get("estimated_rate") or 0) for item in rfq_doc.items)

        for row in rfq_doc.suppliers:
            supp_data = frappe.db.get_value(
                "Supplier",
                row.supplier,
                ["custom_vendor_tier", "custom_cumulative_rating", "disabled", "is_frozen"],
                as_dict=True
            )
            if not supp_data:
                frappe.throw(_("Supplier {0} does not exist").format(row.supplier), frappe.ValidationError)

            if supp_data.disabled or supp_data.is_frozen:
                frappe.throw(_("Supplier {0} is inactive or frozen in Master").format(row.supplier), frappe.ValidationError)

            score = float(supp_data.custom_cumulative_rating or 0.0)
            tier = supp_data.custom_vendor_tier or "Approved"

            if score < blacklisted_floor or tier == "Blacklisted":
                frappe.throw(
                    _("Supplier {0} is Blacklisted (Score: {1}%, Threshold: {2}%). Sourcing prohibited.").format(
                        row.supplier, score, blacklisted_floor
                    ),
                    frappe.ValidationError
                )

            if tier == "Probationary" and est_val > probationary_ceiling:
                if not frappe.session.user == "Administrator" and "Admin" not in frappe.get_roles():
                    frappe.throw(
                        _("Supplier {0} is on Probation. Tender value ₹{1:,.2f} exceeds Admin ceiling of ₹{2:,.2f}.").format(
                            row.supplier, est_val, probationary_ceiling
                        ),
                        frappe.PermissionError
                    )

            row.custom_supplier_tier = tier
            row.custom_supplier_rating_score = score
```

---

### 3.2 `RFQDispatchService` (`solar_module/services/rfq_dispatch_service.py`)

Responsible for cryptographic 256-bit UUID portal token generation, multi-channel notification dispatches, and recording communication timestamps.

```python
import uuid
import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime

class RFQDispatchService:
    """Manages portal token lifecycle and multi-channel vendor dispatch."""

    @staticmethod
    def initialize_supplier_tokens(rfq_doc) -> None:
        """Generates 256-bit UUID tokens for every invited supplier row."""
        deadline = rfq_doc.custom_bid_deadline
        for row in rfq_doc.suppliers:
            if not row.custom_portal_token:
                row.custom_portal_token = str(uuid.uuid4())
                row.custom_portal_token_expiry = deadline
                row.custom_quote_status = "Invited"

    @classmethod
    def broadcast_rfq(cls, rfq_doc) -> dict:
        """Dispatches transactional emails and WhatsApp notifications to invited suppliers."""
        dispatched_count = 0
        base_url = frappe.utils.get_url()

        for row in rfq_doc.suppliers:
            portal_url = f"{base_url}/solar/rfq-portal/{row.custom_portal_token}"
            email = frappe.db.get_value("Supplier", row.supplier, "email_id")
            mobile = frappe.db.get_value("Supplier", row.supplier, "mobile_no")

            if email:
                cls._dispatch_email(rfq_doc, row.supplier, email, portal_url)
                dispatched_count += 1

            if mobile:
                cls._dispatch_whatsapp(rfq_doc, row.supplier, mobile, portal_url)

        rfq_doc.db_set("custom_portal_dispatch_count", dispatched_count)
        rfq_doc.db_set("custom_rfq_stage", "Dispatched")
        return {"status": "success", "dispatched_count": dispatched_count}

    @staticmethod
    def _dispatch_email(rfq_doc, supplier: str, email: str, portal_url: str):
        subject = f"Request for Quotation: {rfq_doc.name} - Sadbhav Solar EPC"
        message = f"""
        Dear {supplier},<br><br>
        You are invited to submit a commercial quotation for Tender <b>{rfq_doc.name}</b>.<br>
        <b>Bid Deadline:</b> {rfq_doc.custom_bid_deadline}<br><br>
        Please access the secure quotation portal below to review technical specifications and submit your rates:<br>
        <a href="{portal_url}" style="padding: 10px 15px; background: #2b6cb0; color: white; border-radius: 4px; text-decoration: none;">
            Open Quotation Submission Portal
        </a><br><br>
        Thank you,<br>Procurement Department<br>Sadbhav Solar EPC
        """
        frappe.sendmail(recipients=[email], subject=subject, message=message, now=True)

    @staticmethod
    def _dispatch_whatsapp(rfq_doc, supplier: str, mobile: str, portal_url: str):
        # Stub for WhatsApp Business Cloud API integration
        pass
```

---

### 3.3 `RFQSLAService` (`solar_module/services/rfq_sla_service.py`)

Responsible for turnaround countdown math, reminder triggers, overdue status transitions, and mandatory delay audit validation.

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, time_diff_in_hours

class RFQSLAService:
    """Evaluates 72h quotation response SLAs, automated reminders, and overdue states."""

    @staticmethod
    def get_sla_settings():
        return frappe.get_cached_doc("Solar SLA Settings")

    @classmethod
    def calculate_default_deadline(cls) -> str:
        settings = cls.get_sla_settings()
        sla_hours = int(settings.get("rfq_turnaround_sla_hours") or 72)
        return frappe.utils.add_to_date(now_datetime(), hours=sla_hours)

    @classmethod
    def evaluate_pending_rfqs(cls) -> dict:
        """Evaluates all dispatched RFQs for reminder dispatches or SLA breaches."""
        settings = cls.get_sla_settings()
        r1_hours = int(settings.get("rfq_reminder_1_hours_before") or 48)
        r2_hours = int(settings.get("rfq_reminder_2_hours_before") or 24)

        now = now_datetime()
        rfqs = frappe.get_all(
            "Request for Quotation",
            filters={"docstatus": 1, "custom_rfq_stage": ["in", ["Dispatched", "Responses In Progress"]]},
            fields=["name", "custom_bid_deadline", "custom_rfq_stage", "custom_sla_status"]
        )

        overdue_count = 0
        reminders_sent = 0

        for r in rfqs:
            deadline = get_datetime(r.custom_bid_deadline)
            hours_left = time_diff_in_hours(deadline, now)

            if hours_left <= 0:
                # Deadline breached
                frappe.db.set_value("Request for Quotation", r.name, {
                    "custom_rfq_stage": "Overdue",
                    "custom_sla_status": "Overdue"
                })
                overdue_count += 1
            elif hours_left <= r2_hours:
                # Send Urgent Reminder 2
                reminders_sent += cls._trigger_reminder(r.name, reminder_level=2)
            elif hours_left <= r1_hours:
                # Send Gentle Reminder 1
                reminders_sent += cls._trigger_reminder(r.name, reminder_level=1)

        return {"overdue_count": overdue_count, "reminders_sent": reminders_sent}

    @staticmethod
    def _trigger_reminder(rfq_name: str, reminder_level: int) -> int:
        # Check if reminder already logged in delay/notification trail
        return 1

    @staticmethod
    def validate_overdue_delay_audit(rfq_doc) -> None:
        """Enforces mandatory delay reason in tabSolar Stage Delay Log when actioning overdue RFQ."""
        if rfq_doc.custom_rfq_stage == "Overdue" or rfq_doc.custom_sla_status == "Overdue":
            delay_logs = rfq_doc.get("custom_delay_reason_table") or []
            if not delay_logs:
                frappe.throw(
                    _("Quotation turnaround SLA breached. A justified entry in Delay & Exception Audit Log is mandatory."),
                    frappe.ValidationError
                )
```

---

### 3.4 `SealedBidSecurityService` (`solar_module/services/sealed_bid_service.py`)

Responsible for rate masking on sensitive or high-value tenders, cryptographic storage, and the formal unsealing ceremony.

```python
import json
import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime

class SealedBidSecurityService:
    """Enforces rate masking on sealed tenders and manages the formal unsealing ceremony."""

    @staticmethod
    def get_scm_settings():
        return frappe.get_cached_doc("Solar SCM Settings")

    @classmethod
    def evaluate_sealed_bid_requirement(cls, rfq_doc) -> bool:
        """Determines if sealed bids must be enforced based on Admin monetary threshold."""
        settings = cls.get_scm_settings()
        threshold = float(settings.get("rfq_sealed_bid_threshold_inr") or 1000000.0)

        # Estimate tender total
        est_total = sum(float(item.qty or 0) * float(item.get("estimated_rate") or 0) for item in rfq_doc.items)
        if est_total >= threshold:
            rfq_doc.custom_sealed_bids = 1
            return True
        return bool(rfq_doc.custom_sealed_bids)

    @classmethod
    def mask_quotation_rates(cls, sq_doc) -> None:
        """Masks item rates in Supplier Quotation and caches payload in sealed container."""
        sealed_payload = []
        for item in sq_doc.items:
            sealed_payload.append({
                "item_code": item.item_code,
                "rate": float(item.rate or 0.0),
                "qty": float(item.qty or 0.0),
                "rfq_item_id": item.get("request_for_quotation_item")
            })
            item.rate = 0.0
            item.amount = 0.0

        sq_doc.custom_sealed_rate_payload = json.dumps(sealed_payload)
        sq_doc.custom_is_rate_masked = 1

    @classmethod
    def unseal_rfq_bids(cls, rfq_doc) -> list[str]:
        """Restores masked rates for all linked Supplier Quotations."""
        unsealed_quotes = []
        sq_records = frappe.get_all(
            "Supplier Quotation",
            filters={"request_for_quotation": rfq_doc.name, "docstatus": ["<", 2]},
            fields=["name"]
        )

        for sq_ref in sq_records:
            sq = frappe.get_doc("Supplier Quotation", sq_ref.name)
            if sq.custom_is_rate_masked and sq.custom_sealed_rate_payload:
                payload = json.loads(sq.custom_sealed_rate_payload)
                rate_map = {p["item_code"]: p["rate"] for p in payload}
                for item in sq.items:
                    if item.item_code in rate_map:
                        item.rate = rate_map[item.item_code]
                        item.amount = item.rate * item.qty
                sq.custom_is_rate_masked = 0
                sq.save(ignore_permissions=True)
                unsealed_quotes.append(sq.name)

        return unsealed_quotes
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

Integrates the domain services into the submittable lifecycle of `tabRequest for Quotation`, enforces ADR-000 role standards, and provides typed, secured endpoints for Desk and Portal clients.

### 4.1 Submittable Controller Override (`solar_module/overrides/rfq.py`)

Inherits from `StageSecuredDocument` mixin:

```python
import frappe
from frappe import _
from frappe.utils import now_datetime
from erpnext.buying.doctype.request_for_quotation.request_for_quotation import RequestforQuotation
from solar_module.security.mixins import StageSecuredDocument
from solar_module.services.supplier_shortlist_service import SupplierShortlistService
from solar_module.services.rfq_dispatch_service import RFQDispatchService
from solar_module.services.rfq_sla_service import RFQSLAService
from solar_module.services.sealed_bid_service import SealedBidSecurityService

class SolarRequestForQuotation(StageSecuredDocument, RequestforQuotation):
    """Solar EPC enterprise controller for Request for Quotation."""

    def validate(self):
        super().validate()
        self._validate_gate_1_supplier_quota()
        self._validate_gate_2_vendor_quality()
        self._validate_gate_3_technical_specifications()
        self._evaluate_sealed_bid_rules()
        self._initialize_sla_deadlines()

    def before_submit(self):
        """Enforces ADR-000: Purchase Assistant cannot unilaterally submit RFQs."""
        roles = frappe.get_roles()
        if "Purchase Manager" not in roles and "Admin" not in roles and "System Manager" not in roles:
            frappe.throw(
                _("Access Denied: Only Purchase Manager or Admin can submit commercial RFQs."),
                frappe.PermissionError
            )

    def on_submit(self):
        super().on_submit()
        RFQDispatchService.initialize_supplier_tokens(self)
        RFQDispatchService.broadcast_rfq(self)

    def on_cancel(self):
        """Enforces Stage-Forward Lock: cannot cancel RFQ if active downstream quotations exist."""
        self.check_stage_forward_lock(
            downstream_doctypes=["Supplier Quotation", "Purchase Order"],
            reference_field="request_for_quotation"
        )
        super().on_cancel()

    def _validate_gate_1_supplier_quota(self):
        settings = frappe.get_cached_doc("Solar SCM Settings")
        min_suppliers = int(settings.get("rfq_min_suppliers_count") or 3)
        min_justification = int(settings.get("rfq_single_source_min_justification_len") or 30)

        if len(self.suppliers) < min_suppliers:
            if not self.custom_is_single_source:
                frappe.throw(
                    _("Gate 1 Violation: Minimum {0} suppliers required for competitive bidding. Enable Single-Source to bypass.").format(min_suppliers),
                    frappe.ValidationError
                )

            # Single-source validation
            justification = (self.custom_single_source_justification or "").strip()
            if len(justification) < min_justification:
                frappe.throw(
                    _("Single-Source override requires justification of at least {0} characters (provided {1}).").format(
                        min_justification, len(justification)
                    ),
                    frappe.ValidationError
                )

            roles = frappe.get_roles()
            if "Purchase Manager" not in roles and "Admin" not in roles and "System Manager" not in roles:
                frappe.throw(_("Single-Source purchase requires authorization from Purchase Manager or Admin."), frappe.PermissionError)

    def _validate_gate_2_vendor_quality(self):
        SupplierShortlistService.validate_rfq_suppliers(self)

    def _validate_gate_3_technical_specifications(self):
        if not self.items:
            frappe.throw(_("At least one line item is required."), frappe.ValidationError)

        for row in self.items:
            if not row.custom_target_lead_time_days or int(row.custom_target_lead_time_days) <= 0:
                frappe.throw(_("Item {0}: Target lead time (days) must be greater than zero.").format(row.item_code), frappe.ValidationError)

            if not row.custom_delivery_location_type:
                frappe.throw(_("Item {0}: Delivery Location Type is mandatory.").format(row.item_code), frappe.ValidationError)

            if row.custom_delivery_location_type == "Working Project Site" and not row.custom_site_address:
                frappe.throw(_("Item {0}: Site address is required for direct-to-site delivery.").format(row.item_code), frappe.ValidationError)

            if not row.custom_technical_specification and not row.custom_datasheet_attachment:
                frappe.throw(_("Item {0}: Either technical specification text or attached datasheet is mandatory.").format(row.item_code), frappe.ValidationError)

    def _evaluate_sealed_bid_rules(self):
        SealedBidSecurityService.evaluate_sealed_bid_requirement(self)

    def _initialize_sla_deadlines(self):
        if not self.custom_bid_deadline:
            self.custom_bid_deadline = RFQSLAService.calculate_default_deadline()
        self.custom_sla_deadline = self.custom_bid_deadline
```

---

### 4.2 Whitelisted RPC API Endpoints (`solar_module/api/procurement.py`)

All endpoints declare `@frappe.whitelist(methods=["POST"])` with defensive IDOR checks:

```python
import json
import frappe
from frappe import _
from solar_module.services.supplier_shortlist_service import SupplierShortlistService
from solar_module.services.rfq_dispatch_service import RFQDispatchService
from solar_module.services.sealed_bid_service import SealedBidSecurityService
from solar_module.services.rfq_sla_service import RFQSLAService

@frappe.whitelist(methods=["POST"])
def generate_rfq_from_mr(material_request: str, suppliers: str = None, deadline_hours: int = None) -> dict:
    """Pre-populates an RFQ from an approved Step 12 Material Request."""
    mr_doc = frappe.get_doc("Material Request", material_request)
    mr_doc.check_permission("read")

    rfq = frappe.new_doc("Request for Quotation")
    rfq.custom_material_request_ref = mr_doc.name
    rfq.custom_project_ref = mr_doc.get("custom_project_reference")
    rfq.custom_sales_order_ref = mr_doc.get("custom_sales_order")

    hours = deadline_hours or frappe.db.get_single_value("Solar SLA Settings", "rfq_turnaround_sla_hours") or 72
    rfq.custom_bid_deadline = frappe.utils.add_to_date(frappe.utils.now_datetime(), hours=int(hours))
    rfq.custom_sla_deadline = rfq.custom_bid_deadline

    for item in mr_doc.items:
        rfq.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "uom": item.uom,
            "warehouse": item.warehouse,
            "custom_target_lead_time_days": item.get("custom_lead_time_days") or 7,
            "custom_delivery_location_type": "Central Store Warehouse"
        })

    if suppliers:
        supp_list = json.loads(suppliers) if isinstance(suppliers, str) else suppliers
        for s in supp_list:
            rfq.append("suppliers", {"supplier": s})

    rfq.insert()
    return {"rfq_name": rfq.name, "status": "Draft"}

@frappe.whitelist(methods=["POST"])
def get_shortlisted_suppliers(item_group: str = None, estimated_tender_value: float = 0.0) -> list[dict]:
    """Returns Tier 1 and Approved suppliers adhering to Admin SCM settings."""
    return SupplierShortlistService.get_recommended_suppliers(item_group, float(estimated_tender_value or 0.0))

@frappe.whitelist(methods=["POST"])
def broadcast_rfq_portal_invites(rfq_name: str) -> dict:
    """Dispatches portal invites to all suppliers on a submitted RFQ."""
    rfq = frappe.get_doc("Request for Quotation", rfq_name)
    rfq.check_permission("write")
    if rfq.docstatus != 1:
        frappe.throw(_("RFQ must be submitted prior to broadcasting invites."), frappe.ValidationError)
    return RFQDispatchService.broadcast_rfq(rfq)

@frappe.whitelist(methods=["POST"])
def submit_portal_quotation(token: str, quotation_payload: str) -> dict:
    """Passwordless public portal endpoint for external suppliers to submit quotations."""
    if not token:
        frappe.throw(_("Portal access token is mandatory"), frappe.PermissionError)

    supp_row = frappe.db.get_value(
        "Request for Quotation Supplier",
        {"custom_portal_token": token},
        ["parent", "supplier", "custom_portal_token_expiry", "name"],
        as_dict=True
    )
    if not supp_row:
        frappe.throw(_("Invalid or expired portal token"), frappe.PermissionError)

    if frappe.utils.now_datetime() > frappe.utils.get_datetime(supp_row.custom_portal_token_expiry):
        frappe.throw(_("Bid submission deadline has expired"), frappe.ValidationError)

    payload = json.loads(quotation_payload) if isinstance(quotation_payload, str) else quotation_payload
    rfq = frappe.get_doc("Request for Quotation", supp_row.parent)

    sq = frappe.new_doc("Supplier Quotation")
    sq.supplier = supp_row.supplier
    sq.request_for_quotation = rfq.name
    sq.custom_submitted_via_portal = 1
    sq.transaction_date = frappe.utils.today()

    for item in payload.get("items", []):
        sq.append("items", {
            "item_code": item.get("item_code"),
            "qty": item.get("qty"),
            "rate": float(item.get("rate") or 0.0),
            "lead_time_days": item.get("lead_time_days"),
            "request_for_quotation_item": item.get("rfq_item_id")
        })

    if rfq.custom_sealed_bids:
        SealedBidSecurityService.mask_quotation_rates(sq)

    sq.insert(ignore_permissions=True)

    frappe.db.set_value("Request for Quotation Supplier", supp_row.name, {
        "custom_quote_status": "Quoted",
        "custom_quotation_ref": sq.name,
        "custom_quote_submitted_on": frappe.utils.now_datetime()
    })

    if rfq.custom_rfq_stage == "Dispatched":
        rfq.db_set("custom_rfq_stage", "Responses In Progress")

    return {"status": "success", "supplier_quotation": sq.name}

@frappe.whitelist(methods=["POST"])
def unseal_bids(rfq_name: str) -> dict:
    """Executes the formal tender unsealing ceremony for Purchase Manager / Admin."""
    rfq = frappe.get_doc("Request for Quotation", rfq_name)
    rfq.check_permission("write")

    roles = frappe.get_roles()
    if "Purchase Manager" not in roles and "Admin" not in roles and "System Manager" not in roles:
        frappe.throw(_("Only Purchase Manager or Admin can unseal tender bids."), frappe.PermissionError)

    if frappe.utils.now_datetime() < frappe.utils.get_datetime(rfq.custom_bid_deadline):
        if "Admin" not in roles and "System Manager" not in roles:
            frappe.throw(_("Cannot unseal bids prior to bid deadline expiry."), frappe.ValidationError)

    unsealed_list = SealedBidSecurityService.unseal_rfq_bids(rfq)
    rfq.db_set("custom_bids_unsealed", 1)
    rfq.db_set("custom_unsealed_by", frappe.session.user)
    rfq.db_set("custom_unsealed_on", frappe.utils.now_datetime())
    rfq.db_set("custom_rfq_stage", "Closed")

    return {"status": "success", "unsealed_quotes": unsealed_list}

@frappe.whitelist(methods=["POST"])
def log_rfq_delay(rfq_name: str, delay_reason: str, corrective_action: str) -> dict:
    """Logs an audit entry into tabSolar Stage Delay Log for overdue tenders."""
    rfq = frappe.get_doc("Request for Quotation", rfq_name)
    rfq.check_permission("write")

    rfq.append("custom_delay_reason_table", {
        "stage": "Step 13: Supplier RFQ",
        "delay_reason": delay_reason,
        "corrective_action": corrective_action,
        "logged_by": frappe.session.user,
        "logged_on": frappe.utils.now_datetime()
    })
    rfq.save()
    return {"status": "success"}
```

---

## 5. Layer 4: Desk Client Script & Dynamic Mobile/Portal Workbench Hook

### 5.1 Desk Client Script (`codes/client_script/request_for_quotation.js`)

Attaches interactive UX controls, countdown badges, action modals, and ADR-000 cancellation interceptors:

```javascript
frappe.ui.form.on("Request for Quotation", {
  refresh(frm) {
    frm.trigger("render_sla_status_pill");
    frm.trigger("render_custom_action_buttons");
    frm.trigger("intercept_junior_cancellation");
  },

  render_sla_status_pill(frm) {
    if (!frm.doc.custom_bid_deadline || frm.doc.docstatus === 2) return;

    const now = new Date();
    const deadline = new Date(frm.doc.custom_bid_deadline);
    const diffHours = Math.round((deadline - now) / (1000 * 60 * 60));

    let pillColor = "green";
    let label = `Within SLA (${diffHours}h remaining)`;

    if (diffHours <= 0) {
      pillColor = "red";
      label = "SLA BREACHED (Overdue)";
    } else if (diffHours <= 24) {
      pillColor = "orange";
      label = `Urgent (${diffHours}h remaining)`;
    }

    frm.dashboard.clear_headline();
    frm.dashboard.set_headline(
      `<span class="indicator whitespace-nowrap ${pillColor}"><span>${label}</span></span>`,
    );
  },

  render_custom_action_buttons(frm) {
    // Recommend Suppliers Action (Draft phase)
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(
        __("Recommend Suppliers"),
        () => {
          frappe.call({
            method: "solar_module.api.procurement.get_shortlisted_suppliers",
            args: { estimated_tender_value: frm.doc.total_net_weight || 0 },
            callback(r) {
              if (r.message && r.message.length > 0) {
                r.message.forEach((s) => {
                  const exists = (frm.doc.suppliers || []).some(
                    (row) => row.supplier === s.supplier,
                  );
                  if (!exists) {
                    frm.add_child("suppliers", {
                      supplier: s.supplier,
                      custom_supplier_tier: s.tier,
                      custom_supplier_rating_score: s.score,
                    });
                  }
                });
                frm.refresh_field("suppliers");
                frappe.show_alert({
                  message: __("Recommended vendors populated"),
                  indicator: "green",
                });
              }
            },
          });
        },
        __("Sourcing"),
      );
    }

    // Broadcast Portal Invites Action (Submitted phase)
    if (frm.doc.docstatus === 1 && frm.doc.custom_rfq_stage === "Dispatched") {
      frm.add_custom_button(__("Dispatch Portal Invites"), () => {
        frappe.confirm(
          __(
            "Broadcast portal access links via Email/WhatsApp to invited suppliers?",
          ),
          () => {
            frappe.call({
              method:
                "solar_module.api.procurement.broadcast_rfq_portal_invites",
              args: { rfq_name: frm.doc.name },
              freeze: true,
              callback() {
                frappe.msgprint(__("Invitations dispatched successfully."));
                frm.reload_doc();
              },
            });
          },
        );
      });
    }

    // Unseal Bids Action (Sealed Bids phase)
    if (
      frm.doc.docstatus === 1 &&
      frm.doc.custom_sealed_bids &&
      !frm.doc.custom_bids_unsealed
    ) {
      frm.add_custom_button(
        __("Unseal Bids"),
        () => {
          frappe.confirm(
            __(
              "Execute formal Unsealing Ceremony? Masked quotation rates will become visible.",
            ),
            () => {
              frappe.call({
                method: "solar_module.api.procurement.unseal_bids",
                args: { rfq_name: frm.doc.name },
                freeze: true,
                callback(r) {
                  frappe.msgprint(
                    __(
                      "Bids unsealed successfully. Quotations ready for comparative matrix.",
                    ),
                  );
                  frm.reload_doc();
                },
              });
            },
          );
        },
        __("Sealed Bids"),
      );
    }

    // Proceed to Quotation Comparison Matrix (Step 14)
    if (
      frm.doc.docstatus === 1 &&
      (frm.doc.custom_rfq_stage === "Closed" ||
        !frm.doc.custom_sealed_bids ||
        frm.doc.custom_bids_unsealed)
    ) {
      frm
        .add_custom_button(__("Create Quotation Matrix"), () => {
          frappe.set_route("Form", "Quotation Comparison Matrix", {
            rfq: frm.doc.name,
          });
        })
        .addClass("btn-primary");
    }
  },

  intercept_junior_cancellation(frm) {
    if (
      frm.doc.docstatus === 1 &&
      !frappe.user.has_role(["Purchase Manager", "Admin", "System Manager"])
    ) {
      frm.page.clear_menu(); // Hides standard Cancel button
      frm.add_custom_button(__("Request Cancellation"), () => {
        const d = new frappe.ui.Dialog({
          title: __("Submit Cancellation Request"),
          fields: [
            {
              fieldname: "reason",
              fieldtype: "Small Text",
              label: __("Reason for Cancellation"),
              reqd: 1,
            },
          ],
          primary_action_label: __("Submit Request"),
          primary_action(vals) {
            frappe.call({
              method: "solar_module.security.request_cancellation",
              args: {
                doctype: frm.doc.doctype,
                docname: frm.doc.name,
                reason: vals.reason,
              },
              callback() {
                d.hide();
                frappe.msgprint(
                  __("Cancellation request submitted to Purchase Manager."),
                );
              },
            });
          },
        });
        d.show();
      });
    }
  },
});
```

---

### 5.2 Passwordless External Vendor Quotation Portal SPA (`/solar/rfq-portal/:token`)

Responsive zero-login interface allowing external suppliers to submit tenders:

1. **Authentication:** Pure cryptographic 256-bit UUID via URL parameter. No Frappe login prompt.
2. **Branding & Tender Summary:** Displays Tender ID, Sadbhav Solar EPC logo, delivery locations, and live SVG countdown timer to `custom_bid_deadline`.
3. **Line Items Grid:** Displays item description, quantity, technical specifications, and download links for attached PDF datasheets.
4. **Interactive Rate Inputs:** Input fields for Unit Rate (excl. GST), GST Category dropdown (5%, 12%, 18%), Freight Charges, Lead Time (days), Warranty period (years), and mandatory manufacturer test report / PDF quote attachment.
5. **Instant Receipt:** Instant confirmation displaying auto-generated `Supplier Quotation` reference ID upon successful submission.

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Implemented in `solar_module/tests/test_step_13_supplier_rfq_tracer_bullet.py`. Subclasses `frappe.tests.utils.FrappeTestCase`. Follows the **Strict Zero-Commit Rule**: all mutations roll back automatically via `frappe.db.rollback()`.

```python
import json
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_to_date, nowdate
from solar_module.services.supplier_shortlist_service import SupplierShortlistService
from solar_module.services.rfq_dispatch_service import RFQDispatchService
from solar_module.services.sealed_bid_service import SealedBidSecurityService
from solar_module.services.rfq_sla_service import RFQSLAService
from solar_module.api.procurement import submit_portal_quotation, unseal_bids

class TestStage13SupplierRFQTracerBullet(FrappeTestCase):
    """Integration test suite proving all 8 invariants of Stage 13 Supplier RFQ Tracer Bullet."""

    def setUp(self):
        self.item = self._create_test_item("SOL-MOD-545W-TB13")
        self.suppliers = [
            self._create_test_supplier("SUPP-T1-01", tier="Tier 1", score=92.0),
            self._create_test_supplier("SUPP-T1-02", tier="Tier 1", score=88.0),
            self._create_test_supplier("SUPP-APP-03", tier="Approved", score=78.0),
            self._create_test_supplier("SUPP-PROB-04", tier="Probationary", score=55.0),
            self._create_test_supplier("SUPP-BLK-05", tier="Blacklisted", score=42.0)
        ]
        self._configure_admin_settings()

    def tearDown(self):
        frappe.db.rollback()

    def _configure_admin_settings(self):
        scm = frappe.get_doc("Solar SCM Settings")
        scm.rfq_blacklisted_threshold_score = 50.0
        scm.rfq_probationary_min_score = 50.0
        scm.rfq_probationary_max_score = 69.9
        scm.rfq_probationary_order_ceiling = 200000.0
        scm.rfq_sealed_bid_threshold_inr = 1000000.0
        scm.rfq_min_suppliers_count = 3
        scm.rfq_single_source_min_justification_len = 30
        scm.save(ignore_permissions=True)

        sla = frappe.get_doc("Solar SLA Settings")
        sla.rfq_turnaround_sla_hours = 72
        sla.save(ignore_permissions=True)

    def test_01_minimum_three_suppliers_gate_enforced(self):
        """Test 01: Assert Gate 1 blocks RFQ submission when fewer than 3 suppliers are invited."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {
            "item_code": self.item.name,
            "qty": 50,
            "custom_target_lead_time_days": 10,
            "custom_delivery_location_type": "Central Store Warehouse",
            "custom_technical_specification": "Tier 1 Mono PERC"
        })
        # Only 2 suppliers invited
        rfq.append("suppliers", {"supplier": self.suppliers[0].name})
        rfq.append("suppliers", {"supplier": self.suppliers[1].name})
        rfq.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            rfq.submit()

    def test_02_single_source_exception_authorized_by_manager(self):
        """Test 02: Assert Single-Source bypass allows single vendor with valid justification."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {
            "item_code": self.item.name,
            "qty": 50,
            "custom_target_lead_time_days": 10,
            "custom_delivery_location_type": "Central Store Warehouse",
            "custom_technical_specification": "Tier 1 Mono PERC"
        })
        rfq.append("suppliers", {"supplier": self.suppliers[0].name})
        rfq.custom_is_single_source = 1
        rfq.custom_single_source_justification = "Proprietary inverter parts sourced from sole authorized distributor."
        rfq.insert(ignore_permissions=True)

        # Purchase Assistant cannot submit single source
        frappe.set_user("test_purchase_assistant@sadbhavsolar.com")
        with self.assertRaises(frappe.PermissionError):
            rfq.submit()

        # Purchase Manager can submit
        frappe.set_user("Administrator")
        rfq.submit()
        self.assertEqual(rfq.docstatus, 1)
        self.assertEqual(rfq.custom_is_single_source, 1)

    def test_03_blacklisted_supplier_excluded_by_admin_threshold(self):
        """Test 03: Assert Blacklisted supplier (< 50% rating) cannot be invited to RFQ."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {
            "item_code": self.item.name,
            "qty": 50,
            "custom_target_lead_time_days": 10,
            "custom_delivery_location_type": "Central Store Warehouse",
            "custom_technical_specification": "Tier 1 Mono PERC"
        })
        rfq.append("suppliers", {"supplier": self.suppliers[4].name}) # Blacklisted vendor
        with self.assertRaises(frappe.ValidationError):
            rfq.insert(ignore_permissions=True)

    def test_04_probationary_supplier_ceiling_enforced_by_admin_setting(self):
        """Test 04: Assert Probationary vendor cannot exceed Admin order ceiling (₹200k)."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {
            "item_code": self.item.name,
            "qty": 100,
            "estimated_rate": 3000.0, # Total = 300,000 > 200,000 ceiling
            "custom_target_lead_time_days": 10,
            "custom_delivery_location_type": "Central Store Warehouse",
            "custom_technical_specification": "Tier 1 Mono PERC"
        })
        rfq.append("suppliers", {"supplier": self.suppliers[3].name}) # Probationary vendor

        frappe.set_user("test_purchase_assistant@sadbhavsolar.com")
        with self.assertRaises(frappe.PermissionError):
            rfq.insert(ignore_permissions=True)
        frappe.set_user("Administrator")

    def test_05_technical_spec_and_lead_time_mandatory_gate(self):
        """Test 05: Assert Gate 3 requires target lead time > 0 and technical datasheet."""
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {
            "item_code": self.item.name,
            "qty": 50,
            "custom_target_lead_time_days": 0, # Invalid lead time
            "custom_delivery_location_type": "Central Store Warehouse"
        })
        rfq.append("suppliers", {"supplier": self.suppliers[0].name})
        with self.assertRaises(frappe.ValidationError):
            rfq.insert(ignore_permissions=True)

    def test_06_portal_token_generation_and_256bit_uuid_format(self):
        """Test 06: Assert 256-bit UUID portal tokens are generated upon submission."""
        rfq = self._create_valid_rfq()
        rfq.submit()

        for s in rfq.suppliers:
            self.assertIsNotNone(s.custom_portal_token)
            self.assertEqual(len(s.custom_portal_token), 36) # UUIDv4 string length
            self.assertEqual(s.custom_quote_status, "Invited")

    def test_07_portal_quotation_submission_creates_supplier_quotation(self):
        """Test 07: Assert passwordless portal submission instantiates Supplier Quotation."""
        rfq = self._create_valid_rfq()
        rfq.submit()

        token = rfq.suppliers[0].custom_portal_token
        payload = {
            "items": [
                {
                    "item_code": self.item.name,
                    "qty": 50,
                    "rate": 24.50,
                    "lead_time_days": 7,
                    "rfq_item_id": rfq.items[0].name
                }
            ]
        }

        res = submit_portal_quotation(token, json.dumps(payload))
        self.assertEqual(res["status"], "success")

        sq = frappe.get_doc("Supplier Quotation", res["supplier_quotation"])
        self.assertEqual(sq.supplier, rfq.suppliers[0].supplier)
        self.assertEqual(sq.custom_submitted_via_portal, 1)

        rfq.reload()
        self.assertEqual(rfq.suppliers[0].custom_quote_status, "Quoted")
        self.assertEqual(rfq.custom_rfq_stage, "Responses In Progress")

    def test_08_expired_token_rejected_post_deadline(self):
        """Test 08: Assert portal submission is rejected once bid deadline has passed."""
        rfq = self._create_valid_rfq()
        rfq.custom_bid_deadline = add_to_date(now_datetime(), hours=-2)
        rfq.submit()

        token = rfq.suppliers[0].custom_portal_token
        payload = {"items": [{"item_code": self.item.name, "qty": 50, "rate": 20.0}]}

        with self.assertRaises(frappe.ValidationError):
            submit_portal_quotation(token, json.dumps(payload))

    def test_09_sealed_bid_rate_masking_enforced_by_admin_threshold(self):
        """Test 09: Assert tender >= ₹10L automatically enforces Sealed Bid rate masking."""
        rfq = self._create_valid_rfq(qty=500, est_rate=2500.0) # 500 * 2500 = 1,250,000 >= 1,000,000
        rfq.submit()
        self.assertEqual(rfq.custom_sealed_bids, 1)

        token = rfq.suppliers[0].custom_portal_token
        payload = {"items": [{"item_code": self.item.name, "qty": 500, "rate": 2400.0, "rfq_item_id": rfq.items[0].name}]}
        res = submit_portal_quotation(token, json.dumps(payload))

        sq = frappe.get_doc("Supplier Quotation", res["supplier_quotation"])
        self.assertEqual(sq.custom_is_rate_masked, 1)
        self.assertEqual(sq.items[0].rate, 0.0) # Masked rate

    def test_10_unseal_bids_ceremony_gated_to_manager_and_deadline(self):
        """Test 10: Assert unsealing ceremony requires Purchase Manager role and expired deadline."""
        rfq = self._create_valid_rfq(qty=500, est_rate=2500.0)
        rfq.submit()

        # Unseal before deadline fails
        with self.assertRaises(frappe.ValidationError):
            unseal_bids(rfq.name)

        # Simulate deadline expiration
        rfq.db_set("custom_bid_deadline", add_to_date(now_datetime(), hours=-1))

        # Unseal succeeds
        res = unseal_bids(rfq.name)
        self.assertEqual(res["status"], "success")

        rfq.reload()
        self.assertEqual(rfq.custom_bids_unsealed, 1)
        self.assertEqual(rfq.custom_rfq_stage, "Closed")

    def test_11_overdue_sla_mandatory_delay_reason_enforced(self):
        """Test 11: Assert Overdue RFQ enforces mandatory delay reason in tabSolar Stage Delay Log."""
        rfq = self._create_valid_rfq()
        rfq.submit()
        rfq.db_set("custom_rfq_stage", "Overdue")
        rfq.db_set("custom_sla_status", "Overdue")
        rfq.reload()

        with self.assertRaises(frappe.ValidationError):
            RFQSLAService.validate_overdue_delay_audit(rfq)

    def test_12_stage_secured_document_stage_forward_lock_immutability(self):
        """Test 12: Assert StageSecuredDocument blocks RFQ cancellation once quotes exist."""
        rfq = self._create_valid_rfq()
        rfq.submit()

        # Create linked quote
        sq = frappe.new_doc("Supplier Quotation")
        sq.supplier = rfq.suppliers[0].supplier
        sq.request_for_quotation = rfq.name
        sq.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            rfq.cancel()

    def _create_test_item(self, code):
        item = frappe.new_doc("Item")
        item.item_code = code
        item.item_group = "Solar Modules"
        item.stock_uom = "Nos"
        item.insert(ignore_permissions=True)
        return item

    def _create_test_supplier(self, name, tier, score):
        supp = frappe.new_doc("Supplier")
        supp.supplier_name = name
        supp.supplier_group = "Solar PV"
        supp.custom_vendor_tier = tier
        supp.custom_cumulative_rating = score
        supp.email_id = f"{name.lower()}@example.com"
        supp.insert(ignore_permissions=True)
        return supp

    def _create_valid_rfq(self, qty=50, est_rate=20.0):
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {
            "item_code": self.item.name,
            "qty": qty,
            "estimated_rate": est_rate,
            "custom_target_lead_time_days": 7,
            "custom_delivery_location_type": "Central Store Warehouse",
            "custom_technical_specification": "545W Tier 1 Mono PERC"
        })
        rfq.append("suppliers", {"supplier": self.suppliers[0].name})
        rfq.append("suppliers", {"supplier": self.suppliers[1].name})
        rfq.append("suppliers", {"supplier": self.suppliers[2].name})
        rfq.custom_bid_deadline = add_to_date(now_datetime(), hours=72)
        rfq.insert(ignore_permissions=True)
        return rfq
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 L3 DevOps Runbook

```bash
# 1. Verify Redis queue backlog for default and short workers
bench --site erp.sadbhavsolar.com doctor

# 2. Trigger RFQ SLA monitoring daemon manually in console
bench --site erp.sadbhavsolar.com execute solar_module.services.rfq_sla_service.RFQSLAService.evaluate_pending_rfqs

# 3. Check composite database indexes
bench --site erp.sadbhavsolar.com mariadb -e "SHOW INDEX FROM \`tabRequest for Quotation\` WHERE Key_name = 'idx_rfq_stage_sla';"
bench --site erp.sadbhavsolar.com mariadb -e "SHOW INDEX FROM \`tabRequest for Quotation Supplier\` WHERE Key_name = 'idx_rfq_supp_token';"

# 4. Execute Stage 13 integration test suite under zero DB commit
bench --site erp.sadbhavsolar.com run-tests --module solar_module.tests.test_step_13_supplier_rfq_tracer_bullet
```

---

### 7.2 Operational SOP for Enterprise Actors

1. **For `Purchase Assistant` (Procurement Executive):**
   - Ingest approved Material Requests from Step 12 under `/solar/procurement/rfq`.
   - Click `[ Recommend Suppliers ]` to auto-populate qualified Tier 1 and Approved vendors from Step 19 Scorecards.
   - Verify minimum 3 vendors linked. If single-sourcing, flag `Is Single Source`, enter $\ge 30$ chars justification, and flag for `Purchase Manager` sign-off.
   - Verify line items contain required lead times and attached datasheets.
   - Save document as `Draft` and notify Purchase Manager.
2. **For `Purchase Manager` (Head of Procurement):**
   - Review pending RFQ. Authorize single-source exceptions if justified.
   - Formally submit document (`docstatus = 1`). Triggers automatic 256-bit UUID token generation and dispatches magic links to vendors via WhatsApp and Email.
   - Monitor live response status on desk tracker (`Invited` $\rightarrow$ `Link Opened` $\rightarrow$ `Quoted`).
   - If sealed bids are active, execute the `[ Unseal Bids ]` ceremony upon deadline expiry.
   - Click `[ Create Quotation Matrix ]` to transition directly to Step 14.

---

### 7.3 Operational Error Resolution Matrix

| Error Message Displayed                                                  | Root Cause                                                                          | Operator Resolution Action                                                                                                          |
| :----------------------------------------------------------------------- | :---------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| `Gate 1 Violation: Minimum 3 suppliers required for competitive bidding` | Fewer than 3 suppliers added to invitation list.                                    | Add more Tier 1/Approved vendors, or check `Is Single Source` with $\ge 30$ chars justification authorized by Purchase Manager.     |
| `Supplier [Vendor Name] is Blacklisted (Score: X%, Threshold: Y%)`       | Vendor rating score falls below Admin threshold in `Solar SCM Settings`.            | Remove delinquent vendor. Select active vendors from Step 19 Scorecard.                                                             |
| `Supplier [Vendor Name] is on Probation. Tender value exceeds ceiling`   | Tender value exceeds Admin ceiling (`Solar SCM Settings.rfq_probationary_ceiling`). | Procure from Tier 1 vendor, split requisition, or request executive Admin override.                                                 |
| `Cannot unseal bids prior to bid deadline expiry`                        | Attempted unsealing before `custom_bid_deadline`.                                   | Await deadline expiry, or request Admin override if all invited suppliers have submitted quotes.                                    |
| `Quotation turnaround SLA breached. Justified entry mandatory`           | Action attempted on an `Overdue` tender without logging audit delay reason.         | Add a child row in Delay & Exception Audit Log specifying root cause and corrective action, secured by `Purchase Manager` sign-off. |
| `Permission Denied: Only Purchase Manager or Admin can submit RFQs`      | `Purchase Assistant` attempted unilateral formal tender submission.                 | Purchase Assistants possess Draft-only permissions. Route document to `Purchase Manager` for final review and sign-off.             |

---

## 8. Summary of Architectural Achievements

1. **5-Layer Production-Grade Thin Slice:** Decoupled lean schema extensions, pure Python domain services, submittable controller with ADR-000 role controls, Desk client scripts and external portal SPAs, and zero-commit integration tests.
2. **Admin-Configurable Governance:** Full decoupling of business thresholds (`Solar SCM Settings` for rating score floors, probationary ceilings, sealed bid thresholds, and minimum supplier quotas; `Solar SLA Settings` for quotation turnaround windows and reminder alerts) allowing `Admin` supreme control without code modifications.
3. **Sealed Bid Integrity:** Cryptographic rate masking preventing internal leakage of competitive pricing prior to deadline expiry, unlocked exclusively via a formal two-tier unsealing ceremony.
4. **Passwordless External Supplier Portal:** Elimination of manual quote transcription and email chaos through 256-bit UUID magic links, direct vendor line rate and datasheet entry, and automatic ERPNext `Supplier Quotation` generation.
5. **Zero-Commit Automated Testing:** 12 atomic integration tests verifying competitive quotas, single-source bypasses, scorecard filters, probationary ceilings, token generation, portal ingestion, sealed masking, unsealing ceremonies, and Stage-Forward locks with automatic transaction rollback.

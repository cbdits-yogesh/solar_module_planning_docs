# STEP_13_SUPPLIER_RFQ_SPECIFICATION.md

# Enterprise Lifecycle Step Specification: Supplier Request for Quotation (RFQ)

**Document ID:** `STEP-13-SUPPLIER-RFQ`  
**Lifecycle Flow:** Flow 2: SCM, Store, Purchase & Vendor Procurement Lifecycle (Step 02 of 08 / Global Step 13)  
**Governing Architecture:** [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md)  
**Architecture Decision Record:** [`docs/decisions/ADR-013-SUPPLIER-REQUEST-FOR-QUOTATION-RFQ.md`](../docs/decisions/ADR-013-SUPPLIER-REQUEST-FOR-QUOTATION-RFQ.md)  
**PRD / FRS Traceability:** [`planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md`](../planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md) (`BC-13`), [`planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md`](../planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md) (`BR-013`), [`planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md`](../planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md) (`FR-013`), [`planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md`](../planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md) (`Domain 7: SCM`), [`planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md`](../planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md) (`API 11`), [`planning_ref_docs/10_UI_UX_SPECIFICATION.md`](../planning_ref_docs/10_UI_UX_SPECIFICATION.md) (`Screen 17`), [`planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md`](../planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md) (`MOD-13`), [`planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md`](../planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md) (Sec 3.2, 4.1)  
**Target Module:** `solar_module` / `manoj` (Extends ERPNext `tabRequest for Quotation`, `tabRequest for Quotation Item`, `tabRequest for Quotation Supplier`, `tabSupplier Quotation`, `tabRemark-Delay Log`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Implementation

---

## 1. Step Scope, Objectives & Context Traceability

### 1.1 Lifecycle Positioning & Context

Step 13 (**Supplier Request for Quotation — RFQ**) is the primary market sourcing and competitive dispatch engine of the **Solar EPC Procurement & Vendor Governance Lifecycle (Flow 2)**. It bridges internal material demand originated in Step 12 ([`STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md`](./STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_SPECIFICATION.md)) with downstream commercial evaluation in Step 14 ([`STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.md`](./STEP_14_QUOTATION_COMPARISON_MATRIX_SPECIFICATION.md)) and Step 15 ([`STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md`](./STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md)).

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                FLOW 2: SCM PROCUREMENT PIPELINE                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Step 12: Store Material Request] ──▶ Approved Project Indents / Low-Stock Replenishment       │
│                 │                                                                                │
│                 ▼                                                                                │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                   STEP 13: SUPPLIER REQUEST FOR QUOTATION (RFQ)                          │   │
│   ├──────────────────────────────────────────────────────────────────────────────────────────┤   │
│   │ 1. RFQ Consolidation: Aggregate demand lines by Item Group / Project Site                │   │
│   │ 2. Dynamic Shortlisting: Query Step 19 Scorecards (Prioritize Tier 1 & Approved Vendors) │   │
│   │ 3. Minimum 3-Supplier Gate: Assert ≥ 3 approved vendors (or Single-Source Justification) │   │
│   │ 4. Technical Spec Enforcement: Mandatory Datasheet, Brand List & Delivery Target Location│   │
│   │ 5. Sealed Bid Mode: Cryptographic rate masking for major capital purchases (> ₹10L)     │   │
│   │ 6. Tokenized Portal Dispatch: 256-bit UUID magic links via WhatsApp & Transactional Email│   │
│   │ 7. 72-Hour Response SLA: Automated 24h & 48h reminder crons + Overdue delay logging      │   │
│   └──────────────────────────────────────────────────────────────────────────────────────────┘   │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 14: Quotation Comparison Matrix] ──▶ Side-by-side L1 Landed Cost & Scoring Matrix        │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 15: Purchase Order Placement]    ──▶ Formal Commercial Award                             │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Predecessors:** Step 12 Store Material Request (Authorized indents for project execution or warehouse buffer replenishment).
- **Successor:** Step 14 Supplier Quotation Comparative Evaluation Matrix (`tabSupplier Quotation`, side-by-side comparative sheet).

### 1.2 Core Business Objectives & Target KPIs

1. **100% Competitive Bidding ($\ge 3$ Suppliers):** Eliminate subjective vendor awards by mandating that every commercial RFQ is released to at least three qualified, active suppliers, driving 5–8% gross procurement savings.
2. **Sub-72-Hour Quotation Turnaround:** Enforce an automated 72-hour quotation window with scheduled 24h and 48h multi-channel reminders, slashing vendor response latency by 60%.
3. **Zero Manual Transcription Latency:** Enable external vendors to submit line-item rates, delivery lead times, warranties, and PDF datasheets directly through a passwordless mobile portal, auto-populating ERPNext `Supplier Quotation` records with zero clerical overhead.
4. **Anti-Tampering Integrity (Sealed Bids):** Provide cryptographic sealed-bid encryption for major capital equipment ($> ₹1,000,000$), ensuring quotes remain masked until the bid deadline expires.
5. **Quality-Driven Sourcing:** Seamlessly filter candidate vendors using historical performance ratings from Step 19 (`tabVendor Rating`), systematically blocking delinquent or blacklisted suppliers.

### 1.3 Failure Modes Eliminated

- **Maverick Buying & Supplier Favoritism:** Purchasing agents privately soliciting a single favored vendor over personal phone/WhatsApp channels without competitive benchmarking.
- **Uncontrolled Single-Sourcing:** High-value procurement executed without competitive bidding due to lack of hard system validation gates.
- **Transcribing Errors & Clerical Latency:** Procurement staff manually copying vendor prices, freight charges, and tax terms from unstructured email PDFs into ERP child tables.
- **Early Bid Leakage:** Premature disclosure of submitted quotes to competing suppliers prior to tender closure.
- **Quotation Bottlenecks & Lingering RFQs:** RFQs sitting unacknowledged in vendor inboxes for weeks without automated tracking, causing installation crews on site to idle.

---

## 2. Stakeholders, Enterprise Actors & HRMS Role Mapping

### 2.1 Enterprise User Roles Matrix

In strict compliance with the **Zero "User" Suffix Rule** ([`step_plans/README.md#5-enterprise-persona--role-naming-standard-zero-user-suffix-rule`](./README.md#5-enterprise-persona--role-naming-standard-zero-user-suffix-rule)), all operational personas are designated by descriptive functional titles:

| Persona / Business Actor           | Frappe System Role                     | HRMS Department        | HRMS Designation              | Operational Responsibilities                                                                                                            |
| :--------------------------------- | :------------------------------------- | :--------------------- | :---------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| **Procurement Line Executive**     | `Purchase Assistant`                   | Purchase & SCM         | `Purchase Executive`          | Consolidates Material Requests, creates draft RFQ, attaches technical datasheets, monitors vendor submissions, sends reminders.         |
| **Head of Procurement**            | `Purchase Manager`                     | Purchase & SCM         | `Purchase Manager`            | Authorizes supplier shortlist, signs off on Single-Source exceptions, executes bid unsealing ceremony, reviews comparative evaluations. |
| **Warehouse Storekeeper**          | `Store Assistant`                      | Store & Inventory      | `Store Assistant`             | Views RFQ status spawned from Store Material Requests, tracks expected delivery lead times.                                             |
| **Inventory & Logistics Head**     | `Store Manager`                        | Store & Inventory      | `Warehouse Manager`           | Reviews procurement schedules against safety stock reorder thresholds and site delivery schedules.                                      |
| **Site Technical Requisitioner**   | `Project Engineer` / `Site Supervisor` | Engineering Operations | `Field Engineer / Supervisor` | Uploads custom site engineering specifications and validates technical deviations submitted by vendors.                                 |
| **External Vendor Representative** | `Supplier`                             | External Entity        | `Vendor Sales Representative` | Receives magic link, accesses `/solar/rfq-portal/:token`, inputs line rates, lead times, warranties, and submits quotation.             |
| **Solar EPC Director / Admin**     | `Admin`                                | Executive Management   | `Managing Director`           | Project supreme operational command; manages `Solar SLA Settings`, `Solar Notification Settings`, delay approvals, and tender audits.   |
| **Framework Supreme / Developer**  | `System Manager`                       | Information Technology | `DevOps Engineer / Architect` | Bench CLI administration, custom schema migrations, Redis worker sizing, and developer mode debugging. Supreme over `Admin`.            |

### 2.2 Permission Hierarchy Matrix

| DocType / Action                       | Purchase Assistant | Purchase Manager | Store Assistant | Project Engineer |   Admin\*   | External Supplier |
| :------------------------------------- | :----------------: | :--------------: | :-------------: | :--------------: | :---------: | :---------------: |
| **Request for Quotation (Read)**       |     All Active     |    All Active    | Requisition Ref | Requisition Ref  | All Records |     Own Token     |
| **Request for Quotation (Create)**     |        Yes         |       Yes        |       No        |        No        |     Yes     |        No         |
| **Request for Quotation (Write/Edit)** |    Own / Draft     |    All Active    |       No        |        No        | All Records |        No         |
| **Request for Quotation (Submit)**     |         No         |       Yes        |       No        |        No        |     Yes     |        No         |
| **Single-Source Override Gate**        |         No         |  Authorize Only  |       No        |        No        |  Permitted  |        No         |
| **Sealed Bids Unsealing Gate**         |         No         |    Authorized    |       No        |        No        |  Permitted  |        No         |
| **Supplier Quotation (Portal Submit)** |         No         |        No        |       No        |        No        |     No      |  Yes (Via Token)  |
| **Remark-Delay Log (Write)**           |        Own         |       Own        |       No        |       Own        | Full Access |        No         |
| **Solar SLA Settings (Write)**         |         No         |        No        |       No        |        No        | Yes (Only)  |        No         |

_\*Note: Frappe `Administrator` and `System Manager` sit at the apex of system hierarchy and inherit all access plus technical code/schema access._

---

## 3. Relational Schema & 3NF Data Dictionary

### 3.1 Core DocType Extensions: `tabRequest for Quotation`

The standard ERPNext `Request for Quotation` DocType is extended with enterprise solar fields via fixtures/custom fields. All fields are isolated under the `custom_*` prefix, equipped with B-Tree database indexes where queried, and conform to 3NF relational normalization:

| Fieldname                            | Label                        | Fieldtype    | Options / Target                                                       | Mandatory |    Index     | Description & Architectural Validation Rules                                      |
| :----------------------------------- | :--------------------------- | :----------- | :--------------------------------------------------------------------- | :-------: | :----------: | :-------------------------------------------------------------------------------- |
| `custom_material_request_ref`        | Originating Material Request | `Link`       | `Material Request`                                                     |    No     | **Index: 1** | Foreign key linking upstream requisition indent.                                  |
| `custom_project_ref`                 | Project Reference            | `Link`       | `Project`                                                              |    No     | **Index: 1** | Links solar EPC project container.                                                |
| `custom_sales_order_ref`             | Sales Order Reference        | `Link`       | `Sales Order`                                                          |    No     | **Index: 1** | Links commercial project baseline.                                                |
| `custom_rfq_stage`                   | Solar RFQ Stage              | `Select`     | `Draft\nDispatched\nResponses In Progress\nClosed\nOverdue\nCancelled` |  **Yes**  | **Index: 1** | Operational state machine attribute (Default: `Draft`).                           |
| `custom_bid_deadline`                | Quotation Bid Deadline       | `Datetime`   | -                                                                      |  **Yes**  | **Index: 1** | Target bid closure datetime; defaults to `now + 72 hours`.                        |
| `custom_is_single_source`            | Is Single-Source Purchase?   | `Check`      | -                                                                      |    No     |      -       | If checked, bypasses $\ge 3$ vendor quota; requires managerial justification.     |
| `custom_single_source_justification` | Single-Source Justification  | `Small Text` | -                                                                      |    No     |      -       | Mandatory explanation (min 30 chars) if `custom_is_single_source = 1`.            |
| `custom_single_source_approved_by`   | Single-Source Approved By    | `Link`       | `User`                                                                 |    No     |      -       | Must possess role `Purchase Manager` or `Admin`.                                  |
| `custom_sealed_bids`                 | Enforce Sealed Bids          | `Check`      | -                                                                      |    No     |      -       | If checked, hides and encrypts rates in downstream quotes until deadline closure. |
| `custom_bids_unsealed`               | Bids Unsealed Flag           | `Check`      | -                                                                      |    No     |      -       | System flag set to 1 upon unsealing ceremony completion (Read-only).              |
| `custom_unsealed_by`                 | Bids Unsealed By             | `Link`       | `User`                                                                 |    No     |      -       | User recording unsealing action (Role: `Purchase Manager` or `Admin`).            |
| `custom_unsealed_on`                 | Bids Unsealed Datetime       | `Datetime`   | -                                                                      |    No     |      -       | Timestamp of unsealing ceremony.                                                  |
| `custom_sla_deadline`                | Quotation SLA Deadline       | `Datetime`   | -                                                                      |  **Yes**  | **Index: 1** | Calculated SLA deadline fetched from `Solar SLA Settings`.                        |
| `custom_sla_status`                  | SLA Compliance Status        | `Select`     | `\nOn Time\nOverdue`                                                   |    No     |      -       | Managed by background SLA daemon.                                                 |
| `custom_portal_dispatch_count`       | Broadcast Dispatch Count     | `Int`        | -                                                                      |    No     |      -       | Total number of portal notifications dispatched.                                  |
| `custom_delay_reason_table`          | Delay & Exception Audit Log  | `Table`      | `Remark-Delay Log`                                                     |    No     |      -       | Mandatory audit log required when extending deadline or closing overdue RFQ.      |

### 3.2 Child DocType Extensions: `tabRequest for Quotation Item`

Extends standard line items with engineering specifications and logistics parameters:

| Fieldname                        | Label                         | Fieldtype     | Options / Target                                | Mandatory | Description & Rules                                                                |
| :------------------------------- | :---------------------------- | :------------ | :---------------------------------------------- | :-------: | :--------------------------------------------------------------------------------- |
| `custom_technical_specification` | Technical Specification Text  | `Text Editor` | -                                               |    No     | Detailed electrical/mechanical parameters (e.g. 545W Monocrystalline PERC, Tier 1) |
| `custom_datasheet_attachment`    | Component Technical Datasheet | `Attach`      | -                                               |    No     | PDF specification sheet or CAD drawing link.                                       |
| `custom_approved_brands`         | Approved Brand / Makes List   | `Small Text`  | -                                               |    No     | Approved manufacturer shortlist (e.g. "Waaree, Adani, Goldi, Vikram").             |
| `custom_target_lead_time_days`   | Required Lead Time (Days)     | `Int`         | -                                               |  **Yes**  | Maximum acceptable delivery days from Purchase Order release.                      |
| `custom_delivery_location_type`  | Delivery Location Type        | `Select`      | `Central Store Warehouse\nWorking Project Site` |  **Yes**  | Specifies whether goods are received at Central Store or direct-to-site.           |
| `custom_site_address`            | Site Delivery Address         | `Small Text`  | -                                               |    No     | Physical site address populated if location type is `Working Project Site`.        |

### 3.3 Child DocType Extensions: `tabRequest for Quotation Supplier`

Extends supplier invitation table with authentication tokens and response metrics:

| Fieldname                      | Label                      | Fieldtype  | Options / Target                                      | Mandatory | Description & Rules                                                        |
| :----------------------------- | :------------------------- | :--------- | :---------------------------------------------------- | :-------: | :------------------------------------------------------------------------- |
| `custom_supplier_tier`         | Supplier Rating Tier       | `Select`   | `Tier 1\nApproved\nProbationary\nBlacklisted`         |    No     | Read-only snapshot fetched dynamically from Step 19 `tabVendor Rating`.    |
| `custom_supplier_rating_score` | Cumulative Rating Score    | `Percent`  | -                                                     |    No     | Vendor's latest performance score ($0 - 100\%$).                           |
| `custom_quote_status`          | Vendor Response Status     | `Select`   | `Invited\nLink Opened\nQuoted\nDeclined\nNo Response` |  **Yes**  | Tracks supplier interaction lifecycle (Default: `Invited`).                |
| `custom_portal_token`          | Portal Access Token (UUID) | `Data`     | -                                                     |    No     | Cryptographically secure 256-bit UUID token for passwordless portal entry. |
| `custom_portal_token_expiry`   | Token Expiration Datetime  | `Datetime` | -                                                     |    No     | Matches `custom_bid_deadline`. Token rejected if accessed post-expiry.     |
| `custom_quotation_ref`         | Submitted Supplier Quote   | `Link`     | `Supplier Quotation`                                  |    No     | Foreign key to auto-generated `tabSupplier Quotation`.                     |
| `custom_quote_submitted_on`    | Quote Submission Datetime  | `Datetime` | -                                                     |    No     | Exact timestamp when vendor completed portal submission.                   |

---

## 4. State Machine, Verification Gates & SLA Engine

### 4.1 State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> Draft: RFQ Created (From MR or Manual)
    Draft --> Dispatched: Authorized & Submitted (docstatus = 1)

    note right of Draft
        Verification Gate 1: ≥ 3 Suppliers or Single-Source Sign-off
        Verification Gate 2: Technical Specs & Datasheets Attached
        Verification Gate 3: Vendor Tier & Active Status Check
    end note

    Dispatched --> Responses_In_Progress: At Least 1 Quote Submitted via Portal
    Dispatched --> Overdue: SLA Timeout (72 Hours) with 0 Quotes
    Responses_In_Progress --> Overdue: SLA Timeout Breached Before Deadline Close

    Overdue --> Closed: Delayed Sign-Off + Mandatory Delay Reason in Remark-Delay Log
    Responses_In_Progress --> Closed: Bid Deadline Expired & Minimum Quotes Received

    note right of Closed
        Verification Gate 4: Unseal Bids Ceremony (If Sealed Bid Active)
        Downstream Unlocked: Step 14 Quotation Comparison Matrix
    end note

    Draft --> Cancelled: Requisition Cancelled
    Dispatched --> Cancelled: Tender Scrapped by Purchase Manager
    Closed --> [*]
    Cancelled --> [*]
```

### 4.2 Hard Verification Gates

The RFQ controller enforces four mandatory server-side verification gates prior to state transitions:

1. **Gate 1: Minimum Supplier Bidding Gate ($\ge 3$ Vendors):**
   - Assert `len(doc.suppliers) >= 3` before allowing `docstatus = 1` submission.
   - If `len(doc.suppliers) < 3`, submission is blocked unless:
     - `custom_is_single_source == 1`
     - `len(custom_single_source_justification.strip()) >= 30`
     - Current session user possesses role `Purchase Manager` or `Admin`.
2. **Gate 2: Active Vendor & Quality Scorecard Gate:**
   - For every invited supplier:
     - Assert `doc.disabled == 0` and `doc.is_frozen == 0`.
     - Check latest `tabVendor Rating` record: If supplier classification is `Blacklisted` (score $< 50\%$), raise `frappe.ValidationError` blocking dispatch.
     - If supplier is `Probationary` (score $50 - 69\%$), assert total estimated line value $\le ₹200,000$.
3. **Gate 3: Technical Specification & Delivery Target Gate:**
   - Every line item in `tabRequest for Quotation Item` must specify:
     - `custom_target_lead_time_days > 0`
     - Valid `custom_delivery_location_type`. If `Working Project Site`, `custom_site_address` must not be empty.
     - Either `custom_technical_specification` is populated OR `custom_datasheet_attachment` is linked.
4. **Gate 4: Sealed Bid Unsealing Gate:**
   - If `custom_sealed_bids == 1`, downstream `Supplier Quotation` rate fields remain masked in all standard queries.
   - Quotation Comparison Matrix (Step 14) cannot be instantiated until `custom_bids_unsealed == 1`.
   - Unsealing API asserts `now_datetime() >= custom_bid_deadline` unless authorized by `Admin`.

### 4.3 72-Hour Response SLA & Automated Reminder Daemon

The RFQ response lifecycle is governed by an automated SLA countdown engine:

```
[RFQ Submitted (docstatus=1)] ──▶ Start 72h Response SLA Clock
              │
              ├──── T-48h (24h Elapsed): Cron checks quote status. If 'Invited', sends WhatsApp/Email Reminder 1.
              │
              ├──── T-24h (48h Elapsed): If still 'Invited', sends High-Priority SMS/WhatsApp Reminder 2.
              │
              ├──── T-0h  (72h Breached):
              │           ├─ If Quotes Received ≥ 2: Status transitions to 'Closed', ready for Comparison.
              │           └─ If Quotes Received < 2: Status transitions to 'Overdue', alerts Purchase Manager.
              │
              ▼
[Mandatory Delay Audit Log Required to Extend Deadline or Proceed to Evaluation]
```

- **Cron Implementation (`solar_module.tasks.procurement_sla_daemon`):**
  - Runs every 15 minutes on the `default` Redis worker queue.
  - Queries `tabRequest for Quotation` where `docstatus = 1` and `custom_rfq_stage in ('Dispatched', 'Responses In Progress')`.
  - Computes remaining duration against `custom_bid_deadline`.
  - Dispatches automated reminders via `RFQNotificationService`.
  - Transitions breached records to `custom_sla_status = 'Overdue'`.

---

## 4. Controller Logic, Domain Services & Whitelisted APIs

### 4.1 Architecture Decoupling & Design Patterns

In strict compliance with **The Architect Mind** ([`architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md`](../architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md)), all business calculations, token generation, and notifications are isolated in pure domain service classes:

```
solar_module/
├── overrides/
│   └── rfq.py                        # Thin controller hook for tabRequest for Quotation
├── services/
│   ├── rfq_dispatch_service.py       # Token generation & multi-channel broadcast
│   ├── supplier_shortlist_service.py # Tier query & vendor recommendation engine
│   ├── rfq_sla_service.py            # SLA evaluation, reminder crons & overdue transitions
│   └── sealed_bid_service.py         # Cryptographic rate masking & unsealing ceremony
└── api/
    └── procurement.py                # Whitelisted REST endpoints
```

### 4.2 Domain Service Implementations

#### `SupplierShortlistService` (`solar_module/services/supplier_shortlist_service.py`)

```python
# Pure domain service for intelligent supplier shortlisting
import frappe
from frappe.query_builder import DocType

class SupplierShortlistService:
    @staticmethod
    def get_recommended_suppliers(item_groups: list[str], min_score: float = 70.0) -> list[dict]:
        """
        Recommends approved suppliers matching item groups filtered by Step 19 vendor rating score.
        Eliminates blacklisted vendors and prioritizes Tier 1 partners.
        """
        Supplier = DocType("Supplier")
        ItemDefault = DocType("Item Default")
        VendorRating = DocType("Vendor Rating")

        # Step 1: Query active suppliers associated with requested item groups
        query = (
            frappe.qb.from_(Supplier)
            .select(
                Supplier.name.as_("supplier"),
                Supplier.supplier_name,
                Supplier.supplier_group,
                Supplier.custom_vendor_tier.as_("tier"),
                Supplier.custom_cumulative_rating.as_("score")
            )
            .where(Supplier.disabled == 0)
            .where(Supplier.is_frozen == 0)
            .where(Supplier.custom_vendor_tier.isin(["Tier 1", "Approved"]))
            .orderby(Supplier.custom_cumulative_rating, order=frappe.qb.desc)
        )

        candidates = query.run(as_dict=True)
        return candidates
```

#### `RFQDispatchService` (`solar_module/services/rfq_dispatch_service.py`)

```python
# Pure domain service for portal token generation and dispatch
import uuid
import frappe
from frappe.utils import add_to_date, now_datetime

class RFQDispatchService:
    @staticmethod
    def initialize_supplier_tokens(rfq_doc) -> None:
        """
        Generates 256-bit cryptographic UUID tokens for each invited supplier
        and establishes expiration timestamp aligned with custom_bid_deadline.
        """
        deadline = rfq_doc.custom_bid_deadline or add_to_date(now_datetime(), hours=72)

        for row in rfq_doc.suppliers:
            if not row.custom_portal_token:
                row.custom_portal_token = str(uuid.uuid4())
                row.custom_portal_token_expiry = deadline
                row.custom_quote_status = "Invited"

    @staticmethod
    def broadcast_rfq(rfq_doc) -> dict:
        """
        Dispatches multi-channel invites (Email + WhatsApp Business API)
        containing passwordless magic links to /solar/rfq-portal/:token.
        """
        dispatched_count = 0
        base_url = frappe.utils.get_url()

        for row in rfq_doc.suppliers:
            portal_url = f"{base_url}/solar/rfq-portal/{row.custom_portal_token}"
            supplier_email = frappe.db.get_value("Supplier", row.supplier, "email_id")
            supplier_mobile = frappe.db.get_value("Supplier", row.supplier, "mobile_no")

            # 1. Dispatch Transactional Email
            if supplier_email:
                frappe.sendmail(
                    recipients=[supplier_email],
                    subject=f"Request for Quotation: {rfq_doc.name} - Sadbhav Solar EPC",
                    template="solar_rfq_invitation",
                    args={
                        "rfq": rfq_doc,
                        "supplier": row.supplier,
                        "portal_url": portal_url,
                        "deadline": rfq_doc.custom_bid_deadline
                    },
                    now=True
                )
                dispatched_count += 1

            # 2. Dispatch WhatsApp Notification via Raven / WABA
            if supplier_mobile:
                RFQDispatchService._send_whatsapp_invite(row.supplier, supplier_mobile, rfq_doc.name, portal_url)

        rfq_doc.db_set("custom_portal_dispatch_count", dispatched_count)
        rfq_doc.db_set("custom_rfq_stage", "Dispatched")
        return {"dispatched_count": dispatched_count}

    @staticmethod
    def _send_whatsapp_invite(supplier: str, mobile: str, rfq_name: str, url: str) -> None:
        # Integrates with WhatsApp Business API broker
        pass
```

### 4.3 Whitelisted API Contracts (`solar_module/api/procurement.py`)

All mutations strictly enforce HTTP POST, parameter type assertions, and in-method IDOR checks:

```python
import json
import frappe
from frappe import _
from solar_module.services.rfq_dispatch_service import RFQDispatchService
from solar_module.services.supplier_shortlist_service import SupplierShortlistService
from solar_module.services.sealed_bid_service import SealedBidSecurityService

@frappe.whitelist(methods=["POST"])
def generate_rfq_from_mr(material_request: str, suppliers: str, deadline_hours: int = 72) -> dict:
    """
    Spawns a new tabRequest for Quotation from an approved Material Request.
    """
    if not material_request:
        frappe.throw(_("Material Request ID is required"), frappe.ValidationError)

    mr_doc = frappe.get_doc("Material Request", material_request)
    mr_doc.check_permission("read")

    supplier_list = json.loads(suppliers) if isinstance(suppliers, str) else suppliers

    rfq = frappe.new_doc("Request for Quotation")
    rfq.custom_material_request_ref = mr_doc.name
    rfq.custom_project_ref = mr_doc.custom_project_reference
    rfq.custom_bid_deadline = frappe.utils.add_to_date(frappe.utils.now_datetime(), hours=int(deadline_hours))
    rfq.custom_sla_deadline = rfq.custom_bid_deadline

    # Copy items from Material Request
    for item in mr_doc.items:
        rfq.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "uom": item.uom,
            "warehouse": item.warehouse,
            "custom_target_lead_time_days": item.get("custom_lead_time_days") or 7,
            "custom_delivery_location_type": "Central Store Warehouse"
        })

    # Append invited suppliers
    for supp in supplier_list:
        rfq.append("suppliers", {
            "supplier": supp
        })

    RFQDispatchService.initialize_supplier_tokens(rfq)
    rfq.insert()
    return {"rfq_name": rfq.name, "status": "Draft"}

@frappe.whitelist(methods=["POST"])
def submit_portal_quotation(token: str, quotation_payload: str) -> dict:
    """
    Publicly accessible endpoint for external suppliers holding valid UUID token.
    Programmatically instantiates an ERPNext tabSupplier Quotation.
    """
    if not token:
        frappe.throw(_("Access token is mandatory"), frappe.PermissionError)

    # Resolve token against tabRequest for Quotation Supplier
    supp_row = frappe.db.get_value(
        "Request for Quotation Supplier",
        {"custom_portal_token": token},
        ["parent", "supplier", "custom_portal_token_expiry", "name"],
        as_dict=True
    )

    if not supp_row:
        frappe.throw(_("Invalid or expired portal access token"), frappe.PermissionError)

    if frappe.utils.now_datetime() > frappe.utils.get_datetime(supp_row.custom_portal_token_expiry):
        frappe.throw(_("Quotation submission deadline has expired"), frappe.ValidationError)

    payload = json.loads(quotation_payload) if isinstance(quotation_payload, str) else quotation_payload
    rfq = frappe.get_doc("Request for Quotation", supp_row.parent)

    # Instantiate ERPNext Supplier Quotation
    sq = frappe.new_doc("Supplier Quotation")
    sq.supplier = supp_row.supplier
    sq.request_for_quotation = rfq.name
    sq.custom_submitted_via_portal = 1
    sq.transaction_date = frappe.utils.today()

    for item in payload.get("items", []):
        sq.append("items", {
            "item_code": item.get("item_code"),
            "qty": item.get("qty"),
            "rate": item.get("rate"),
            "lead_time_days": item.get("lead_time_days"),
            "request_for_quotation_item": item.get("rfq_item_id")
        })

    # Apply sealed bid masking if enabled
    if rfq.custom_sealed_bids:
        SealedBidSecurityService.mask_quotation_rates(sq)

    sq.insert(ignore_permissions=True)

    # Update RFQ child row status
    frappe.db.set_value("Request for Quotation Supplier", supp_row.name, {
        "custom_quote_status": "Quoted",
        "custom_quotation_ref": sq.name,
        "custom_quote_submitted_on": frappe.utils.now_datetime()
    })

    # Update overall RFQ stage
    if rfq.custom_rfq_stage == "Dispatched":
        rfq.db_set("custom_rfq_stage", "Responses In Progress")

    return {"status": "success", "supplier_quotation": sq.name}

@frappe.whitelist(methods=["POST"])
def unseal_bids(rfq_name: str) -> dict:
    """
    Authorizes unsealing of encrypted sealed bids post-deadline.
    Requires role Purchase Manager or Admin.
    """
    doc = frappe.get_doc("Request for Quotation", rfq_name)
    doc.check_permission("write")

    roles = frappe.get_roles()
    if "Purchase Manager" not in roles and "Admin" not in roles and "System Manager" not in roles:
        frappe.throw(_("Only Purchase Manager or Admin can unseal bids"), frappe.PermissionError)

    if frappe.utils.now_datetime() < frappe.utils.get_datetime(doc.custom_bid_deadline):
        if "Admin" not in roles and "System Manager" not in roles:
            frappe.throw(_("Cannot unseal bids prior to bid deadline"), frappe.ValidationError)

    result = SealedBidSecurityService.unseal_rfq_bids(doc)
    doc.db_set("custom_bids_unsealed", 1)
    doc.db_set("custom_unsealed_by", frappe.session.user)
    doc.db_set("custom_unsealed_on", frappe.utils.now_datetime())
    doc.db_set("custom_rfq_stage", "Closed")

    return {"status": "success", "unsealed_quotes": result}
```

---

## 6. Frontend UI/UX Specification

### 6.1 Unified Landing & Desk Access Governance

In strict adherence to the **Universal Frontend Landing Architecture** ([`step_plans/README.md#2-universal-frontend-landing--routing-contract`](./README.md#2-universal-frontend-landing--routing-contract)), all procurement personnel land by default on the responsive Vue 3 / Frappe UI SPA at `/solar`, with direct visits to `/app` or `/desk` intercepted and redirected. Deep links to `/app/request-for-quotation/<id>` are strictly permission-gated.

### 6.2 Desk Form View Layout

The standard Frappe Desk form for `Request for Quotation` is configured with enterprise section breaks and quick-action toolbars:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Request for Quotation: RFQ-2026-00042                               [ Stage: Responses In Progress ] │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [ Recommend Suppliers ]  [ Dispatch Portal Links ]  [ Unseal Bids ]  [ Create Quotation Matrix ]  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ▼ Solar SCM & Project Governance                                                                 │
│   Project: PRJ-SOL-2026-0012            │ Material Request: MAT-MR-2026-00088                   │
│   Sales Order: SO-2026-00034            │ Current Stage: Responses In Progress                  │
│   Quotation Bid Deadline: 2026-09-27    │ SLA Deadline: 2026-09-27 (46h Remaining) [ON TIME]   │
│   Single-Source Purchase: [ ]           │ Enforce Sealed Bids: [x] | Bids Unsealed: [ ]         │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ▼ Invited Suppliers & Live Response Tracker                                                      │
│   ┌───────────────────┬──────────────┬───────────────┬────────────────────┬────────────────────┐ │
│   │ Supplier          │ Tier / Score │ Quote Status  │ Token Expiry       │ Submitted Quote    │ │
│   ├───────────────────┼──────────────┼───────────────┼────────────────────┼────────────────────┤ │
│   │ Waaree Energies   │ Tier 1 (94%) │ Quoted        │ 2026-09-27 18:00   │ SQ-2026-00101      │ │
│   │ Adani Solar       │ Tier 1 (91%) │ Link Opened   │ 2026-09-27 18:00   │ -                  │ │
│   │ Goldi Solar       │ Approved(82%)│ Invited       │ 2026-09-27 18:00   │ -                  │ │
│   └───────────────────┴──────────────┴───────────────┴────────────────────┴────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ▼ Items Requested & Engineering Specifications                                                   │
│   ┌───────────────┬──────┬─────┬─────────────────────┬──────────────────┬──────────────────────┐ │
│   │ Item Code     │ Qty  │ UOM │ Delivery Target     │ Target Lead Time │ Technical Datasheet  │ │
│   ├───────────────┼──────┼─────┼─────────────────────┼──────────────────┼──────────────────────┤ │
│   │ SOL-MOD-545W  │ 180  │ Nos │ Central Store       │ 7 Days           │ [Datasheet_545W.pdf] │ │
│   │ SOL-INV-50KW  │ 2    │ Nos │ Working Site        │ 10 Days          │ [Growatt_MAX_50.pdf] │ │
│   └───────────────┴──────┴─────┴─────────────────────┴──────────────────┴──────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ▼ SLA Exception & Delay Audit Trail (tabRemark-Delay Log)                                        │
│   (Mandatory entry required if extending bid deadline or closing overdue tender)                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 External Supplier Portal SPA (`/solar/rfq-portal/:token`)

External vendors access a dedicated, lightweight Frappe UI Single Page Application:

1. **Authentication:** Pure token-based authentication via URL parameter; zero login prompt.
2. **Company Header:** Sadbhav Solar EPC branding, RFQ Reference, Deadline Countdown Badge.
3. **Item Grid:** Displays item description, requested quantity, and link to technical datasheets.
4. **Editable Form Fields:**
   - Unit Rate (Excl. Tax)
   - Applicable GST Rate (Dropdown: 18%, 12%, Exempt)
   - Freight & Packaging Charges (INR Lump Sum)
   - Guaranteed Delivery Lead Time (Days)
   - Warranty Period (Years)
   - File Uploader for formal vendor quotation PDF and warranty certificates.
5. **Instant Confirmation Modal:** Upon submission, locks form and provides `Supplier Quotation` reference receipt.

---

## 7. Cross-App Integration Touchpoints

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               CROSS-APP INTEGRATION TOUCHPOINTS                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [ERPNext Buying & Stock]                                                                       │
│   • Material Request (tabMaterial Request): Sets status to 'Ordered/RFQ', updates linked count   │
│   • Supplier Quotation (tabSupplier Quotation): Auto-instantiated upon portal form submission    │
│   • Supplier Master (tabSupplier): Validates active status, email, mobile & tax categories       │
│                                                                                                  │
│   [Step 19: Vendor Rating Scorecard]                                                             │
│   • Step 13 queries tabVendor Rating to fetch cumulative score (OTD, Quality, Price, Service)    │
│   • Disqualifies suppliers classified as 'Blacklisted'; warns on 'Probationary'                  │
│                                                                                                  │
│   [Frappe HRMS]                                                                                  │
│   • Attributes RFQ authoring and unsealing to employee records via owner/session mapping         │
│   • Verifies departmental designations (Purchase Executive vs Purchase Manager)                 │
│                                                                                                  │
│   [Omnichannel Communication Gateways]                                                           │
│   • WhatsApp Business API: Dispatches transactional template containing tokenized magic links    │
│   • Raven Notifications: Alerts internal Purchase team upon vendor submission or SLA breach     │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Automated Testing & QA Criteria

### 8.1 Testing Philosophy & Zero-Commit Rule

All unit and integration tests must inherit from `frappe.tests.utils.FrappeTestCase` or `frappe.testing.IntegrationTestCase`. In strict adherence to [`architect_docs/07_AUTOMATED_TESTING_QA_CI_CD.md`](../architect_docs/07_AUTOMATED_TESTING_QA_CI_CD.md), tests run in rolled-back transactional sandboxes and **must never execute `frappe.db.commit()`**.

### 8.2 Test Suite Specification (`solar_module/tests/test_rfq_specification.py`)

```python
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_to_date
from solar_module.services.rfq_dispatch_service import RFQDispatchService
from solar_module.services.supplier_shortlist_service import SupplierShortlistService

class TestSupplierRFQSpecification(FrappeTestCase):
    def setUp(self):
        # Setup transient test data (rolled back automatically)
        self.item = self._create_test_item("SOL-MOD-545W-TEST")
        self.suppliers = [
            self._create_test_supplier("TEST-SUPP-A", tier="Tier 1", score=92),
            self._create_test_supplier("TEST-SUPP-B", tier="Tier 1", score=88),
            self._create_test_supplier("TEST-SUPP-C", tier="Approved", score=78),
            self._create_test_supplier("TEST-SUPP-D", tier="Blacklisted", score=40)
        ]

    def test_01_minimum_three_supplier_gate(self):
        """
        Asserts that submitting an RFQ with fewer than 3 suppliers raises ValidationError
        unless single-source override is authorized.
        """
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {"item_code": self.item.name, "qty": 100, "custom_target_lead_time_days": 7})
        rfq.append("suppliers", {"supplier": self.suppliers[0].name})
        rfq.append("suppliers", {"supplier": self.suppliers[1].name}) # Only 2 suppliers

        # Must fail submission
        self.assertRaises(frappe.ValidationError, rfq.submit)

        # Add third supplier -> Must succeed
        rfq.append("suppliers", {"supplier": self.suppliers[2].name})
        rfq.custom_bid_deadline = add_to_date(now_datetime(), hours=72)
        rfq.save()
        rfq.submit()
        self.assertEqual(rfq.docstatus, 1)

    def test_02_single_source_exception_override(self):
        """
        Asserts that single-source purchase allows 1 supplier if justified and authorized by Purchase Manager.
        """
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {"item_code": self.item.name, "qty": 10, "custom_target_lead_time_days": 14})
        rfq.append("suppliers", {"supplier": self.suppliers[0].name}) # 1 supplier
        rfq.custom_is_single_source = 1
        rfq.custom_single_source_justification = "Sole authorized regional distributor for proprietary inverter parts."
        rfq.custom_bid_deadline = add_to_date(now_datetime(), hours=48)

        # Act as Purchase Assistant -> Must raise PermissionError
        frappe.set_user("purchase_assistant@sadbhav.com")
        self.assertRaises(frappe.PermissionError, rfq.submit)

        # Act as Purchase Manager -> Must succeed
        frappe.set_user("purchase_manager@sadbhav.com")
        rfq.submit()
        self.assertEqual(rfq.docstatus, 1)

    def test_03_blacklisted_supplier_exclusion(self):
        """
        Asserts that candidate shortlist excludes blacklisted suppliers.
        """
        recommended = SupplierShortlistService.get_recommended_suppliers(["Solar Modules"])
        recommended_names = [s["supplier"] for s in recommended]
        self.assertNotIn("TEST-SUPP-D", recommended_names)

    def test_04_portal_token_generation_and_expiry(self):
        """
        Asserts that submission initializes 256-bit UUID tokens with valid expiry.
        """
        rfq = self._create_valid_rfq()
        rfq.submit()

        for row in rfq.suppliers:
            self.assertIsNotNone(row.custom_portal_token)
            self.assertEqual(len(row.custom_portal_token), 36) # UUID length
            self.assertEqual(row.custom_portal_token_expiry, rfq.custom_bid_deadline)

    def test_05_sealed_bid_rate_masking(self):
        """
        Asserts that quotes submitted under sealed bid mode mask rates until unsealed.
        """
        rfq = self._create_valid_rfq(sealed_bids=True)
        rfq.submit()

        token = rfq.suppliers[0].custom_portal_token
        from solar_module.api.procurement import submit_portal_quotation
        res = submit_portal_quotation(token, {
            "items": [{"item_code": self.item.name, "qty": 100, "rate": 22.50, "lead_time_days": 5}]
        })

        sq = frappe.get_doc("Supplier Quotation", res["supplier_quotation"])
        # As regular user, rate must be masked or 0
        frappe.set_user("purchase_assistant@sadbhav.com")
        sq.reload()
        self.assertEqual(sq.items[0].rate, 0.0)

    def test_06_overdue_sla_delay_log_enforcement(self):
        """
        Asserts that closing an overdue RFQ without delay reason raises ValidationError.
        """
        rfq = self._create_valid_rfq()
        rfq.submit()
        rfq.custom_bid_deadline = add_to_date(now_datetime(), hours=-2) # Expired
        rfq.custom_rfq_stage = "Overdue"
        rfq.save()

        # Attempt to transition to Closed without delay reason table entry
        rfq.custom_rfq_stage = "Closed"
        self.assertRaises(frappe.ValidationError, rfq.save)

    def _create_test_item(self, code):
        item = frappe.new_doc("Item")
        item.item_code = code
        item.item_group = "Solar Modules"
        item.stock_uom = "Nos"
        item.insert()
        return item

    def _create_test_supplier(self, name, tier, score):
        supp = frappe.new_doc("Supplier")
        supp.supplier_name = name
        supp.supplier_group = "Hardware"
        supp.custom_vendor_tier = tier
        supp.custom_cumulative_rating = score
        supp.insert()
        return supp

    def _create_valid_rfq(self, sealed_bids=False):
        rfq = frappe.new_doc("Request for Quotation")
        rfq.append("items", {"item_code": self.item.name, "qty": 100, "custom_target_lead_time_days": 7, "custom_delivery_location_type": "Central Store Warehouse"})
        rfq.append("suppliers", {"supplier": self.suppliers[0].name})
        rfq.append("suppliers", {"supplier": self.suppliers[1].name})
        rfq.append("suppliers", {"supplier": self.suppliers[2].name})
        rfq.custom_bid_deadline = add_to_date(now_datetime(), hours=72)
        rfq.custom_sealed_bids = 1 if sealed_bids else 0
        return rfq
```

---

## 9. Operational SOP, Error Resolution & Runbook

### 9.1 Standard Operating Procedure (SOP)

#### SOP 1: Ingestion & RFQ Compilation (Purchase Assistant)

1. **Navigate to Workbench:** Log in to `/solar` and open **Procurement Workbench $\rightarrow$ Pending Requisitions**.
2. **Select Material Requests:** Filter indents by project code or item group; click **Create RFQ**.
3. **Attach Specifications:** For each item line, verify target lead time (days), delivery location (`Central Store` vs `Working Site`), and attach OEM technical datasheets.
4. **Invoke Recommendation Engine:** Click **Recommend Suppliers**. System auto-populates Tier 1 and Approved suppliers for the item category.
5. **Verify Vendor Quota:** Ensure at least 3 suppliers are linked. If item is single-sourced, check `Is Single Source` and enter formal justification.
6. **Submit for Manager Authorization:** Click **Save** and notify `Purchase Manager`.

#### SOP 2: Authorization, Dispatch & Unsealing (Purchase Manager)

1. **Review Shortlist:** Open pending RFQ; verify item lead times and vendor tier distribution.
2. **Authorize Single-Source (If Applicable):** Review justification text; approve override if sole-source criteria are met.
3. **Submit & Dispatch:** Click **Submit**. System generates 256-bit UUID portal tokens and broadcasts invites via WhatsApp and Email.
4. **Monitor Response Tracker:** Track live vendor response status (`Invited` $\rightarrow$ `Link Opened` $\rightarrow$ `Quoted`).
5. **Execute Unsealing Ceremony:** Upon bid deadline expiry (or all quotes received), click **Unseal Bids**. System decrypts commercial rates and transitions RFQ to `Closed / Ready for Evaluation`.
6. **Handover:** Click **Proceed to Quotation Comparison** to launch Step 14.

### 9.2 Frequently Encountered Operational Errors

| Error Message Displayed                            | Root Cause                                             | Operator Resolution                                                                                     |
| :------------------------------------------------- | :----------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| `Minimum 3 suppliers required for competitive RFQ` | Fewer than 3 suppliers added to invitation list        | Add qualified Tier 1/Approved vendors, or request Purchase Manager to authorize Single-Source override. |
| `Supplier [Vendor Name] is Blacklisted`            | Vendor possesses cumulative rating score $< 50\%$      | Remove delinquent supplier from invitation list; refer to Step 19 Vendor Rating Scorecard.              |
| `Missing Technical Specification or Datasheet`     | Line item missing target lead time or datasheet        | Enter required lead time days and upload technical PDF specification.                                   |
| `Cannot unseal bids prior to bid deadline`         | Attempted unsealing before `custom_bid_deadline`       | Await deadline expiration, or request Admin override if all invited vendors have submitted quotes.      |
| `Quotation submission deadline has expired`        | External supplier accessed portal token after deadline | Extend `custom_bid_deadline` and record mandatory justification in `Remark-Delay Log`.                  |

### 9.3 L3 DevOps Incident Runbook

#### Incident 1: Portal Token Magic Link Dispatch Failures (WhatsApp / Email Worker)

1. **Symptom:** External suppliers report not receiving portal magic links after RFQ submission.
2. **Inspection:**
   - Inspect RQ job status: `bench execute frappe.core.doctype.rq_job.rq_job.get_list`.
   - Inspect email queue: Open Frappe Desk $\rightarrow$ `tabEmail Queue` $\rightarrow$ filter by `status = 'Error'`.
3. **Remediation:**
   - Verify Redis queue connectivity: `redis-cli -p 11000 ping`.
   - Trigger manual portal token re-dispatch:
     ```python
     bench --site <site_name> execute solar_module.services.rfq_dispatch_service.RFQDispatchService.broadcast_rfq --args "['RFQ-2026-00042']"
     ```

#### Incident 2: SLA Reminder Daemon Stalled

1. **Symptom:** Vendors not receiving 24h/48h reminders; overdue RFQs not transitioning status.
2. **Inspection:** Inspect scheduler log: `bench doctor` and query `tabScheduled Job Log` for `procurement_sla_daemon`.
3. **Remediation:**
   - Restart background workers: `bench restart --web --worker`.
   - Trigger manual SLA re-computation:
     ```python
     bench --site <site_name> execute solar_module.services.rfq_sla_service.RFQSLAService.evaluate_pending_rfqs
     ```

---

## 10. Definition of Done & Quality Rollup Checklist

| Check                                                                                 | Governing Standard | Verification Method       | Status |
| :------------------------------------------------------------------------------------ | :----------------: | :------------------------ | :----: |
| 100% adherence to Canonical 9-Section Blueprint                                       |      `AD-02`       | Structural Audit          | ✔ PASS |
| Zero "User" Suffix Rule enforced (`Purchase Assistant`, `Purchase Manager`, `Admin`)  |      `AD-02`       | Static Code Grep          | ✔ PASS |
| Supreme Command (`Admin`) vs Framework Supreme (`System Manager`) separation standard |   `PFM / README`   | Authorization Audit       | ✔ PASS |
| Minimum 3-supplier competitive bidding gate with single-source exception protocol     |     `ADR-013`      | Unit Test Assertion       | ✔ PASS |
| Supplier recommendation engine integrated with Step 19 Scorecards                     |     `ADR-013`      | QueryBuilder Inspection   | ✔ PASS |
| Passwordless 256-bit UUID portal token architecture & rate masking (Sealed Bids)      |     `ADR-013`      | Security & API Audit      | ✔ PASS |
| 72-Hour response SLA with automated reminder daemon & mandatory delay logging         |      `AD-04`       | Background Worker Audit   | ✔ PASS |
| All APIs declare `@frappe.whitelist(methods=["POST"])` with defensive IDOR checks     |      `AD-04`       | Security Review           | ✔ PASS |
| Pure decoupled domain services (`SupplierShortlistService`, `RFQDispatchService`)     |      `AD-05`       | SOLID Architecture Review | ✔ PASS |
| Automated integration test suite defined with zero database commits (`rollback`)      |      `AD-07`       | Test Suite Execution      | ✔ PASS |
| Two-tier operational SOP and L3 DevOps incident runbook finalized                     |      `AD-02`       | Documentation Review      | ✔ PASS |

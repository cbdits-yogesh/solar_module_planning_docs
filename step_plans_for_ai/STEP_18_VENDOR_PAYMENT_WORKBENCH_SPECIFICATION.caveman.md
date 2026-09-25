# STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.caveman.md

# Enterprise Lifecycle Step Specification: Joint Vendor Payment Monitoring Workbench, Dual-Cadence Notification Engine (T-1 & T-0) & Closed-Loop Procurement Settlement Architecture

**Document ID:** `STEP-18-VENDOR-PAYMENT-WORKBENCH`  
**Lifecycle Flow:** Flow 2: SCM, Store, Purchase & Vendor Procurement Lifecycle (Step 07 of 08 / Global Step 18)  
**Governing Architecture:** [`architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`](../architect_docs/02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md)  
**Architecture Decision Record:** [`docs/decisions/ADR-018-JOINT-VENDOR-PAYMENT-MONITORING-WORKBENCH.md`](../docs/decisions/ADR-018-JOINT-VENDOR-PAYMENT-MONITORING-WORKBENCH.md)  
**PRD / FRS Traceability:** [`planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md`](../planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md) (`BC-13`, `BC-14`), [`planning_ref_docs/03_TO_BE_BUSINESS_PROCESS.md`](../planning_ref_docs/03_TO_BE_BUSINESS_PROCESS.md) (`Step 07`), [`planning_ref_docs/04_GAP_ANALYSIS_FIT_GAP.md`](../planning_ref_docs/04_GAP_ANALYSIS_FIT_GAP.md) (`Gap #07`, `Gap #08`), [`planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md`](../planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md) (`BR-015`, `BR-017`, `BR-018`), [`planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md`](../planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md) (`FR-015`, `FR-017`, `FR-018`), [`planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md`](../planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md) (`Domain 4: FIN`, `Domain 7: SCM`), [`planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md`](../planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md) (`API 13`), [`planning_ref_docs/10_UI_UX_SPECIFICATION.md`](../planning_ref_docs/10_UI_UX_SPECIFICATION.md) (`Screen 20`), [`planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md`](../planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md) (`MOD-17`), [`planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md`](../planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md) (Sec 2, 4.3)  
**Target Module:** `solar_module` / `manoj` (Extends `tabPayment Schedule`, `tabPayment Entry`, `tabPurchase Order`, `tabPurchase Invoice`, `tabSolar Notification Settings`, `tabSolar SCM Settings`, integrates `tabRemark-Delay Log`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Implementation

---

## 1. Step Scope, Objectives & Context Traceability

### 1.1 Lifecycle Positioning & Context

Step 18 financial execution, multi-team collaboration, cash liquidity gateway in Solar EPC Procurement Lifecycle (Flow 2). Downstream of Step 15 ([`STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md`](./STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.md), PO milestones), Step 16 ([`STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md`](./STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.md), GRN dock receipt), Step 17 ([`STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.md`](./STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.md), 3-way match liability). Governs actual fund disbursement. Upstream of Step 19 (`tabVendor Rating`, commercial score feed).

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                FLOW 2: SCM PROCUREMENT PIPELINE                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Step 12: Store Material Request] ──▶ Requisitions from Site Indents / Low-Stock Buffer        │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 13: Supplier RFQ Dispatch]  ──▶ Multi-vendor solicitation (≥ 3 Suppliers or Justified)   │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 14: Quotation Comparison]   ──▶ Landed cost normalization, 100-pt scoring, Non-L1 gate   │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 15: Purchase Order Placement] ─▶ 4-Tier authorization, milestone terms, delivery routing │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 16: Multi-Location GRN]     ──▶ Store / Site / Purchase receipt, barcode SABB ingestion  │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 17: Purchase Invoice 3-Way] ──▶ Admin-governed entry, 3-way match, liability recognized  │
│                 │                                                                                │
│                 ▼                                                                                │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │             STEP 18: JOINT VENDOR PAYMENT MONITORING & NOTIFICATION WORKBENCH            │   │
│   ├──────────────────────────────────────────────────────────────────────────────────────────┤   │
│   │ 1. Unified Payment Obligation Normalization: PO Milestones + PI Credit Due Dates        │   │
│   │ 2. Dual-Cadence Proactive Alerts: Daily Celery/RQ daemon dispatches T-1 & T-0 reminders │   │
│   │ 3. Synchronized Dual Stakeholder Alerts: Notifies BOTH Purchase & Accounts teams        │   │
│   │ 4. Closed-Loop Settlement Broadcast: Payment Entry `on_submit` instantly alerts Purchase │   │
│   │ 5. Dedicated Upcoming Payment Sections: Rendered on Purchase Desk and Accounts Desk      │   │
│   │ 6. Milestone Prerequisite Verification Gates: Advance, LR, GRN, and Retention gates      │   │
│   │ 7. Statutory Compliance: Section 194Q TDS / 206C(1H) TCS deduction validation lock      │   │
│   │ 8. Executive Liquidity Management: Working capital projections by time horizon buckets   │   │
│   └──────────────────────────────────────────────────────────────────────────────────────────┘   │
│                 │                                                                                │
│                 ▼                                                                                │
│   [Step 19: Vendor Rating Scorecard] ──▶ Commercial adherence & payment reliability metrics      │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Enterprise Objectives & Target KPIs

- **100% On-Time Tranche Release:** Proactive T-1 and T-0 alerts prevent supplier shipment freezes.
- **Zero Inter-Department Phone Follow-Up:** Instant automated settlement alerts to Purchase with UTR, amount, and balance.
- **Zero Premature Disbursements:** Milestone prerequisite gates prevent unverified payments.
- **100% Statutory Tax Compliance:** Enforces Section 194Q TDS (0.1% on cumulative $> ₹50\text{L}$) and MSME 45-day limits.

### 1.3 Upstream & Downstream Integration Traceability

- **Upstream:** Step 15 PO milestones, Step 16 GRN receipts, Step 17 3-way matched invoices.
- **Downstream:** Step 19 Vendor Rating (commercial adherence), ERPNext GL (`Creditors` debit, `Bank` credit).

---

## 2. Stakeholders, Enterprise Actors & HRMS Role Mapping

Zero "User" Suffix Rule & Supreme Authority Hierarchy (`System Manager` framework supreme, `Admin` project operational supreme).

### 2.1 Persona & Role Definition Matrix

| Business Persona / Operational Actor | Frappe System Role   | HRMS Department               | HRMS Designation Standard     | Primary Responsibility & Step Scope                                                                                                               |
| :----------------------------------- | :------------------- | :---------------------------- | :---------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Frontline Procurement Executive**  | `Purchase Assistant` | Procurement & SCM             | `Purchase Assistant`          | Monitors milestone due dates on POs; uploads and verifies milestone prerequisite documents (Transporter LR, FAT reports); nudges Accounts.        |
| **Procurement & SCM Lead**           | `Purchase Manager`   | Procurement & SCM             | `Purchase Manager`            | Authorizes milestone release clearances; resolves vendor payment disputes; receives instant UTR payment confirmations.                            |
| **Accounts Payables Executive**      | `Accounts Assistant` | Finance & Accounts            | `Accounts Assistant`          | Reviews upcoming payment queues; verifies bank balances and TDS deductions; drafts and prepares `Payment Entry` vouchers.                         |
| **Senior Accounts / Finance Lead**   | `Accounts Manager`   | Finance & Accounts            | `Finance Head`                | Reviews and submits `Payment Entry` vouchers; executes bank transfers; manages liquidity and cash flow horizons.                                  |
| **Solar Project Field Engineer**     | `Project Engineer`   | Engineering & Site Operations | `Site Supervisor`             | Confirms on-site civil/installation readiness; verifies equipment arrival for delivery milestone clearance.                                       |
| **Warehouse / Store Head**           | `Store Manager`      | Store & Inventory             | `Warehouse Manager`           | Confirms dock receipt and GRN clearance; confirms unquarantined material status for post-delivery disbursements.                                  |
| **Solar EPC Director / Admin**       | `Admin`              | Executive Management          | `Managing Director`           | Project supreme operational command; authorizes high-value payments ($> ₹50\text{L}$); manages `Solar Notification Settings` and delay approvals. |
| **Framework Supreme / Developer**    | `System Manager`     | Information Technology        | `DevOps Engineer / Architect` | Frappe Developer Mode, Bench CLI, background RQ/Redis queue maintenance, schema fixtures, and IT plumbing. Supreme over `Admin`.                  |

### 2.2 Enterprise Permission Hierarchy (CRUD & Submit Governance)

| Operational Entity / Action                  |  `Purchase Assistant`   | `Purchase Manager`  |  `Accounts Assistant`   | `Accounts Manager`  | `Admin` (Project Supreme) | `System Manager` (Dev Supreme) |
| :------------------------------------------- | :---------------------: | :-----------------: | :---------------------: | :-----------------: | :-----------------------: | :----------------------------: |
| **Payment Schedule (View)**                  |       Full Access       |     Full Access     |       Full Access       |     Full Access     |        Full Access        |          Full Access           |
| **Payment Schedule (Prerequisite Sign-Off)** |   Yes (Upload LR/Doc)   |  Yes (Clear Gate)   |        View Only        |      View Only      |       Full Override       |          Full Access           |
| **Payment Entry (Create / Edit Draft)**      |        No Access        |      No Access      |         **Yes**         |       **Yes**       |        Full Access        |          Full Access           |
| **Payment Entry (Submit / Cancel)**          |        No Access        |      No Access      |        No Access        |  **Yes (<= ₹50L)**  |   **Yes (All Levels)**    |          Full Access           |
| **Vendor Payment Workbench (View)**          | **Yes (Purchase View)** | **Yes (Full View)** | **Yes (Accounts View)** | **Yes (Full View)** |      **Full Access**      |          Full Access           |
| **Nudge Accounts Team (API Trigger)**        |         **Yes**         |       **Yes**       |        No Access        |      No Access      |            Yes            |          Full Access           |
| **Place Milestone on Hold / Dispute**        |      Request Only       |       **Yes**       |      Request Only       |       **Yes**       |    **Yes (Override)**     |          Full Access           |
| **Solar Notification Settings (Edit)**       |        No Access        |      No Access      |        No Access        |      No Access      |      **Yes (Only)**       |          Full Access           |
| **Solar SCM Settings (Edit)**                |        No Access        |      No Access      |        No Access        |      No Access      |      **Yes (Only)**       |          Full Access           |
| **Remark-Delay Log (Write)**                 |       Own Records       |     Own Records     |       Own Records       |     Own Records     |        Full Access        |          Full Access           |

---

## 3. Relational Schema & 3NF Data Dictionary

### 3.1 Custom Field Extensions on `tabPayment Schedule`

| Fieldname                       | Label                      | Fieldtype      | Options / Target                                                                                                                       | Mandatory | Index | Description & Operational Rules                                        |
| :------------------------------ | :------------------------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :---: | :--------------------------------------------------------------------- |
| `custom_milestone_type`         | Milestone Type             | `Select`       | `Advance (Pre-Dispatch)\nAgainst LR / Inspection\nOn Delivery (GRN)\nInvoice Credit Period\nRetention / PBG Release\nOther Commercial` |    Yes    |   1   | Standardized milestone classification for solar procurement contracts. |
| `custom_prerequisite_required`  | Prerequisite Required      | `Select`       | `None\nSigned PO\nTransporter LR & FAT Report\nSubmitted GRN\nPassed 3-Way Match\nGrid Synchronization COD`                            |    Yes    |   0   | Specifies mandatory operational event before fund disbursement.        |
| `custom_prerequisite_satisfied` | Prerequisite Satisfied     | `Check`        | -                                                                                                                                      |    No     |   1   | Programmatic boolean flag when prerequisite condition verified.        |
| `custom_prerequisite_doc_ref`   | Prerequisite Doc Reference | `Dynamic Link` | `custom_prerequisite_doc_type`                                                                                                         |    No     |   0   | Reference to verified document (e.g. `PR-2026-00042`).                 |
| `custom_prerequisite_doc_type`  | Prerequisite DocType       | `Link`         | `DocType`                                                                                                                              |    No     |   0   | Target DocType for dynamic reference.                                  |
| `custom_notification_t1_sent`   | T-1 Reminder Sent          | `Check`        | -                                                                                                                                      |    No     |   1   | Set to 1 by background daemon once T-1 alert sent.                     |
| `custom_notification_t1_time`   | T-1 Sent Timestamp         | `Datetime`     | -                                                                                                                                      |    No     |   0   | Timestamp of T-1 reminder dispatch.                                    |
| `custom_notification_t0_sent`   | T-0 Reminder Sent          | `Check`        | -                                                                                                                                      |    No     |   1   | Set to 1 by background daemon once T-0 alert sent.                     |
| `custom_notification_t0_time`   | T-0 Sent Timestamp         | `Datetime`     | -                                                                                                                                      |    No     |   0   | Timestamp of T-0 reminder dispatch.                                    |
| `custom_settlement_status`      | Settlement Status          | `Select`       | `Scheduled\nDue Tomorrow\nDue Today\nOverdue\nDisbursed\nOn Dispute Hold`                                                              |    Yes    |   1   | Dynamic operational state managed by daemon and observer.              |
| `custom_linked_payment_entry`   | Linked Payment Entry       | `Link`         | `Payment Entry`                                                                                                                        |    No     |   1   | Foreign key linking disbursed payment entry to schedule row.           |
| `custom_hold_reason`            | Hold Reason                | `Small Text`   | -                                                                                                                                      |    No     |   0   | Explanatory note if milestone flagged as `On Dispute Hold`.            |

### 3.2 Custom Field Extensions on `tabPayment Entry`

| Fieldname                       | Label                     | Fieldtype    | Options / Target | Mandatory | Index | Description & Operational Rules                                   |
| :------------------------------ | :------------------------ | :----------- | :--------------- | :-------: | :---: | :---------------------------------------------------------------- |
| `custom_po_milestone_ref`       | PO Milestone Schedule Row | `Data`       | -                |    No     |   1   | Row ID (`name`) of linked `tabPayment Schedule` row in source PO. |
| `custom_solar_project_ref`      | Solar Project Code        | `Link`       | `Project`        |    No     |   1   | Linked solar EPC project code for project cash flow tracking.     |
| `custom_purchase_team_notified` | Purchase Team Notified    | `Check`      | -                |    No     |   1   | Set to 1 when post-payment settlement alert dispatched.           |
| `custom_purchase_notified_at`   | Purchase Notified At      | `Datetime`   | -                |    No     |   0   | Timestamp when notification delivered to Purchase team.           |
| `custom_bank_utr_no`            | Bank UTR / Ref No         | `Data`       | -                |    No     |   1   | Bank transaction reference / UTR number entered by Accounts.      |
| `custom_disbursement_remarks`   | Disbursement Remarks      | `Small Text` | -                |    No     |   0   | Operational notes shared directly with Purchase team.             |

### 3.3 Custom Field Extensions on `tabSolar Notification Settings`

| Fieldname                               | Label                                     | Fieldtype |     Default      | Description & Governance Rules                                                |
| :-------------------------------------- | :---------------------------------------- | :-------- | :--------------: | :---------------------------------------------------------------------------- |
| `notify_vendor_payment_t_minus_1`       | Enable T-1 Payment Reminder (Day Before)  | `Check`   |        1         | Toggles morning alert to Purchase & Accounts 24h prior to milestone due date. |
| `notify_vendor_payment_t_zero`          | Enable T-0 Payment Reminder (Payment Day) | `Check`   |        1         | Toggles morning urgent alert to Purchase & Accounts on payment due date.      |
| `notify_purchase_on_payment_settlement` | Enable Instant Purchase Settlement Alert  | `Check`   |        1         | Toggles real-time alert to Purchase team upon `Payment Entry` submission.     |
| `vendor_payment_notification_hour`      | Daily Daemon Execution Hour (24h)         | `Int`     |        8         | Scheduled hour of day (default 08:00 AM) when daily cron runs.                |
| `vendor_payment_alert_channels`         | Active Alert Channels                     | `Select`  | `System & Email` | Options: `System In-App Only`, `System & Email`, `System, Email & WhatsApp`.  |

### 3.4 Relational Composite Indexes (Database Performance)

```sql
-- Composite index for T-1 / T-0 daily daemon scan on Payment Schedule
CREATE INDEX IF NOT EXISTS idx_payment_schedule_due_status
ON `tabPayment Schedule` (parenttype, due_date, custom_settlement_status);

-- Composite index for fast supplier payment workbench lookups
CREATE INDEX IF NOT EXISTS idx_payment_entry_supplier_party
ON `tabPayment Entry` (party_type, party, docstatus, posting_date);

-- Composite index for milestone tracking by project
CREATE INDEX IF NOT EXISTS idx_payment_entry_project_milestone
ON `tabPayment Entry` (custom_solar_project_ref, custom_po_milestone_ref);
```

---

## 4. State Machine, Verification Gates & Dual-Timer Notification Engine

### 4.1 Payment Obligation Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> Scheduled: PO / PI Submitted & Authorized
    Scheduled --> Due_Tomorrow: Daily Daemon at 08:00 AM (Due Date = Today + 1)
    Due_Tomorrow --> Due_Today: Daily Daemon at 08:00 AM (Due Date = Today)
    Scheduled --> Due_Today: Direct Maturity (Zero Lead Time)

    Due_Today --> Disbursed: Accounts Submits Payment Entry (Purchase Auto-Notified)
    Due_Tomorrow --> Disbursed: Early Disbursement by Accounts
    Scheduled --> Disbursed: Advance Paid Prior to Scheduled Window

    Due_Today --> Overdue: Due Date Passed with No Payment Entry
    Overdue --> Disbursed: Delayed Payment + Mandatory Delay Log Entry

    Scheduled --> On_Dispute_Hold: Quality Issue / Missing Documents Flagged
    Due_Tomorrow --> On_Dispute_Hold: Hold Placed by Purchase / Accounts Lead
    Due_Today --> On_Dispute_Hold: Hold Placed by Purchase / Accounts Lead
    On_Dispute_Hold --> Scheduled: Dispute Resolved & Hold Released

    Disbursed --> [*]: Closed-Loop Confirmation Complete
```

### 4.2 Hard Verification Gates

- **Gate 1: Milestone Prerequisite Verification Gate:**
  - `Advance (Pre-Dispatch)`: Requires linked `Purchase Order` submitted (`docstatus = 1`).
  - `Against LR / Inspection`: Requires `custom_prerequisite_satisfied = 1` with uploaded Transporter LR and FAT sign-off.
  - `On Delivery (GRN)`: Requires linked `Purchase Receipt` submitted and `custom_3way_match_status = 'Match Passed'`.
  - `Retention / PBG Release`: Requires linked `tabLiaisoning And Synchronization` COD or attached PBG doc.
- **Gate 2: Statutory Tax Compliance Gate (TDS u/s 194Q):**
  - Asserts 0.1% TDS deduction item present in `Payment Entry` if cumulative vendor purchases exceed ₹50 Lakhs in fiscal year.
- **Gate 3: Verified Supplier Bank Details Gate:**
  - Asserts bank account in `Payment Entry` matches active, verified `Bank Account` (`custom_is_verified = 1`).

---

## 5. Controller Logic, Domain Services & Whitelisted APIs

### 5.1 Domain Service Layer Architecture

#### 1. `VendorPaymentNotificationDaemon` (Proactive Daily Alerts)

```python
# solar_module/sitemanagement/domain/vendor_payment_notification_daemon.py

import frappe
from frappe import _
from frappe.utils import nowdate, add_days, getdate, format_date

class VendorPaymentNotificationDaemon:
    """
    Scheduled daemon executing daily (default 08:00 AM) to evaluate all open
    vendor payment obligations and dispatch synchronized T-1 and T-0 alerts
    to both Purchase and Accounts teams.
    """

    @classmethod
    def execute_daily_evaluations(cls):
        settings = frappe.get_cached_doc("Solar Notification Settings")
        today = getdate(nowdate())
        tomorrow = add_days(today, 1)

        # 1. Evaluate T-1 Day Reminders (Due Tomorrow)
        if settings.notify_vendor_payment_t_minus_1:
            cls._process_reminders_for_date(
                target_date=tomorrow,
                reminder_type="T-1",
                flag_field="custom_notification_t1_sent",
                timestamp_field="custom_notification_t1_time"
            )

        # 2. Evaluate T-0 Day Reminders (Due Today)
        if settings.notify_vendor_payment_t_zero:
            cls._process_reminders_for_date(
                target_date=today,
                reminder_type="T-0",
                flag_field="custom_notification_t0_sent",
                timestamp_field="custom_notification_t0_time"
            )

        # 3. Update Overdue States
        cls._mark_overdue_obligations(today)

    @classmethod
    def _process_reminders_for_date(cls, target_date, reminder_type: str, flag_field: str, timestamp_field: str):
        query = """
            SELECT
                ps.name AS schedule_row_id,
                ps.parent AS parent_doc,
                ps.parenttype AS parent_type,
                ps.due_date,
                ps.payment_amount,
                ps.custom_milestone_type,
                ps.custom_prerequisite_satisfied,
                parent_tab.supplier,
                parent_tab.company,
                parent_tab.custom_project_ref
            FROM `tabPayment Schedule` ps
            INNER JOIN `tab{parent_type}` parent_tab ON parent_tab.name = ps.parent
            WHERE ps.parenttype IN ('Purchase Order', 'Purchase Invoice')
              AND ps.due_date = %(target_date)s
              AND ps.{flag_field} = 0
              AND ps.custom_settlement_status NOT IN ('Disbursed', 'On Dispute Hold')
              AND parent_tab.docstatus = 1
        """

        for p_type in ["Purchase Order", "Purchase Invoice"]:
            formatted_query = query.replace("{parent_type}", p_type)
            records = frappe.db.sql(formatted_query, {"target_date": target_date}, as_dict=True)

            for row in records:
                cls._dispatch_dual_notifications(row, reminder_type)
                frappe.db.set_value("Payment Schedule", row.schedule_row_id, {
                    flag_field: 1,
                    timestamp_field: frappe.utils.now_datetime(),
                    "custom_settlement_status": "Due Tomorrow" if reminder_type == "T-1" else "Due Today"
                }, update_modified=False)

    @classmethod
    def _dispatch_dual_notifications(cls, row: dict, reminder_type: str):
        urgency = "URGENT: " if reminder_type == "T-0" else "UPCOMING: "
        subject = _("{0} Supplier Payment Due {1}: {2} (INR {3:,.2f})").format(
            urgency,
            "TODAY" if reminder_type == "T-0" else "TOMORROW",
            row.supplier,
            row.payment_amount
        )

        message = _(
            "<b>Vendor Payment Reminder ({0})</b><br>"
            "<b>Supplier:</b> {1}<br>"
            "<b>Milestone:</b> {2}<br>"
            "<b>Amount:</b> INR {3:,.2f}<br>"
            "<b>Due Date:</b> {4}<br>"
            "<b>Document:</b> {5} ({6})<br>"
            "<b>Project:</b> {7}<br>"
            "<b>Prerequisite Satisfied:</b> {8}"
        ).format(
            reminder_type,
            row.supplier,
            row.custom_milestone_type or "General Due Date",
            row.payment_amount,
            format_date(row.due_date),
            row.parent_doc,
            row.parent_type,
            row.custom_project_ref or "Central Inventory",
            "YES" if row.custom_prerequisite_satisfied else "NO (Action Required)"
        )

        recipients = cls._get_stakeholder_recipients(row)
        for user_id in recipients:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": subject,
                "email_content": message,
                "for_user": user_id,
                "type": "Alert",
                "document_type": row.parent_type,
                "document_name": row.parent_doc
            }).insert(ignore_permissions=True)

    @classmethod
    def _get_stakeholder_recipients(cls, row: dict) -> set:
        users = set()
        accounts_users = frappe.get_all("Has Role", filters={"role": ["in", ["Accounts Manager", "Accounts Assistant"]]}, fields=["parent"])
        users.update([u.parent for u in accounts_users])

        purchase_users = frappe.get_all("Has Role", filters={"role": ["in", ["Purchase Manager", "Purchase Assistant"]]}, fields=["parent"])
        users.update([u.parent for u in purchase_users])

        if row.get("custom_project_ref"):
            proj_user = frappe.db.get_value("Project", row["custom_project_ref"], "custom_project_engineer")
            if proj_user:
                users.add(proj_user)

        return users

    @classmethod
    def _mark_overdue_obligations(cls, today):
        frappe.db.sql("""
            UPDATE `tabPayment Schedule`
            SET custom_settlement_status = 'Overdue'
            WHERE due_date < %(today)s
              AND custom_settlement_status NOT IN ('Disbursed', 'On Dispute Hold', 'Overdue')
        """, {"today": today})
```

#### 2. `VendorPaymentSettlementService` (Closed-Loop Settlement Observer)

```python
# solar_module/sitemanagement/domain/vendor_payment_settlement_service.py

import frappe
from frappe import _
from frappe.utils import format_date

class VendorPaymentSettlementService:
    """
    Event-driven observer bound to `Payment Entry.on_submit`.
    Automatically reconciles payment milestones and dispatches instant
    closed-loop settlement notifications to the Purchase Team.
    """

    @classmethod
    def on_payment_submitted(cls, doc):
        if doc.payment_type != "Pay" or doc.party_type != "Supplier":
            return

        supplier = doc.party
        paid_amount = doc.paid_amount
        reference_no = doc.reference_no or doc.name
        posting_date = doc.posting_date

        for ref in doc.references:
            if ref.reference_doctype == "Purchase Order":
                cls._handle_po_disbursement(doc, ref)
            elif ref.reference_doctype == "Purchase Invoice":
                cls._handle_pi_disbursement(doc, ref)

    @classmethod
    def _handle_po_disbursement(cls, doc, ref):
        po_doc = frappe.get_doc("Purchase Order", ref.reference_name)

        schedule_updated = False
        for row in po_doc.payment_schedule:
            if row.custom_settlement_status != "Disbursed" and not schedule_updated:
                row.custom_settlement_status = "Disbursed"
                row.custom_linked_payment_entry = doc.name
                schedule_updated = True

        po_doc.flags.ignore_validate_update_after_submit = True
        po_doc.save(ignore_permissions=True)

        cls._broadcast_settlement_to_purchase(
            doc=doc,
            parent_type="Purchase Order",
            parent_name=ref.reference_name,
            supplier=doc.party,
            allocated_amount=ref.allocated_amount,
            remaining_balance=ref.outstanding_amount,
            project_code=po_doc.get("custom_project_ref")
        )

    @classmethod
    def _handle_pi_disbursement(cls, doc, ref):
        pi_doc = frappe.get_doc("Purchase Invoice", ref.reference_name)

        schedule_updated = False
        for row in pi_doc.payment_schedule:
            if row.custom_settlement_status != "Disbursed" and not schedule_updated:
                row.custom_settlement_status = "Disbursed"
                row.custom_linked_payment_entry = doc.name
                schedule_updated = True

        pi_doc.flags.ignore_validate_update_after_submit = True
        pi_doc.save(ignore_permissions=True)

        cls._broadcast_settlement_to_purchase(
            doc=doc,
            parent_type="Purchase Invoice",
            parent_name=ref.reference_name,
            supplier=doc.party,
            allocated_amount=ref.allocated_amount,
            remaining_balance=ref.outstanding_amount,
            project_code=pi_doc.get("custom_project_ref")
        )

    @classmethod
    def _broadcast_settlement_to_purchase(cls, doc, parent_type: str, parent_name: str, supplier: str, allocated_amount: float, remaining_balance: float, project_code: str):
        settings = frappe.get_cached_doc("Solar Notification Settings")
        if not settings.notify_purchase_on_payment_settlement:
            return

        subject = _("✔ Payment Completed: {0} for {1} (INR {2:,.2f})").format(
            parent_name, supplier, allocated_amount
        )

        message = _(
            "<b>Vendor Payment Completed by Accounts</b><br>"
            "<b>Supplier:</b> {0}<br>"
            "<b>Reference Document:</b> {1} ({2})<br>"
            "<b>Disbursed Amount:</b> INR {3:,.2f}<br>"
            "<b>Bank UTR / Ref No:</b> {4}<br>"
            "<b>Payment Mode:</b> {5}<br>"
            "<b>Instrument Date:</b> {6}<br>"
            "<b>Remaining Balance:</b> INR {7:,.2f}<br>"
            "<b>Payment Voucher:</b> {8}<br>"
            "<i>Procurement team may proceed with supplier dispatch clearance.</i>"
        ).format(
            supplier,
            parent_name,
            parent_type,
            allocated_amount,
            doc.reference_no or "Direct Bank Transfer",
            doc.mode_of_payment,
            format_date(doc.posting_date),
            remaining_balance,
            doc.name
        )

        purchase_users = frappe.get_all("Has Role", filters={"role": ["in", ["Purchase Manager", "Purchase Assistant"]]}, fields=["parent"])
        recipients = {u.parent for u in purchase_users}

        if project_code:
            eng = frappe.db.get_value("Project", project_code, "custom_project_engineer")
            if eng:
                recipients.add(eng)

        for user_id in recipients:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": subject,
                "email_content": message,
                "for_user": user_id,
                "type": "Alert",
                "document_type": "Payment Entry",
                "document_name": doc.name
            }).insert(ignore_permissions=True)

        doc.db_set("custom_purchase_team_notified", 1)
        doc.db_set("custom_purchase_notified_at", frappe.utils.now_datetime())
```

### 5.2 Whitelisted API Endpoints

```python
# solar_module/api/payment_monitoring.py

import json
import frappe
from frappe import _
from frappe.utils import nowdate, add_days

@frappe.whitelist(methods=["POST"])
def get_upcoming_vendor_payments(department: str = "Purchase", time_horizon_days: int = 30) -> dict:
    frappe.has_permission("Purchase Order", "read", throw=True)
    today = nowdate()
    future_date = add_days(today, int(time_horizon_days))

    query = """
        SELECT
            ps.name AS milestone_id,
            ps.parent AS parent_doc,
            ps.parenttype AS parent_type,
            ps.due_date,
            ps.payment_amount,
            ps.custom_milestone_type,
            ps.custom_prerequisite_required,
            ps.custom_prerequisite_satisfied,
            ps.custom_settlement_status,
            p.supplier,
            p.custom_project_ref AS project,
            sup.supplier_name
        FROM `tabPayment Schedule` ps
        INNER JOIN `tabPurchase Order` p ON p.name = ps.parent AND ps.parenttype = 'Purchase Order'
        INNER JOIN `tabSupplier` sup ON sup.name = p.supplier
        WHERE ps.due_date BETWEEN %(today)s AND %(future_date)s
          AND ps.custom_settlement_status != 'Disbursed'
          AND p.docstatus = 1
        ORDER BY ps.due_date ASC
    """

    obligations = frappe.db.sql(query, {"today": today, "future_date": future_date}, as_dict=True)

    summary = {
        "due_today_count": sum(1 for o in obligations if str(o.due_date) == str(today)),
        "due_today_amount": sum(o.payment_amount for o in obligations if str(o.due_date) == str(today)),
        "due_tomorrow_count": sum(1 for o in obligations if str(o.due_date) == str(add_days(today, 1))),
        "due_tomorrow_amount": sum(o.payment_amount for o in obligations if str(o.due_date) == str(add_days(today, 1))),
        "total_upcoming_amount": sum(o.payment_amount for o in obligations),
        "obligations": obligations
    }
    return summary

@frappe.whitelist(methods=["POST"])
def nudge_accounts_team(milestone_id: str, urgency_note: str) -> dict:
    doc = frappe.get_doc("Payment Schedule", milestone_id)
    parent_doc = frappe.get_doc(doc.parenttype, doc.parent)
    parent_doc.check_permission("read")

    sender = frappe.session.user
    accounts_users = frappe.get_all("Has Role", filters={"role": "Accounts Manager"}, fields=["parent"])

    subject = _("⚡ Procurement Priority Nudge: Payment Needed for {0}").format(parent_doc.supplier)
    message = _(
        "<b>Procurement Nudge from {0}</b><br>"
        "<b>Supplier:</b> {1}<br>"
        "<b>Milestone:</b> {2} (INR {3:,.2f})<br>"
        "<b>Reference:</b> {4}<br>"
        "<b>Note from Purchase:</b> {5}<br>"
        "<i>Supplier is holding dispatch pending payment clearance.</i>"
    ).format(sender, parent_doc.supplier, doc.custom_milestone_type, doc.payment_amount, parent_doc.name, urgency_note)

    for acc_user in accounts_users:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": subject,
            "email_content": message,
            "for_user": acc_user.parent,
            "type": "Alert",
            "document_type": doc.parenttype,
            "document_name": doc.parent
        }).insert(ignore_permissions=True)

    return {"status": "success", "message": _("Accounts team notified successfully")}
```

---

## 6. Frontend UI/UX Specification

### 6.1 Purchase Workspace Upcoming Payments Section (`/solar/procurement`)

Card section focused on dispatch blockers and prerequisite readiness.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ▼ UPCOMING SUPPLIER MILESTONE PAYMENTS (PURCHASE DESK)                 [Filter: Next 14 Days ▼] │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Summary: 3 Due Today (₹18.4L) | 2 Due Tomorrow (₹6.5L) | 1 Dispatched Today (₹42.0L)            │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Supplier Name       Milestone Type      Amount (INR)   Due Date    Prerequisites     Action      │
│ ─────────────────   ─────────────────   ────────────   ──────────  ───────────────   ──────────  │
│ Waaree Energies     Advance (15%)       ₹14,25,000.00  TODAY       [✔ PO Signed]     [Nudge]     │
│ Sungrow Inverters   Against LR (70%)    ₹18,50,000.00  TOMORROW    [✔ LR Uploaded]   [Details]   │
│ Tata Power Solar    Post-GRN (10%)       ₹4,20,000.00  2026-09-28  [✔ 3-Way Match]   [Details]   │
│ Rayzon Solar        Retention (5%)       ₹2,10,000.00  2026-10-15  [⏳ Pending COD]   [Hold]     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Traffic light status badges (`[✔ PO Signed]`, `[✔ LR Uploaded]`, `[⏳ Pending COD]`).
- `[Nudge Accounts]` button opens modal to send urgent push alert with operational reason.

### 6.2 Accounts Workspace Upcoming Payments Section (`/solar/accounts`)

Card section focused on liquidity horizons, TDS deductions, and bank payouts.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ▼ UPCOMING VENDOR DISBURSEMENTS (FINANCE & ACCOUNTS)                  [View: Liquidity Horizon ▼]│
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Cash Forecast: Today: ₹18.40L | Tomorrow: ₹6.50L | This Week: ₹54.20L | 30-Day Total: ₹1.82 Cr   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Supplier Name       Document Ref   TDS (194Q)    Net Payable     Due Status       Action         │
│ ─────────────────   ────────────   ──────────    ───────────     ───────────      ────────────── │
│ Waaree Energies     PO-2026-0012   ₹1,425.00     ₹14,23,575.00   [DUE TODAY]      [Pay Now]      │
│ Sungrow Inverters   PO-2026-0015   ₹1,850.00     ₹18,48,150.00   [DUE TOMORROW]   [Prepare Entry]│
│ Polycab India Ltd   PI-2026-0089     ₹450.00      ₹4,49,550.00   [Due in 4 Days]  [Schedule]     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- `[Pay Now]` launches pre-filled `Payment Entry` dialog.

### 6.3 Joint Collaborative Vendor Payment Workbench (`/solar/procurement/payment-workbench`)

Full-screen interactive matrix with filters for Project, Equipment Category, Milestone Type, and Status. Side drawer for real-time inter-department communication logs.

---

## 7. Cross-App Integration Touchpoints

- **ERPNext Buying:** `tabPurchase Order`, `tabPurchase Receipt`, `tabSupplier`.
- **ERPNext Accounts:** `tabPayment Entry`, `tabPayment Schedule`, General Ledger.
- **Frappe Framework:** `tabNotification Log`, Redis queues, Email/WhatsApp alerts.
- **Frappe HRMS:** Links users to `Procurement & SCM` and `Finance & Accounts` departments.

---

## 8. Automated Testing & QA Criteria

Zero-Commit Rule (`frappe.db.rollback()`, zero `frappe.db.commit()`).

```python
# solar_module/tests/test_step_18_vendor_payment_workbench.py

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days
from solar_module.sitemanagement.domain.vendor_payment_notification_daemon import VendorPaymentNotificationDaemon
from solar_module.sitemanagement.domain.vendor_payment_settlement_service import VendorPaymentSettlementService

class TestStep18VendorPaymentWorkbench(FrappeTestCase):

    def setUp(self):
        super().setUp()
        self._setup_test_prerequisites()

    def _setup_test_prerequisites(self):
        if not frappe.db.exists("Supplier", "_Test Solar PV Supplier"):
            self.supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": "_Test Solar PV Supplier",
                "supplier_group": "Solar Hardware"
            }).insert(ignore_permissions=True)
        else:
            self.supplier = frappe.get_doc("Supplier", "_Test Solar PV Supplier")

    def test_01_daemon_dispatches_t1_notification(self):
        """Assert daemon dispatches T-1 alert one day before due date to both teams."""
        tomorrow = add_days(nowdate(), 1)

        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": self.supplier.name,
            "company": "_Test Company",
            "schedule_date": add_days(nowdate(), 10),
            "items": [{"item_code": "_Test Item", "qty": 10, "rate": 1000}],
            "payment_schedule": [{
                "due_date": tomorrow,
                "payment_amount": 10000,
                "custom_milestone_type": "Advance (Pre-Dispatch)",
                "custom_prerequisite_satisfied": 1
            }]
        }).insert(ignore_permissions=True)
        po.submit()

        VendorPaymentNotificationDaemon.execute_daily_evaluations()

        schedule_row = frappe.db.get_value(
            "Payment Schedule",
            {"parent": po.name, "due_date": tomorrow},
            ["custom_notification_t1_sent", "custom_settlement_status"],
            as_dict=True
        )
        self.assertEqual(schedule_row.custom_notification_t1_sent, 1)
        self.assertEqual(schedule_row.custom_settlement_status, "Due Tomorrow")

    def test_02_daemon_dispatches_t0_notification(self):
        """Assert daemon dispatches urgent T-0 alert on payment due date to both teams."""
        today = nowdate()

        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": self.supplier.name,
            "company": "_Test Company",
            "schedule_date": add_days(nowdate(), 5),
            "items": [{"item_code": "_Test Item", "qty": 5, "rate": 2000}],
            "payment_schedule": [{
                "due_date": today,
                "payment_amount": 10000,
                "custom_milestone_type": "Against LR / Inspection",
                "custom_prerequisite_satisfied": 1
            }]
        }).insert(ignore_permissions=True)
        po.submit()

        VendorPaymentNotificationDaemon.execute_daily_evaluations()

        schedule_row = frappe.db.get_value(
            "Payment Schedule",
            {"parent": po.name, "due_date": today},
            ["custom_notification_t0_sent", "custom_settlement_status"],
            as_dict=True
        )
        self.assertEqual(schedule_row.custom_notification_t0_sent, 1)
        self.assertEqual(schedule_row.custom_settlement_status, "Due Today")

    def test_03_payment_entry_submission_alerts_purchase_team(self):
        """Assert submitting Payment Entry triggers instant settlement alert to Purchase."""
        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": self.supplier.name,
            "company": "_Test Company",
            "schedule_date": add_days(nowdate(), 7),
            "items": [{"item_code": "_Test Item", "qty": 10, "rate": 5000}],
            "payment_schedule": [{
                "due_date": nowdate(),
                "payment_amount": 50000,
                "custom_milestone_type": "Advance (Pre-Dispatch)"
            }]
        }).insert(ignore_permissions=True)
        po.submit()

        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": self.supplier.name,
            "company": "_Test Company",
            "paid_amount": 50000,
            "received_amount": 50000,
            "paid_from": "_Test Bank - _TC",
            "paid_to": "Creditors - _TC",
            "reference_no": "UTR-TEST-998877",
            "references": [{
                "reference_doctype": "Purchase Order",
                "reference_name": po.name,
                "total_amount": 50000,
                "allocated_amount": 50000
            }]
        }).insert(ignore_permissions=True)
        pe.submit()

        pe_reloaded = frappe.get_doc("Payment Entry", pe.name)
        self.assertEqual(pe_reloaded.custom_purchase_team_notified, 1)

        po_schedule = frappe.db.get_value(
            "Payment Schedule",
            {"parent": po.name},
            ["custom_settlement_status", "custom_linked_payment_entry"],
            as_dict=True
        )
        self.assertEqual(po_schedule.custom_settlement_status, "Disbursed")
        self.assertEqual(po_schedule.custom_linked_payment_entry, pe.name)
```

---

## 9. Operational SOP, Error Resolution & Runbook

### 9.1 End-User Standard Operating Procedures (SOP)

#### For Purchase Assistant / Purchase Manager:

1. Review impending obligations in `/solar` Upcoming Payments card.
2. Verify milestone prerequisites (LR, inspection report, PO sign-off).
3. If vendor holds loading, click `[Nudge Accounts]` with urgency explanation.
4. On settlement notification, confirm UTR and release factory dispatch clearance.

#### For Accounts Assistant / Accounts Manager:

1. At 08:00 AM, inspect T-1 / T-0 alerts and Accounts Upcoming Payments section.
2. Click `[Pay Now]` to prepare payment voucher; verify bank balance and 194Q TDS deduction.
3. Submit `Payment Entry` with bank UTR; system automatically updates milestone and notifies Purchase.

### 9.2 Operational Error Resolution Matrix

| Error Condition / Message                                 | Root Cause                                                                     | Operator Resolution Path                                                           |
| :-------------------------------------------------------- | :----------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| `ValidationError: Prerequisite Unsatisfied for Milestone` | Milestone requires operational doc (LR, 3-Way Match) not yet uploaded/cleared. | Purchase Assistant uploads prerequisite document or completes GRN inspection.      |
| `PermissionError: Not Authorized to Submit Payment Entry` | User lacks `Accounts Manager` or `Admin` role.                                 | Submit voucher as Draft for approval by authorized `Accounts Manager`.             |
| `Missing Bank Verification: Target Account Unverified`    | Supplier bank account altered within 48h or lacks verification flag.           | `Admin` and `Accounts Manager` verify bank proof and set `custom_is_verified = 1`. |
| `TDS Deduction Missing: Supplier Exceeds ₹50L Threshold`  | Section 194Q requires 0.1% TDS on cumulative purchases $> ₹50\text{L}$.        | Add TDS deduction line to `Payment Entry` or attach Section 197 certificate.       |

### 9.3 L3 DevOps Runbook & Daemon Maintenance

```bash
# Check worker health
bench --site <site_name> doctor
bench --site <site_name> show-pending-jobs

# Manual execution of daily notification daemon
bench --site <site_name> execute solar_module.sitemanagement.domain.vendor_payment_notification_daemon.VendorPaymentNotificationDaemon.execute_daily_evaluations

# Inspect generated notifications
bench --site <site_name> mariadb -e "SELECT name, for_user, subject, creation FROM \`tabNotification Log\` WHERE creation >= CURDATE() AND subject LIKE '%Supplier Payment Due%' ORDER BY creation DESC LIMIT 10;"
```

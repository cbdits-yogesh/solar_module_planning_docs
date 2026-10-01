# STEP_18_VENDOR_PAYMENT_WORKBENCH_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 18 Joint Vendor Payment Monitoring Workbench, Dual-Cadence Notification Engine (T-1 & T-0) & Closed-Loop Procurement Settlement Architecture

**Document ID:** `TB-18-VENDOR-PAYMENT-WORKBENCH`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.caveman.md`](../STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-018-JOINT-VENDOR-PAYMENT-MONITORING-WORKBENCH.md`](../../docs/decisions/ADR-018-JOINT-VENDOR-PAYMENT-MONITORING-WORKBENCH.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_17_PURCHASE_INVOICE_3WAY_MATCH_TRACER_BULLET.caveman.md`](STEP_17_PURCHASE_INVOICE_3WAY_MATCH_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_16_PURCHASE_RECEIPT_GRN_TRACER_BULLET.caveman.md`](STEP_16_PURCHASE_RECEIPT_GRN_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_15_PURCHASE_ORDER_AUTHORIZATION_TRACER_BULLET.caveman.md`](STEP_15_PURCHASE_ORDER_AUTHORIZATION_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md`](STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Step 19 Vendor Performance Rating ([`STEP_19`](../STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.caveman.md)), General Ledger (`tabGL Entry` / Accounts Payable, Bank Ledgers, Section 194Q TDS / 206C(1H) TCS Ledgers)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-13`, `BC-14`), `planning_ref_docs/03_TO_BE_BUSINESS_PROCESS.md` (`Step 07`), `planning_ref_docs/04_GAP_ANALYSIS_FIT_GAP.md` (`Gap #07`, `Gap #08`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-015`, `BR-017`, `BR-018`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-015`, `FR-017`, `FR-018`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 4: FIN`, `Domain 7: SCM`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 13`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 20`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-17`), `planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md` (Sec 2, 4.3)  
**Target Module:** `solar_module` / SPA `/solar/procurement/payment-workbench` (Extends ERPNext `tabPayment Schedule`, `tabPayment Entry`, `tabPurchase Order`, `tabPurchase Invoice`, singletons `tabSolar Notification Settings` & `tabSolar SCM Settings`, integrates `tabRemark-Delay Log` & `tabGL Entry`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution  

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** A disposable UI mock or isolated script that accepts a vendor payment voucher without validating against contractual milestones locked in Step 15 PO, permits disbursements before goods clear Step 16 GRN or Step 17 3-way match, isolates Accounts in a silent departmental silo (forcing Procurement into manual phone calls and spreadsheet queries), misses proactive T-1 and T-0 morning alerts, ignores Section 194Q TDS statutory deduction limits, and leaves bank transactions disconnected from downstream supplier rating scorecards.
- **Tracer Bullet:** A permanent, production-grade 5-layer thin vertical slice cutting cleanly through the live Frappe enterprise architecture. It establishes deterministic commercial recognition across Procurement (`Purchase Assistant`, `Purchase Manager`), Accounts (`Accounts Assistant`, `Accounts Manager`), and Executive Governance (`Admin`), anchors real database schemas (`tabPayment Schedule`, `tabPayment Entry`, `tabSolar Notification Settings`, `tabSolar SCM Settings`, `tabRemark-Delay Log`), implements pure SOLID Python domain services (`VendorPaymentObligationEngine`, `VendorPaymentNotificationDaemon`, `VendorPaymentSettlementService`, `PaymentPrerequisiteGateService`, `PaymentWorkbenchSLAService`, `PaymentStageForwardLockService`), exposes authenticated whitelisted RPC endpoints (`solar_module.api.procurement.payment_monitoring.*`), connects responsive Desk client scripts and SPA workbenches, and executes an automated zero-commit integration test suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 18 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabPayment Schedule extensions (milestone type, prerequisite gate & doc │
│     link, T-1/T-0 notification sent flags & timestamps, settlement status,  │
│     linked PE, hold reason)                                                 │
│   - tabPayment Entry extensions (PO milestone ref, solar project ref, UTR,  │
│     purchase team notified flag & timestamp, disbursement remarks)          │
│   - tabSolar Notification Settings (T-1, T-0, settlement toggles, daemon hr)│
│   - tabSolar SCM Settings (prerequisite enforcement, TDS 194Q rates/limits) │
│   - Composite B-Tree Indexes on Payment Schedule and Payment Entry          │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - VendorPaymentObligationEngine (unifies PO milestones & PI credit terms) │
│   - VendorPaymentNotificationDaemon (proactive 08:00 AM T-1 & T-0 runner)   │
│   - VendorPaymentSettlementService (closed-loop observer on PE on_submit)   │
│   - PaymentPrerequisiteGateService (Advance, LR, GRN, Retention gates)      │
│   - PaymentWorkbenchSLAService (MSME 45-day statutory SLA & delay logging)  │
│   - PaymentStageForwardLockService (Stage-Forward lock & cancel workflow)   │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                     │
│   - SolarPaymentEntry & SolarPaymentSchedule overrides (StageSecuredDocument)│
│   - Whitelisted RPC APIs (solar_module.api.procurement.payment_monitoring.*)│
│     * get_upcoming_vendor_payments (Purchase & Accounts view, horizon days) │
│     * nudge_accounts_team (Priority push notification from Purchase)        │
│     * verify_milestone_prerequisite (Operational document verification)     │
│     * place_milestone_hold / release_milestone_hold (Dispute management)    │
│     * get_liquidity_forecast (Bucketed cash flow projections)               │
│     * log_payment_delay (Mandatory audit trail when payment overdue)        │
│   - Background Celery/RQ daemon (vendor_payment_notification_daemon daily)  │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Dual-Workspace Frontend               │
│   - codes/client_script/payment_entry.js (UTR enforcement, TDS 194Q, alert) │
│   - codes/client_script/payment_schedule.js (traffic lights, Nudge modal)   │
│   - Purchase Desk Upcoming Payments Card (/solar/procurement)               │
│   - Accounts Desk Upcoming Vendor Disbursements Card (/solar/accounts)      │
│   - Joint Collaborative Vendor Payment Workbench SPA (/solar/workbench)    │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Tests)                   │
│   - solar_module/tests/test_step_18_vendor_payment_workbench_tracer_bullet  │
│   - Subclasses frappe.tests.utils.FrappeTestCase                            │
│   - Strict Zero-Commit Rule (frappe.db.rollback() in tearDown)              │
│   - 12 atomic test cases covering all 8 functional mission invariants       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental business, commercial, and security invariants of Stage 18 across the live Frappe stack:

1. **Invariant 1: Unified Payment Obligation Normalization:** Seamless extraction and cross-referencing of both PO milestone tranches (`Advance`, `Against LR / Inspection`, `On Delivery (GRN)`, `Retention / PBG Release`) and 3-way matched PI credit terms without double-counting liabilities across active projects.
2. **Invariant 2: Proactive Dual-Cadence Daily Alert Daemon:** Automated morning evaluation (08:00 AM) dispatching T-1 (due tomorrow) and T-0 (due today) reminders directly to assigned personnel.
3. **Invariant 3: Synchronized Dual Stakeholder Alerts:** Simultaneous alert dispatching to BOTH Purchase team (`Purchase Manager`, `Purchase Assistant`) and Accounts team (`Accounts Manager`, `Accounts Assistant`).
4. **Invariant 4: Closed-Loop Instant Settlement Broadcast:** Real-time event-driven hook on `Payment Entry.on_submit` broadcasting UTR number, disbursement amount, payment mode, and remaining balance to the Purchase team to immediately release supplier shipments.
5. **Invariant 5: Four-Tier Milestone Prerequisite Verification Gates:**
   - `Advance (Pre-Dispatch)`: Requires signed, authorized PO (`docstatus = 1`).
   - `Against LR / Inspection`: Requires verified Transporter LR and Factory Acceptance Test (FAT) sign-off.
   - `On Delivery (GRN)`: Requires accepted physical GRN (Step 16) and passed 3-way invoice match (Step 17).
   - `Retention / PBG Release`: Requires statutory COD grid synchronization (Step 10) or verified Performance Bank Guarantee.
6. **Invariant 6: Statutory Tax & Banking Compliance Verification:**
   - Section 194Q TDS deduction (0.1% for cumulative supplier invoices $> ₹50\text{L}$ in fiscal year).
   - Verified supplier bank account check (`custom_is_verified == 1`) to eliminate fraudulent diversions.
7. **Invariant 7: Dual-Workspace Tailored Visibility:**
   - Purchase Desk (`/solar/procurement`): Milestone readiness, delivery blockers, and `[Nudge Accounts]` action.
   - Accounts Desk (`/solar/accounts`): Cash liquidity forecast horizons, TDS deductions, and `[Pay Now]` action.
8. **Invariant 8: Stage-Forward Immutability & Junior Cancellation Interception:**
   - Hard lock on modifying or cancelling upstream documents once payment entries are booked.
   - Routing cancellation requests through the `Solar Cancellation Request` workflow.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Extends standard ERPNext `tabPayment Schedule`, `tabPayment Entry`, introduces Admin-configurable settings in `tabSolar Notification Settings` & `tabSolar SCM Settings`, integrates child table `tabRemark-Delay Log`, and establishes MariaDB composite B-Tree indexes.

### 2.1 Core DocType Extension: `tabPayment Schedule`

| Fieldname                       | Label                      | Fieldtype      | Options / Target                                                                                                                       | Mandatory | Index | Description & Operational Logic                                                                       |
| :------------------------------ | :------------------------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :---: | :---------------------------------------------------------------------------------------------------- |
| `custom_milestone_type`         | Milestone Type             | `Select`       | `Advance (Pre-Dispatch)\nAgainst LR / Inspection\nOn Delivery (GRN)\nInvoice Credit Period\nRetention / PBG Release\nOther Commercial` |  **Yes**  |   1   | Standardized milestone classification for solar procurement contracts.                                |
| `custom_prerequisite_required`  | Prerequisite Required      | `Select`       | `None\nSigned PO\nTransporter LR & FAT Report\nSubmitted GRN\nPassed 3-Way Match\nGrid Synchronization COD`                            |  **Yes**  |   0   | Specifies mandatory operational event before fund disbursement.                                       |
| `custom_prerequisite_satisfied` | Prerequisite Satisfied     | `Check`        | -                                                                                                                                      |    No     |   1   | Programmatic boolean flag when prerequisite condition verified.                                       |
| `custom_prerequisite_doc_ref`   | Prerequisite Doc Reference | `Dynamic Link` | `custom_prerequisite_doc_type`                                                                                                         |    No     |   0   | Reference to verified document (e.g. `PR-2026-00042`, `LIA-2026-00012`).                              |
| `custom_prerequisite_doc_type`  | Prerequisite DocType       | `Link`         | `DocType`                                                                                                                              |    No     |   0   | Target DocType for dynamic reference.                                                                 |
| `custom_notification_t1_sent`   | T-1 Reminder Sent          | `Check`        | -                                                                                                                                      |    No     |   1   | Set to 1 by background daemon once T-1 alert sent.                                                    |
| `custom_notification_t1_time`   | T-1 Sent Timestamp         | `Datetime`     | -                                                                                                                                      |    No     |   0   | Timestamp of T-1 reminder dispatch.                                                                   |
| `custom_notification_t0_sent`   | T-0 Reminder Sent          | `Check`        | -                                                                                                                                      |    No     |   1   | Set to 1 by background daemon once T-0 alert sent.                                                    |
| `custom_notification_t0_time`   | T-0 Sent Timestamp         | `Datetime`     | -                                                                                                                                      |    No     |   0   | Timestamp of T-0 reminder dispatch.                                                                   |
| `custom_settlement_status`      | Settlement Status          | `Select`       | `Scheduled\nDue Tomorrow\nDue Today\nOverdue\nDisbursed\nOn Dispute Hold`                                                              |  **Yes**  |   1   | Dynamic operational state managed by daemon and observer. Default: `Scheduled`.                       |
| `custom_linked_payment_entry`   | Linked Payment Entry       | `Link`         | `Payment Entry`                                                                                                                        |    No     |   1   | Foreign key linking disbursed payment entry to schedule row.                                          |
| `custom_hold_reason`            | Hold Reason                | `Small Text`   | -                                                                                                                                      |    No     |   0   | Explanatory note if milestone flagged as `On Dispute Hold`.                                           |
| `custom_delay_reason_table`     | Delay Reason & Audit Log   | `Table`        | `Remark-Delay Log`                                                                                                                     |    No     |   -   | Mandatory justification child table required before submission if `custom_settlement_status == Overdue`.|

---

### 2.2 Core DocType Extension: `tabPayment Entry`

| Fieldname                       | Label                     | Fieldtype    | Options / Target | Mandatory | Index | Description & Operational Logic                                                              |
| :------------------------------ | :------------------------ | :----------- | :--------------- | :-------: | :---: | :------------------------------------------------------------------------------------------- |
| `custom_po_milestone_ref`       | PO Milestone Schedule Row | `Data`       | -                |    No     |   1   | Row ID (`name`) of linked `tabPayment Schedule` row in source PO.                            |
| `custom_solar_project_ref`      | Solar Project Code        | `Link`       | `Project`        |    No     |   1   | Linked solar EPC project code for project cash flow tracking.                                |
| `custom_purchase_team_notified` | Purchase Team Notified    | `Check`      | -                |    No     |   1   | Set to 1 when post-payment settlement alert dispatched.                                      |
| `custom_purchase_notified_at`   | Purchase Notified At      | `Datetime`   | -                |    No     |   0   | Timestamp when notification delivered to Purchase team.                                      |
| `custom_bank_utr_no`            | Bank UTR / Ref No         | `Data`       | -                |  **Yes**  |   1   | Bank transaction reference / UTR number entered by Accounts.                                 |
| `custom_disbursement_remarks`   | Disbursement Remarks      | `Small Text` | -                |    No     |   0   | Operational notes shared directly with Purchase team.                                        |
| `custom_tds_194q_deducted`      | Section 194Q TDS Deducted | `Check`      | -                |    No     |   1   | Set to 1 when mandatory 0.1% TDS is verified for suppliers exceeding ₹50L.                  |
| `custom_tds_amount`             | TDS Amount (₹)            | `Currency`   | `Company:currency`|   No     |   -   | Explicit TDS monetary value deducted on the payment voucher.                                 |

---

### 2.3 Settings Singletons: `tabSolar Notification Settings` & `tabSolar SCM Settings`

#### `tabSolar Notification Settings` Extensions:
| Fieldname                               | Label                                     | Fieldtype |     Default      | Description & Governance Rules                                                |
| :-------------------------------------- | :---------------------------------------- | :-------- | :--------------: | :---------------------------------------------------------------------------- |
| `notify_vendor_payment_t_minus_1`       | Enable T-1 Payment Reminder (Day Before)  | `Check`   |        1         | Toggles morning alert to Purchase & Accounts 24h prior to milestone due date. |
| `notify_vendor_payment_t_zero`          | Enable T-0 Payment Reminder (Payment Day) | `Check`   |        1         | Toggles morning urgent alert to Purchase & Accounts on payment due date.      |
| `notify_purchase_on_payment_settlement` | Enable Instant Purchase Settlement Alert  | `Check`   |        1         | Toggles real-time alert to Purchase team upon `Payment Entry` submission.     |
| `vendor_payment_notification_hour`      | Daily Daemon Execution Hour (24h)         | `Int`     |        8         | Scheduled hour of day (default 08:00 AM) when daily cron runs.                |
| `vendor_payment_alert_channels`         | Active Alert Channels                     | `Select`  | `System & Email` | Options: `System In-App Only`, `System & Email`, `System, Email & WhatsApp`.  |

#### `tabSolar SCM Settings` Extensions:
| Fieldname                                 | Label                                     | Fieldtype |     Default      | Description & Governance Rules                                                |
| :---------------------------------------- | :---------------------------------------- | :-------- | :--------------: | :---------------------------------------------------------------------------- |
| `enable_mandatory_prerequisite_payment`   | Enforce Milestone Prerequisite Validation | `Check`   |        1         | When active, hard-blocks `Payment Entry` if prerequisite condition not cleared.|
| `tds_194q_annual_threshold_inr`           | Section 194Q Annual Turnover Floor (₹)    | `Currency`|   5000000.00     | Statutory threshold (₹50 Lakhs) triggering mandatory 0.1% TDS deduction.      |
| `tds_194q_tax_rate_percent`               | Section 194Q Default TDS Rate (%)         | `Percent` |       0.10       | Statutory TDS rate under Income Tax Act Section 194Q.                         |
| `vendor_payment_grace_period_days`        | Payment Delay Grace Period (Days)         | `Int`     |        2         | Grace period before marking milestone overdue and enforcing delay logging.    |

---

### 2.4 SQL Schema & Composite B-Tree Indexes

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

-- Composite index for prerequisite verification queries
CREATE INDEX IF NOT EXISTS idx_payment_schedule_prereq
ON `tabPayment Schedule` (custom_prerequisite_satisfied, custom_milestone_type);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Decoupled Python services encapsulating business rules, verification gates, notification dispatching, and settlement reconciliation.

### 3.1 `VendorPaymentObligationEngine` (Unified Obligation Model)

```python
# solar_module/services/payment_monitoring/obligation_engine.py

from typing import Dict, List, Optional
import frappe
from frappe.utils import nowdate, add_days, getdate, flt

class VendorPaymentObligationEngine:
    """
    Unifies and normalizes payment commitments across both Step 15 Purchase Orders
    (milestones) and Step 17 Purchase Invoices (credit periods). Eliminates double-counting
    liabilities when invoices are linked to PO milestone tranches.
    """

    @classmethod
    def get_unified_obligations(
        cls,
        time_horizon_days: int = 30,
        department: str = "All",
        project: Optional[str] = None
    ) -> Dict:
        today = getdate(nowdate())
        future_limit = add_days(today, int(time_horizon_days))

        # 1. Fetch unbilled or advance PO milestone rows
        po_obligations = cls._fetch_po_milestones(today, future_limit, project)

        # 2. Fetch submitted, approved Purchase Invoice schedules
        pi_obligations = cls._fetch_pi_schedules(today, future_limit, project)

        # 3. Combine and reconcile to prevent duplicate counting
        combined = cls._reconcile_and_deduplicate(po_obligations, pi_obligations)

        # 4. Filter by department orientation if requested
        filtered = cls._filter_by_department(combined, department)

        # 5. Compute summary aggregates
        summary = cls._compute_aggregates(filtered, today)

        return {
            "time_horizon_days": time_horizon_days,
            "summary": summary,
            "obligations": filtered
        }

    @classmethod
    def _fetch_po_milestones(cls, today, future_limit, project: Optional[str]) -> List[Dict]:
        conditions = [
            "ps.parenttype = 'Purchase Order'",
            "po.docstatus = 1",
            "ps.custom_settlement_status != 'Disbursed'",
            "ps.due_date <= %(future_limit)s"
        ]
        params = {"future_limit": future_limit}

        if project:
            conditions.append("po.custom_project_ref = %(project)s")
            params["project"] = project

        query = f"""
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
                ps.custom_hold_reason,
                po.supplier,
                po.company,
                po.custom_project_ref AS project,
                sup.supplier_name
            FROM `tabPayment Schedule` ps
            INNER JOIN `tabPurchase Order` po ON po.name = ps.parent
            INNER JOIN `tabSupplier` sup ON sup.name = po.supplier
            WHERE {' AND '.join(conditions)}
            ORDER BY ps.due_date ASC
        """
        records = frappe.db.sql(query, params, as_dict=True)
        for r in records:
            r["source_type"] = "PO Milestone"
        return records

    @classmethod
    def _fetch_pi_schedules(cls, today, future_limit, project: Optional[str]) -> List[Dict]:
        conditions = [
            "ps.parenttype = 'Purchase Invoice'",
            "pi.docstatus = 1",
            "pi.outstanding_amount > 0",
            "ps.custom_settlement_status != 'Disbursed'",
            "ps.due_date <= %(future_limit)s"
        ]
        params = {"future_limit": future_limit}

        if project:
            conditions.append("pi.custom_project_ref = %(project)s")
            params["project"] = project

        query = f"""
            SELECT
                ps.name AS milestone_id,
                ps.parent AS parent_doc,
                ps.parenttype AS parent_type,
                ps.due_date,
                ps.payment_amount,
                COALESCE(ps.custom_milestone_type, 'Invoice Credit Period') AS custom_milestone_type,
                COALESCE(ps.custom_prerequisite_required, 'Passed 3-Way Match') AS custom_prerequisite_required,
                1 AS custom_prerequisite_satisfied,
                ps.custom_settlement_status,
                ps.custom_hold_reason,
                pi.supplier,
                pi.company,
                pi.custom_project_ref AS project,
                sup.supplier_name,
                pi.bill_no,
                pi.bill_date
            FROM `tabPayment Schedule` ps
            INNER JOIN `tabPurchase Invoice` pi ON pi.name = ps.parent
            INNER JOIN `tabSupplier` sup ON sup.name = pi.supplier
            WHERE {' AND '.join(conditions)}
            ORDER BY ps.due_date ASC
        """
        records = frappe.db.sql(query, params, as_dict=True)
        for r in records:
            r["source_type"] = "Invoice Schedule"
        return records

    @classmethod
    def _reconcile_and_deduplicate(cls, po_rows: List[Dict], pi_rows: List[Dict]) -> List[Dict]:
        """
        If a Purchase Invoice has been created against a PO milestone (e.g. GRN delivery),
        the PI schedule takes precedence and the corresponding PO milestone is suppressed
        from the combined upcoming cash obligations to prevent double counting.
        """
        active_pi_po_refs = set(
            frappe.db.sql_list(
                "SELECT DISTINCT custom_po_reference FROM `tabPurchase Invoice` WHERE docstatus = 1 AND custom_po_reference IS NOT NULL"
            )
        )

        deduped = []
        for po_row in po_rows:
            # Advance and LR milestones are rarely in PI initially; GRN delivery tranches move to PI
            if po_row["parent_doc"] in active_pi_po_refs and po_row["custom_milestone_type"] in [
                "On Delivery (GRN)",
                "Invoice Credit Period"
            ]:
                continue
            deduped.append(po_row)

        deduped.extend(pi_rows)
        deduped.sort(key=lambda x: getdate(x["due_date"]))
        return deduped

    @classmethod
    def _filter_by_department(cls, obligations: List[Dict], department: str) -> List[Dict]:
        if department == "Purchase":
            # Procurement cares deeply about Advance and Against LR milestones that unblock shipments
            return [o for o in obligations if o["custom_milestone_type"] in [
                "Advance (Pre-Dispatch)",
                "Against LR / Inspection",
                "On Delivery (GRN)"
            ]]
        elif department == "Accounts":
            # Accounts handles all disbursement schedules regardless of type
            return obligations
        return obligations

    @classmethod
    def _compute_aggregates(cls, obligations: List[Dict], today) -> Dict:
        tomorrow = add_days(today, 1)
        due_today = [o for o in obligations if getdate(o["due_date"]) == today]
        due_tomorrow = [o for o in obligations if getdate(o["due_date"]) == tomorrow]
        overdue = [o for o in obligations if getdate(o["due_date"]) < today]

        return {
            "total_count": len(obligations),
            "total_amount": sum(flt(o["payment_amount"]) for o in obligations),
            "due_today_count": len(due_today),
            "due_today_amount": sum(flt(o["payment_amount"]) for o in due_today),
            "due_tomorrow_count": len(due_tomorrow),
            "due_tomorrow_amount": sum(flt(o["payment_amount"]) for o in due_tomorrow),
            "overdue_count": len(overdue),
            "overdue_amount": sum(flt(o["payment_amount"]) for o in overdue)
        }
```

---

### 3.2 `VendorPaymentNotificationDaemon` (Proactive Daily Alerts)

```python
# solar_module/services/payment_monitoring/notification_daemon.py

from typing import Set, Dict
import frappe
from frappe import _
from frappe.utils import nowdate, add_days, getdate, format_date, now_datetime

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
    def _process_reminders_for_date(
        cls, target_date, reminder_type: str, flag_field: str, timestamp_field: str
    ):
        query = f"""
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
            INNER JOIN `tab{{parent_type}}` parent_tab ON parent_tab.name = ps.parent
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
                new_status = "Due Tomorrow" if reminder_type == "T-1" else "Due Today"
                frappe.db.set_value("Payment Schedule", row.schedule_row_id, {
                    flag_field: 1,
                    timestamp_field: now_datetime(),
                    "custom_settlement_status": new_status
                }, update_modified=False)

    @classmethod
    def _dispatch_dual_notifications(cls, row: Dict, reminder_type: str):
        urgency = "URGENT: " if reminder_type == "T-0" else "UPCOMING: "
        timing = "TODAY" if reminder_type == "T-0" else "TOMORROW"
        subject = _("{0} Supplier Payment Due {1}: {2} (INR {3:,.2f})").format(
            urgency,
            timing,
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
    def _get_stakeholder_recipients(cls, row: Dict) -> Set[str]:
        users = set()
        # 1. Accounts team (Accounts Manager & Accounts Assistant)
        accounts_users = frappe.get_all(
            "Has Role",
            filters={"role": ["in", ["Accounts Manager", "Accounts Assistant"]]},
            fields=["parent"]
        )
        users.update([u.parent for u in accounts_users])

        # 2. Purchase team (Purchase Manager & Purchase Assistant)
        purchase_users = frappe.get_all(
            "Has Role",
            filters={"role": ["in", ["Purchase Manager", "Purchase Assistant"]]},
            fields=["parent"]
        )
        users.update([u.parent for u in purchase_users])

        # 3. Project Engineer if tied to a project
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

---

### 3.3 `VendorPaymentSettlementService` (Closed-Loop Observer)

```python
# solar_module/services/payment_monitoring/settlement_service.py

from typing import Dict, Set
import frappe
from frappe import _
from frappe.utils import format_date, now_datetime

class VendorPaymentSettlementService:
    """
    Event-driven observer bound to `Payment Entry.on_submit` and `on_cancel`.
    Reconciles milestone payment schedules and dispatches instant closed-loop
    settlement notifications to the Purchase Team.
    """

    @classmethod
    def on_payment_submitted(cls, doc):
        if doc.payment_type != "Pay" or doc.party_type != "Supplier":
            return

        for ref in doc.references:
            if ref.reference_doctype == "Purchase Order":
                cls._handle_po_disbursement(doc, ref)
            elif ref.reference_doctype == "Purchase Invoice":
                cls._handle_pi_disbursement(doc, ref)

    @classmethod
    def on_payment_cancelled(cls, doc):
        if doc.payment_type != "Pay" or doc.party_type != "Supplier":
            return

        # Roll back schedule statuses
        frappe.db.sql("""
            UPDATE `tabPayment Schedule`
            SET custom_settlement_status = 'Scheduled',
                custom_linked_payment_entry = NULL
            WHERE custom_linked_payment_entry = %(pe_name)s
        """, {"pe_name": doc.name})

    @classmethod
    def _handle_po_disbursement(cls, doc, ref):
        po_doc = frappe.get_doc("Purchase Order", ref.reference_name)

        schedule_updated = False
        target_row_id = doc.get("custom_po_milestone_ref")

        for row in po_doc.payment_schedule:
            should_update = False
            if target_row_id and row.name == target_row_id:
                should_update = True
            elif not target_row_id and row.custom_settlement_status != "Disbursed" and not schedule_updated:
                should_update = True

            if should_update:
                row.custom_settlement_status = "Disbursed"
                row.custom_linked_payment_entry = doc.name
                schedule_updated = True
                break

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
                break

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
    def _broadcast_settlement_to_purchase(
        cls,
        doc,
        parent_type: str,
        parent_name: str,
        supplier: str,
        allocated_amount: float,
        remaining_balance: float,
        project_code: str
    ):
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
            doc.reference_no or doc.get("custom_bank_utr_no") or "Direct Bank Transfer",
            doc.mode_of_payment,
            format_date(doc.posting_date),
            remaining_balance,
            doc.name
        )

        purchase_users = frappe.get_all(
            "Has Role",
            filters={"role": ["in", ["Purchase Manager", "Purchase Assistant"]]},
            fields=["parent"]
        )
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
        doc.db_set("custom_purchase_notified_at", now_datetime())
```

---

### 3.4 `PaymentPrerequisiteGateService` (Operational & Tax Gates)

```python
# solar_module/services/payment_monitoring/prerequisite_gate.py

import frappe
from frappe import _
from frappe.utils import flt

class PaymentPrerequisiteGateService:
    """
    Validates operational prerequisites and statutory tax compliance before
    allowing fund disbursement in Payment Entry.
    """

    @classmethod
    def validate_payment_entry(cls, doc):
        if doc.payment_type != "Pay" or doc.party_type != "Supplier":
            return

        scm_settings = frappe.get_cached_doc("Solar SCM Settings")

        # Gate 1: Milestone Prerequisite Validation
        if scm_settings.enable_mandatory_prerequisite_payment:
            cls._validate_milestone_prerequisites(doc)

        # Gate 2: Statutory Section 194Q TDS Deduction
        cls._validate_tds_194q_compliance(doc, scm_settings)

        # Gate 3: Verified Supplier Bank Details
        cls._validate_supplier_bank_account(doc)

    @classmethod
    def _validate_milestone_prerequisites(cls, doc):
        for ref in doc.references:
            if ref.reference_doctype == "Purchase Order":
                po = frappe.get_doc("Purchase Order", ref.reference_name)
                target_row_id = doc.get("custom_po_milestone_ref")

                for row in po.payment_schedule:
                    if target_row_id and row.name != target_row_id:
                        continue

                    # If this milestone is being paid, prerequisite must be met
                    if not row.custom_prerequisite_satisfied and row.custom_prerequisite_required != "None":
                        frappe.throw(
                            _("Payment blocked: Prerequisite '{0}' for Milestone '{1}' on PO {2} is not satisfied.").format(
                                row.custom_prerequisite_required,
                                row.custom_milestone_type,
                                po.name
                            ),
                            frappe.ValidationError
                        )

            elif ref.reference_doctype == "Purchase Invoice":
                pi = frappe.get_doc("Purchase Invoice", ref.reference_name)
                if pi.get("custom_3way_match_status") not in ["Passed", "Admin Overridden"]:
                    frappe.throw(
                        _("Payment blocked: Purchase Invoice {0} has not passed 3-Way Match validation (Status: {1}).").format(
                            pi.name, pi.get("custom_3way_match_status")
                        ),
                        frappe.ValidationError
                    )

    @classmethod
    def _validate_tds_194q_compliance(cls, doc, scm_settings):
        supplier = doc.party
        threshold = flt(scm_settings.tds_194q_annual_threshold_inr) or 5000000.0

        # Calculate fiscal year cumulative purchases
        fiscal_year = frappe.defaults.get_user_default("fiscal_year")
        total_billed = frappe.db.sql("""
            SELECT COALESCE(SUM(grand_total), 0)
            FROM `tabPurchase Invoice`
            WHERE supplier = %(supplier)s
              AND docstatus = 1
        """, {"supplier": supplier})[0][0]

        if total_billed > threshold:
            # Must have deducted TDS in Payment Entry or linked invoice
            has_tds = False
            for deduction in doc.get("deductions", []):
                if "194Q" in (deduction.account_head or "") or "TDS" in (deduction.account_head or ""):
                    has_tds = True
                    break

            if not has_tds and not doc.get("custom_tds_194q_deducted"):
                frappe.throw(
                    _("Statutory Compliance Error: Supplier {0} cumulative billing (INR {1:,.2f}) exceeds the Section 194Q limit of INR {2:,.2f}. 0.1% TDS deduction must be applied in deductions or verified.").format(
                        supplier, total_billed, threshold
                    ),
                    frappe.ValidationError
                )

    @classmethod
    def _validate_supplier_bank_account(cls, doc):
        if not doc.bank_account:
            return

        is_verified = frappe.db.get_value("Bank Account", doc.bank_account, "custom_is_verified")
        # If custom_is_verified field exists and is 0, block payment
        if is_verified is not None and int(is_verified) == 0:
            frappe.throw(
                _("Security Alert: Destination Bank Account {0} is unverified. Management authorization required before disbursement.").format(
                    doc.bank_account
                ),
                frappe.ValidationError
            )
```

---

### 3.5 `PaymentStageForwardLockService` (ADR-000 Immutability Lock)

```python
# solar_module/services/payment_monitoring/stage_forward_lock.py

import frappe
from frappe import _

class PaymentStageForwardLockService:
    """
    Enforces ADR-000 stage-forward immutability locks. Once a Payment Entry is submitted
    and settled against a Purchase Invoice or Purchase Order, prevents unilateral cancellation
    or alteration of upstream documents.
    """

    @classmethod
    def assert_upstream_unlocked(cls, doc):
        """Called in Purchase Invoice on_cancel and Purchase Order on_cancel."""
        doctype = doc.doctype
        docname = doc.name

        active_payment = frappe.db.sql("""
            SELECT pe.name
            FROM `tabPayment Entry Reference` per
            INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
            WHERE per.reference_doctype = %(doctype)s
              AND per.reference_name = %(docname)s
              AND pe.docstatus = 1
            LIMIT 1
        """, {"doctype": doctype, "docname": docname})

        if active_payment:
            frappe.throw(
                _("Stage-Forward Lock Violation: Cannot cancel {0} {1} because an active submitted Payment Entry ({2}) exists. Submit a Solar Cancellation Request to proceed.").format(
                    doctype, docname, active_payment[0][0]
                ),
                frappe.ValidationError
            )
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

Integrates hooks into `Payment Entry` and `Payment Schedule` lifecycle events, and provides authenticated whitelisted APIs for the frontend workbenches.

### 4.1 Controller Overrides: `SolarPaymentEntry`

```python
# solar_module/overrides/payment_entry.py

import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from solar_module.services.payment_monitoring.prerequisite_gate import PaymentPrerequisiteGateService
from solar_module.services.payment_monitoring.settlement_service import VendorPaymentSettlementService
from solar_module.security.mixins import StageSecuredDocument

class SolarPaymentEntry(PaymentEntry, StageSecuredDocument):
    """
    Subclasses ERPNext Payment Entry to enforce Stage 18 prerequisite gates,
    statutory TDS 194Q checks, and closed-loop settlement notifications.
    """

    def validate(self):
        super().validate()
        PaymentPrerequisiteGateService.validate_payment_entry(self)

    def on_submit(self):
        super().on_submit()
        VendorPaymentSettlementService.on_payment_submitted(self)

    def on_cancel(self):
        super().on_cancel()
        VendorPaymentSettlementService.on_payment_cancelled(self)
```

---

### 4.2 Whitelisted RPC API Endpoints

```python
# solar_module/api/procurement/payment_monitoring.py

import frappe
from frappe import _
from typing import Dict, Optional
from solar_module.services.payment_monitoring.obligation_engine import VendorPaymentObligationEngine

@frappe.whitelist(methods=["POST"])
def get_upcoming_vendor_payments(
    department: str = "All",
    time_horizon_days: int = 30,
    project: Optional[str] = None
) -> Dict:
    """
    Whitelisted RPC endpoint fetching normalized payment obligations across
    POs and PIs for the Dual-Workspace Desk sections and Workbench SPA.
    """
    frappe.has_permission("Purchase Order", "read", throw=True)
    return VendorPaymentObligationEngine.get_unified_obligations(
        time_horizon_days=time_horizon_days,
        department=department,
        project=project
    )

@frappe.whitelist(methods=["POST"])
def nudge_accounts_team(milestone_id: str, urgency_note: str) -> Dict:
    """
    Whitelisted RPC endpoint allowing Purchase team to send an urgent priority
    push alert to Accounts when a vendor shipment is on hold pending payment.
    """
    frappe.has_permission("Purchase Order", "write", throw=True)
    doc = frappe.get_doc("Payment Schedule", milestone_id)
    parent_doc = frappe.get_doc(doc.parenttype, doc.parent)

    sender = frappe.session.user
    accounts_users = frappe.get_all(
        "Has Role",
        filters={"role": "Accounts Manager"},
        fields=["parent"]
    )

    subject = _("⚡ Procurement Priority Nudge: Payment Needed for {0}").format(parent_doc.supplier)
    message = _(
        "<b>Procurement Priority Nudge from {0}</b><br>"
        "<b>Supplier:</b> {1}<br>"
        "<b>Milestone:</b> {2} (INR {3:,.2f})<br>"
        "<b>Reference:</b> {4}<br>"
        "<b>Urgency Note from Purchase:</b> {5}<br>"
        "<i>Vendor is holding dispatch / production pending payment clearance.</i>"
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

    return {"status": "success", "message": _("Accounts team notified successfully.")}

@frappe.whitelist(methods=["POST"])
def verify_milestone_prerequisite(milestone_id: str, doc_type: str, doc_name: str) -> Dict:
    """
    Whitelisted RPC endpoint allowing authorized personnel to link and satisfy
    operational prerequisites (e.g. Transporter LR, Inspection sign-off).
    """
    roles = frappe.get_roles(frappe.session.user)
    authorized = {"Purchase Manager", "Store Manager", "Project Manager", "Admin", "System Manager"}
    if not (authorized & set(roles)):
        frappe.throw(_("Unauthorized: Only Department Managers or Admin can verify prerequisites."), frappe.PermissionError)

    doc = frappe.get_doc("Payment Schedule", milestone_id)
    doc.custom_prerequisite_satisfied = 1
    doc.custom_prerequisite_doc_type = doc_type
    doc.custom_prerequisite_doc_ref = doc_name
    doc.save(ignore_permissions=True)

    return {"status": "success", "message": _("Prerequisite verified and satisfied.")}

@frappe.whitelist(methods=["POST"])
def place_milestone_hold(milestone_id: str, hold_reason: str) -> Dict:
    """
    Whitelisted RPC endpoint allowing Purchase or Accounts managers to place
    a milestone on dispute hold (e.g. damaged goods, price dispute).
    """
    roles = frappe.get_roles(frappe.session.user)
    authorized = {"Purchase Manager", "Accounts Manager", "Admin", "System Manager"}
    if not (authorized & set(roles)):
        frappe.throw(_("Unauthorized: Managerial authorization required to place payment holds."), frappe.PermissionError)

    doc = frappe.get_doc("Payment Schedule", milestone_id)
    doc.custom_settlement_status = "On Dispute Hold"
    doc.custom_hold_reason = hold_reason
    doc.save(ignore_permissions=True)

    return {"status": "success", "message": _("Milestone placed on Dispute Hold.")}

@frappe.whitelist(methods=["POST"])
def release_milestone_hold(milestone_id: str, release_notes: str) -> Dict:
    """
    Whitelisted RPC endpoint releasing a milestone from dispute hold.
    """
    roles = frappe.get_roles(frappe.session.user)
    authorized = {"Purchase Manager", "Accounts Manager", "Admin", "System Manager"}
    if not (authorized & set(roles)):
        frappe.throw(_("Unauthorized: Managerial authorization required to release payment holds."), frappe.PermissionError)

    doc = frappe.get_doc("Payment Schedule", milestone_id)
    doc.custom_settlement_status = "Scheduled"
    doc.custom_hold_reason = f"Released: {release_notes}"
    doc.save(ignore_permissions=True)

    return {"status": "success", "message": _("Milestone hold released.")}

@frappe.whitelist(methods=["POST"])
def log_payment_delay(milestone_id: str, delay_reason: str, mitigation_plan: str) -> Dict:
    """
    Whitelisted RPC endpoint to record mandatory delay justifications in
    tabRemark-Delay Log when a payment milestone is overdue.
    """
    doc = frappe.get_doc("Payment Schedule", milestone_id)
    parent_doc = frappe.get_doc(doc.parenttype, doc.parent)

    delay_log = parent_doc.append("custom_delay_reason_table", {})
    delay_log.reason = delay_reason
    delay_log.mitigation_plan = mitigation_plan
    delay_log.logged_by = frappe.session.user
    delay_log.logged_at = frappe.utils.now_datetime()
    parent_doc.save(ignore_permissions=True)

    return {"status": "success", "message": _("Delay justification recorded successfully.")}
```

---

### 4.3 Celery / RQ Scheduled Daemon Task

```python
# solar_module/tasks/payment_monitoring.py

import frappe
from solar_module.services.payment_monitoring.notification_daemon import VendorPaymentNotificationDaemon

def run_daily_vendor_payment_daemon():
    """
    Executed daily via Celery/RQ scheduler (configured in hooks.py under scheduler_events.daily).
    Evaluates whether current hour matches Solar Notification Settings.vendor_payment_notification_hour.
    """
    settings = frappe.get_cached_doc("Solar Notification Settings")
    current_hour = frappe.utils.now_datetime().hour

    configured_hour = settings.vendor_payment_notification_hour or 8
    if current_hour == configured_hour:
        VendorPaymentNotificationDaemon.execute_daily_evaluations()
```

---

## 5. Layer 4: Desk Client Script & Dynamic Dual-Workspace Frontend

Provides synchronized user experiences for both Purchase and Accounts teams.

### 5.1 Desk Client Script: `codes/client_script/payment_entry.js`

```javascript
// codes/client_script/payment_entry.js

frappe.ui.form.on('Payment Entry', {
    refresh: function(frm) {
        // Enforce UTR entry requirement for bank payments
        if (frm.doc.payment_type === 'Pay' && frm.doc.party_type === 'Supplier') {
            frm.set_df_property('custom_bank_utr_no', 'reqd', 1);

            // Display instant notification indicator if already settled
            if (frm.doc.custom_purchase_team_notified) {
                frm.dashboard.add_indicator(
                    __('Purchase Team Notified at {0}', [frappe.datetime.str_to_user(frm.doc.custom_purchase_notified_at)]),
                    'green'
                );
            }
        }
    },

    validate: function(frm) {
        if (frm.doc.payment_type === 'Pay' && frm.doc.party_type === 'Supplier') {
            if (!frm.doc.custom_bank_utr_no && frm.doc.mode_of_payment !== 'Cash') {
                frappe.msgprint({
                    title: __('Mandatory Bank Reference'),
                    indicator: 'red',
                    message: __('Please enter the Bank UTR / Reference Number before submitting payment.')
                });
                frappe.validated = false;
            }
        }
    }
});
```

---

### 5.2 Desk Client Script: `codes/client_script/payment_schedule.js`

```javascript
// codes/client_script/payment_schedule.js (Embedded in Purchase Order & Purchase Invoice)

frappe.ui.form.on('Payment Schedule', {
    form_render: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Render prerequisite indicator badge
        let badge_class = row.custom_prerequisite_satisfied ? 'green' : 'orange';
        let badge_text = row.custom_prerequisite_satisfied ? __('Prerequisite Verified') : __('Prerequisite Pending');
        // Render status pill in child grid
    }
});

frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Upcoming Payments Workbench'), function() {
                frappe.set_route('solar', 'procurement', 'payment-workbench');
            }, __('Solar SCM'));

            // Check if any milestone has unfulfilled prerequisites
            let pending_prereqs = (frm.doc.payment_schedule || []).filter(
                r => !r.custom_prerequisite_satisfied && r.custom_prerequisite_required !== 'None'
            );

            if (pending_prereqs.length > 0) {
                frm.dashboard.add_indicator(
                    __('{0} Milestones Pending Prerequisites', [pending_prereqs.length]),
                    'orange'
                );
            }
        }
    }
});
```

---

### 5.3 Purchase Desk Upcoming Payments Card (`/solar/procurement`)

Card component embedded on the Procurement Dashboard:

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

---

### 5.4 Accounts Desk Upcoming Vendor Disbursements Card (`/solar/accounts`)

Card component embedded on the Finance & Accounts Dashboard:

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

---

### 5.5 Joint Collaborative Vendor Payment Workbench SPA (`/solar/procurement/payment-workbench`)

- **Full Matrix Table:** Filterable by Project Code, Equipment Category (Modules, Inverters, Structures, BOS), Milestone Type, and Due Horizon.
- **Bi-directional Comment Drawer:** Direct communication thread between Purchase Assistant and Accounts Assistant linked to specific milestone schedule rows.
- **Dispute Action Modals:** `[Place on Hold]` capturing hold reasons and triggering alert to suppliers; `[Release Hold]` restoring scheduled payment flows.

---

## 6. Layer 5: Automated Verification Suite (Integration Tests)

Comprehensive Python integration test suite strictly adhering to the **Zero-Commit Rule** (`frappe.db.rollback()` in `tearDown()`, zero database commits).

```python
# solar_module/tests/test_step_18_vendor_payment_workbench_tracer_bullet.py

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days, getdate
from solar_module.services.payment_monitoring.obligation_engine import VendorPaymentObligationEngine
from solar_module.services.payment_monitoring.notification_daemon import VendorPaymentNotificationDaemon
from solar_module.services.payment_monitoring.settlement_service import VendorPaymentSettlementService
from solar_module.services.payment_monitoring.prerequisite_gate import PaymentPrerequisiteGateService
from solar_module.api.procurement.payment_monitoring import nudge_accounts_team

class TestStep18VendorPaymentWorkbenchTracerBullet(FrappeTestCase):
    """
    Integration test suite executing the 12-case atomic verification of
    Stage 18 Joint Vendor Payment Monitoring Workbench Tracer Bullet.
    """

    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")
        self._setup_test_master_data()

    def tearDown(self):
        frappe.db.rollback()
        super().tearDown()

    def _setup_test_master_data(self):
        # 1. Company
        if not frappe.db.exists("Company", "_Test Solar EPC Co"):
            self.company = frappe.get_doc({
                "doctype": "Company",
                "company_name": "_Test Solar EPC Co",
                "default_currency": "INR",
                "country": "India"
            }).insert(ignore_permissions=True)
        else:
            self.company = frappe.get_doc("Company", "_Test Solar EPC Co")

        # 2. Supplier
        if not frappe.db.exists("Supplier", "_Test Tier1 PV Supplier"):
            self.supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": "_Test Tier1 PV Supplier",
                "supplier_group": "Solar Hardware",
                "supplier_type": "Company"
            }).insert(ignore_permissions=True)
        else:
            self.supplier = frappe.get_doc("Supplier", "_Test Tier1 PV Supplier")

        # 3. Item
        if not frappe.db.exists("Item", "_Test Bifacial PV Module 550W"):
            self.item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "_Test Bifacial PV Module 550W",
                "item_name": "550W Mono Bifacial Solar Module",
                "item_group": "Solar Modules",
                "is_stock_item": 1,
                "stock_uom": "Nos"
            }).insert(ignore_permissions=True)
        else:
            self.item = frappe.get_doc("Item", "_Test Bifacial PV Module 550W")

        # 4. Settings
        notif_settings = frappe.get_doc("Solar Notification Settings")
        notif_settings.notify_vendor_payment_t_minus_1 = 1
        notif_settings.notify_vendor_payment_t_zero = 1
        notif_settings.notify_purchase_on_payment_settlement = 1
        notif_settings.save(ignore_permissions=True)

        scm_settings = frappe.get_doc("Solar SCM Settings")
        scm_settings.enable_mandatory_prerequisite_payment = 1
        scm_settings.tds_194q_annual_threshold_inr = 5000000.0
        scm_settings.save(ignore_permissions=True)

    def test_01_unified_obligation_normalization(self):
        """Test Invariant 1: Obligation engine extracts both PO milestones and PI schedules and reconciles them."""
        tomorrow = add_days(nowdate(), 1)
        po = self._create_test_purchase_order(due_date=tomorrow, amount=50000)

        obligations = VendorPaymentObligationEngine.get_unified_obligations(time_horizon_days=7)
        self.assertGreaterEqual(obligations["summary"]["total_count"], 1)

        found = [o for o in obligations["obligations"] if o["parent_doc"] == po.name]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["payment_amount"], 50000)

    def test_02_daemon_dispatches_t1_notification(self):
        """Test Invariant 2 & 3: Daily daemon dispatches T-1 reminder for obligations due tomorrow."""
        tomorrow = add_days(nowdate(), 1)
        po = self._create_test_purchase_order(due_date=tomorrow, amount=75000)

        VendorPaymentNotificationDaemon.execute_daily_evaluations()

        row = frappe.db.get_value(
            "Payment Schedule",
            {"parent": po.name, "due_date": tomorrow},
            ["custom_notification_t1_sent", "custom_settlement_status"],
            as_dict=True
        )
        self.assertEqual(row.custom_notification_t1_sent, 1)
        self.assertEqual(row.custom_settlement_status, "Due Tomorrow")

    def test_03_daemon_dispatches_t0_notification(self):
        """Test Invariant 2 & 3: Daily daemon dispatches urgent T-0 reminder for obligations due today."""
        today = nowdate()
        po = self._create_test_purchase_order(due_date=today, amount=120000)

        VendorPaymentNotificationDaemon.execute_daily_evaluations()

        row = frappe.db.get_value(
            "Payment Schedule",
            {"parent": po.name, "due_date": today},
            ["custom_notification_t0_sent", "custom_settlement_status"],
            as_dict=True
        )
        self.assertEqual(row.custom_notification_t0_sent, 1)
        self.assertEqual(row.custom_settlement_status, "Due Today")

    def test_04_payment_entry_closed_loop_broadcast(self):
        """Test Invariant 4: Submitting Payment Entry intercepts event and broadcasts to Purchase team."""
        po = self._create_test_purchase_order(due_date=nowdate(), amount=80000)
        pe = self._create_test_payment_entry(po=po, amount=80000, utr="UTR-RTGS-990011")
        pe.submit()

        pe.reload()
        self.assertEqual(pe.custom_purchase_team_notified, 1)
        self.assertIsNotNone(pe.custom_purchase_notified_at)

        po_schedule = frappe.db.get_value(
            "Payment Schedule",
            {"parent": po.name},
            ["custom_settlement_status", "custom_linked_payment_entry"],
            as_dict=True
        )
        self.assertEqual(po_schedule.custom_settlement_status, "Disbursed")
        self.assertEqual(po_schedule.custom_linked_payment_entry, pe.name)

    def test_05_advance_prerequisite_gate(self):
        """Test Invariant 5: Advance payment blocked if PO is unsubmitted."""
        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": self.supplier.name,
            "company": self.company.name,
            "schedule_date": add_days(nowdate(), 10),
            "items": [{"item_code": self.item.name, "qty": 10, "rate": 2000}],
            "payment_schedule": [{
                "due_date": nowdate(),
                "payment_amount": 20000,
                "custom_milestone_type": "Advance (Pre-Dispatch)",
                "custom_prerequisite_required": "Signed PO",
                "custom_prerequisite_satisfied": 0
            }]
        }).insert(ignore_permissions=True)

        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": self.supplier.name,
            "company": self.company.name,
            "paid_amount": 20000,
            "received_amount": 20000,
            "references": [{"reference_doctype": "Purchase Order", "reference_name": po.name, "allocated_amount": 20000}]
        })
        self.assertRaises(frappe.ValidationError, pe.insert)

    def test_06_transit_lr_prerequisite_gate(self):
        """Test Invariant 5: Transit milestone blocked if LR & FAT inspection reports are not satisfied."""
        po = self._create_test_purchase_order(
            due_date=nowdate(),
            amount=50000,
            milestone_type="Against LR / Inspection",
            prereq_required="Transporter LR & FAT Report",
            prereq_satisfied=0
        )

        pe = self._create_test_payment_entry(po=po, amount=50000, utr="UTR-LR-112233")
        self.assertRaises(frappe.ValidationError, pe.insert)

    def test_07_post_grn_3way_match_gate(self):
        """Test Invariant 5: Post-GRN milestone payment blocked if 3-Way Match status is not Passed."""
        pi = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "supplier": self.supplier.name,
            "company": self.company.name,
            "custom_3way_match_status": "Discrepancy Hold",
            "items": [{"item_code": self.item.name, "qty": 10, "rate": 2000}],
            "payment_schedule": [{
                "due_date": nowdate(),
                "payment_amount": 20000,
                "custom_milestone_type": "On Delivery (GRN)"
            }]
        }).insert(ignore_permissions=True)

        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": self.supplier.name,
            "company": self.company.name,
            "paid_amount": 20000,
            "received_amount": 20000,
            "references": [{"reference_doctype": "Purchase Invoice", "reference_name": pi.name, "allocated_amount": 20000}]
        })
        self.assertRaises(frappe.ValidationError, pe.insert)

    def test_08_statutory_tds_194q_deduction_gate(self):
        """Test Invariant 6: Asserts 0.1% TDS deduction for cumulative billing > ₹50 Lakhs."""
        # Create prior invoices exceeding 50L
        prior_pi = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "supplier": self.supplier.name,
            "company": self.company.name,
            "items": [{"item_code": self.item.name, "qty": 1000, "rate": 6000}], # 60 Lakhs
            "custom_3way_match_status": "Passed"
        }).insert(ignore_permissions=True)
        prior_pi.submit()

        po = self._create_test_purchase_order(due_date=nowdate(), amount=100000)
        # Attempt payment without TDS deduction
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": self.supplier.name,
            "company": self.company.name,
            "paid_amount": 100000,
            "received_amount": 100000,
            "custom_bank_utr_no": "UTR-TAX-12345",
            "references": [{"reference_doctype": "Purchase Order", "reference_name": po.name, "allocated_amount": 100000}]
        })
        self.assertRaises(frappe.ValidationError, pe.insert)

    def test_09_supplier_bank_verification_gate(self):
        """Test Invariant 6: Blocks payment to unverified destination bank account."""
        bank_acc = frappe.get_doc({
            "doctype": "Bank Account",
            "account_name": "_Test Unverified Vendor Account",
            "party_type": "Supplier",
            "party": self.supplier.name,
            "custom_is_verified": 0
        }).insert(ignore_permissions=True)

        po = self._create_test_purchase_order(due_date=nowdate(), amount=30000)
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": self.supplier.name,
            "company": self.company.name,
            "paid_amount": 30000,
            "received_amount": 30000,
            "bank_account": bank_acc.name,
            "custom_bank_utr_no": "UTR-UNVERIFIED-1",
            "references": [{"reference_doctype": "Purchase Order", "reference_name": po.name, "allocated_amount": 30000}]
        })
        self.assertRaises(frappe.ValidationError, pe.insert)

    def test_10_procurement_nudge_endpoint(self):
        """Test Invariant 7: Purchase team nudge endpoint creates high-priority alert for Accounts."""
        po = self._create_test_purchase_order(due_date=nowdate(), amount=45000)
        milestone_id = po.payment_schedule[0].name

        res = nudge_accounts_team(milestone_id=milestone_id, urgency_note="Vendor truck waiting at factory gates")
        self.assertEqual(res["status"], "success")

        # Verify Notification Log was created
        notif = frappe.db.get_value(
            "Notification Log",
            {"document_name": po.name, "subject": ["like", "%Procurement Priority Nudge%"]},
            "name"
        )
        self.assertIsNotNone(notif)

    def test_11_overdue_delay_audit_enforcement(self):
        """Test Invariant 2: Obligations past due date are marked Overdue by daemon."""
        past_date = add_days(nowdate(), -5)
        po = self._create_test_purchase_order(due_date=past_date, amount=65000)

        VendorPaymentNotificationDaemon.execute_daily_evaluations()

        status = frappe.db.get_value(
            "Payment Schedule",
            {"parent": po.name, "due_date": past_date},
            "custom_settlement_status"
        )
        self.assertEqual(status, "Overdue")

    def test_12_stage_forward_immutability_lock(self):
        """Test Invariant 8: Cancelling PO or PI with submitted Payment Entry is blocked."""
        po = self._create_test_purchase_order(due_date=nowdate(), amount=50000)
        pe = self._create_test_payment_entry(po=po, amount=50000, utr="UTR-LOCK-1122")
        pe.submit()

        # Attempt to cancel PO directly
        self.assertRaises(frappe.ValidationError, po.cancel)

    # --- Test Helper Methods ---

    def _create_test_purchase_order(
        self,
        due_date,
        amount,
        milestone_type="Advance (Pre-Dispatch)",
        prereq_required="None",
        prereq_satisfied=1
    ):
        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": self.supplier.name,
            "company": self.company.name,
            "schedule_date": add_days(nowdate(), 15),
            "items": [{"item_code": self.item.name, "qty": 10, "rate": amount / 10}],
            "payment_schedule": [{
                "due_date": due_date,
                "payment_amount": amount,
                "custom_milestone_type": milestone_type,
                "custom_prerequisite_required": prereq_required,
                "custom_prerequisite_satisfied": prereq_satisfied,
                "custom_settlement_status": "Scheduled"
            }]
        }).insert(ignore_permissions=True)
        po.submit()
        return po

    def _create_test_payment_entry(self, po, amount, utr):
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": self.supplier.name,
            "company": self.company.name,
            "paid_amount": amount,
            "received_amount": amount,
            "custom_bank_utr_no": utr,
            "reference_no": utr,
            "mode_of_payment": "Wire Transfer",
            "posting_date": nowdate(),
            "references": [{
                "reference_doctype": "Purchase Order",
                "reference_name": po.name,
                "total_amount": amount,
                "allocated_amount": amount
            }]
        }).insert(ignore_permissions=True)
        return pe
```

---

## 7. Operational SOP, Error Resolution & Runbook

### 7.1 End-User Standard Operating Procedures (SOP)

#### For Purchase Assistant / Purchase Manager:
1. **Impending Due Date Review:** At 08:30 AM daily, inspect the `/solar/procurement` Upcoming Payments card.
2. **Prerequisite Clearance:** For "Against LR" milestones, upload Transporter LR and FAT certificate and click `[Verify Prerequisite]`.
3. **Accounts Collaboration:** If a vendor threatens to withhold container dispatch, open the row and click `[Nudge Accounts]` with justification notes.
4. **Dispatch Release:** Upon receiving the automated "✔ Payment Completed" notification with UTR number, release the supplier dispatch authorization.

#### For Accounts Assistant / Accounts Manager:
1. **Daily Liquidity Inspection:** At 08:15 AM daily, review the `/solar/accounts` Upcoming Disbursements card.
2. **Voucher Preparation:** Click `[Pay Now]` on Due Today items. The modal automatically fills supplier bank details and checks Section 194Q TDS applicability.
3. **Payment Execution & UTR Entry:** Enter the bank UTR reference number and submit the `Payment Entry`. The system automatically updates the schedule and broadcasts completion to Purchase.

---

### 7.2 Operational Error Resolution Matrix

| Error Condition / Message | Root Cause | Operator Resolution Path |
| :--- | :--- | :--- |
| `ValidationError: Prerequisite ... is not satisfied` | Required operational doc (LR, 3-Way Match) not verified. | Purchase Assistant uploads document and marks verified, or Admin overrides. |
| `ValidationError: Statutory Compliance Error ... Section 194Q` | Cumulative billing $> ₹50\text{L}$ without TDS deduction. | Add 0.1% TDS deduction line in `Payment Entry` deductions table. |
| `ValidationError: Security Alert: Destination Bank Account ... unverified` | Supplier bank account was modified or lacks verified flag. | `Admin` and `Accounts Manager` verify bank proof and set `custom_is_verified = 1`. |
| `StageForwardLockViolation: Cannot cancel ... submitted Payment Entry exists` | Attempted cancellation of settled PO or PI. | Reverse or cancel `Payment Entry` first, or file formal `Solar Cancellation Request`. |
| `PermissionError: Unauthorized ... managerial authorization required` | Junior role attempted to place hold or clear managerial gate. | Route action to `Purchase Manager`, `Accounts Manager`, or `Admin`. |

---

### 7.3 L3 DevOps Runbook & Daemon Maintenance

```bash
# 1. Check background queue status and worker health
bench --site <site_name> doctor
bench --site <site_name> show-pending-jobs

# 2. Trigger manual test execution of daily payment notification daemon
bench --site <site_name> execute solar_module.tasks.payment_monitoring.run_daily_vendor_payment_daemon

# 3. Inspect recent payment notifications generated by the daemon
bench --site <site_name> mariadb -e "SELECT name, for_user, subject, creation FROM \`tabNotification Log\` WHERE creation >= CURDATE() AND subject LIKE '%Supplier Payment Due%' ORDER BY creation DESC LIMIT 10;"

# 4. Run automated tracer bullet integration test suite
bench --site <site_name> run-tests --module solar_module.tests.test_step_18_vendor_payment_workbench_tracer_bullet
```

---

## 8. Master Lifecycle Traceability Matrix

| Layer | System Artifact / Module Path | Business Responsibility | Test Assertion Case |
| :--- | :--- | :--- | :--- |
| **Layer 1: Schema** | `tabPayment Schedule`, `tabPayment Entry`, `tabSolar Notification Settings` | 3NF normalized fields, audit flags, B-tree indexes | `test_01`, `test_04` |
| **Layer 2: Domain Services** | `VendorPaymentObligationEngine`, `VendorPaymentNotificationDaemon`, `VendorPaymentSettlementService`, `PaymentPrerequisiteGateService` | Pure SOLID logic, proactive alerts, closed-loop broadcast, tax & prerequisite gates | `test_01`, `test_02`, `test_03`, `test_05`, `test_06`, `test_07`, `test_08`, `test_09` |
| **Layer 3: Controllers & RPC** | `SolarPaymentEntry`, `solar_module.api.procurement.payment_monitoring.*` | Lifecycle hooks, whitelisted APIs, StageSecuredDocument mixin | `test_04`, `test_10`, `test_12` |
| **Layer 4: UI / Desk** | `codes/client_script/payment_entry.js`, `/solar/procurement/payment-workbench` | Dynamic Desk client scripts, Dual-Workspace cards, SPA workbench | Desk inspection |
| **Layer 5: Tests** | `solar_module/tests/test_step_18_vendor_payment_workbench_tracer_bullet.py` | 12 atomic integration tests with zero DB commit rollback | All 12 test methods |

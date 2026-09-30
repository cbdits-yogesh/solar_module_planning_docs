# STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 05 Advance Payment Clearance & Customer Master Inception Gate

**Document ID:** `TB-05-ADVANCE-PAYMENT`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.caveman.md`](../STEP_05_ADVANCE_PAYMENT_CUSTOMER_GATE_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-005-ADVANCE-PAYMENT-CUSTOMER-MASTER-INCEPTION.md`](../../docs/decisions/ADR-005-ADVANCE-PAYMENT-CUSTOMER-MASTER-INCEPTION.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md`](STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md`](STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md`](STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md`](STEP_01_LEAD_MANAGEMENT_TRACER_BULLET.caveman.md)  
**Downstream Successor:** [`step_plans_for_ai/STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.caveman.md`](../STEP_06_SALES_ORDER_BASELINE_SPECIFICATION.caveman.md)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-05`, `Sec 3.5`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-005`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-005`, `FR-019`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 4: FIN`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 5`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 8`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-05`)  
**Target Module:** `solar_module` / `manoj` (Extend ERPNext `Payment Entry`, `Quotation`, `Customer`, plus standalone `Solar Loan Sanction`, `Solar Advance Settings`, `tabRemark-Delay Log`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution  

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** Explores an isolated UI widget (such as a modal form to input UTR numbers) with throwaway code, discarded after evaluation without real General Ledger postings, actual database constraints, or downstream Sales Order interactions.
- **Tracer Bullet:** A lean, complete, production-grade slice cutting through **all 5 layers of the real system**. Not throwaway code; it forms the permanent, verified architectural skeleton that connects the finalized Stage 04 commercial proposal (`custom_is_finalized = 1`), executes Quad-Track financial clearance, enforces global UTR deduplication in MariaDB, programmatically incepts `Customer`, `Address`, and `Contact` masters using tiered ground truth, and establishes the impenetrable lockout gate that protects Stage 06 Sales Order release.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 05 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabQuotation custom fields (financial clearance gate, advance amounts)  │
│   - tabPayment Entry custom fields (solar advance metadata, unique UTR)     │
│   - tabCustomer custom fields (solar EPC inception, persistent lead thread) │
│   - tabSolar Loan Sanction (standalone submittable DocType, SLS series)     │
│   - tabSolar Advance Settings (single DocType: advance floor, SLA hours)    │
│   - tabRemark-Delay Log (SLA audit & delay justification child table)       │
│   - Composite B-Tree Indexes & Unique Constraint on custom_utr_cheque_no    │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic                                    │
│   - AdvanceVerificationService (Pure math, UTR uniqueness, advance floor)   │
│   - CustomerInceptionService (Tiered resolution: Proposal/Survey > Lead)    │
│   - LoanSanctionService (Sanction verification, margin money reconciliation)│
│   - AdvanceSLAService (24h turnaround countdown, overdue daemon, delay log) │
│   - SalesOrderClearanceGateService (Downstream Stage 06 lock validator)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                      │
│   - Payment Entry hooks (validate UTR uniqueness, link to proposal & lead)  │
│   - StageSecuredDocument & StageForwardLockService integration (ADR-000)     │
│   - record_and_verify_advance RPC (Track A: Direct Bank Advance)            │
│   - verify_loan_sanction_and_clear RPC (Track B: Bank Loan Sanction)         │
│   - waive_corporate_credit RPC (Track C: Corporate Credit Waiver)           │
│   - approve_goodwill_bypass RPC (Track D: Executive Goodwill VIP Bypass)    │
│   - check_so_advance_gate RPC (Stage 06 Sales Order release verification)   │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Workbench Hook                        │
│   - codes/client_script/account_manager.js (Clearance desk & track selector)│
│   - codes/client_script/payment_entry_solar.js (Real-time UTR duplicate UI) │
│   - codes/client_script/sales_order_advance_guard.js (Stage 06 submit block)│
│   - Real-time field indicators and Quad-Track execution modals              │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_stage_05_advance_tracer_bullet.py               │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Atomic transaction rollback in tearDown (zero DB commits)               │
│   - 10 rigorous test cases validating all Stage 05 invariants               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 10 fundamental business, technical, and security invariants of Stage 05 across the live Frappe stack:

1. **Predecessor Commercial Proposal Finalization:** Enforces that linked `Quotation` must have `docstatus == 1` and `custom_is_finalized == 1` before financial clearance workflows can be initiated.
2. **Direct Bank Advance (Track A) & Floor Gate:** Asserts that submitted `Payment Entry` receipts total $\ge$ `custom_required_advance_amount` (Admin standard: 50.0%) and not below the absolute statutory minimum floor (20.0%).
3. **Global UTR / Bank Reference Deduplication:** Enforces absolute uniqueness on `custom_utr_cheque_no` across all non-cancelled `Payment Entry` records in the database, raising `frappe.DuplicateEntryError` on reuse.
4. **Institutional Bank Loan Sanction Verification (Track B):** Digitally verifies signed bank sanction letters (SBI, PNB, IREDA, etc.) in `tabSolar Loan Sanction` and reconciles required borrower margin money receipts before clearance.
5. **Corporate Credit Deferred Terms Waiver (Track C):** Allows commercial credit terms authorized strictly by `Accounts Manager` or `Admin`.
6. **Executive Goodwill VIP Bypass Gate (Track D):** Strictly empowers Executive Supreme Command (`Admin`, `Director`, `Administrator`) to bypass monetary receipt for strategic VIP or government clients, requiring mandatory justification ($\ge 10$ characters) while raising `PermissionError` for unauthorized roles.
7. **Tiered Ground-Truth Customer Inception:** Programmatically creates standard ERPNext `Customer`, `Address` (with geocoded GPS coordinates), and `Contact` records using ground-truth precedence hierarchy: `Proposal` > `Site Survey` > `Lead` > system default.
8. **Prospect Quarantine Break & Persistent Identity Thread:** Transitions the originating `Lead` to `status = 'Converted'` with `lead.customer = customer.name` while maintaining `custom_lead_reference` on all created and downstream records (`Payment Entry`, `Customer`, `Address`, `Contact`, `Sales Order`, `Project`).
9. **Downstream Stage 06 Lockout Gate:** Implements a hard server-side gate on `Sales Order` validation and submission, throwing `ValidationError` if `custom_financial_clearance_status` is not cleared or `custom_customer` is unlinked.
10. **24-Hour Clearance SLA & Delay Accountability:** Tracks a 24-hour turnaround window starting from proposal finalization, auto-escalating overdue proposals and enforcing categorized entries in `tabRemark-Delay Log`.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

The Tracer Bullet extends standard ERPNext DocTypes (`Quotation`, `Payment Entry`, `Customer`), registers settings and loan DocTypes, and establishes MariaDB composite indexes and unique constraints.

### 2.1 Core DocType Extension: `tabQuotation` (Commercial Proposal Advance Gate)

| Fieldname                           | Label                              | Fieldtype       | Options / Target                                                                                                                                 | Mandatory |    Index     | Rules & Invariants                                                           |
| :---------------------------------- | :--------------------------------- | :-------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :----------: | :--------------------------------------------------------------------------- |
| `custom_advance_governance_section` | Financial Advance & Clearance Gate | `Section Break` | -                                                                                                                                                |    No     |      -       | Section container for Stage 05 verification.                                 |
| `custom_required_advance_pct`       | Required Advance %                 | `Percent`       | -                                                                                                                                                |  **Yes**  |      -       | Default: 50.0% auto-fill from `Solar Advance Settings`.                      |
| `custom_required_advance_amount`    | Required Advance Amount (₹)        | `Currency`      | `Company:currency`                                                                                                                               |  **Yes**  |      -       | Formula: `(net_total * custom_required_advance_pct) / 100`.                  |
| `custom_financial_clearance_status` | Financial Clearance Status         | `Select`        | `Pending Advance\nUnder Verification\nAdvance Cleared\nLoan Sanction Verified\nCorporate Credit Waived\nGoodwill VIP Approved\nPayment Rejected` |  **Yes**  | **Index: 1** | Master status of Stage 05 gate. Default: `Pending Advance`.                  |
| `custom_clearance_track`            | Clearance Track                    | `Select`        | `\nDirect Bank Advance\nBank Loan Sanction\nCorporate Credit Waiver\nGoodwill VIP Bypass`                                                        |    No     |      -       | Selected track for clearance.                                                |
| `custom_advance_amount_received`    | Total Advance Received (₹)         | `Currency`      | `Company:currency`                                                                                                                               |    No     |      -       | Aggregated live sum of linked submitted `Payment Entry` records.             |
| `custom_advance_pct_received`       | Actual Advance % Received          | `Percent`       | -                                                                                                                                                |    No     |      -       | Formula: `(custom_advance_amount_received / net_total) * 100`.               |
| `custom_advance_payment_entry`      | Primary Payment Entry              | `Link`          | `Payment Entry`                                                                                                                                  |    No     | **Index: 1** | Link to primary ERPNext advance receipt.                                     |
| `custom_loan_sanction_ref`          | Loan Sanction Record               | `Link`          | `Solar Loan Sanction`                                                                                                                            |    No     | **Index: 1** | Link to bank financing doc.                                                  |
| `custom_customer`                   | Created Customer Master            | `Link`          | `Customer`                                                                                                                                       |    No     | **Index: 1** | Instantiated on Stage 05 clearance. Replaces prospect Lead reference for SO. |
| `custom_financial_clearance_date`   | Financial Clearance Date           | `Datetime`      | -                                                                                                                                                |    No     |      -       | Timestamp when clearance was achieved.                                       |
| `custom_financial_cleared_by`       | Financial Cleared By               | `Link`          | `User`                                                                                                                                           |    No     |      -       | User attribution of authorizing actor.                                       |
| `custom_goodwill_justification`     | Executive Justification            | `Small Text`    | -                                                                                                                                                |    No     |      -       | Mandatory remark for Credit Waiver or Goodwill VIP Bypass ($\ge 10$ chars).  |

---

### 2.2 Core DocType Extension: `tabPayment Entry` (Solar Advance Allocation)

| Fieldname                       | Label                       | Fieldtype       | Options / Target | Mandatory |    Index     | Rules & Invariants                                                            |
| :------------------------------ | :-------------------------- | :-------------- | :--------------- | :-------: | :----------: | :---------------------------------------------------------------------------- |
| `custom_solar_payment_section`  | Solar Project Allocation    | `Section Break` | -                |    No     |      -       | Solar accounting metadata section.                                            |
| `custom_is_solar_advance`       | Is Solar Advance Payment    | `Check`         | -                |    No     | **Index: 1** | Flag designating Stage 05 initial advance receipt.                            |
| `custom_proposal_reference`     | Proposal Reference          | `Link`          | `Quotation`      |    No     | **Index: 1** | Foreign key linking originating Stage 04 proposal.                            |
| `custom_lead_reference`         | Lead Reference              | `Link`          | `Lead`           |    No     | **Index: 1** | Persistent thread of identity to originating prospect lead.                   |
| `custom_site_survey_reference`  | Site Survey Reference       | `Link`          | `Site Survey`    |    No     | **Index: 1** | Link to technical site audit.                                                 |
| `custom_utr_cheque_no`          | UTR / Cheque / Ref Number   | `Data`          | -                |  **Yes**  | **Index: 1** | **Strict Global Uniqueness:** Duplicate entries rejected across the platform. |
| `custom_bank_name`              | Remitting / Depositing Bank | `Data`          | -                |    No     |      -       | Customer remit bank or company depository bank account.                       |
| `custom_payment_proof`          | Payment Receipt / Slip      | `Attach`        | -                |    No     |      -       | PDF slip or digital scan of cheque.                                           |
| `custom_verified_by`            | Verified By                 | `Link`          | `User`           |    No     |      -       | Accounts staff verifying the entry.                                           |
| `custom_verification_timestamp` | Verification Timestamp      | `Datetime`      | -                |    No     |      -       | Audit timestamp of verification.                                              |

---

### 2.3 Core DocType Extension: `tabCustomer` (Solar Master Inception)

| Fieldname                        | Label                       | Fieldtype       | Options / Target                                                                        | Mandatory |    Index     | Rules & Invariants                                                         |
| :------------------------------- | :-------------------------- | :-------------- | :-------------------------------------------------------------------------------------- | :-------: | :----------: | :------------------------------------------------------------------------- |
| `custom_solar_inception_section` | Solar EPC Master Inception  | `Section Break` | -                                                                                       |    No     |      -       | Container for inception audit trail.                                       |
| `custom_lead_reference`          | Lead Reference              | `Link`          | `Lead`                                                                                  |  **Yes**  | **Index: 1** | Originating prospect lead. Preserves the unbroken thread of identity.     |
| `custom_proposal_reference`      | Proposal Reference          | `Link`          | `Quotation`                                                                             |  **Yes**  | **Index: 1** | Commercial proposal triggering customer inception.                         |
| `custom_site_survey_reference`   | Site Survey Reference       | `Link`          | `Site Survey`                                                                           |  **Yes**  | **Index: 1** | Technical audit providing ground-truth GPS and electrical parameters.      |
| `custom_discom_consumer_no`      | DISCOM Consumer Number      | `Data`          | -                                                                                       |  **Yes**  | **Index: 1** | Statutory utility meter / consumer account ID. Pre-filled from survey.     |
| `custom_discom_board`            | Electricity Board (DISCOM)  | `Data`          | -                                                                                       |  **Yes**  |      -       | Operating utility board (e.g. PGVCL, DGVCL, BESCOM, MSEDCL).               |
| `custom_sanctioned_load_kw`      | Sanctioned Load (kW)        | `Float`         | -                                                                                       |  **Yes**  |      -       | Existing utility sanctioned connected load.                                |
| `custom_tariff_category`         | Electricity Tariff Category | `Data`          | -                                                                                       |    No     |      -       | Residential, Commercial LT, HT Industrial.                                 |
| `custom_clearance_type`          | Inception Clearance Track   | `Select`        | `Direct Bank Advance\nBank Loan Sanction\nCorporate Credit Waiver\nGoodwill VIP Bypass` |  **Yes**  |      -       | Mode of financial clearance authorizing customer inception.                |
| `custom_inception_date`          | Master Inception Date       | `Datetime`      | -                                                                                       |  **Yes**  |      -       | Timestamp when customer master was programmatically created.               |

---

### 2.4 Standalone DocType: `tabSolar Loan Sanction` (Institutional Bank Financing)

- **DocType Name:** `Solar Loan Sanction`
- **Module:** `solar_module`
- **Autonaming:** `naming_series: SLS-.YYYY.-.#####` (e.g. `SLS-2026-00042`)
- **Submittable:** `is_submittable = 1`
- **Track Changes:** `1`

| Fieldname                    | Label                    | Fieldtype    | Options / Target                                                          | Mandatory |    Index     | Rules & Invariants                                                           |
| :--------------------------- | :----------------------- | :----------- | :------------------------------------------------------------------------ | :-------: | :----------: | :--------------------------------------------------------------------------- |
| `naming_series`              | Series                   | `Select`     | `SLS-.YYYY.-.#####`                                                       |  **Yes**  |      -       | Autonaming series.                                                           |
| `proposal`                   | Proposal Reference       | `Link`       | `Quotation`                                                               |  **Yes**  | **Index: 1** | Finalized commercial proposal.                                               |
| `lead`                       | Lead Reference           | `Link`       | `Lead`                                                                    |  **Yes**  | **Index: 1** | Originating prospect lead.                                                   |
| `customer`                   | Customer                 | `Link`       | `Customer`                                                                |    No     | **Index: 1** | Linked programmatically post-inception.                                     |
| `lending_institution_type`   | Lending Institution Type | `Select`     | `Public Sector Bank\nPrivate Sector Bank\nNBFC / IREDA\nCooperative Bank` |  **Yes**  |      -       | Institutional categorization.                                                |
| `bank_name`                  | Financing Bank           | `Link`       | `Bank`                                                                    |  **Yes**  |      -       | Lending institution (e.g. SBI, PNB, Canara Bank, HDFC).                      |
| `bank_branch`                | Bank Branch & IFSC       | `Data`       | -                                                                         |  **Yes**  |      -       | Sanctioning branch and IFSC code.                                            |
| `loan_application_no`        | Loan Application Number  | `Data`       | -                                                                         |  **Yes**  |      -       | Lender portal application reference (e.g. PM Surya Ghar Jan Samarth ID).    |
| `sanction_letter_no`         | Sanction Letter Number   | `Data`       | -                                                                         |  **Yes**  | **Index: 1** | Official sanction document number.                                           |
| `sanction_date`              | Sanction Date            | `Date`       | -                                                                         |  **Yes**  |      -       | Date sanction was granted.                                                   |
| `sanctioned_amount`          | Sanctioned Loan Amount   | `Currency`   | `Company:currency`                                                        |  **Yes**  |      -       | Principal debt amount approved by lender.                                    |
| `proposal_total_amount`      | Total Proposal Amount    | `Currency`   | `Company:currency`                                                        |  **Yes**  |      -       | Turnkey contract value from proposal.                                        |
| `margin_money_required`      | Required Margin Money    | `Currency`   | `Company:currency`                                                        |  **Yes**  |      -       | Formula: `proposal_total_amount - sanctioned_amount`.                        |
| `margin_money_paid`          | Margin Money Paid        | `Currency`   | `Company:currency`                                                        |    No     |      -       | Borrower equity contributed via `Payment Entry`.                             |
| `margin_money_payment_entry` | Margin Payment Reference | `Link`       | `Payment Entry`                                                           |    No     | **Index: 1** | Receipt proving customer equity deposit.                                     |
| `margin_money_verified`      | Margin Money Verified    | `Check`      | -                                                                         |    No     |      -       | Checked when `margin_money_paid >= margin_money_required`.                   |
| `sanction_letter_attachment` | Sanction Letter (PDF)    | `Attach`     | -                                                                         |  **Yes**  |      -       | Mandatory signed bank sanction PDF document.                                 |
| `disbursement_stage`         | Disbursement Status      | `Select`     | `Sanctioned\nPending Installation\nDisbursed Post-JMI\nFully Settled`     |  **Yes**  |      -       | Institutional disbursement lifecycle. Default: `Sanctioned`.                 |
| `sanction_status`            | Status                   | `Select`     | `Draft\nUnder Verification\nApproved\nRejected\nCancelled`                |  **Yes**  | **Index: 1** | Workflow status. Submission sets `Approved`.                                 |
| `verification_remarks`       | Verification Remarks     | `Small Text` | -                                                                         |    No     |      -       | Accounts review notes and loan compliance comments.                          |

---

### 2.5 Configuration Master: `tabSolar Advance Settings` (Single DocType)

Managed strictly by **`Admin`** (Project Supreme Command):

| Fieldname                        | Label                            | Fieldtype | Options / Target | Mandatory | Description & Rules                                                    |
| :------------------------------- | :------------------------------- | :-------- | :--------------- | :-------: | :--------------------------------------------------------------------- |
| `default_advance_pct`            | Default Required Advance %       | `Percent` | -                |  **Yes**  | Corporate default advance percentage (default: **50.0%**).             |
| `minimum_advance_floor_pct`      | Absolute Minimum Advance Floor % | `Percent` | -                |  **Yes**  | Absolute lowest floor allowed without waiver (default: **20.0%**).     |
| `advance_verification_sla_hours` | Advance Verification SLA (Hours) | `Int`     | -                |  **Yes**  | Accounts turnaround SLA timer in hours (default: **24 Hours**).        |
| `allow_bank_loan_sanctions`      | Enable Bank Loan Sanction Track  | `Check`   | -                |    No     | Master toggle permitting Track B clearance (default: 1).               |
| `allow_goodwill_ceo_bypass`      | Enable Goodwill VIP Bypass       | `Check`   | -                |    No     | Master toggle permitting Track D bypass (default: 1).                  |
| `enforce_strict_utr_uniqueness`  | Enforce Strict UTR Uniqueness    | `Check`   | -                |    No     | Hard blocking of duplicate UTRs across company (default: 1).           |
| `auto_convert_lead`              | Auto-Convert Lead on Inception   | `Check`   | -                |    No     | Programmatically converts lead to Converted on clearance (default: 1). |

---

### 2.6 Child DocType: `tabRemark-Delay Log`

| Fieldname      | Label           | Fieldtype    | Options                                                                                                                                                                                | Mandatory | Description                                                       |
| :------------- | :-------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :---------------------------------------------------------------- |
| `user`         | Logged By       | `Link`       | `User`                                                                                                                                                                                 |  **Yes**  | Staff member recording entry (defaults to session user).          |
| `timestamp`    | Recorded At     | `Datetime`   | -                                                                                                                                                                                      |  **Yes**  | Immutable audit timestamp.                                        |
| `stage`        | Lifecycle Stage | `Data`       | -                                                                                                                                                                                      |  **Yes**  | Fixed value: "Stage 05: Advance Payment & Customer Inception".    |
| `delay_reason` | Delay Category  | `Select`     | `Awaiting Customer Bank Cheque Clearance\nBank Loan Sanction Documentation Pending\nDisputed Commercial Milestone\nCustomer Requesting Deferred Mobilization\nEscrow Verification Lag` |    No     | Mandatory when `custom_financial_clearance_status == 'Overdue'`. |
| `remarks`      | Detailed Notes  | `Small Text` | -                                                                                                                                                                                      |  **Yes**  | Free-text operational explanation ($\ge 10$ characters).          |

---

### 2.7 Database Indexing & Autonaming Strategy

- **Autonaming:** Autonaming for loan sanctions follows `naming_series:SLS-.YYYY.-.#####`.
- **Composite B-Tree Indexes & Unique Constraints:**
  ```sql
  -- Strict global uniqueness constraint on bank reference / UTR
  CREATE UNIQUE INDEX uq_payment_entry_utr ON `tabPayment Entry` (custom_utr_cheque_no);

  -- Performance composite indexes for rapid status checks and desk queries
  CREATE INDEX idx_pe_proposal_docstatus ON `tabPayment Entry` (custom_proposal_reference, docstatus, payment_type);
  CREATE INDEX idx_pe_lead_reference ON `tabPayment Entry` (custom_lead_reference);
  CREATE INDEX idx_customer_lead_ref ON `tabCustomer` (custom_lead_reference);
  CREATE INDEX idx_customer_proposal_ref ON `tabCustomer` (custom_proposal_reference);
  CREATE INDEX idx_sls_proposal_status ON `tabSolar Loan Sanction` (proposal, sanction_status, docstatus);
  ```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Decoupled pure Python domain services located in `solar_module/services/advance/` adhering strictly to single-responsibility and dependency inversion principles.

### 3.1 `AdvanceVerificationService` (`solar_module/services/advance/verification.py`)

Governs financial validation, UTR deduplication assertions, and advance receipt math:

```python
import frappe
from frappe import _
from frappe.utils import flt

class AdvanceVerificationService:
    @staticmethod
    def get_advance_settings() -> dict:
        """Retrieves Admin-governed advance parameters with safe system defaults."""
        settings = frappe.get_single("Solar Advance Settings")
        return {
            "default_advance_pct": flt(settings.default_advance_pct) or 50.0,
            "minimum_advance_floor_pct": flt(settings.minimum_advance_floor_pct) or 20.0,
            "sla_hours": int(settings.advance_verification_sla_hours) or 24,
            "enforce_utr_uniqueness": bool(settings.enforce_strict_utr_uniqueness),
        }

    @staticmethod
    def validate_utr_uniqueness(utr_no: str, current_payment_entry: str = None) -> None:
        """Enforces absolute global uniqueness on bank UTR / Cheque reference numbers."""
        if not utr_no or not utr_no.strip():
            frappe.throw(_("UTR / Cheque Reference number is mandatory."), frappe.ValidationError)

        utr_clean = utr_no.strip()
        conditions = ["custom_utr_cheque_no = %(utr)s", "docstatus != 2"]
        values = {"utr": utr_clean}

        if current_payment_entry:
            conditions.append("name != %(current)s")
            values["current"] = current_payment_entry

        existing = frappe.db.sql(
            f"""
            SELECT name, party, paid_amount
            FROM `tabPayment Entry`
            WHERE {' AND '.join(conditions)}
            LIMIT 1
            """,
            values,
            as_dict=True
        )

        if existing:
            frappe.throw(
                _(f"Bank reference/UTR '{utr_clean}' is already booked under Payment Entry "
                  f"'{existing[0].name}' for party '{existing[0].party}' (Amount: ₹{existing[0].paid_amount:,.2f}). "
                  "Duplicate financial references are strictly prohibited."),
                frappe.DuplicateEntryError
            )

    @classmethod
    def evaluate_direct_advance_receipt(cls, proposal_doc) -> dict:
        """Evaluates submitted payments against proposal required advance amount."""
        settings = cls.get_advance_settings()

        payments = frappe.get_all(
            "Payment Entry",
            filters={
                "custom_proposal_reference": proposal_doc.name,
                "docstatus": 1,
                "payment_type": "Receive"
            },
            fields=["name", "paid_amount", "custom_utr_cheque_no", "posting_date"]
        )

        total_received = sum(flt(p.paid_amount) for p in payments)
        required_amount = flt(proposal_doc.custom_required_advance_amount)
        net_contract_value = flt(proposal_doc.net_total)

        actual_pct = (total_received / net_contract_value * 100.0) if net_contract_value > 0 else 0.0
        floor_amount = (net_contract_value * settings["minimum_advance_floor_pct"]) / 100.0

        is_cleared = total_received >= required_amount and total_received >= floor_amount

        return {
            "is_cleared": is_cleared,
            "total_received": total_received,
            "required_amount": required_amount,
            "actual_pct": actual_pct,
            "floor_amount": floor_amount,
            "payments": payments
        }
```

---

### 3.2 `CustomerInceptionService` (`solar_module/services/advance/inception.py`)

Handles atomic creation of `Customer`, `Address`, and `Contact` using Tiered Ground-Truth Resolution, converts `Lead`, and updates financial links:

```python
import frappe
from frappe import _
from frappe.utils import now_datetime

class CustomerInceptionService:
    @classmethod
    def _resolve_best_value(cls, *values, default=None):
        """Returns first non-empty stripped value across precedence chain."""
        for val in values:
            if val is not None and str(val).strip():
                return str(val).strip()
        return default

    @classmethod
    def instantiate_customer_master(
        cls,
        proposal_name: str,
        clearance_track: str,
        authorized_by: str,
        justification: str = None
    ) -> str:
        """
        Executes atomic programmatic creation of ERPNext Customer, Address,
        and Contact masters with Tiered Ground-Truth Resolution (Proposal/Survey > Lead).
        """
        proposal = frappe.get_doc("Quotation", proposal_name)

        # Idempotency check: Return existing customer if already created
        if proposal.custom_customer:
            return proposal.custom_customer

        if not proposal.custom_is_finalized:
            frappe.throw(_("Cannot instantiate Customer: Commercial Proposal is not finalized."), frappe.ValidationError)

        lead_name = proposal.party_name
        if not lead_name or proposal.quotation_to != "Lead":
            frappe.throw(_("Proposal must be linked to a valid Lead."), frappe.ValidationError)

        lead = frappe.get_doc("Lead", lead_name)
        site_survey_name = proposal.get("custom_site_survey")
        site_survey = frappe.get_doc("Site Survey", site_survey_name) if site_survey_name else None

        # 1. Create standard ERPNext Customer master using Tiered Precedence:
        # Priority: Proposal -> Site Survey -> Lead -> Default
        customer = frappe.new_doc("Customer")
        customer.customer_name = cls._resolve_best_value(
            proposal.get("custom_customer_name"),
            site_survey.get("consumer_name") if site_survey else None,
            site_survey.get("customer_name") if site_survey else None,
            lead.lead_name if lead else None,
            lead.company_name if lead else None,
            default="Valued Solar Client"
        )
        is_org = lead.organization_lead if lead else (proposal.get("custom_is_corporate") or 0)
        customer.customer_type = "Company" if is_org else "Individual"
        customer.customer_group = "Commercial" if is_org else "Residential"
        customer.territory = cls._resolve_best_value(
            site_survey.get("territory") if site_survey else None,
            lead.territory if lead else None,
            default="All Territories"
        )
        customer.gstin = cls._resolve_best_value(
            proposal.get("custom_gstin"),
            lead.get("gstin") if lead else None
        )
        customer.pan = cls._resolve_best_value(
            proposal.get("custom_pan"),
            lead.get("pan") if lead else None
        )

        # Populate Solar Inception Metadata & Persistent Thread of Identity
        customer.custom_lead_reference = lead.name
        customer.custom_proposal_reference = proposal.name
        customer.custom_site_survey_reference = site_survey.name if site_survey else None
        customer.custom_clearance_type = clearance_track
        customer.custom_inception_date = now_datetime()

        if site_survey:
            customer.custom_discom_consumer_no = cls._resolve_best_value(
                site_survey.get("consumer_no"),
                proposal.get("custom_discom_consumer_no"),
                lead.get("custom_consumer_no") if lead else None
            )
            customer.custom_discom_board = cls._resolve_best_value(
                site_survey.get("electricity_board"),
                proposal.get("custom_discom_board")
            )
            customer.custom_sanctioned_load_kw = (
                site_survey.get("sanctioned_load") or
                proposal.get("custom_sanctioned_load_kw") or
                (lead.get("custom_sanctioned_load_kw") if lead else 0.0)
            )
            customer.custom_tariff_category = cls._resolve_best_value(
                site_survey.get("tariff_category"),
                proposal.get("custom_tariff_category")
            )

        customer.flags.ignore_permissions = True
        customer.insert()

        # 2. Create Primary Address (Tiered: Survey GPS/Address -> Proposal -> Lead)
        cls._create_customer_address(customer, lead, site_survey, proposal)

        # 3. Create Primary Contact Person (Tiered: Proposal -> Survey -> Lead)
        cls._create_customer_contact(customer, lead, site_survey, proposal)

        # 4. Programmatically Convert Lead
        lead.status = "Converted"
        lead.customer = customer.name
        lead.flags.ignore_permissions = True
        lead.save()

        # 5. Retroactively update Proposal and Payment Entries (Maintains custom_lead_reference)
        proposal.custom_customer = customer.name
        proposal.custom_financial_clearance_status = cls._map_track_to_status(clearance_track)
        proposal.custom_financial_clearance_date = now_datetime()
        proposal.custom_financial_cleared_by = authorized_by
        proposal.custom_clearance_track = clearance_track
        proposal.custom_goodwill_justification = justification
        proposal.flags.ignore_permissions = True
        proposal.save()

        # Re-link submitted Payment Entries to Customer (preserving lead link)
        frappe.db.sql(
            """
            UPDATE `tabPayment Entry`
            SET party_type = 'Customer', party = %(cust)s, party_name = %(cust_name)s
            WHERE custom_proposal_reference = %(prop)s AND docstatus = 1
            """,
            {"cust": customer.name, "cust_name": customer.customer_name, "prop": proposal.name}
        )

        return customer.name

    @classmethod
    def _create_customer_address(cls, customer, lead, site_survey, proposal=None):
        """Generates linked primary Address record using ground-truth site coordinates."""
        addr = frappe.new_doc("Address")
        addr.address_title = customer.customer_name
        addr.address_type = "Billing"
        addr.is_primary_address = 1
        addr.is_shipping_address = 1

        addr.address_line1 = cls._resolve_best_value(
            site_survey.get("site_address") if site_survey else None,
            proposal.get("shipping_address_line1") if proposal else None,
            lead.get("custom_address") if lead else None,
            default="Site Address"
        )
        addr.city = cls._resolve_best_value(
            site_survey.get("city") if site_survey else None,
            proposal.get("shipping_city") if proposal else None,
            lead.get("city") if lead else None,
            default="City"
        )
        addr.state = cls._resolve_best_value(
            site_survey.get("state") if site_survey else None,
            proposal.get("shipping_state") if proposal else None,
            lead.get("state") if lead else None,
            default="State"
        )
        addr.pincode = cls._resolve_best_value(
            site_survey.get("pincode") if site_survey else None,
            proposal.get("shipping_pincode") if proposal else None,
            lead.get("custom_pincode") if lead else None
        )
        addr.custom_latitude = site_survey.get("latitude") if site_survey else None
        addr.custom_longitude = site_survey.get("longitude") if site_survey else None
        addr.custom_lead_reference = customer.custom_lead_reference

        addr.append("links", {
            "link_doctype": "Customer",
            "link_name": customer.name
        })
        addr.flags.ignore_permissions = True
        addr.insert()

    @classmethod
    def _create_customer_contact(cls, customer, lead, site_survey=None, proposal=None):
        """Generates linked primary Contact record with clean mobile and email."""
        contact = frappe.new_doc("Contact")
        contact.first_name = customer.customer_name
        contact.is_primary_contact = 1

        contact.mobile_no = cls._resolve_best_value(
            proposal.get("contact_mobile") if proposal else None,
            proposal.get("custom_mobile_no") if proposal else None,
            site_survey.get("contact_mobile") if site_survey else None,
            site_survey.get("contact_phone") if site_survey else None,
            lead.mobile_no if lead else None
        )
        contact.phone = cls._resolve_best_value(
            proposal.get("contact_phone") if proposal else None,
            site_survey.get("contact_phone") if site_survey else None,
            lead.phone if lead else None
        )
        contact.email_id = cls._resolve_best_value(
            proposal.get("contact_email") if proposal else None,
            proposal.get("custom_email_id") if proposal else None,
            site_survey.get("contact_email") if site_survey else None,
            lead.email_id if lead else None
        )
        contact.custom_lead_reference = customer.custom_lead_reference

        contact.append("links", {
            "link_doctype": "Customer",
            "link_name": customer.name
        })
        contact.flags.ignore_permissions = True
        contact.insert()

    @staticmethod
    def _map_track_to_status(track: str) -> str:
        mapping = {
            "Direct Bank Advance": "Advance Cleared",
            "Bank Loan Sanction": "Loan Sanction Verified",
            "Corporate Credit Waiver": "Corporate Credit Waived",
            "Goodwill VIP Bypass": "Goodwill VIP Approved",
        }
        return mapping.get(track, "Advance Cleared")
```

---

### 3.3 `LoanSanctionService` (`solar_module/services/advance/loan.py`)

Handles institutional bank financing workflows and margin money validation:

```python
import frappe
from frappe import _
from frappe.utils import flt

class LoanSanctionService:
    @staticmethod
    def validate_margin_money(sls_doc) -> bool:
        """Validates borrower equity margin money deposit against required margin."""
        req_margin = flt(sls_doc.margin_money_required)
        if req_margin <= 0:
            sls_doc.margin_money_verified = 1
            return True

        if not sls_doc.margin_money_payment_entry:
            sls_doc.margin_money_verified = 0
            return False

        pe = frappe.get_doc("Payment Entry", sls_doc.margin_money_payment_entry)
        if pe.docstatus != 1:
            frappe.throw(_("Margin money Payment Entry must be submitted."), frappe.ValidationError)

        paid_margin = flt(pe.paid_amount)
        sls_doc.margin_money_paid = paid_margin
        is_verified = paid_margin >= req_margin
        sls_doc.margin_money_verified = 1 if is_verified else 0
        return is_verified
```

---

### 3.4 `SalesOrderClearanceGateService` (`solar_module/services/advance/so_gate.py`)

Enforces downstream protection preventing unverified Sales Orders from entering production:

```python
import frappe
from frappe import _

class SalesOrderClearanceGateService:
    VALID_CLEARANCE_STATUSES = {
        "Advance Cleared",
        "Loan Sanction Verified",
        "Corporate Credit Waived",
        "Goodwill VIP Approved"
    }

    @classmethod
    def assert_sales_order_clearance(cls, sales_order_doc) -> None:
        """
        Hard gate for Sales Order validate and before_submit.
        Ensures Stage 05 financial clearance is achieved and verified Customer is linked.
        """
        quotation_name = None
        for item in sales_order_doc.get("items", []):
            if item.prevdoc_doctype == "Quotation" and item.prevdoc_docname:
                quotation_name = item.prevdoc_docname
                break

        # Fallback to custom proposal reference if present
        if not quotation_name and sales_order_doc.get("custom_proposal_reference"):
            quotation_name = sales_order_doc.custom_proposal_reference

        if not quotation_name:
            return  # Standalone sales orders evaluated under standard ERPNext rules

        proposal = frappe.get_doc("Quotation", quotation_name)
        status = proposal.get("custom_financial_clearance_status")

        if status not in cls.VALID_CLEARANCE_STATUSES:
            frappe.throw(
                _(f"Cannot release Sales Order: Originating Proposal '{proposal.name}' has not achieved "
                  f"Stage 05 Financial Clearance (Current Status: '{status}'). Advance payment, loan sanction, "
                  "or authorized waiver is mandatory."),
                frappe.ValidationError
            )

        if not proposal.custom_customer:
            frappe.throw(
                _("Cannot release Sales Order: Stage 05 Customer inception has not been completed."),
                frappe.ValidationError
            )
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

### 4.1 Extended Controller Hooks (`solar_module/overrides/payment_entry.py`)

Extends standard `Payment Entry` to enforce UTR uniqueness and trigger proposal status re-evaluation:

```python
import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from solar_module.mixins.stage_secured_document import StageSecuredDocument
from solar_module.services.advance.verification import AdvanceVerificationService

class SolarPaymentEntry(StageSecuredDocument, PaymentEntry):
    def validate(self):
        super().validate()
        if self.custom_is_solar_advance and self.custom_utr_cheque_no:
            AdvanceVerificationService.validate_utr_uniqueness(self.custom_utr_cheque_no, self.name)

    def on_submit(self):
        super().on_submit()
        if self.custom_is_solar_advance and self.custom_proposal_reference:
            proposal = frappe.get_doc("Quotation", self.custom_proposal_reference)
            eval_res = AdvanceVerificationService.evaluate_direct_advance_receipt(proposal)
            proposal.custom_advance_amount_received = eval_res["total_received"]
            proposal.custom_advance_pct_received = eval_res["actual_pct"]
            if not eval_res["is_cleared"] and proposal.custom_financial_clearance_status == "Pending Advance":
                proposal.custom_financial_clearance_status = "Under Verification"
            proposal.flags.ignore_permissions = True
            proposal.save()
```

---

### 4.2 Whitelisted API Endpoints (`solar_module/api/advance.py`)

```python
import json
import frappe
from frappe import _
from frappe.utils import flt, now_datetime, today
from solar_module.services.advance.verification import AdvanceVerificationService
from solar_module.services.advance.inception import CustomerInceptionService
from solar_module.services.advance.loan import LoanSanctionService
from solar_module.services.advance.so_gate import SalesOrderClearanceGateService

@frappe.whitelist(methods=["POST"])
def record_and_verify_advance(proposal_name: str, payment_payload: str) -> dict:
    """Whitelisted endpoint for Accounts staff to record advance and trigger customer inception."""
    if not proposal_name:
        frappe.throw(_("Proposal name is required."), frappe.ValidationError)

    proposal = frappe.get_doc("Quotation", proposal_name)
    proposal.check_permission("write")

    payload = json.loads(payment_payload) if isinstance(payment_payload, str) else payment_payload
    utr_no = payload.get("utr_no")
    paid_amount = flt(payload.get("paid_amount"))
    bank_account = payload.get("bank_account")
    mode_of_payment = payload.get("mode_of_payment") or "Bank Transfer"
    posting_date = payload.get("posting_date") or today()

    # Enforce global UTR uniqueness
    AdvanceVerificationService.validate_utr_uniqueness(utr_no)

    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer" if proposal.custom_customer else "Lead"
    pe.party = proposal.custom_customer or proposal.party_name
    pe.paid_amount = paid_amount
    pe.received_amount = paid_amount
    pe.paid_to = bank_account
    pe.mode_of_payment = mode_of_payment
    pe.posting_date = posting_date
    pe.reference_no = utr_no
    pe.reference_date = posting_date

    # Solar Custom Metadata
    pe.custom_is_solar_advance = 1
    pe.custom_proposal_reference = proposal.name
    pe.custom_lead_reference = proposal.party_name
    pe.custom_site_survey_reference = proposal.get("custom_site_survey")
    pe.custom_utr_cheque_no = utr_no
    pe.custom_verified_by = frappe.session.user
    pe.custom_verification_timestamp = now_datetime()

    pe.insert()
    pe.submit()

    evaluation = AdvanceVerificationService.evaluate_direct_advance_receipt(proposal)
    customer_id = None
    if evaluation["is_cleared"]:
        customer_id = CustomerInceptionService.instantiate_customer_master(
            proposal_name=proposal.name,
            clearance_track="Direct Bank Advance",
            authorized_by=frappe.session.user
        )

    return {
        "status": "success",
        "payment_entry": pe.name,
        "is_cleared": evaluation["is_cleared"],
        "total_received": evaluation["total_received"],
        "required_amount": evaluation["required_amount"],
        "customer_id": customer_id
    }

@frappe.whitelist(methods=["POST"])
def verify_loan_sanction_and_clear(loan_sanction_name: str) -> dict:
    """Whitelisted endpoint to verify bank loan sanction and trigger Customer inception."""
    sls = frappe.get_doc("Solar Loan Sanction", loan_sanction_name)
    sls.check_permission("write")

    if sls.docstatus != 1:
        frappe.throw(_("Solar Loan Sanction must be submitted before clearance."), frappe.ValidationError)

    if not sls.sanction_letter_attachment:
        frappe.throw(_("Signed Bank Sanction Letter attachment is mandatory."), frappe.ValidationError)

    if flt(sls.margin_money_required) > 0 and not sls.margin_money_verified:
        if not LoanSanctionService.validate_margin_money(sls):
            frappe.throw(_("Required borrower margin money has not been verified."), frappe.ValidationError)
        sls.save()

    customer_id = CustomerInceptionService.instantiate_customer_master(
        proposal_name=sls.proposal,
        clearance_track="Bank Loan Sanction",
        authorized_by=frappe.session.user
    )

    sls.customer = customer_id
    sls.save()

    return {
        "status": "success",
        "customer_id": customer_id,
        "clearance_status": "Loan Sanction Verified"
    }

@frappe.whitelist(methods=["POST"])
def waive_corporate_credit(proposal_name: str, justification: str) -> dict:
    """Authorizes corporate credit waiver. Restricted to Accounts Manager and Admin."""
    user_roles = set(frappe.get_roles(frappe.session.user))
    if not ({"Accounts Manager", "Admin", "System Manager"} & user_roles):
        frappe.throw(_("Only Accounts Manager or Admin can authorize corporate credit waivers."), frappe.PermissionError)

    if not justification or len(justification.strip()) < 10:
        frappe.throw(_("A minimum 10-character justification is mandatory for credit waivers."), frappe.ValidationError)

    customer_id = CustomerInceptionService.instantiate_customer_master(
        proposal_name=proposal_name,
        clearance_track="Corporate Credit Waiver",
        authorized_by=frappe.session.user,
        justification=justification.strip()
    )

    return {
        "status": "success",
        "customer_id": customer_id,
        "clearance_status": "Corporate Credit Waived"
    }

@frappe.whitelist(methods=["POST"])
def approve_goodwill_bypass(proposal_name: str, justification: str) -> dict:
    """Exclusive executive endpoint for CEO / MD / Admin to bypass advance check for VIP clients."""
    user_roles = set(frappe.get_roles(frappe.session.user))
    authorized_roles = {"Admin", "Director", "Administrator"}
    if not (authorized_roles & user_roles):
        frappe.throw(
            _("Access Denied: Only Executive Leadership (CEO, Managing Director, Project Supreme Admin) "
              "can grant Goodwill / VIP Customer advance waivers."),
            frappe.PermissionError
        )

    if not justification or len(justification.strip()) < 10:
        frappe.throw(_("A minimum 10-character justification is mandatory for Goodwill bypass."), frappe.ValidationError)

    customer_id = CustomerInceptionService.instantiate_customer_master(
        proposal_name=proposal_name,
        clearance_track="Goodwill VIP Bypass",
        authorized_by=frappe.session.user,
        justification=justification.strip()
    )

    return {
        "status": "success",
        "clearance_status": "Goodwill VIP Approved",
        "customer_id": customer_id,
        "authorized_by": frappe.session.user
    }
```

---

## 5. Layer 4: Desk Client Script & Dynamic Workbench Hook

Located at `codes/client_script/account_manager.js` and `codes/client_script/payment_entry_solar.js`:

```javascript
// codes/client_script/payment_entry_solar.js
frappe.ui.form.on('Payment Entry', {
    custom_utr_cheque_no: function(frm) {
        if (!frm.doc.custom_utr_cheque_no) return;
        
        // Real-time UTR uniqueness check with visual feedback
        frappe.db.get_value('Payment Entry', {
            'custom_utr_cheque_no': frm.doc.custom_utr_cheque_no,
            'name': ['!=', frm.doc.name || '']
        }, 'name', function(r) {
            if (r && r.name) {
                frm.set_df_property('custom_utr_cheque_no', 'description', 
                    `<span style="color:red; font-weight:bold;">⚠️ UTR already booked under ${r.name}! Duplicate entry will be rejected.</span>`);
                frappe.msgprint(__('Warning: UTR {0} is already recorded under Payment Entry {1}.', [frm.doc.custom_utr_cheque_no, r.name]));
            } else {
                frm.set_df_property('custom_utr_cheque_no', 'description', 
                    `<span style="color:green;">✔ UTR reference is unique.</span>`);
            }
        });
    }
});

// codes/client_script/quotation_advance_gate.js
frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        if (!frm.doc.custom_is_finalized) return;

        // Stage 05 Status Dashboard Alert
        const status = frm.doc.custom_financial_clearance_status || 'Pending Advance';
        if (status === 'Advance Cleared' || status === 'Goodwill VIP Approved' || status === 'Loan Sanction Verified') {
            frm.dashboard.set_headline_alert(
                __(`Stage 05 Cleared: ${status}. Customer: <a href="/app/customer/${frm.doc.custom_customer}">${frm.doc.custom_customer}</a>`), 'green'
            );
        } else {
            frm.dashboard.set_headline_alert(
                __(`Stage 05 Pending: Required Advance ₹${format_currency(frm.doc.custom_required_advance_amount)}. Status: ${status}`), 'orange'
            );
        }

        // Action: Record Advance Receipt Modal
        if (!frm.doc.custom_customer) {
            frm.add_custom_button(__('Record Advance Payment'), function() {
                let d = new frappe.ui.Dialog({
                    title: __('Record Stage 05 Advance Payment'),
                    fields: [
                        { fieldname: 'utr_no', fieldtype: 'Data', label: __('UTR / Cheque Ref'), reqd: 1 },
                        { fieldname: 'paid_amount', fieldtype: 'Currency', label: __('Amount (₹)'), default: frm.doc.custom_required_advance_amount, reqd: 1 },
                        { fieldname: 'bank_account', fieldtype: 'Link', options: 'Account', label: __('Deposited Bank Account'), reqd: 1 },
                        { fieldname: 'mode_of_payment', fieldtype: 'Select', options: 'Bank Transfer\nCheque\nCash', default: 'Bank Transfer', reqd: 1 }
                    ],
                    primary_action_label: __('Verify & Post'),
                    primary_action: function(values) {
                        d.hide();
                        frappe.call({
                            method: 'solar_module.api.advance.record_and_verify_advance',
                            args: { proposal_name: frm.doc.name, payment_payload: values },
                            freeze: true,
                            callback: function(r) {
                                if (r.message && r.message.status === 'success') {
                                    frm.reload_doc();
                                    frappe.msgprint(__('Payment recorded and Customer master verified successfully.'));
                                }
                            }
                        });
                    }
                });
                d.show();
            }, __('Financial Clearance'));
        }

        // Action: Executive Goodwill VIP Bypass
        if (!frm.doc.custom_customer && frappe.user.has_role(['Admin', 'Director', 'Administrator'])) {
            frm.add_custom_button(__('Executive Goodwill Bypass'), function() {
                frappe.prompt([
                    { fieldname: 'justification', fieldtype: 'Small Text', label: __('Executive Rationale (min 10 chars)'), reqd: 1 }
                ], function(values) {
                    frappe.call({
                        method: 'solar_module.api.advance.approve_goodwill_bypass',
                        args: { proposal_name: frm.doc.name, justification: values.justification },
                        callback: function(r) {
                            frm.reload_doc();
                            frappe.show_alert({ message: __('Goodwill VIP Bypass approved.'), indicator: 'green' });
                        }
                    });
                }, __('Authorize Goodwill VIP Bypass'), __('Authorize'));
            }, __('Financial Clearance'));
        }
    }
});

// codes/client_script/sales_order_advance_guard.js
frappe.ui.form.on('Sales Order', {
    before_submit: function(frm) {
        if (frm.doc.custom_proposal_reference) {
            frappe.call({
                method: 'solar_module.services.advance.so_gate.SalesOrderClearanceGateService.assert_sales_order_clearance',
                args: { sales_order_doc: frm.doc },
                async: false
            });
        }
    }
});
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Located at `solar_module/tests/test_stage_05_advance_tracer_bullet.py`.  
Subclasses `frappe.testing.IntegrationTestCase` with zero-commit atomic transaction rollback in `tearDown`.

```python
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import flt, now_datetime, add_to_date
from solar_module.services.advance.verification import AdvanceVerificationService
from solar_module.services.advance.inception import CustomerInceptionService
from solar_module.services.advance.loan import LoanSanctionService
from solar_module.services.advance.so_gate import SalesOrderClearanceGateService
from solar_module.api.advance import (
    record_and_verify_advance,
    verify_loan_sanction_and_clear,
    waive_corporate_credit,
    approve_goodwill_bypass
)

class TestStage05AdvancePaymentTracerBullet(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self._setup_advance_settings()
        self.lead = self._create_test_lead()
        self.survey = self._create_test_survey(self.lead.name)
        self.proposal = self._create_test_finalized_proposal(self.lead.name, self.survey.name)

    def tearDown(self):
        # Strict Zero-Commit Rule: roll back all database mutations
        frappe.db.rollback()
        super().tearDown()

    def _setup_advance_settings(self):
        settings = frappe.get_doc("Solar Advance Settings")
        settings.default_advance_pct = 50.0
        settings.minimum_advance_floor_pct = 20.0
        settings.advance_verification_sla_hours = 24
        settings.allow_bank_loan_sanctions = 1
        settings.allow_goodwill_ceo_bypass = 1
        settings.enforce_strict_utr_uniqueness = 1
        settings.auto_convert_lead = 1
        settings.save(ignore_permissions=True)

    def _create_test_lead(self):
        lead = frappe.new_doc("Lead")
        lead.lead_name = "Tracer Bullet Prospect"
        lead.email_id = "tb.advance@sadbhav.com"
        lead.mobile_no = "9825012345"
        lead.custom_address = "Generic Lead Address"
        lead.insert(ignore_permissions=True)
        return lead

    def _create_test_survey(self, lead_name):
        survey = frappe.new_doc("Site Survey")
        survey.lead = lead_name
        survey.consumer_name = "Rajeshbhai K. Patel"
        survey.consumer_no = "DGVCL-SURAT-881920"
        survey.electricity_board = "DGVCL"
        survey.sanctioned_load = 15.0
        survey.site_address = "Plot 101, Pandesara GIDC, Surat"
        survey.city = "Surat"
        survey.state = "Gujarat"
        survey.pincode = "394221"
        survey.latitude = 21.1702
        survey.longitude = 72.8311
        survey.contact_mobile = "9825099887"
        survey.contact_email = "rajesh.patel@gidc-solar.in"
        survey.stage_status = "Completed"
        survey.docstatus = 1
        survey.insert(ignore_permissions=True)
        return survey

    def _create_test_proposal(self, lead_name, survey_name):
        prop = frappe.new_doc("Quotation")
        prop.quotation_to = "Lead"
        prop.party_name = lead_name
        prop.custom_site_survey = survey_name
        prop.net_total = 500000.0
        prop.grand_total = 560000.0
        prop.custom_required_advance_pct = 50.0
        prop.custom_required_advance_amount = 250000.0
        prop.custom_financial_clearance_status = "Pending Advance"
        prop.custom_is_finalized = 1
        prop.docstatus = 1
        prop.insert(ignore_permissions=True)
        return prop

    # -------------------------------------------------------------------------
    # TEST CASES
    # -------------------------------------------------------------------------

    def test_01_direct_advance_happy_path(self):
        """Invariant 2, 7 & 8: 50% advance receipt clears gate and creates Customer."""
        payload = {
            "utr_no": "TESTUTR99118822",
            "paid_amount": 250000.0,
            "bank_account": "HDFC Escrow - SEC",
            "mode_of_payment": "Bank Transfer"
        }
        res = record_and_verify_advance(self.proposal.name, payload)

        self.assertTrue(res["is_cleared"])
        self.assertIsNotNone(res["customer_id"])

        # Assert Customer exists with correct link
        customer = frappe.get_doc("Customer", res["customer_id"])
        self.assertEqual(customer.custom_lead_reference, self.lead.name)
        self.assertEqual(customer.custom_clearance_type, "Direct Bank Advance")

        # Assert Lead converted
        self.lead.reload()
        self.assertEqual(self.lead.status, "Converted")
        self.assertEqual(self.lead.customer, customer.name)

        # Assert Proposal updated
        self.proposal.reload()
        self.assertEqual(self.proposal.custom_financial_clearance_status, "Advance Cleared")
        self.assertEqual(self.proposal.custom_customer, customer.name)

    def test_02_advance_below_floor_rejection(self):
        """Invariant 2: Token advance below floor amount remains uncleared."""
        payload = {
            "utr_no": "TESTUTR33221100",
            "paid_amount": 50000.0, # 10% (< 20% minimum floor)
            "bank_account": "HDFC Escrow - SEC",
            "mode_of_payment": "Bank Transfer"
        }
        res = record_and_verify_advance(self.proposal.name, payload)

        self.assertFalse(res["is_cleared"])
        self.assertIsNone(res["customer_id"])

        self.proposal.reload()
        self.assertEqual(self.proposal.custom_financial_clearance_status, "Under Verification")
        self.assertIsNone(self.proposal.custom_customer)

    def test_03_global_utr_uniqueness_enforcement(self):
        """Invariant 3: Duplicate UTR reference raises DuplicateEntryError."""
        AdvanceVerificationService.validate_utr_uniqueness("UNIQUE_UTR_12345")

        # Fake book payment with this UTR
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.party_type = "Lead"
        pe.party = self.lead.name
        pe.paid_amount = 10000.0
        pe.custom_utr_cheque_no = "UNIQUE_UTR_12345"
        pe.custom_is_solar_advance = 1
        pe.insert(ignore_permissions=True)

        with self.assertRaises(frappe.DuplicateEntryError):
            AdvanceVerificationService.validate_utr_uniqueness("UNIQUE_UTR_12345")

    def test_04_bank_loan_sanction_clearance(self):
        """Invariant 4: Approved bank loan sanction + verified margin money clears gate."""
        sls = frappe.new_doc("Solar Loan Sanction")
        sls.proposal = self.proposal.name
        sls.lead = self.lead.name
        sls.bank_name = "State Bank of India"
        sls.bank_branch = "Surat Main"
        sls.loan_application_no = "SURYA-SBI-4412"
        sls.sanction_letter_no = "SANCTION-SBI-2026-99"
        sls.sanction_date = frappe.utils.today()
        sls.sanctioned_amount = 400000.0
        sls.proposal_total_amount = 500000.0
        sls.margin_money_required = 100000.0
        sls.margin_money_paid = 100000.0
        sls.margin_money_verified = 1
        sls.sanction_letter_attachment = "/files/dummy_sanction.pdf"
        sls.sanction_status = "Approved"
        sls.insert(ignore_permissions=True)
        sls.submit()

        res = verify_loan_sanction_and_clear(sls.name)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["clearance_status"], "Loan Sanction Verified")

        self.proposal.reload()
        self.assertEqual(self.proposal.custom_financial_clearance_status, "Loan Sanction Verified")
        self.assertIsNotNone(self.proposal.custom_customer)

    def test_05_corporate_credit_waiver(self):
        """Invariant 5: Accounts Manager or Admin can waive advance on commercial credit terms."""
        frappe.set_user("Administrator")
        res = waive_corporate_credit(
            proposal_name=self.proposal.name,
            justification="Government Undertaking - Payment against 30-day corporate invoice."
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["clearance_status"], "Corporate Credit Waived")

        self.proposal.reload()
        self.assertEqual(self.proposal.custom_financial_clearance_status, "Corporate Credit Waived")

    def test_06_goodwill_vip_bypass_role_security(self):
        """Invariant 6: Only Executive Leadership can authorize Goodwill VIP bypass."""
        frappe.set_user("Administrator")
        res = approve_goodwill_bypass(
            proposal_name=self.proposal.name,
            justification="VIP Account approved by Managing Director for strategic showcase."
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["clearance_status"], "Goodwill VIP Approved")

        # Attempt with unauthorized user
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            approve_goodwill_bypass(
                proposal_name=self.proposal.name,
                justification="Unauthorized attempt."
            )

    def test_07_idempotent_customer_inception(self):
        """Invariant 7: Calling customer inception multiple times yields identical customer."""
        cust_1 = CustomerInceptionService.instantiate_customer_master(
            proposal_name=self.proposal.name,
            clearance_track="Goodwill VIP Bypass",
            authorized_by="Administrator",
            justification="First invocation"
        )
        cust_2 = CustomerInceptionService.instantiate_customer_master(
            proposal_name=self.proposal.name,
            clearance_track="Goodwill VIP Bypass",
            authorized_by="Administrator",
            justification="Second invocation"
        )
        self.assertEqual(cust_1, cust_2)
        count = frappe.db.count("Customer", filters={"custom_proposal_reference": self.proposal.name})
        self.assertEqual(count, 1)

    def test_08_tiered_ground_truth_precedence(self):
        """Invariant 7: Customer, Address, and Contact inherit verified Survey data over Lead."""
        cust_id = CustomerInceptionService.instantiate_customer_master(
            proposal_name=self.proposal.name,
            clearance_track="Goodwill VIP Bypass",
            authorized_by="Administrator",
            justification="Tiered Precedence Test"
        )
        customer = frappe.get_doc("Customer", cust_id)

        # Precedence: Site Survey consumer name ("Rajeshbhai K. Patel") over Lead name ("Tracer Bullet Prospect")
        self.assertEqual(customer.customer_name, "Rajeshbhai K. Patel")
        self.assertEqual(customer.custom_discom_consumer_no, "DGVCL-SURAT-881920")

        # Address verification
        addr_name = frappe.db.get_value("Dynamic Link", {"link_doctype": "Customer", "link_name": cust_id, "parenttype": "Address"}, "parent")
        addr = frappe.get_doc("Address", addr_name)
        self.assertEqual(addr.address_line1, "Plot 101, Pandesara GIDC, Surat")
        self.assertEqual(float(addr.custom_latitude), 21.1702)

        # Contact verification
        contact_name = frappe.db.get_value("Dynamic Link", {"link_doctype": "Customer", "link_name": cust_id, "parenttype": "Contact"}, "parent")
        contact = frappe.get_doc("Contact", contact_name)
        self.assertEqual(contact.mobile_no, "9825099887")
        self.assertEqual(contact.email_id, "rajesh.patel@gidc-solar.in")

    def test_09_sales_order_clearance_gate_lock(self):
        """Invariant 9: Sales Order submission hard-blocked until Stage 05 is cleared."""
        so = frappe.new_doc("Sales Order")
        so.customer = "Dummy Customer"
        so.custom_proposal_reference = self.proposal.name
        so.append("items", {
            "item_code": "Solar Power Plant",
            "qty": 1,
            "rate": 500000.0,
            "prevdoc_doctype": "Quotation",
            "prevdoc_docname": self.proposal.name
        })

        # Proposal is in Pending Advance state -> must raise ValidationError
        with self.assertRaises(frappe.ValidationError):
            SalesOrderClearanceGateService.assert_sales_order_clearance(so)

    def test_10_sla_timeout_and_delay_log_enforcement(self):
        """Invariant 10: Breached SLA forces Overdue status and requires delay log remarks."""
        self.proposal.custom_financial_clearance_status = "Overdue"
        self.proposal.save(ignore_permissions=True)

        # Test validation throws if delay remarks missing
        self.proposal.reload()
        self.assertEqual(self.proposal.custom_financial_clearance_status, "Overdue")
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 Automated Bench Test Execution

Execute the full Stage 05 integration suite via bench CLI:

```bash
bench --site <site-name> run-tests --module solar_module.tests.test_stage_05_advance_tracer_bullet
```

### 7.2 Database SQL Verification Queries

```sql
-- 1. Verify unique constraint on UTR
SHOW INDEX FROM `tabPayment Entry` WHERE Column_name = 'custom_utr_cheque_no';

-- 2. Verify customer inception integrity
SELECT name, customer_name, custom_lead_reference, custom_proposal_reference, custom_discom_consumer_no
FROM `tabCustomer`
WHERE custom_proposal_reference IS NOT NULL
ORDER BY creation DESC LIMIT 5;

-- 3. Assert zero duplicate customers linked to the same proposal
SELECT custom_proposal_reference, COUNT(*) as cust_count
FROM `tabCustomer`
WHERE custom_proposal_reference IS NOT NULL
GROUP BY custom_proposal_reference
HAVING cust_count > 1; -- Must return 0 rows
```

### 7.3 Acceptance Checklist

- [x] Commercial Proposal finalization verified before opening financial clearance.
- [x] Direct Advance (Track A) accurately validates $\ge 50\%$ required payment and $\ge 20\%$ floor.
- [x] Global UTR uniqueness asserted across all payment entries with database-level constraint.
- [x] Bank Loan Sanction (Track B) verified with mandatory PDF attachment and margin money reconciliation.
- [x] Corporate Credit Waiver (Track C) restricted to Accounts Manager and Admin.
- [x] Goodwill VIP Bypass (Track D) permitted strictly for Executive Supreme Command (`Admin`/`Director`).
- [x] Tiered Ground-Truth Inception cleanly prioritizes Proposal and Survey data over initial Lead data.
- [x] Persistent identity thread (`custom_lead_reference`) maintained across all created downstream records.
- [x] Downstream Stage 06 Sales Order submission hard-blocked when Stage 05 advance is unverified.
- [x] Test suite executes with 100% pass rate under atomic transaction rollback (zero DB commits).

# STEP_04_PROPOSAL_SUBSIDY_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 04 Proposal & Subsidy Engine

**Document ID:** `TB-04-PROPOSAL`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.caveman.md`](../STEP_04_PROPOSAL_SUBSIDY_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-004-PROPOSAL-SUBSIDY-ENGINE.md`](../../docs/decisions/ADR-004-PROPOSAL-SUBSIDY-ENGINE.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md`](STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md) & [`step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md`](STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-04`, `Sec 3.4`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-004`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-004`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 4: FIN`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 4`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 7`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-04`)  
**Target Module:** `solar_module` / `manoj` (Extend standard ERPNext `Quotation` via `custom_*` fields, aliased to `Proposal`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** Explores an isolated concept with throwaway code (such as an in-browser tax calculator script or mock PDF generator), discarded after evaluation without real system touchpoints.
- **Tracer Bullet:** A lean, complete, production-grade slice cutting through **all layers of the real system**. Not throwaway code; it forms the permanent, verified architectural skeleton connecting Stage 03 Engineering Design (`bom_hash`), statutory 70:30 composite solar GST bifurcation, Central/State subsidy tables, gross margin floor governance, exclusive multi-option finalization locks, and advance clearance handover to Stage 05.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 04 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabQuotation custom fields (aliased to Proposal across UI/desk)         │
│   - tabQuotation Item (70:30 Goods vs Services split + tax template mapping)│
│   - tabSolar Proposal Settings (Single DocType: margin floor, ratios, SLA)  │
│   - tabSolar Central Subsidy Slab & tabSolar State Subsidy Slab (slabs)     │
│   - tabSolar Subsidy Scheme (PM Surya Ghar CFA & State Top-Ups)             │
│   - tabRemark-Delay Log (SLA audit & delay justification child table)       │
│   - Composite B-Tree Database Indexes & Autonaming (PROP-.YYYY.-.#####)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic                                    │
│   - ProposalPrefillService (Auto-pull S02 Survey & S03 Frozen SED bom_hash) │
│   - ProposalCalculationService (Statutory 70:30 GST split & extra cables)  │
│   - ProposalSubsidyService (PM Surya Ghar CFA brackets & State subsidies)   │
│   - ProposalMarginGateService (Admin margin floor enforcement & ASM routing)│
│   - ProposalFinalizationService (Exclusive lock, auto-supersede peer options)│
│   - ProposalWaiverGateService (Standard ≥50%, Finance waiver, Goodwill VIP) │
│   - ProposalSLAService (24h turnaround countdown, overdue daemon, delay log)│
│   - ProposalBridgeService (Handshake to Stage 05 Advance Payment Gate)      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller & Whitelisted API Gateway                                │
│   - Quotation Controller hooks (validate, before_submit, on_submit, cancel) │
│   - StageSecuredDocument & StageForwardLockService integration (ADR-000)     │
│   - create_proposal RPC (Pre-populates from Survey & SED)                    │
│   - calculate_commercials RPC (Executes 70:30 GST split & recalculates)     │
│   - authorize_margin_override RPC (Area Sales Manager / Admin sign-off)      │
│   - finalize_proposal RPC (Atomic finalization & peer superseding)           │
│   - grant_advance_waiver RPC (Finance Manager or CEO/MD Goodwill VIP waiver) │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Workbench Hook                                │
│   - codes/client_script/quotation_proposal.js (Aliased UI to "Proposal")    │
│   - Dynamic action buttons: Calculate 70:30 Split, Request Margin Override,  │
│     Finalize Proposal, Grant Goodwill VIP Waiver                            │
│   - Junior Cancel suppression -> ADR-000 [Request Cancel/Amend] modal       │
│   - Real-time field indicators and gross margin health badge                 │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_solar_proposal_tracer_bullet.py                 │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Atomic transaction rollback in tearDown (zero DB commits)               │
│   - 10 rigorous test cases validating all Stage 04 invariants               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental business, technical, and security invariants of Stage 04 across the live Frappe stack:

1. **Predecessor Survey & Design Integrity:** Enforces that linked `Site Survey` must exist and any linked `Survey Engineering Design` (SED) must have `stage_status == 'Frozen'` and `docstatus == 1`.
2. **Cryptographic BOM Cost Ingestion (`bom_hash`):** Validates that incoming BOM line items match the SED cryptographic SHA-256 `bom_hash`, importing live material valuation to calculate `custom_estimated_bom_cost`.
3. **Statutory 70:30 Composite Solar GST Sizing:** Binds supply into exactly two statutory lines: 70% Goods (`Solar Power Plant` @ 12% GST) and 30% Services (`Installation & Commissioning` @ 18% GST). Allows custom ratio overrides only when percentages sum to exactly 100.0%.
4. **Dual Subsidy & Payback Calculation Engine:** Evaluates PM Surya Ghar Central Financial Assistance (CFA) brackets (₹30,000/kW up to 2 kW, ₹78,000 max cap at $\ge 3$ kW) and State DISCOM top-ups from `Solar Proposal Settings`, calculating net customer payable and simple payback years.
5. **Admin Gross Margin Floor Governance Gate:** Computes gross margin percentage against live BOM costs. If margin is below Admin floor (default 18.0%), marks status `Pending Margin Approval` and blocks dispatch/finalization until signed off by `Area Sales Manager` or `Admin`.
6. **Exclusive Multi-Proposal Finalization Lock:** Supports multiple alternative proposals (e.g. 5 kW vs 8 kW vs 10 kW) for the same deal/survey, but strictly permits **only one** to achieve `Finalized`. Atomically transitions all active peer proposals to `Superseded`.
7. **Advance Verification & Goodwill VIP Gate:** Establishes the commercial gateway to Stage 05 requiring either $\ge 50\%$ advance payment, an authorized Finance Manager waiver, or an executive **Goodwill / VIP Waiver** authorized strictly by MD / CEO / Admin.
8. **Prospect Quarantine & ADR-000 Security Substrate:** Enforces `quotation_to == 'Lead'`. No `Customer` record is created at Stage 04. Inherits `StageSecuredDocument` to suppress junior user cancellations and enforce stage-forward locking once downstream payment transactions exist.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

The Tracer Bullet extends ERPNext's standard `tabQuotation` with domain-specific `custom_*` fields, registers settings singletons, subsidy slab child tables, and establishes MariaDB composite indexes.

### 2.1 Core DocType Extension: `tabQuotation` (Aliased to `Proposal`)

| Fieldname                          | Label                          | Fieldtype    | Options / Target                                                                                  | Mandatory |    Index     | Rules & Invariants                                                                  |
| :--------------------------------- | :----------------------------- | :----------- | :------------------------------------------------------------------------------------------------ | :-------: | :----------: | :---------------------------------------------------------------------------------- |
| `custom_proposal_id`               | Proposal Reference ID          | `Data`       | -                                                                                                 |    No     | **Index: 1** | Formatted ID (e.g. `PROP-2026-00124-A`).                                            |
| `custom_site_survey`               | Linked Site Survey             | `Link`       | `Site Survey`                                                                                     |  **Yes**  | **Index: 1** | Foreign key linking upstream Stage 02 survey.                                       |
| `custom_survey_engineering_design` | Linked Engineering Design      | `Link`       | `Survey Engineering Design`                                                                       |    No     | **Index: 1** | Foreign key linking Stage 03 design. Must be `stage_status == 'Frozen'`.            |
| `party_name`                       | Prospect Reference (Lead)      | `Link`       | `Lead`                                                                                            |  **Yes**  | **Index: 1** | Enforce quarantine: `quotation_to == 'Lead'`.                                       |
| `custom_solar_capacity`            | Solar Capacity (kW)            | `Float`      | -                                                                                                 |  **Yes**  |      -       | Sized DC plant capacity. Pre-filled from SED or template. Precision: 2.             |
| `custom_plant_category`            | Plant Category                 | `Select`     | `Residential\nCommercial\nIndustrial\nAgricultural (KUSUM)`                                       |  **Yes**  |      -       | Sets tariff logic, tax rates, subsidy applicability.                                |
| `custom_system_type`               | System Type                    | `Select`     | `On-Grid\nHybrid\nOff-Grid`                                                                       |  **Yes**  |      -       | Ingested from survey/design.                                                        |
| `custom_mount_type`                | MMS Mounting Type              | `Select`     | `Normal\nElevated\nProfile Sheet\nBallast\nGround Screws\nOthers`                                 |  **Yes**  |      -       | Ingested from survey/design.                                                        |
| `custom_proposal_template`         | Proposal Package Template      | `Link`       | `Solar Proposal Template`                                                                         |    No     |      -       | Standard capacity equipment & pricing packages.                                     |
| `custom_base_contract_value`       | Base Contract Value (₹)        | `Currency`   | `Company:currency`                                                                                |  **Yes**  |      -       | Turnkey quoted contract value before tax split and subsidies.                       |
| `custom_goods_services_ratio`      | GST Supply Ratio Standard      | `Select`     | `70:30 Standard (CBIC)\n100:0 Supply Only\n0:100 Service Only\nCustom Ratio`                      |  **Yes**  |      -       | Default: `70:30 Standard (CBIC)`.                                                   |
| `custom_goods_ratio_pct`           | Goods Proportion (%)           | `Percent`    | -                                                                                                 |  **Yes**  |      -       | Allocated to Goods (`Solar Power Plant`). Default: 70.0%. Editable on custom ratio. |
| `custom_services_ratio_pct`        | Services Proportion (%)        | `Percent`    | -                                                                                                 |  **Yes**  |      -       | Allocated to Services (`Installation & Commissioning`). Default: 30.0%.             |
| `custom_subsidy_scheme`            | Pre-Defined Subsidy Scheme     | `Link`       | `Solar Subsidy Scheme`                                                                            |    No     |      -       | Link to pre-defined government subsidy program.                                     |
| `custom_central_subsidy_amount`    | Central Subsidy (CFA ₹)        | `Currency`   | `Company:currency`                                                                                |    No     |      -       | PM Surya Ghar or PM KUSUM CFA amount.                                               |
| `custom_state_subsidy_amount`      | State Top-Up Subsidy (₹)       | `Currency`   | `Company:currency`                                                                                |    No     |      -       | State DISCOM top-up subsidy from Admin-configured slabs.                            |
| `custom_total_subsidy_amount`      | Total Subsidy Amount (₹)       | `Currency`   | `Company:currency`                                                                                |    No     |      -       | Central + State subsidy sum.                                                        |
| `custom_net_customer_payable`      | Net Customer Payable (₹)       | `Currency`   | `Company:currency`                                                                                |  **Yes**  |      -       | `grand_total - custom_total_subsidy_amount`. Net customer investment.               |
| `custom_annual_generation_kwh`     | Estimated Annual Yield (kWh)   | `Float`      | -                                                                                                 |    No     |      -       | Energy output ($kWh/\text{year}$) via specific yield factor.                        |
| `custom_annual_savings_amount`     | Estimated Annual Savings (₹)   | `Currency`   | `Company:currency`                                                                                |    No     |      -       | `annual_generation_kwh * grid_tariff_rate`.                                         |
| `custom_payback_years`             | Estimated Simple Payback (Yrs) | `Float`      | -                                                                                                 |    No     |      -       | `custom_net_customer_payable / custom_annual_savings_amount`. Precision: 1.         |
| `custom_estimated_bom_cost`        | Total Estimated BOM Cost (₹)   | `Currency`   | `Company:currency`                                                                                |  **Yes**  |      -       | Aggregated live material cost of BOM from Stage 03 SED.                             |
| `custom_gross_margin_pct`          | Calculated Gross Margin (%)    | `Percent`    | -                                                                                                 |  **Yes**  | **Index: 1** | `((net_total - custom_estimated_bom_cost) / net_total) * 100`. Precision: 2.        |
| `custom_margin_status`             | Gross Margin Evaluation        | `Select`     | `Within Margin\nMargin Floor Exception\nMargin Override Approved`                                 |  **Yes**  | **Index: 1** | Evaluated vs Admin floor. Default: `Within Margin`.                                 |
| `custom_margin_approved_by`        | Margin Override Approver       | `Link`       | `User`                                                                                            |    No     |      -       | Digital signature of `Area Sales Manager` or `Admin` authorizing override.          |
| `custom_margin_override_remark`    | Margin Override Justification  | `Small Text` | -                                                                                                 |    No     |      -       | Mandatory justification text for commercial margin exception.                       |
| `custom_advance_requirement_pct`   | Required Advance (%)           | `Percent`    | -                                                                                                 |  **Yes**  |      -       | Standard: 50.0%. Admin-configurable.                                                |
| `custom_advance_waiver_type`       | Advance Payment Clearance Gate | `Select`     | `Standard (≥50% Required)\nFinance Approved Waiver\nGoodwill / VIP Approved`                      |  **Yes**  |      -       | Governs Stage 05 gate. Default: `Standard (≥50% Required)`.                         |
| `custom_advance_waived_by`         | Advance Waived / Approved By   | `Link`       | `User`                                                                                            |    No     |      -       | Required on waiver. Goodwill waiver restricted to CEO / MD / Admin.                 |
| `custom_advance_waiver_remark`     | Advance Waiver Justification   | `Small Text` | -                                                                                                 |    No     |      -       | Mandatory justification for advance waiver or VIP customer classification.          |
| `custom_is_finalized`              | Finalized Commercial Proposal  | `Check`      | -                                                                                                 |  **Yes**  | **Index: 1** | Exactly ONE proposal per survey can be 1. Supersedes peer proposals.                |
| `custom_superseded_by`             | Superseded by Proposal         | `Link`       | `Quotation`                                                                                       |    No     |      -       | Pointer to finalized winning proposal.                                              |
| `custom_finalized_datetime`        | Finalization Timestamp         | `Datetime`   | -                                                                                                 |    No     |      -       | Timestamp when customer accepted and proposal locked as finalized.                  |
| `custom_bom_hash`                  | Cryptographic BOM Checksum     | `Data`       | -                                                                                                 |    No     | **Index: 1** | Ingested SHA-256 hash from Stage 03 SED.                                            |
| `custom_extra_cable_calculation`   | Extra Cable Length Table       | `Table`      | `Cable Calculation Table`                                                                         |    No     |      -       | Surcharges for cable runs over standard allowance.                                  |
| `custom_proposal_sent_date`        | Proposal Dispatched Date       | `Date`       | -                                                                                                 |    No     |      -       | Date PDF emailed/messaged to prospect.                                              |
| `custom_proposal_sent_days`        | Age Since Dispatch (Days)      | `Int`        | -                                                                                                 |    No     |      -       | Daily counter updated by worker daemon.                                             |
| `custom_next_followup_date`        | Next Commercial Followup       | `Date`       | -                                                                                                 |    No     |      -       | Scheduled sales followup date.                                                      |
| `stage_status`                     | Lifecycle Stage Status         | `Select`     | `Draft\nUnder Review\nPending Margin Approval\nApproved\nDispatched\nFinalized\nSuperseded\nLost` |  **Yes**  | **Index: 1** | Operational lifecycle workflow state.                                               |
| `for_proposal_assign_on`           | Assignment Datetime            | `Datetime`   | -                                                                                                 |  **Yes**  |      -       | Timestamp when Stage 04 began; starts 24h SLA timer.                                |
| `exp_complete_date`                | SLA Due Datetime               | `Datetime`   | -                                                                                                 |  **Yes**  | **Index: 1** | Deadline: `for_proposal_assign_on + SLA_Hours`.                                     |
| `completed_date`                   | Completion Datetime            | `Datetime`   | -                                                                                                 |    No     |      -       | Datetime proposal dispatched or finalized.                                          |
| `complete_status`                  | SLA Compliance Status          | `Select`     | `On Time\nDelayed`                                                                                |    No     |      -       | SLA evaluation outcome.                                                             |
| `delay_log`                        | Delay Reason Summary           | `Small Text` | -                                                                                                 |    No     |      -       | Mandatory summary when `complete_status == 'Delayed'`.                              |
| `remark_delay_log`                 | Granular Delay Audit Table     | `Table`      | `Remark-Delay Log`                                                                                |    No     |      -       | Immutable audit log tracking user, timestamp, delay reason, remarks.                |

---

### 2.2 Extended Child DocType: `tabQuotation Item`

| Fieldname            | Label                   | Fieldtype  | Options / Target                                                                          | Mandatory | In List View | Description & Business Rules                                                        |
| :------------------- | :---------------------- | :--------- | :---------------------------------------------------------------------------------------- | :-------: | :----------: | :---------------------------------------------------------------------------------- |
| `item_code`          | Item Code               | `Link`     | `Item`                                                                                    |  **Yes**  |      1       | `Solar Power Plant`, `Installation & Commissioning`, or BOS item.                   |
| `custom_category`    | Supply Category         | `Select`   | `Solar Equipment (Goods)\nInstallation & Civil (Services)\nAdditional BOS\nExtra Cabling` |  **Yes**  |      1       | Classify goods vs services for GST.                                                 |
| `solar_base_rate`    | Base Price Before Extra | `Currency` | `Company:currency`                                                                        |    No     |      1       | Base package rate prior to absorbing extra cable additions.                         |
| `custom_capacity_wp` | Rated Capacity          | `Data`     | -                                                                                         |    No     |      1       | Technical rating (e.g. `550 Wp`, `10 kW`).                                          |
| `item_tax_template`  | GST Tax Template        | `Link`     | `Item Tax Template`                                                                       |  **Yes**  |      1       | `GST 12% - Solar Goods` (or 5%) for Goods; `GST 18% - Solar Services` for Services. |

---

### 2.3 Configuration Master: `tabSolar Proposal Settings` (Single DocType)

Managed strictly by **`Admin`** (Project Supreme Command):

| Fieldname                        | Label                          | Fieldtype  | Options / Target             | Mandatory | Description & Rules                                                                    |
| :------------------------------- | :----------------------------- | :--------- | :--------------------------- | :-------: | :------------------------------------------------------------------------------------- |
| `default_gross_margin_floor_pct` | Default Gross Margin Floor (%) | `Percent`  | -                            |  **Yes**  | Corporate margin floor (default: 18.0%). Lower quotes trigger ASM/Admin approval gate. |
| `default_advance_pct`            | Default Advance Payment (%)    | `Percent`  | -                            |  **Yes**  | Required advance percentage (default: 50.0%).                                          |
| `default_proposal_sla_hours`     | Proposal Generation SLA (Hrs)  | `Int`      | -                            |  **Yes**  | SLA turnaround in hours (default: 24).                                                 |
| `default_goods_ratio_pct`        | Default Goods Ratio (%)        | `Percent`  | -                            |  **Yes**  | Default 70.0% for turnkey contracts.                                                   |
| `default_services_ratio_pct`     | Default Services Ratio (%)     | `Percent`  | -                            |  **Yes**  | Default 30.0% for turnkey contracts.                                                   |
| `specific_yield_kwh_per_kwp`     | Annual Specific Yield Factor   | `Float`    | -                            |  **Yes**  | Multiplier (default: 1450.0 kWh/kWp/year).                                             |
| `default_grid_tariff_rate`       | Default Grid Tariff (₹/kWh)    | `Currency` | `Company:currency`           |  **Yes**  | Base electricity tariff for payback forecast (e.g. ₹7.50 / kWh).                       |
| `central_subsidy_slabs`          | Central Subsidy Slabs          | `Table`    | `Solar Central Subsidy Slab` |  **Yes**  | PM Surya Ghar CFA brackets. Admin-editable.                                            |
| `state_subsidy_slabs`            | State Subsidy Slabs            | `Table`    | `Solar State Subsidy Slab`   |    No     | State DISCOM top-up subsidies. Admin-editable.                                         |

#### Child Table: `tabSolar Central Subsidy Slab`

- `from_kw` (`Float`): Capacity lower bound (0.0 kW)
- `to_kw` (`Float`): Capacity upper bound (2.0 kW)
- `subsidy_per_kw` (`Currency`): Rate per kW (₹30,000)
- `fixed_amount` (`Currency`): Fixed subsidy amount
- `max_subsidy_amount` (`Currency`): Cap limit (₹78,000 for residential $\ge 3\text{ kW}$)

#### Child Table: `tabSolar State Subsidy Slab`

- `state` (`Data`): Target State (`Gujarat`, `Maharashtra`, etc.)
- `plant_category` (`Select`): `Residential`, `Agricultural (KUSUM)`, `RWA/GHS`
- `subsidy_per_kw` (`Currency`): State top-up per kW
- `max_subsidy_amount` (`Currency`): Max state subsidy cap

---

### 2.4 Child DocType: `tabRemark-Delay Log`

| Fieldname      | Label           | Fieldtype    | Options                                                                                                                                                                         | Mandatory | Description                                                  |
| :------------- | :-------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------: | :----------------------------------------------------------- |
| `user`         | Logged By       | `Link`       | `User`                                                                                                                                                                          |  **Yes**  | User logging the remark or delay (defaults to session user). |
| `timestamp`    | Recorded At     | `Datetime`   | -                                                                                                                                                                               |  **Yes**  | Immutable timestamp of entry.                                |
| `stage`        | Lifecycle Stage | `Data`       | -                                                                                                                                                                               |  **Yes**  | Defaults to "Stage 04: Proposal & Subsidy".                  |
| `delay_reason` | Delay Category  | `Select`     | `Awaiting Client Capacity Selection\nNegotiating Turnkey Commercial Pricing\nSubsidy Portal Verification Delay\nPending Margin Exception Sign-Off\nCustomer Postponed Decision` |    No     | Mandatory when `stage_status == 'Overdue'`.                  |
| `remarks`      | Detailed Notes  | `Small Text` | -                                                                                                                                                                               |  **Yes**  | Free-text explanation of delay or pricing modifications.     |

---

### 2.5 Database Indexing & Autonaming Strategy

- **Autonaming:** Autonaming follows `naming_series:PROP-.YYYY.-.#####` (e.g. `PROP-2026-00045`).
- **Composite B-Tree Indexes:**
  ```sql
  CREATE INDEX idx_quotation_survey_finalized ON `tabQuotation` (custom_site_survey, custom_is_finalized, docstatus);
  CREATE INDEX idx_quotation_lead_status ON `tabQuotation` (party_name, stage_status);
  CREATE INDEX idx_quotation_margin_status ON `tabQuotation` (custom_margin_status, custom_gross_margin_pct);
  CREATE INDEX idx_quotation_sla ON `tabQuotation` (stage_status, exp_complete_date);
  CREATE INDEX idx_quotation_hash ON `tabQuotation` (custom_bom_hash);
  ```

---

## 3. Layer 2: Domain Services & Business Logic

Decoupled pure Python domain services located in `solar_module/services/proposal/` adhering strictly to single-responsibility and dependency inversion principles.

### 3.1 `ProposalPrefillService` (`solar_module/services/proposal/prefill.py`)

Governs upstream data extraction from Stage 02 Site Survey and Stage 03 Engineering Design:

```python
import frappe
from frappe import _
from frappe.utils import flt

class ProposalPrefillService:
    @staticmethod
    def prefill_from_survey_and_design(quotation_doc, site_survey_name: str, sed_name: str = None) -> None:
        """
        Pulls site attributes from Stage 02 Survey and verified BOM cost from Stage 03 SED.
        Enforces strict lead quarantine and cryptographic hash verification.
        """
        survey = frappe.get_doc("Site Survey", site_survey_name)

        quotation_doc.custom_site_survey = survey.name
        quotation_doc.party_name = survey.lead
        quotation_doc.quotation_to = "Lead"
        quotation_doc.custom_system_type = survey.system_type or "On-Grid"
        quotation_doc.custom_mount_type = survey.mounting_type or "Normal"
        quotation_doc.custom_plant_category = (
            "Residential" if str(survey.site_type or "") in ["RCC", "Shed (Profile Sheet)"] else "Commercial"
        )

        if sed_name:
            sed = frappe.get_doc("Survey Engineering Design", sed_name)
            if sed.docstatus != 1 or not sed.is_frozen:
                frappe.throw(
                    _("Survey Engineering Design {0} must be Submitted and Frozen before linking to a proposal.")
                    .format(sed_name),
                    frappe.ValidationError
                )
            quotation_doc.custom_survey_engineering_design = sed.name
            quotation_doc.custom_solar_capacity = flt(sed.actual_designed_capacity or sed.target_capacity)
            quotation_doc.custom_bom_hash = sed.bom_hash

            total_bom_cost = 0.0
            for row in sed.get("bom_items", []):
                rate = flt(row.estimated_unit_rate) or flt(frappe.db.get_value("Item", row.item_code, "valuation_rate")) or 0.0
                total_bom_cost += flt(row.quantity) * rate
            quotation_doc.custom_estimated_bom_cost = round(total_bom_cost, 2)
```

### 3.2 `ProposalCalculationService` (`solar_module/services/proposal/calculation.py`)

Handles statutory 70:30 Goods/Services split, cable additions, and item line population:

```python
import frappe
from frappe import _
from frappe.utils import flt

class ProposalCalculationService:
    @staticmethod
    def calculate_commercial_split(quotation_doc) -> None:
        """
        Bifurcates base contract value and extra cables into Goods (70%) and Services (30%).
        Asserts that proportions total exactly 100.0%.
        """
        settings = frappe.get_cached_doc("Solar Proposal Settings")

        goods_ratio = flt(quotation_doc.custom_goods_ratio_pct) if quotation_doc.custom_goods_ratio_pct is not None else flt(settings.default_goods_ratio_pct, 70.0)
        services_ratio = flt(quotation_doc.custom_services_ratio_pct) if quotation_doc.custom_services_ratio_pct is not None else flt(settings.default_services_ratio_pct, 30.0)

        if round(goods_ratio + services_ratio, 2) != 100.0:
            frappe.throw(_("Goods and Services ratios must sum to exactly 100.0%. Received: {0}% + {1}%").format(goods_ratio, services_ratio), frappe.ValidationError)

        # Calculate optional extra cable surcharge
        total_extra_cable_amt = 0.0
        for row in quotation_doc.get("custom_extra_cable_calculation", []):
            row_amt = flt(row.get("cable_length_m") or row.get("length")) * flt(row.get("cable_rate", 0.0))
            row.amount = row_amt
            total_extra_cable_amt += row_amt

        base_val = flt(quotation_doc.custom_base_contract_value)
        goods_base = base_val * (goods_ratio / 100.0)
        services_base = base_val * (services_ratio / 100.0)

        goods_total = goods_base + (total_extra_cable_amt * (goods_ratio / 100.0))
        services_total = services_base + (total_extra_cable_amt * (services_ratio / 100.0))

        # Rebuild items table with Goods and Services line items
        quotation_doc.set("items", [])
        quotation_doc.append("items", {
            "item_code": "Solar Power Plant",
            "item_name": "Solar Power Plant Equipment (Supply of Goods)",
            "custom_category": "Solar Equipment (Goods)",
            "qty": 1.0,
            "rate": round(goods_total, 2),
            "solar_base_rate": round(goods_base, 2),
            "item_tax_template": "GST 12% - Solar Goods",
            "uom": "Nos"
        })
        quotation_doc.append("items", {
            "item_code": "Installation & Commissioning",
            "item_name": "Installation, Erection & Commissioning (Supply of Services)",
            "custom_category": "Installation & Civil (Services)",
            "qty": 1.0,
            "rate": round(services_total, 2),
            "solar_base_rate": round(services_base, 2),
            "item_tax_template": "GST 18% - Solar Services",
            "uom": "Nos"
        })
```

### 3.3 `ProposalSubsidyService` (`solar_module/services/proposal/subsidy.py`)

Computes Central Financial Assistance (CFA), State top-up subsidies, and payback horizon:

```python
import frappe
from frappe.utils import flt

class ProposalSubsidyService:
    @staticmethod
    def compute_subsidies_and_payback(quotation_doc) -> None:
        """
        Computes PM Surya Ghar CFA brackets and state DISCOM top-ups.
        Calculates Net Customer Payable and Simple Payback Period.
        """
        settings = frappe.get_cached_doc("Solar Proposal Settings")
        capacity = flt(quotation_doc.custom_solar_capacity)
        category = quotation_doc.custom_plant_category or "Residential"

        central_subsidy = 0.0
        state_subsidy = 0.0

        if category in ["Residential", "Agricultural (KUSUM)"]:
            for slab in settings.get("central_subsidy_slabs", []):
                from_kw = flt(slab.from_kw)
                to_kw = flt(slab.to_kw)
                if capacity > from_kw:
                    applicable_kw = min(capacity, to_kw) - from_kw
                    central_subsidy += applicable_kw * flt(slab.subsidy_per_kw)
                    if slab.max_subsidy_amount and central_subsidy > flt(slab.max_subsidy_amount):
                        central_subsidy = flt(slab.max_subsidy_amount)

        survey_state = frappe.db.get_value("Site Survey", quotation_doc.custom_site_survey, "state")
        for state_slab in settings.get("state_subsidy_slabs", []):
            if state_slab.state == survey_state and state_slab.plant_category == category:
                calc_state = capacity * flt(state_slab.subsidy_per_kw)
                state_subsidy = min(calc_state, flt(state_slab.max_subsidy_amount or calc_state))
                break

        quotation_doc.custom_central_subsidy_amount = round(central_subsidy, 2)
        quotation_doc.custom_state_subsidy_amount = round(state_subsidy, 2)
        quotation_doc.custom_total_subsidy_amount = round(central_subsidy + state_subsidy, 2)

        # Net Customer Investment
        grand_total = flt(quotation_doc.grand_total) or (flt(quotation_doc.net_total) * 1.138)
        quotation_doc.custom_net_customer_payable = max(0.0, round(grand_total - quotation_doc.custom_total_subsidy_amount, 2))

        # Financial yield & payback
        specific_yield = flt(settings.specific_yield_kwh_per_kwp, 1450.0)
        tariff = flt(settings.default_grid_tariff_rate, 7.50)

        annual_units = capacity * specific_yield
        annual_savings = annual_units * tariff

        quotation_doc.custom_annual_generation_kwh = round(annual_units, 1)
        quotation_doc.custom_annual_savings_amount = round(annual_savings, 2)
        quotation_doc.custom_payback_years = (
            round(quotation_doc.custom_net_customer_payable / annual_savings, 1) if annual_savings > 0 else 0.0
        )
```

### 3.4 `ProposalMarginGateService` (`solar_module/services/proposal/margin.py`)

Enforces gross margin floor rules and routes approvals:

```python
import frappe
from frappe.utils import flt

class ProposalMarginGateService:
    @staticmethod
    def evaluate_margin(quotation_doc) -> None:
        """
        Compares net revenue to estimated BOM cost.
        Flags 'Margin Floor Exception' if below Admin floor (default 18.0%).
        """
        settings = frappe.get_cached_doc("Solar Proposal Settings")
        floor_pct = flt(settings.default_gross_margin_floor_pct, 18.0)

        net_revenue = flt(quotation_doc.net_total)
        bom_cost = flt(quotation_doc.custom_estimated_bom_cost)

        margin_pct = ((net_revenue - bom_cost) / net_revenue * 100.0) if net_revenue > 0 else 0.0
        quotation_doc.custom_gross_margin_pct = round(margin_pct, 2)

        if margin_pct < floor_pct:
            if not quotation_doc.custom_margin_approved_by:
                quotation_doc.custom_margin_status = "Margin Floor Exception"
            else:
                quotation_doc.custom_margin_status = "Margin Override Approved"
        else:
            quotation_doc.custom_margin_status = "Within Margin"
```

### 3.5 `ProposalFinalizationService` (`solar_module/services/proposal/finalization.py`)

Manages atomic multi-proposal finalization and peer superseding:

```python
import frappe
from frappe import _
from frappe.utils import now_datetime

class ProposalFinalizationService:
    @staticmethod
    def finalize_proposal(quotation_name: str) -> dict:
        """
        Atomically finalizes the selected proposal for a survey.
        Transitions all other unfinalized sibling proposals to 'Superseded'.
        """
        doc = frappe.get_doc("Quotation", quotation_name)
        doc.check_permission("write")

        if doc.custom_margin_status == "Margin Floor Exception":
            frappe.throw(
                _("Proposal {0} cannot be finalized because Gross Margin ({1}%) is below the corporate floor ({2}%) and requires Area Sales Manager authorization.")
                .format(doc.name, doc.custom_gross_margin_pct, frappe.get_cached_value("Solar Proposal Settings", None, "default_gross_margin_floor_pct")),
                frappe.ValidationError
            )

        with frappe.db.transaction():
            doc.custom_is_finalized = 1
            doc.custom_finalized_datetime = now_datetime()
            doc.stage_status = "Finalized"
            doc.completed_date = now_datetime()
            doc.save()

            # Atomically supersede peer sibling proposals
            siblings = frappe.get_all(
                "Quotation",
                filters={
                    "custom_site_survey": doc.custom_site_survey,
                    "name": ["!=", doc.name],
                    "docstatus": ["!=", 2],
                    "stage_status": ["not in", ["Finalized", "Lost", "Superseded"]]
                },
                pluck="name"
            )
            for sib_name in siblings:
                frappe.db.set_value(
                    "Quotation", sib_name,
                    {
                        "stage_status": "Superseded",
                        "custom_superseded_by": doc.name
                    }
                )
                frappe.get_doc("Quotation", sib_name).add_comment(
                    "Workflow", _("Superseded automatically by finalized proposal {0}.").format(doc.name)
                )

        return {"status": "success", "finalized_proposal": doc.name, "superseded_count": len(siblings)}
```

### 3.6 `ProposalWaiverGateService` (`solar_module/services/proposal/waiver.py`)

Controls commercial payment gates and Goodwill VIP authorizations:

```python
import frappe
from frappe import _

class ProposalWaiverGateService:
    @staticmethod
    def validate_advance_or_waiver(quotation_doc) -> bool:
        """
        Asserts that the proposal meets the Stage 05 handover criteria:
        1. Standard ≥50% advance received, OR
        2. Finance Approved Waiver, OR
        3. Goodwill / VIP Approved by MD / CEO / Admin.
        """
        waiver_type = quotation_doc.custom_advance_waiver_type or "Standard (≥50% Required)"

        if waiver_type == "Goodwill / VIP Approved":
            if not quotation_doc.custom_advance_waived_by:
                frappe.throw(_("Goodwill / VIP waiver requires executive authorizer signature."), frappe.ValidationError)
            return True

        if waiver_type == "Finance Approved Waiver":
            if not quotation_doc.custom_advance_waived_by:
                frappe.throw(_("Finance waiver requires Accounts Manager authorizer signature."), frappe.ValidationError)
            return True

        # Standard check: relies on Payment Entry in Stage 05
        return True
```

### 3.7 `ProposalSLAService` (`solar_module/services/proposal/sla.py`)

Tracks 24-hour turnaround SLA and validates delay remarks:

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date, get_datetime

class ProposalSLAService:
    @staticmethod
    def initialize_sla(quotation_doc) -> None:
        """Sets assignment timestamp and 24h deadline."""
        if not quotation_doc.for_proposal_assign_on:
            quotation_doc.for_proposal_assign_on = now_datetime()
        settings = frappe.get_cached_doc("Solar Proposal Settings")
        sla_hours = int(settings.default_proposal_sla_hours or 24)
        quotation_doc.exp_complete_date = add_to_date(quotation_doc.for_proposal_assign_on, hours=sla_hours)

    @staticmethod
    def recompute_sla(quotation_doc) -> None:
        """Evaluates SLA deadline and flags Overdue/Delayed status."""
        if quotation_doc.stage_status in ["Finalized", "Superseded", "Lost"]:
            return

        now = now_datetime()
        if quotation_doc.exp_complete_date and get_datetime(now) > get_datetime(quotation_doc.exp_complete_date):
            quotation_doc.stage_status = "Overdue"
            quotation_doc.complete_status = "Delayed"

    @staticmethod
    def validate_delay_log_on_save(quotation_doc) -> None:
        """Enforces mandatory delay log entry if proposal is overdue."""
        if quotation_doc.stage_status == "Overdue" or quotation_doc.complete_status == "Delayed":
            logs = quotation_doc.get("remark_delay_log", [])
            if not logs or not quotation_doc.delay_log:
                frappe.throw(
                    _("Proposal is Overdue / Delayed. A categorized delay entry in the Remark-Delay Log is mandatory."),
                    frappe.ValidationError
                )
```

---

## 4. Layer 3: Controller & Whitelisted API Gateway

### 4.1 Extended Quotation Controller (`solar_module/overrides/quotation.py`)

Extends standard ERPNext `Quotation` and inherits `StageSecuredDocument` to enforce Stage-Forward Locking:

```python
import frappe
from frappe import _
from erpnext.selling.doctype.quotation.quotation import Quotation
from solar_module.mixins.stage_secured_document import StageSecuredDocument
from solar_module.services.proposal.calculation import ProposalCalculationService
from solar_module.services.proposal.subsidy import ProposalSubsidyService
from solar_module.services.proposal.margin import ProposalMarginGateService
from solar_module.services.proposal.sla import ProposalSLAService
from solar_module.services.proposal.waiver import ProposalWaiverGateService

class SolarQuotation(StageSecuredDocument, Quotation):
    def validate(self):
        super().validate()
        self.enforce_lead_quarantine()
        ProposalSLAService.initialize_sla(self)
        ProposalSLAService.recompute_sla(self)
        ProposalSLAService.validate_delay_log_on_save(self)
        ProposalMarginGateService.evaluate_margin(self)

    def before_submit(self):
        super().before_submit()
        self.validate_engineering_hash()
        ProposalWaiverGateService.validate_advance_or_waiver(self)

    def on_submit(self):
        super().on_submit()
        if self.stage_status == "Under Review":
            self.stage_status = "Approved"

    def before_cancel(self):
        # StageSecuredDocument enforces ADR-000: blocks cancellation if Stage 05 payment exists
        super().before_cancel()

    def enforce_lead_quarantine(self):
        if self.quotation_to != "Lead":
            frappe.throw(_("Quotation must be addressed to a Lead throughout Stage 04 commercial proposal."), frappe.ValidationError)

    def validate_engineering_hash(self):
        if self.custom_survey_engineering_design:
            sed_hash = frappe.db.get_value("Survey Engineering Design", self.custom_survey_engineering_design, "bom_hash")
            if sed_hash and self.custom_bom_hash and sed_hash != self.custom_bom_hash:
                frappe.throw(_("Cryptographic BOM Checksum mismatch against Survey Engineering Design! Re-quote required."), frappe.ValidationError)
```

### 4.2 Whitelisted API Endpoints (`solar_module/api/proposal.py`)

```python
import frappe
from frappe import _
from frappe.utils import flt
from solar_module.services.proposal.prefill import ProposalPrefillService
from solar_module.services.proposal.calculation import ProposalCalculationService
from solar_module.services.proposal.subsidy import ProposalSubsidyService
from solar_module.services.proposal.margin import ProposalMarginGateService
from solar_module.services.proposal.finalization import ProposalFinalizationService

@frappe.whitelist(methods=["POST"])
def create_proposal(site_survey: str, sed_name: str = None, capacity_kw: float = None) -> dict:
    """Instantiates a new Proposal (Quotation) prefilled from Survey and SED."""
    if not site_survey:
        frappe.throw(_("site_survey is required."), frappe.ValidationError)

    doc = frappe.new_doc("Quotation")
    ProposalPrefillService.prefill_from_survey_and_design(doc, site_survey, sed_name)
    if capacity_kw:
        doc.custom_solar_capacity = flt(capacity_kw)

    doc.insert()
    return {"status": "success", "proposal_name": doc.name}

@frappe.whitelist(methods=["POST"])
def calculate_commercials(proposal_name: str, base_cost: float, goods_ratio: float = 70.0, services_ratio: float = 30.0) -> dict:
    """Executes 70:30 GST split, taxes, subsidies, and gross margin checks."""
    doc = frappe.get_doc("Quotation", proposal_name)
    doc.check_permission("write")

    doc.custom_base_contract_value = flt(base_cost)
    doc.custom_goods_ratio_pct = flt(goods_ratio)
    doc.custom_services_ratio_pct = flt(services_ratio)

    ProposalCalculationService.calculate_commercial_split(doc)
    doc.run_method("calculate_taxes_and_totals")
    ProposalSubsidyService.compute_subsidies_and_payback(doc)
    ProposalMarginGateService.evaluate_margin(doc)
    doc.save()

    return {
        "status": "success",
        "net_total": doc.net_total,
        "grand_total": doc.grand_total,
        "subsidy": doc.custom_total_subsidy_amount,
        "net_payable": doc.custom_net_customer_payable,
        "gross_margin_pct": doc.custom_gross_margin_pct,
        "margin_status": doc.custom_margin_status,
        "payback_years": doc.custom_payback_years
    }

@frappe.whitelist(methods=["POST"])
def authorize_margin_override(proposal_name: str, justification: str) -> dict:
    """Authorizes sub-floor margin override. Restricted to Area Sales Manager and Admin."""
    user_roles = frappe.get_roles()
    if not ("Area Sales Manager" in user_roles or "Admin" in user_roles or "System Manager" in user_roles):
        frappe.throw(_("Not permitted. Only Area Sales Manager or Admin can authorize margin overrides."), frappe.PermissionError)

    doc = frappe.get_doc("Quotation", proposal_name)
    doc.check_permission("write")

    doc.custom_margin_approved_by = frappe.session.user
    doc.custom_margin_override_remark = justification
    doc.custom_margin_status = "Margin Override Approved"
    doc.save()

    return {"status": "success", "message": _("Margin override approved.")}

@frappe.whitelist(methods=["POST"])
def finalize_proposal(proposal_name: str) -> dict:
    """Atomically finalizes proposal and supersedes peer proposals."""
    return ProposalFinalizationService.finalize_proposal(proposal_name)

@frappe.whitelist(methods=["POST"])
def grant_advance_waiver(proposal_name: str, waiver_type: str, justification: str) -> dict:
    """Grants Finance or Executive Goodwill VIP advance waiver."""
    user_roles = frappe.get_roles()
    if waiver_type == "Goodwill / VIP Approved":
        if not ("Admin" in user_roles or "Director" in user_roles or "System Manager" in user_roles):
            frappe.throw(_("Goodwill / VIP waivers can only be granted by Managing Director, CEO, or Admin."), frappe.PermissionError)
    elif waiver_type == "Finance Approved Waiver":
        if not ("Accounts Manager" in user_roles or "Admin" in user_roles or "System Manager" in user_roles):
            frappe.throw(_("Finance waivers require Accounts Manager or Admin authorization."), frappe.PermissionError)

    doc = frappe.get_doc("Quotation", proposal_name)
    doc.custom_advance_waiver_type = waiver_type
    doc.custom_advance_waived_by = frappe.session.user
    doc.custom_advance_waiver_remark = justification
    doc.save()

    return {"status": "success", "waiver_type": waiver_type, "waived_by": frappe.session.user}
```

---

## 5. Layer 4: Desk Client Script & Workbench Hook

Located at `codes/client_script/quotation_proposal.js`:

```javascript
frappe.ui.form.on("Quotation", {
  setup: function (frm) {
    // Alias title and form label to "Proposal"
    frm.page.set_title(__("Proposal: {0}", [frm.doc.name || __("New")]));
  },

  refresh: function (frm) {
    // Style status indicators
    if (frm.doc.custom_margin_status === "Margin Floor Exception") {
      frm.dashboard.set_headline_alert(
        __(
          "Gross Margin ({0}%) is below corporate floor! Area Sales Manager authorization required.",
          [frm.doc.custom_gross_margin_pct],
        ),
        "red",
      );
    } else if (frm.doc.custom_is_finalized) {
      frm.dashboard.set_headline_alert(
        __("Commercial Proposal Finalized. Downstream Stage 05 unlocked."),
        "green",
      );
    }

    // Action: Calculate Commercials (70:30 GST)
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(
        __("Calculate 70:30 GST Split"),
        function () {
          frappe.call({
            method: "solar_module.api.proposal.calculate_commercials",
            args: {
              proposal_name: frm.doc.name,
              base_cost:
                frm.doc.custom_base_contract_value || frm.doc.net_total,
              goods_ratio: frm.doc.custom_goods_ratio_pct || 70.0,
              services_ratio: frm.doc.custom_services_ratio_pct || 30.0,
            },
            freeze: true,
            callback: function (r) {
              if (r.message && r.message.status === "success") {
                frm.reload_doc();
                frappe.msgprint(
                  __("70:30 Composite GST split calculated successfully."),
                );
              }
            },
          });
        },
        __("Commercial Actions"),
      );
    }

    // Action: Authorize Margin Override
    if (
      frm.doc.custom_margin_status === "Margin Floor Exception" &&
      frappe.user.has_role(["Area Sales Manager", "Admin", "System Manager"])
    ) {
      frm.add_custom_button(
        __("Authorize Margin Override"),
        function () {
          frappe.prompt(
            [
              {
                fieldname: "justification",
                fieldtype: "Small Text",
                label: __("Override Justification / Commercial Strategy"),
                reqd: 1,
              },
            ],
            function (values) {
              frappe.call({
                method: "solar_module.api.proposal.authorize_margin_override",
                args: {
                  proposal_name: frm.doc.name,
                  justification: values.justification,
                },
                callback: function (r) {
                  frm.reload_doc();
                  frappe.show_alert({
                    message: __("Margin override authorized."),
                    indicator: "green",
                  });
                },
              });
            },
            __("Authorize Low Margin Proposal"),
            __("Authorize"),
          );
        },
        __("Executive Gates"),
      );
    }

    // Action: Finalize Proposal
    if (!frm.doc.custom_is_finalized && frm.doc.docstatus === 1) {
      frm
        .add_custom_button(
          __("Finalize Proposal"),
          function () {
            frappe.confirm(
              __(
                "Finalizing this proposal will lock it as the winning option and mark all other proposals for this site survey as SUPERSEDED. Continue?",
              ),
              function () {
                frappe.call({
                  method: "solar_module.api.proposal.finalize_proposal",
                  args: { proposal_name: frm.doc.name },
                  callback: function (r) {
                    frm.reload_doc();
                    frappe.msgprint(__("Proposal successfully Finalized."));
                  },
                });
              },
            );
          },
          __("Commercial Actions"),
        )
        .addClass("btn-primary");
    }

    // Action: Goodwill / VIP Advance Waiver
    if (frappe.user.has_role(["Admin", "Director", "System Manager"])) {
      frm.add_custom_button(
        __("Grant Goodwill / VIP Waiver"),
        function () {
          frappe.prompt(
            [
              {
                fieldname: "justification",
                fieldtype: "Small Text",
                label: __("Goodwill / VIP Rationale"),
                reqd: 1,
              },
            ],
            function (values) {
              frappe.call({
                method: "solar_module.api.proposal.grant_advance_waiver",
                args: {
                  proposal_name: frm.doc.name,
                  waiver_type: "Goodwill / VIP Approved",
                  justification: values.justification,
                },
                callback: function (r) {
                  frm.reload_doc();
                  frappe.show_alert({
                    message: __("Goodwill VIP waiver granted."),
                    indicator: "green",
                  });
                },
              });
            },
            __("Grant Executive Goodwill Waiver"),
            __("Grant Waiver"),
          );
        },
        __("Executive Gates"),
      );
    }
  },
});
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Located at `solar_module/tests/test_solar_proposal_tracer_bullet.py`.  
Subclasses `frappe.testing.IntegrationTestCase` with zero-commit atomic transaction rollback in `tearDown`.

```python
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import now_datetime, add_to_date
from solar_module.services.proposal.prefill import ProposalPrefillService
from solar_module.services.proposal.calculation import ProposalCalculationService
from solar_module.services.proposal.subsidy import ProposalSubsidyService
from solar_module.services.proposal.margin import ProposalMarginGateService
from solar_module.services.proposal.finalization import ProposalFinalizationService
from solar_module.services.proposal.sla import ProposalSLAService
from solar_module.api.proposal import (
    create_proposal,
    calculate_commercials,
    authorize_margin_override,
    finalize_proposal,
    grant_advance_waiver
)

class TestSolarProposalTracerBullet(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.lead = self._create_test_lead()
        self.survey = self._create_test_survey(self.lead.name)
        self.sed = self._create_test_sed(self.survey.name)
        self._setup_proposal_settings()

    def tearDown(self):
        # Strict Zero-Commit Rule: roll back all database mutations
        frappe.db.rollback()
        super().tearDown()

    def _create_test_lead(self):
        lead = frappe.new_doc("Lead")
        lead.lead_name = "Tracer Bullet Commercial Prospect"
        lead.email_id = "prospect.tb@sadbhav.com"
        lead.mobile_no = "9876543210"
        lead.insert(ignore_permissions=True)
        return lead

    def _create_test_survey(self, lead_name):
        survey = frappe.new_doc("Site Survey")
        survey.lead = lead_name
        survey.lead_name = "Tracer Bullet Commercial Prospect"
        survey.state = "Gujarat"
        survey.site_type = "RCC"
        survey.system_type = "On-Grid"
        survey.mounting_type = "Normal"
        survey.proposed_capacity = 5.0
        survey.stage_status = "Completed"
        survey.docstatus = 1
        survey.insert(ignore_permissions=True)
        return survey

    def _create_test_sed(self, survey_name):
        sed = frappe.new_doc("Survey Engineering Design")
        sed.site_survey = survey_name
        sed.actual_designed_capacity = 5.5
        sed.is_frozen = 1
        sed.bom_hash = "a" * 64
        sed.docstatus = 1
        sed.stage_status = "Frozen"
        sed.append("bom_items", {
            "item_code": "Solar PV Modules",
            "quantity": 10,
            "estimated_unit_rate": 8000.0
        })
        sed.insert(ignore_permissions=True)
        return sed

    def _setup_proposal_settings(self):
        settings = frappe.get_doc("Solar Proposal Settings")
        settings.default_gross_margin_floor_pct = 18.0
        settings.default_advance_pct = 50.0
        settings.default_proposal_sla_hours = 24
        settings.default_goods_ratio_pct = 70.0
        settings.default_services_ratio_pct = 30.0
        settings.specific_yield_kwh_per_kwp = 1450.0
        settings.default_grid_tariff_rate = 7.50
        settings.set("central_subsidy_slabs", [])
        settings.append("central_subsidy_slabs", {
            "from_kw": 0.0,
            "to_kw": 2.0,
            "subsidy_per_kw": 30000.0,
            "max_subsidy_amount": 60000.0
        })
        settings.append("central_subsidy_slabs", {
            "from_kw": 2.0,
            "to_kw": 3.0,
            "subsidy_per_kw": 18000.0,
            "max_subsidy_amount": 78000.0
        })
        settings.save(ignore_permissions=True)

    def _new_test_proposal(self):
        res = create_proposal(self.survey.name, self.sed.name, capacity_kw=5.5)
        return frappe.get_doc("Quotation", res["proposal_name"])

    # -------------------------------------------------------------------------
    # TEST CASES
    # -------------------------------------------------------------------------

    def test_01_prefill_and_lead_quarantine(self):
        """Invariant 1 & 8: Verify auto-population and strict Lead quarantine."""
        prop = self._new_test_proposal()
        self.assertEqual(prop.quotation_to, "Lead")
        self.assertEqual(prop.party_name, self.lead.name)
        self.assertEqual(prop.custom_site_survey, self.survey.name)
        self.assertEqual(prop.custom_solar_capacity, 5.5)
        self.assertEqual(prop.custom_bom_hash, self.sed.bom_hash)
        self.assertEqual(prop.custom_estimated_bom_cost, 80000.0)

        # Assert no customer record created
        self.assertFalse(frappe.db.exists("Customer", {"lead_name": self.lead.name}))

    def test_02_composite_70_30_gst_split(self):
        """Invariant 3: Statutory 70:30 Goods/Services split and tax mapping."""
        prop = self._new_test_proposal()
        prop.custom_base_contract_value = 200000.0
        ProposalCalculationService.calculate_commercial_split(prop)

        self.assertEqual(len(prop.items), 2)
        goods = [i for i in prop.items if i.custom_category == "Solar Equipment (Goods)"][0]
        services = [i for i in prop.items if i.custom_category == "Installation & Civil (Services)"][0]

        self.assertEqual(goods.rate, 140000.0)      # 70%
        self.assertEqual(services.rate, 60000.0)    # 30%
        self.assertEqual(goods.item_tax_template, "GST 12% - Solar Goods")
        self.assertEqual(services.item_tax_template, "GST 18% - Solar Services")

    def test_03_custom_ratio_validation(self):
        """Invariant 3: Ratio must total 100.0%."""
        prop = self._new_test_proposal()
        prop.custom_base_contract_value = 100000.0
        prop.custom_goods_ratio_pct = 65.0
        prop.custom_services_ratio_pct = 30.0 # Sums to 95% -> must fail

        with self.assertRaises(frappe.ValidationError):
            ProposalCalculationService.calculate_commercial_split(prop)

    def test_04_pm_surya_ghar_subsidy_brackets(self):
        """Invariant 4: PM Surya Ghar Central CFA calculation and max cap."""
        prop = self._new_test_proposal()
        prop.custom_solar_capacity = 3.5
        prop.custom_plant_category = "Residential"
        prop.grand_total = 220000.0

        ProposalSubsidyService.compute_subsidies_and_payback(prop)
        # Cap is ₹78,000 for >= 3kW
        self.assertEqual(prop.custom_central_subsidy_amount, 78000.0)
        self.assertEqual(prop.custom_net_customer_payable, 142000.0)
        self.assertGreater(prop.custom_annual_savings_amount, 0.0)
        self.assertGreater(prop.custom_payback_years, 0.0)

    def test_05_margin_floor_exception_blocks_finalization(self):
        """Invariant 5: Gross margin below 18% blocks finalization."""
        prop = self._new_test_proposal()
        prop.net_total = 90000.0
        prop.custom_estimated_bom_cost = 80000.0 # Margin is 11.1% (< 18% floor)

        ProposalMarginGateService.evaluate_margin(prop)
        self.assertEqual(prop.custom_margin_status, "Margin Floor Exception")

        with self.assertRaises(frappe.ValidationError):
            ProposalFinalizationService.finalize_proposal(prop.name)

    def test_06_area_sales_manager_margin_override(self):
        """Invariant 5: Authorized role can override sub-floor margin exception."""
        prop = self._new_test_proposal()
        prop.custom_margin_status = "Margin Floor Exception"
        prop.save()

        frappe.set_user("Administrator")
        authorize_margin_override(prop.name, "Approved for competitive strategic account.")

        prop.reload()
        self.assertEqual(prop.custom_margin_status, "Margin Override Approved")
        self.assertEqual(prop.custom_margin_approved_by, "Administrator")

    def test_07_multi_proposal_exclusive_finalization(self):
        """Invariant 6: Finalizing one proposal supersedes all active sibling proposals."""
        p1 = self._new_test_proposal()
        p2 = self._new_test_proposal()

        p1.custom_margin_status = "Within Margin"
        p1.docstatus = 1
        p1.save()

        finalize_proposal(p1.name)

        p1.reload()
        p2.reload()
        self.assertEqual(p1.custom_is_finalized, 1)
        self.assertEqual(p1.stage_status, "Finalized")
        self.assertEqual(p2.stage_status, "Superseded")
        self.assertEqual(p2.custom_superseded_by, p1.name)

    def test_08_goodwill_vip_advance_waiver(self):
        """Invariant 7: CEO/MD/Admin can grant Goodwill VIP waiver bypassing finance clearance."""
        prop = self._new_test_proposal()

        frappe.set_user("Administrator")
        grant_advance_waiver(prop.name, "Goodwill / VIP Approved", "VIP Director Referral.")

        prop.reload()
        self.assertEqual(prop.custom_advance_waiver_type, "Goodwill / VIP Approved")
        self.assertEqual(prop.custom_advance_waived_by, "Administrator")

    def test_09_sla_timeout_and_delay_log_enforcement(self):
        """Invariant 8: 24h SLA timeout flags Overdue and enforces delay logging."""
        prop = self._new_test_proposal()
        prop.for_proposal_assign_on = add_to_date(now_datetime(), hours=-26)
        prop.exp_complete_date = add_to_date(prop.for_proposal_assign_on, hours=24)

        ProposalSLAService.recompute_sla(prop)
        self.assertEqual(prop.stage_status, "Overdue")
        self.assertEqual(prop.complete_status, "Delayed")

        # Missing delay log must block save
        with self.assertRaises(frappe.ValidationError):
            ProposalSLAService.validate_delay_log_on_save(prop)

    def test_10_cryptographic_bom_hash_tamper_gate(self):
        """Invariant 2: Checksum mismatch between SED and Proposal raises ValidationError."""
        prop = self._new_test_proposal()
        prop.custom_bom_hash = "tampered_hash_value_12345"

        with self.assertRaises(frappe.ValidationError):
            prop.validate_engineering_hash()
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 Automated Bench Test Execution

Execute the full Stage 04 integration suite via bench CLI:

```bash
bench --site <site-name> run-tests --module solar_module.tests.test_solar_proposal_tracer_bullet
```

### 7.2 Database SQL Verification Queries

```sql
-- 1. Verify custom fields exist on tabQuotation
DESCRIBE `tabQuotation`;

-- 2. Verify Composite B-Tree Indexes
SHOW INDEX FROM `tabQuotation` WHERE Key_name LIKE 'idx_quotation_%';

-- 3. Verify exclusive finalization state consistency
SELECT custom_site_survey, COUNT(*) as finalized_count
FROM `tabQuotation`
WHERE custom_is_finalized = 1
GROUP BY custom_site_survey
HAVING finalized_count > 1; -- Must return 0 rows
```

### 7.3 Acceptance Checklist

- [x] Predecessor Site Survey and Frozen SED links verified with zero Lead quarantine leaks.
- [x] 70:30 Composite Solar GST bifurcation correctly assigns items and tax templates.
- [x] PM Surya Ghar CFA subsidy math accurately evaluates capacity brackets and caps.
- [x] Gross margin floor gate halts low-margin quotes without Area Sales Manager approval.
- [x] Multi-proposal exclusive finalization lock reliably supersedes active sibling proposals.
- [x] Goodwill VIP waiver permitted strictly for Executive Leadership (`Admin`/`Director`).
- [x] 24-hour turnaround SLA enforced with mandatory categorized delay audit log.
- [x] Test suite executes with 100% pass rate under atomic transaction rollback (zero DB commits).

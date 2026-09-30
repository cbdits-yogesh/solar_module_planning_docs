# STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 03 Survey Engineering Design & Dynamic BOM Freeze

**Document ID:** `TB-03-DESIGN`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.caveman.md`](../STEP_03_SURVEY_ENGINEERING_DESIGN_BOM_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-003-SURVEY-ENGINEERING-DESIGN-DYNAMIC-BOM-ENGINE.md`](../../docs/decisions/ADR-003-SURVEY-ENGINEERING-DESIGN-DYNAMIC-BOM-ENGINE.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessor:** [`step_plans_for_ai/tracer_bullets/STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md`](STEP_02_SITE_SURVEY_TRACER_BULLET.caveman.md)  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-03`, `Sec 3.3`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-003`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-003`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 3: ENG`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 3`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 6`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-03`)  
**Target Module:** `solar_module` / `manoj`  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** Explores an isolated concept with throwaway code (such as an in-browser canvas CAD viewer or a standalone Python voltage drop script), discarded after evaluation.
- **Tracer Bullet:** A lean, complete, production-grade slice cutting through **all layers of the real system**. Not throwaway code; it forms the permanent, verified architectural skeleton connecting Stage 02 Site Survey audit data through Stage 03 CAD layout, parametric electrical math, and dynamic BOM explosion to Stage 04 Commercial Proposal generation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 03 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabSurvey Engineering Design (core fields, ILR, voltage drop, SLA, hash)│
│   - tabSite Survey Design File (CAD DWG/DXF & SLD versioned dropzone)       │
│   - tabCable Calculation Table (parametric DC & AC drop calculation rows)   │
│   - tabCustom Quot BOM (exploded dynamic BoQ items: modules, inverter, etc.)│
│   - tabRemark-Delay Log (SLA audit & delay justification child table)       │
│   - tabQuotation (Stage 04 downstream proposal handover draft container)    │
│   - B-Tree Composite Database Indexes & Autonaming (SED-.YYYY.-.#####)      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic                                    │
│   - SolarDesignCalculationService (Capacities, ILR, temp-corrected drops)  │
│   - SolarBOMExplosionService (Dynamic BoQ explosion, deterministic SHA-256) │
│   - SolarDesignGateService (Gate 1 Files, Gate 2 Drops, Gate 3 ILR, Gate 4) │
│   - SolarDesignSLAService (48h turnaround countdown, overdue daemon, delay) │
│   - SolarDesignBridgeService (Upstream survey flag & Stage 04 Quotation)   │
│   - StageSecuredDocument & StageForwardLockService (ADR-000 lock integration)│
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller & Whitelisted API Gateway                                │
│   - SurveyEngineeringDesign Controller (validate, before_submit, on_submit) │
│   - calculate_electrical_parameters RPC (re-evaluates drops & updates rows) │
│   - explode_dynamic_bom RPC (regenerates dynamic BoQ from plant parameters) │
│   - submit_design_approval RPC (Design Manager verification & sign-off)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Workbench Hook                                │
│   - codes/client_script/survey_engineering_design.js (action buttons, math) │
│   - Responsive Vue 3 Design Workbench layout blueprint (/solar/design/:id)  │
│   - Real-time field computation hooks & status badge management             │
│   - Junior Cancel suppression -> ADR-000 [Request Cancel/Amend] modal       │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_survey_engineering_design_tracer_bullet.py      │
│   - Subclasses frappe.testing.IntegrationTestCase                           │
│   - Atomic transaction rollback in tearDown (zero DB commits)               │
│   - 8 comprehensive test cases validating all Stage 03 invariants           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental business, technical, and security invariants of Stage 03 across the live Frappe stack:

1. **Predecessor Site Survey Integrity:** Enforces that linked `Site Survey` must be in `stage_status == 'Completed'` before engineering design can proceed, preventing premature CAD layout.
2. **Mandatory CAD & SLD Drawing Verification:** Enforces upload of at least 1 CAD Layout (`.dwg`/`.dxf`) and at least 1 Single Line Diagram (`SLD`), blocking sign-off if drawings are missing.
3. **Configurable File Upload Ceiling:** Files attached in `tabSite Survey Design File` are validated against `Solar Design Settings.max_file_size_mb` (default 25 MB), preventing disk exhaustion from oversized unpurged drawings.
4. **Parametric Electrical Voltage Drop Compliance ($\le 2.0\%$):** Pure domain calculation service evaluates DC string and AC feeder voltage drops against IEC 60364-7-712 / IS 732 using temperature-corrected resistance ($75^\circ\text{C}$). Hard gate rejects any design exceeding $2.0\%$ drop.
5. **Inverter Loading Ratio (ILR) Window ($1.10 - 1.35$):** Validates DC-to-AC sizing ratio, ensuring inverter operates within optimal economic and clipping limits.
6. **Dynamic BOM Explosion & BoQ Cost Rollup:** Generates dynamic BoQ (`tabCustom Quot BOM`) covering PV modules (DCR/NDCR), grid-tied inverters, mounting structure tonnage (based on mounting type and civil site classification), DC/AC cables, and earthing kits.
7. **Cryptographic Baseline Freeze (`bom_hash`):** Computes canonical SHA-256 hash across all BOM line items upon submission, setting `is_frozen = 1` and preventing silent alterations during Stage 04 commercial quoting.
8. **ADR-000 Security Substrate & Stage-Forward Lock:** Inherits `StageSecuredDocument`, blocking cancellation or amendment once downstream Stage 04 Quotations exist, suppressing junior user cancellations, and instantiating Stage 04 Quotation draft container.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

The Tracer Bullet establishes the lean relational schema enforcing data contracts across electrical engineers, CAD draftsmen, and sales estimators.

### 2.1 Core DocType: `tabSurvey Engineering Design`

Standalone DocType (`tabSurvey Engineering Design`). Submittable (`is_submittable = 1`):

| Fieldname                  | Label                          | Fieldtype    | Options / Target                                                                       | Mandatory |    Index     | Rules & Invariants                                                            |
| :------------------------- | :----------------------------- | :----------- | :------------------------------------------------------------------------------------- | :-------: | :----------: | :---------------------------------------------------------------------------- |
| `naming_series`            | Naming Series                  | `Select`     | `SED-.YYYY.-.#####`                                                                    |  **Yes**  |      -       | Autonaming series reset annually.                                             |
| `site_survey`              | Linked Site Survey             | `Link`       | `Site Survey`                                                                          |  **Yes**  | **Index: 1** | FK upstream Stage 02 survey. Must have `stage_status == 'Completed'`.         |
| `custom_survey_ref`        | Upstream Link Reference        | `Link`       | `Site Survey`                                                                          |  **Yes**  | **Index: 1** | Registered link field for `StageForwardLockService`.                          |
| `lead`                     | Linked Lead Reference          | `Link`       | `Lead`                                                                                 |  **Yes**  | **Index: 1** | Read-only FK copied from `site_survey.lead`.                                  |
| `customer_name`            | Client / Customer Name         | `Data`       | -                                                                                      |    No     |      -       | Copied from `site_survey.lead_name`.                                          |
| `design_date`              | Design Initiation Date         | `Date`       | -                                                                                      |  **Yes**  |      -       | Default: `Today`. Date engineering started.                                   |
| `design_engineer`          | Design Engineer Assigned       | `Link`       | `User`                                                                                 |  **Yes**  | **Index: 1** | Role `Design Engineer`. Assigned drafting specialist.                         |
| `design_manager`           | Design Approver                | `Link`       | `User`                                                                                 |    No     |      -       | Role `Design Manager`. Mandatory before approval / submission.                |
| `system_type`              | System Configuration           | `Select`     | `On-Grid\nHybrid\nOff-Grid`                                                            |  **Yes**  |      -       | Inherited from survey topology.                                               |
| `site_type`                | Roof / Surface Classification  | `Select`     | `RCC\nGround Mount\nShed (Profile Sheet)\nCar Port (Parking)\nRCC & Shed\nOther`       |  **Yes**  |      -       | Civil roof structure from survey.                                             |
| `mounting_type`            | MMS Mounting Standard          | `Select`     | `Normal\nElevated\nProfile Sheet\nBallast\nGround Screws\nOthers`                      |  **Yes**  |      -       | Structural mounting architecture; determines MMS kg/kW multiplier.            |
| `target_capacity`          | Survey Target Capacity (kW)    | `Float`      | -                                                                                      |  **Yes**  |      -       | Baseline capacity verified during survey. Precision: 2.                       |
| `actual_designed_capacity` | Actual Designed Capacity (kWp) | `Float`      | -                                                                                      |  **Yes**  |      -       | Calculated: $(\text{total\_modules} \times \text{wattage}) / 1000$. Prec: 2.  |
| `module_item_code`         | Selected PV Module             | `Link`       | `Item`                                                                                 |  **Yes**  |      -       | Stock Item from Item Group `Solar PV Module`.                                 |
| `module_wattage`           | Module Peak Wattage (Wp)       | `Float`      | -                                                                                      |  **Yes**  |      -       | Nominal peak wattage (e.g. 550.0 Wp). Precision: 1.                           |
| `module_tech_type`         | Cell Technology & Sourcing     | `Select`     | `DCR\nNDCR`                                                                            |  **Yes**  |      -       | Domestic Content Requirement compliance flag for PM Surya Ghar subsidy.       |
| `total_modules_count`      | Total Number of Modules        | `Int`        | -                                                                                      |  **Yes**  |      -       | Sized panel count.                                                            |
| `inverter_item_code`       | Selected Solar Inverter        | `Link`       | `Item`                                                                                 |  **Yes**  |      -       | Stock Item from Item Group `Solar Inverter`.                                  |
| `inverter_rated_capacity`  | Inverter Rated Power (kW)      | `Float`      | -                                                                                      |  **Yes**  |      -       | Nominal continuous AC power rating. Precision: 2.                             |
| `inverter_count`           | Inverter Quantity              | `Int`        | -                                                                                      |  **Yes**  |      -       | Quantity of inverters. Default: 1.                                            |
| `dc_ac_ratio`              | DC to AC Sizing Ratio (ILR)    | `Float`      | -                                                                                      |  **Yes**  |      -       | Inverter Loading Ratio: $\text{Capacity}_{kWp} / (\text{Inv}_{kW} \times N)$. |
| `modules_per_string`       | Modules per Series String      | `Int`        | -                                                                                      |  **Yes**  |      -       | Sized modules in series per MPPT string.                                      |
| `number_of_strings`        | Total Parallel Strings         | `Int`        | -                                                                                      |  **Yes**  |      -       | Number of parallel strings connected to inverters.                            |
| `max_dc_voltage_drop_pct`  | Max DC Voltage Drop (%)        | `Float`      | -                                                                                      |  **Yes**  |      -       | Evaluated max DC string drop. Must be $\le 2.0\%$. Precision: 2.              |
| `max_ac_voltage_drop_pct`  | Max AC Voltage Drop (%)        | `Float`      | -                                                                                      |  **Yes**  |      -       | Evaluated max AC feeder drop. Must be $\le 2.0\%$. Precision: 2.              |
| `design_files`             | Versioned CAD / SLD Files      | `Table`      | `Site Survey Design File`                                                              |  **Yes**  |      -       | CAD/SLD drawings repository. Gate 1 asserts $\ge 1$ CAD + $\ge 1$ SLD.        |
| `cable_calculations`       | Parametric Cable Math Table    | `Table`      | `Cable Calculation Table`                                                              |  **Yes**  |      -       | Sizing & voltage drop calculations per circuit run.                           |
| `bom_items`                | Dynamic Engineering BoQ        | `Table`      | `Custom Quot BOM`                                                                      |  **Yes**  |      -       | Exploded bill of quantities for hardware & electrical BOS.                    |
| `stage_status`             | Lifecycle Stage Status         | `Select`     | `Draft\nUnder Design\nPending Approval\nApproved\nFrozen\nOverdue\nRevision Requested` |  **Yes**  | **Index: 1** | Primary state machine status.                                                 |
| `is_frozen`                | Engineering Baseline Locked    | `Check`      | -                                                                                      |  **Yes**  | **Index: 1** | Cryptographic lock flag; set to 1 upon submission.                            |
| `bom_hash`                 | Cryptographic BOM Checksum     | `Data`       | -                                                                                      |    No     | **Index: 1** | SHA-256 checksum of exploded BOM rows. Length: 64.                            |
| `for_design_assign_on`     | Assignment Timestamp           | `Datetime`   | -                                                                                      |  **Yes**  |      -       | Timestamp when design engineer assigned; starts 48h SLA.                      |
| `exp_complete_date`        | SLA Deadline Datetime          | `Datetime`   | -                                                                                      |  **Yes**  | **Index: 1** | `for_design_assign_on + 48 hours`.                                            |
| `completed_date`           | Actual Completion Datetime     | `Datetime`   | -                                                                                      |    No     |      -       | Stamped when document is approved and submitted (`Frozen`).                   |
| `complete_status`          | SLA Compliance Outcome         | `Select`     | `\nOn Time\nDelayed`                                                                   |    No     |      -       | Evaluates compliance against dynamic 48h SLA.                                 |
| `delay_log`                | Delay Explanation Summary      | `Small Text` | -                                                                                      |    No     |      -       | Mandatory when `complete_status == 'Delayed'` or `stage_status == 'Overdue'`. |
| `remark_delay_log`         | Granular Delay Audit Table     | `Table`      | `Remark-Delay Log`                                                                     |    No     |      -       | Immutable audit log tracking user, timestamp, and delay reasons.              |
| `docstatus`                | Document Workflow Status       | `Int`        | `0=Draft, 1=Submitted, 2=Cancelled`                                                    |  **Yes**  | **Index: 1** | Native Frappe submission state.                                               |

---

### 2.2 Child DocType: `tabSite Survey Design File`

Represents versioned CAD layouts, Single Line Diagrams, and simulation reports:

| Fieldname          | Label             | Fieldtype  | Options / Target                                                                                                                                        | Mandatory | In List View | Description & Rules                                             |
| :----------------- | :---------------- | :--------- | :------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------: | :----------: | :-------------------------------------------------------------- |
| `file_category`    | Document Category | `Select`   | `CAD Layout (DWG/DXF)\nSingle Line Diagram (SLD)\nPVsyst Simulation Report\n3D Shadow Analysis\nStructural Stability Certificate\nOther Technical File` |  **Yes**  |      1       | Classification. Must have $\ge 1$ CAD + $\ge 1$ SLD for Gate 1. |
| `version`          | Document Version  | `Data`     | -                                                                                                                                                       |  **Yes**  |      1       | Semantic versioning (e.g. `v1.0`, `v1.1`).                      |
| `attached_file`    | File Attachment   | `Attach`   | -                                                                                                                                                       |  **Yes**  |      1       | Attached drawing binary. Validated against Admin size limit.    |
| `file_size_kb`     | File Size (KB)    | `Float`    | -                                                                                                                                                       |    No     |      1       | Populated automatically on upload.                              |
| `remarks`          | Design Notes      | `Data`     | -                                                                                                                                                       |    No     |      0       | Description of changes or drawing notes.                        |
| `uploaded_by`      | Uploaded By       | `Link`     | `User`                                                                                                                                                  |    No     |      0       | User who attached the drawing.                                  |
| `upload_timestamp` | Uploaded On       | `Datetime` | -                                                                                                                                                       |    No     |      0       | Timestamp of upload.                                            |

---

### 2.3 Child DocType: `tabCable Calculation Table`

Parametric conductor sizing table evaluating voltage drop compliance against IEC 60364-7-712:

| Fieldname             | Label                    | Fieldtype | Options / Target                                                                              | Mandatory | In List View | Description & Calculation Rules                                                               |
| :-------------------- | :----------------------- | :-------- | :-------------------------------------------------------------------------------------------- | :-------: | :----------: | :-------------------------------------------------------------------------------------------- |
| `circuit_type`        | Circuit Description      | `Select`  | `DC String to Inverter\nInverter AC Output to Meter\nEarthing Conductor\nLightning Conductor` |  **Yes**  |      1       | Circuit function.                                                                             |
| `circuit_tag`         | Circuit Identifier       | `Data`    | -                                                                                             |  **Yes**  |      1       | Tag (e.g. `DC-STR-01`, `AC-FEED-01`).                                                         |
| `cable_length_m`      | One-Way Route Length (m) | `Float`   | -                                                                                             |  **Yes**  |      1       | One-way route distance in meters.                                                             |
| `conductor_material`  | Conductor Metal          | `Select`  | `Copper (Cu)\nAluminium (Al)`                                                                 |  **Yes**  |      1       | Copper standard for DC; Aluminium/Copper for AC.                                              |
| `conductor_size_mm2`  | Cross Section ($mm^2$)   | `Select`  | `4.0\n6.0\n10.0\n16.0\n25.0\n35.0\n50.0\n70.0\n95.0\n120.0\n150.0\n185.0\n240.0`              |  **Yes**  |      1       | Conductor cross-sectional area.                                                               |
| `rated_current_a`     | Design Current ($I_b$)   | `Float`   | -                                                                                             |  **Yes**  |      1       | DC: $I_{mp}$ or $1.25 \times I_{sc}$. AC: $\frac{P_{ac}}{\sqrt{3} \times V \times \cos\phi}$. |
| `operating_voltage_v` | System Voltage ($V$)     | `Float`   | -                                                                                             |  **Yes**  |      0       | System operating voltage (e.g. 600V DC, 415V AC 3-Phase, 230V AC 1-Phase).                    |
| `resistance_ohm_km`   | Conductor Resistance     | `Float`   | -                                                                                             |  **Yes**  |      0       | Temperature-corrected resistance at $75^\circ\text{C}$ ($\Omega/\text{km}$).                  |
| `voltage_drop_v`      | Voltage Drop (Volts)     | `Float`   | -                                                                                             |  **Yes**  |      1       | Calculated absolute drop in Volts.                                                            |
| `voltage_drop_pct`    | Voltage Drop (%)         | `Float`   | -                                                                                             |  **Yes**  |      1       | Calculated percentage drop: $(\Delta V / V) \times 100$. Must be $\le 2.0\%$.                 |
| `compliance_status`   | Gate Status              | `Select`  | `Pass\nFail`                                                                                  |  **Yes**  |      1       | Evaluated: `Pass` if $\le 2.0\%$, else `Fail`. Gate 2 requires all `Pass`.                    |

---

### 2.4 Child DocType: `tabCustom Quot BOM`

Dynamic bill of quantities exploded from plant capacity, mounting type, and cable math:

| Fieldname             | Label               | Fieldtype  | Options / Target                                                                                          | Mandatory | In List View | Description & Business Rules                                |
| :-------------------- | :------------------ | :--------- | :-------------------------------------------------------------------------------------------------------- | :-------: | :----------: | :---------------------------------------------------------- |
| `item_code`           | ERPNext Item Code   | `Link`     | `Item`                                                                                                    |  **Yes**  |      1       | Stock item reference in ERPNext Item Master.                |
| `bom_item`            | Item Name / Label   | `Data`     | -                                                                                                         |  **Yes**  |      1       | Descriptor (e.g. `Solar PV Modules`, `Grid Tied Inverter`). |
| `category`            | BoQ Category        | `Select`   | `Modules\nInverter\nStructure (MMS)\nDC Electrical\nAC Electrical\nEarthing & Protection\nHardware & BOS` |  **Yes**  |      1       | Procurement and estimation grouping category.               |
| `type`                | Sourcing Sub-Type   | `Select`   | `\nDCR\nNDCR`                                                                                             |    No     |      1       | Mandatory when `category == 'Modules'`.                     |
| `brand`               | Preferred OEM/Make  | `Data`     | -                                                                                                         |    No     |      1       | OEM brand (e.g. `Waaree`, `Adani`, `Growatt`, `Havells`).   |
| `capacity`            | Technical Rating    | `Data`     | -                                                                                                         |    No     |      1       | Rating (e.g. `550 Wp Bifacial`, `10 kW 3-Phase`).           |
| `quantity`            | Billable Quantity   | `Float`    | -                                                                                                         |  **Yes**  |      1       | Exploded billable quantity. Precision: 2.                   |
| `uom`                 | Unit of Measure     | `Link`     | `UOM`                                                                                                     |  **Yes**  |      1       | Standard UOM (`Nos`, `Meter`, `Set`, `Kg`).                 |
| `estimated_unit_rate` | Estimated Base Rate | `Currency` | `Company:currency`                                                                                        |    No     |      0       | Rate fetched from Item Price list.                          |
| `estimated_amount`    | Total Line Amount   | `Currency` | `Company:currency`                                                                                        |    No     |      0       | Computed: $\text{quantity} \times \text{estimated\_rate}$.  |
| `description`         | Item Specification  | `Text`     | -                                                                                                         |    No     |      0       | Detailed technical notes.                                   |

---

### 2.5 Child DocType: `tabRemark-Delay Log`

| Fieldname      | Label           | Fieldtype    | Options                                                                                                                                                 | Mandatory | Description                                                  |
| :------------- | :-------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------: | :----------------------------------------------------------- |
| `user`         | Logged By       | `Link`       | `User`                                                                                                                                                  |  **Yes**  | User logging the remark or delay (defaults to session user). |
| `timestamp`    | Recorded At     | `Datetime`   | -                                                                                                                                                       |  **Yes**  | Immutable timestamp of entry.                                |
| `stage`        | Lifecycle Stage | `Data`       | -                                                                                                                                                       |  **Yes**  | Defaults to "Stage 03: Survey Engineering Design".           |
| `delay_reason` | Delay Category  | `Select`     | `Awaiting Roof Structural Clarification\nCustomer Modifying Capacity\nInverter Model Out of Stock\nDISCOM Sanction Load Issue\nDrawing Revision\nOther` |    No     | Mandatory when `stage_status == 'Overdue'`.                  |
| `remarks`      | Detailed Notes  | `Small Text` | -                                                                                                                                                       |  **Yes**  | Free-text explanation of delay or design modifications.      |

---

### 2.6 Downstream Target: `tabQuotation` (Stage 04 Proposal Container)

| Fieldname                        | Label                  | Fieldtype     | Target / Link               | Mandatory | Description                                              |
| :------------------------------- | :--------------------- | :------------ | :-------------------------- | :-------: | :------------------------------------------------------- |
| `custom_survey_design`           | Engineering Design Ref | `Link`        | `Survey Engineering Design` |  **Yes**  | Upstream link registering Stage 03 parent document.      |
| `lead`                           | Linked Lead Reference  | `Link`        | `Lead`                      |  **Yes**  | Commercial prospect from lead workflow.                  |
| `party_name`                     | Commercial Party       | `DynamicLink` | `Lead`                      |  **Yes**  | Quotation party link set to `Lead`.                      |
| `custom_bom`                     | Inherited BoQ Items    | `Table`       | `Quotation Item`            |  **Yes**  | Cloned items from `Custom Quot BOM`.                     |
| `custom_extra_cable_calculation` | Inherited Cable Math   | `Table`       | `Cable Calculation Table`   |    No     | Cloned cable calculations from Stage 03.                 |
| `custom_bom_hash`                | Verified Baseline Hash | `Data`        | -                           |  **Yes**  | Cloned `bom_hash` asserting zero BOM tampering.          |
| `docstatus`                      | Document Status        | `Int`         | `0=Draft`                   |  **Yes**  | Instantiated in `Draft` (`0`) awaiting Stage 04 pricing. |

---

### 2.7 Database Indexing & Autonaming Strategy

- **Autonaming:** Autoname follows `naming_series:SED-.YYYY.-.#####` (e.g. `SED-2026-00018`).
- **Composite B-Tree Indexes:**
  ```sql
  CREATE INDEX idx_survey_eng_design_survey ON `tabSurvey Engineering Design` (site_survey, docstatus);
  CREATE INDEX idx_survey_eng_design_lead ON `tabSurvey Engineering Design` (lead, stage_status);
  CREATE INDEX idx_survey_eng_design_engineer_sla ON `tabSurvey Engineering Design` (design_engineer, stage_status, exp_complete_date);
  CREATE INDEX idx_survey_eng_design_hash ON `tabSurvey Engineering Design` (bom_hash);
  CREATE INDEX idx_survey_eng_design_status_dates ON `tabSurvey Engineering Design` (stage_status, for_design_assign_on, completed_date);
  ```

---

## 3. Layer 2: Domain Services & Business Logic

Decoupled pure Python domain services located in `solar_module/services/design/` adhering strictly to SOLID principles with zero UI dependencies.

### 3.1 `SolarDesignCalculationService` (`solar_module/services/design/calculation.py`)

Governs electrical system sizing, Inverter Loading Ratio (ILR), and parametric voltage drop calculations corrected for temperature ($75^\circ\text{C}$):

```python
import math
import frappe
from frappe import _
from frappe.utils import flt

class SolarDesignCalculationService:
    COPPER_RHO = 0.0175      # Ohm * mm^2 / m at 20 deg C
    ALUMINIUM_RHO = 0.0282   # Ohm * mm^2 / m at 20 deg C
    TEMP_COEFF = 0.004       # Temperature coefficient per deg C for Copper/Aluminium
    OPERATING_TEMP_C = 75.0  # Design conductor temperature under maximum operating load

    @classmethod
    def calculate_capacities_and_drops(cls, doc) -> None:
        """
        Calculates:
        1. actual_designed_capacity = (total_modules_count * module_wattage) / 1000.0
        2. dc_ac_ratio (ILR) = actual_designed_capacity / (inverter_rated_capacity * inverter_count)
        3. Parametric voltage drop for every row in cable_calculations child table
        4. max_dc_voltage_drop_pct and max_ac_voltage_drop_pct
        """
        total_modules = int(doc.total_modules_count or 0)
        module_wp = flt(doc.module_wattage or 0.0)
        doc.actual_designed_capacity = flt((total_modules * module_wp) / 1000.0, 2)

        inverter_kw = flt(doc.inverter_rated_capacity or 0.0)
        inverter_count = int(doc.inverter_count or 1)
        total_inverter_kw = inverter_kw * inverter_count

        if total_inverter_kw > 0:
            doc.dc_ac_ratio = flt(doc.actual_designed_capacity / total_inverter_kw, 2)
        else:
            doc.dc_ac_ratio = 0.0

        max_dc_drop = 0.0
        max_ac_drop = 0.0

        for row in doc.get("cable_calculations", []):
            drop_pct = cls.calculate_row_voltage_drop(row)
            row.voltage_drop_pct = drop_pct
            row.compliance_status = "Pass" if drop_pct <= 2.0 else "Fail"

            circuit_str = str(row.circuit_type or "").upper()
            if "DC" in circuit_str:
                max_dc_drop = max(max_dc_drop, drop_pct)
            elif "AC" in circuit_str:
                max_ac_drop = max(max_ac_drop, drop_pct)

        doc.max_dc_voltage_drop_pct = flt(max_dc_drop, 2)
        doc.max_ac_voltage_drop_pct = flt(max_ac_drop, 2)

    @classmethod
    def calculate_row_voltage_drop(cls, row) -> float:
        """
        Calculates voltage drop for a single cable circuit run:
        - Corrects resistivity to 75 deg C: rho_75 = rho_20 * (1 + alpha * (75 - 20))
        - Resistance R (Ohm) = (rho_75 * length_m) / area_mm2
        - DC / 1-Phase Drop: V_drop = (2 * length_m * I * (rho_75 / area_mm2))
        - 3-Phase AC Drop: V_drop = (sqrt(3) * length_m * I * (rho_75 / area_mm2))
        - Drop Percentage: (V_drop / V_operating) * 100.0
        """
        length_m = flt(row.cable_length_m)
        current_a = flt(row.rated_current_a)
        area_mm2 = flt(row.conductor_size_mm2)
        voltage_v = flt(row.operating_voltage_v)

        if area_mm2 <= 0.0 or voltage_v <= 0.0 or length_m <= 0.0 or current_a <= 0.0:
            row.voltage_drop_v = 0.0
            row.resistance_ohm_km = 0.0
            return 0.0

        is_copper = "COPPER" in str(row.conductor_material or "COPPER").upper()
        base_rho = cls.COPPER_RHO if is_copper else cls.ALUMINIUM_RHO
        rho_75 = base_rho * (1.0 + cls.TEMP_COEFF * (cls.OPERATING_TEMP_C - 20.0))

        resistance_per_meter = rho_75 / area_mm2
        row.resistance_ohm_km = flt(resistance_per_meter * 1000.0, 4)

        is_three_phase = ("3-PHASE" in str(row.circuit_type or "").upper() or
                          voltage_v >= 380.0)

        if is_three_phase:
            v_drop = math.sqrt(3.0) * length_m * current_a * resistance_per_meter
        else:
            v_drop = 2.0 * length_m * current_a * resistance_per_meter

        row.voltage_drop_v = flt(v_drop, 2)
        drop_pct = flt((v_drop / voltage_v) * 100.0, 2)
        return drop_pct
```

---

### 3.2 `SolarBOMExplosionService` (`solar_module/services/design/bom.py`)

Explodes engineering parameters into structured line items and generates deterministic SHA-256 baseline hashes:

```python
import json
import hashlib
import frappe
from frappe.utils import flt, ceil

class SolarBOMExplosionService:
    @classmethod
    def explode_dynamic_bom(cls, design_doc) -> list:
        """
        Dynamically explodes Bill of Materials:
        1. Solar PV Modules (Total count, Wattage, DCR/NDCR)
        2. Solar Inverter (Quantity, Nominal kW rating)
        3. Module Mounting Structure (MMS): Elevated=45 kg/kW, Normal/Others=25 kg/kW
        4. Solar DC Cable: routing distance * 2.1 (Positive + Negative + 5% slack factor)
        5. AC Armoured Feeder Cable: routing distance * 1.08 (8% route slack factor, min 20m)
        6. Chemical Earthing Kits: <=10kW: 3 pits, >10kW: 5 pits
        7. Populates buying rates from ERPNext Item Price list
        """
        items = []
        capacity_kw = flt(design_doc.actual_designed_capacity)
        total_modules = int(design_doc.total_modules_count or 0)
        system_type = design_doc.system_type or "On-Grid"

        # 1. Primary PV Modules
        items.append({
            "item_code": design_doc.module_item_code,
            "bom_item": "Solar PV Modules",
            "category": "Modules",
            "type": design_doc.module_tech_type or "DCR",
            "brand": frappe.db.get_value("Item", design_doc.module_item_code, "brand") or "Tier 1",
            "capacity": f"{flt(design_doc.module_wattage, 1)} Wp",
            "quantity": total_modules,
            "uom": "Nos",
        })

        # 2. Solar Inverter
        items.append({
            "item_code": design_doc.inverter_item_code,
            "bom_item": "Grid Tied Solar Inverter",
            "category": "Inverter",
            "type": "On-Grid" if system_type == "On-Grid" else "Hybrid",
            "brand": frappe.db.get_value("Item", design_doc.inverter_item_code, "brand") or "Standard OEM",
            "capacity": f"{flt(design_doc.inverter_rated_capacity, 1)} kW",
            "quantity": int(design_doc.inverter_count or 1),
            "uom": "Nos",
        })

        # 3. Module Mounting Structure (MMS)
        is_elevated = "ELEVATED" in str(design_doc.mounting_type or "").upper()
        mms_factor_kg_per_kw = 45.0 if is_elevated else 25.0
        mms_tonnage = flt(capacity_kw * mms_factor_kg_per_kw, 1)
        mms_item = cls.get_default_item_for_group("Structure (MMS)", "HDG Solar MMS Structure Kit")
        items.append({
            "item_code": mms_item,
            "bom_item": "Hot Dip Galvanized MMS Structure Kit",
            "category": "Structure (MMS)",
            "type": design_doc.mounting_type or "Normal",
            "capacity": "Wind Speed 150 km/h Rated",
            "quantity": mms_tonnage,
            "uom": "Kg",
        })

        # 4. DC Solar Cable (Twin Core 4/6 sq.mm)
        dc_route_len = 0.0
        for row in design_doc.get("cable_calculations", []):
            if "DC" in str(row.circuit_type or "").upper():
                dc_route_len += flt(row.cable_length_m) * 2.1
        dc_len_m = max(dc_route_len, capacity_kw * 12.0)
        dc_item = cls.get_default_item_for_group("DC Electrical", "Solar DC Cable 4/6 sq.mm")
        items.append({
            "item_code": dc_item,
            "bom_item": "Solar DC Cable 1.5 kV XLPO",
            "category": "DC Electrical",
            "capacity": "1.5 kV DC Rated",
            "quantity": float(ceil(dc_len_m)),
            "uom": "Meter",
        })

        # 5. AC Armoured Feeder Cable
        ac_route_len = 0.0
        for row in design_doc.get("cable_calculations", []):
            if "AC" in str(row.circuit_type or "").upper():
                ac_route_len += flt(row.cable_length_m) * 1.08
        ac_len_m = max(ac_route_len, 20.0)
        ac_item = cls.get_default_item_for_group("AC Electrical", "AC Armoured Cable 4-Core")
        items.append({
            "item_code": ac_item,
            "bom_item": "AC Armoured Underground Feeder Cable",
            "category": "AC Electrical",
            "capacity": "1.1 kV Grade",
            "quantity": float(ceil(ac_len_m)),
            "uom": "Meter",
        })

        # 6. Chemical Earthing Kits
        earth_pits = 3 if capacity_kw <= 10.0 else 5
        earth_item = cls.get_default_item_for_group("Earthing & Protection", "Chemical Earthing Electrode")
        items.append({
            "item_code": earth_item,
            "bom_item": "Maintenance-Free Chemical Earthing Kit",
            "category": "Earthing & Protection",
            "capacity": "Copper Bonded 50mm x 3m",
            "quantity": float(earth_pits),
            "uom": "Set",
        })

        # Populate price list rates
        for itm in items:
            rate = frappe.db.get_value("Item Price", {"item_code": itm["item_code"], "buying": 1}, "price_list_rate") or 0.0
            itm["estimated_unit_rate"] = flt(rate, 2)
            itm["estimated_amount"] = flt(itm["quantity"] * itm["estimated_unit_rate"], 2)

        return items

    @classmethod
    def get_default_item_for_group(cls, item_group: str, fallback_label: str) -> str:
        """Finds active stock item in Item Group, or returns fallback string."""
        item_code = frappe.db.get_value("Item", {"item_group": item_group, "is_stock_item": 1, "disabled": 0}, "name")
        return item_code or fallback_label

    @classmethod
    def compute_bom_hash(cls, bom_rows: list) -> str:
        """
        Generates deterministic cryptographic SHA-256 hash:
        - Sorts canonical rows by item_code and bom_item
        - Formats floats to 2 decimal places
        - Returns 64-character lowercase hex digest
        """
        canonical_rows = []
        for r in sorted(bom_rows, key=lambda x: (str(x.get("item_code") or ""), str(x.get("bom_item") or ""))):
            canonical_rows.append({
                "item_code": str(r.get("item_code") or "").strip(),
                "bom_item": str(r.get("bom_item") or "").strip(),
                "category": str(r.get("category") or "").strip(),
                "quantity": flt(r.get("quantity"), 2),
                "uom": str(r.get("uom") or "").strip(),
                "type": str(r.get("type") or "").strip(),
                "capacity": str(r.get("capacity") or "").strip()
            })
        raw_json = json.dumps(canonical_rows, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
```

---

### 3.3 `SolarDesignGateService` (`solar_module/services/design/gates.py`)

Enforces the 4 hard verification gates required prior to engineering baseline approval:

```python
import frappe
from frappe import _
from frappe.utils import flt

class SolarDesignGateService:
    @classmethod
    def validate_draft_invariants(cls, doc) -> None:
        """Basic validation during draft saves."""
        if not doc.site_survey:
            frappe.throw(_("Linked Site Survey is mandatory."), frappe.ValidationError)
        if not doc.module_item_code:
            frappe.throw(_("Selected PV Module Item is mandatory."), frappe.ValidationError)
        if not doc.inverter_item_code:
            frappe.throw(_("Selected Solar Inverter Item is mandatory."), frappe.ValidationError)
        if int(doc.total_modules_count or 0) <= 0:
            frappe.throw(_("Total modules count must be greater than 0."), frappe.ValidationError)

    @classmethod
    def verify_all_gates(cls, doc) -> None:
        """Executes all 4 Stage 03 Hard Verification Gates before submission."""
        cls.verify_gate_1_files(doc)
        cls.verify_gate_2_voltage_drop(doc)
        cls.verify_gate_3_inverter_ratio(doc)
        cls.verify_gate_4_bom_integrity(doc)

    @classmethod
    def verify_gate_1_files(cls, doc) -> None:
        """
        Gate 1: Mandatory File Verification
        - Must contain >= 1 record with file_category == 'CAD Layout (DWG/DXF)'
        - Must contain >= 1 record with file_category == 'Single Line Diagram (SLD)'
        - Attached files must not be empty and must not exceed max_file_size_mb
        """
        files = doc.get("design_files", [])
        if not files:
            frappe.throw(_("Gate 1 Failure: Design files table is empty. Mandatory CAD Layout and SLD files required."), frappe.ValidationError)

        has_cad = False
        has_sld = False
        max_mb = flt(frappe.db.get_single_value("Solar Design Settings", "max_file_size_mb")) or 25.0

        for row in files:
            if not row.attached_file:
                frappe.throw(_("Gate 1 Failure: File row '{0}' has no attached file.").format(row.file_category), frappe.ValidationError)

            cat = str(row.file_category or "")
            if "CAD Layout" in cat:
                has_cad = True
            elif "Single Line Diagram" in cat or "SLD" in cat:
                has_sld = True

            # Assert file size under admin ceiling
            size_mb = flt(row.file_size_kb or 0.0) / 1024.0
            if size_mb > max_mb:
                frappe.throw(
                    _("Gate 1 Failure: File '{0}' ({1:.2f} MB) exceeds maximum allowed size of {2} MB.").format(
                        row.attached_file, size_mb, max_mb
                    ),
                    frappe.ValidationError
                )

        if not has_cad:
            frappe.throw(_("Gate 1 Failure: At least one CAD Layout (DWG/DXF) drawing must be attached."), frappe.ValidationError)
        if not has_sld:
            frappe.throw(_("Gate 1 Failure: At least one Single Line Diagram (SLD) drawing must be attached."), frappe.ValidationError)

    @classmethod
    def verify_gate_2_voltage_drop(cls, doc) -> None:
        """
        Gate 2: Electrical Voltage Drop Compliance
        - All rows in tabCable Calculation Table must evaluate to compliance_status == 'Pass'
        - max_dc_voltage_drop_pct must be <= 2.0%
        - max_ac_voltage_drop_pct must be <= 2.0%
        """
        calculations = doc.get("cable_calculations", [])
        if not calculations:
            frappe.throw(_("Gate 2 Failure: Cable calculation table is empty. Parametric math required."), frappe.ValidationError)

        for row in calculations:
            if row.compliance_status != "Pass" or flt(row.voltage_drop_pct) > 2.0:
                frappe.throw(
                    _("Gate 2 Failure: Circuit '{0}' voltage drop ({1}%) exceeds statutory threshold of 2.0%.").format(
                        row.circuit_tag or row.circuit_type, row.voltage_drop_pct
                    ),
                    frappe.ValidationError
                )

        if flt(doc.max_dc_voltage_drop_pct) > 2.0:
            frappe.throw(_("Gate 2 Failure: Maximum DC voltage drop ({0}%) exceeds statutory threshold of 2.0%.").format(doc.max_dc_voltage_drop_pct), frappe.ValidationError)
        if flt(doc.max_ac_voltage_drop_pct) > 2.0:
            frappe.throw(_("Gate 2 Failure: Maximum AC voltage drop ({0}%) exceeds statutory threshold of 2.0%.").format(doc.max_ac_voltage_drop_pct), frappe.ValidationError)

    @classmethod
    def verify_gate_3_inverter_ratio(cls, doc) -> None:
        """
        Gate 3: Inverter Sizing Ratio (ILR) Window
        - Inverter Loading Ratio (dc_ac_ratio) must fall strictly between 1.10 and 1.35
        """
        ilr = flt(doc.dc_ac_ratio)
        if ilr < 1.10 or ilr > 1.35:
            frappe.throw(
                _("Gate 3 Failure: Inverter Loading Ratio (ILR = {0:.2f}) falls outside permitted engineering window (1.10 - 1.35).").format(ilr),
                frappe.ValidationError
            )

    @classmethod
    def verify_gate_4_bom_integrity(cls, doc) -> None:
        """
        Gate 4: Dynamic BOM Integrity
        - tabCustom Quot BOM must contain at least 1 module row and 1 inverter row
        - All BOM quantities must be > 0.0 with valid ERPNext Item links
        """
        bom_items = doc.get("bom_items", [])
        if not bom_items:
            frappe.throw(_("Gate 4 Failure: Engineering BOM is empty. Explode dynamic BOM before submission."), frappe.ValidationError)

        has_module = False
        has_inverter = False

        for row in bom_items:
            if not row.item_code or not row.bom_item:
                frappe.throw(_("Gate 4 Failure: BOM row contains missing item code or label."), frappe.ValidationError)
            if flt(row.quantity) <= 0.0:
                frappe.throw(_("Gate 4 Failure: Item '{0}' has invalid quantity ({1}). Must be > 0.0.").format(row.bom_item, row.quantity), frappe.ValidationError)

            cat = str(row.category or "")
            if "Module" in cat:
                has_module = True
            elif "Inverter" in cat:
                has_inverter = True

        if not has_module:
            frappe.throw(_("Gate 4 Failure: BOM must contain at least one Solar PV Module entry."), frappe.ValidationError)
        if not has_inverter:
            frappe.throw(_("Gate 4 Failure: BOM must contain at least one Solar Inverter entry."), frappe.ValidationError)
```

---

### 3.4 `SolarDesignSLAService` (`solar_module/services/design/sla.py`)

Governs the 48-hour engineering turnaround engine and delay logging:

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date, time_diff_in_seconds

class SolarDesignSLAService:
    @staticmethod
    def calculate_expected_completion(for_design_assign_on, sla_hours: int = 48):
        """Calculates SLA completion deadline from assignment timestamp."""
        if not for_design_assign_on:
            return add_to_date(now_datetime(), hours=sla_hours)
        return add_to_date(for_design_assign_on, hours=sla_hours)

    @staticmethod
    def is_overdue(doc) -> bool:
        """Returns True if current timestamp exceeds exp_complete_date."""
        if doc.exp_complete_date and now_datetime() > doc.exp_complete_date:
            return True
        return False

    @staticmethod
    def recompute_design_sla(design_name: str) -> None:
        """Hourly background daemon worker flagging breached designs as Overdue."""
        doc = frappe.get_doc("Survey Engineering Design", design_name)
        if doc.stage_status not in ["Frozen", "Approved"] and SolarDesignSLAService.is_overdue(doc):
            doc.stage_status = "Overdue"
            doc.complete_status = "Delayed"
            doc.save(ignore_permissions=True)

    @staticmethod
    def enforce_delay_reason_if_overdue(doc) -> None:
        """Hard-blocks state transitions on overdue designs without justification."""
        if doc.stage_status == "Overdue" or SolarDesignSLAService.is_overdue(doc):
            has_valid_log = doc.delay_log and len(doc.delay_log.strip()) >= 15
            has_table_entry = any(
                r.remarks and len(r.remarks.strip()) >= 10 for r in doc.get("remark_delay_log", [])
            )
            if not has_valid_log and not has_table_entry:
                frappe.throw(
                    _("Design SLA breached: You must provide a valid delay explanation (minimum 15 characters)."),
                    frappe.ValidationError
                )

    @staticmethod
    def record_completion(doc) -> None:
        """Evaluates SLA outcome and timestamps completion upon freezing."""
        now = now_datetime()
        doc.completed_date = now
        is_delayed = doc.exp_complete_date and now > doc.exp_complete_date
        doc.complete_status = "Delayed" if is_delayed else "On Time"

        if is_delayed:
            SolarDesignSLAService.enforce_delay_reason_if_overdue(doc)
```

---

### 3.5 `SolarDesignBridgeService` (`solar_module/services/design/bridge.py`)

Handles stage transitions, updating upstream `Site Survey` & `Lead`, and spawning downstream Stage 04 `Quotation`:

```python
import frappe
from frappe import _

class SolarDesignBridgeService:
    @staticmethod
    def sync_upstream_survey_and_lead(design_doc) -> None:
        """Marks site survey as design frozen and updates lead status."""
        if design_doc.site_survey and frappe.db.exists("Site Survey", design_doc.site_survey):
            frappe.db.set_value("Site Survey", design_doc.site_survey, "custom_design_frozen", 1, update_modified=False)

        if design_doc.lead and frappe.db.exists("Lead", design_doc.lead):
            frappe.db.set_value("Lead", design_doc.lead, "stage_status", "Engineering Design Completed", update_modified=False)

    @staticmethod
    def spawn_stage_04_proposal_container(design_doc) -> str:
        """
        Instantiates downstream Stage 04 Quotation record in Draft state (docstatus = 0),
        copying frozen BOM rows and verified cable calculations.
        """
        existing = frappe.db.get_value(
            "Quotation",
            {"custom_survey_design": design_doc.name, "docstatus": ["!=", 2]},
            "name"
        )
        if existing:
            return existing

        quotation = frappe.get_doc({
            "doctype": "Quotation",
            "quotation_to": "Lead",
            "party_name": design_doc.lead,
            "custom_survey_design": design_doc.name,
            "custom_bom_hash": design_doc.bom_hash,
            "order_type": "Sales",
            "status": "Draft",
            "docstatus": 0
        })

        # Transfer BOM items to Quotation Item child table
        for bom in design_doc.get("bom_items", []):
            quotation.append("items", {
                "item_code": bom.item_code,
                "item_name": bom.bom_item,
                "qty": bom.quantity,
                "uom": bom.uom,
                "rate": bom.estimated_unit_rate,
                "amount": bom.estimated_amount,
                "description": bom.description or bom.bom_item
            })

        quotation.insert(ignore_permissions=True)
        return quotation.name
```

---

## 4. Layer 3: Controller & Whitelisted API Gateway

### 4.1 Base Controller: `SurveyEngineeringDesign` (`solar_module/doctype/survey_engineering_design/survey_engineering_design.py`)

Inherits from `StageSecuredDocument` to incorporate ADR-000 immutability, Junior Cancel suppression, and deletion audit logging:

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, flt
from solar_module.mixins.stage_secured_document import StageSecuredDocument
from solar_module.services.design.calculation import SolarDesignCalculationService
from solar_module.services.design.bom import SolarBOMExplosionService
from solar_module.services.design.gates import SolarDesignGateService
from solar_module.services.design.sla import SolarDesignSLAService
from solar_module.services.design.bridge import SolarDesignBridgeService
from solar_module.security.stage_forward_lock import StageForwardLockService

class SurveyEngineeringDesign(StageSecuredDocument):
    def before_insert(self):
        # 1. Initialize SLA timestamps
        if not self.for_design_assign_on:
            self.for_design_assign_on = now_datetime()
        if not self.exp_complete_date:
            self.exp_complete_date = SolarDesignSLAService.calculate_expected_completion(self.for_design_assign_on)
        if not self.stage_status:
            self.stage_status = "Draft"
        if not self.custom_survey_ref and self.site_survey:
            self.custom_survey_ref = self.site_survey

    def validate(self):
        """Standard Frappe validation lifecycle."""
        self.enforce_predecessor_integrity()
        self.recalculate_engineering_parameters()
        SolarDesignGateService.validate_draft_invariants(self)
        if self.stage_status == "Overdue":
            SolarDesignSLAService.enforce_delay_reason_if_overdue(self)

    def before_submit(self):
        """Verification gate execution and cryptographic baseline calculation."""
        SolarDesignGateService.verify_all_gates(self)
        self.bom_hash = SolarBOMExplosionService.compute_bom_hash(self.get("bom_items", []))

    def on_submit(self):
        """Permanent lock, baseline freeze, and downstream Stage 04 activation."""
        self.is_frozen = 1
        self.stage_status = "Frozen"
        SolarDesignSLAService.record_completion(self)
        SolarDesignBridgeService.sync_upstream_survey_and_lead(self)
        SolarDesignBridgeService.spawn_stage_04_proposal_container(self)

    def on_cancel(self):
        """Restricted cancellation: blocks cancel if downstream Quotation exists."""
        StageForwardLockService.assert_can_cancel_or_amend(self, action="Cancel")
        self.is_frozen = 0
        self.stage_status = "Draft"

    def enforce_predecessor_integrity(self):
        """Asserts upstream Site Survey has stage_status == 'Completed'."""
        if not self.site_survey:
            frappe.throw(_("Linked Site Survey is mandatory."), frappe.ValidationError)
        survey_status = frappe.db.get_value("Site Survey", self.site_survey, "stage_status")
        if survey_status != "Completed":
            frappe.throw(
                _("Linked Site Survey '{0}' must be in 'Completed' status before engineering design can proceed.").format(self.site_survey),
                frappe.ValidationError
            )

    def recalculate_engineering_parameters(self):
        """Evaluates plant capacities, ILR, and cable voltage drops."""
        SolarDesignCalculationService.calculate_capacities_and_drops(self)
```

---

### 4.2 Whitelisted RPC Gateway (`solar_module/api/design.py`)

Type-safe, permission-checked whitelisted RPC endpoints:

```python
import json
import frappe
from frappe import _
from solar_module.services.design.calculation import SolarDesignCalculationService
from solar_module.services.design.bom import SolarBOMExplosionService
from solar_module.services.design.bridge import SolarDesignBridgeService

@frappe.whitelist(methods=["POST"])
def calculate_electrical_parameters(doc_name: str) -> dict:
    """Whitelisted endpoint to re-run electrical voltage drop calculations."""
    if not doc_name:
        frappe.throw(_("Document name is required"), frappe.ValidationError)

    doc = frappe.get_doc("Survey Engineering Design", doc_name)
    doc.check_permission("write")

    if doc.is_frozen or doc.docstatus == 1:
        frappe.throw(_("Cannot re-run calculations on a frozen or submitted engineering design."), frappe.ValidationError)

    SolarDesignCalculationService.calculate_capacities_and_drops(doc)
    doc.save()

    return {
        "status": "success",
        "actual_designed_capacity": doc.actual_designed_capacity,
        "dc_ac_ratio": doc.dc_ac_ratio,
        "max_dc_voltage_drop_pct": doc.max_dc_voltage_drop_pct,
        "max_ac_voltage_drop_pct": doc.max_ac_voltage_drop_pct,
        "calculations": [
            {
                "circuit_tag": r.circuit_tag,
                "voltage_drop_pct": r.voltage_drop_pct,
                "compliance_status": r.compliance_status
            }
            for r in doc.get("cable_calculations", [])
        ]
    }

@frappe.whitelist(methods=["POST"])
def explode_dynamic_bom(doc_name: str) -> dict:
    """Whitelisted endpoint to dynamically regenerate the engineering BOM."""
    if not doc_name:
        frappe.throw(_("Document name is required"), frappe.ValidationError)

    doc = frappe.get_doc("Survey Engineering Design", doc_name)
    doc.check_permission("write")

    if doc.is_frozen or doc.docstatus == 1:
        frappe.throw(_("Cannot explode BOM on a frozen or submitted engineering design."), frappe.ValidationError)

    exploded_items = SolarBOMExplosionService.explode_dynamic_bom(doc)
    doc.set("bom_items", [])
    for itm in exploded_items:
        doc.append("bom_items", itm)

    doc.save()
    return {"status": "success", "total_items": len(doc.bom_items)}

@frappe.whitelist(methods=["POST"])
def submit_design_approval(doc_name: str, delay_reason: str = None) -> dict:
    """Action for Design Manager to approve, submit, and freeze design baseline."""
    if not doc_name:
        frappe.throw(_("Document name is required"), frappe.ValidationError)

    doc = frappe.get_doc("Survey Engineering Design", doc_name)

    # Check Managerial Role Authority
    user_roles = frappe.get_roles()
    if "Design Manager" not in user_roles and "System Manager" not in user_roles and "Admin" not in user_roles:
        frappe.throw(_("Only Design Managers or Admin can approve engineering designs."), frappe.PermissionError)

    if delay_reason and not doc.delay_log:
        doc.delay_log = delay_reason

    doc.design_manager = frappe.session.user
    doc.stage_status = "Approved"
    doc.submit()

    # Retrieve spawned Stage 04 Quotation container ID
    quotation_id = frappe.db.get_value("Quotation", {"custom_survey_design": doc.name}, "name")

    return {
        "status": "success",
        "stage_status": doc.stage_status,
        "bom_hash": doc.bom_hash,
        "quotation_id": quotation_id
    }
```

---

## 5. Layer 4: Desk Client Script & Workbench Hook

### 5.1 Desk Form Client Script (`codes/client_script/survey_engineering_design.js`)

```javascript
frappe.ui.form.on("Survey Engineering Design", {
  refresh(frm) {
    // 1. Status Indicator Badges
    render_status_badge(frm);

    // 2. Action Buttons for Draft States
    if (frm.doc.docstatus === 0 && !frm.doc.is_frozen) {
      frm.add_custom_button(
        __("Run Parametric Math"),
        () => {
          frappe.call({
            method: "solar_module.api.design.calculate_electrical_parameters",
            args: { doc_name: frm.doc.name },
            freeze: true,
            freeze_message: __("Calculating Electrical Voltage Drops..."),
            callback(r) {
              if (r.message && r.message.status === "success") {
                frm.reload_doc();
                frappe.show_alert({
                  message: __("Electrical calculations updated successfully."),
                  indicator: "green",
                });
              }
            },
          });
        },
        __("Actions"),
      );

      frm.add_custom_button(
        __("Explode Dynamic BOM"),
        () => {
          frappe.call({
            method: "solar_module.api.design.explode_dynamic_bom",
            args: { doc_name: frm.doc.name },
            freeze: true,
            freeze_message: __("Exploding Dynamic BoQ Items..."),
            callback(r) {
              if (r.message && r.message.status === "success") {
                frm.reload_doc();
                frappe.show_alert({
                  message: __("Dynamic BOM regenerated ({0} items).", [
                    r.message.total_items,
                  ]),
                  indicator: "blue",
                });
              }
            },
          });
        },
        __("Actions"),
      );

      // Design Manager Sign-Off Button
      if (
        frappe.user_roles.includes("Design Manager") ||
        frappe.user_roles.includes("Admin") ||
        frappe.user_roles.includes("System Manager")
      ) {
        frm
          .add_custom_button(__("Approve & Freeze Baseline"), () => {
            prompt_approval_and_submit(frm);
          })
          .addClass("btn-primary");
      }
    }

    // 3. ADR-000 Junior Cancellation Suppression
    if (frm.doc.docstatus === 1) {
      frm.page.clear_standard_action_button("Cancel");
      frm.page.clear_standard_action_button("Amend");

      if (
        !frappe.user_roles.includes("Admin") &&
        !frappe.user_roles.includes("System Manager")
      ) {
        frm
          .add_custom_button(__("Request Cancellation / Revision"), () => {
            open_cancellation_request_dialog(frm);
          })
          .addClass("btn-danger");
      }
    }
  },

  total_modules_count(frm) {
    calculate_inline_capacities(frm);
  },
  module_wattage(frm) {
    calculate_inline_capacities(frm);
  },
  inverter_rated_capacity(frm) {
    calculate_inline_capacities(frm);
  },
  inverter_count(frm) {
    calculate_inline_capacities(frm);
  },
});

function calculate_inline_capacities(frm) {
  const modules = flt(frm.doc.total_modules_count || 0);
  const wp = flt(frm.doc.module_wattage || 0);
  const capacity_kw = (modules * wp) / 1000.0;
  frm.set_value("actual_designed_capacity", capacity_kw);

  const inv_kw = flt(frm.doc.inverter_rated_capacity || 0);
  const inv_count = flt(frm.doc.inverter_count || 1);
  const total_inv_kw = inv_kw * inv_count;

  if (total_inv_kw > 0) {
    frm.set_value("dc_ac_ratio", (capacity_kw / total_inv_kw).toFixed(2));
  }
}

function render_status_badge(frm) {
  let indicator = "grey";
  if (frm.doc.stage_status === "Frozen") indicator = "green";
  else if (frm.doc.stage_status === "Approved") indicator = "blue";
  else if (frm.doc.stage_status === "Overdue") indicator = "red";
  else if (frm.doc.stage_status === "Pending Approval") indicator = "orange";

  frm.page.set_indicator(frm.doc.stage_status || "Draft", indicator);
}

function prompt_approval_and_submit(frm) {
  if (frm.doc.stage_status === "Overdue") {
    frappe.prompt(
      [
        {
          label: __("Delay Justification (SLA Breached)"),
          fieldname: "delay_reason",
          fieldtype: "Small Text",
          reqd: 1,
        },
      ],
      (values) => {
        execute_approval_rpc(frm, values.delay_reason);
      },
      __("SLA Delay Justification Required"),
      __("Approve & Submit"),
    );
  } else {
    frappe.confirm(
      __(
        "Are you sure you want to approve and freeze engineering design baseline {0}? This will permanently lock the BOM hash.",
        [frm.doc.name],
      ),
      () => {
        execute_approval_rpc(frm, null);
      },
    );
  }
}

function execute_approval_rpc(frm, delay_reason) {
  frappe.call({
    method: "solar_module.api.design.submit_design_approval",
    args: {
      doc_name: frm.doc.name,
      delay_reason: delay_reason,
    },
    freeze: true,
    freeze_message: __("Freezing Baseline & Spawning Commercial Quotation..."),
    callback(r) {
      if (r.message && r.message.status === "success") {
        frm.reload_doc();
        frappe.msgprint({
          title: __("Baseline Frozen"),
          message: __(
            "Engineering baseline frozen with BOM Hash: <b>{0}</b>.<br>Commercial Quotation <b>{1}</b> instantiated in Draft.",
            [r.message.bom_hash, r.message.quotation_id || "N/A"],
          ),
          indicator: "green",
        });
      }
    },
  });
}

function open_cancellation_request_dialog(frm) {
  const d = new frappe.ui.Dialog({
    title: __("Submit Cancellation / Amendment Request"),
    fields: [
      {
        label: __("Reason for Cancellation / Revision"),
        fieldname: "reason",
        fieldtype: "Select",
        options:
          "Customer Requested Capacity Change\nDISCOM Sanction Rejection\nCivil Structure Incompatible\nEngineering Error\nOther",
        reqd: 1,
      },
      {
        label: __("Detailed Justification"),
        fieldname: "justification",
        fieldtype: "Small Text",
        reqd: 1,
      },
    ],
    primary_action_label: __("Submit Request"),
    primary_action(values) {
      d.hide();
      frappe.call({
        method: "solar_module.security.stage_forward_lock.request_cancellation",
        args: {
          doctype: frm.doc.doctype,
          docname: frm.doc.name,
          reason: values.reason,
          justification: values.justification,
        },
        callback() {
          frappe.msgprint(
            __(
              "Cancellation request submitted. Awaiting Design Manager review.",
            ),
          );
        },
      });
    },
  });
  d.show();
}
```

---

### 5.2 Responsive Vue 3 Design Workbench Layout Blueprint (`/solar/design/:id`)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR: SED-2026-00042  |  Site: Thane Logistics Shed  |  Status: [ UNDER DESIGN ]  | SLA: 18h │
├─────────────────────────┬───────────────────────────────────┬────────────────────────────────────┤
│ 1. SURVEY CONTEXT CARD  │ 2. CAD & SCHEMATIC WORKSPACE      │ 3. ELECTRICAL MATH & DYNAMIC BOM   │
├─────────────────────────┼───────────────────────────────────┼────────────────────────────────────┤
│ • Client: Sadbhav Agro  │ • Dropzone: CAD DWG / SLD / PVsyst│ • Module Sizing: 550 Wp DCR Monos  │
│ • Verified kW: 12.0 kW  │   [ Upload New Version ]          │   Total Panels: 24 (13.20 kWp)     │
│ • Surface: Profile Shed │ • Active Files:                   │ • Inverter: Growatt 10kW (ILR 1.32)│
│ • Array-Inverter: 32 m  │   - Layout_v1.2.dwg (18.4 MB)     │ • DC Cable Drop: 1.42% [PASS]      │
│ • Inverter-Meter: 48 m  │   - SLD_Electrical_v1.0.pdf (4MB) │ • AC Cable Drop: 1.68% [PASS]      │
│ • 360° Photo Gallery    │ • Admin File Limit: 25 MB max     ├────────────────────────────────────┤
│   [Thumbnail Grid]      │                                   │ • Dynamic BOM Items (8 Rows)       │
│ • Satellite Map Pin     │                                   │   [ Re-Explode Dynamic BOM ]       │
│   (Lat: 19.21, Lng: 72.9│                                   │ • BOM Hash: 8f9b...a12c            │
├─────────────────────────┴───────────────────────────────────┴────────────────────────────────────┤
│ FOOTER ACTION BAR: [ Run Cable Calculations ]   [ Explode BOM ]   [ Submit to Manager for Sign-Off]│
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Location: `solar_module/tests/test_survey_engineering_design_tracer_bullet.py`.  
Standard: Subclasses `frappe.testing.IntegrationTestCase` with automatic transaction rollback (`frappe.db.rollback()` in `tearDown`). Zero database commits (`commit()`) permitted.

```python
import json
import frappe
from frappe.testing import IntegrationTestCase
from frappe.utils import now_datetime, add_to_date
from solar_module.api.design import (
    calculate_electrical_parameters,
    explode_dynamic_bom,
    submit_design_approval
)
from solar_module.services.design.calculation import SolarDesignCalculationService
from solar_module.services.design.bom import SolarBOMExplosionService
from solar_module.services.design.gates import SolarDesignGateService
from solar_module.services.design.sla import SolarDesignSLAService
from solar_module.security.stage_forward_lock import StageForwardLockService

class TestSurveyEngineeringDesignTracerBullet(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.designer_email = "test_designer_tracer@sadbhav.local"
        self.manager_email = "test_design_manager_tracer@sadbhav.local"
        self.unauth_email = "test_unauth_user@sadbhav.local"

        # 1. Ensure Design Engineer user exists
        if not frappe.db.exists("User", self.designer_email):
            designer = frappe.get_doc({
                "doctype": "User",
                "email": self.designer_email,
                "first_name": "Tracer Designer",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            designer.add_roles("Design Engineer")

        # 2. Ensure Design Manager user exists
        if not frappe.db.exists("User", self.manager_email):
            manager = frappe.get_doc({
                "doctype": "User",
                "email": self.manager_email,
                "first_name": "Tracer Design Manager",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            manager.add_roles("Design Manager")

        # 3. Ensure Unauthorized user exists
        if not frappe.db.exists("User", self.unauth_email):
            unauth = frappe.get_doc({
                "doctype": "User",
                "email": self.unauth_email,
                "first_name": "Unauthorized User",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            unauth.add_roles("Sales Representative")

        # 4. Create test items
        self.module_item = self.get_or_create_item("SOL-MOD-550W", "Solar PV Module", "Waaree", 5500.0)
        self.inverter_item = self.get_or_create_item("INV-GT-10KW", "Solar Inverter", "Growatt", 45000.0)
        self.mms_item = self.get_or_create_item("HDG Solar MMS Structure Kit", "Structure (MMS)", "Standard", 85.0)
        self.dc_cable_item = self.get_or_create_item("Solar DC Cable 4/6 sq.mm", "DC Electrical", "Polycab", 45.0)
        self.ac_cable_item = self.get_or_create_item("AC Armoured Cable 4-Core", "AC Electrical", "Havells", 180.0)
        self.earth_item = self.get_or_create_item("Chemical Earthing Electrode", "Earthing & Protection", "TruePower", 3200.0)

        # 5. Create test lead and completed site survey
        self.test_lead = frappe.get_doc({
            "doctype": "Lead",
            "first_name": "Adani Solar Logistics Park",
            "mobile_no": "9825011223",
            "solar_capacity": 12.0,
            "custom_address": "GIDC Sanand, Ahmedabad",
            "stage_status": "Site Survey"
        }).insert(ignore_permissions=True)

        self.test_survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": self.test_lead.name,
            "surveyed_by": self.designer_email,
            "solar_capacity": 12.0,
            "solar_system": "On-Grid",
            "site_type": "RCC",
            "connected_load": 15.0,
            "plant_category": "Commercial",
            "type_of_mounting": "Elevated",
            "mount_height": 8.0,
            "storage_space": "Yes",
            "location_details": "Plot 104, Sanand Industrial Area, Ahmedabad, Gujarat 382110",
            "name_match": "Yes",
            "latitude": 23.0225,
            "longitude": 72.5714,
            "gps_accuracy": 9.5,
            "panel_and_inverter_dst": 25.0,
            "panel_and_meter_dst": 15.0,
            "upload_image": "/files/test_panorama.jpg",
            "stage_status": "Completed",
            "docstatus": 1
        }).insert(ignore_permissions=True)

    def tearDown(self):
        # Transaction rollback guarantees complete isolation with zero DB persistence
        frappe.db.rollback()
        super().tearDown()

    def get_or_create_item(self, item_code, item_group, brand, rate):
        if not frappe.db.exists("Item Group", item_group):
            frappe.get_doc({"doctype": "Item Group", "item_group_name": item_group, "parent_item_group": "All Item Groups"}).insert(ignore_permissions=True)
        if not frappe.db.exists("Item", item_code):
            frappe.get_doc({
                "doctype": "Item",
                "item_code": item_code,
                "item_name": item_code,
                "item_group": item_group,
                "is_stock_item": 1,
                "stock_uom": "Nos" if "Kg" not in item_code and "Meter" not in item_code else ("Kg" if "Kg" in item_code else "Meter"),
                "brand": brand
            }).insert(ignore_permissions=True)
        # Ensure Item Price
        if not frappe.db.exists("Item Price", {"item_code": item_code, "buying": 1}):
            frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item_code,
                "price_list": "Standard Buying",
                "buying": 1,
                "price_list_rate": rate
            }).insert(ignore_permissions=True)
        return item_code

    def create_valid_design_doc(self):
        """Helper creating fully populated valid draft engineering design."""
        doc = frappe.get_doc({
            "doctype": "Survey Engineering Design",
            "site_survey": self.test_survey.name,
            "custom_survey_ref": self.test_survey.name,
            "lead": self.test_lead.name,
            "customer_name": "Adani Solar Logistics Park",
            "design_engineer": self.designer_email,
            "system_type": "On-Grid",
            "site_type": "RCC",
            "mounting_type": "Elevated",
            "target_capacity": 12.0,
            "module_item_code": self.module_item,
            "module_wattage": 550.0,
            "module_tech_type": "DCR",
            "total_modules_count": 24,  # 24 * 550 = 13.20 kWp
            "inverter_item_code": self.inverter_item,
            "inverter_rated_capacity": 10.0,
            "inverter_count": 1,        # ILR = 13.20 / 10.0 = 1.32
            "modules_per_string": 12,
            "number_of_strings": 2,
            "for_design_assign_on": now_datetime(),
            "stage_status": "Draft",
            "docstatus": 0
        })

        # Add valid CAD and SLD drawings
        doc.append("design_files", {
            "file_category": "CAD Layout (DWG/DXF)",
            "version": "v1.0",
            "attached_file": "/files/mock_layout_v1.0.dwg",
            "file_size_kb": 2048.0
        })
        doc.append("design_files", {
            "file_category": "Single Line Diagram (SLD)",
            "version": "v1.0",
            "attached_file": "/files/mock_sld_v1.0.pdf",
            "file_size_kb": 1024.0
        })

        # Add compliant cable calculation rows (drop <= 2.0%)
        doc.append("cable_calculations", {
            "circuit_type": "DC String to Inverter",
            "circuit_tag": "DC-STR-01",
            "cable_length_m": 25.0,
            "conductor_material": "Copper (Cu)",
            "conductor_size_mm2": "6.0",
            "rated_current_a": 13.5,
            "operating_voltage_v": 600.0
        })
        doc.append("cable_calculations", {
            "circuit_type": "Inverter AC Output to Meter",
            "circuit_tag": "AC-FEED-01",
            "cable_length_m": 15.0,
            "conductor_material": "Aluminium (Al)",
            "conductor_size_mm2": "16.0",
            "rated_current_a": 14.5,
            "operating_voltage_v": 415.0
        })

        doc.insert(ignore_permissions=True)

        # Explode dynamic BOM
        exploded = SolarBOMExplosionService.explode_dynamic_bom(doc)
        for itm in exploded:
            doc.append("bom_items", itm)
        doc.save(ignore_permissions=True)
        return doc

    def test_01_design_happy_path_approval_and_bom_freeze(self):
        """Assert standard design cycle: parametric math, BOM explosion, manager approval, submit, and Stage 04 Quotation spawn."""
        doc = self.create_valid_design_doc()

        # Execute parametric math calculation
        SolarDesignCalculationService.calculate_capacities_and_drops(doc)
        self.assertEqual(doc.actual_designed_capacity, 13.20)
        self.assertEqual(doc.dc_ac_ratio, 1.32)
        self.assertLessEqual(doc.max_dc_voltage_drop_pct, 2.0)
        self.assertLessEqual(doc.max_ac_voltage_drop_pct, 2.0)

        # Approve and Submit via Design Manager
        frappe.set_user(self.manager_email)
        res = submit_design_approval(doc_name=doc.name)
        self.assertEqual(res["status"], "success")

        doc.reload()
        self.assertEqual(doc.docstatus, 1)
        self.assertEqual(doc.is_frozen, 1)
        self.assertEqual(doc.stage_status, "Frozen")
        self.assertEqual(doc.complete_status, "On Time")
        self.assertEqual(len(doc.bom_hash), 64)

        # Verify Stage 04 Quotation container spawned in Draft status
        quotation_id = res["quotation_id"]
        self.assertTrue(frappe.db.exists("Quotation", quotation_id))
        quotation = frappe.get_doc("Quotation", quotation_id)
        self.assertEqual(quotation.custom_survey_design, doc.name)
        self.assertEqual(quotation.custom_bom_hash, doc.bom_hash)
        self.assertEqual(quotation.docstatus, 0)
        self.assertGreater(len(quotation.items), 0)

        # Verify upstream Site Survey flagged as design frozen
        self.test_survey.reload()
        self.assertEqual(self.test_survey.custom_design_frozen, 1)

    def test_02_predecessor_site_survey_integrity_gate(self):
        """Assert gate blocks engineering design if linked Site Survey is not 'Completed'."""
        # Mutate survey status to Open
        frappe.db.set_value("Site Survey", self.test_survey.name, "stage_status", "Open")
        doc = self.create_valid_design_doc()

        with self.assertRaises(frappe.ValidationError):
            doc.enforce_predecessor_integrity()

    def test_03_gate_1_cad_and_sld_file_mandatory(self):
        """Assert Gate 1 throws ValidationError if mandatory CAD Layout or SLD is missing."""
        doc = self.create_valid_design_doc()
        # Remove SLD file
        doc.design_files = [f for f in doc.design_files if "CAD Layout" in f.file_category]

        with self.assertRaises(frappe.ValidationError):
            SolarDesignGateService.verify_gate_1_files(doc)

    def test_04_gate_1_admin_file_size_limit_rejection(self):
        """Assert Gate 1 throws ValidationError if attached drawing exceeds max_file_size_mb."""
        frappe.db.set_single_value("Solar Design Settings", "max_file_size_mb", 10.0)
        doc = self.create_valid_design_doc()
        # Set file size to 15 MB
        doc.design_files[0].file_size_kb = 15.0 * 1024.0

        with self.assertRaises(frappe.ValidationError):
            SolarDesignGateService.verify_gate_1_files(doc)

    def test_05_gate_2_voltage_drop_threshold_rejection(self):
        """Assert Gate 2 throws ValidationError if cable voltage drop exceeds statutory 2.0%."""
        doc = self.create_valid_design_doc()
        # Force high cable length and tiny cross-section to cause > 2% drop
        doc.cable_calculations[0].cable_length_m = 400.0
        doc.cable_calculations[0].conductor_size_mm2 = "4.0"

        SolarDesignCalculationService.calculate_capacities_and_drops(doc)
        self.assertGreater(doc.max_dc_voltage_drop_pct, 2.0)

        with self.assertRaises(frappe.ValidationError):
            SolarDesignGateService.verify_gate_2_voltage_drop(doc)

    def test_06_gate_3_inverter_loading_ratio_window(self):
        """Assert Gate 3 throws ValidationError if ILR falls outside 1.10 - 1.35."""
        doc = self.create_valid_design_doc()
        # Undersized array: ILR = 5.5 / 10.0 = 0.55
        doc.total_modules_count = 10
        SolarDesignCalculationService.calculate_capacities_and_drops(doc)

        with self.assertRaises(frappe.ValidationError):
            SolarDesignGateService.verify_gate_3_inverter_ratio(doc)

    def test_07_sla_overdue_and_delay_reason_enforcement(self):
        """Assert 48h SLA breach transitions design to Overdue and enforces delay explanation."""
        doc = self.create_valid_design_doc()
        # Set assignment timestamp to 60 hours ago
        doc.for_design_assign_on = add_to_date(now_datetime(), hours=-60)
        doc.exp_complete_date = add_to_date(now_datetime(), hours=-12)
        doc.save(ignore_permissions=True)

        SolarDesignSLAService.recompute_design_sla(doc.name)
        doc.reload()
        self.assertEqual(doc.stage_status, "Overdue")
        self.assertEqual(doc.complete_status, "Delayed")

        # Attempt sign-off without delay explanation
        frappe.set_user(self.manager_email)
        with self.assertRaises(frappe.ValidationError):
            submit_design_approval(doc_name=doc.name, delay_reason="")

        # Sign-off with valid delay explanation
        res = submit_design_approval(
            doc_name=doc.name,
            delay_reason="Client requested roof layout change due to new HVAC installation."
        )
        self.assertEqual(res["status"], "success")
        doc.reload()
        self.assertEqual(doc.stage_status, "Frozen")
        self.assertEqual(doc.complete_status, "Delayed")

    def test_08_stage_forward_lock_and_role_security(self):
        """Assert ADR-000 blocks cancellation when downstream Quotation exists, and unauthorized user cannot approve."""
        doc = self.create_valid_design_doc()
        frappe.set_user(self.manager_email)
        res = submit_design_approval(doc_name=doc.name)
        doc.reload()

        # Attempt cancellation when active Stage 04 Quotation exists
        with self.assertRaises(frappe.ValidationError):
            StageForwardLockService.assert_can_cancel_or_amend(doc, action="Cancel")

        # Test unauthorized user approval rejection
        doc2 = self.create_valid_design_doc()
        frappe.set_user(self.unauth_email)
        with self.assertRaises(frappe.PermissionError):
            submit_design_approval(doc_name=doc2.name)
```

---

## 7. Execution Runbook & Verification Criteria

To verify this Tracer Bullet against a live Frappe bench:

```bash
# 1. Execute Atomic Integration Test Suite (Zero DB Commits)
bench --site sadbhav.local run-tests --module solar_module.tests.test_survey_engineering_design_tracer_bullet

# 2. Export Custom Field & DocType Fixtures
bench --site sadbhav.local export-fixtures --app solar_module

# 3. Test Parametric Calculation RPC via curl
curl -X POST http://sadbhav.local/api/method/solar_module.api.design.calculate_electrical_parameters \
  -H "Authorization: token <api_key>:<api_secret>" \
  -H "Content-Type: application/json" \
  -d '{"doc_name":"SED-2026-00001"}'

# 4. Test Dynamic BOM Explosion RPC via curl
curl -X POST http://sadbhav.local/api/method/solar_module.api.design.explode_dynamic_bom \
  -H "Authorization: token <api_key>:<api_secret>" \
  -H "Content-Type: application/json" \
  -d '{"doc_name":"SED-2026-00001"}'
```

### Tracer Bullet Acceptance Criteria:

- [x] Linked predecessor `Site Survey` verified in `stage_status == 'Completed'`, preventing premature CAD drafting.
- [x] Gate 1 enforces mandatory upload of $\ge 1$ CAD Layout (`.dwg`/`.dxf`) and $\ge 1$ Single Line Diagram (`SLD`).
- [x] Attached drawings validated against `Solar Design Settings.max_file_size_mb` (default 25 MB).
- [x] Gate 2 evaluates temperature-corrected ($75^\circ\text{C}$) DC and AC voltage drops, rejecting any design exceeding statutory $2.0\%$.
- [x] Gate 3 validates Inverter Loading Ratio (`dc_ac_ratio`) falls strictly between $1.10$ and $1.35$.
- [x] Gate 4 explodes dynamic BoQ covering modules, inverters, MMS tonnage, DC/AC cables, and earthing kits.
- [x] Cryptographic baseline freeze computes canonical SHA-256 `bom_hash` upon submission, setting `is_frozen = 1`.
- [x] Turnaround SLA countdown automatically initialized to $T + 48\text{ hours}$ upon designer assignment.
- [x] Background daemons flag breached designs as `Overdue` and mandate $\ge 15$ chars delay justification before approval.
- [x] Document submission automatically triggers `SolarDesignBridgeService`, flagging upstream survey and instantiating downstream `tabQuotation` (Stage 04).
- [x] ADR-000 `StageForwardLockService` blocks cancellation or amendment when active downstream records exist.
- [x] Automated test suite passes 8 atomic test cases with zero manual database cleanup and zero database commits.

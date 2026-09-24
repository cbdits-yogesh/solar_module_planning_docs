# ADR-003: Survey Engineering Design & Dynamic BOM Explosion Architecture

## Status

Accepted

## Date

2026-09-23

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), Stage 03 transitions field-audited site data from Stage 02 (**Technical Site Survey & Audit**) into an engineering design package and an exploded Bill of Quantities (BoQ/BOM).

The legacy implementation suffered from three fundamental structural problems:

1. **Coupled Data Boundaries:** Design files, cable estimates, and provisional BOM rows were scattered across tabs in `Site Survey` and standard `Quotation`. This blurred persona boundaries between field surveyors (`Survey Engineer`) and design specialists (`Design Engineer`), allowing post-survey notes to inadvertently mutate engineering calculations.
2. **Static & Unverified BOM Sizing:** Pre-sales quotations relied on static rules of thumb or manual BoQ entry. Because DC cable runs, earthing pits, and MMS tonnage vary wildly based on roof type (RCC vs. Profile Sheet) and surveyed distances (`panel_and_inverter_dst`, `panel_and_meter_dst`), off-contract material shortages frequently emerged during site installation (Stage 08), eroding project margins by 8–15%.
3. **Lack of Immutable Baseline Freezing:** When a customer agreed to a quotation, no cryptographic mechanism prevented engineering items from being quietly altered in the database before material dispatch (Stage 07) or surplus reconciliation (Stage 09).

We required an enterprise architecture standard to govern:

- The relational entity structure for engineering design.
- The BOM representation for pre-sales estimation vs. downstream manufacturing/procurement.
- The electrical sizing calculation layer.
- The governance and role authority structure.

---

## Decision

We have established the following architectural standards for Stage 03:

### 1. Dedicated Submittable DocType: `tabSurvey Engineering Design`

Stage 03 is isolated into a standalone submittable DocType (`tabSurvey Engineering Design`) linked to `Site Survey`.

- **Ownership Separation:** Authored by `Design Engineer`, reviewed and submitted by `Design Manager`.
- **Immutability via `docstatus: 1`:** Upon manager approval and submission, the document state transitions to `Approved` and `Frozen`, locking all calculation parameters, CAD attachments, and BOM lines.
- **Traceability:** Creates an independent audit trail with its own naming series (`SED-.YYYY.-.#####`), SLA countdown timer, and revision management (`Revision Requested`).

### 2. Pure Domain Service Layer (SOLID Architecture)

In accordance with [`architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md`](../../architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md), all mathematical sizing and BoQ logic are decoupled from the DocType controller into pure Python domain services:

- **`SolarDesignCalculationService`:** Encapsulates electrical engineering math (string sizing within inverter MPPT voltage windows, DC voltage drop, and AC 3-phase/1-phase voltage drop corrected for $75^\circ\text{C}$ conductor temperature). Enforces a hard gate: maximum voltage drop must be $\le 2.0\%$.
- **`SolarBOMExplosionService`:** Programmatically explodes the dynamic Bill of Quantities into child table `Custom Quot BOM` using surveyed capacity, mounting structure type, and calculated cable lengths.
- **`SolarDesignGateService`:** Evaluates non-bypassable server-side verification gates (Mandatory CAD/SLD attachments, voltage drop threshold, and Inverter Loading Ratio $1.10 \le \text{ILR} \le 1.35$).
- **`SolarDesignSLAService`:** Manages the 24h–48h SLA countdown, overdue escalation, and mandatory `tabRemark-Delay Log` recording.

### 3. Lightweight `Custom Quot BOM` with Cryptographic Baseline Hashing

Rather than forcing heavy multi-level ERPNext manufacturing BOMs during pre-sales, we standardize on `Custom Quot BOM` (`tabCustom Quot BOM`):

- Provides rapid, flexible BoQ explosion customized to site geometry.
- Upon submission, `SolarBOMExplosionService.compute_bom_hash()` generates a canonical SHA-256 checksum (`bom_hash`) of all item codes, descriptions, quantities, and ratings.
- This cryptographic hash is propagated to Stage 04 (`Quotation`), Stage 06 (`Sales Order`), and Stage 07 (`Delivery Note`), guaranteeing instantaneous tamper detection if lines are modified out-of-band.

### 4. Admin-Configurable File Upload Threshold (Default 25 MB)

CAD drawings (.dwg, .dxf) and PVsyst yield reports can be large. Rather than hardcoding upload ceilings in code, the threshold is governed by `tabSolar Design Settings` (`max_file_size_mb`, default 25.0 MB). The controller validates attached file sizes against this setting dynamically, preventing disk exhaustion while allowing the `Admin` to scale limits for industrial MW projects.

### 5. Role Hierarchy & Nomenclature Enforcement

In strict compliance with the Zero "User" Suffix Rule:

- **`Design Engineer`:** Primary engineering author.
- **`Design Manager`:** Approval authority with exclusive right to submit and freeze the design baseline.
- **`Admin` (Project Supreme Command):** Project-level operational governance (manages `Solar SLA Settings` and `Solar Design Settings`). Restricted from source code and DocType builders.
- **`System Manager` (Framework Supreme / Developer Apex):** Technical DevOps and bench administration.

---

## Alternatives Considered

### 1. ERPNext Standard `BOM` (`tabBOM`) for Pre-Sales Sizing

- **Pros:** Native out-of-the-box entity in ERPNext; integrates directly with Work Orders.
- **Cons:** Standard ERPNext `BOM` is built for repetitive discrete manufacturing with rigid operations and workstations. Solar EPC rooftop installations represent unique engineered-to-order projects where no two BoQs share identical cable lengths or clamp counts. Creating dozens of transient manufacturing BOMs during pre-sales leads to severe database bloat and operational friction.
- **Rejected:** Keep `Custom Quot BOM` for dynamic pre-sales estimation; bridge into standard ERPNext `BOM` only at Stage 06 (`Sales Order` inception) when procurement and manufacturing work orders are triggered.

### 2. Embedding Design as a Tab in `Site Survey`

- **Pros:** Fewer DocTypes in the database; single document to view.
- **Cons:** Violates the Single Responsibility Principle. Field auditors and CAD design specialists have different permissions, SLA clocks, and lifecycles. A combined document prevents submittable baseline locking without locking the survey or requiring complex custom workflow scripts.
- **Rejected:** Dedicated submittable DocType `Survey Engineering Design` cleanly decouples field auditing from office engineering.

### 3. Client-Side JavaScript Calculations without Server Verification

- **Pros:** Fast interactive UI feedback in the Vue 3 frontend.
- **Cons:** Zero security guarantee. Users could bypass cable drop restrictions or inflate component quantities using browser developer tools or raw REST calls.
- **Rejected:** The Vue 3 SPA calls whitelisted endpoints (`solar_module.api.design.*`) that execute calculations through the server-side domain service, guaranteeing mathematical integrity.

---

## Consequences

### Positive

- **Guaranteed Margin Protection:** Accurate parametric cable math and dynamic MMS sizing eliminate unbudgeted site purchases at Stage 08.
- **Cryptographic Auditability:** `bom_hash` provides verifiable proof that dispatched materials match approved engineering specifications.
- **Modular Maintainability:** Sizing algorithms reside in pure domain services, making them easy to unit-test without database commits (`IntegrationTestCase`).
- **Clean Upgrade Safety:** Zero core Frappe or ERPNext files are modified. All additions reside cleanly in `solar_module`.

### Negative / Trade-Offs

- Requires an additional DocType (`tabSurvey Engineering Design`) and child tables.
- Downstream stages (`Quotation`, `Sales Order`) must reference both `Site Survey` and `Survey Engineering Design`.
- Design Engineers must be trained on the Vue 3 Design Workbench and CAD upload procedures.

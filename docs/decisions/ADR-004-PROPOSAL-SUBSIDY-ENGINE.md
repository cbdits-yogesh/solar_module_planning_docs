# ADR-004: Proposal & Subsidy Engine Architecture (Quotation Extension)

## Status

Accepted

## Date

2026-09-23

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), Stage 04 (**Proposal & Subsidy Engine**) translates technical designs and frozen Bill of Quantities from Stage 03 (`Survey Engineering Design` and `Custom Quot BOM`) into commercial proposals delivered to prospective customers.

In the legacy prototype and standard ERP setups, several architectural ambiguities and operational bottlenecks existed:

1. **Quotation vs. Proposal Nomenclature Collision:** While ERPNext natively calls the commercial estimate `Quotation`, Sadbhav Solar EPC business operations, executive leadership, and customer communications strictly identify this document as **`Proposal`**. Using "Quotation" in user interfaces and forms caused cognitive disconnect and operational confusion.
2. **Singular vs. Repetitive Proposal Needs:** A prospective customer frequently requests multiple commercial alternatives for the same physical property—such as varying capacities (e.g. 5 kW vs. 8 kW vs. 10 kW), different equipment brands (Tier 1 Mono Perc vs. TopCon Bifacial, string inverter vs. micro-inverter), or differing commercial discount structures. The system required a robust mechanism to generate **multiple proposals for the same project/survey**, while guaranteeing that **only one proposal can be finalized**, with non-finalized peer proposals automatically transitioning to superseded or lost status.
3. **Upstream Data Pre-Fill Chain:** There was no automated mechanism to pre-populate proposals with field audit parameters from Stage 02 (`Site Survey`—such as sanctioned connected load, roof type, DISCOM, and address) and technical baseline specifications from Stage 03 (`Survey Engineering Design`—such as designed capacity, inverter model, cable calculations, and frozen BOM).
4. **Rigid Statutory Solar GST Handling:** Indian solar EPC contracts are legally subject to composite supply rules (under Ministry of Finance / CBIC circulars), requiring the total contract value to be split between **Goods** (Solar PV plant equipment) and **Services** (Erection, installation, and commissioning), each with distinct GST rates. The system lacked a flexible engine capable of handling the standard 70:30 ratio while allowing per-proposal adjustments when requested by clients.
5. **Rigid Subsidy Computation:** Calculating PM Surya Ghar: Muft Bijli Yojana Central Financial Assistance (CFA) and state DISCOM subsidies was either done manually or lacked flexibility. Users needed both **pre-defined subsidy scheme selection** and **Admin-configurable subsidy slabs** to adapt to state-level policy updates without code deployment.
6. **Margin Slippage & Lack of Governance:** Sales representatives frequently offered ad-hoc discounts without visibility into procurement costs, eroding project gross margins below corporate sustainability levels.
7. **Advance Verification Ambiguity:** The financial gate required clear business criteria: standard advance collection ($\ge 50\%$) vs. formal finance waiver vs. **Goodwill / VIP customer approval** by executive leadership (CEO/MD/Admin) that bypasses financial clearance.

---

## Decision

We have established the following architectural standards for Stage 04:

### 1. Architectural Strategy: ERPNext `Quotation` Extension with Label Aliasing (Option B)

Rather than inventing an isolated standalone DocType that duplicates ERPNext's extensive selling machinery, Stage 04 extends ERPNext's standard `Quotation` (`tabQuotation`) using custom fields (`custom_*`) and Property Setters:

- **Universal UI Aliasing to "Proposal":** All Desk forms, list views, workspace links, print formats, and Vue 3 / Frappe UI SPA screens label this entity strictly as **`Proposal`**.
- **Leveraging Core Selling Integrations:** Inherits ERPNext's battle-tested multi-currency handling, tax templates, line-item discounts, email communication trails, and seamless downstream conversion to `Sales Order`.
- **Clean Field Segregation:** Solar-specific attributes (`site_survey`, `survey_engineering_design`, `solar_capacity`, `plant_category`, `mount_type`, subsidy calculations, 70:30 GST split, margin governance, and `bom_hash`) are grouped cleanly into dedicated section breaks.

### 2. Multi-Proposal Generation with Exclusive Finalization Lock

To accommodate diverse client preferences, multiple proposals can be generated for the same Lead / Site Survey:

- **Repetitive Creation Allowed:** Frontline `Sales Representative` can generate multiple proposal options for the same site survey (e.g. Option A: 5 kW Residential DCR, Option B: 8 kW Residential NDCR, Option C: Premium Bifacial Package).
- **Exclusive Finalization Gate:** Exactly **one proposal** can transition to `Finalized` (`custom_is_finalized = 1`) upon customer acceptance.
- **Automated Peer Invalidation:** Marking a proposal as `Finalized` automatically transitions all other active, unfinalized proposals for the same site survey to `Superseded`.
- **Customer Drop-Off:** If a prospective customer decides not to proceed, all associated proposals are transitioned to `Lost` / `Rejected` with a mandatory cancellation/lost reason.

### 3. Automated Two-Tier Data Pre-Fill Pipeline

To eliminate manual data re-entry, proposals automatically pre-fill data across both upstream stages:

- **Stage 02 (`Site Survey`):** Ingests client name, site address, latitude/longitude, sanctioned connected electrical load, DISCOM utility board, consumer number, and roof surface classification.
- **Stage 03 (`Survey Engineering Design`):** Ingests designed kWp capacity, module model and count, inverter model and count, parametric cable lengths from `Cable Calculation Table`, and the exploded `Custom Quot BOM` with its cryptographic checksum (`bom_hash`).
- **Template-Driven Alternatives:** When drafting an alternative proposal for a different capacity, the representative can select a `Solar Proposal Template` that automatically generates standard item lines and component costs.

### 4. Configurable Indian Solar EPC Composite GST (70:30 Rule)

In compliance with CBIC tax circulars for turnkey solar contracts:

- **Default 70:30 Bifurcation:** The proposal automatically bifurcates the total project cost into two primary line items:
  1. **Supply of Goods (70%):** Item `Solar Power Plant` attracting concessional GST (12% or 5%).
  2. **Supply of Services (30%):** Item `Installation & Commissioning` attracting standard service GST (18%).
- **Client-Driven Flexibility:** The ratio is governed by `custom_goods_ratio_pct` and `custom_services_ratio_pct`. While defaulting to 70:30, `CRM Representative` or `CRM Manager` can adjust the ratio (e.g. 100:0 for supply-only supply contracts, or custom splits) as mandated by specific client contracts.

### 5. Dual Subsidy Engine: Pre-Defined Schemes & Admin-Configurable Slabs

To handle residential and agricultural subsidy dynamics:

- **Pre-Defined Scheme Selector:** Users can select from standard schemes via `custom_subsidy_scheme` (`PM Surya Ghar Residential`, `PM Surya Ghar GHS/RWA`, `PM KUSUM Component B`, `Surya Gujarat`, `Commercial Non-Subsidy`).
- **Admin-Managed Slabs in `Solar Proposal Settings`:** Both Central Financial Assistance (CFA) brackets and State DISCOM top-ups are maintained in child tables (`Solar Central Subsidy Slab` and `Solar State Subsidy Slab`) managed exclusively by `Admin`. Subsidy amounts are computed deterministically without hardcoded code dependencies.
- **Customer Net Investment & Payback:** The system automatically deducts eligible subsidies from the gross proposal value to display Net Customer Payable, estimated annual generation ($kWh$), annual power bill savings, and simple payback duration in years.

### 6. Admin-Controlled Gross Margin Floor Governance

To protect corporate profitability:

- **Live BOM Cost Aggregation:** Compares total quoted revenue (excluding GST) against the live estimated BOM cost pulled from `Survey Engineering Design`.
- **Gross Margin Formula:** $\text{Gross Margin \%} = \frac{\text{Quoted Amount} - \text{Estimated BOM Cost}}{\text{Quoted Amount}} \times 100\%$.
- **Admin Governance:** The minimum allowable gross margin floor (default 18.0%) is configured by `Admin` in `Solar Proposal Settings`.
- **Approval Gate:** If the calculated margin falls below the floor, the proposal is automatically locked into `Pending Margin Approval`. It cannot be dispatched to the customer or finalized until an `Area Sales Manager` or `Admin` records an explicit digital sign-off (`custom_margin_approved_by` and justification remarks).

### 7. Enforced Advance Verification & Goodwill / VIP Bypass Gate

Before transitioning to Stage 05/06 (`Sales Order` inception):

- **Standard Gate:** Receipt of verified customer advance payment of **$\ge 50\%$** of the net contract value.
- **Finance Officer Waiver:** Advance threshold adjusted or deferred with formal finance approval.
- **Goodwill / VIP Customer Bypass:** For VIP clients, strategic accounts, or government bodies, the **Managing Director / CEO / Admin** can grant a `Goodwill Approval` (`custom_advance_waiver_type = 'Goodwill / VIP Customer Approved'`), completely bypassing financial advance clearance and unlocking immediate downstream project mobilization.

### 8. Prospect Quarantine & Clean Stage 05 Handshake

In strict accordance with ADR-001:

- **Quarantine in `tabLead`:** The prospect remains strictly an inquiry (`tabLead`). No ERPNext `Customer` master is created during proposal creation, revision, or dispatch.
- **Stage 05 Conversion Gate:** Only upon proposal finalization AND verified advance payment (or Goodwill waiver) does Stage 05 programmatically instantiate the formal `Customer` master, addresses, and DISCOM consumer profile.

---

## Alternatives Considered

### 1. Standalone Custom DocType `tabProposal` (Option A)

- **Pros:** Completely isolated schema, zero interference from standard ERPNext quotation fields.
- **Cons:** Disconnects from ERPNext's native selling pipeline, pricing rules, tax rules, and standard print engine; requires building duplicate controllers to convert proposals into `Sales Order` or `Payment Entry`.
- **Rejected:** The user explicitly directed to extend standard `Quotation` with label aliasing (Option B) to maintain compatibility with ERPNext core while tailoring the user experience to Sadbhav Solar EPC operations.

### 2. Hardcoded 70:30 GST Logic in Server Scripts

- **Pros:** Quick to implement for standard rooftop projects.
- **Cons:** Fails for supply-only contracts, government tenders requiring 100% goods invoicing, or regional industrial projects with customized service contracts.
- **Rejected:** Make the goods-to-services ratio configurable per proposal, defaulting to 70:30.

### 3. Enforcing a Single Proposal per Site Survey

- **Pros:** Simpler database state; no need to track sibling proposals.
- **Cons:** Completely detached from real-world solar sales where customers routinely ask for multiple capacity and equipment options before making a purchasing decision.
- **Rejected:** Support multiple proposals per survey with an automated exclusive finalization lock.

---

## Consequences

### Positive

- **Full Commercial Flexibility:** Sales teams can deliver multiple proposal variations (capacities, OEMs, payment terms) to a client without database conflicts.
- **Profitability Safeguard:** Non-bypassable margin floor alerts prevent loss-making proposals from reaching customers without executive sign-off.
- **100% Statutory Tax Compliance:** Clean 70:30 goods/services separation guarantees flawless GST compliance during audits and invoicing.
- **Rapid Turnaround:** Automated pre-fill from Site Survey and Engineering Design reduces proposal generation time from hours to under 15 minutes.
- **Executive Goodwill Governance:** Legitimate VIP and strategic accounts can be fast-tracked via CEO/Admin goodwill approvals without breaking financial controls.

### Negative / Trade-Offs

- **Custom Field Density on `tabQuotation`:** Extends `tabQuotation` with approximately 30 solar-specific fields. Mitigated by clean section grouping and tab breaks.
- **State Synchronization Overhead:** Exclusive finalization requires updating peer proposals in a database transaction to prevent race conditions.

# ADR-013: Supplier Request for Quotation (RFQ) Multi-Vendor Governance & SCM Dispatch Architecture

## Status

Accepted

## Date

2026-09-24

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), **Step 13: Supplier Request for Quotation (RFQ)** (Flow 2: Step 02 of 08) constitutes the critical sourcing gateway bridging internal material requisitions (Step 12: Store Material Requests) with external vendor supply markets. It directly precedes Step 14 (Supplier Quotation Comparative Evaluation Matrix) and Step 15 (Purchase Order Placement).

Under legacy solar EPC procurement practices and generic ERP implementations, the RFQ and vendor quotation initiation process suffered from systemic operational friction, commercial leakage, and governance blindspots:

1. **Maverick Buying & Supplier Favoritism (Informal RFQs):** In legacy operations, purchasing staff solicited quotes through informal, unmonitored channels (phone calls, private WhatsApp messages, personal emails) targeting 1 or 2 favored vendors. This subjective sourcing eliminated market price discovery, resulting in 5–8% commercial premium leakage, lack of procurement transparency, and severe vulnerability to kickbacks or supplier collusion.
2. **Missing Multi-Vendor Bidding Discipline:** Standard systems allowed a single quote to be converted directly into a Purchase Order without enforcing competitive bidding. For high-value solar capital assets—such as Monocrystalline PERC/TOPCon PV Modules, Solar String/Central Inverters, Galvanized Module Mounting Structures (MMS), and Solar DC Cables—procurement lacked a mandatory minimum multi-vendor quota.
3. **Disconnection from Vendor Quality & Historical Performance:** Purchase executives frequently solicited quotations from suppliers with active quality disputes, high historical rejection rates, or chronic on-time delivery (OTD) failures. Sourcing decisions were completely isolated from Step 19 (`Vendor Rating` Scorecard), treating delinquent vendors identically to Tier 1 strategic partners.
4. **Friction in External Vendor Quote Ingestion:** Requiring third-party manufacturers and distributors to create Desk accounts, navigate complex ERP forms, or email unstructured PDF attachments introduced massive data entry bottlenecks. Procurement teams spent days manually transcribing PDF line items into ERP child tables, introducing transcription errors in tax rates, delivery lead times, and freight terms.
5. **Bid Tampering & Early Price Leakage:** In competitive tenders, premature disclosure of one vendor's quotation to a favored competitor distorted fair bidding. Standard ERP systems exposed submitted rates immediately to all purchasing personnel upon entry, lacking a cryptographically secure "Sealed Bid" mechanism.
6. **Absence of Quotation Response Turnaround (SLA) Tracking:** RFQs sat in vendor queues indefinitely without systematic follow-up. Project schedules idled while waiting for equipment pricing, with management blind to vendor turnaround bottlenecks and missing automated countdown reminders.

---

## Decision

We establish an authoritative, comprehensive architectural standard for **Step 13: Supplier Request for Quotation (RFQ)**, extending ERPNext's native `tabRequest for Quotation` (`is_submittable = 1`) and embedding deep governance integrations within `solar_module`:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                STEP 13: SUPPLIER RFQ ARCHITECTURE OVERVIEW                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   [Step 12: Store Material Request Authorized & Released]                                        │
│           │                                                                                      │
│           ▼                                                                                      │
│   [RFQ Inception & Item Aggregation] ──▶ Grouped by Item Group / Project Site                    │
│           │                                                                                      │
│           ▼                                                                                      │
│   [Supplier Recommendation Engine] ◀── Step 19 Scorecard Query (Tier 1 & Approved Vendors)       │
│           │                                                                                      │
│           ├──────────────────────────────────────────────────────────────────────┐               │
│           ▼                                                                      ▼               │
│   [Verification Gate 1: Min 3 Vendors]                            [Verification Gate 2: Specs]   │
│   • Enforces ≥ 3 independent approved suppliers                  • Mandatory technical datasheet │
│   • Single-Source Override requires Purchase Manager sign-off     • Approved brands & lead times │
│           │                                                       • Store vs Site delivery target│
│           │                                                                      │               │
│           └──────────────────────────────────┬───────────────────────────────────┘               │
│                                              ▼                                                   │
│                           [Submit RFQ Document (docstatus = 1)]                                  │
│                           • Generates 256-bit UUID portal tokens per supplier                    │
│                           • Freezes RFQ line items, target dates & quantities                    │
│                           • Initiates 72-Hour Response SLA countdown timer                       │
│                                              │                                                   │
│                                              ▼                                                   │
│                           [Multi-Channel Vendor Broadcast Engine]                                │
│                           • Automated WhatsApp Business API template dispatch                    │
│                           • Transactional Email with one-click magic link                        │
│                                              │                                                   │
│                                              ▼                                                   │
│                           [Passwordless Supplier Portal / Web Submission]                        │
│                           • Endpoint: /solar/rfq-portal/:token                                   │
│                           • Direct capture of rates, freight, GST & lead time                    │
│                           • Sealed Bid Option: rates encrypted until deadline                    │
│                                              │                                                   │
│                                              ▼                                                   │
│                           [Bid Deadline Expiration / SCM Evaluation Gate]                        │
│                           • Automatic 24h & 48h reminder crons                                   │
│                           • Overdue escalation to Purchase Manager if 0 quotes                   │
│                           • Seamless handoff ──▶ Step 14: Quotation Comparison Matrix            │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Standard ERPNext `Request for Quotation` as the Core Procurement Ledger

Rather than creating a divergent standalone procurement entity, Step 13 extends ERPNext's native `tabRequest for Quotation` (`is_submittable = 1`):

- **Core Framework Alignment:** Reuses standard vendor dispatch mechanics, child item structures (`tabRequest for Quotation Item`), and supplier mappings (`tabRequest for Quotation Supplier`).
- **Solar EPC Extension Namespace:** All custom attributes are isolated under the `custom_*` prefix in `solar_module` (e.g. `custom_project_ref`, `custom_material_request_ref`, `custom_bid_deadline`, `custom_is_single_source`, `custom_sealed_bids`, `custom_rfq_stage`).
- **Traceability:** Establishes bidirectional relational links between upstream `tabMaterial Request` records and downstream `tabSupplier Quotation` entries.

### 2. Mandatory Multi-Supplier Bidding Gate ($\ge 3$ Vendors) & Single-Source Exception Protocol

To eradicate maverick buying and enforce competitive bidding:

- **The Rule of Three:** The controller strictly blocks RFQ submission (`docstatus = 1`) unless `len(doc.suppliers) >= 3`.
- **Single-Source Exception Protocol:** If an item is proprietary, sole-sourced, or specialized (e.g. specialized micro-inverters or patented tracker mounting clamps):
  - The flag `custom_is_single_source` must be set to `1`.
  - A mandatory `custom_single_source_justification` (minimum 30 characters) must be entered.
  - The RFQ must be explicitly authorized by `Purchase Manager` or `Admin`. Without this role-level clearance, saving or submitting with $< 3$ vendors throws a `ValidationError`.

### 3. Dynamic Supplier Recommendation & Step 19 Scorecard Tier Integration

Step 13 connects procurement dispatch directly to vendor quality intelligence from Step 19 (`tabVendor Rating`):

- **Tier Filtering (`SupplierShortlistService`):**
  - **Tier 1 (Score $\ge 85\%$):** Automatically prioritized and recommended during vendor selection.
  - **Approved (Score $70 - 84\%$):** Fully eligible for standard RFQ participation.
  - **Probationary (Score $50 - 69\%$):** Restricted to non-critical BOS or small-value tenders ($\le ₹200,000$).
  - **Blacklisted / Suspended (Score $< 50\%$ or `disabled = 1`):** Blocked completely from inclusion. Any attempt to add a blacklisted vendor raises an immediate validation halt.

### 4. Passwordless Supplier Portal & Cryptographic Token Architecture

To eliminate manual transcription bottlenecks and ease supplier response:

- **Token Generation:** Upon RFQ submission, the system generates a unique, cryptographically random 256-bit UUID token (`custom_portal_token`) for each linked supplier in `tabRequest for Quotation Supplier`.
- **Dedicated External Route:** Vendors access a mobile-optimized Vue 3 / Frappe UI portal screen at `/solar/rfq-portal/:token`.
- **Direct Submission:** Vendors input their item unit rates, applicable GST rates (18% vs 12% vs composite), freight charges, guaranteed delivery lead times, and attach their quotation PDF/warranty datasheet.
- **Auto-Instantiation of `Supplier Quotation`:** Submitting the portal form programmatically creates an ERPNext `Supplier Quotation` in `Draft` status, perfectly mapped to the RFQ, completely removing human data entry latency.
- **Token Expiry:** Tokens automatically invalidate once a quote is submitted or when `custom_bid_deadline` expires.

### 5. Anti-Tampering Sealed Bids Governance

To prevent bid tampering, price leakage, and internal corruption:

- **Sealed Bid Toggle (`custom_sealed_bids = 1`):** Applicable to high-value capital equipment ($> ₹1,000,000$).
- **Cryptographic Masking:** When sealed bid mode is active, submitted rates in downstream `Supplier Quotation` records remain encrypted/masked in the database and hidden from `Purchase Assistant` and `Purchase Manager` views until the bid deadline expires.
- **Formal Unsealing Ceremony:** After `custom_bid_deadline` has passed, an authorized `Purchase Manager` or `Admin` triggers the `solar_module.api.procurement.unseal_bids` API, which verifies the deadline, decrypts the line items, and transitions the RFQ to `Responses In Progress` / `Closed for Evaluation`.

### 6. 72-Hour Response SLA, Automated Reminders & Delay Logging

To eliminate procurement lag and maintain tight project delivery schedules:

- **Standard SLA:** All standard RFQs enforce a default **72-hour quotation window** from submission (`custom_sla_deadline = doc.modified + 72 hours`).
- **Automated Reminder Crons (`solar_module.tasks.procurement_sla_daemon`):**
  - **T-24h (24 hours remaining):** Evaluates non-responsive vendors; sends reminder via WhatsApp Business API and Email.
  - **T-8h (8 hours remaining):** Sends high-priority countdown notification to non-responsive vendors.
  - **T-0 (Deadline breached):** If fewer than 2 valid quotes are received, marks RFQ as `Overdue` and alerts `Purchase Manager`.
- **Mandatory Delay Log:** Any extension of `custom_bid_deadline` or transition past SLA mandates a recorded entry in `custom_delay_reason_table` (`tabRemark-Delay Log`), capturing reason category, duration, and managerial sign-off.

### 7. Separation of Roles & Authority Standard

In strict adherence to repository governance:

- **Zero "User" Suffix Rule:** Eliminates deprecated terms (`Purchase User`, `Vendor User`); establishes **`Purchase Assistant`**, **`Purchase Manager`**, **`Store Assistant`**, **`Store Manager`**, and **`Admin`**.
- **Supreme Authority Hierarchy:**
  - `Administrator` & `System Manager`: Technical framework control, source code, doctype builders, Redis queues.
  - `Admin`: Project-level operational supreme command over procurement SLA settings, emergency single-source tender approvals, and executive audit dashboards. Restricted from Python source code and doctype schemas.

---

## Consequences

### Positive Consequences

1. **Procurement Cost Optimization:** Enforced 3-vendor minimum competition and automated RFQ dispatch consistently yields 5–8% gross procurement savings across PV modules, inverters, and BOS.
2. **Zero Manual Transcription Errors:** Direct supplier portal submission automatically populates `Supplier Quotation` line items, tax templates, and lead times with zero clerical intervention.
3. **Audit Trail & Anti-Corruption:** Sealed bids and immutable delay logging prevent bid shopping, favoritism, and post-submission tampering.
4. **Synchronized SCM Pipeline:** Instant linkage from Store Material Requests (`STEP_12`) through RFQ (`STEP_13`) to Quotation Comparison (`STEP_14`) guarantees end-to-end traceability.

### Trade-offs & Mitigations

1. **Trade-off:** Small-volume or proprietary emergency spare parts cannot easily meet the 3-vendor quota.
   - _Mitigation:_ Explicit `custom_is_single_source` override workflow requiring `Purchase Manager` / `Admin` approval with mandatory justification text.
2. **Trade-off:** Some rural or traditional hardware vendors may resist using a digital web portal.
   - _Mitigation:_ Dual submission mode—`Purchase Assistant` retains capability to enter quotations manually on behalf of the supplier via Desk, with an explicit audit flag `entered_by_buyer = 1`.

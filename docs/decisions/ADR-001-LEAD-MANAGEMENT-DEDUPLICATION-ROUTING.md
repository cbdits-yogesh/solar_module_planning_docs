# ADR-001: Lead Ingestion, Sanitization, Deduplication & Survey Dispatch Architecture

## Status

Accepted

## Date

2026-09-23

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), Stage 01 serves as the primary commercial entry gateway of the Solar EPC Project Execution Lifecycle. It receives inquiries across diverse omnichannel sources (PM Surya Ghar national portal, web landing pages, walk-in showrooms, referral networks, and field telecalling).

The legacy implementation suffered from four major operational and structural deficiencies:

1. **Unstandardized Phone Formatting & Sales Collision:** Mobile phone numbers were stored in arbitrary formats (+91, leading 0, embedded hyphens, whitespace), preventing deterministic uniqueness checks. Multiple sales representatives frequently called the same prospective client simultaneously, causing customer friction, commission disputes, and wasted telecalling resources.
2. **Premature Customer Master Inception:** Unqualified inquiries were prematurely instantiated as ERPNext `Customer` and `Address` records upon first intake. This bloated the core accounting ledger and master customer directory with low-intent, non-converting contacts, contaminating receivables aging, customer segmentation, and GST reporting.
3. **Absence of Enforced SLA Clocks & Accountability:** Inbound leads lacked deterministic turnaround time (TAT) tracking. Inquiries regularly lingered in unassigned queues past 48 hours without alerts. When delays occurred, no structured audit log captured why the lead stalled.
4. **Unqualified Field Dispatch:** Field survey engineers were dispatched without capturing preliminary technical feasibility data (sanctioned connected electrical load, electricity tariff class, average monthly power bill, and proposed solar kW capacity), resulting in high on-site rejection rates and wasted field engineering hours.

We required an enterprise architecture standard to govern:

- The ingestion, phone sanitization, and deduplication engine.
- The separation boundary between commercial prospects and accounting customer entities.
- The real-time SLA engine and delay accountability logging.
- The automated technical validation and dispatch bridge to Stage 02 (`Site Survey`).
- The role authority hierarchy and permission governance.

---

## Decision

We have established the following architectural standards for Stage 01:

### 1. 10-Digit Mobile Sanitization & Cross-Table Deduplication Gate

All phone inputs must pass through a strict server-side validation pipeline in `LeadValidationService`:

- **Sanitization:** Strips all non-numeric characters, international prefixes (`+91`), and trunk prefixes (`0`), reducing the input to a raw 10-digit numeric sequence.
- **Regex Enforcement:** Validates against `^[6-9]\d{9}$`. Any invalid or malformed number raises a blocking `frappe.ValidationError`.
- **Cross-Table Deduplication Query:** Queries across `tabLead`, `tabCRM Lead`, `tabCustomer`, and `tabContact`. If an active, non-cancelled record exists with the identical 10-digit mobile number, record creation is blocked with `frappe.DuplicateEntryError` unless an explicit manager override (`duplicate_mobile = 1`) is granted by an `Area Sales Manager` or `Admin`.
- **Indexed Anchor:** The field `mobile_no` on `tabLead` is backed by a composite B-Tree index `(mobile_no, status)` to ensure sub-millisecond deduplication checks at scale.

### 2. Strict Customer Inception Boundary (Quarantine in `tabLead`)

To preserve the integrity of ERPNext core financial and inventory ledgers:

- **Quarantine Principle:** Prospects remain strictly inside `tabLead` throughout Stages 01, 02, 03, and 04. No standard ERPNext `Customer` master is created during lead capture, qualification, site audit, or preliminary quotation.
- **Inception Gate at Stage 05:** The formal ERPNext `Customer` record is instantiated programmatically only at Stage 05 (**Advance Clearance & Customer Master Inception**) upon verified receipt of a minimum 20% project advance payment or confirmed bank loan sanction.
- **Automated Entity Migration:** Upon reaching Stage 05, customer contact details (`mobile_no`, `custom_address`, `custom_pincode`) migrate cleanly into standard `tabCustomer`, `tabAddress`, and `tabContact` entities.

### 3. Two-Tier Enforced SLA Engine & Mandatory Delay Audit Logging

To guarantee swift customer response and eliminate operational bottlenecks:

- **Tier 1 (Initial Contact SLA):** 2-hour response window for frontline sales executives upon lead ingestion during operational hours.
- **Tier 2 (Survey Scheduling SLA):** 24-hour turnaround window to qualify prospects and schedule a site survey.
- **Asynchronous Daemon (`solar_module.tasks.recompute_lead_sla`):** A background worker executing every 15 minutes checks active leads against `sla_due_date = creation_timestamp + SLA_Hours`. If breached, the engine updates `stage_status = 'Overdue'`, sets `complete_status = 'Delayed'`, and dispatches high-priority escalation cards to Raven chat and WhatsApp.
- **Mandatory Delay Reason Gate:** Once marked `Overdue`, any subsequent state transition or update is hard-blocked unless a justified delay reason is appended to `tabRemark-Delay Log` (`delay_reason` enum + detailed remark text).

### 4. Technical Sizing Feasibility Gate & Automated Survey Spawning

Before a lead can transition to status `Qualified` or be scheduled for a field audit:

- **Server-Side Sizing Gate:** Asserts that `solar_capacity > 0.0`, `len(custom_pincode) == 6`, and `custom_address` is populated.
- **Automated Stage 02 Spawning (`SiteSurveyBridgeService`):** Assigning an active `Survey Engineer` automatically updates `lead.stage_status = 'Site Survey'`, stamps `for_survey_assign_on = now_datetime()`, and programmatically creates a linked `Site Survey` document in `Draft` status pre-populated with lead attributes, starting the 24-hour Stage 02 audit clock.

### 5. Decoupled SOLID Domain Service Layer

In accordance with [`architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md`](../../architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md), all business logic is decoupled from `Lead` controllers into specialized domain services:

- **`LeadValidationService`:** Mobile regex parsing, deduplication queries, address and pincode validation.
- **`LeadSLAService`:** Response/scheduling countdowns, overdue daemon evaluation, and delay justification enforcement.
- **`SiteSurveyBridgeService`:** Downstream `Site Survey` instantiation and bidirectional status synchronization.
- **`LeadNotificationService`:** Omnichannel message broadcasting to Raven internal channels and WhatsApp Business API.

### 6. Role Authority Hierarchy & Zero "User" Suffix Enforcement

In compliance with enterprise standards:

- **`Sales Representative`:** Frontline lead ingestion, phone sanitization, preliminary qualification, kW sizing, and survey scheduling.
- **`Sales Manager`:** Territory assignment, duplicate override authorization, SLA escalation oversight, and supervisory management of Sales Representatives.
- **`Admin` (Project Supreme Command):** Supreme operational authority; manages `Solar SLA Settings`, `Solar Notification Settings`, and delay reason overrides. Restricted from source code and DocType builders.
- **`System Manager` (Framework Supreme / Developer Apex):** Technical DevOps, Redis worker configuration, DocType schema builder, and bench administration.

---

## Alternatives Considered

### 1. Immediate ERPNext `Customer` / `Opportunity` Inception on Intake

- **Pros:** Native ERPNext CRM flow; uses out-of-the-box DocTypes without custom boundaries.
- **Cons:** In residential and commercial solar, inquiry-to-order conversion rates hover around 10–25%. Creating `Customer` records on day one floods the ledger with dummy records, breaks standard sales conversion funnel analytics, and creates phantom records in accounting databases.
- **Rejected:** Quarantine prospects in `tabLead` until commercial commitment (Stage 05).

### 2. Relying on Native Frappe Workflow Engine for SLA Management

- **Pros:** Graphical workflow builder in Frappe Desk.
- **Cons:** Native Frappe workflows are purely transition-triggered and lack scheduled background time-decay daemons. They cannot dynamically evaluate SLA countdowns in the background, calculate business hour windows, or enforce delay logs upon overdue submission without brittle custom scripts.
- **Rejected:** Implement a decoupled `LeadSLAService` driven by standard Frappe background scheduler jobs.

### 3. Client-Side Only Phone Number Sanitization

- **Pros:** Instant UI feedback in Vue 3 modals.
- **Cons:** Bypassed completely by REST/RPC API calls, third-party webhooks (PM Surya Ghar), or CSV lead imports, allowing dirty numbers into the database.
- **Rejected:** Client-side formatting provides immediate UX feedback, but server-side validation in `LeadValidationService` acts as an inviolable gate on `before_save` and whitelisted endpoints.

---

## Consequences

### Positive

- **Elimination of Sales Collisions:** Deterministic 10-digit mobile deduplication guarantees no two reps work the same prospect.
- **Clean Accounting Master Data:** Zero phantom customer accounts in ERPNext core ledgers prior to financial clearance.
- **Transparent Accountability:** 2-hour response and 24-hour survey dispatch SLAs with immutable delay audit tracking.
- **Seamless Downstream Handoff:** Automated generation of Stage 02 `Site Survey` container eliminates manual re-entry errors.
- **Upgrade-Safe Architecture:** 100% compliant with standard Frappe hooks and clean app boundaries; zero modifications to core ERPNext files.

### Negative / Trade-Offs

- Requires sales executives to enter complete sizing information (bill amount, capacity, pincode) before survey scheduling.
- Duplicate inquiries for genuine multi-property clients require manager intervention (`duplicate_mobile = 1`).
- Requires maintaining scheduled background worker tasks for 15-minute SLA evaluations.

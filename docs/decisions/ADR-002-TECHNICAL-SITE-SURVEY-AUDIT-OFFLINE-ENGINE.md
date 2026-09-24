# ADR-002: Technical Site Survey & Audit Offline-First PWA Architecture

## Status

Accepted

## Date

2026-09-23

## Context

In the Sadbhav Solar EPC Enterprise ERP platform (`solar_module`), Stage 02 (**Technical Site Survey & Audit**) establishes the engineering foundation of the Solar EPC Project Execution Lifecycle. Triggered upon surveyor assignment in Stage 01 (**Lead Management**), this stage dispatches a field engineer to the customer premises to inspect roof civil structures, electrical connection points, cable routing distances, shadow obstacles, and utility meter attributes within an enforced **24-hour SLA turnaround window**.

Solar EPC field audits take place across diverse and challenging environments: remote agricultural farms (PM KUSUM solar agricultural pumps), rural residential rooftops (PM Surya Ghar), and isolated industrial sheds with zero or highly unstable cellular connectivity.

The legacy audit process suffered from four critical operational failure modes:

1. **Catastrophic Field Data Loss:** Web forms required continuous connectivity. When cellular networks dropped in basements, switchgear rooms, or rural areas, auditors lost 30–45 minutes of detailed measurements, notes, and photos upon page reload.
2. **High Rate of Costly Repeat Site Inspections:** Design engineers frequently rejected survey handoffs days later because field auditors forgot crucial engineering parameters (array-to-inverter distance, busbar ratings, roof parapet height, or mounting clearance). Each repeat site inspection cost ₹1,500–₹3,500 and added 3–5 days of delay.
3. **Missing or Fraudulent Audit Evidence:** Audits lacked verifiable physical evidence. Surveyors occasionally completed checklists from memory without visiting the site, or attached blurred, irrelevant photos that failed DISCOM net-meter inspection requirements at Stage 10.
4. **Premature Client Storage Eviction:** Naive offline caching scripts cleared client storage immediately upon dispatching network requests, causing irrecoverable data loss when server timeouts or proxy dropped connections mid-upload.

We required an enterprise architecture standard to govern:

- The offline-first data persistence and synchronization model.
- The relational schema and mandatory engineering invariants.
- The photographic and video verification checklist pattern.
- Geolocation verification and reverse geocoding.
- The 24-hour SLA engine and delay accountability.
- The role authority hierarchy and permission governance.

---

## Decision

We have established the following architectural standards for Stage 02:

### 1. Dedicated Standalone Audit DocType: `tabSite Survey`

Stage 02 is housed in a standalone custom DocType (`tabSite Survey`) rather than an overloaded child table or sub-form in `Lead`:

- **Decoupled Lifecycle:** Possesses an independent lifecycle state machine (`Open`, `Overdue`, `Completed`), its own autonaming series (`SRV-.YYYY.-.#####`), and an immutable audit trail.
- **10 Mandatory Technical Invariants:** Enforces strict server-side validation ensuring that plant capacity, electrical system configuration (`On-Grid`, `Hybrid`, `Off-Grid`), civil site type, connected load, tariff category, mounting type, elevation height, on-site storage availability, reverse-geocoded address, and utility bill name match are fully captured before completion can occur.

### 2. Offline-First PWA Mobile Architecture with Dexie.js (IndexedDB)

The mobile field auditor interface is built as a touch-optimized Progressive Web Application (PWA) mounted within the universal `/solar` wrapper at `/solar/surveys/:id`:

- **Persistent Client Storage:** Uses **Dexie.js** to manage an IndexedDB database (`SiteSurveyOfflineDB`) storing complete survey records, draft values, high-resolution photo blobs, and 360° video files directly on the field auditor's device.
- **Zero Data Loss Guarantee:** All field interactions are committed to client IndexedDB immediately before any network transmission is attempted. Survives app termination, browser crashes, low-battery shutdowns, and device reboots.

### 3. Resilient Two-Stage Auto-Sync Pipeline with Fail-Safe Cache Eviction

To handle large media uploads over degraded 2G/3G field networks without blocking form sync:

- **Stage A (Chunked Media Transmission):** High-resolution photographs and 360° video walkthroughs are divided into $1.0\text{MB}$ binary chunks and transmitted via `@frappe.whitelist` endpoint `upload_survey_media_chunk`. Each file verifies against a client-generated SHA-256 content checksum.
- **Stage B (Atomic Payload Commit):** Once all media binaries are confirmed, the complete survey document JSON is transmitted via `sync_offline_survey`.
- **Fail-Safe Cache Eviction Protocol:** Client-side IndexedDB records are deleted **only when the server responds with HTTP 200 AND a matching document verification hash**. If the transmission fails or times out, the local cache remains 100% intact, and the background synchronization engine retries with exponential backoff upon network restoration.
- **Idempotency Guarantee:** Every client payload includes an `offline_client_id` (device-generated UUID). The server detects replay attempts and safely acknowledges duplicate sync requests without generating duplicate documents or corrupted attachments.

### 4. Geolocation Integrity Gate & OpenStreetMap Reverse Geocoding

To eliminate fraudulent or off-site audits:

- **GPS Satellite Lock:** Requires hardware GPS coordinates (`latitude`, `longitude`) with a reported horizontal accuracy $\le 50.0\text{m}$ (target $\le 15.0\text{m}$). Rejects zero coordinates (`0.0, 0.0`) and cached/mock location providers.
- **Radius Assertion:** Validates that the recorded coordinates fall within a $50\text{km}$ boundary of the customer's registered site pincode.
- **OpenStreetMap / Nominatim Reverse Geocoding:** Automatically resolves device coordinates into a verified municipal street address stored in `location_details`.

### 5. Fixed 6-Photo Checklist & 360° Panoramic Video Walkthrough

Adhering to **Pattern A (Mandatory Verification Checklist Table)** ([`architect_docs/03_DOCTYPE_SCHEMA_RELATIONAL_DESIGN.md`](../../architect_docs/03_DOCTYPE_SCHEMA_RELATIONAL_DESIGN.md)):

- **Child Table `tabSite Survey Doc Table`:** Contains 6 pre-seeded, fixed photo rows that cannot be deleted or renamed by users:
  1. `Inverter, ACDB and DCDB Location Image`
  2. `Earthing-1 Location Image`
  3. `Earthing-2 Location Image`
  4. `Earthing-3 Location Image`
  5. `LT Panel Location Image`
  6. `Meter Location Image`
- **Mandatory Video Walkthrough:** Requires $\ge 1$ video walkthrough row (`Site Video Walkthrough (360 Panorama)`) with a minimum file size of $1.0\text{MB}$ to capture physical roof obstacles and shading trees.
- **Server Verification Gate:** Hard server-side validation in `SurveyValidationService` halts survey completion if any mandatory row lacks a valid binary link in `tabFile`.

### 6. 24-Hour SLA Turnaround Engine & Escalation Daemons

- **SLA Clock Initiation:** Stamped immediately upon lead assignment (`for_survey_assign_on`), setting deadline `exp_complete_date = for_survey_assign_on + 24 hours`.
- **Background Daemon (`solar_module.tasks.recompute_survey_sla`):** Runs every 15 minutes, identifying active surveys where `NOW() > exp_complete_date`. Transitions status to `Overdue`, sets `complete_status = 'Delayed'`, and dispatches high-priority escalation cards to Raven chat and WhatsApp.
- **Mandatory Delay Logging:** Overdue surveys cannot be completed without recording an explicit delay justification ($\ge 20$ characters in `delay_log` or an audit row in `tabRemark-Delay Log`).

### 7. Decoupled SOLID Domain Service Layer

In accordance with [`architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md`](../../architect_docs/05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md), all survey logic is factored into pure Python domain services:

- **`SurveyValidationService`:** Validates technical invariants, GPS tolerances, and 6-photo checklist integrity.
- **`SurveySLAService`:** Manages 24h SLA timers, overdue state transitions, and delay calculations.
- **`SurveySyncService`:** Ingests chunked media, validates SHA-256 hashes, handles offline payload idempotency, and computes document verification hashes.
- **`SurveyGeolocationService`:** Evaluates GPS tolerances and queries Nominatim reverse geocoding APIs.
- **`SurveyBridgeService`:** Synchronizes completion state back to `tabLead` and auto-spawns the Stage 03 engineering container.

### 8. Role Authority Hierarchy & Zero "User" Suffix Enforcement

- **`Survey Engineer` / `Site Survey Auditor`:** Certified field engineer responsible for on-site audit, GPS locking, photo/video capture, and technical sign-off.
- **`Survey Assistant`:** Field helper assisting with roof tape measurements and cable path tracing.
- **`Area Sales Manager`:** Regional territory oversight, surveyor assignment, and SLA escalation review.
- **`Admin` (Project Supreme Command):** Supreme operational authority; manages `Solar SLA Settings`, `Solar Notification Settings`, and delay reason overrides. Restricted from source code and DocType builders.
- **`System Manager` (Framework Supreme / Developer Apex):** Technical DevOps, Redis queue worker configuration, DocType schema customization, and bench CLI tooling.

---

## Alternatives Considered

### 1. Standard Online Frappe Desk Web Form / Mobile Browser Form

- **Pros:** Standard Frappe framework feature; zero custom frontend code required.
- **Cons:** Utterly unsuited for remote field realities. Requires continuous online connectivity. In intermittent 2G/3G zones, forms fail during submission, file uploads drop silently, and uncommitted field data is lost on mobile browser refresh.
- **Rejected:** Offline-first PWA with IndexedDB is mandatory for field operational reliability.

### 2. Third-Party Standalone Survey Platforms (KoboToolbox, Google Forms, Survey123)

- **Pros:** Mature off-the-shelf mobile survey apps with native offline capabilities.
- **Cons:** Creates an isolated data silo decoupled from the ERPNext core database. Requires fragile third-party webhook integrations, duplicate user master management, external license costs, and lacks deep-link integration with Frappe role-based permissions and Stage 03 CAD design automation.
- **Rejected:** Native Vue 3 PWA mounted directly on `/solar` ensures seamless end-to-end data integrity within `solar_module`.

### 3. Single-Stage Monolithic Sync Payload

- **Pros:** Simpler client implementation; single HTTP request.
- **Cons:** Uploading 10+ high-resolution photos and a 20MB video in a single multipart HTTP POST over spotty rural cellular connections results in high failure and timeout rates ($> 40\%$). A failure on byte $19,999,999$ forces the surveyor to re-upload the entire 20MB package from scratch.
- **Rejected:** Two-stage sync with resumable $1.0\text{MB}$ chunked media uploads guarantees resilience even on unstable 2G/3G cellular links.

---

## Consequences

### Positive

- **100% Offline Resilience:** Field auditors can perform complete rooftop audits in remote zones with zero connectivity without fear of data loss.
- **Zero Redundant Revisits:** Hard validation gates ensure all 10 engineering invariants and 6 photographic evidence rows are captured before the auditor departs the site.
- **Tamper-Proof Geolocation:** Verified device GPS coordinates prevent proxy audits and provide audited proof of site inspection for government DISCOM subsidy filings.
- **Seamless Engineering Handoff:** Survey completion automatically unlocks Stage 03 (`Survey Engineering Design`), pre-populating verified roof and cable distances into CAD sizing algorithms.
- **Clean Architecture:** Zero core code modifications; fully encapsulated in `solar_module`.

### Negative / Trade-Offs

- Requires maintaining client-side IndexedDB schemas (Dexie.js) in the Vue 3 PWA.
- Requires robust background queue sizing in Redis for processing chunked media files.
- Field engineers must carry modern smartphones with functioning GPS hardware and camera modules.

# Phase 7: Software Requirements Specification (SRS)

**Multi-Tier Architecture, Background Lifecycle Daemons, Security & Reliability**  
_Source: Sadbhav Solar EPC Enterprise Architecture Suite_

---

## 1. System Architecture Blueprint

```
+-----------------------------------------------------------------------------------------+
|                                  PRESENTATION TIER                                      |
|            Frappe Desk Interface (Forms/Lists/Reports) + Vue 3 / Frappe UI SPA          |
|   - Flow 1 11-Stage Progress Stepper             - Mobile Touch Survey with 24h SLA     |
|   - Engineering CAD/SLD Design Workbench         - Dynamic Proposal & Subsidy Builder   |
|   - Delivery Note Material Dispatch Modal        - Zone WBS Execution & Mobile DPR Log  |
|   - Post-Install Material Return Screen          - Dual-Timing Liaisoning & Grid Sync   |
|   - Store Material Request & Low Stock Dashboard - Supplier Quotation Comparison Matrix |
|   - Store/Site Barcode GRN Scanner               - Collaborative Vendor Payment Desk    |
|   - Vendor Performance Scorecard                 - Admin SLA & Notification Center      |
+-----------------------------------------------------------------------------------------+
                                             │  HTTPS / REST / WebSocket (Socket.IO)
                                             ▼
+-----------------------------------------------------------------------------------------+
|                                APPLICATION & LOGIC TIER                                 |
|                      Frappe Framework v15/v16+ (Python 3.11/3.12+)                      |
|                                                                                         |
|   [Domain Service Layer]                                                                |
|   - SLAService (Task countdown, overdue transitions, custom SLA config lookup)           |
|   - NotificationEngine (Granular toggle checking, multi-recipient routing, admin feed)  |
|   - QuotationComparisonService (Multi-vendor matrix analysis and ranking)               |
|   - MaterialReconciliationService (Dispatched vs Installed audit, return generation)    |
|   - VendorRatingService (4-factor weighted score calculation upon GRN/PI)               |
|                                                                                         |
|   [Core Lifecycle Controllers & Hooks]                                                  |
|   - LeadPipelineController              - SiteSurveyValidator (24h SLA enforcement)     |
|   - DesignBOMExplosionEngine            - ProposalSubsidyCalculator                     |
|   - AdvanceGate & CustomerInceptionHook - SalesOrderBaselineLock                        |
|   - DeliveryNoteDispatchController      - ZoneExecution & DPRController                 |
|   - LiaisoningSync & ProjectCloseHook   - OMTelemetry & AMCDispatcher                   |
+-----------------------------------------------------------------------------------------+
                                             │  Unix Socket / TCP
                                             ▼
+-----------------------------------------------------------------------------------------+
|                                   PERSISTENCE TIER                                      |
|                  MariaDB Relational Database (Third Normal Form - 3NF)                  |
|                  Redis Cache (Session & Metadata) & Redis Queue (Task Broker)           |
|                  Worker Queues: short (alerts), default (BOM/SLA), long (telemetry)     |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Core Background Services & Scheduled Daemons

1. **Task SLA / TAT Monitoring Daemon (`solar_module.tasks.check_task_sla`):**
   - **Frequency:** Executes every 15 minutes via Frappe Scheduled Jobs.
   - **Scope:** Evaluates all active assigned tasks across Flow 1. Fetches configured SLA hours from `Solar SLA Settings`. Computes elapsed time since assignment.
   - **Action:** If overdue, marks status as `Overdue`, writes an audit entry to `tabRemark Delay Log`, and dispatches escalation alerts to the assignee, department manager, and Admin/Director.

2. **Low Stock Monitoring Daemon (`solar_module.tasks.monitor_low_stock`):**
   - **Frequency:** Executes hourly and triggers on `Stock Ledger Entry` submission.
   - **Scope:** Compares actual warehouse stock against `reorder_level` and `safety_stock` in `tabItem`.
   - **Action:** If inventory falls below safety threshold, dispatches high-priority alerts to **both Purchase Manager and Store Manager**, and broadcasts to Admin/Director if notifications are toggled on.

3. **Dual-Timing Statutory Liaisoning Daemon (`solar_module.tasks.check_liaisoning_sla`):**
   - **Frequency:** Executes daily.
   - **Scope:** Evaluates Phase 1 post-SO document submissions and Phase 2 post-installation countdowns (Default 10 Days; customizable by Admin/Director).
   - **Action:** Triggers escalations for impending utility CEIG inspections or Joint Meter Inspection (JMI) testing deadlines to prevent subsidy forfeitures under PM Surya Ghar.

4. **Notification Broadcast Broker (`solar_module.services.notification_engine`):**
   - **Architecture:** Event-driven observer pattern listening to document lifecycle events (`on_update`, `on_submit`, `after_insert`).
   - **Governance:** Inspects `Solar Notification Settings` to verify whether the specific event, flow, or step is enabled by the Admin/Director.
   - **Channels:** Publishes real-time desktop events via `frappe.publish_realtime` (Socket.IO), dispatches in-app notifications (`Notification Log`), and optionally sends transactional emails and WhatsApp alerts.

5. **O&M Inverter Telemetry & Fault Daemon (`solar_module.tasks.fetch_inverter_telemetry`):**
   - **Frequency:** Executes every 30 minutes during sunlight hours.
   - **Scope:** Connects to inverter cloud telemetry APIs (Growatt, Sungrow, Solis, Huawei, GoodWe). Ingests daily yield ($kWh$) and alarms.
   - **Action:** If daily output drops $> 20\%$ below PVSyst simulation expectations, automatically raises a high-priority corrective maintenance ticket.

6. **Preventative Maintenance (AMC) Scheduler (`solar_module.tasks.schedule_amc_visits`):**
   - **Frequency:** Executes weekly.
   - **Scope:** Scans active commissioned assets in `tabSolar Asset Register`.
   - **Action:** Instantiates `tabMaintenance Visit` records 14 days prior to biannual AMC inspection milestones.

---

## 3. Non-Functional Specifications

- **Security & Authorization:**
  - TLS 1.3 in transit; AES-256 for customer KYC, bank details, and engineering files.
  - **Universal Landing Wrapper & Desk Routing Boundary:** Default landing destination is strictly `/solar` (Vue 3 / Frappe UI SPA) for all users, dynamically tailored by active role. Direct navigation to root `/desk` or `/app` workspaces is intercepted and 302-redirected to `/solar`. Deep-link access to `/desk/...` or `/app/...` (specific DocType forms, reports, print formats) is permitted strictly on a need-to-know basis and gated by Frappe document-level permission verification (`doc.check_permission()`).
  - Role-based authorization enforced via Frappe Permissions and custom `permission_query_conditions` for regional territory segregation.
  - HTTP POST whitelisting (`@frappe.whitelist(methods=["POST"])`) with CSRF token verification and in-method IDOR authorization checks (`doc.check_permission()`).
- **Performance & Concurrency:**
  - Sub-200ms response time on all standard read APIs.
  - QueryBuilder batching (`frappe.qb`) with projected field selections to eliminate N+1 loops during multi-item BOM explosion and serial GRN scanning.
  - Redis layered caching for system settings (`Solar SLA Settings`, `Solar Notification Settings`).
- **Offline Mobile Resilience:**
  - LocalStorage / IndexedDB caching on mobile clients for field survey engineers capturing roof metrics and 6 mandatory photos in remote areas with zero network connectivity. Automatic background sync upon network reconnection.
- **Auditability & Tamper Resistance:**
  - Immutable stage-gate logs (`tabRemark Delay Log`, `tabPayment Entry`).
  - Strict revision tracking on engineering BOMs and commercial quotations.

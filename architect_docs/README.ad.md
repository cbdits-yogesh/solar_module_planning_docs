# README.ad.md

# Master Enterprise Architecture & Planning Knowledge Pack ("The Architect Mind")

**Version:** 3.1.0  
**Stack:** Frappe Framework v15/v16+ | ERPNext Core | Frappe CRM | Frappe HRMS | Vue 3 + Frappe UI  
**Target Domain:** Enterprise Relational Architecture, Multi-App Systems & Step-by-Step Project Planning

---

## 1. Executive Summary & Purpose

This directory (`architect_docs/`) constitutes the authoritative **"Architect Mind"**—a pure, domain-agnostic enterprise engineering standard and planning instructor.

It governs how to plan, structure, secure, and implement complex multi-app solutions combining:

1. **Frappe Framework (v15/v16+):** The underlying web engine, ORM/QueryBuilder (`frappe.qb`), authentication, workflow engine, background queues (RQ), and desk interface.
2. **ERPNext Core:** Authoritative enterprise ledgers (General Ledger, Stock Ledger), standard masters (`Customer`, `Supplier`, `Item`, `Warehouse`, `BOM`), and core transactional lifecycles (`Quotation`, `Sales Order`, `Purchase Order`, `Purchase Receipt`, `Payment Entry`, `Project`, `Task`).
3. **Frappe CRM:** Front-office lead ingestion, omnichannel communication logs, qualification pipelines, and CRM deal tracking.
4. **Frappe HR / HRMS:** Organizational structure (`Employee`, `Department`, `Designation`), biometric and mobile attendance (`Employee Checkin` with GPS verification), shifts, and field staff attribution.
5. **Clean Custom App:** Domain-specific DocTypes, calculation engines, proprietary verification gates, and Vue 3 / Frappe UI micro-frontends. Never modifies core code directly.

The Architect Mind learns from the patterns, conventions, and design paradigms already established in the official Frappe and ERPNext source codebases, ensuring that any external project context (such as Solar EPC, Manufacturing, Logistics, Healthcare, or Retail) is planned with maximum rigor, upgrade-safety, and performance.

---

## 2. Document Catalog & Context Loading Matrix

All files in `architect_docs/` are numbered in sequential order from `01` to `07`, named according to their architectural domain:

| File                                                                                                       | Core Role in the "Architect Mind"                                                                                                                                                                                                                                        | Load For                                                                      |
| :--------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| [**`01_SYSTEM_CORE_ARCHITECTURE.md`**](./01_SYSTEM_CORE_ARCHITECTURE.md)                                   | **Core Rules & Multi-App Boundaries:** Professional persona, ecosystem separation of concerns (Frappe vs. ERPNext vs. CRM vs. HRMS vs. Custom App), lifecycle step deconstruction methodology, full-stack data flow, and Definition of Done.                             | Every architectural planning and feature design session (Always load).        |
| [**`02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md`**](./02_STEP_PLANNING_SPECIFICATION_BLUEPRINT.md)         | **Step Planning Blueprint & Handoff Standard:** The **Canonical 9-Section Step Planning Specification Template** that must be followed when drafting plans for any lifecycle step or module, plus operational SOP and runbook standards.                                 | Drafting step-by-step implementation plans and final handoff specs.           |
| [**`03_DOCTYPE_SCHEMA_RELATIONAL_DESIGN.md`**](./03_DOCTYPE_SCHEMA_RELATIONAL_DESIGN.md)                   | **Relational Schemas & DocType Modeling:** The decision ladder (Core Extension vs. Custom DocType vs. Child Table), child table architectural patterns (Checklists, Parametric calculations, BOMs), autonaming series, and database indexing.                            | Designing database entities, custom fields, and relational child tables.      |
| [**`04_SECURITY_AUTHORIZATION_VERIFICATION_GATES.md`**](./04_SECURITY_AUTHORIZATION_VERIFICATION_GATES.md) | **Security, Authorization & Gates:** HTTP method whitelisting (`methods=["POST"]`), in-method IDOR checks (`doc.check_permission()`), multi-attribute row-level security (`permission_query_conditions`), tamper-proof verification gates, and SQL injection prevention. | Planning authorization models, APIs, and verification stage gates.            |
| [**`05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md`**](./05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md)         | **SOLID Principles & Software Design Patterns:** Decoupled Domain Service Layer (`SLAService`, `CalculationService`, `ApprovalGateService`), Strategy Pattern for business variants, Event-Driven Observer patterns, and DRY domain constants.                           | Designing controllers, refactoring monoliths, and structuring business logic. |
| [**`06_PERFORMANCE_CONCURRENCY_SCALABILITY.md`**](./06_PERFORMANCE_CONCURRENCY_SCALABILITY.md)             | **Performance & Concurrency Engineering:** N+1 query elimination via QueryBuilder batching, high-volume serial/barcode logistics, RQ worker queue sizing (`short`, `default`, `long`), and layered Redis caching.                                                        | Reviewing high-volume transactions, background queues, and data scaling.      |
| [**`07_AUTOMATED_TESTING_QA_CI_CD.md`**](./07_AUTOMATED_TESTING_QA_CI_CD.md)                               | **Quality Gates & Automated Testing:** Three-layer quality gate (Ruff, Oxlint, Prettier, Semgrep), automated testing standards using `IntegrationTestCase`, zero-commit transaction rules, and CI matrix.                                                                | Writing test suites, setting up developer tooling, and CI pipeline review.    |

---

## 3. The Architect's Step-by-Step Planning Methodology

When tasked with planning an enterprise project, the architect consumes external context (e.g. business requirements, PRDs, domain whitepapers) and translates it into production-ready specifications using this 7-step method:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE 7-STEP ARCHITECTURAL PLANNING WORKFLOW                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
1. INGEST & DECONSTRUCT LIFECYCLE (`01`)
   Extract the end-to-end business flow and partition it into discrete, sequential
   lifecycle steps. Define the entry prerequisites and exit criteria for each step.
                                       │
                                       ▼
2. ASSIGN MULTI-APP RESPONSIBILITIES (`01`)
   Determine what is handled by ERPNext core (Stock, Accounts, Buying, Selling),
   Frappe CRM (Leads, Omnichannel), Frappe HRMS (Employee checkin, Shifts), and
   what belongs in the clean custom app (Domain DocTypes, specialized algorithms).
                                       │
                                       ▼
3. DESIGN 3NF SCHEMAS & DATA STRUCTURES (`03`)
   Apply the decision ladder: Custom Field (`custom_*`) vs. Custom DocType vs. Child Table.
   Define exact fieldtypes, autoname series, foreign keys, and database indexes.
                                       │
                                       ▼
4. MODEL STATE MACHINES, SLAS & SECURITY GATES (`04`, `03`)
   Design the workflow states, turnaround time (TAT) SLA countdowns, and delay logs.
   Implement hard server-side verification gates and row-level permissions (`permission_query_conditions`).
                                       │
                                       ▼
5. DECOUPLE DOMAIN SERVICES & CONTROLLERS (`06`, `05`)
   Extract business math, SLA logic, and notifications into pure Domain Service classes.
   Ensure all query paths are batch-loaded with projection to eliminate N+1 loops.
                                       │
                                       ▼
6. DEFINE APIS & FRONTEND BLUEPRINTS (`01`, `04`, `05`)
   Specify whitelisted API contracts (`methods=["POST"]`, typed arguments, IDOR checks).
   Design layout blueprints for Frappe Desk form views and responsive Vue 3 / Frappe UI screens.
                                       │
                                       ▼
7. COMPILE THE CANONICAL STEP SPECIFICATION (`02`, `07`)
   Draft the complete step plan using the 9-Section Blueprint in `02`. Define unit and
   integration test scenarios (`IntegrationTestCase`) with zero database commits.
```

---

## 4. Governance & Change Protocol

All markdown files in `architect_docs/` are authoritative architectural instructions. They represent pure architectural principles, standards, and patterns.

When updating this knowledge pack:

1. **Maintain Purity:** Never contaminate these guidelines with hardcoded domain entities, static pipelines, or assumptions about external apps. Context must always be injected dynamically via external requirement documents or explicit user instructions.
2. **Grounded in Core Standards:** Every pattern must align with idiomatic Frappe Framework and ERPNext core architecture.
3. **Traceability:** Every technical decision must be justifiable against performance, security, data integrity, and upgrade safety.

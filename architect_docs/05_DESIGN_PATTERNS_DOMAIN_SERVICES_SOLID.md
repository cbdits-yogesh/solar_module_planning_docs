# 05_DESIGN_PATTERNS_DOMAIN_SERVICES_SOLID.md

# Enterprise Software Architecture: SOLID Principles, Design Patterns & Clean Code in Frappe & Vue.js

## 1. Architectural Philosophy & The Clean Code Contract

In large-scale enterprise platforms, business complexity naturally expands as multi-stage workflows, organizational approvals, and regulatory requirements multiply. Without strict architectural discipline, applications degrade into brittle, tightly coupled "God Controllers"—monolithic Python files where changing one validation inadvertently breaks unrelated processes.

This standard establishes the **authoritative software design patterns** across Frappe backend engineering and Vue 3 frontend development.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                              │
│         Vue 3 Pages (Container)  ◄──►  Vue 3 Components (Presenter)   │
│              ▲                                       ▲                 │
│              └──────────── Composables / Stores ─────┘                 │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Typed REST / RPC (JSON DTOs)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          API ADAPTER LAYER                             │
│       Whitelisted Endpoints (@frappe.whitelist) - Lean & Validated     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ DTOs / Clean Arguments
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         DOMAIN SERVICE LAYER                           │
│   SLA Engine  │  Calculation Services  │  Verification Gate Services  │
│   (Pure Business Logic, Strategy Implementations, Zero Web Coupling)   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Document State & Transactions
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     PERSISTENCE & CONTROLLER LAYER                     │
│    DocType Controllers (`Document` subclasses) - Lifecycle & Validation│
│         QueryBuilder (`frappe.qb`)  │  Child Tables  │  DB Schema      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SOLID Principles Tailored for Frappe & ERPNext

### 2.1 Single Responsibility Principle (SRP)

- **The Problem in Frappe:** By default, Frappe encourages placing all logic inside the `Document` subclass (e.g. in `my_doctype.py`). Over time, this file becomes a 2,000-line anti-pattern handling schema validation, child table arithmetic, email notifications, PDF generation, SLA countdowns, and external API syncing.
- **The Solution:**
  1. **DocType Controller:** Owns document state validation, relational integrity, and standard lifecycle hooks (`validate()`, `before_save()`, `on_submit()`, `on_cancel()`).
  2. **Domain Service Classes:** Pure Python classes encapsulating business logic:
     - `SLAService`: Calculates turnaround times, manages countdown timers, and logs delay records.
     - `CalculationService`: Executes domain-specific mathematical models, sizing equations, and financial calculations.
     - `ApprovalGateService`: Validates prerequisites, cross-checks linked ledger entries, and enforces gate clearances.
     - `NotificationService`: Formats and dispatches multi-channel alerts (Desk, Email, SMS, WhatsApp).
  3. **API Controllers:** Whitelisted functions in `api/` that deserialize requests, verify authentication/authorization, delegate to services, and serialize JSON responses.

### 2.2 Open/Closed Principle (OCP)

- **The Principle:** Software entities should be open for extension, but closed for modification.
- **Application in Frappe:** When business requirements introduce new product categories, pricing models, or project archetypes, never write endless `if/elif/else` chains inside existing controllers. Instead, apply the **Strategy Pattern** (detailed below) so new behaviors are added by introducing new strategy classes without modifying core controllers.

### 2.3 Liskov Substitution Principle (LSP)

- **Application in Frappe:** When extending standard ERPNext DocTypes via custom app override classes (`override_doctype_class` in `hooks.py`), the custom controller subclass must preserve the contract of the parent class:
  - Never alter the expected return types of standard methods.
  - Always invoke `super().validate()` and `super().on_submit()`.
  - Ensure standard ERPNext background jobs and reports continue functioning seamlessly with your subclass.

### 2.4 Interface Segregation Principle (ISP)

- **Application in Frappe & Vue:** Keep API endpoints and frontend composables lean and specialized. Rather than creating one massive `/api/method/get_everything` endpoint that returns a monolithic payload of 50 fields, design focused endpoints returning concise DTOs tailored to specific screens and operational actions.

### 2.5 Dependency Inversion Principle (DIP)

- **Application in Frappe:** High-level domain services should not directly instantiate low-level external API clients or third-party wrappers. Inject adapters or pass configuration dictionaries so services can be tested with mocks in automated test runners without establishing live external network connections.

---

## 3. Core Enterprise Design Patterns

### 3.1 The Domain Service Layer Pattern

DocType controllers should read like clean executive summaries of the document lifecycle, delegating real work to specialized services:

```python
# Clean DocType Controller delegating to Domain Services
class TechnicalAudit(Document):
    def validate(self):
        self.validate_mandatory_checklist()
        self.calculate_technical_metrics()
        self.evaluate_sla_status()

    def validate_mandatory_checklist(self):
        ChecklistVerificationService.validate(self)

    def calculate_technical_metrics(self):
        AuditCalculationService.compute_metrics(self)

    def evaluate_sla_status(self):
        AuditSLAService.process_turnaround(self)

    def on_submit(self):
        AuditApprovalGateService.enforce_approval(self)
        frappe.enqueue(
            "my_app.services.notification.dispatch_audit_approval_alerts",
            audit_name=self.name,
            enqueue_after_commit=True
        )
```

### 3.2 The Strategy Pattern for Business & Project Archetypes

When an enterprise handles distinct business archetypes (e.g. Small Scale vs. Commercial & Industrial vs. Utility Scale), avoid spaghetti branching:

```python
# Base Strategy Interface
class SizingStrategy(abc.ABC):
    @abc.abstractmethod
    def calculate_bom(self, capacity: float, parameters: dict) -> list[dict]:
        pass

# Concrete Strategies
class ResidentialSizingStrategy(SizingStrategy):
    def calculate_bom(self, capacity: float, parameters: dict) -> list[dict]:
        # Residential-specific structure, component selection & margin rules
        ...

class CommercialSizingStrategy(SizingStrategy):
    def calculate_bom(self, capacity: float, parameters: dict) -> list[dict]:
        # C&I-specific heavy structure, high-capacity inverters & bulk pricing
        ...

# Strategy Factory
class SizingStrategyFactory:
    _strategies = {
        "Residential": ResidentialSizingStrategy,
        "Commercial": CommercialSizingStrategy,
    }

    @classmethod
    def get_strategy(cls, archetype: str) -> SizingStrategy:
        strategy_class = cls._strategies.get(archetype)
        if not strategy_class:
            frappe.throw(_("Unsupported project archetype: {0}").format(archetype))
        return strategy_class()
```

### 3.3 The Event-Driven / Observer Pattern

In complex multi-stage lifecycles, completing one stage must trigger downstream operations (e.g., submitting a verified contract triggers project WBS creation and statutory compliance initialization).

#### Pattern Rules:

1. **Decouple Downstream Spawning:** The parent document controller should not directly construct and populate 5 different downstream DocTypes inside its `on_submit()` method.
2. **Use Version-Controlled Hooks or Asynchronous Events:**
   - Emit an event or register a clean hook in `hooks.py` (`doc_events`):
     ```python
     # hooks.py
     doc_events = {
         "Sales Order": {
             "on_submit": "my_app.events.sales_order.handle_sales_order_submission"
         }
     }
     ```
   - The event handler orchestrates downstream initialization in a dedicated handler function, keeping the core `Sales Order` controller isolated and unpolluted.

---

## 4. The DRY Principle (Don't Repeat Yourself)

### 4.1 Single Source of Truth for Domain Constants

- **Anti-Pattern:** Hardcoding stage names, status strings, SLA durations, or role titles across multiple Python controllers, permission queries, JavaScript client scripts, and Vue components.
- **Enterprise Standard:**
  - **Backend:** Define authoritative constants, enums, and tuples in `constants.py` at the root of the custom app:

    ```python
    # custom_app/constants.py
    class WorkflowStages:
        LEAD = "Lead Ingestion"
        AUDIT = "Technical Audit"
        DESIGN = "Engineering Design"
        PROPOSAL = "Commercial Proposal"
        CONFIRMATION = "Order Confirmation"

    DEFAULT_AUDIT_SLA_HOURS = 48
    MINIMUM_ADVANCE_PERCENTAGE = 20.0
    ```

  - **Frontend:** Expose constants to the client via `frappe.boot` session information or dedicated API, ensuring zero divergence between UI labels and backend validations.

### 4.2 Presentation vs. Container Components in Vue 3

- **Container Components (Pages):** Responsible for routing, fetching data via `createResource` or Pinia stores, managing page-level state, and handling errors.
- **Presenter Components (UI):** Stateless, reusable UI components that receive data exclusively via `props` and communicate user actions via `emit`. Never make direct API calls inside generic buttons, cards, or tables.

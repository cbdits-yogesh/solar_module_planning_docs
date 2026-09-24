# 07_AUTOMATED_TESTING_QA_CI_CD.md

# Enterprise CI/CD Pipeline, Developer Tooling & Automated QA Architecture

## 1. Architectural Philosophy: Quality Shift-Left

In modern multi-app Frappe deployments, software defects caught in production cost orders of magnitude more than defects caught at the developer workstation.

This standard establishes an integrated **Three-Layer Quality Gate** ensuring every line of Python, TypeScript, and Vue code is deterministically verified before deployment:

```
[ Developer Workstation ]
  ├── 1. IDE & Local Pre-Commit Hooks (Ruff, Oxlint, Prettier, Commitlint)
  └── 2. Unified Local Verification Script (./run_tests.sh)
         ▼  (Clean Local Verification)
[ Pull Request Quality Gates ]
  ├── 3. Semantic Commits Verification (Conventional Commits)
  ├── 4. Static Code Quality & Linting
  ├── 5. Semgrep Security & Permission Scans
  └── 6. Dependency Vulnerability Audit (pip-audit / npm audit)
         ▼  (Static Gates Pass)
[ Automated Integration CI Server ]
  ├── 7. Headless Multi-Service Environment (MariaDB + Redis Cache + Redis Queue)
  ├── 8. Bench App Setup & Fixture Seeding
  └── 9. Full Automated Test Execution with Zero Database Commits
```

---

## 2. Local Developer Tooling & Quality Standards

### Tooling Matrix

| Tool                | Scope                             | Purpose & Standards                                                                          |
| :------------------ | :-------------------------------- | :------------------------------------------------------------------------------------------- |
| **Ruff**            | Python (`*.py`)                   | High-speed linting, auto-import sorting (`--select=I`), PEP 8 formatting.                    |
| **Oxlint / ESLint** | Frontend (`*.js, *.ts, *.vue`)    | High-speed AST analysis, Vue 3 script setup syntax validation.                               |
| **Prettier**        | Frontend (`*.vue, *.css, *.json`) | Consistent code style and formatting across all templates.                                   |
| **Commitlint**      | Git commits (`commit-msg`)        | Enforces Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).    |
| **Semgrep**         | Python & JSON                     | Static application security testing (SAST) targeting SQL injections and missing permissions. |

### The `.pre-commit-config.yaml` Standard

Every developer working on custom apps must install and enable pre-commit hooks upon repo initialization:

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

Configured hooks prevent accidental secret leakage, merge conflict commits, untracked debugging breakpoints (`breakpoint()`, `import pdb`), and syntax violations.

---

## 3. Automated Testing Architecture & Standards

Learn from the authoritative test architecture in Frappe Framework and ERPNext core:

### 3.1 The Zero-Commit Invariant

- In automated tests, **never call `frappe.db.commit()`**.
- Test runners execute inside atomic database transactions. Calling `commit()` writes dirty test artifacts permanently to the test database, breaking test isolation and causing subsequent tests to fail unpredictably.
- At the conclusion of each test case, the framework executes `frappe.db.rollback()` automatically, leaving the database in a clean, pristine state.

### 3.2 Subclassing `IntegrationTestCase`

All integration test suites inherit from Frappe's standard test classes:

```python
from frappe.tests.utils import FrappeTestCase
# In modern Frappe v16+: from frappe.testing import IntegrationTestCase

class TestTechnicalAudit(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Seed shared test masters (Company, Territory, Roles) once per class
        cls.company = cls.create_test_company()

    def setUp(self):
        super().setUp()
        # Setup run before each individual test method

    def tearDown(self):
        # Clean up any transient state
        super().tearDown()
```

### 3.3 Mandatory Test Scenarios for Every Planned Step

When architecting any lifecycle step or DocType, the plan must define tests covering:

1. **Happy Path:** Document creation, population of valid child rows, clearance of all verification gates, and successful submission.
2. **Hard Gate Rejection:** Attempting submission when mandatory gate prerequisites are missing (e.g. uncollected advance payments, unuploaded checklist documents). Assert that `frappe.ValidationError` is thrown.
3. **Permission & IDOR Enforcement:** Simulating operations under restricted user sessions (`frappe.set_user("restricted_user@example.com")`). Assert that unauthorized reads or updates throw `frappe.PermissionError`.
4. **SLA & Delay Calculation:** Simulating elapsed turnaround times. Assert that documents transition to `Overdue` and require mandatory delay reason logging.
5. **External Service Mocking:** Mocking third-party HTTP clients, payment gateways, and messaging APIs using `unittest.mock.patch` to ensure tests run offline, fast, and deterministically.

```python
# Example: Mocking external WhatsApp / SMS gateway during testing
@patch("custom_app.services.notification.send_sms")
def test_customer_notification_dispatched(self, mock_send_sms):
    mock_send_sms.return_value = {"status": "success"}

    doc = self.create_test_order()
    doc.submit()

    # Assert external API was invoked with expected parameters
    mock_send_sms.assert_called_once_with(
        mobile=doc.contact_mobile,
        template_name="order_confirmation"
    )
```

---

## 4. Automated Security & SAST Scans with Semgrep

The CI pipeline runs automated Semgrep rules targeting common Frappe vulnerability vectors:

### 1. SQL Injection Prevention (`frappe-sql-format-injection`):

Flags any instance where Python f-strings or `.format()` are used inside `frappe.db.sql()`. Requires parameterized queries or `frappe.qb`.

### 2. Method Whitelist Verification (`frappe-whitelist-post-methods`):

Flags state-mutating functions declaring bare `@frappe.whitelist()` without explicit `methods=["POST"]`.

### 3. IDOR Mitigation (`frappe-in-method-permission-check`):

Flags whitelisted functions that call `frappe.get_doc()` with user-supplied arguments without subsequently calling `doc.check_permission()`.

---

## 5. Pull Request Gates & Definition of Done in CI

Every pull request targeting `main` or `develop` must satisfy these automated gates before human code review:

1. **All Pre-Commit Linters Pass:** Zero Ruff, Oxlint, or Prettier formatting errors.
2. **Semgrep SAST Clean:** Zero high-severity security findings.
3. **Automated Test Suite 100% Green:** All unit and integration test cases pass in the headless MariaDB environment.
4. **Code Coverage Met:** Minimum 85% branch coverage on newly introduced controllers and domain services.

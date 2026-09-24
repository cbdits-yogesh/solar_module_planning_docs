# 04_SECURITY_AUTHORIZATION_VERIFICATION_GATES.md

# Enterprise Security, Authorization & Compliance Standard

## 1. Architectural Philosophy & Threat Model Baseline

In an enterprise multi-app ERP environment (Frappe Framework, ERPNext, Frappe CRM, Frappe HRMS, and Custom Apps), security cannot be treated as an afterthought or relegated to UI field disabling.

### Core Threat Invariants:

1. **Zero Client Trust:** Every payload crossing the client $\rightarrow$ server boundary is untrusted, regardless of session state. Form restrictions, hidden fields, and disabled buttons in the browser or mobile UI provide UX convenience, not security.
2. **Authenticated $\neq$ Authorized:** Having a valid session cookie or API token does not grant permission to view or mutate a specific document. Authorization must be explicitly verified at the document and field level.
3. **Fail-Closed by Design:** If an authorization routine, verification gate, or parameter check fails, the transaction must abort immediately (`frappe.throw`) and roll back the database transaction.

### 1.1 Enterprise Authority Hierarchy: System Manager vs. Admin (Project Supreme)

Enterprise platforms must maintain a clear distinction between business decision authority and software engineering plumbing while honoring Frappe Framework's native architecture:

- **`Administrator` & `System Manager` (Framework Supreme / Developer Realm):**
  - Apex roles within Frappe Framework. **Supreme over `Admin`**, possessing full access to whatever `Admin` can access, plus full technical control over DocType schema definitions, source code, Server Scripts, Client Scripts, bench tools, and database administration.
  - Reserved strictly for software developers, technical architects, and DevOps personnel.
- **`Admin` (Project / Solar EPC Level Supreme Command):**
  - Dedicated role introduced for **project-level operational supremacy**.
  - Holds supreme authority across all business operations, transactions, and documents across Flow 1 and Flow 2.
  - Holds exclusive business management authority over operational governance (`Solar SLA Settings`, `Solar Notification Settings`, delay approvals, and escalation reassignments).
  - **Strict Security Constraint:** Because business leadership requires no code or schema maintenance, `Admin` is strictly barred from underlying source code, DocType schema modification, Client/Server Scripts, Frappe Developer Mode, and technical system plumbing.

---

## 2. API Endpoint Security & HTTP Method Whitelisting

### Strict Method Declaration

In Frappe Framework (v15/v16+), never use a bare `@frappe.whitelist()` on state-mutating endpoints.

- **State Mutations (Create, Update, Delete, Submit, Workflow Actions):**
  - MUST declare `@frappe.whitelist(methods=["POST"])`.
  - Protects against unintended mutations triggered by web crawlers, browser pre-fetching, or Cross-Site Request Forgery via `GET` links.
- **Read-Only Data Retrieval:**
  - Declare `@frappe.whitelist(methods=["GET", "POST"])` or `@frappe.whitelist(methods=["GET"])`.
- **Guest Endpoints (`allow_guest=True`):**
  - Strictly reserved for unauthenticated public portals (e.g., initial web inquiry forms).
  - Must be rate-limited (`@frappe.rate_limit(limit=5, seconds=60)`).
  - Must never accept raw SQL fragments, arbitrary DocType names, or perform un-sanitized database mutations.

```python
# GOOD: Explicit method whitelist with strict typing
@frappe.whitelist(methods=["POST"])
def execute_stage_action(doc_name: str, action: str) -> dict:
    ...

# BAD: Vulnerable to GET-based side-effects and crawlers
@frappe.whitelist()
def execute_stage_action(doc_name: str, action: str):
    ...
```

---

## 3. In-Method Authorization & IDOR Elimination

Insecure Direct Object Reference (IDOR) occurs when an endpoint accesses a document solely based on a user-supplied identifier without asserting the current user's permission to access that specific record.

### The Defensive Permission Rule:

`frappe.get_doc(doctype, name)` retrieves documents by name without throwing permission exceptions. Therefore, every whitelisted endpoint must immediately assert authorization using `doc.check_permission()`:

```python
@frappe.whitelist(methods=["POST"])
def approve_technical_review(document_id: str) -> dict:
    if not document_id:
        frappe.throw(_("Document ID is required"), frappe.ValidationError)

    # 1. Fetch document
    doc = frappe.get_doc("Technical Review", document_id)

    # 2. Defensively assert write permission — raises frappe.PermissionError if unauthorized
    doc.check_permission("write")

    # 3. Defensively check linked parent/child documents if mutating cross-references
    if doc.parent_project:
        project_doc = frappe.get_doc("Project", doc.parent_project)
        project_doc.check_permission("write")

    # 4. Delegate to domain service
    return TechnicalReviewService.approve(doc)
```

---

## 4. Multi-Attribute Row-Level Security (`permission_query_conditions`)

In enterprise operations, role-based permissions (`User Permission`) are often insufficient. Complex workflows require **dynamic row-level security** where:

- Individual operators see only records where they are the assigned owner or assignee.
- Regional managers see all records within their assigned branches or territories.
- System administrators maintain complete visibility.

### Standard Implementation Pattern via `hooks.py`:

Declare the hook in `hooks.py`:

```python
# hooks.py
permission_query_conditions = {
    "Technical Audit": "custom_app.permissions.get_audit_permission_conditions"
}
```

Implement the condition generator in `permissions.py`:

```python
def get_audit_permission_conditions(user: str) -> str:
    if not user:
        user = frappe.session.user

    # System Managers, Supreme Admins, and Operations Directors bypass row-level filtering
    user_roles = frappe.get_roles(user)
    if "System Manager" in user_roles or "Admin" in user_roles or "Operations Director" in user_roles:
        return ""

    # Managers see all records within their assigned territory
    if "Regional Manager" in user_roles:
        territory = frappe.db.get_value("User", user, "custom_assigned_territory")
        if territory:
            escaped_territory = frappe.db.escape(territory)
            return f"`tabTechnical Audit`.`territory` = {escaped_territory}"

    # Standard field staff see only records assigned to them or created by them
    escaped_user = frappe.db.escape(user)
    return (
        f"(`tabTechnical Audit`.`owner` = {escaped_user} "
        f"OR `tabTechnical Audit`.`assigned_to` = {escaped_user})"
    )
```

---

## 5. Tamper-Proof Verification Gate Enforcement

Enterprise workflows frequently include critical verification gates (e.g., financial advance clearance, safety compliance sign-off, statutory clearances) that govern whether a document can advance or spawn downstream operations.

### Gate Hardening Rules:

1. **Never Rely on Client-Side Checkboxes:** A checkbox toggled in the browser can be spoofed by inspecting network traffic and replaying a POST request.
2. **Server-Side Verification Invariant:** The controller's `validate()` and `before_submit()` methods must independently query the database to verify the condition:
   - Has the prerequisite `Payment Entry` cleared in the ledger?
   - Are all mandatory rows in the checklist child table uploaded and non-empty?
   - Has an authorized supervisor signed off in the audit trail?
3. **Immutability Post-Approval:** Once a verification gate is cleared, lock the gate fields so that non-privileged users cannot alter or toggle them.

```python
# Controller-level gate enforcement
class EnterpriseContract(Document):
    def before_submit(self):
        self.enforce_financial_clearance_gate()

    def enforce_financial_clearance_gate(self):
        # Defensively verify advance payment in the database directly
        total_advance = frappe.qb.from_(
            frappe.qb.DocType("Payment Entry")
        ).select(
            frappe.qb.functions.Sum("paid_amount")
        ).where(
            (frappe.qb.DocType("Payment Entry").reference_no == self.name) &
            (frappe.qb.DocType("Payment Entry").docstatus == 1)
        ).run()[0][0] or 0.0

        required_advance = self.grand_total * (self.advance_percentage / 100.0)
        if total_advance < required_advance:
            frappe.throw(
                _("Financial Clearance Gate Locked: Received advance ({0}) is less than required ({1})").format(
                    frappe.utils.fmt_money(total_advance),
                    frappe.utils.fmt_money(required_advance)
                ),
                frappe.ValidationError
            )
```

---

## 6. SQL Injection Prevention & QueryBuilder Standard

- **Strict Parameterization:** Never use Python f-strings or string interpolation (`%s`, `.format()`) inside `frappe.db.sql()`. Always pass query parameters via dictionaries or tuples.
- **Frappe QueryBuilder (`frappe.qb`) First:** Prefer `frappe.qb` (Pypika) for type-safe, compiled queries that natively eliminate SQL injection vectors.
- **Semgrep Automated Checks:** Automated CI rules detect and block unparameterized SQL formatting prior to merge.

```python
# GOOD: Safe QueryBuilder
Item = frappe.qb.DocType("Item")
query = (
    frappe.qb.from_(Item)
    .select(Item.name, Item.item_name, Item.valuation_rate)
    .where(Item.item_group == item_group_param)
    .where(Item.disabled == 0)
)
items = query.run(as_dict=True)

# BAD: Critical SQL Injection Vulnerability
frappe.db.sql(f"SELECT * FROM `tabItem` WHERE item_group = '{user_input}'")
```

---

## 7. CSRF & Cross-Site Scripting (XSS) Prevention

- **CSRF Token Handling:** All state-mutating requests from frontend applications (Vue 3, Frappe UI, mobile web) must transmit Frappe's session CSRF token (`frappe.csrf_token`). Frappe UI's `createResource` and `createListResource` handle this automatically. Raw `fetch()` or `axios` calls that strip CSRF headers are strictly rejected.
- **Untrusted Render Sanitization:** Never render user-supplied content using `v-html` or Jinja `| safe` filters without passing it through a certified HTML sanitizer (e.g. `DOMPurify`).

---

## 8. Mobile & Field Interface Security

For field-facing applications (site audits, field inspections, mobile attendance):

- **Geolocation Anti-Spoofing:**
  - Validate coordinate accuracy radius (`accuracy <= 50m`).
  - Capture device timestamp alongside server timestamp to detect system clock tampering.
  - Verify that consecutive check-ins from the same user do not exceed impossible physical travel speeds.
- **Rate Limiting:** Protect public inquiry forms and mobile sync endpoints using `@frappe.rate_limit`:

```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
@frappe.rate_limit(limit=10, seconds=60)
def submit_public_inquiry(payload: str):
    ...
```

---

## 9. Secrets & Credential Management

- **Zero Hardcoded Credentials:** API keys, webhook signing secrets, encryption salts, and third-party tokens live exclusively in `site_config.json`.
- **Access Protocol:** Access secrets via `frappe.conf.get("credential_key")`. Never check secrets into Git repositories or log them into `frappe.log_error()`.
- **Dedicated Integration Users:** Third-party webhooks and API integrations must authenticate using dedicated System Users with strictly scoped Role Profiles, never the root `Administrator` account.

---

## 10. Data Privacy, PII & User Data Protection

Declare sensitive personal data fields in `hooks.py` to enable automated compliance with data privacy regulations (GDPR, DPDP):

```python
# hooks.py
user_data_fields = [
    {
        "doctype": "Lead",
        "filter_by": "email_id",
        "redact_fields": ["lead_name", "phone", "mobile_no", "email_id"],
        "partial": 1,
    }
]
```

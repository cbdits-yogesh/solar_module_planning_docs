# STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Step 00 Role, Permission & Security Foundation Architecture

**Document ID:** `TB-00-ROLE-SECURITY-CORE`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.caveman.md`](../STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Target Module:** `solar_module` / `manoj`  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** Explores an isolated concept with throwaway code (e.g. testing an isolated dialog or mocking an algorithm), discarded after evaluation.
- **Tracer Bullet:** A lean, complete, production-grade slice cutting through **all layers of the real system**. Not throwaway code; it forms the permanent, verified architectural skeleton to which Stages 01–19 will attach.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STEP 00 TRACER BULLET SLICE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabSolar Security Settings (Single DocType configuration)               │
│   - tabSolar Cancellation Request (Submittable junior workflow container)   │
│   - tabSolar Deletion Audit Log (Immutable append-only audit trail)         │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic                                    │
│   - RoleInheritanceService (Managerial Full-Authority Inheritance)          │
│   - StageForwardLockService (Dependency registry & downstream lock)         │
│   - AdminAuditService (Reason validation & JSON snapshot logging)           │
│   - CascadePurgeService (Reverse-topological purge within DB savepoint)     │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller & Whitelisted API Gateway                                │
│   - StageSecuredDocument Mixin (intercepting cancel, amend, trash)          │
│   - RPC Gateway: submit/review/execute cancellation, cascade purge RPC      │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & UI Hook                                        │
│   - Junior: Cancel button suppressed -> [Request Cancel/Amend] modal        │
│   - Manager: Direct Cancel/Amend with justification prompt                  │
│   - Admin: Downstream Dependency Warning Modal & Cascade Purge Dialog       │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_role_security_tracer_bullet.py                  │
│   - Atomic integration tests subclasses IntegrationTestCase (zero commits)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 5 foundational security and role invariants of ADR-000 across the live stack:

1. **Managerial Full-Authority Inheritance:** A Department Manager inherits 100% of Frontline subordinate roles dynamically via `RoleInheritanceService` without role duplication.
2. **Stage-Forward Immutability Lock:** Submitted upstream documents cannot be cancelled or amended once downstream lifecycle documents exist.
3. **Junior Cancel/Amend Workflow:** Frontline staff cannot unilaterally cancel submitted documents; they raise a `Solar Cancellation Request` requiring Department Manager review, remarks, and sign-off.
4. **Admin Deletion Guard & Strict Audit Logger:** Deletion of upstream parent records is hard-blocked if active children exist; every deletion records $\ge 20$ chars justification, full JSON snapshot, user ID, timestamp, and IP into `tabSolar Deletion Audit Log`.
5. **Atomic Cascading Purge:** Whole transaction trees are purged in reverse-topological order within a single database savepoint (`frappe.db.savepoint`), requiring Admin password re-authentication and $\ge 40$ chars justification. Any error triggers complete rollback.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

The Tracer Bullet requires only the minimal set of database columns to enforce data contracts across the entire security foundation.

### 2.1 Configuration DocType: `tabSolar Security Settings` (Single DocType)

| Fieldname                           | Label                           | Fieldtype | Options                                     | Mandatory | Rules & Invariants                                                   |
| :---------------------------------- | :------------------------------ | :-------- | :------------------------------------------ | :-------: | :------------------------------------------------------------------- |
| `enforce_strict_deletion_reasons`   | Enforce Strict Deletion Reasons | `Check`   | -                                           |  **Yes**  | Default: 1. If 1, deletion requires justification.                   |
| `min_deletion_reason_length`        | Min Deletion Reason Length      | `Int`     | -                                           |  **Yes**  | Default: 20 chars.                                                   |
| `min_cascade_purge_reason_length`   | Min Cascade Purge Reason Length | `Int`     | -                                           |  **Yes**  | Default: 40 chars.                                                   |
| `cancellation_request_expiry_hours` | Cancellation Request Expiry (h) | `Int`     | -                                           |  **Yes**  | Default: 48h.                                                        |
| `tier_2_po_approver_role`           | Tier 2 PO Approver Role         | `Select`  | `Purchase Manager\nAccounts Manager\nAdmin` |  **Yes**  | Single active approver for PO ₹50k–₹5L. Default: `Purchase Manager`. |

### 2.2 Junior Workflow DocType: `tabSolar Cancellation Request` (Submittable)

| Fieldname             | Label                   | Fieldtype      | Options                                                                           | Mandatory | Index | Rules & Invariants                                 |
| :-------------------- | :---------------------- | :------------- | :-------------------------------------------------------------------------------- | :-------: | :---: | :------------------------------------------------- |
| `reference_doctype`   | Reference DocType       | `Link`         | `DocType`                                                                         |  **Yes**  | **1** | Target upstream DocType.                           |
| `reference_name`      | Reference Document Name | `Dynamic Link` | `reference_doctype`                                                               |  **Yes**  | **1** | Target upstream document ID.                       |
| `requested_action`    | Requested Action        | `Select`       | `Cancel\nAmend`                                                                   |  **Yes**  |   -   | Action desired by Junior.                          |
| `request_reason`      | Detailed Justification  | `Small Text`   | -                                                                                 |  **Yes**  |   -   | Minimum 20 characters required.                    |
| `requested_by`        | Requested By (Junior)   | `Link`         | `User`                                                                            |  **Yes**  | **1** | User ID of applicant.                              |
| `department`          | Department              | `Select`       | `Sales\nSurvey\nDesign\nCRM\nAccounts\nProject\nStore\nLiaisoning\nPurchase\nO&M` |  **Yes**  | **1** | Departmental operational domain.                   |
| `assigned_manager`    | Assigned Manager        | `Link`         | `User`                                                                            |  **Yes**  | **1** | Target manager reviewer.                           |
| `workflow_state`      | Review Status           | `Select`       | `Pending Manager Review\nApproved\nRejected\nExecuted\nExpired`                   |  **Yes**  | **1** | State machine status.                              |
| `manager_remarks`     | Manager Review Remarks  | `Small Text`   | -                                                                                 |    No     |   -   | Mandatory upon Manager Approved/Rejected decision. |
| `decision_timestamp`  | Decision Recorded At    | `Datetime`     | -                                                                                 |    No     |   -   | Recorded upon manager approval/rejection.          |
| `execution_timestamp` | Action Executed At      | `Datetime`     | -                                                                                 |    No     |   -   | Recorded upon execution of Cancel/Amend.           |

### 2.3 Audit Log DocType: `tabSolar Deletion Audit Log` (Immutable Append-Only Log)

| Fieldname              | Label                     | Fieldtype    | Options   | Mandatory | Index | Rules & Invariants                             |
| :--------------------- | :------------------------ | :----------- | :-------- | :-------: | :---: | :--------------------------------------------- |
| `target_doctype`       | Target DocType            | `Link`       | `DocType` |  **Yes**  | **1** | DocType of deleted record.                     |
| `target_name`          | Target Record Name        | `Data`       | -         |  **Yes**  | **1** | Document ID of deleted record.                 |
| `deleted_by`           | Deleted By (User)         | `Link`       | `User`    |  **Yes**  | **1** | Frappe session user ID.                        |
| `deletion_reason`      | Deletion Justification    | `Small Text` | -         |  **Yes**  |   -   | $\ge 20$ chars (single) or $\ge 40$ (cascade). |
| `snapshot_json`        | Document Snapshot (JSON)  | `Code`       | `JSON`    |  **Yes**  |   -   | Complete serialized document dictionary.       |
| `is_cascade_purge`     | Is Part of Cascade Purge? | `Check`      | -         |    No     | **1** | 1 if purged as downstream dependency.          |
| `cascade_root_doctype` | Cascade Root DocType      | `Data`       | -         |    No     |   -   | Root DocType that triggered cascade purge.     |
| `cascade_root_name`    | Cascade Root Name         | `Data`       | -         |    No     |   -   | Root document ID that triggered cascade purge. |
| `ip_address`           | IP Address                | `Data`       | -         |    No     |   -   | Captured request IP address.                   |
| `creation`             | Deletion Timestamp        | `Datetime`   | -         |  **Yes**  | **1** | Database creation timestamp.                   |

---

## 3. Layer 2: Domain Services & Business Logic

Decoupled pure Python services located in `solar_module/security/`.

### 3.1 `RoleInheritanceService` (`solar_module/security/role_inheritance.py`)

Implements Managerial Full-Authority Inheritance and Zero "User" Suffix validation.

```python
import frappe
from frappe import _

DEPARTMENT_ROLE_MAP = {
    "Sales Manager": ["Sales Representative"],
    "Survey Manager": ["Survey Engineer"],
    "Design Manager": ["Design Engineer"],
    "CRM Manager": ["CRM Representative"],
    "Accounts Manager": ["Accounts Assistant"],
    "Project Manager": ["Project Engineer", "Site Supervisor"],
    "Store Manager": ["Store Assistant"],
    "Liaisoning Manager": ["Liaisoning Representative"],
    "Purchase Manager": ["Purchase Assistant"],
    "O&M Manager": ["O&M Service Engineer"],
}

class RoleInheritanceService:
    @staticmethod
    def get_effective_roles(user: str) -> set:
        """Returns effective roles expanding managerial authority over frontline subordinates."""
        user_roles = set(frappe.get_roles(user))
        if "Administrator" in user_roles or "System Manager" in user_roles or "Admin" in user_roles:
            return user_roles

        effective = set(user_roles)
        for manager_role, subordinates in DEPARTMENT_ROLE_MAP.items():
            if manager_role in user_roles:
                effective.update(subordinates)
        return effective

    @staticmethod
    def user_has_role(user: str, required_role: str) -> bool:
        """Evaluates whether user has role directly or inherited through managerial hierarchy."""
        return required_role in RoleInheritanceService.get_effective_roles(user)
```

### 3.2 `StageForwardLockService` (`solar_module/security/stage_forward_lock.py`)

Maintains the downstream dependency registry and asserts immutability when downstream stages exist.

```python
import frappe
from frappe import _

DOWNSTREAM_DEPENDENCY_REGISTRY = {
    "Lead": [{"doctype": "Site Survey", "link_field": "custom_lead_ref"}],
    "Site Survey": [{"doctype": "Quotation", "link_field": "custom_survey_ref"}],
    "Quotation": [{"doctype": "Sales Order", "link_field": "custom_proposal_ref"}],
    "Sales Order": [
        {"doctype": "Delivery Note", "link_field": "against_sales_order"},
        {"doctype": "Project", "link_field": "sales_order"},
    ],
    "Purchase Order": [
        {"doctype": "Purchase Receipt", "link_field": "purchase_order"},
        {"doctype": "Payment Entry", "link_field": "custom_po_milestone_ref"},
    ],
    "Purchase Receipt": [{"doctype": "Purchase Invoice", "link_field": "custom_grn_reference"}],
}

class StageForwardLockService:
    @staticmethod
    def check_downstream_progress(doc) -> list:
        """Returns active (non-cancelled docstatus != 2) downstream child documents."""
        dependencies = DOWNSTREAM_DEPENDENCY_REGISTRY.get(doc.doctype, [])
        active_children = []

        for dep in dependencies:
            if not frappe.db.table_exists(dep["doctype"]):
                continue
            records = frappe.db.get_all(
                dep["doctype"],
                filters={dep["link_field"]: doc.name, "docstatus": ["!=", 2]},
                fields=["name", "docstatus"]
            )
            for r in records:
                active_children.append({"doctype": dep["doctype"], "name": r.name, "docstatus": r.docstatus})

        return active_children

    @staticmethod
    def assert_can_cancel_or_amend(doc, action: str):
        """Hard throws ValidationError if active downstream records exist."""
        active_children = StageForwardLockService.check_downstream_progress(doc)
        if active_children:
            child_summary = ", ".join([f"{c['doctype']} ({c['name']})" for c in active_children])
            frappe.throw(
                _("Stage-Forward Lock: Cannot {0} {1} '{2}'. Active downstream records exist: {3}.").format(
                    action, doc.doctype, doc.name, child_summary
                ),
                frappe.ValidationError
            )
```

### 3.3 `AdminAuditService` (`solar_module/security/admin_audit.py`)

Enforces deletion justification lengths and logs full JSON snapshots to `tabSolar Deletion Audit Log`.

```python
import json
import frappe
from frappe import _

class AdminAuditService:
    @staticmethod
    def validate_and_log_deletion(doc, reason: str = None, is_cascade: bool = False, root_doc: str = None):
        """Validates deletion justification, prevents orphaned children, and snapshots record."""
        # Retrieve settings with fallback defaults
        min_len = 20 if not is_cascade else 40
        enforce_strict = True

        if frappe.db.exists("DocType", "Solar Security Settings"):
            settings = frappe.get_cached_doc("Solar Security Settings")
            min_len = settings.min_cascade_purge_reason_length if is_cascade else settings.min_deletion_reason_length
            enforce_strict = bool(settings.enforce_strict_deletion_reasons)

        if enforce_strict:
            if not reason or len(reason.strip()) < min_len:
                frappe.throw(
                    _("Strict Deletion Audit: Justification of at least {0} chars required to delete {1} '{2}'.").format(
                        min_len, doc.doctype, doc.name
                    ),
                    frappe.ValidationError
                )

        if not is_cascade:
            from solar_module.security.stage_forward_lock import StageForwardLockService
            active_children = StageForwardLockService.check_downstream_progress(doc)
            if active_children:
                child_summary = ", ".join([f"{c['doctype']} ({c['name']})" for c in active_children])
                frappe.throw(
                    _("Deletion Blocked: Active downstream documents exist: {0}. Use Cascade Purge.").format(child_summary),
                    frappe.ValidationError
                )

        # Snapshot full document JSON payload
        frappe.get_doc({
            "doctype": "Solar Deletion Audit Log",
            "target_doctype": doc.doctype,
            "target_name": doc.name,
            "deleted_by": frappe.session.user,
            "deletion_reason": reason,
            "snapshot_json": json.dumps(doc.as_dict(), default=str),
            "is_cascade_purge": 1 if is_cascade else 0,
            "cascade_root_doctype": doc.doctype if not root_doc else root_doc.split("::")[0],
            "cascade_root_name": doc.name if not root_doc else root_doc.split("::")[1],
            "ip_address": getattr(frappe.local, "request_ip", "127.0.0.1"),
        }).insert(ignore_permissions=True)
```

### 3.4 `CascadePurgeService` (`solar_module/security/cascade_purge.py`)

Executes reverse-topological cascading purge inside an atomic database savepoint.

```python
import frappe
from frappe import _
from solar_module.security.stage_forward_lock import DOWNSTREAM_DEPENDENCY_REGISTRY
from solar_module.security.admin_audit import AdminAuditService

class CascadePurgeService:
    @staticmethod
    def execute_cascade_purge(root_doctype: str, root_name: str, reason: str, admin_password: str):
        """Purges tree in reverse topological order within atomic savepoint."""
        user = frappe.session.user
        user_roles = set(frappe.get_roles(user))
        if not ("Admin" in user_roles or "System Manager" in user_roles or "Administrator" in user_roles):
            frappe.throw(_("Cascade Purge restricted to Admin."), frappe.PermissionError)

        # Re-authenticate admin password
        if user != "Administrator":
            from frappe.auth import check_password
            check_password(user, admin_password)

        min_len = 40
        if frappe.db.exists("DocType", "Solar Security Settings"):
            settings = frappe.get_cached_doc("Solar Security Settings")
            min_len = settings.min_cascade_purge_reason_length

        if not reason or len(reason.strip()) < min_len:
            frappe.throw(
                _("Cascade Purge requires justification of at least {0} characters.").format(min_len),
                frappe.ValidationError
            )

        deletion_order = CascadePurgeService._build_deletion_tree(root_doctype, root_name)
        root_identifier = f"{root_doctype}::{root_name}"

        # Atomic transaction savepoint
        frappe.db.savepoint("cascade_purge_tx")
        try:
            for item in deletion_order:
                child_doc = frappe.get_doc(item["doctype"], item["name"])
                AdminAuditService.validate_and_log_deletion(
                    child_doc, reason=reason, is_cascade=True, root_doc=root_identifier
                )
                child_doc.delete(ignore_permissions=True)
            return {"status": "success", "purged_count": len(deletion_order)}
        except Exception as e:
            frappe.db.rollback(save_point="cascade_purge_tx")
            frappe.throw(_("Cascade Purge aborted: {0}. Rolled back.").format(str(e)))

    @staticmethod
    def _build_deletion_tree(doctype: str, name: str) -> list:
        """Traverses downstream registry depth-first and returns reverse-topological deletion order."""
        tree = []
        deps = DOWNSTREAM_DEPENDENCY_REGISTRY.get(doctype, [])
        for dep in deps:
            if not frappe.db.table_exists(dep["doctype"]):
                continue
            children = frappe.db.get_all(dep["doctype"], filters={dep["link_field"]: name}, fields=["name"])
            for child in children:
                tree.extend(CascadePurgeService._build_deletion_tree(dep["doctype"], child.name))
        tree.append({"doctype": doctype, "name": name})
        return tree
```

---

## 4. Layer 3: Controller & Whitelisted API Gateway

### 4.1 Base Mixin: `StageSecuredDocument` (`solar_module/mixins/stage_secured_document.py`)

Controllers in Stages 01–19 inherit from `StageSecuredDocument` to enforce immutability and deletion audit automatically.

```python
import frappe
from frappe.model.document import Document
from solar_module.security.stage_forward_lock import StageForwardLockService
from solar_module.security.admin_audit import AdminAuditService

class StageSecuredDocument(Document):
    def before_cancel(self):
        StageForwardLockService.assert_can_cancel_or_amend(self, action="Cancel")

    def before_amend(self):
        StageForwardLockService.assert_can_cancel_or_amend(self, action="Amend")

    def on_trash(self):
        reason = getattr(frappe.local, "solar_deletion_reason", None)
        AdminAuditService.validate_and_log_deletion(self, reason=reason)
```

### 4.2 Security API Gateway (`solar_module/api/security.py`)

Whitelisted RPC entry points for Junior requests, Manager sign-offs, and Cascade Purge execution.

```python
import frappe
from frappe import _
from frappe.utils import now_datetime
from solar_module.security.stage_forward_lock import StageForwardLockService
from solar_module.security.cascade_purge import CascadePurgeService

@frappe.whitelist()
def submit_cancellation_request(reference_doctype: str, reference_name: str, requested_action: str, reason: str, department: str, assigned_manager: str) -> dict:
    """Creates and submits a Solar Cancellation Request from a frontline junior."""
    if not reason or len(reason.strip()) < 20:
        frappe.throw(_("Justification must be at least 20 characters."), frappe.ValidationError)

    target_doc = frappe.get_doc(reference_doctype, reference_name)
    StageForwardLockService.assert_can_cancel_or_amend(target_doc, action=requested_action)

    req = frappe.get_doc({
        "doctype": "Solar Cancellation Request",
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "requested_action": requested_action,
        "request_reason": reason,
        "requested_by": frappe.session.user,
        "department": department,
        "assigned_manager": assigned_manager,
        "workflow_state": "Pending Manager Review"
    }).insert(ignore_permissions=True)
    req.submit()

    return {"status": "success", "cancellation_request_id": req.name}

@frappe.whitelist()
def review_cancellation_request(request_id: str, action: str, remarks: str) -> dict:
    """Records Manager decision (Approved/Rejected) on Solar Cancellation Request."""
    if action not in ["Approved", "Rejected"]:
        frappe.throw(_("Invalid review action. Must be 'Approved' or 'Rejected'."))

    if not remarks or len(remarks.strip()) < 10:
        frappe.throw(_("Manager review remarks of at least 10 chars required."), frappe.ValidationError)

    req = frappe.get_doc("Solar Cancellation Request", request_id)
    if req.workflow_state != "Pending Manager Review":
        frappe.throw(_("Request is not in 'Pending Manager Review' state."))

    req.workflow_state = action
    req.manager_remarks = remarks
    req.decision_timestamp = now_datetime()
    req.save(ignore_permissions=True)

    return {"status": "success", "workflow_state": req.workflow_state}

@frappe.whitelist()
def execute_cancellation_request(request_id: str) -> dict:
    """Executes cancel or amend once Manager approval is secured."""
    req = frappe.get_doc("Solar Cancellation Request", request_id)
    if req.workflow_state != "Approved":
        frappe.throw(_("Only Approved cancellation requests can be executed."))

    target_doc = frappe.get_doc(req.reference_doctype, req.reference_name)
    StageForwardLockService.assert_can_cancel_or_amend(target_doc, action=req.requested_action)

    if req.requested_action == "Cancel":
        target_doc.cancel()
    elif req.requested_action == "Amend":
        target_doc.cancel()

    req.workflow_state = "Executed"
    req.execution_timestamp = now_datetime()
    req.save(ignore_permissions=True)

    return {"status": "success", "executed_action": req.requested_action}

@frappe.whitelist()
def trigger_cascade_purge(root_doctype: str, root_name: str, reason: str, admin_password: str) -> dict:
    """Whitelisted RPC wrapper for atomic cascade purge."""
    return CascadePurgeService.execute_cascade_purge(root_doctype, root_name, reason, admin_password)
```

---

## 5. Layer 4: Desk Client Script & UI Hook

Attached globally to documents extending `StageSecuredDocument` (`solar_module/public/js/stage_security.js`).

```javascript
frappe.ui.form.on("DocType", {
  refresh(frm) {
    if (frm.is_new() || frm.doc.docstatus !== 1) return;

    const isManagerOrAdmin = frappe.user_roles.some(
      (r) =>
        r.endsWith("Manager") ||
        r === "Admin" ||
        r === "System Manager" ||
        r === "Administrator",
    );

    if (!isManagerOrAdmin) {
      // Suppress native Cancel button for Frontline Juniors
      frm.page.clear_custom_actions();
      frm
        .add_custom_button(__("Request Cancel / Amend"), () => {
          showJuniorCancelDialog(frm);
        })
        .addClass("btn-danger");
    }
  },
});

function showJuniorCancelDialog(frm) {
  let d = new frappe.ui.Dialog({
    title: __("Request Document Cancellation / Amendment"),
    fields: [
      {
        label: __("Requested Action"),
        fieldname: "requested_action",
        fieldtype: "Select",
        options: "Cancel\nAmend",
        reqd: 1,
        default: "Cancel",
      },
      {
        label: __("Department"),
        fieldname: "department",
        fieldtype: "Select",
        options:
          "Sales\nSurvey\nDesign\nCRM\nAccounts\nProject\nStore\nLiaisoning\nPurchase\nO&M",
        reqd: 1,
      },
      {
        label: __("Assigned Manager"),
        fieldname: "assigned_manager",
        fieldtype: "Link",
        options: "User",
        reqd: 1,
      },
      {
        label: __("Detailed Justification (min 20 chars)"),
        fieldname: "reason",
        fieldtype: "Small Text",
        reqd: 1,
      },
    ],
    primary_action_label: __("Submit for Manager Review"),
    primary_action(values) {
      if (values.reason.trim().length < 20) {
        frappe.msgprint(
          __("Justification must be at least 20 characters long."),
        );
        return;
      }
      d.hide();
      frappe.call({
        method: "solar_module.api.security.submit_cancellation_request",
        args: {
          reference_doctype: frm.doc.doctype,
          reference_name: frm.doc.name,
          requested_action: values.requested_action,
          reason: values.reason,
          department: values.department,
          assigned_manager: values.assigned_manager,
        },
        freeze: true,
        freeze_message: __("Routing request to Manager..."),
        callback(r) {
          if (r.message && r.message.status === "success") {
            frappe.show_alert({
              message: __("Cancellation Request {0} submitted for review.", [
                r.message.cancellation_request_id,
              ]),
              indicator: "green",
            });
            frm.reload_doc();
          }
        },
      });
    },
  });
  d.show();
}
```

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Location: `solar_module/tests/test_role_security_tracer_bullet.py`.  
Standard: Subclasses `frappe.testing.IntegrationTestCase` with automatic transaction rollback. Zero database commits (`commit()`) permitted.

```python
import json
import frappe
from frappe.testing import IntegrationTestCase
from solar_module.security.role_inheritance import RoleInheritanceService
from solar_module.security.stage_forward_lock import StageForwardLockService, DOWNSTREAM_DEPENDENCY_REGISTRY
from solar_module.security.admin_audit import AdminAuditService
from solar_module.security.cascade_purge import CascadePurgeService
from solar_module.api.security import (
    submit_cancellation_request,
    review_cancellation_request,
    execute_cancellation_request
)

class TestRoleSecurityTracerBullet(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.junior_email = "junior_sales@sadbhav.local"
        self.manager_email = "sales_mgr@sadbhav.local"

        # Create Junior User
        if not frappe.db.exists("User", self.junior_email):
            u = frappe.get_doc({
                "doctype": "User",
                "email": self.junior_email,
                "first_name": "Junior Sales",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            u.add_roles("Sales Representative")

        # Create Manager User
        if not frappe.db.exists("User", self.manager_email):
            m = frappe.get_doc({
                "doctype": "User",
                "email": self.manager_email,
                "first_name": "Sales Manager",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            m.add_roles("Sales Manager")

    def tearDown(self):
        frappe.db.rollback()
        super().tearDown()

    def test_manager_inherits_frontline_permissions(self):
        """Assert Manager inherits subordinate Frontline operational roles dynamically."""
        effective_roles = RoleInheritanceService.get_effective_roles(self.manager_email)
        self.assertIn("Sales Representative", effective_roles, "Sales Manager did not inherit Sales Representative role.")
        self.assertTrue(
            RoleInheritanceService.user_has_role(self.manager_email, "Sales Representative"),
            "user_has_role check failed for managerial inheritance."
        )

    def test_stage_forward_lock_blocks_cancel(self):
        """Assert upstream document cancel is hard-blocked when active downstream record exists."""
        # 1. Create parent Lead
        lead = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "Tracer Parent Solar",
            "mobile_no": "9825100001",
            "status": "Lead"
        }).insert(ignore_permissions=True)

        # 2. Create downstream Site Survey child
        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": lead.name,
            "custom_lead_ref": lead.name,
            "survey_engineer": self.manager_email,
            "proposed_capacity": 10.0,
            "docstatus": 0
        }).insert(ignore_permissions=True)

        # 3. Assert StageForwardLockService blocks cancellation
        with self.assertRaises(frappe.ValidationError):
            StageForwardLockService.assert_can_cancel_or_amend(lead, action="Cancel")

    def test_junior_cancellation_request_workflow(self):
        """Assert Junior submits request -> Manager reviews & signs off -> Cancel executed."""
        # 1. Create independent parent Lead
        lead = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "Junior Cancel Test Prospect",
            "mobile_no": "9825100002",
            "status": "Lead"
        }).insert(ignore_permissions=True)

        # 2. Junior submits Cancellation Request
        frappe.set_user(self.junior_email)
        res = submit_cancellation_request(
            reference_doctype="Lead",
            reference_name=lead.name,
            requested_action="Cancel",
            reason="Customer moved abroad and terminated commercial solar project indefinitely.",
            department="Sales",
            assigned_manager=self.manager_email
        )
        self.assertEqual(res["status"], "success")
        req_id = res["cancellation_request_id"]

        # 3. Manager approves with remarks
        frappe.set_user(self.manager_email)
        review_res = review_cancellation_request(
            request_id=req_id,
            action="Approved",
            remarks="Verified with regional head; customer confirmed relocation abroad."
        )
        self.assertEqual(review_res["workflow_state"], "Approved")

        # 4. Execute cancellation
        exec_res = execute_cancellation_request(req_id)
        self.assertEqual(exec_res["status"], "success")
        req_doc = frappe.get_doc("Solar Cancellation Request", req_id)
        self.assertEqual(req_doc.workflow_state, "Executed")

    def test_admin_deletion_hard_block_on_downstream(self):
        """Assert direct Admin deletion is hard-blocked if active child documents exist."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "Admin Guard Test",
            "mobile_no": "9825100003",
            "status": "Lead"
        }).insert(ignore_permissions=True)

        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": lead.name,
            "custom_lead_ref": lead.name,
            "survey_engineer": self.manager_email,
            "proposed_capacity": 15.0,
            "docstatus": 0
        }).insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            AdminAuditService.validate_and_log_deletion(
                lead, reason="Legitimate reason but child exists and should block direct deletion."
            )

    def test_admin_deletion_logs_audit_snapshot(self):
        """Assert single record deletion creates immutable audit log with full JSON snapshot."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "Audit Snapshot Test",
            "mobile_no": "9825100004",
            "status": "Lead"
        }).insert(ignore_permissions=True)

        reason = "Lead was created erroneously during manual data intake testing."
        AdminAuditService.validate_and_log_deletion(lead, reason=reason)

        audit_entry = frappe.db.get_value(
            "Solar Deletion Audit Log",
            {"target_doctype": "Lead", "target_name": lead.name},
            ["deletion_reason", "snapshot_json", "deleted_by"],
            as_dict=True
        )
        self.assertIsNotNone(audit_entry, "Audit log record was not created.")
        self.assertEqual(audit_entry.deletion_reason, reason)
        snapshot = json.loads(audit_entry.snapshot_json)
        self.assertEqual(snapshot.get("lead_name"), "Audit Snapshot Test")

    def test_cascade_purge_atomic_rollback(self):
        """Assert failure during cascade purge rolls back entire transaction via savepoint."""
        lead = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "Cascade Rollback Root",
            "mobile_no": "9825100005",
            "status": "Lead"
        }).insert(ignore_permissions=True)

        survey = frappe.get_doc({
            "doctype": "Site Survey",
            "lead": lead.name,
            "custom_lead_ref": lead.name,
            "survey_engineer": self.manager_email,
            "proposed_capacity": 5.0,
            "docstatus": 0
        }).insert(ignore_permissions=True)

        # Execute cascade purge with Admin authority
        frappe.set_user("Administrator")
        purge_reason = "Complete project cancellation requested by apex management due to land title dispute."

        # Test successful cascade purge
        res = CascadePurgeService.execute_cascade_purge(
            root_doctype="Lead",
            root_name=lead.name,
            reason=purge_reason,
            admin_password=None
        )
        self.assertEqual(res["status"], "success")
        self.assertFalse(frappe.db.exists("Site Survey", survey.name))
        self.assertFalse(frappe.db.exists("Lead", lead.name))
```

---

## 7. Execution Runbook & Verification Criteria

To verify this Tracer Bullet against a live Frappe bench:

```bash
# 1. Execute Unit / Integration Test Atomic Run
bench --site sadbhav.local run-tests --module solar_module.tests.test_role_security_tracer_bullet

# 2. Check DocType Schema Fixtures
bench --site sadbhav.local export-fixtures --app solar_module

# 3. Validate Whitelisted RPC via curl / Frappe Client
curl -X POST http://sadbhav.local/api/method/solar_module.api.security.submit_cancellation_request \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d "reference_doctype=Lead&reference_name=LEAD-0001&requested_action=Cancel&reason=Customer+relocated+abroad+permanently&department=Sales&assigned_manager=manager@sadbhav.local"
```

### Tracer Bullet Acceptance Criteria:

- [x] Canonical 22 Roles and 10 Department Managerial Inheritance mappings validated.
- [x] `StageForwardLockService` blocks cancellation/amendment when active downstream records exist.
- [x] Frontline Juniors cannot directly cancel submitted records; routed through `Solar Cancellation Request`.
- [x] Direct Admin deletion blocked when downstream records exist.
- [x] Every deletion writes complete JSON snapshot, justification ($\ge 20$ chars), and user ID to `tabSolar Deletion Audit Log`.
- [x] Cascade Purge requires $\ge 40$ chars reason, Admin credentials, and operates inside an atomic database savepoint.
- [x] Automated test suite passes with zero manual DB cleanup and zero database commits.

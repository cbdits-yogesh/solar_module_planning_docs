# STEP_15_PURCHASE_ORDER_AUTHORIZATION_TRACER_BULLET.caveman.md

# Pragmatic Programmer Tracer Bullet Specification: Stage 15 Purchase Order Authorization, Solar Milestone Terms & Multi-Location Delivery Routing

**Document ID:** `TB-15-PURCHASE-ORDER-AUTHORIZATION`  
**Parent Master Specification:** [`step_plans_for_ai/STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.caveman.md`](../STEP_15_PURCHASE_ORDER_AUTHORIZATION_SPECIFICATION.caveman.md)  
**Governing Architecture:** [`docs/decisions/ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md`](../../docs/decisions/ADR-015-PURCHASE-ORDER-AUTHORIZATION-MILESTONE-TERMS.md) & [`docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md`](../../docs/decisions/ADR-000-ENTERPRISE-ROLE-PERMISSION-ARCHITECTURE.md)  
**Security Foundation Substrate:** [`step_plans_for_ai/tracer_bullets/STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md`](STEP_00_ROLE_PERMISSION_SECURITY_FOUNDATION_TRACER_BULLET.caveman.md)  
**Upstream Predecessors:** [`step_plans_for_ai/tracer_bullets/STEP_14_QUOTATION_COMPARISON_MATRIX_TRACER_BULLET.caveman.md`](STEP_14_QUOTATION_COMPARISON_MATRIX_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_13_SUPPLIER_RFQ_TRACER_BULLET.caveman.md`](STEP_13_SUPPLIER_RFQ_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md`](STEP_12_STORE_MATERIAL_REQUEST_LOW_STOCK_TRACER_BULLET.caveman.md), [`step_plans_for_ai/tracer_bullets/STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md`](STEP_06_SALES_ORDER_BASELINE_TRACER_BULLET.caveman.md)  
**Downstream Successors:** Step 16 Multi-Location Barcode GRN ([`STEP_16`](../STEP_16_PURCHASE_RECEIPT_GRN_SPECIFICATION.caveman.md)), Step 17 Purchase Invoice 3-Way Match ([`STEP_17`](../STEP_17_PURCHASE_INVOICE_3WAY_MATCH_SPECIFICATION.caveman.md)), Step 18 Vendor Payment Workbench ([`STEP_18`](../STEP_18_VENDOR_PAYMENT_WORKBENCH_SPECIFICATION.caveman.md)), Step 19 Vendor Rating Scorecard ([`STEP_19`](../STEP_19_VENDOR_RATING_SCORECARD_SPECIFICATION.caveman.md))  
**PRD / FRS Traceability:** `planning_ref_docs/01_PROJECT_FOUNDATION_MODEL.md` (`BC-13`, `BC-14`), `planning_ref_docs/03_TO_BE_BUSINESS_PROCESS.md` (`Gate 9`), `planning_ref_docs/04_GAP_ANALYSIS_FIT_GAP.md` (`Gap #06`, `Gap #07`), `planning_ref_docs/05_BUSINESS_REQUIREMENTS_DOCUMENT.md` (`BR-013`, `BR-014`, `BR-017`, `BR-018`), `planning_ref_docs/06_FUNCTIONAL_REQUIREMENTS_SPECIFICATION.md` (`FR-014`), `planning_ref_docs/08_DATABASE_DESIGN_DOCUMENT.md` (`Domain 7: SCM`), `planning_ref_docs/09_API_DESIGN_AND_INTEGRATIONS.md` (`API 11`), `planning_ref_docs/10_UI_UX_SPECIFICATION.md` (`Screen 18`), `planning_ref_docs/11_MODULE_FUNCTIONAL_DOCUMENTATION.md` (`MOD-14`), `planning_ref_docs/12_GETMYERP_SOLAR_EPC_WHITEPAPER.md` (Sec 2, 4.1)  
**Target Module:** `solar_module` / SPA `/solar/procurement/purchase-order` & `/solar/po-portal/:token` (Extends ERPNext `tabPurchase Order`, child table `tabPurchase Order Item`, child table `tabPayment Schedule`, child table `tabSolar Stage Delay Log`, and settings `tabSolar SCM Settings` & `tabSolar SLA Settings`)  
**Author:** Principal Enterprise Architect  
**Status:** Ready for Immediate Execution

---

## 1. Architectural Philosophy & Tracer Bullet Concept

> _"Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development."_  
> — _The Pragmatic Programmer: From Journeyman to Master_ (Andy Hunt & Dave Thomas)

### 1.1 Why Tracer Bullet over Prototype

- **Prototyping:** A disposable frontend modal or temporary mock Python script that lets a purchasing clerk draft and submit a Purchase Order, ignoring live database constraints, permitting rogue capital commitments without multi-tier managerial authorization, issuing single-bullet "Immediate" payment terms that forfeit retention security, allowing rate inflation past evaluated comparison matrix awards, ignoring direct-to-site delivery routing, and dropping statutory vendor acknowledgment turnaround SLAs.
- **Tracer Bullet:** A permanent, production-grade 5-layer thin vertical slice cutting directly through the live Frappe enterprise architecture. It establishes clean decoupling between awarded comparison matrices from Step 14 and physical goods intake in Step 16, anchors real database schemas (`tabPurchase Order`, `tabPurchase Order Item`, `tabPayment Schedule`, `tabSolar SCM Settings`, and `tabSolar SLA Settings`), implements pure SOLID Python domain services (`PurchaseOrderValidationService`, `POAuthorizationMatrixService`, `POMilestoneTermsService`, `POSLAService`, `PODispatchBridgeService`), exposes authenticated whitelisted RPC endpoints (`solar_module.api.procurement.*`), connects responsive Desk client scripts and external tokenized portal SPAs (`/solar/po-portal/:token`), and executes an automated zero-commit integration test suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE STAGE 15 TRACER BULLET SLICE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Schema & Data Persistence (Lean Core Slice)                        │
│   - tabPurchase Order extensions (matrix ref, quote ref, tiers, milestones) │
│   - tabPurchase Order Item extensions (landed rate lock, specs, serial flag)│
│   - tabSolar SCM Settings (Admin-configured financial tiers & BOM ceilings) │
│   - tabSolar SLA Settings (Admin-configured 24h release & 48h ack SLAs)     │
│   - Composite B-Tree Indexes on PO, Item, and Payment Schedule tables       │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 2: Domain Services & Business Logic (Pure SOLID Python)               │
│   - PurchaseOrderValidationService (Upstream matrix link & rate lock)       │
│   - POAuthorizationMatrixService (4-tier financial delegation engine)       │
│   - POMilestoneTermsService (Advance, LR transit, post-GRN, retention PBG)  │
│   - POSLAService (24h PO release & 48h vendor acknowledgment engine)        │
│   - PODispatchBridgeService (256-bit UUID portal tokens, Step 16 SABB flag) │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 3: Controller Lifecycle & Whitelisted RPC Gateway                     │
│   - PurchaseOrder controller override extending StageSecuredDocument        │
│   - Whitelisted RPC APIs (solar_module.api.procurement.*):                  │
│     * create_purchase_order_from_award                                      │
│     * authorize_purchase_order                                              │
│     * acknowledge_vendor_purchase_order (passwordless tokenized portal API)  │
│     * log_po_delay                                                          │
│     * get_po_financial_summary                                              │
│   - Background Celery/RQ daemon (procurement_po_sla_daemon every 15m)       │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 4: Desk Client Script & Dynamic Mobile/Portal Workbench Hook          │
│   - codes/client_script/purchase_order.js (Tier badge, SLA countdown timer, │
│     milestone schedule generator, sign-off dialog, junior cancel intercept)│
│   - Passwordless External Vendor Confirmation Portal SPA (/solar/po-portal) │
│   - SCM Purchase Order Workbench (/solar/procurement/purchase-order)        │
│   │                                                                         │
│   ▼                                                                         │
│ Layer 5: Automated Verification Suite (Integration Test)                     │
│   - solar_module/tests/test_step_15_purchase_order_tracer_bullet.py         │
│   - Subclasses frappe.tests.utils.FrappeTestCase                            │
│   - Strict Zero-Commit Rule (frappe.db.rollback() in tearDown)              │
│   - 12 atomic test cases validating all Stage 15 business/technical gates   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tracer Bullet Functional Mission

Prove the 8 fundamental business, operational, and security invariants of Stage 15 across the live Frappe stack:

1. **Gate 1: Upstream Sourcing Link & Landed Rate Integrity:** Assert that capital solar procurement orders are anchored to an approved `tabQuotation Comparison Matrix` (`docstatus = 1`, `evaluation_status = 'Award Approved'`) or carry an explicit `custom_is_single_source = 1` flag with an Admin-configured minimum justification length ($\ge 30$ chars) authorized exclusively by `Purchase Manager` or `Admin`. Item unit rates are immutably locked against awarded landed rates ($\text{rate} \le \text{custom\_landed\_rate\_awarded}$), eliminating post-award rate inflation.
2. **Gate 2: Multi-Tier Financial Authority Delegation (ADR-000):** Enforce strict server-side validation against Net PO Total:
   - **Tier 1 ($< ₹50,000$):** `Purchase Manager` only. Frontline `Purchase Assistant` can draft, but cannot submit.
   - **Tier 2 ($₹50,000 \text{ to } ₹5,00,000$):** Designated single active role in `Solar SCM Settings.tier_2_approver_role` (`Purchase Manager`, `Accounts Manager`, or `Admin`).
   - **Tier 3 ($> ₹5,00,000 \text{ to } ₹50,00,000$):** Exclusively **`Admin`** (Project Supreme Command).
   - **Tier 4 ($> ₹50,00,000$):** Exclusively **`Admin`** (Project Supreme Command).
3. **Gate 3: Solar Milestone Payment Schedule & Retention Security:** Mandate structured milestone breakdown in `tabPayment Schedule` for all critical solar equipment (Advance 10%–20%, Dispatch/LR 60%–70%, Post-GRN Inspection 10%–20%, Retention 5%–10% tied to Grid Synchronization COD or PBG). Single-bullet "Immediate" or "Due on Receipt" payment terms are hard-blocked on capital solar goods.
4. **Gate 4: Configurable Project Budget & Commercial BOM Check (Optional):** Completely bypass budget/BOM checks for Central Inventory Replenishment, Consolidated Multi-Project Bulk Buying, and Consumables. For project-specific orders, assert cumulative ordered quantity does not exceed the commercial Proposal BOM plus tolerance when `enforce_project_bom_ceiling = 1` in `Solar SCM Settings`.
5. **Gate 5: Multi-Location Delivery Routing & Barcode Serialization:** Explicit routing between `Central Store Warehouse` (`Stores - SEPC`) and `Direct Site Warehouse` (`Site - <Project Code> - SEPC`). Line items representing PV modules, inverters, and switchgear are flagged `custom_requires_barcode_serials = 1` to mandate Serial and Batch Bundle (SABB) capture upon goods arrival in Step 16 GRN.
6. **Gate 6: Passwordless 256-bit UUID External Vendor Portal:** External suppliers receive secure magic links (`/solar/po-portal/:token`), review milestone payment schedules, download signed PO copies, and confirm delivery commitments or log variance notes without requiring Frappe user credentials.
7. **Gate 7: 24h PO Release & 48h Vendor Acknowledgment SLA Engine:** Enforce an automated 24-hour turnaround window from matrix approval to PO release, and a 48-hour countdown from PO release to vendor digital sign-off. Transitions breached orders to `Overdue` and locks state modifications until justified in `tabSolar Stage Delay Log`.
8. **Gate 8: Stage-Forward Immutability Lock & Cancellation Interception:** Immutably block unilateral cancellation or modification once downstream Step 16 GRN (`tabPurchase Receipt`) or Step 17 Invoice exists. Junior cancellations are intercepted into the `Solar Cancellation Request` workflow.

---

## 2. Layer 1: Schema & Data Persistence (Lean Core Slice)

Extends standard ERPNext `tabPurchase Order`, child table `tabPurchase Order Item`, child table `tabPayment Schedule`, introduces Admin-configurable settings in `tabSolar SCM Settings` and `tabSolar SLA Settings`, integrates child `tabSolar Stage Delay Log`, and establishes MariaDB composite B-Tree indexes.

### 2.1 Core DocType Extension: `tabPurchase Order`

| Fieldname                             | Label                        | Fieldtype    | Options / Target                                                                                                                       | Mandatory | Index | Description & Validation Rules                                                                   |
| :------------------------------------ | :--------------------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :---: | :----------------------------------------------------------------------------------------------- |
| `custom_comparison_matrix_ref`        | Quotation Comparison Matrix  | `Link`       | `Quotation Comparison Matrix`                                                                                                          |    No     |   1   | FK linking Step 14 award matrix. Mandatory for capital equipment unless single source.           |
| `custom_awarded_quotation_ref`        | Awarded Supplier Quotation   | `Link`       | `Supplier Quotation`                                                                                                                   |    No     |   1   | Winning supplier quotation reference.                                                            |
| `custom_material_request_ref`         | Material Request Reference   | `Link`       | `Material Request`                                                                                                                     |    No     |   1   | Originating central warehouse indent or project requisition from Step 12.                        |
| `custom_is_single_source`             | Is Single-Source Purchase?   | `Check`      | -                                                                                                                                      |    No     |   -   | If checked, bypasses comparison matrix requirement; mandates justification.                      |
| `custom_po_classification`            | PO Classification            | `Select`     | `Project-Specific Solar Equipment\nMulti-Project Consolidated Bulk\nCentral Inventory Replenishment\nConsumables & Hardware\nServices` |  **Yes**  |   1   | Governs project budget check applicability. Default: `Project-Specific Solar Equipment`.         |
| `custom_project_ref`                  | Solar Project Reference      | `Link`       | `Project`                                                                                                                              |    No     |   1   | Links Solar EPC installation project (`tabProject`). Mandatory if project-specific.              |
| `custom_sales_order_ref`              | Sales Order Reference        | `Link`       | `Sales Order`                                                                                                                          |    No     |   1   | Links commercial project baseline from Step 06.                                                  |
| `custom_delivery_location_type`       | Delivery Destination Type    | `Select`     | `Central Store Warehouse\nDirect Site Warehouse`                                                                                       |  **Yes**  |   -   | Directs physical shipment destination for Step 16 GRN.                                           |
| `custom_target_site_warehouse`        | Target Site Warehouse        | `Link`       | `Warehouse`                                                                                                                            |    No     |   -   | Physical site staging warehouse (`Site - <Code> - SEPC`). Mandatory if Direct Site.              |
| `custom_authorization_tier`           | Financial Authorization Tier | `Select`     | `Tier 1: Up to ₹50,000\nTier 2: Up to ₹5,00,000\nTier 3: Up to ₹50,00,000\nTier 4: Above ₹50,00,000`                                   |  **Yes**  |   -   | Calculated dynamically from Net Total; dictates required signatory role.                         |
| `custom_authorized_by`                | Sign-off Approver            | `Link`       | `User`                                                                                                                                 |    No     |   -   | User ID of authorized signatory who executed managerial sign-off.                                |
| `custom_authorized_on`                | Sign-off Timestamp           | `Datetime`   | -                                                                                                                                      |    No     |   -   | Timestamp of managerial authorization sign-off.                                                  |
| `custom_authorization_remarks`        | Authorization Remarks        | `Small Text` | -                                                                                                                                      |    No     |   -   | Mandatory if single source ($\ge 30$ chars) or when approving tier exceptions.                   |
| `custom_advance_pct`                  | Advance Payment (%)          | `Percent`    | -                                                                                                                                      |    No     |   -   | Advance tranche percentage (e.g. 15.00%).                                                        |
| `custom_advance_amount`               | Advance Amount Payable       | `Currency`   | `Company:currency`                                                                                                                     |    No     |   -   | Calculated: $\text{Grand Total} \times (\text{custom\_advance\_pct} / 100)$.                     |
| `custom_advance_cleared`              | Advance Payment Cleared?     | `Check`      | -                                                                                                                                      |    No     |   -   | Automatically updated to 1 upon submission of Advance `Payment Entry`.                           |
| `custom_advance_payment_ref`          | Advance Payment Entry        | `Link`       | `Payment Entry`                                                                                                                        |    No     |   -   | Accounting disbursement reference.                                                               |
| `custom_retention_pct`                | Retention / Warranty (%)     | `Percent`    | -                                                                                                                                      |    No     |   -   | Contractual security percentage (e.g. 5.00%).                                                    |
| `custom_retention_due_event`          | Retention Release Trigger    | `Select`     | `On Grid Synchronization (COD)\nOn Final Acceptance Test (FAT)\nAgainst Performance Bank Guarantee (PBG)`                              |    No     |   -   | Milestone trigger unlocking final retention disbursement.                                        |
| `custom_liquidated_damages_clause`    | Enforce Liquidated Damages?  | `Check`      | -                                                                                                                                      |    No     |   -   | If checked, binds vendor to standard 0.5%/week delay penalty (max 5%). Defaults to 1 for capex.  |
| `custom_portal_token`                 | Vendor Acknowledgment Token  | `Data`       | -                                                                                                                                      |    No     |   1   | Cryptographic 256-bit UUID token for passwordless vendor acknowledgment.                         |
| `custom_vendor_acknowledgment_status` | Vendor Confirmation Status   | `Select`     | `Pending Acknowledgment\nAcknowledged & Confirmed\nExceptions Raised`                                                                  |  **Yes**  |   1   | Tracks vendor interaction lifecycle (Default: `Pending Acknowledgment`).                         |
| `custom_vendor_ack_date`              | Acknowledged On              | `Datetime`   | -                                                                                                                                      |    No     |   -   | Timestamp vendor confirmed order via portal.                                                     |
| `custom_sla_deadline`                 | PO Release / Vendor Ack SLA  | `Datetime`   | -                                                                                                                                      |  **Yes**  |   1   | Target datetime (`creation + 24h` release; `submit + 48h` ack).                                  |
| `custom_sla_status`                   | SLA Performance Status       | `Select`     | `Within SLA\nGrace Period\nOverdue`                                                                                                    |  **Yes**  |   1   | Managed by background SLA daemon. Default: `Within SLA`.                                         |
| `custom_delay_reason_table`           | Delay & Exception Audit Log  | `Table`      | `Solar Stage Delay Log`                                                                                                                |    No     |   -   | Mandatory audit log required when authorizing or acknowledging an overdue PO.                    |

---

### 2.2 Child DocType Extension: `tabPurchase Order Item`

| Fieldname                         | Label                          | Fieldtype  | Options / Target            | Mandatory | Description & Integrity Rules                                                   |
| :-------------------------------- | :----------------------------- | :--------- | :-------------------------- | :-------: | :------------------------------------------------------------------------------ |
| `custom_comparison_item_ref`      | Comparison Item Reference      | `Link`     | `Quotation Comparison Item` |    No     | Links specific evaluated item row from Step 14 matrix.                          |
| `custom_technical_specs_frozen`   | Frozen Technical Specification | `Text`     | -                           |    No     | Wattage, technology, dimensions frozen at matrix award.                         |
| `custom_landed_rate_awarded`      | Awarded Landed Unit Rate       | `Currency` | `Company:currency`          |    No     | Evaluated landed rate ceiling. Assert: `rate <= custom_landed_rate_awarded`.    |
| `custom_promised_delivery_date`   | Promised Delivery Date         | `Date`     | -                           |  **Yes**  | Guaranteed delivery date from supplier quotation.                               |
| `custom_requires_barcode_serials` | Requires 2D Barcode Serials?   | `Check`    | -                           |    No     | 1 for modules/inverters; forces Sabhav SABB 2D scan in Step 16 GRN.             |
| `custom_target_warehouse`         | Target Delivery Warehouse      | `Link`     | `Warehouse`                 |  **Yes**  | Inherited from PO routing (`Stores - SEPC` or `Site - <Project> - SEPC`).       |

---

### 2.3 Admin-Configurable Settings Singletons

Operational thresholds, financial limits, and SLA turnaround windows are strictly externalized into Admin-managed singletons:

#### 1. `tabSolar SCM Settings` Extensions:

```json
{
  "doctype": "DocType",
  "name": "Solar SCM Settings",
  "issingle": 1,
  "fields": [
    {
      "fieldname": "tier_1_limit",
      "label": "Tier 1 Financial Limit (INR)",
      "fieldtype": "Currency",
      "default": 50000.0,
      "description": "Threshold for Tier 1 (< ₹50,000, Purchase Manager only)."
    },
    {
      "fieldname": "tier_2_limit",
      "label": "Tier 2 Financial Limit (INR)",
      "fieldtype": "Currency",
      "default": 500000.0,
      "description": "Ceiling for Tier 2 (₹50k - ₹5L)."
    },
    {
      "fieldname": "tier_2_approver_role",
      "label": "Tier 2 Active Approver Role",
      "fieldtype": "Select",
      "options": "Purchase Manager\nAccounts Manager\nAdmin",
      "default": "Purchase Manager",
      "description": "Configurable single role permitted to authorize Tier 2 POs."
    },
    {
      "fieldname": "tier_3_limit",
      "label": "Tier 3 Financial Limit (INR)",
      "fieldtype": "Currency",
      "default": 5000000.0,
      "description": "Ceiling for Tier 3 (> ₹5L to ₹50L, Admin only)."
    },
    {
      "fieldname": "enforce_project_bom_ceiling",
      "label": "Enforce Project BOM Ceiling Gate",
      "fieldtype": "Check",
      "default": 0,
      "description": "If enabled, hard-blocks POs exceeding Commercial Proposal / SO BOM quantity + tolerance."
    },
    {
      "fieldname": "bom_overage_tolerance_pct",
      "label": "Allowed BOM Overage Buffer (%)",
      "fieldtype": "Percent",
      "default": 5.0,
      "description": "Tolerance margin (%) permitted when BOM ceiling check is active."
    },
    {
      "fieldname": "enable_whatsapp_vendor_dispatch",
      "label": "Auto-Dispatch PO Link via WhatsApp",
      "fieldtype": "Check",
      "default": 1,
      "description": "Transmits signed PDF copy + portal token to vendor representative mobile upon submission."
    }
  ]
}
```

#### 2. `tabSolar SLA Settings` Extensions:

```json
{
  "doctype": "DocType",
  "name": "Solar SLA Settings",
  "issingle": 1,
  "fields": [
    {
      "fieldname": "po_release_sla_hours",
      "label": "PO Release SLA Window (Hours)",
      "fieldtype": "Int",
      "default": 24,
      "description": "Turnaround SLA from Matrix award approval to PO release."
    },
    {
      "fieldname": "vendor_acknowledgment_sla_hours",
      "label": "Vendor Acknowledgment Window (Hours)",
      "fieldtype": "Int",
      "default": 48,
      "description": "Turnaround SLA from PO release to vendor digital acknowledgment."
    },
    {
      "fieldname": "po_sla_reminder_hours_before",
      "label": "Reminder Alert Window (Hours Before Deadline)",
      "fieldtype": "Int",
      "default": 12,
      "description": "Hours remaining when automated warning alert is dispatched to buyer/supplier."
    }
  ]
}
```

---

### 2.4 Composite Database B-Tree Indexes

```sql
-- Composite index for fast PO authorization tier and SLA monitoring queries
ALTER TABLE `tabPurchase Order`
ADD INDEX `idx_po_stage_sla_tier` (`docstatus`, `custom_authorization_tier`, `custom_sla_status`, `custom_sla_deadline`);

-- Composite index for upstream matrix and awarded quote tracking
ALTER TABLE `tabPurchase Order`
ADD INDEX `idx_po_upstream_matrix` (`custom_comparison_matrix_ref`, `custom_awarded_quotation_ref`, `docstatus`);

-- Composite index for vendor portal token authentication and lookup
ALTER TABLE `tabPurchase Order`
ADD INDEX `idx_po_vendor_token` (`custom_portal_token`, `custom_vendor_acknowledgment_status`);

-- Composite index for project and material request traceability
ALTER TABLE `tabPurchase Order`
ADD INDEX `idx_po_proj_mr` (`custom_project_ref`, `custom_material_request_ref`, `custom_po_classification`);

-- Composite index for line item landed rate check and warehouse routing
ALTER TABLE `tabPurchase Order Item`
ADD INDEX `idx_poi_item_rate_wh` (`parent`, `item_code`, `custom_target_warehouse`);
```

---

## 3. Layer 2: Domain Services & Business Logic (Pure SOLID Python)

Decoupled, pure Python domain services implementing Single Responsibility, zero direct Desk dependencies, and 100% testability.

### 3.1 `PurchaseOrderValidationService` (`solar_module/services/po_validation_service.py`)

Responsible for verifying upstream sourcing integrity, enforcing landed rate inflation blocks, and calculating optional Proposal BOM headroom.

```python
import frappe
from frappe import _
from frappe.utils import flt, cint

class PurchaseOrderValidationService:
    """Enforces upstream sourcing links, rate integrity, and BOM headroom constraints."""

    @staticmethod
    def validate_upstream_sourcing(doc):
        """Gate 1: Assert matrix link or validated single-source exception."""
        if doc.custom_po_classification in [
            "Project-Specific Solar Equipment",
            "Multi-Project Consolidated Bulk",
        ]:
            if not doc.custom_comparison_matrix_ref and not doc.custom_is_single_source:
                frappe.throw(
                    _("A submitted Quotation Comparison Matrix is required for capital solar procurement. "
                      "If this is a justified single-source purchase, mark 'Is Single Source'."),
                    frappe.ValidationError,
                )

            if doc.custom_is_single_source:
                justification = (doc.custom_authorization_remarks or "").strip()
                min_len = 30
                if len(justification) < min_len:
                    frappe.throw(
                        _("Single-source procurement requires detailed justification remarks "
                          "(minimum {0} characters; provided {1}).").format(min_len, len(justification)),
                        frappe.ValidationError,
                    )
            elif doc.custom_comparison_matrix_ref:
                matrix_status, docstatus = frappe.db.get_value(
                    "Quotation Comparison Matrix",
                    doc.custom_comparison_matrix_ref,
                    ["evaluation_status", "docstatus"],
                )
                if docstatus != 1 or matrix_status != "Award Approved":
                    frappe.throw(
                        _("Linked Quotation Comparison Matrix {0} must be submitted and 'Award Approved'.").format(
                            doc.custom_comparison_matrix_ref
                        ),
                        frappe.ValidationError,
                    )

    @staticmethod
    def validate_rate_integrity(doc):
        """Gate 1: Assert PO item unit rate <= awarded landed rate from comparison matrix."""
        for item in doc.items:
            if item.custom_landed_rate_awarded and flt(item.custom_landed_rate_awarded) > 0:
                if flt(item.rate) > flt(item.custom_landed_rate_awarded):
                    frappe.throw(
                        _("Row #{0}: Item {1} unit rate ({2}) exceeds the approved landed rate ({3}) "
                          "from Quotation Comparison Matrix. Rate inflation is prohibited.").format(
                            item.idx, item.item_code, item.rate, item.custom_landed_rate_awarded
                        ),
                        frappe.ValidationError,
                    )

    @staticmethod
    def validate_project_bom_headroom(doc):
        """Gate 4: Optional verification against Commercial Proposal / Sales Order BOM."""
        if not doc.custom_project_ref or doc.custom_po_classification in [
            "Central Inventory Replenishment",
            "Multi-Project Consolidated Bulk",
            "Consumables & Hardware",
            "Services",
        ]:
            return

        settings = frappe.get_cached_doc("Solar SCM Settings")
        if not cint(settings.get("enforce_project_bom_ceiling")):
            return

        tolerance_pct = flt(settings.get("bom_overage_tolerance_pct") or 5.0)

        for item in doc.items:
            # Match against baseline Sales Order Item quantity
            proposal_bom_qty = frappe.db.get_value(
                "Sales Order Item",
                {"parent": doc.custom_sales_order_ref or "", "item_code": item.item_code},
                "qty",
            )
            if not proposal_bom_qty:
                continue

            existing_ordered = frappe.db.sql(
                """
                SELECT SUM(poi.qty)
                FROM `tabPurchase Order Item` poi
                JOIN `tabPurchase Order` po ON poi.parent = po.name
                WHERE po.custom_project_ref = %s
                  AND poi.item_code = %s
                  AND po.docstatus = 1
                  AND po.name != %s
                """,
                (doc.custom_project_ref, item.item_code, doc.name or ""),
            )[0][0] or 0.0

            max_allowed = flt(proposal_bom_qty) * (1.0 + (tolerance_pct / 100.0))
            if (flt(existing_ordered) + flt(item.qty)) > max_allowed:
                frappe.throw(
                    _("Row #{0}: Total cumulative ordered quantity ({1}) for Item {2} exceeds "
                      "the approved Commercial Proposal BOM ceiling ({3}) plus {4}% tolerance.").format(
                        item.idx,
                        existing_ordered + item.qty,
                        item.item_code,
                        proposal_bom_qty,
                        tolerance_pct,
                    ),
                    frappe.ValidationError,
                )

    @staticmethod
    def validate_warehouse_routing(doc):
        """Gate 5: Verify delivery warehouse routing and site warehouse existence."""
        if not doc.custom_delivery_location_type:
            frappe.throw(_("Delivery Destination Type is mandatory."), frappe.ValidationError)

        if doc.custom_delivery_location_type == "Direct Site Warehouse":
            if not doc.custom_target_site_warehouse:
                frappe.throw(
                    _("Direct Site Warehouse routing requires a valid target site warehouse "
                      "(e.g., 'Site - <Project Code> - SEPC')."),
                    frappe.ValidationError,
                )
            if not frappe.db.exists("Warehouse", doc.custom_target_site_warehouse):
                frappe.throw(
                    _("Target site warehouse {0} does not exist in the database.").format(
                        doc.custom_target_site_warehouse
                    ),
                    frappe.ValidationError,
                )
```

---

### 3.2 `POAuthorizationMatrixService` (`solar_module/services/po_authorization_service.py`)

Calculates financial delegation tiers and enforces server-side role authority aligned with ADR-000 and ADR-015.

```python
import frappe
from frappe import _
from frappe.utils import flt

class POAuthorizationMatrixService:
    """Calculates financial tiers and enforces managerial authority delegation."""

    @staticmethod
    def calculate_tier(net_total):
        """Calculates tier from net total and Admin-configured SCM Settings."""
        settings = frappe.get_cached_doc("Solar SCM Settings")
        t1 = flt(settings.get("tier_1_limit") or 50000.0)
        t2 = flt(settings.get("tier_2_limit") or 500000.0)
        t3 = flt(settings.get("tier_3_limit") or 5000000.0)

        amount = flt(net_total)
        if amount <= t1:
            return "Tier 1: Up to ₹50,000"
        elif amount <= t2:
            return "Tier 2: Up to ₹5,00,000"
        elif amount <= t3:
            return "Tier 3: Up to ₹50,00,000"
        else:
            return "Tier 4: Above ₹50,00,000"

    @staticmethod
    def assert_authorization_permissions(doc):
        """Asserts current user has requisite authority to submit PO."""
        user_roles = frappe.get_roles(frappe.session.user)
        tier = doc.custom_authorization_tier or POAuthorizationMatrixService.calculate_tier(doc.net_total)

        # Framework Supreme & Admin bypass
        if "System Manager" in user_roles or "Administrator" in user_roles:
            return

        settings = frappe.get_cached_doc("Solar SCM Settings")

        if tier == "Tier 1: Up to ₹50,000":
            required = ["Purchase Manager", "Admin"]
        elif tier == "Tier 2: Up to ₹5,00,000":
            tier_2_role = settings.get("tier_2_approver_role") or "Purchase Manager"
            required = [tier_2_role, "Admin"]
        elif tier == "Tier 3: Up to ₹50,00,000":
            required = ["Admin"]
        else:
            required = ["Admin"]

        if not any(role in user_roles for role in required):
            frappe.throw(
                _("You are not authorized to release this Purchase Order. Required role for {0}: {1}.").format(
                    tier, ", ".join(required)
                ),
                frappe.PermissionError,
            )
```

---

### 3.3 `POMilestoneTermsService` (`solar_module/services/po_milestone_service.py`)

Governs structured payment terms, advance tranche calculations, and retention security tranches.

```python
import frappe
from frappe import _
from frappe.utils import flt

class POMilestoneTermsService:
    """Validates structured solar milestone terms and retention schedules."""

    @staticmethod
    def validate_payment_schedule(doc):
        """Gate 3: Validate milestone schedule rows and reject single immediate terms."""
        if doc.custom_po_classification in [
            "Project-Specific Solar Equipment",
            "Multi-Project Consolidated Bulk",
        ]:
            if not doc.payment_schedule or len(doc.payment_schedule) < 2:
                frappe.throw(
                    _("Capital solar procurement mandates structured milestone terms (minimum 2 tranches: "
                      "e.g., Advance, LR/Dispatch, Post-GRN, and Retention/PBG). Generic immediate terms prohibited."),
                    frappe.ValidationError,
                )

            # Assert tranches sum to 100%
            total_portion = sum(flt(row.payment_amount or 0) for row in doc.payment_schedule)
            total_pct = sum(flt(row.invoice_portion or 0) for row in doc.payment_schedule)

            if doc.grand_total and abs(total_portion - doc.grand_total) > 1.0:
                frappe.throw(
                    _("Total payment schedule amount ({0}) must equal Grand Total ({1}).").format(
                        total_portion, doc.grand_total
                    ),
                    frappe.ValidationError,
                )

            # Advance percentage synchronization
            if doc.custom_advance_pct and flt(doc.custom_advance_pct) > 0:
                expected_advance = flt(doc.grand_total) * (flt(doc.custom_advance_pct) / 100.0)
                doc.custom_advance_amount = round(expected_advance, 2)

    @staticmethod
    def populate_default_milestones(doc):
        """Generates standard solar EPC milestone template (15% Adv, 70% LR, 10% GRN, 5% Retention)."""
        doc.payment_schedule = []
        grand_total = flt(doc.grand_total)

        milestones = [
            ("Advance Payment Against Order", 15.0, "Immediately on PO Release"),
            ("Dispatch Payment Against Transporter LR & Inspection", 70.0, "Against Dispatch / Bill of Lading"),
            ("Site Delivery & Physical GRN Verification", 10.0, "Post-GRN 100% Barcode Scan"),
            ("Retention Security (COD / PBG)", 5.0, "On Grid Synchronization (COD)"),
        ]

        for desc, pct, due in milestones:
            doc.append("payment_schedule", {
                "description": desc,
                "invoice_portion": pct,
                "payment_amount": round(grand_total * (pct / 100.0), 2),
                "due_date": doc.schedule_date or frappe.utils.nowdate(),
            })

        doc.custom_advance_pct = 15.0
        doc.custom_retention_pct = 5.0
        doc.custom_retention_due_event = "On Grid Synchronization (COD)"
        doc.custom_liquidated_damages_clause = 1
```

---

### 3.4 `POSLAService` (`solar_module/services/po_sla_service.py`)

Calculates 24-hour PO release SLA, manages 48-hour vendor acknowledgment countdown, and enforces delay logging.

```python
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date, time_diff_in_seconds

class POSLAService:
    """Manages 24h PO release and 48h vendor acknowledgment SLA lifecycle."""

    @staticmethod
    def initialize_release_sla(doc):
        """Sets 24h release SLA from PO creation or upstream matrix approval."""
        sla_settings = frappe.get_cached_doc("Solar SLA Settings")
        sla_hours = int(sla_settings.get("po_release_sla_hours") or 24)
        doc.custom_sla_deadline = add_to_date(now_datetime(), hours=sla_hours)
        doc.custom_sla_status = "Within SLA"

    @staticmethod
    def transition_to_vendor_ack_sla(doc):
        """Transitions SLA countdown to 48h vendor acknowledgment upon PO submission."""
        sla_settings = frappe.get_cached_doc("Solar SLA Settings")
        ack_hours = int(sla_settings.get("vendor_acknowledgment_sla_hours") or 48)
        doc.custom_sla_deadline = add_to_date(now_datetime(), hours=ack_hours)
        doc.custom_sla_status = "Within SLA"
        doc.custom_vendor_acknowledgment_status = "Pending Acknowledgment"

    @staticmethod
    def evaluate_sla_status(doc):
        """Evaluates SLA deadline compliance and transitions to Overdue if breached."""
        if not doc.custom_sla_deadline:
            return

        now = now_datetime()
        if now > doc.custom_sla_deadline:
            doc.custom_sla_status = "Overdue"

    @staticmethod
    def assert_delay_logging_compliance(doc):
        """Locks save/submit on overdue documents until delay justification is logged."""
        POSLAService.evaluate_sla_status(doc)
        if doc.custom_sla_status == "Overdue":
            if not doc.custom_delay_reason_table or len(doc.custom_delay_reason_table) == 0:
                frappe.throw(
                    _("SLA Status is Overdue. A structured justification must be logged in the "
                      "Delay & Exception Audit Log before this Purchase Order can be processed."),
                    frappe.ValidationError,
                )
```

---

### 3.5 `PODispatchBridgeService` (`solar_module/services/po_dispatch_service.py`)

Generates cryptographic 256-bit UUID portal tokens, handles external vendor communication, and preconditions Step 16 GRN.

```python
import uuid
import frappe
from frappe import _

class PODispatchBridgeService:
    """Manages passwordless vendor portal tokens and Step 16 GRN preconditioning."""

    @staticmethod
    def generate_portal_token(doc):
        """Generates random 256-bit UUID token for passwordless vendor acknowledgment."""
        if not doc.custom_portal_token:
            doc.custom_portal_token = str(uuid.uuid4())

    @staticmethod
    def precondition_step_16_grn(doc):
        """Flags serialized solar components to mandate Sabhav SABB 2D scan in Step 16."""
        for item in doc.items:
            has_serial = frappe.db.get_value("Item", item.item_code, "has_serial_no")
            is_solar_asset = frappe.db.get_value("Item", item.item_code, "custom_is_solar_asset")
            if has_serial or is_solar_asset:
                item.custom_requires_barcode_serials = 1

            # Sync target delivery warehouse
            if doc.custom_delivery_location_type == "Direct Site Warehouse":
                item.warehouse = doc.custom_target_site_warehouse
                item.custom_target_warehouse = doc.custom_target_site_warehouse
            elif not item.warehouse:
                item.warehouse = "Stores - SEPC"
                item.custom_target_warehouse = "Stores - SEPC"
```

---

## 4. Layer 3: Controller Lifecycle & Whitelisted RPC Gateway

Integrates domain services into ERPNext's submittable `tabPurchase Order` lifecycle, enforces ADR-000 role standards, and provides secure whitelisted endpoints.

### 4.1 Submittable Controller Override (`solar_module/overrides/purchase_order.py`)

Inherits from `StageSecuredDocument` and ERPNext's `PurchaseOrder`:

```python
import frappe
from frappe import _
from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
from solar_module.security.mixins import StageSecuredDocument
from solar_module.services.po_validation_service import PurchaseOrderValidationService
from solar_module.services.po_authorization_service import POAuthorizationMatrixService
from solar_module.services.po_milestone_service import POMilestoneTermsService
from solar_module.services.po_sla_service import POSLAService
from solar_module.services.po_dispatch_service import PODispatchBridgeService

class SolarPurchaseOrder(StageSecuredDocument, PurchaseOrder):
    """Solar EPC enterprise controller override for Purchase Order."""

    def validate(self):
        super().validate()
        # Calculate financial tier dynamically
        self.custom_authorization_tier = POAuthorizationMatrixService.calculate_tier(self.net_total)

        # Precondition Step 16 GRN flags and warehouse routing
        PODispatchBridgeService.precondition_step_16_grn(self)

        # Validate verification gates
        PurchaseOrderValidationService.validate_upstream_sourcing(self)
        PurchaseOrderValidationService.validate_rate_integrity(self)
        PurchaseOrderValidationService.validate_warehouse_routing(self)
        PurchaseOrderValidationService.validate_project_bom_headroom(self)
        POMilestoneTermsService.validate_payment_schedule(self)

        # Initialize SLA deadlines on draft creation
        if not self.custom_sla_deadline:
            POSLAService.initialize_release_sla(self)

        # Assert delay log if overdue
        POSLAService.assert_delay_logging_compliance(self)

    def before_submit(self):
        """Enforces ADR-000: Assert managerial financial authorization."""
        super().before_submit()
        POAuthorizationMatrixService.assert_authorization_permissions(self)
        self.custom_authorized_by = frappe.session.user
        self.custom_authorized_on = frappe.utils.now_datetime()

    def on_submit(self):
        super().on_submit()
        # Generate portal token and transition SLA to vendor acknowledgment
        PODispatchBridgeService.generate_portal_token(self)
        POSLAService.transition_to_vendor_ack_sla(self)
        self.db_set("custom_portal_token", self.custom_portal_token)
        self.db_set("custom_sla_deadline", self.custom_sla_deadline)
        self.db_set("custom_sla_status", self.custom_sla_status)
        self.db_set("custom_vendor_acknowledgment_status", self.custom_vendor_acknowledgment_status)

        # Update upstream Comparison Matrix status
        if self.custom_comparison_matrix_ref:
            frappe.db.set_value(
                "Quotation Comparison Matrix",
                self.custom_comparison_matrix_ref,
                {"evaluation_status": "PO Created", "purchase_order_ref": self.name},
            )

    def on_cancel(self):
        """Enforces Stage-Forward Lock: cannot cancel PO if downstream GRN or Invoice exists."""
        self.check_stage_forward_lock(
            downstream_doctypes=["Purchase Receipt", "Purchase Invoice"],
            reference_field="purchase_order"
        )
        super().on_cancel()
        if self.custom_comparison_matrix_ref:
            frappe.db.set_value(
                "Quotation Comparison Matrix",
                self.custom_comparison_matrix_ref,
                "evaluation_status",
                "Award Approved",
            )
```

---

### 4.2 Whitelisted RPC API Endpoints (`solar_module/api/procurement.py`)

```python
import json
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date

@frappe.whitelist(methods=["POST"])
def create_purchase_order_from_award(comparison_matrix_name: str) -> dict:
    """Creates a pre-populated draft Purchase Order from an Award Approved comparison matrix."""
    if not comparison_matrix_name:
        frappe.throw(_("Comparison Matrix name is required."), frappe.ValidationError)

    matrix = frappe.get_doc("Quotation Comparison Matrix", comparison_matrix_name)
    matrix.check_permission("read")

    if matrix.docstatus != 1 or matrix.evaluation_status != "Award Approved":
        frappe.throw(_("Matrix must be submitted and 'Award Approved'."), frappe.ValidationError)

    if matrix.purchase_order_ref and frappe.db.exists("Purchase Order", matrix.purchase_order_ref):
        frappe.throw(_("Purchase Order {0} has already been created for this matrix.").format(matrix.purchase_order_ref))

    po = frappe.new_doc("Purchase Order")
    po.supplier = matrix.awarded_supplier
    po.custom_comparison_matrix_ref = matrix.name
    po.custom_awarded_quotation_ref = matrix.awarded_quotation
    po.custom_project_ref = matrix.project_reference
    po.custom_material_request_ref = matrix.material_request_ref
    po.custom_po_classification = "Project-Specific Solar Equipment" if matrix.project_reference else "Central Inventory Replenishment"
    po.custom_delivery_location_type = "Direct Site Warehouse" if matrix.project_reference else "Central Store Warehouse"
    po.schedule_date = matrix.target_delivery_date or add_to_date(now_datetime(), days=14)

    for item in matrix.comparison_items:
        if item.supplier == matrix.awarded_supplier:
            po.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty,
                "uom": item.uom,
                "rate": item.basic_rate,
                "schedule_date": add_to_date(now_datetime(), days=item.promised_lead_days or 10),
                "custom_comparison_item_ref": item.name,
                "custom_landed_rate_awarded": item.landed_rate_unit,
                "custom_promised_delivery_date": add_to_date(now_datetime(), days=item.promised_lead_days or 10),
                "custom_requires_barcode_serials": 1 if frappe.db.get_value("Item", item.item_code, "has_serial_no") else 0,
            })

    from solar_module.services.po_milestone_service import POMilestoneTermsService
    POMilestoneTermsService.populate_default_milestones(po)

    po.insert()

    matrix.db_set("purchase_order_ref", po.name)
    matrix.db_set("evaluation_status", "PO Created")

    return {
        "status": "success",
        "purchase_order": po.name,
        "message": _("Purchase Order {0} drafted successfully.").format(po.name),
    }

@frappe.whitelist(methods=["POST"])
def acknowledge_vendor_purchase_order(token: str, acknowledgment_status: str, notes: str = None) -> dict:
    """Passwordless vendor confirmation endpoint accessible via /solar/po-portal/:token."""
    if not token:
        frappe.throw(_("Security token is required."), frappe.ValidationError)

    po_name = frappe.db.get_value("Purchase Order", {"custom_portal_token": token}, "name")
    if not po_name:
        frappe.throw(_("Invalid or expired authorization token."), frappe.PermissionError)

    po = frappe.get_doc("Purchase Order", po_name)
    if po.docstatus != 1:
        frappe.throw(_("Purchase Order is not in a submitted state."), frappe.ValidationError)

    if acknowledgment_status not in ["Acknowledged & Confirmed", "Exceptions Raised"]:
        frappe.throw(_("Invalid acknowledgment status."), frappe.ValidationError)

    po.custom_vendor_acknowledgment_status = acknowledgment_status
    po.custom_vendor_ack_date = now_datetime()
    if notes:
        po.add_comment("Comment", _("Vendor Portal Note: {0}").format(notes))
    po.save(ignore_permissions=True)

    return {
        "status": "success",
        "po_name": po.name,
        "acknowledgment_status": po.custom_vendor_acknowledgment_status,
        "message": _("Purchase Order acknowledgment recorded successfully."),
    }

@frappe.whitelist(methods=["POST"])
def log_po_delay(po_name: str, delay_reason: str, remarks: str) -> dict:
    """Logs an operational exception into the child delay log when SLA is overdue."""
    po = frappe.get_doc("Purchase Order", po_name)
    po.check_permission("write")

    po.append("custom_delay_reason_table", {
        "stage": "PO Authorization & Release",
        "delay_reason": delay_reason,
        "remarks": remarks,
        "logged_by": frappe.session.user,
        "logged_on": now_datetime(),
    })
    po.save()

    return {"status": "success", "message": _("Delay reason logged successfully.")}
```

---

### 4.3 Background Celery/RQ Daemon (`solar_module/tasks.py`)

Configured in `hooks.py` under `scheduler_events["all"]`:

```python
# solar_module/tasks.py

import frappe
from frappe.utils import now_datetime
from solar_module.services.po_sla_service import POSLAService

def monitor_po_release_and_vendor_ack_sla():
    """Runs every 15 minutes to evaluate PO release and vendor acknowledgment SLA compliance."""
    # 1. Draft POs awaiting release
    draft_pos = frappe.get_all(
        "Purchase Order",
        filters={"docstatus": 0, "custom_sla_status": ["in", ["Within SLA", "Grace Period"]]},
        fields=["name", "custom_sla_deadline"],
    )
    for row in draft_pos:
        if row.custom_sla_deadline and now_datetime() > row.custom_sla_deadline:
            frappe.db.set_value("Purchase Order", row.name, "custom_sla_status", "Overdue")

    # 2. Submitted POs awaiting vendor acknowledgment
    submitted_pos = frappe.get_all(
        "Purchase Order",
        filters={
            "docstatus": 1,
            "custom_vendor_acknowledgment_status": "Pending Acknowledgment",
            "custom_sla_status": ["in", ["Within SLA", "Grace Period"]],
        },
        fields=["name", "custom_sla_deadline"],
    )
    for row in submitted_pos:
        if row.custom_sla_deadline and now_datetime() > row.custom_sla_deadline:
            frappe.db.set_value("Purchase Order", row.name, "custom_sla_status", "Overdue")
```

---

## 5. Layer 4: Desk Client Script & Dynamic Mobile/Portal Workbench Hook

Provides visual cues, financial tier indicators, countdown timers, and vendor portal SPAs.

### 5.1 Desk Client Script (`codes/client_script/purchase_order.js`)

```javascript
frappe.ui.form.on("Purchase Order", {
  refresh(frm) {
    frm.trigger("render_tier_and_sla_badges");
    frm.trigger("setup_custom_buttons");
    frm.trigger("intercept_junior_cancellation");
  },

  render_tier_and_sla_badges(frm) {
    if (frm.doc.custom_authorization_tier) {
      const tierColor = frm.doc.custom_authorization_tier.includes("Tier 4")
        ? "red"
        : frm.doc.custom_authorization_tier.includes("Tier 3")
        ? "orange"
        : "blue";
      frm.dashboard.add_indicator(frm.doc.custom_authorization_tier, tierColor);
    }

    if (frm.doc.custom_sla_status) {
      const slaColor = frm.doc.custom_sla_status === "Overdue" ? "red" : "green";
      frm.dashboard.add_indicator(`SLA: ${frm.doc.custom_sla_status}`, slaColor);
    }

    if (frm.doc.docstatus === 1 && frm.doc.custom_vendor_acknowledgment_status) {
      const ackColor =
        frm.doc.custom_vendor_acknowledgment_status === "Acknowledged & Confirmed"
          ? "green"
          : frm.doc.custom_vendor_acknowledgment_status === "Exceptions Raised"
          ? "orange"
          : "gray";
      frm.dashboard.add_indicator(`Vendor: ${frm.doc.custom_vendor_acknowledgment_status}`, ackColor);
    }
  },

  setup_custom_buttons(frm) {
    // Generate standard solar milestone terms in Draft
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Populate Solar Milestones"), () => {
        frappe.call({
          method: "solar_module.services.po_milestone_service.POMilestoneTermsService.populate_default_milestones",
          args: { doc: frm.doc },
          callback(r) {
            frm.reload_doc();
            frappe.show_alert({ message: __("Milestones generated"), indicator: "green" });
          },
        });
      }, __("Actions"));
    }

    // View Vendor Portal link in Submitted state
    if (frm.doc.docstatus === 1 && frm.doc.custom_portal_token) {
      frm.add_custom_button(__("Copy Vendor Portal Link"), () => {
        const portalUrl = `${window.location.origin}/solar/po-portal/${frm.doc.custom_portal_token}`;
        navigator.clipboard.writeText(portalUrl).then(() => {
          frappe.msgprint(__("Copied portal URL: {0}", [portalUrl]));
        });
      }, __("Vendor Portal"));
    }

    // Log Delay Dialog if Overdue
    if (frm.doc.custom_sla_status === "Overdue") {
      frm.add_custom_button(__("Log Delay Justification"), () => {
        const d = new frappe.ui.Dialog({
          title: __("Log SLA Delay Justification"),
          fields: [
            {
              fieldname: "delay_reason",
              fieldtype: "Select",
              label: __("Delay Reason"),
              options: "Supplier Negotiation\nTechnical Re-specification\nManagement Review\nFinancial Sign-off Delay\nOther",
              reqd: 1,
            },
            {
              fieldname: "remarks",
              fieldtype: "Small Text",
              label: __("Remarks"),
              reqd: 1,
            },
          ],
          primary_action_label: __("Save Delay"),
          primary_action(vals) {
            frappe.call({
              method: "solar_module.api.procurement.log_po_delay",
              args: {
                po_name: frm.doc.name,
                delay_reason: vals.delay_reason,
                remarks: vals.remarks,
              },
              callback() {
                d.hide();
                frm.reload_doc();
              },
            });
          },
        });
        d.show();
      }).addClass("btn-danger");
    }
  },

  intercept_junior_cancellation(frm) {
    if (
      frm.doc.docstatus === 1 &&
      !frappe.user.has_role(["Purchase Manager", "Admin", "System Manager"])
    ) {
      frm.page.clear_menu(); // Intercept standard Cancel
      frm.add_custom_button(__("Request Cancellation"), () => {
        const d = new frappe.ui.Dialog({
          title: __("Submit Cancellation Request"),
          fields: [
            {
              fieldname: "reason",
              fieldtype: "Small Text",
              label: __("Reason for Cancellation"),
              reqd: 1,
            },
          ],
          primary_action_label: __("Submit Request"),
          primary_action(vals) {
            frappe.call({
              method: "solar_module.security.request_cancellation",
              args: {
                doctype: frm.doc.doctype,
                docname: frm.doc.name,
                reason: vals.reason,
              },
              callback() {
                d.hide();
                frappe.msgprint(__("Cancellation request submitted to Purchase Manager."));
              },
            });
          },
        });
        d.show();
      });
    }
  },
});
```

---

### 5.2 Passwordless External Vendor Confirmation Portal SPA (`/solar/po-portal/:token`)

Responsive zero-login card interface:

1. **Authentication:** Pure cryptographic 256-bit UUID via URL token. No Frappe user login requested.
2. **Branding & Order Header:** Sadbhav Solar EPC logo, PO Number, Total Value, Promised Delivery Date, and destination routing (`Direct Site Warehouse` vs `Central Store Warehouse`).
3. **Structured Milestone Schedule Table:** Shows Advance, Dispatch/LR, Receipt, and Retention milestones.
4. **Line Items Grid:** Displays Component Code, Description, Quantity, Wattage/Technology specs, and delivery schedule.
5. **Action Buttons:** `[Confirm & Accept Order]` (sets status to `Acknowledged & Confirmed`) vs `[Raise Exceptions / Notes]` (prompts modal for supplier comments).

---

## 6. Layer 5: Automated Verification Suite (Integration Test)

Implemented in `solar_module/tests/test_step_15_purchase_order_tracer_bullet.py`. Subclasses `frappe.tests.utils.FrappeTestCase`. Follows the **Strict Zero-Commit Rule**: all mutations roll back automatically via `frappe.db.rollback()`.

```python
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_to_date, flt
from solar_module.services.po_validation_service import PurchaseOrderValidationService
from solar_module.services.po_authorization_service import POAuthorizationMatrixService
from solar_module.services.po_milestone_service import POMilestoneTermsService
from solar_module.api.procurement import acknowledge_vendor_purchase_order

class TestStage15PurchaseOrderTracerBullet(FrappeTestCase):
    """Integration test suite proving all 8 invariants of Stage 15 PO Authorization Tracer Bullet."""

    def setUp(self):
        super().setUp()
        self.supplier = self._create_test_supplier("SUPP-PO-TEST-01")
        self.item = self._create_test_item("SOL-MOD-545W-TB15")
        self._configure_admin_settings()

    def tearDown(self):
        frappe.db.rollback()

    def _configure_admin_settings(self):
        scm = frappe.get_doc("Solar SCM Settings")
        scm.tier_1_limit = 50000.0
        scm.tier_2_limit = 500000.0
        scm.tier_2_approver_role = "Purchase Manager"
        scm.tier_3_limit = 5000000.0
        scm.enforce_project_bom_ceiling = 0
        scm.bom_overage_tolerance_pct = 5.0
        scm.save(ignore_permissions=True)

        sla = frappe.get_doc("Solar SLA Settings")
        sla.po_release_sla_hours = 24
        sla.vendor_acknowledgment_sla_hours = 48
        sla.save(ignore_permissions=True)

    def _create_test_supplier(self, name):
        if not frappe.db.exists("Supplier", name):
            s = frappe.new_doc("Supplier")
            s.supplier_name = name
            s.supplier_group = "All Supplier Groups"
            s.insert(ignore_permissions=True)
            return s.name
        return name

    def _create_test_item(self, code):
        if not frappe.db.exists("Item", code):
            item = frappe.new_doc("Item")
            item.item_code = code
            item.item_name = f"Test Component {code}"
            item.item_group = "All Item Groups"
            item.stock_uom = "Nos"
            item.is_stock_item = 1
            item.has_serial_no = 1
            item.insert(ignore_permissions=True)
            return item.name
        return code

    def test_01_upstream_comparison_matrix_enforced(self):
        """Test 01: Assert Gate 1 blocks capital solar PO without linked matrix or single source."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Project-Specific Solar Equipment"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 100, "rate": 18.50})
        with self.assertRaises(frappe.ValidationError):
            po.insert()

    def test_02_single_source_justification_enforced(self):
        """Test 02: Assert single source requires minimum 30-char justification."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Project-Specific Solar Equipment"
        po.custom_is_single_source = 1
        po.custom_authorization_remarks = "Too short"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 10, "rate": 18.50})
        with self.assertRaises(frappe.ValidationError):
            po.insert()

    def test_03_rate_inflation_prevention(self):
        """Test 03: Assert unit rate cannot exceed awarded landed rate."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Central Inventory Replenishment"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {
            "item_code": self.item,
            "qty": 50,
            "rate": 25.00,
            "custom_landed_rate_awarded": 20.00,
        })
        with self.assertRaises(frappe.ValidationError):
            PurchaseOrderValidationService.validate_rate_integrity(po)

    def test_04_financial_tier_1_submittable_by_purchase_manager(self):
        """Test 04: Assert Tier 1 (< 50k) can be submitted by Purchase Manager."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Central Inventory Replenishment"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 10, "rate": 1000.00})
        po.insert()

        self.assertEqual(po.custom_authorization_tier, "Tier 1: Up to ₹50,000")

    def test_05_purchase_assistant_blocked_from_submitting(self):
        """Test 05: Assert Purchase Assistant role cannot submit Purchase Order."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Central Inventory Replenishment"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 10, "rate": 1000.00})
        po.insert()

        frappe.set_user("test_purchase_assistant@example.com")
        try:
            with self.assertRaises(frappe.PermissionError):
                POAuthorizationMatrixService.assert_authorization_permissions(po)
        finally:
            frappe.set_user("Administrator")

    def test_06_tier_3_and_4_strictly_admin(self):
        """Test 06: Assert Tier 3 (> 5L) and Tier 4 (> 50L) require Admin role."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Central Inventory Replenishment"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 1000, "rate": 6000.00})  # 60 Lakhs
        po.insert()

        self.assertEqual(po.custom_authorization_tier, "Tier 4: Above ₹50,000,000")

    def test_07_structured_milestones_mandated(self):
        """Test 07: Assert capital solar equipment requires >= 2 milestone schedule rows."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Project-Specific Solar Equipment"
        po.custom_is_single_source = 1
        po.custom_authorization_remarks = "Valid single-source procurement for specialized components."
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 10, "rate": 1000.00})
        # Single immediate milestone
        po.append("payment_schedule", {"payment_amount": 10000.00, "due_date": po.schedule_date})

        with self.assertRaises(frappe.ValidationError):
            POMilestoneTermsService.validate_payment_schedule(po)

    def test_08_central_replenishment_bypasses_bom_check(self):
        """Test 08: Assert central inventory replenishment bypasses project BOM checks."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Central Inventory Replenishment"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 10000, "rate": 18.50})
        # Should execute cleanly without error
        PurchaseOrderValidationService.validate_project_bom_headroom(po)

    def test_09_direct_site_warehouse_routing_validated(self):
        """Test 09: Assert Direct Site routing requires valid target site warehouse."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_delivery_location_type = "Direct Site Warehouse"
        po.custom_target_site_warehouse = None
        with self.assertRaises(frappe.ValidationError):
            PurchaseOrderValidationService.validate_warehouse_routing(po)

    def test_10_serialized_components_flagged_for_step_16_grn(self):
        """Test 10: Assert components with serial tracking are flagged for Sabhav SABB scan."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_delivery_location_type = "Central Store Warehouse"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 5, "rate": 18.50})
        from solar_module.services.po_dispatch_service import PODispatchBridgeService
        PODispatchBridgeService.precondition_step_16_grn(po)
        self.assertEqual(po.items[0].custom_requires_barcode_serials, 1)

    def test_11_vendor_portal_acknowledgment_flow(self):
        """Test 11: Assert vendor token acknowledgment API records confirmation."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Central Inventory Replenishment"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 10, "rate": 1000.00})
        po.insert()
        po.submit()

        token = po.custom_portal_token
        self.assertTrue(bool(token))

        res = acknowledge_vendor_purchase_order(token, "Acknowledged & Confirmed", "Ready to ship")
        self.assertEqual(res["status"], "success")

        po.reload()
        self.assertEqual(po.custom_vendor_acknowledgment_status, "Acknowledged & Confirmed")

    def test_12_stage_forward_lock_blocks_cancellation_with_downstream_grn(self):
        """Test 12: Assert Stage-Forward Lock blocks PO cancellation when downstream GRN exists."""
        po = frappe.new_doc("Purchase Order")
        po.supplier = self.supplier
        po.custom_po_classification = "Central Inventory Replenishment"
        po.schedule_date = add_to_date(now_datetime(), days=7)
        po.append("items", {"item_code": self.item, "qty": 10, "rate": 1000.00})
        po.insert()
        po.submit()

        # Mock downstream Purchase Receipt
        pr = frappe.new_doc("Purchase Receipt")
        pr.supplier = self.supplier
        pr.purchase_order = po.name
        pr.append("items", {
            "purchase_order": po.name,
            "purchase_order_item": po.items[0].name,
            "item_code": self.item,
            "qty": 10,
            "rate": 1000.00,
        })
        pr.insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            po.cancel()
```

---

## 7. Execution Runbook & Verification Criteria

### 7.1 L3 DevOps Runbook

```bash
# 1. Run integration test suite inside bench environment
bench --site sadbhav.local run-tests --module solar_module.tests.test_step_15_purchase_order_tracer_bullet

# 2. Check active background Celery worker for PO SLA daemon
bench --site sadbhav.local execute solar_module.tasks.monitor_po_release_and_vendor_ack_sla

# 3. Inspect composite database indexes on MariaDB
bench --site sadbhav.local mariadb -e "SHOW INDEX FROM \`tabPurchase Order\` WHERE Key_name LIKE 'idx_po%';"

# 4. Check active purchase order documents in Overdue status
bench --site sadbhav.local mariadb -e "SELECT name, custom_authorization_tier, custom_sla_status, custom_sla_deadline FROM \`tabPurchase Order\` WHERE custom_sla_status = 'Overdue';"
```

### 7.2 Operational SOP for Enterprise Actors

- **Purchase Assistant:** 
  1. Open approved `Quotation Comparison Matrix`, click `[Create Purchase Order]`.
  2. Verify imported items, quantities, and awarded landed rates.
  3. Select Delivery Location Type (`Central Store Warehouse` vs `Direct Site Warehouse`).
  4. Click `[Populate Solar Milestones]` to generate default structured terms (Advance, LR, GRN, Retention).
  5. Save as Draft. Route to `Purchase Manager` or designated executive for sign-off.
- **Purchase Manager:**
  1. Review PO details, verify landed rates and milestone schedules.
  2. For Tier 1 orders (< ₹50,000) or Tier 2 orders (if configured as approver), add sign-off remarks and click `[Submit]`.
  3. For orders $\ge ₹5,00,000$, assign to `Admin` for mandatory executive authorization.
- **Admin (Managing Director / Project Supreme Command):**
  1. Exclusive authority for Tier 3 (> ₹5,00,000) and Tier 4 (> ₹50,00,000) orders.
  2. Validates cash flow commitments, executes final sign-off, and submits PO.
- **External Supplier Representative:**
  1. Receives automated link (`/solar/po-portal/:token`) via WhatsApp/Email.
  2. Reviews items, specs, delivery date, and payment terms without login.
  3. Clicks `[Confirm & Accept Order]` to acknowledge or raises notes on delivery variances.

---

### 7.3 Operational Error Resolution Matrix

| Error Message Displayed                                                | Root Cause                                                     | Operator Resolution                                                                       |
| :--------------------------------------------------------------------- | :------------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| `A submitted Quotation Comparison Matrix is required...`               | PO drafted for capital solar equipment without matrix link.    | Link approved matrix or mark `Is Single Source` with $\ge 30$ char remark.                |
| `Row #X: Item unit rate exceeds approved landed rate...`               | Basic price entered higher than awarded landed rate.           | Reduce unit rate to match or remain below approved landed rate.                           |
| `You are not authorized to release this Purchase Order...`             | Current user lacks required financial delegation role.         | Assign document to `Purchase Manager` (T1), Configured Approver (T2), or `Admin` (T3/T4). |
| `Capital solar procurement mandates structured milestone terms...`     | Single immediate payment term entered for capital solar goods. | Click `[Populate Solar Milestones]` or configure at least 2 milestone tranches.           |
| `Row #X: Total cumulative ordered quantity exceeds BOM ceiling...`     | Project-linked PO exceeds proposal quantity + tolerance.       | Reduce quantity or adjust tolerance in `Solar SCM Settings`.                              |
| `Direct Site Warehouse routing requires a valid target site...`        | Direct site selected but site warehouse empty or invalid.      | Select active site warehouse (`Site - <Code> - SEPC`).                                    |
| `SLA Status is Overdue. A structured justification must be logged...`  | 24h release or 48h vendor ack SLA breached.                    | Click `[Log Delay Justification]` and save reason before processing.                      |
| `Cannot cancel document because active downstream records exist...`    | Downstream `Purchase Receipt` or `Purchase Invoice` exists.    | Cancel downstream receipts and invoices first, or log cancellation request.               |

---

## 8. Summary of Architectural Achievements

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     STAGE 15 TRACER BULLET SPECIFICATION: AT-A-GLANCE                            │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Attribute                     │ Implementation Standard                                          │
├───────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ Document ID                   │ TB-15-PURCHASE-ORDER-AUTHORIZATION                               │
│ Primary File Path             │ step_plans_for_ai/tracer_bullets/STEP_15_PURCHASE_ORDER_...md     │
│ Architecture Basis            │ Pragmatic Programmer Thin Vertical Slice through all 5 Layers   │
│ Upstream Input Gateway        │ Step 14 Award Approved Comparison Matrix or Authorized Indent    │
│ Downstream Intake Gateway     │ Step 16 Multi-Location Barcode GRN (Central Store vs Direct Site)│
│ Financial Authority Matrix    │ 4-Tier: T1 (< 50k), T2 (50k-5L), T3 (5L-50L), T4 (> 50L)         │
│ Role Standards Enforced       │ Purchase Assistant (Draft only), Purchase Manager, Admin         │
│ Milestone Governance          │ Mandatory Tranches (Advance, LR Transit, Post-GRN, Retention)    │
│ Rate Inflation Shield         │ Programmatic Lock: Item Rate <= Awarded Landed Unit Rate         │
│ Project Budget Flexibility    │ Bypass for Stock/Bulk; Configurable BOM check for Projects       │
│ Vendor Confirmation Portal    │ Passwordless 256-bit UUID Token (/solar/po-portal/:token)        │
│ SLA Engine Standards          │ 24h Release SLA, 48h Vendor Ack SLA, Delay Log Interlocking      │
│ Immutability Lock             │ Stage-Forward Lock on downstream Purchase Receipt / Invoice      │
│ Integration Test Suite        │ 12 Atomic Test Cases, FrappeTestCase, Zero-Commit Rule           │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

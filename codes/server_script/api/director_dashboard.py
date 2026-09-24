# =====================================================================
# Server Script: director_dashboard  (v4 — live drilldown + all 9 pages)
# Script Type : API
# API Method  : director_dashboard
# Allow Guest : Unchecked (logged-in Desk users only)
# =====================================================================
# No `import` statements — Frappe Server Script sandbox blocks them.
# `frappe`, `nowdate`, `getdate`, `flt`, `cint` are pre-injected globals.
# =====================================================================

CFG = {
    "lead_doctype": "Lead",
    "site_survey_doctype": "Site Survey",
    "quotation_doctype": "Quotation",           # Proposal
    "sales_order_doctype": "Sales Order",
    "delivery_note_doctype": "Delivery Note",   # Dispatch
    "sync_doctype": "Liaisoning And Synchronization",
    "installation_doctype": "Installation Note",
    "sales_invoice_doctype": "Sales Invoice",
    "payment_entry_doctype": "Payment Entry",
}

SLA_DOCTYPES = [
    {"doctype": CFG["lead_doctype"], "label": "Lead", "date_field": "creation",
     "owner_field": "lead_owner", "name_field": "lead_name"},
    {"doctype": CFG["site_survey_doctype"], "label": "Site Survey", "date_field": "survey_date",
     "owner_field": "surveyed_by", "name_field": "lead_name"},
    {"doctype": CFG["quotation_doctype"], "label": "Proposal", "date_field": "transaction_date",
     "owner_field": "owner", "name_field": "customer_name"},
    {"doctype": CFG["sales_order_doctype"], "label": "Sales Order", "date_field": "transaction_date",
     "owner_field": "owner", "name_field": "customer_name"},
    {"doctype": CFG["delivery_note_doctype"], "label": "Dispatch", "date_field": "posting_date",
     "owner_field": "owner", "name_field": "customer_name"},
    {"doctype": CFG["sync_doctype"], "label": "Synchronization", "date_field": "posting_date",
     "owner_field": "owner", "name_field": "customer_name"},
]

# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------
action = frappe.form_dict.get("action")
from_date = frappe.form_dict.get("from_date") or nowdate()
to_date = frappe.form_dict.get("to_date") or nowdate()

try:
    if action == "get_overview":
        frappe.response["message"] = {
            "pipeline": get_pipeline(from_date, to_date),
            "stats": get_stats(),
            "payments_summary": get_payments_summary(from_date, to_date),
            "financial": get_financial(from_date, to_date),
            "inventory": get_inventory(),
            "stage_wise": get_stage_wise(),
            "tat_summary": get_tat_summary(),
            "top_delayed": get_top_delayed(),
        }
    elif action == "get_crm":
        frappe.response["message"] = get_crm_data(from_date, to_date)
    elif action == "get_projects":
        frappe.response["message"] = get_projects_data(from_date, to_date)
    elif action == "get_finance":
        frappe.response["message"] = get_finance_data(from_date, to_date)
    elif action == "get_stores":
        frappe.response["message"] = get_stores_data()
    elif action == "get_hrms":
        frappe.response["message"] = get_hrms_data()
    elif action == "get_performance":
        frappe.response["message"] = get_performance_data(from_date, to_date)
    elif action == "get_tat":
        frappe.response["message"] = {"tat_summary": get_tat_summary()}
    elif action == "get_support":
        frappe.response["message"] = get_support_data()
    # ------------------------------------------------------------------
    # NEW (v4): generic live-record drilldown — used by every KPI card,
    # funnel stage and table row on the frontend via openLiveDrilldown().
    # ------------------------------------------------------------------
    elif action == "get_records":
        frappe.response["message"] = get_records_generic()
    else:
        frappe.response["message"] = {"error": "Invalid Request"}
except Exception:
    frappe.log_error(frappe.get_traceback(), "director_dashboard error")
    frappe.response["message"] = {"error": frappe.get_traceback()}


# =====================================================================
# HELPERS
# =====================================================================

def safe_count(doctype, filters):
    try:
        return cint(frappe.db.count(doctype, filters))
    except Exception:
        return 0


def get_pipeline(from_date, to_date):
    lead = safe_count(CFG["lead_doctype"], [["creation", "between", [from_date, to_date]]])
    survey = safe_count(CFG["site_survey_doctype"], [["survey_date", "between", [from_date, to_date]]])
    proposal = safe_count(CFG["quotation_doctype"], [["transaction_date", "between", [from_date, to_date]]])
    sales_order = safe_count(CFG["sales_order_doctype"], [["transaction_date", "between", [from_date, to_date]]])
    dispatch = safe_count(CFG["delivery_note_doctype"], [["posting_date", "between", [from_date, to_date]]])
    installation = safe_count(CFG["installation_doctype"], [
        ["inst_date", "between", [from_date, to_date]],
        ["status", "=", "Submitted"],
    ])
    sync = safe_count(CFG["sync_doctype"], [["posting_date", "between", [from_date, to_date]]])
    payments = safe_count(CFG["payment_entry_doctype"], [
        ["posting_date", "between", [from_date, to_date]],
        ["payment_type", "=", "Receive"],
        ["docstatus", "=", 1],
    ])

    return {
        "lead": lead, "survey": survey, "proposal": proposal,
        "sales_order": sales_order, "dispatch": dispatch,
        "installation": installation, "sync": sync, "payments": payments,
    }


def get_stats():
    total = 0
    delayed = 0
    completed = 0
    for d in SLA_DOCTYPES:
        total += safe_count(d["doctype"], [])
        delayed += safe_count(d["doctype"], [["complete_status", "=", "Delayed"]])
        completed += safe_count(d["doctype"], [["stage_status", "=", "Completed"]])
    return {"total": total, "delayed": delayed, "installation_completed": completed}


def get_payments_summary(from_date, to_date):
    filters = {
        "posting_date": ["between", [from_date, to_date]],
        "payment_type": "Receive",
        "docstatus": 1,
    }
    total_received = flt(frappe.db.get_value(
        CFG["payment_entry_doctype"], filters, "sum(paid_amount)"
    ) or 0)

    advance = flt(frappe.db.get_value(
        CFG["payment_entry_doctype"], dict(filters, is_advance="Yes"), "sum(paid_amount)"
    ) or 0)
    non_advance = total_received - advance

    overdue = flt(frappe.db.get_value(
        CFG["sales_invoice_doctype"], {"status": "Overdue", "docstatus": 1}, "sum(outstanding_amount)"
    ) or 0)

    return {
        "total_received": total_received,
        "advance": advance,
        "milestone": non_advance * 0.6,
        "final": non_advance * 0.4,
        "overdue": overdue,
    }


def get_financial(from_date, to_date):
    revenue = flt(frappe.db.get_value(
        CFG["sales_invoice_doctype"],
        {"posting_date": ["between", [from_date, to_date]], "docstatus": 1},
        "sum(grand_total)"
    ) or 0)
    cost = 0  # no confirmed costing source yet
    profit = revenue - cost
    margin = round((profit / revenue) * 100, 1) if revenue else 0
    return {"revenue": revenue, "cost": cost, "profit": profit, "margin": margin}


def get_inventory():
    try:
        total_items = safe_count("Item", [["disabled", "=", 0]])
        bins = frappe.db.sql("SELECT actual_qty, reorder_level FROM `tabBin`", as_dict=True)
        in_stock = len([b for b in bins if flt(b.actual_qty) > 0])
        out_of_stock = len([b for b in bins if flt(b.actual_qty) <= 0])
        low_stock = len([
            b for b in bins
            if flt(b.actual_qty) > 0 and flt(b.reorder_level) and flt(b.actual_qty) <= flt(b.reorder_level)
        ])
        return {"total_items": total_items, "in_stock": in_stock, "low_stock": low_stock, "out_of_stock": out_of_stock}
    except Exception:
        return {"total_items": 0, "in_stock": 0, "low_stock": 0, "out_of_stock": 0}


def get_stage_wise():
    result = {}
    for d in SLA_DOCTYPES:
        on_time = safe_count(d["doctype"], [["complete_status", "=", "On Time"]])
        delayed = safe_count(d["doctype"], [["complete_status", "=", "Delayed"]])
        result[d["label"]] = {"on_time": on_time, "delayed": delayed}
    return result


def get_tat_summary():
    out = []
    for d in SLA_DOCTYPES:
        doctype = d["doctype"]
        avg_tat = 0
        avg_sla = 0
        try:
            row = frappe.db.sql("""
                SELECT AVG(DATEDIFF(complete_date, creation)) as avg_tat
                FROM `tab{doctype}`
                WHERE complete_date IS NOT NULL
            """.format(doctype=doctype), as_dict=True)
            avg_tat = round(flt(row[0].avg_tat) if row and row[0].avg_tat else 0, 1)

            row2 = frappe.db.sql("""
                SELECT AVG(DATEDIFF(sla_due_date, creation)) as avg_sla
                FROM `tab{doctype}`
                WHERE sla_due_date IS NOT NULL
            """.format(doctype=doctype), as_dict=True)
            avg_sla = round(flt(row2[0].avg_sla) if row2 and row2[0].avg_sla else 0, 1)
        except Exception:
            pass

        if not avg_sla:
            status = "No Data"
        elif avg_tat <= avg_sla:
            status = "On Time"
        elif avg_tat <= avg_sla + 2:
            status = "Near SLA"
        else:
            status = "Delayed"

        out.append({"stage": d["label"], "avg_tat": avg_tat, "sla": avg_sla or 0, "status": status})
    return out


def get_top_delayed(limit=10):
    rows = []
    for d in SLA_DOCTYPES:
        doctype = d["doctype"]
        owner_field = d["owner_field"]
        name_field = d["name_field"]
        try:
            data = frappe.db.sql("""
                SELECT
                    name,
                    {name_field} as display_name,
                    {owner_field} as owner,
                    sla_due_date,
                    DATEDIFF(%s, sla_due_date) as delay_days
                FROM `tab{doctype}`
                WHERE sla_due_date IS NOT NULL
                  AND sla_due_date < %s
                  AND (stage_status = 'Overdue' OR complete_status = 'Delayed')
                  AND (stage_status != 'Completed')
                ORDER BY sla_due_date ASC
                LIMIT %s
            """.format(name_field=name_field, owner_field=owner_field, doctype=doctype),
                (nowdate(), nowdate(), limit), as_dict=True)

            for r in data:
                rows.append({
                    "project": (r.display_name or r.name) + " (" + d["label"] + ")",
                    "delay_days": cint(r.delay_days) or 0,
                    "owner": r.owner or "Unassigned",
                })
        except Exception:
            continue

    rows.sort(key=lambda x: x["delay_days"], reverse=True)
    return rows[:limit]


# ---------------------------------------------------------------------
# CRM & SALES
# ---------------------------------------------------------------------
def get_crm_data(from_date, to_date):
    try:
        total_leads = safe_count(CFG["lead_doctype"], [["creation", "between", [from_date, to_date]]])
        proposals = safe_count(CFG["quotation_doctype"], [["transaction_date", "between", [from_date, to_date]]])
        converted = safe_count(CFG["lead_doctype"], [
            ["creation", "between", [from_date, to_date]], ["status", "=", "Converted"]])
        lost = safe_count(CFG["lead_doctype"], [
            ["creation", "between", [from_date, to_date]],
            ["status", "in", ["Do Not Contact", "Not Interested"]]])
        conversion_rate = round((converted / total_leads) * 100, 1) if total_leads else 0

        rows = frappe.db.sql("""
            SELECT lead_owner as owner, COUNT(*) as owned,
                   SUM(CASE WHEN status='Converted' THEN 1 ELSE 0 END) as converted,
                   AVG(tat_days) as avg_tat
            FROM `tabLead`
            WHERE creation BETWEEN %s AND %s AND lead_owner IS NOT NULL
            GROUP BY lead_owner
            ORDER BY owned DESC
            LIMIT 10
        """, (from_date, to_date), as_dict=True)

        top_salespersons = []
        for r in rows:
            owned = cint(r.owned)
            conv = cint(r.converted)
            top_salespersons.append({
                "name": frappe.db.get_value("User", r.owner, "full_name") or r.owner,
                "leads_owned": owned,
                "converted": conv,
                "conversion_pct": round((conv / owned) * 100, 1) if owned else 0,
                "avg_tat": round(flt(r.avg_tat), 1) if r.avg_tat else 0,
            })

        return {
            "kpis": {
                "total_leads": total_leads, "proposals_sent": proposals,
                "conversion_rate": conversion_rate, "lost_leads": lost,
            },
            "top_salespersons": top_salespersons,
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_crm_data error")
        return {"error": frappe.get_traceback()}


# ---------------------------------------------------------------------
# PROJECTS & OPERATIONS
# ---------------------------------------------------------------------
def get_projects_data(from_date, to_date):
    try:
        active = safe_count(CFG["sales_order_doctype"], [["transaction_date", "between", [from_date, to_date]]])
        installations = safe_count(CFG["installation_doctype"], [
            ["inst_date", "between", [from_date, to_date]], ["status", "=", "Submitted"]])
        dispatched = safe_count(CFG["delivery_note_doctype"], [["posting_date", "between", [from_date, to_date]]])
        synced = safe_count(CFG["sync_doctype"], [["posting_date", "between", [from_date, to_date]]])

        rows = frappe.db.sql("""
            SELECT so.name as project, so.customer_name as customer, so.owner as owner,
                   so.complete_status as complete_status, so.stage_status as stage_status
            FROM `tabSales Order` so
            WHERE so.transaction_date BETWEEN %s AND %s
            ORDER BY so.modified DESC
            LIMIT 15
        """, (from_date, to_date), as_dict=True)

        table = []
        for r in rows:
            health = "On Track"
            if r.complete_status == "Delayed":
                health = "Critical" if r.stage_status == "Overdue" else "At Risk"
            table.append({
                "project": r.project, "customer": r.customer, "stage": r.stage_status or "Open",
                "health": health, "owner": frappe.db.get_value("User", r.owner, "full_name") or r.owner,
            })

        return {
            "kpis": {
                "active_projects": active, "installations": installations,
                "dispatched": dispatched, "synchronized": synced,
            },
            "project_health": table,
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_projects_data error")
        return {"error": frappe.get_traceback()}


# ---------------------------------------------------------------------
# FINANCE
# ---------------------------------------------------------------------
def get_finance_data(from_date, to_date):
    try:
        fin = get_financial(from_date, to_date)
        overdue = flt(frappe.db.get_value(
            CFG["sales_invoice_doctype"], {"status": "Overdue", "docstatus": 1}, "sum(outstanding_amount)"
        ) or 0)

        top_profitable = frappe.db.sql("""
            SELECT name, grand_total FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s AND docstatus = 1
            ORDER BY grand_total DESC LIMIT 5
        """, (from_date, to_date), as_dict=True)

        return {
            "kpis": {
                "revenue": fin["revenue"], "gross_profit": fin["profit"],
                "margin": fin["margin"], "overdue_payment": overdue,
            },
            "top_profitable": [{"project": r.name, "profit": r.grand_total} for r in top_profitable],
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_finance_data error")
        return {"error": frappe.get_traceback()}


# ---------------------------------------------------------------------
# STORES & PURCHASE  (confirmed: Item, Purchase Order w/ per_received; Bin standard)
# ---------------------------------------------------------------------
def get_stores_data():
    try:
        total_items = safe_count("Item", [["disabled", "=", 0]])
        bins = frappe.db.sql("SELECT actual_qty, reorder_level FROM `tabBin`", as_dict=True)
        in_stock = len([b for b in bins if flt(b.actual_qty) > 0])
        out_of_stock = len([b for b in bins if flt(b.actual_qty) <= 0])
        low_stock = len([b for b in bins if flt(b.actual_qty) > 0 and flt(b.reorder_level)
                          and flt(b.actual_qty) <= flt(b.reorder_level)])

        po_rows = frappe.db.sql("""
            SELECT po.name as po_no, po.supplier as vendor, poi.item_name as item,
                   po.status as status, po.per_received as per_received,
                   DATEDIFF(CURDATE(), po.transaction_date) as days_pending
            FROM `tabPurchase Order` po
            LEFT JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
            WHERE po.docstatus = 1 AND po.status NOT IN ('Completed', 'Cancelled', 'Closed')
                  AND IFNULL(po.per_received, 0) < 100
            ORDER BY po.transaction_date ASC LIMIT 10
        """, as_dict=True)

        return {
            "kpis": {"total_items": total_items, "in_stock": in_stock,
                     "low_stock": low_stock, "out_of_stock": out_of_stock},
            "purchase_pending": po_rows,
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_stores_data error")
        return {"error": frappe.get_traceback()}


# ---------------------------------------------------------------------
# HRMS & PAYROLL  (confirmed from HRMS.txt)
# ---------------------------------------------------------------------
def get_hrms_data():
    try:
        total_emp = safe_count("Employee", [["status", "=", "Active"]])
        today = nowdate()
        present = safe_count("Attendance", [["attendance_date", "=", today], ["status", "=", "Present"]])
        wfh = safe_count("Attendance", [["attendance_date", "=", today], ["status", "=", "Work From Home"]])
        on_leave = safe_count("Attendance", [["attendance_date", "=", today], ["status", "=", "On Leave"]])
        half_day = safe_count("Attendance", [["attendance_date", "=", today], ["status", "=", "Half Day"]])

        dept_rows = frappe.db.sql("""
            SELECT department, COUNT(*) as headcount FROM `tabEmployee`
            WHERE status = 'Active' AND department IS NOT NULL
            GROUP BY department ORDER BY headcount DESC
        """, as_dict=True)

        return {
            "kpis": {
                "total_employees": total_emp,
                "present_today": present + wfh,
                "on_leave": on_leave + half_day,
            },
            "department_headcount": dept_rows,
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_hrms_data error")
        return {"error": frappe.get_traceback()}


# ---------------------------------------------------------------------
# EMPLOYEE PERFORMANCE  (SLA_DOCTYPES owner-wise rollup)
# ---------------------------------------------------------------------
def get_performance_data(from_date, to_date):
    try:
        combined = {}
        for d in SLA_DOCTYPES:
            rows = frappe.db.sql("""
                SELECT {owner_field} as owner,
                       COUNT(*) as assigned,
                       SUM(CASE WHEN stage_status='Completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN complete_status='On Time' THEN 1 ELSE 0 END) as on_time
                FROM `tab{doctype}`
                WHERE creation BETWEEN %s AND %s AND {owner_field} IS NOT NULL
                GROUP BY {owner_field}
            """.format(owner_field=d["owner_field"], doctype=d["doctype"]),
                (from_date, to_date), as_dict=True)
            for r in rows:
                key = r.owner
                if key not in combined:
                    combined[key] = {"assigned": 0, "completed": 0, "on_time": 0}
                combined[key]["assigned"] = combined[key]["assigned"] + cint(r.assigned)
                combined[key]["completed"] = combined[key]["completed"] + cint(r.completed)
                combined[key]["on_time"] = combined[key]["on_time"] + cint(r.on_time)

        out = []
        for owner, v in combined.items():
            out.append({
                "employee": frappe.db.get_value("User", owner, "full_name") or owner,
                "assigned": v["assigned"], "completed": v["completed"],
                "on_time_pct": round((v["on_time"] / v["assigned"]) * 100, 1) if v["assigned"] else 0,
            })
        out.sort(key=lambda x: x["assigned"], reverse=True)
        return {"employee_performance": out[:15]}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_performance_data error")
        return {"error": frappe.get_traceback()}


# ---------------------------------------------------------------------
# SUPPORT & TICKETS  (defaults to HD Ticket; safely reports if absent)
# ---------------------------------------------------------------------
def get_support_data():
    try:
        if not frappe.db.exists("DocType", "HD Ticket"):
            return {"available": False,
                    "note": "HD Ticket doctype not found on this site — confirm your ticket doctype name to wire this page."}

        open_t = safe_count("HD Ticket", [["status", "=", "Open"]])
        in_progress = safe_count("HD Ticket", [["status", "=", "Replied"]])
        resolved_30d = safe_count("HD Ticket", [["status", "=", "Closed"],
                                                 ["modified", ">=", frappe.utils.add_days(nowdate(), -30)]])

        recent = frappe.db.sql("""
            SELECT name as ticket, subject, priority, status FROM `tabHD Ticket`
            ORDER BY creation DESC LIMIT 10
        """, as_dict=True)

        return {
            "available": True,
            "kpis": {"open_tickets": open_t, "in_progress": in_progress, "resolved_30d": resolved_30d},
            "recent_tickets": recent,
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_support_data error")
        return {"error": frappe.get_traceback()}


# ---------------------------------------------------------------------
# NEW (v4): GENERIC LIVE DRILLDOWN
# Called by openLiveDrilldown() on the frontend for every KPI card,
# funnel stage, and (going forward) table row. Auto-picks whichever
# display columns actually exist on the target doctype so it never
# breaks when different doctypes are passed in.
# ---------------------------------------------------------------------
def get_records_generic():
    doctype = frappe.form_dict.get("doctype")
    filters_json = frappe.form_dict.get("filters") or "{}"
    limit = cint(frappe.form_dict.get("limit") or 50)

    if not doctype:
        return {"error": "No doctype passed to get_records"}
    if not frappe.db.exists("DocType", doctype):
        return {"error": "DocType '{0}' not found on this site".format(doctype)}

    try:
        filters = frappe.parse_json(filters_json)
        meta = frappe.get_meta(doctype)

        # Build a safe, existence-checked field list — never assume a field exists
        candidate_fields = [
            "customer_name", "lead_name", "supplier", "supplier_name", "status",
            "stage_status", "complete_status", "owner", "creation", "transaction_date",
            "posting_date", "grand_total", "paid_amount", "sla_due_date", "employee_name",
            "department", "subject", "priority",
        ]
        fields = ["name"]
        for f in candidate_fields:
            if meta.has_field(f) and f not in fields:
                fields.append(f)

        rows = frappe.get_list(
            doctype,
            filters=filters,
            fields=fields,
            limit_page_length=limit,
            order_by="creation desc",
        )
        return {"doctype": doctype, "columns": fields, "rows": rows}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_records_generic error")
        return {"error": frappe.get_traceback()}
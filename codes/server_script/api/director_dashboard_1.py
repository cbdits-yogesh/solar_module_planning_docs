# =====================================================
# GETMYERP DIRECTOR DASHBOARD — SERVER SCRIPT
# Script Type : API
# Method name : director_dashboard
# Version     : v1
# =====================================================

action    = frappe.form_dict.get("action", "get_overview")
from_date = frappe.form_dict.get("from_date", "")
to_date   = frappe.form_dict.get("to_date", "")

# ── DEFAULT DATE RANGE: 01 Apr 2026 → Today ─────────────
if not from_date:
    from_date = "2026-04-01"
if not to_date:
    to_date = frappe.utils.today()


def safe_count(doctype, filters=None):
    try:
        return frappe.db.count(doctype, filters=filters or {})
    except Exception:
        return 0


def safe_sum(doctype, field, filters=None):
    try:
        rows = frappe.db.get_all(doctype, filters=filters or {}, fields=["sum(%s) as total" % field])
        return float(rows[0].get("total") or 0) if rows else 0
    except Exception:
        return 0


def fmt(d):
    if d:
        try:
            return frappe.utils.formatdate(str(d)[:10])
        except Exception:
            return str(d)[:10]
    return "Pending"


try:

    # =====================================================
    # ACTION: get_overview  → Director Dashboard main screen
    # =====================================================
    if action == "get_overview":

        date_filter_creation = [["creation", ">=", from_date], ["creation", "<=", to_date + " 23:59:59"]]

        # ── PIPELINE COUNTS (Lead → Payment) ─────────────
        lead_count = safe_count("Lead", {"creation": ["between", [from_date, to_date + " 23:59:59"]]})

        survey_count = safe_count("Site Survey", {"creation": ["between", [from_date, to_date + " 23:59:59"]]})

        proposal_count = safe_count("Quotation", {
            "docstatus": ["!=", 2],
            "transaction_date": ["between", [from_date, to_date]]
        })

        sales_order_count = safe_count("Sales Order", {
            "docstatus": ["!=", 2],
            "transaction_date": ["between", [from_date, to_date]]
        })

        dispatch_count = safe_count("Delivery Note", {
            "docstatus": ["!=", 2],
            "posting_date": ["between", [from_date, to_date]]
        })

        # Installation = Project marked Completed within range (using modified as proxy)
        installation_count = safe_count("Project", {
            "status": "Completed",
            "modified": ["between", [from_date, to_date + " 23:59:59"]]
        })

        # Synchronization completed
        sync_count = 0
        try:
            sync_count = frappe.db.sql("""
                SELECT COUNT(*) FROM `tabLiaisoning And Synchronization`
                WHERE complete_status IS NOT NULL AND complete_status != ''
                AND posting_date BETWEEN %s AND %s
            """, (from_date, to_date))[0][0] or 0
        except Exception:
            pass

        # Payments = submitted Payment Entries in range
        payments_count = safe_count("Payment Entry", {
            "docstatus": 1,
            "posting_date": ["between", [from_date, to_date]]
        })

        # ── PROJECT-LEVEL STATS (Ongoing / Delayed / Total) ──
        total_projects   = safe_count("Project", {"creation": ["between", [from_date, to_date + " 23:59:59"]]})
        ongoing_projects = safe_count("Project", {"status": "Open"})
        delayed_projects = safe_count("Project", {"complete_status": "Delayed"})

        # ── PAYMENTS SUMMARY (Advance / Milestone / Final / Overdue) ──
        today_date = frappe.utils.getdate(frappe.utils.today())

        advance_amt   = 0
        milestone_amt = 0
        final_amt     = 0
        overdue_amt   = 0

        try:
            schedules = frappe.db.sql("""
                SELECT ps.invoice_portion, ps.payment_amount, ps.outstanding, ps.due_date
                FROM `tabPayment Schedule` ps
                INNER JOIN `tabSales Order` so ON ps.parent = so.name
                WHERE so.docstatus != 2
                AND so.transaction_date BETWEEN %s AND %s
            """, (from_date, to_date), as_dict=1)

            for s in schedules:
                paid = float(s.payment_amount or 0) - float(s.outstanding or 0)
                portion = (s.invoice_portion or "").strip().lower()

                if "advance" in portion:
                    advance_amt = advance_amt + paid
                elif "final" in portion:
                    final_amt = final_amt + paid
                elif "milestone" in portion:
                    milestone_amt = milestone_amt + paid
                else:
                    milestone_amt = milestone_amt + paid

                if s.due_date and s.outstanding:
                    try:
                        if frappe.utils.getdate(s.due_date) < today_date:
                            overdue_amt = overdue_amt + float(s.outstanding or 0)
                    except Exception:
                        pass
        except Exception:
            pass

        total_received = advance_amt + milestone_amt + final_amt

        # ── FINANCIAL OVERVIEW ────────────────────────────
        revenue = safe_sum("Sales Order", "grand_total", {
            "docstatus": 1,
            "transaction_date": ["between", [from_date, to_date]]
        })

        cost = safe_sum("Purchase Order", "grand_total", {
            "docstatus": 1,
            "transaction_date": ["between", [from_date, to_date]]
        })

        profit = revenue - cost
        margin = round((profit / revenue) * 100, 2) if revenue > 0 else 0

        # ── INVENTORY SNAPSHOT ────────────────────────────
        total_items = safe_count("Item", {"disabled": 0})

        in_stock = 0
        low_stock = 0
        out_of_stock = 0
        try:
            bins = frappe.db.sql("""
                SELECT b.actual_qty, i.reorder_level
                FROM `tabBin` b
                INNER JOIN `tabItem` i ON b.item_code = i.name
                WHERE i.disabled = 0
            """, as_dict=1)
            for b in bins:
                qty = float(b.actual_qty or 0)
                reorder = float(b.reorder_level or 0)
                if qty <= 0:
                    out_of_stock += 1
                elif reorder > 0 and qty <= reorder:
                    low_stock += 1
                    in_stock += 1
                else:
                    in_stock += 1
        except Exception:
            pass

        # ── PROJECT STAGE WISE STATUS (On Time / Delayed / Yet to Start) ──
        stage_wise = {}
        stage_doctype_map = [
            ("Site Survey", "Site Survey", None),
            ("Proposal", "Quotation", None),
            ("Sales Order", "Sales Order", None),
            ("Dispatch", "Delivery Note", None),
            ("Installation", "Project", "stage_status"),
            ("Synchronization", "Liaisoning And Synchronization", "stage_status"),
        ]
        for label, dt, status_field in stage_doctype_map:
            on_time = 0
            delayed = 0
            yet_to_start = 0
            try:
                if status_field:
                    on_time = safe_count(dt, {status_field: ["!=", "Overdue"]})
                    delayed = safe_count(dt, {status_field: "Overdue"})
                else:
                    on_time = safe_count(dt, {"docstatus": ["!=", 2]})
                    delayed = 0
            except Exception:
                pass
            stage_wise[label] = {"on_time": on_time, "delayed": delayed, "yet_to_start": yet_to_start}

        # ── TAT SUMMARY (Stage Wise Average) ─────────────
        tat_summary = []
        tat_map = [
            ("Site Survey", "Site Survey", 7),
            ("Proposal", "Quotation", 10),
            ("Sales Order", "Sales Order", 7),
            ("Material Dispatch", "Delivery Note", 5),
            ("Installation", "Project", 10),
            ("Synchronization", "Liaisoning And Synchronization", 7),
        ]
        for label, dt, sla in tat_map:
            avg_tat = 0
            try:
                avg_row = frappe.db.get_all(dt, fields=["avg(tat_days) as avg_tat"], filters={"docstatus": ["!=", 2]} if dt != "Project" else {})
                avg_tat = round(float(avg_row[0].get("avg_tat") or 0), 1) if avg_row else 0
            except Exception:
                avg_tat = 0
            status = "On Time" if avg_tat <= sla or avg_tat == 0 else "Delayed"
            tat_summary.append({"stage": label, "avg_tat": avg_tat, "sla": sla, "status": status})

        # ── TOP DELAYED PROJECTS ──────────────────────────
        top_delayed = []
        try:
            rows = frappe.db.get_all("Project",
                filters={"complete_status": "Delayed"},
                fields=["name", "customer", "tat_days", "custom_project_manager"],
                order_by="tat_days desc",
                limit_page_length=5)
            for r in rows:
                owner_name = r.get("custom_project_manager") or ""
                if owner_name:
                    fn = frappe.db.get_value("User", owner_name, "full_name")
                    owner_name = fn or owner_name
                top_delayed.append({
                    "project": r.get("name"),
                    "stage": "Installation",
                    "delay_days": int(r.get("tat_days") or 0),
                    "reason": "N/A",
                    "owner": owner_name or "Unassigned"
                })
        except Exception:
            pass

        frappe.response["message"] = {
            "pipeline": {
                "lead": lead_count,
                "survey": survey_count,
                "proposal": proposal_count,
                "sales_order": sales_order_count,
                "dispatch": dispatch_count,
                "installation": installation_count,
                "sync": sync_count,
                "payments": payments_count
            },
            "stats": {
                "total": total_projects,
                "ongoing": ongoing_projects,
                "delayed": delayed_projects,
                "installation_completed": installation_count,
                "sync_completed": sync_count
            },
            "payments_summary": {
                "advance": round(advance_amt, 2),
                "milestone": round(milestone_amt, 2),
                "final": round(final_amt, 2),
                "overdue": round(overdue_amt, 2),
                "total_received": round(total_received, 2)
            },
            "financial": {
                "revenue": round(revenue, 2),
                "cost": round(cost, 2),
                "profit": round(profit, 2),
                "margin": margin
            },
            "inventory": {
                "total_items": total_items,
                "in_stock": in_stock,
                "low_stock": low_stock,
                "out_of_stock": out_of_stock
            },
            "stage_wise": stage_wise,
            "tat_summary": tat_summary,
            "top_delayed": top_delayed,
            "date_range": {"from": from_date, "to": to_date}
        }

    else:
        frappe.response["message"] = {"error": "Unknown action: " + str(action)}

except Exception as e:
    frappe.log_error(str(e), "Director Dashboard Error")
    frappe.response["message"] = {"error": str(e)}
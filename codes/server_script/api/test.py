# ============================================================
#  project_test — Sadbhav Dashboard Server Script (FIXED v2)
#  Fixes:
#  1. Typo: project_project → project_id
#  2. Read lead/site_survey/proposal directly from Project doc
#  3. Synchronization doctype name fixed
#  4. All build_detail fields aligned with actual custom fields
# ============================================================

def has_field(doctype, fieldname):
    try:
        return frappe.db.has_column(doctype, fieldname)
    except Exception:
        return False

def flt(v):
    try:
        return frappe.utils.flt(v or 0)
    except Exception:
        return 0.0

def cint(v, d=0):
    try:
        return frappe.utils.cint(v or d)
    except Exception:
        return d

def safe_date(v):
    if not v:
        return None
    try:
        return str(v)[:10]
    except Exception:
        return None

# ── Status resolver ──────────────────────────────────────────
def get_status_info(stage_status, complete_status, expected_end_date=None):
    ss = (stage_status or "").strip().lower()
    cs = (complete_status or "").strip().lower()

    if ss == "completed":
        if cs == "delayed":
            return {"category": "Delayed", "display": "Completed (Delayed)"}
        elif cs == "on time":
            return {"category": "Completed", "display": "Completed"}
        else:
            if expected_end_date:
                try:
                    today = frappe.utils.getdate(frappe.utils.nowdate())
                    end   = frappe.utils.getdate(expected_end_date)
                    if today > end:
                        return {"category": "Delayed", "display": "Completed (Delayed)"}
                except Exception:
                    pass
            return {"category": "Completed", "display": "Completed"}

    elif ss == "overdue":
        return {"category": "Delayed", "display": "Overdue"}

    else:
        if expected_end_date:
            try:
                today = frappe.utils.getdate(frappe.utils.nowdate())
                end   = frappe.utils.getdate(expected_end_date)
                if today > end:
                    return {"category": "Delayed", "display": "Overdue"}
            except Exception:
                pass
        return {"category": "Ongoing", "display": "Open"}


# ── DATE RANGE HELPER ─────────────────────────────────────────
def get_date_range(preset, from_date, to_date):
    today = frappe.utils.nowdate()
    if preset == "today":
        return today, today
    elif preset == "this_month":
        from_dt = frappe.utils.get_first_day(today)
        to_dt   = frappe.utils.get_last_day(today)
        return str(from_dt), str(to_dt)
    elif preset == "quarterly":
        from frappe.utils import get_quarter_start, get_quarter_ending
        return str(get_quarter_start(today)), str(get_quarter_ending(today))
    elif preset == "this_year":
        yr = frappe.utils.getdate(today).year
        return "{}-01-01".format(yr), "{}-12-31".format(yr)
    elif preset == "last_year":
        yr = frappe.utils.getdate(today).year - 1
        return "{}-01-01".format(yr), "{}-12-31".format(yr)
    elif preset == "custom":
        return (from_date or "2000-01-01"), (to_date or today)
    else:  # till_now
        return "2000-01-01", today


# ── OVERVIEW DASHBOARD ────────────────────────────────────────
def build_overview_data(preset, from_date, to_date, project_type, stage_filter, name_filter):
    fd, td = get_date_range(preset, from_date, to_date)

    # ── Project filters ──
    proj_filters = {"docstatus": ["<", 2]}
    if project_type:
        proj_filters["plant_category"] = project_type

    pfields = [
        "name", "customer", "status", "percent_complete",
        "expected_end_date", "modified", "creation",
        "stage_status", "complete_status",
        "solar_capacity", "plant_category",
        "lead", "site_survey", "proposal", "sales_order",
        "liaisoning_and_sync"
    ]

    all_projects = frappe.get_all(
        "Project",
        filters=proj_filters,
        fields=pfields,
        order_by="modified desc",
        limit_page_length=0
    )

    project_names = [p.get("name") for p in all_projects if p.get("name")]

    # ── Pipeline counts ──
    def count_stage(doctype, filters):
        try:
            return frappe.db.count(doctype, filters) or 0
        except Exception:
            return 0

    fd_filter = ["creation", ">=", fd]
    td_filter = ["creation", "<=", td]

    timeline = {
        "Lead":     count_stage("Lead",     [fd_filter, td_filter]),
        "Survey":   count_stage("Site Survey", [fd_filter, td_filter]),
        "Proposal": count_stage("Quotation",   [fd_filter, td_filter]),
        "Order":    count_stage("Sales Order", [fd_filter, td_filter, ["docstatus", "=", 1]]),
        "Dispatch": count_stage("Delivery Note", [fd_filter, td_filter, ["docstatus", "=", 1]]),
        "Installation": count_stage("Installation Note", [fd_filter, td_filter]),
        "Sync":     count_stage("Liaisoning And Synchronization", [fd_filter, td_filter]),
    }

    # ── Financial ──
    fin_total, fin_adv, fin_recv, fin_out, fin_overdue = 0, 0, 0, 0, 0
    if project_names:
        so_rows = frappe.get_all("Sales Order",
            filters={"project": ["in", project_names], "docstatus": 1},
            fields=["rounded_total", "advance_paid"],
            limit_page_length=0)
        for r in so_rows:
            fin_total += flt(r.get("rounded_total"))
            fin_adv   += flt(r.get("advance_paid"))

        inv_rows = frappe.get_all("Sales Invoice",
            filters={"project": ["in", project_names], "docstatus": 1},
            fields=["grand_total", "outstanding_amount", "due_date"],
            limit_page_length=0)
        today_str = frappe.utils.nowdate()
        for r in inv_rows:
            fin_recv += flt(r.get("grand_total")) - flt(r.get("outstanding_amount"))
            fin_out  += flt(r.get("outstanding_amount"))
            if (r.get("outstanding_amount") or 0) > 0:
                if (r.get("due_date") or "9999-12-31") < today_str:
                    fin_overdue += flt(r.get("outstanding_amount"))

    # ── Costing ──
    cost_mat, cost_civ, cost_lab, cost_partner = 0, 0, 0, 0
    if project_names:
        po_rows = frappe.get_all("Purchase Order Item",
            filters={"project": ["in", project_names], "docstatus": 1},
            fields=["amount", "item_group"],
            limit_page_length=0)
        for r in po_rows:
            grp = (r.get("item_group") or "").lower()
            if "civil" in grp:
                cost_civ += flt(r.get("amount"))
            elif "labour" in grp or "labor" in grp:
                cost_lab += flt(r.get("amount"))
            else:
                cost_mat += flt(r.get("amount"))

    cost_act = cost_mat + cost_civ + cost_lab + cost_partner

    # ── Purchase & Inventory ──
    pi_po       = count_stage("Purchase Order", [["status", "in", ["Draft","To Receive","To Receive and Bill"]], ["docstatus", "=", 1]])
    pi_mat_pend = count_stage("Purchase Order", [["status", "in", ["To Receive","To Receive and Bill"]], ["docstatus", "=", 1]])
    pi_grn      = count_stage("Purchase Receipt", [["docstatus", "=", 0]])
    pi_inv      = 0  # Can be filtered by item group if needed

    # ── Dispatch ──
    disp_total   = count_stage("Delivery Note", [["docstatus", "=", 1], fd_filter, td_filter])
    disp_partial = frappe.db.count("Delivery Note", {"docstatus": 1, "per_billed": ["<", 100]}) or 0
    disp_delay   = 0

    # ── Material Returns ──
    ret_logged = count_stage("Stock Entry", [["stock_entry_type", "=", "Material Return"], ["docstatus", "=", 1]])
    ret_value  = 0
    try:
        ret_rows = frappe.get_all("Stock Entry",
            filters={"stock_entry_type": "Material Return", "docstatus": 1},
            fields=["total_outgoing_value"],
            limit_page_length=0)
        ret_value = sum([flt(r.get("total_outgoing_value")) for r in ret_rows])
    except Exception:
        pass

    # ── Synchronization ──
    sync_prog   = count_stage("Liaisoning And Synchronization",
        [["liaisoning_status", "in", ["New","In Process","Registered","Agreement Signed","Submit to Division"]]])
    sync_delayed = count_stage("Liaisoning And Synchronization", [["stage_status", "=", "Overdue"]])
    sync_discom  = count_stage("Liaisoning And Synchronization",
        [["liaisoning_status", "in", ["Submit to Division","In Process"]]])

    # ── Productivity ──
    prod_comp = count_stage("Project", [["status", "=", "Completed"], ["modified", ">=", fd], ["modified", "<=", td]])

    # ── Delay Panel ──
    delay_panel = []
    try:
        delay_rows = frappe.db.sql("""
            SELECT
                so.name AS task_name,
                so.customer_name AS project_name,
                'Sales Order' AS stage,
                'Sales' AS dept,
                so.delay_log AS reason,
                DATEDIFF(CURDATE(), so.sla_due_date) AS delay_days
            FROM `tabSales Order` so
            WHERE so.stage_status = 'Overdue'
              AND so.docstatus = 1
              AND so.sla_due_date < CURDATE()
            ORDER BY delay_days DESC
            LIMIT 50
        """, as_dict=1)
        delay_panel = delay_rows or []
    except Exception:
        pass

    return {
        "timeline":    timeline,
        "delay_panel": delay_panel,
        "fin_total":   fin_total,
        "fin_adv":     fin_adv,
        "fin_recv":    fin_recv,
        "fin_out":     fin_out,
        "fin_overdue": fin_overdue,
        "cost_mat":    cost_mat,
        "cost_civ":    cost_civ,
        "cost_lab":    cost_lab,
        "cost_partner":cost_partner,
        "cost_act":    cost_act,
        "pi_po":       pi_po,
        "pi_mat_pend": pi_mat_pend,
        "pi_inv":      pi_inv,
        "pi_grn":      pi_grn,
        "disp_total":  disp_total,
        "disp_partial":disp_partial,
        "disp_delay":  disp_delay,
        "ret_logged":  ret_logged,
        "ret_value":   ret_value,
        "sync_prog":   sync_prog,
        "sync_delayed":sync_delayed,
        "sync_discom": sync_discom,
        "prod_comp":   prod_comp,
        "prod_avg_comp": "—",
        "prod_time":     "—",
        "prod_sync_time":"—",
    }


# ── STAGE DATA (modal drill-down) ─────────────────────────────
def get_stage_data(stage, project, name_filter, preset, from_date, to_date):
    fd, td = get_date_range(preset, from_date, to_date)
    rows = []

    try:
        if stage == "Lead":
            filters = [["creation",">=",fd],["creation","<=",td]]
            if name_filter: filters.append(["name","=",name_filter])
            if project:
                filters.append(["name","=",
                    frappe.db.get_value("Project", project, "lead") or "__none__"])
            data = frappe.get_all("Lead",
                filters=filters,
                fields=["name","lead_name","mobile_no","city","source","lead_owner","status","creation_date"],
                order_by="creation desc", limit_page_length=200)
            for r in data:
                rows.append([r.name,
                    r.get("lead_name") or "—",
                    r.get("mobile_no") or "—",
                    r.get("city") or "—",
                    r.get("source") or "—",
                    r.get("lead_owner") or "—",
                    r.get("status") or "—",
                    safe_date(r.get("creation_date")) or "—"])

        elif stage == "Site Survey":
            filters = [["creation",">=",fd],["creation","<=",td]]
            if name_filter: filters.append(["name","=",name_filter])
            if project:
                filters.append(["name","=",
                    frappe.db.get_value("Project", project, "site_survey") or "__none__"])
            data = frappe.get_all("Site Survey",
                filters=filters,
                fields=["name","lead_name","surveyed_by","solar_capacity","site_type","survey_date","status"],
                order_by="creation desc", limit_page_length=200)
            for r in data:
                rows.append([r.name,
                    r.get("lead_name") or "—",
                    safe_date(r.get("survey_date")) or "—",
                    r.get("surveyed_by") or "—",
                    r.get("solar_capacity") or "—",
                    r.get("site_type") or "—",
                    r.get("status") or "—"])

        elif stage == "Proposal":
            filters = [["creation",">=",fd],["creation","<=",td]]
            if name_filter: filters.append(["name","=",name_filter])
            if project:
                filters.append(["name","=",
                    frappe.db.get_value("Project", project, "proposal") or "__none__"])
            data = frappe.get_all("Quotation",
                filters=filters,
                fields=["name","customer_name","solar_capacity","manager","transaction_date","rounded_total","status"],
                order_by="creation desc", limit_page_length=200)
            for r in data:
                rows.append([r.name,
                    r.get("customer_name") or "—",
                    r.get("solar_capacity") or "—",
                    r.get("manager") or "—",
                    safe_date(r.get("transaction_date")) or "—",
                    frappe.utils.fmt_money(flt(r.get("rounded_total"))),
                    r.get("status") or "—"])

        elif stage == "Sales Order":
            filters = [["creation",">=",fd],["creation","<=",td],["docstatus","=",1]]
            if name_filter: filters.append(["name","=",name_filter])
            if project:
                filters.append(["project","=",project])
            data = frappe.get_all("Sales Order",
                filters=filters,
                fields=["name","customer_name","rounded_total","advance_paid","per_advance","transaction_date","manager","status"],
                order_by="creation desc", limit_page_length=200)
            for r in data:
                out = flt(r.get("rounded_total")) - flt(r.get("advance_paid"))
                rows.append([r.name,
                    r.get("customer_name") or "—",
                    frappe.utils.fmt_money(flt(r.get("rounded_total"))),
                    frappe.utils.fmt_money(flt(r.get("advance_paid"))),
                    frappe.utils.fmt_money(out),
                    str(r.get("per_advance") or 0) + "%",
                    safe_date(r.get("transaction_date")) or "—",
                    r.get("manager") or "—",
                    r.get("status") or "—"])

        elif stage == "Dispatch":
            filters = [["creation",">=",fd],["creation","<=",td],["docstatus","=",1]]
            if name_filter: filters.append(["name","=",name_filter])
            if project: filters.append(["project","=",project])
            data = frappe.get_all("Delivery Note",
                filters=filters,
                fields=["name","customer_name","posting_date","manager","late_remark","status"],
                order_by="creation desc", limit_page_length=200)
            for r in data:
                rows.append([r.name,
                    r.get("customer_name") or "—",
                    safe_date(r.get("posting_date")) or "—",
                    r.get("manager") or "—",
                    r.get("status") or "—",
                    r.get("late_remark") or "—"])

        elif stage == "Installation":
            filters = [["creation",">=",fd],["creation","<=",td]]
            if name_filter: filters.append(["name","=",name_filter])
            data = frappe.get_all("Installation Note",
                filters=filters,
                fields=["name","customer_name","inst_date","territory","status","remarks"],
                order_by="creation desc", limit_page_length=200)
            for r in data:
                rows.append([r.name,
                    r.get("customer_name") or "—",
                    safe_date(r.get("inst_date")) or "—",
                    r.get("territory") or "—",
                    r.get("status") or "—",
                    r.get("remarks") or "—"])

        elif stage == "Synchronization":
            filters = [["creation",">=",fd],["creation","<=",td]]
            if name_filter: filters.append(["name","=",name_filter])
            if project:
                filters.append(["project","=",project])
            data = frappe.get_all("Liaisoning And Synchronization",
                filters=filters,
                fields=["name","customer_name","posting_date","liaisoning_status","synchronization_don_dt","lead"],
                order_by="creation desc", limit_page_length=200)
            for r in data:
                rows.append([r.name,
                    r.get("customer_name") or "—",
                    safe_date(r.get("posting_date")) or "—",
                    r.get("liaisoning_status") or "—",
                    safe_date(r.get("synchronization_don_dt")) or "—",
                    r.get("lead") or "—"])

        elif stage == "Project":
            filters = [["creation",">=",fd],["creation","<=",td]]
            if name_filter: filters.append(["name","=",name_filter])
            data = frappe.get_all("Project",
                filters=filters,
                fields=["name","project_name","status","percent_complete","expected_start_date","expected_end_date"],
                order_by="creation desc", limit_page_length=200)
            for r in data:
                rows.append([r.name,
                    r.get("project_name") or r.name,
                    r.get("status") or "—",
                    str(flt(r.get("percent_complete"))) + "%",
                    safe_date(r.get("expected_start_date")) or "—",
                    safe_date(r.get("expected_end_date")) or "—"])

    except Exception as e:
        rows = [["Error: " + str(e)]]

    return rows


# ── NAMES BY STAGE (for filter dropdown) ─────────────────────
def get_names_by_stage(stage):
    doctype_map = {
        "Lead":           ("Lead",                          "lead_name"),
        "Site Survey":    ("Site Survey",                   "lead_name"),
        "Proposal":       ("Quotation",                     "customer_name"),
        "Sales Order":    ("Sales Order",                   "customer_name"),
        "Project":        ("Project",                       "project_name"),
        "Synchronization":("Liaisoning And Synchronization","customer_name"),
    }
    if stage not in doctype_map:
        return []
    dt, label_field = doctype_map[stage]
    try:
        rows = frappe.get_all(dt,
            fields=["name", label_field],
            filters={"docstatus": ["<", 2]},
            order_by="creation desc",
            limit_page_length=500)
        return [{"name": r.name, "label": r.get(label_field) or r.name} for r in rows]
    except Exception:
        return []


# ── SEARCH PROJECTS ───────────────────────────────────────────
def search_projects(query):
    try:
        q = "%" + (query or "") + "%"
        rows = frappe.db.sql("""
            SELECT p.name, p.project_name, c.customer_name, p.status
            FROM `tabProject` p
            LEFT JOIN `tabCustomer` c ON c.name = p.customer
            WHERE p.name LIKE %(q)s
               OR p.project_name LIKE %(q)s
               OR c.customer_name LIKE %(q)s
            ORDER BY p.modified DESC
            LIMIT 40
        """, {"q": q}, as_dict=1)
        return [{"name": r.name, "customer": r.customer_name or "", "status": r.status or ""} for r in rows]
    except Exception:
        return []


# ── PROJECT DATA (hero card) ──────────────────────────────────
def get_project_data(project):
    if not project or not frappe.db.exists("Project", project):
        return {}
    try:
        pfields = [
            "name", "project_name", "customer", "status", "stage_status",
            "complete_status", "percent_complete", "expected_end_date",
            "expected_start_date", "solar_capacity", "plant_category",
            "custom_project_manager", "sales_order"
        ]
        pdoc = frappe.db.get_value("Project", project, pfields, as_dict=1) or {}

        status_info = get_status_info(
            pdoc.get("stage_status"), pdoc.get("complete_status"), pdoc.get("expected_end_date"))

        cust_id   = pdoc.get("customer") or ""
        cust_name = frappe.db.get_value("Customer", cust_id, "customer_name") or cust_id if cust_id else "—"

        so_id     = pdoc.get("sales_order") or ""
        fin_total = flt(frappe.db.get_value("Sales Order", so_id, "rounded_total")) if so_id else 0

        fin_recv, fin_out = 0, 0
        inv_rows = frappe.get_all("Sales Invoice",
            filters={"project": project, "docstatus": 1},
            fields=["grand_total","outstanding_amount"],
            limit_page_length=0)
        for r in inv_rows:
            fin_recv += flt(r.get("grand_total")) - flt(r.get("outstanding_amount"))
            fin_out  += flt(r.get("outstanding_amount"))

        pm = pdoc.get("custom_project_manager") or ""
        pm_name = frappe.db.get_value("User", pm, "full_name") or pm if pm else "—"

        cap_raw = flt(pdoc.get("solar_capacity") or 0)

        return {
            "project_name":      pdoc.get("project_name") or project,
            "status":            status_info["display"],
            "capacity":          str(cap_raw) if cap_raw else "—",
            "project_type":      pdoc.get("plant_category") or "—",
            "percent_complete":  flt(pdoc.get("percent_complete")),
            "expected_start_date": safe_date(pdoc.get("expected_start_date")),
            "expected_end_date": safe_date(pdoc.get("expected_end_date")),
            "customer":          cust_name,
            "project_manager":   pm_name,
            "fin_total":         fin_total,
            "fin_recv":          fin_recv,
            "fin_out":           fin_out,
        }
    except Exception as e:
        return {"error": str(e)}


# ── PROCESS VIEW (stage journey cards) ───────────────────────
def get_process_view(stage, name, project):
    """
    Query EACH doctype independently by customer.
    Never rely on one doc linking to another.
    Strategy:
      1. Get customer_id from the Project (or SO, or whichever doc we have)
      2. Search each doctype separately using customer field
    """
    result = {}

    # ── Step 1: Resolve customer_id from whatever we have ──
    customer_id  = ""
    project_id   = ""
    so_id        = ""
    sync_id      = ""

    if project and frappe.db.exists("Project", project):
        project_id  = project
        pdata = frappe.db.get_value("Project", project,
            ["customer", "sales_order", "liaisoning_and_sync"], as_dict=1) or {}
        customer_id = pdata.get("customer") or ""
        so_id       = pdata.get("sales_order") or ""
        sync_id     = pdata.get("liaisoning_and_sync") or ""

    elif name:
        if stage == "Lead":
            ld = frappe.db.get_value("Lead", name, ["customer"], as_dict=1) or {}
            # Lead has no customer link; use lead_name to search customer
            lead_name = frappe.db.get_value("Lead", name, "lead_name") or ""
            # Try to find customer by name match
            cust = frappe.db.get_value("Customer", {"customer_name": lead_name}, "name")
            customer_id = cust or ""

        elif stage == "Site Survey":
            lead_id_sv = frappe.db.get_value("Site Survey", name, "lead") or ""
            if lead_id_sv:
                lead_name = frappe.db.get_value("Lead", lead_id_sv, "lead_name") or ""
                cust = frappe.db.get_value("Customer", {"customer_name": lead_name}, "name")
                customer_id = cust or ""

        elif stage == "Proposal":
            qt = frappe.db.get_value("Quotation", name,
                ["party_name", "customer_name"], as_dict=1) or {}
            customer_id = qt.get("party_name") or ""

        elif stage == "Sales Order":
            so_id = name
            customer_id = frappe.db.get_value("Sales Order", name, "customer") or ""
            project_id  = frappe.db.get_value("Sales Order", name, "project") or ""

        elif stage == "Project":
            project_id  = name
            pdata = frappe.db.get_value("Project", name,
                ["customer","sales_order","liaisoning_and_sync"], as_dict=1) or {}
            customer_id = pdata.get("customer") or ""
            so_id       = pdata.get("sales_order") or ""
            sync_id     = pdata.get("liaisoning_and_sync") or ""

        elif stage == "Synchronization":
            sync_id = name
            sy = frappe.db.get_value("Liaisoning And Synchronization", name,
                ["customer","sales_order","project"], as_dict=1) or {}
            customer_id = sy.get("customer") or ""
            so_id       = sy.get("sales_order") or ""
            project_id  = sy.get("project") or ""

    # ── Step 2: Query each doctype independently by customer ──

    # ── LEAD ──
    # Lead has no customer link — search by customer_name match
    result["lead"]     = {"reached": False}
    result["lead_doc"] = ""
    try:
        # First try: customer_name on Lead matches customer's customer_name
        cust_name = frappe.db.get_value("Customer", customer_id, "customer_name") if customer_id else ""
        lead_rows = []
        if cust_name:
            lead_rows = frappe.get_all("Lead",
                filters=[["lead_name", "like", "%{}%".format(cust_name)]],
                fields=["name","lead_name","mobile_no","source","lead_owner",
                        "status","creation_date","stage_status"],
                order_by="creation desc", limit_page_length=1)
        # Second try: use customer field on Lead if exists
        if not lead_rows and customer_id:
            lead_rows = frappe.get_all("Lead",
                filters={"customer": customer_id},
                fields=["name","lead_name","mobile_no","source","lead_owner",
                        "status","creation_date","stage_status"],
                order_by="creation desc", limit_page_length=1)
        if lead_rows:
            ld = lead_rows[0]
            result["lead"] = {
                "reached":   True,
                "customer":  ld.get("lead_name") or "—",
                "mobile":    ld.get("mobile_no") or "—",
                "source":    ld.get("source") or "—",
                "actor":     ld.get("lead_owner") or "—",
                "status":    ld.get("status") or "—",
                "date":      safe_date(ld.get("creation_date")),
                "next_step": ld.get("stage_status") or "—",
            }
            result["lead_doc"] = ld.get("name") or ""
    except Exception:
        pass

    # ── SITE SURVEY ──
    # Site Survey has lead (Link to Lead) — search by customer_name on lead_name field
    result["survey"]     = {"reached": False}
    result["survey_doc"] = ""
    try:
        cust_name = frappe.db.get_value("Customer", customer_id, "customer_name") if customer_id else ""
        sv_rows = []
        if cust_name:
            sv_rows = frappe.get_all("Site Survey",
                filters=[["lead_name", "like", "%{}%".format(cust_name)]],
                fields=["name","lead_name","surveyed_by","solar_capacity",
                        "site_type","location_details","survey_date","status"],
                order_by="creation desc", limit_page_length=1)
        if sv_rows:
            sv = sv_rows[0]
            result["survey"] = {
                "reached":   True,
                "customer":  sv.get("lead_name") or "—",
                "actor":     sv.get("surveyed_by") or "—",
                "capacity":  sv.get("solar_capacity") or "—",
                "site_type": sv.get("site_type") or "—",
                "location":  sv.get("location_details") or "—",
                "date":      safe_date(sv.get("survey_date")),
                "status":    sv.get("status") or "—",
            }
            result["survey_doc"] = sv.get("name") or ""
    except Exception:
        pass

    # ── PROPOSAL (Quotation) ──
    # Quotation has party_name (Link to Customer)
    result["proposal"]     = {"reached": False}
    result["proposal_doc"] = ""
    try:
        qt_rows = []
        if customer_id:
            qt_rows = frappe.get_all("Quotation",
                filters={"party_name": customer_id, "docstatus": ["<", 2]},
                fields=["name","customer_name","manager","solar_capacity",
                        "rounded_total","transaction_date","status","next_followup_date"],
                order_by="creation desc", limit_page_length=1)
        # fallback: search by customer_name text
        if not qt_rows:
            cust_name = frappe.db.get_value("Customer", customer_id, "customer_name") if customer_id else ""
            if cust_name:
                qt_rows = frappe.get_all("Quotation",
                    filters=[["customer_name", "like", "%{}%".format(cust_name)],
                             ["docstatus", "<", 2]],
                    fields=["name","customer_name","manager","solar_capacity",
                            "rounded_total","transaction_date","status","next_followup_date"],
                    order_by="creation desc", limit_page_length=1)
        if qt_rows:
            qt = qt_rows[0]
            result["proposal"] = {
                "reached":   True,
                "customer":  qt.get("customer_name") or "—",
                "actor":     qt.get("manager") or "—",
                "capacity":  qt.get("solar_capacity") or "—",
                "amount":    flt(qt.get("rounded_total")),
                "date":      safe_date(qt.get("transaction_date")),
                "status":    qt.get("status") or "—",
                "next_step": safe_date(qt.get("next_followup_date")),
            }
            result["proposal_doc"] = qt.get("name") or ""
    except Exception:
        pass

    # ── SALES ORDER ──
    # Sales Order has customer (Link to Customer)
    result["sales_order"]     = {"reached": False}
    result["sales_order_doc"] = ""
    try:
        so_rows = []
        # If we already know the SO, use it directly
        if so_id and frappe.db.exists("Sales Order", so_id):
            so_rows = frappe.get_all("Sales Order",
                filters={"name": so_id},
                fields=["name","customer_name","manager","rounded_total",
                        "advance_paid","per_advance","transaction_date","status"],
                limit_page_length=1)
        elif customer_id:
            so_rows = frappe.get_all("Sales Order",
                filters={"customer": customer_id, "docstatus": ["<", 2]},
                fields=["name","customer_name","manager","rounded_total",
                        "advance_paid","per_advance","transaction_date","status"],
                order_by="creation desc", limit_page_length=1)
        if so_rows:
            so = so_rows[0]
            if not so_id:
                so_id = so.get("name") or ""
            out = flt(so.get("rounded_total")) - flt(so.get("advance_paid"))
            result["sales_order"] = {
                "reached":     True,
                "customer":    so.get("customer_name") or "—",
                "actor":       so.get("manager") or "—",
                "amount":      flt(so.get("rounded_total")),
                "advance":     flt(so.get("advance_paid")),
                "outstanding": out,
                "adv_pct":     str(so.get("per_advance") or 0) + "%",
                "date":        safe_date(so.get("transaction_date")),
                "status":      so.get("status") or "—",
            }
            result["sales_order_doc"] = so.get("name") or ""
    except Exception:
        pass

    # ── DISPATCH (Delivery Note) ──
    # Delivery Note has customer (Link) and project (Link)
    result["dispatch"]     = {"reached": False}
    result["dispatch_doc"] = ""
    try:
        dn_rows = []
        if project_id:
            dn_rows = frappe.get_all("Delivery Note",
                filters={"project": project_id, "docstatus": ["<", 2]},
                fields=["name","customer_name","manager","posting_date","status","late_remark"],
                order_by="creation desc", limit_page_length=1)
        if not dn_rows and so_id:
            dn_rows = frappe.get_all("Delivery Note",
                filters={"against_sales_order": so_id, "docstatus": ["<", 2]},
                fields=["name","customer_name","manager","posting_date","status","late_remark"],
                order_by="creation desc", limit_page_length=1)
        if not dn_rows and customer_id:
            dn_rows = frappe.get_all("Delivery Note",
                filters={"customer": customer_id, "docstatus": ["<", 2]},
                fields=["name","customer_name","manager","posting_date","status","late_remark"],
                order_by="creation desc", limit_page_length=1)
        if dn_rows:
            dn = dn_rows[0]
            result["dispatch"] = {
                "reached":  True,
                "customer": dn.get("customer_name") or "—",
                "actor":    dn.get("manager") or "—",
                "date":     safe_date(dn.get("posting_date")),
                "status":   dn.get("status") or "—",
                "remark":   dn.get("late_remark") or "—",
            }
            result["dispatch_doc"] = dn.get("name") or ""
    except Exception:
        pass

    # ── PROJECT ──
    result["project"]     = {"reached": False}
    result["project_doc"] = ""
    try:
        pj_rows = []
        if project_id and frappe.db.exists("Project", project_id):
            pj_rows = frappe.get_all("Project",
                filters={"name": project_id},
                fields=["name","project_name","custom_project_manager",
                        "percent_complete","expected_start_date","status"],
                limit_page_length=1)
        elif customer_id:
            pj_rows = frappe.get_all("Project",
                filters={"customer": customer_id, "docstatus": ["<", 2]},
                fields=["name","project_name","custom_project_manager",
                        "percent_complete","expected_start_date","status"],
                order_by="creation desc", limit_page_length=1)
        if pj_rows:
            pj = pj_rows[0]
            if not project_id:
                project_id = pj.get("name") or ""
            pm = pj.get("custom_project_manager") or ""
            pm_name = frappe.db.get_value("User", pm, "full_name") or pm if pm else "—"
            result["project"] = {
                "reached":  True,
                "customer": pj.get("project_name") or project_id,
                "actor":    pm_name,
                "pct":      str(flt(pj.get("percent_complete"))) + "%",
                "date":     safe_date(pj.get("expected_start_date")),
                "status":   pj.get("status") or "—",
            }
            result["project_doc"] = pj.get("name") or ""
    except Exception:
        pass

    # ── SYNCHRONIZATION ──
    result["sync"]     = {"reached": False}
    result["sync_doc"] = ""
    try:
        sy_rows = []
        # If we already know sync_id use it
        if sync_id and frappe.db.exists("Liaisoning And Synchronization", sync_id):
            sy_rows = frappe.get_all("Liaisoning And Synchronization",
                filters={"name": sync_id},
                fields=["name","customer_name","customer","liaisoning_status",
                        "posting_date","synchronization_don_dt","delay_log"],
                limit_page_length=1)
        elif project_id:
            sy_rows = frappe.get_all("Liaisoning And Synchronization",
                filters={"project": project_id, "docstatus": ["<", 2]},
                fields=["name","customer_name","customer","liaisoning_status",
                        "posting_date","synchronization_don_dt","delay_log"],
                order_by="creation desc", limit_page_length=1)
        if not sy_rows and so_id:
            sy_rows = frappe.get_all("Liaisoning And Synchronization",
                filters={"sales_order": so_id, "docstatus": ["<", 2]},
                fields=["name","customer_name","customer","liaisoning_status",
                        "posting_date","synchronization_don_dt","delay_log"],
                order_by="creation desc", limit_page_length=1)
        if not sy_rows and customer_id:
            sy_rows = frappe.get_all("Liaisoning And Synchronization",
                filters={"customer": customer_id, "docstatus": ["<", 2]},
                fields=["name","customer_name","customer","liaisoning_status",
                        "posting_date","synchronization_don_dt","delay_log"],
                order_by="creation desc", limit_page_length=1)
        if sy_rows:
            sy = sy_rows[0]
            sync_done = safe_date(sy.get("synchronization_don_dt")) or "Pending"
            result["sync"] = {
                "reached":   True,
                "customer":  sy.get("customer_name") or "—",
                "actor":     sy.get("customer") or "—",
                "status":    sy.get("liaisoning_status") or "—",
                "date":      safe_date(sy.get("posting_date")),
                "sync_done": sync_done,
                "remark":    sy.get("delay_log") or "—",
            }
            result["sync_doc"] = sy.get("name") or ""
    except Exception:
        pass

    return result


# ── SITE IMAGES ───────────────────────────────────────────────
def get_site_images(stage, name, project):
    images = []
    doctypes_to_check = []

    if project and frappe.db.exists("Project", project):
        pdata = frappe.db.get_value("Project", project,
            ["lead","site_survey","proposal","sales_order","liaisoning_and_sync"],
            as_dict=1) or {}
        doctypes_to_check = [
            ("Site Survey",                   pdata.get("site_survey")),
            ("Project",                        project),
            ("Delivery Note",                  None),
            ("Liaisoning And Synchronization", pdata.get("liaisoning_and_sync")),
        ]
        # also fetch delivery notes for this project
        dn_rows = frappe.get_all("Delivery Note",
            filters={"project": project, "docstatus": ["<",2]},
            fields=["name"], limit_page_length=5)
        for dn in dn_rows:
            doctypes_to_check.append(("Delivery Note", dn.name))

    elif name:
        if stage == "Site Survey":
            doctypes_to_check = [("Site Survey", name)]
        elif stage == "Project":
            doctypes_to_check = [("Project", name)]
        elif stage == "Dispatch":
            doctypes_to_check = [("Delivery Note", name)]
        elif stage == "Synchronization":
            doctypes_to_check = [("Liaisoning And Synchronization", name)]
        else:
            doctypes_to_check = [(stage, name)]

    exts = (".jpg",".jpeg",".png",".gif",".webp")
    seen = set()

    for dt, dn in doctypes_to_check:
        if not dn:
            continue
        try:
            files = frappe.get_all("File",
                filters={"attached_to_doctype": dt, "attached_to_name": dn, "is_folder": 0},
                fields=["file_name","file_url","creation"],
                order_by="creation asc",
                limit_page_length=30)
            for f in files:
                fu = (f.get("file_url") or "").lower()
                fn = (f.get("file_name") or "").lower()
                if any(fu.endswith(e) or fn.endswith(e) for e in exts):
                    key = f.get("file_url")
                    if key and key not in seen:
                        seen.add(key)
                        images.append({
                            "file_name": f.get("file_name"),
                            "file_url":  f.get("file_url"),
                            "doctype":   dt,
                            "docname":   dn,
                        })
        except Exception:
            pass

    return images


# ── ENTRY POINT ───────────────────────────────────────────────
try:
    action     = (frappe.form_dict.get("action") or "").strip()
    preset     = (frappe.form_dict.get("preset") or "till_now").strip()
    from_date  = (frappe.form_dict.get("from_date") or "").strip()
    to_date    = (frappe.form_dict.get("to_date") or "").strip()
    proj_type  = (frappe.form_dict.get("project_type") or "").strip()
    stage_f    = (frappe.form_dict.get("stage_filter") or "").strip()
    name_f     = (frappe.form_dict.get("name_filter") or "").strip()
    project    = (frappe.form_dict.get("project") or "").strip()
    stage      = (frappe.form_dict.get("stage") or "").strip()
    name       = (frappe.form_dict.get("name") or "").strip()
    query      = (frappe.form_dict.get("query") or "").strip()

    if action == "get_dashboard_data":
        frappe.response["message"] = build_overview_data(
            preset, from_date, to_date, proj_type, stage_f, name_f)

    elif action == "get_stage_data":
        frappe.response["message"] = get_stage_data(
            stage, project, name_f, preset, from_date, to_date)

    elif action == "get_names_by_stage":
        frappe.response["message"] = get_names_by_stage(stage)

    elif action == "search_projects":
        frappe.response["message"] = search_projects(query)

    elif action == "get_project_data":
        pid = project or name
        frappe.response["message"] = get_project_data(pid)

    elif action == "get_process_view":
        frappe.response["message"] = get_process_view(stage, name, project)

    elif action == "get_site_images":
        frappe.response["message"] = get_site_images(stage, name, project)

    else:
        frappe.response["message"] = {"error": "Unknown action: " + action}

except Exception:
    frappe.log_error(frappe.get_traceback(), "project_test")
    frappe.response["message"] = {"error": "Server error — see Error Log"}



'''trial and error'''
# ═══════════════════════════════════════════════════════════════
#   SADBHAV EPC CONTROL PANEL — Server Script v5.2
#   Method Name: test
#   Safe-Exec Compatible
# ═══════════════════════════════════════════════════════════════

def safe_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def sq(sql, args=None, as_dict=False):
    if args is None:
        args = ()
    try:
        out = frappe.db.sql(sql, args, as_dict=as_dict)
        if as_dict:
            if out:
                return out
            return []
        if out:
            return out
        return [[0]]
    except Exception as e:
        frappe.log_error("EPC SQL: " + str(e)[:500])
        if as_dict:
            return []
        return [[0]]


def table_exists(tname):
    r = sq(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = %s",
        (tname,)
    )
    return int(r[0][0] or 0) > 0


def column_exists(tab_name, col_name):
    r = sq(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s",
        (tab_name, col_name)
    )
    return int(r[0][0] or 0) > 0


def get_sync_table():
    cands = [
        "tabLiaisoning And Synchronization",
        "tabSynchronization",
        "tabLiaisoning and Synchronization",
        "tabLiaisoning & Synchronization"
    ]
    i = 0
    while i < len(cands):
        if table_exists(cands[i]):
            return cands[i]
        i = i + 1
    return ""


def get_date_range(preset=None, from_date=None, to_date=None):
    t = frappe.utils.today()
    if preset == "today":
        return [t, t]
    if preset == "this_month":
        return [str(frappe.utils.get_first_day(t)), t]
    if preset == "this_year":
        return [t[0:4] + "-01-01", t]
    if preset == "last_year":
        y = int(t[0:4]) - 1
        return [str(y) + "-01-01", str(y) + "-12-31"]
    if preset == "quarterly":
        m = int(t[5:7])
        if m >= 10:
            q = 10
        elif m >= 7:
            q = 7
        elif m >= 4:
            q = 4
        else:
            q = 1
        mm = ("0" + str(q))[-2:]
        return [t[0:4] + "-" + mm + "-01", t]
    if preset == "custom" and from_date and to_date:
        return [str(from_date), str(to_date)]
    return ["2000-01-01", t]


def user_full_name(alias, field):
    return (
        "COALESCE("
        "(SELECT uu.full_name FROM `tabUser` uu WHERE uu.name=" + alias + "." + field + " LIMIT 1),"
        + alias + "." + field + ",'—')"
    )


def classify_cost_rows(rows):
    mat = 0.0
    civ = 0.0
    lab = 0.0
    par = 0.0
    i = 0
    while i < len(rows or []):
        g = rows[i]
        grp = (g.get("item_group") or "").lower()
        amt = safe_float(g.get("amt"))
        if ("panel" in grp or "module" in grp or "cable" in grp or "inverter" in grp or "material" in grp or "solar" in grp or "wire" in grp or "battery" in grp):
            mat = mat + amt
        elif ("civil" in grp or "structure" in grp or "rcc" in grp or "foundation" in grp or "grouting" in grp or "mounting" in grp):
            civ = civ + amt
        elif ("labour" in grp or "labor" in grp or "manpower" in grp or "worker" in grp or "technician" in grp):
            lab = lab + amt
        elif ("partner" in grp or "contractor" in grp or "install" in grp or "commissioning" in grp or "erection" in grp):
            par = par + amt
        else:
            mat = mat + amt
        i = i + 1
    return [mat, civ, lab, par]


# ══════════════════════════════════════════════════════════════
# Names by Stage
# ══════════════════════════════════════════════════════════════

def get_names_by_stage(stage):
    if stage == "Lead":
        return sq("SELECT name, COALESCE(lead_name, name) AS label FROM `tabLead` ORDER BY modified DESC LIMIT 500", as_dict=True)

    if stage == "Site Survey":
        if not table_exists("tabSite Survey"):
            return []
        return sq("SELECT name, COALESCE(lead_name, name) AS label FROM `tabSite Survey` ORDER BY modified DESC LIMIT 500", as_dict=True)

    if stage == "Proposal":
        return sq("SELECT name, COALESCE(customer_name, name) AS label FROM `tabQuotation` WHERE docstatus!=2 ORDER BY modified DESC LIMIT 500", as_dict=True)

    if stage == "Sales Order":
        return sq("SELECT name, COALESCE(customer_name, name) AS label FROM `tabSales Order` WHERE docstatus=1 ORDER BY modified DESC LIMIT 500", as_dict=True)

    if stage == "Project":
        return sq("SELECT name, COALESCE(project_name, name) AS label FROM `tabProject` WHERE status NOT IN ('Cancelled') ORDER BY modified DESC LIMIT 500", as_dict=True)

    if stage == "Synchronization":
        st = get_sync_table()
        if not st:
            return []
        return sq("SELECT name, COALESCE(customer_name, name) AS label FROM `" + st + "` ORDER BY modified DESC LIMIT 500", as_dict=True)

    return []


# ══════════════════════════════════════════════════════════════
# Dashboard Data (Overview Tab)
# ═════════════════════════════════════════��════════════════════

def get_dashboard_data(preset=None, from_date=None, to_date=None, project_type=None, stage_filter=None, name_filter=None):
    data = {}
    t = frappe.utils.today()
    dr = get_date_range(preset, from_date, to_date)
    fd = dr[0]
    td = dr[1]
    st = get_sync_table()
    ptype = (project_type or "").strip()

    # Pipeline counts
    if ptype:
        data["bo_leads"] = sq("SELECT COUNT(*) FROM `tabLead` WHERE DATE(creation) BETWEEN %s AND %s AND COALESCE(plant_category,'')=%s", (fd, td, ptype))[0][0]
    else:
        data["bo_leads"] = sq("SELECT COUNT(*) FROM `tabLead` WHERE DATE(creation) BETWEEN %s AND %s", (fd, td))[0][0]

    if table_exists("tabSite Survey"):
        if ptype:
            data["bo_surveys"] = sq("SELECT COUNT(*) FROM `tabSite Survey` WHERE DATE(survey_date) BETWEEN %s AND %s AND COALESCE(plant_category,'')=%s", (fd, td, ptype))[0][0]
        else:
            data["bo_surveys"] = sq("SELECT COUNT(*) FROM `tabSite Survey` WHERE DATE(survey_date) BETWEEN %s AND %s", (fd, td))[0][0]
    else:
        data["bo_surveys"] = 0

    if ptype:
        data["bo_proposals"] = sq("SELECT COUNT(*) FROM `tabQuotation` WHERE docstatus!=2 AND DATE(transaction_date) BETWEEN %s AND %s AND COALESCE(plant_category,'')=%s", (fd, td, ptype))[0][0]
        data["bo_orders"] = sq("SELECT COUNT(*) FROM `tabSales Order` WHERE docstatus=1 AND DATE(transaction_date) BETWEEN %s AND %s AND COALESCE(plant_category,'')=%s", (fd, td, ptype))[0][0]
    else:
        data["bo_proposals"] = sq("SELECT COUNT(*) FROM `tabQuotation` WHERE docstatus!=2 AND DATE(transaction_date) BETWEEN %s AND %s", (fd, td))[0][0]
        data["bo_orders"] = sq("SELECT COUNT(*) FROM `tabSales Order` WHERE docstatus=1 AND DATE(transaction_date) BETWEEN %s AND %s", (fd, td))[0][0]

    if ptype:
        data["bo_dispatches"] = sq(
            "SELECT COUNT(*) FROM `tabDelivery Note` dn "
            "LEFT JOIN `tabProject` p ON p.name=dn.project "
            "WHERE dn.docstatus=1 AND DATE(dn.posting_date) BETWEEN %s AND %s "
            "AND COALESCE(p.plant_category,'')=%s",
            (fd, td, ptype)
        )[0][0]
    else:
        data["bo_dispatches"] = sq(
            "SELECT COUNT(*) FROM `tabDelivery Note` WHERE docstatus=1 AND DATE(posting_date) BETWEEN %s AND %s",
            (fd, td)
        )[0][0]

    if table_exists("tabInstallation Note"):
        if ptype:
            data["bo_installation"] = sq(
                "SELECT COUNT(*) FROM `tabInstallation Note` i "
                "LEFT JOIN `tabProject` p ON p.name=i.project "
                "WHERE i.status='Submitted' AND DATE(i.inst_date) BETWEEN %s AND %s "
                "AND COALESCE(p.plant_category,'')=%s",
                (fd, td, ptype)
            )[0][0]
        else:
            data["bo_installation"] = sq(
                "SELECT COUNT(*) FROM `tabInstallation Note` WHERE status='Submitted' AND DATE(inst_date) BETWEEN %s AND %s",
                (fd, td)
            )[0][0]
    else:
        data["bo_installation"] = 0

    if st:
        if ptype:
            data["bo_sync"] = sq(
                "SELECT COUNT(*) FROM `" + st + "` s "
                "LEFT JOIN `tabProject` p ON p.name=s.project "
                "WHERE DATE(s.posting_date) BETWEEN %s AND %s "
                "AND COALESCE(p.plant_category,'')=%s",
                (fd, td, ptype)
            )[0][0]
        else:
            data["bo_sync"] = sq(
                "SELECT COUNT(*) FROM `" + st + "` WHERE DATE(posting_date) BETWEEN %s AND %s",
                (fd, td)
            )[0][0]
    else:
        data["bo_sync"] = 0

    data["timeline"] = {
        "Lead":         data["bo_leads"],
        "Survey":       data["bo_surveys"],
        "Proposal":     data["bo_proposals"],
        "Order":        data["bo_orders"],
        "Dispatch":     data["bo_dispatches"],
        "Installation": data["bo_installation"],
        "Sync":         data["bo_sync"]
    }

    # Delay panel
    delays = []
    x1 = sq("""
        SELECT so.name AS task_name, COALESCE(so.customer_name,so.name) AS project_name,
               'Sales Order' AS stage, 'Operations' AS dept,
               COALESCE(so.delay_log,'Order Overdue') AS reason,
               GREATEST(0, DATEDIFF(%s, so.sla_due_date)) AS delay_days
        FROM `tabSales Order` so
        WHERE so.stage_status='Overdue' AND so.sla_due_date IS NOT NULL
        ORDER BY delay_days DESC LIMIT 15
    """, (t,), as_dict=True)
    i = 0
    while i < len(x1):
        delays.append(x1[i])
        i = i + 1

    x2 = sq("""
        SELECT q.name AS task_name, COALESCE(q.customer_name,q.name) AS project_name,
               'Proposal' AS stage, 'Sales' AS dept,
               COALESCE(q.delay_log,'Proposal Overdue') AS reason,
               GREATEST(0, DATEDIFF(%s, q.sla_due_date)) AS delay_days
        FROM `tabQuotation` q
        WHERE q.stage_status='Overdue' AND q.sla_due_date IS NOT NULL
        ORDER BY delay_days DESC LIMIT 15
    """, (t,), as_dict=True)
    i = 0
    while i < len(x2):
        delays.append(x2[i])
        i = i + 1

    x3 = sq("""
        SELECT l.name AS task_name, COALESCE(l.lead_name,l.name) AS project_name,
               'Lead' AS stage, 'CRM' AS dept,
               COALESCE(l.delay_log,'Follow-up Overdue') AS reason,
               GREATEST(0, DATEDIFF(%s, l.sla_due_date)) AS delay_days
        FROM `tabLead` l
        WHERE l.stage_status='Overdue' AND l.sla_due_date IS NOT NULL
        ORDER BY delay_days DESC LIMIT 10
    """, (t,), as_dict=True)
    i = 0
    while i < len(x3):
        delays.append(x3[i])
        i = i + 1

    if st:
        x4 = sq(
            "SELECT s.name AS task_name, COALESCE(s.customer_name,s.name) AS project_name, "
            "'Synchronization' AS stage, 'Liaisoning' AS dept, "
            "COALESCE(s.delay_log,'Sync Overdue') AS reason, "
            "GREATEST(0, DATEDIFF(%s, s.sla_due_date)) AS delay_days "
            "FROM `" + st + "` s "
            "WHERE (s.stage_status='Overdue' OR s.liaisoning_status='Overdue') AND s.sla_due_date IS NOT NULL "
            "ORDER BY delay_days DESC LIMIT 10",
            (t,), as_dict=True
        )
        i = 0
        while i < len(x4):
            delays.append(x4[i])
            i = i + 1

    delays = sorted(delays, key=lambda z: z.get("delay_days") or 0, reverse=True)
    data["delay_panel"] = delays[:20]

    # Financial
    if ptype:
        data["fin_total"] = safe_float(sq("SELECT COALESCE(SUM(grand_total),0) FROM `tabSales Order` WHERE docstatus=1 AND DATE(transaction_date) BETWEEN %s AND %s AND COALESCE(plant_category,'')=%s", (fd, td, ptype))[0][0])
    else:
        data["fin_total"] = safe_float(sq("SELECT COALESCE(SUM(grand_total),0) FROM `tabSales Order` WHERE docstatus=1 AND DATE(transaction_date) BETWEEN %s AND %s", (fd, td))[0][0])

    if ptype:
        data["fin_adv"] = safe_float(sq(
            "SELECT COALESCE(SUM(pe.paid_amount),0) FROM `tabPayment Entry` pe "
            "WHERE pe.docstatus=1 AND pe.payment_type='Receive' AND pe.unallocated_amount>0 "
            "AND DATE(pe.posting_date) BETWEEN %s AND %s "
            "AND pe.name IN ("
            "  SELECT per.parent FROM `tabPayment Entry Reference` per "
            "  JOIN `tabSales Order` so ON so.name=per.reference_name "
            "  WHERE per.reference_doctype='Sales Order' AND COALESCE(so.plant_category,'')=%s"
            ")",
            (fd, td, ptype)
        )[0][0])
        data["fin_recv"] = safe_float(sq(
            "SELECT COALESCE(SUM(pe.paid_amount),0) FROM `tabPayment Entry` pe "
            "WHERE pe.docstatus=1 AND pe.payment_type='Receive' "
            "AND DATE(pe.posting_date) BETWEEN %s AND %s "
            "AND pe.name IN ("
            "  SELECT per.parent FROM `tabPayment Entry Reference` per "
            "  JOIN `tabSales Order` so ON so.name=per.reference_name "
            "  WHERE per.reference_doctype='Sales Order' AND COALESCE(so.plant_category,'')=%s"
            ")",
            (fd, td, ptype)
        )[0][0])
        data["fin_out"] = safe_float(sq(
            "SELECT COALESCE(SUM(si.outstanding_amount),0) FROM `tabSales Invoice` si "
            "LEFT JOIN `tabProject` p ON p.name=si.project "
            "WHERE si.docstatus=1 AND DATE(si.posting_date) BETWEEN %s AND %s "
            "AND COALESCE(p.plant_category,'')=%s",
            (fd, td, ptype)
        )[0][0])
        data["fin_overdue"] = safe_float(sq(
            "SELECT COALESCE(SUM(si.outstanding_amount),0) FROM `tabSales Invoice` si "
            "LEFT JOIN `tabProject` p ON p.name=si.project "
            "WHERE si.docstatus=1 AND si.outstanding_amount>0 AND si.due_date<%s "
            "AND DATE(si.posting_date) BETWEEN %s AND %s "
            "AND COALESCE(p.plant_category,'')=%s",
            (t, fd, td, ptype)
        )[0][0])
    else:
        data["fin_adv"] = safe_float(sq(
            "SELECT COALESCE(SUM(paid_amount),0) FROM `tabPayment Entry` "
            "WHERE docstatus=1 AND payment_type='Receive' AND unallocated_amount>0 "
            "AND DATE(posting_date) BETWEEN %s AND %s",
            (fd, td)
        )[0][0])
        data["fin_recv"] = safe_float(sq(
            "SELECT COALESCE(SUM(paid_amount),0) FROM `tabPayment Entry` "
            "WHERE docstatus=1 AND payment_type='Receive' AND DATE(posting_date) BETWEEN %s AND %s",
            (fd, td)
        )[0][0])
        data["fin_out"] = safe_float(sq(
            "SELECT COALESCE(SUM(outstanding_amount),0) FROM `tabSales Invoice` "
            "WHERE docstatus=1 AND DATE(posting_date) BETWEEN %s AND %s",
            (fd, td)
        )[0][0])
        data["fin_overdue"] = safe_float(sq(
            "SELECT COALESCE(SUM(outstanding_amount),0) FROM `tabSales Invoice` "
            "WHERE docstatus=1 AND outstanding_amount>0 AND due_date<%s "
            "AND DATE(posting_date) BETWEEN %s AND %s",
            (t, fd, td)
        )[0][0])

    # Costing
    if ptype:
        grp = sq(
            "SELECT poi.item_group, COALESCE(SUM(poi.amount),0) AS amt "
            "FROM `tabPurchase Order Item` poi "
            "JOIN `tabPurchase Order` po ON po.name=poi.parent "
            "LEFT JOIN `tabProject` p ON p.name=po.project "
            "WHERE po.docstatus=1 AND DATE(po.transaction_date) BETWEEN %s AND %s "
            "AND COALESCE(p.plant_category,'')=%s "
            "GROUP BY poi.item_group",
            (fd, td, ptype), as_dict=True
        )
    else:
        grp = sq(
            "SELECT poi.item_group, COALESCE(SUM(poi.amount),0) AS amt "
            "FROM `tabPurchase Order Item` poi "
            "JOIN `tabPurchase Order` po ON po.name=poi.parent "
            "WHERE po.docstatus=1 AND DATE(po.transaction_date) BETWEEN %s AND %s "
            "GROUP BY poi.item_group",
            (fd, td), as_dict=True
        )
    cc = classify_cost_rows(grp)
    data["cost_mat"]     = cc[0]
    data["cost_civ"]     = cc[1]
    data["cost_lab"]     = cc[2]
    data["cost_partner"] = cc[3]
    data["cost_act"]     = cc[0] + cc[1] + cc[2] + cc[3]

    # Purchase / inventory
    data["pi_po"] = sq("SELECT COUNT(*) FROM `tabPurchase Order` WHERE docstatus=1 AND status IN ('Draft','To Receive','To Receive and Bill')")[0][0]
    data["pi_mat_pend"] = sq("SELECT COUNT(*) FROM `tabPurchase Order Item` poi JOIN `tabPurchase Order` po ON po.name=poi.parent WHERE po.docstatus=1 AND poi.received_qty<poi.qty")[0][0]
    data["pi_inv"] = sq("SELECT COUNT(*) FROM `tabPurchase Order Item` poi JOIN `tabPurchase Order` po ON po.name=poi.parent WHERE po.docstatus=1 AND poi.received_qty<poi.qty AND (poi.item_group LIKE %s OR poi.item_code LIKE %s)", ("%Inverter%", "%Inverter%"))[0][0]
    data["pi_grn"] = sq("SELECT COUNT(*) FROM `tabPurchase Receipt` WHERE docstatus=0")[0][0]

    # Dispatch / returns
    data["disp_total"]   = data["bo_dispatches"]
    data["disp_partial"] = sq("SELECT COUNT(*) FROM `tabDelivery Note` WHERE docstatus=1 AND per_billed<100 AND DATE(posting_date) BETWEEN %s AND %s", (fd, td))[0][0]
    data["disp_delay"]   = sq("SELECT COUNT(*) FROM `tabDelivery Note` WHERE docstatus=1 AND stage_status='Overdue'")[0][0]
    data["ret_logged"]   = sq("SELECT COUNT(*) FROM `tabStock Entry` WHERE docstatus=1 AND stock_entry_type IN ('Material Return','Material Receipt') AND DATE(posting_date) BETWEEN %s AND %s", (fd, td))[0][0]
    data["ret_value"]    = safe_float(sq("SELECT COALESCE(SUM(total_amount),0) FROM `tabStock Entry` WHERE docstatus=1 AND stock_entry_type IN ('Material Return','Material Receipt') AND DATE(posting_date) BETWEEN %s AND %s", (fd, td))[0][0])

    # Sync / productivity
    if st:
        data["sync_prog"]    = sq("SELECT COUNT(*) FROM `" + st + "` WHERE liaisoning_status IN ('New','Docs Completed','Registered','Agreement Signed','Submit to Division','In Process') AND DATE(posting_date) BETWEEN %s AND %s", (fd, td))[0][0]
        data["sync_delayed"] = sq("SELECT COUNT(*) FROM `" + st + "` WHERE (stage_status='Overdue' OR liaisoning_status='Overdue') AND DATE(posting_date) BETWEEN %s AND %s", (fd, td))[0][0]
        data["sync_discom"]  = sq("SELECT COUNT(*) FROM `" + st + "` WHERE liaisoning_status IN ('Submit to Division','In Process') AND DATE(posting_date) BETWEEN %s AND %s", (fd, td))[0][0]
        ar = sq(
            "SELECT AVG(DATEDIFF(completed_date, posting_date)) AS d FROM `" + st + "` "
            "WHERE completed_date IS NOT NULL AND posting_date IS NOT NULL "
            "AND DATE(posting_date) BETWEEN %s AND %s",
            (fd, td), as_dict=True
        )
        if ar and ar[0].get("d"):
            data["prod_sync_time"] = str(round(ar[0].get("d") or 0)) + " Days"
        else:
            data["prod_sync_time"] = "—"
    else:
        data["sync_prog"]      = 0
        data["sync_delayed"]   = 0
        data["sync_discom"]    = 0
        data["prod_sync_time"] = "—"

    data["prod_comp"] = sq("SELECT COUNT(*) FROM `tabProject` WHERE status='Completed' AND DATE(modified) BETWEEN %s AND %s", (fd, td))[0][0]
    ap = sq(
        "SELECT AVG(DATEDIFF(actual_end_date, expected_start_date)) AS d "
        "FROM `tabProject` "
        "WHERE status='Completed' AND actual_end_date IS NOT NULL AND expected_start_date IS NOT NULL "
        "AND DATE(actual_end_date) BETWEEN %s AND %s",
        (fd, td), as_dict=True
    )
    if ap and ap[0].get("d"):
        data["prod_avg_comp"] = str(round(ap[0].get("d") or 0)) + " Days"
    else:
        data["prod_avg_comp"] = "—"
    data["prod_time"] = "—"

    return data
    
    

# Image data
def get_site_images(stage=None, name=None, project=None):
    # Reuse process resolver to get all linked docs
    pv = get_process_view(stage, name, project)

    refs = []
    # all linked docs in journey
    if pv.get("lead_doc"):
        refs.append(("Lead", pv.get("lead_doc")))
    if pv.get("survey_doc"):
        refs.append(("Site Survey", pv.get("survey_doc")))
    if pv.get("proposal_doc"):
        refs.append(("Quotation", pv.get("proposal_doc")))
    if pv.get("sales_order_doc"):
        refs.append(("Sales Order", pv.get("sales_order_doc")))
    if pv.get("dispatch_doc"):
        refs.append(("Delivery Note", pv.get("dispatch_doc")))
    if pv.get("project_doc"):
        refs.append(("Project", pv.get("project_doc")))
    if pv.get("sync_doc"):
        refs.append(("Liaisoning And Synchronization", pv.get("sync_doc")))

    out = []
    seen = {}

    i = 0
    while i < len(refs):
        dt = refs[i][0]
        dn = refs[i][1]

        # attached files for this doctype/docname
        rows = sq(
            "SELECT name, file_name, file_url, attached_to_doctype, attached_to_name, is_private, creation "
            "FROM `tabFile` "
            "WHERE attached_to_doctype=%s AND attached_to_name=%s "
            "ORDER BY creation DESC",
            (dt, dn),
            as_dict=True
        )

        j = 0
        while j < len(rows):
            r = rows[j]
            fn = (r.get("file_name") or "").lower()
            fu = (r.get("file_url") or "").lower()

            is_img = (
                fn.endswith(".jpg") or fn.endswith(".jpeg") or fn.endswith(".png") or fn.endswith(".webp") or
                fu.endswith(".jpg") or fu.endswith(".jpeg") or fu.endswith(".png") or fu.endswith(".webp")
            )

            if is_img:
                key = (r.get("file_url") or "") + "|" + (r.get("attached_to_doctype") or "") + "|" + (r.get("attached_to_name") or "")
                if not seen.get(key):
                    seen[key] = 1
                    out.append({
                        "file_name": r.get("file_name") or "image",
                        "file_url": r.get("file_url") or "",
                        "doctype": r.get("attached_to_doctype") or "",
                        "docname": r.get("attached_to_name") or "",
                        "is_private": r.get("is_private") or 0,
                        "creation": r.get("creation")
                    })
            j = j + 1

        i = i + 1

    return out


# ════════════���═════════════════════════════════════════════════
# Process View (Stage Journey Cards)
# ══════════════════════════════════════════════════════════════

def get_process_view(stage=None, name=None, project=None):
    st = get_sync_table()
    sel = (stage or "").strip()
    nm = (name or "").strip()
    cp = (project or "").strip()

    lead_doc = ""
    survey_doc = ""
    proposal_doc = ""
    so_doc = ""
    dispatch_doc = ""
    project_doc = cp
    sync_doc = ""

    # anchor by selected stage/name
    if sel == "Lead" and nm:
        lead_doc = nm

    elif sel == "Site Survey" and nm and table_exists("tabSite Survey"):
        survey_doc = nm
        x = sq("SELECT lead FROM `tabSite Survey` WHERE name=%s LIMIT 1", (nm,), as_dict=True)
        if x:
            lead_doc = x[0].get("lead") or ""

    elif sel == "Proposal" and nm:
        proposal_doc = nm
        x = sq("SELECT lead FROM `tabQuotation` WHERE name=%s LIMIT 1", (nm,), as_dict=True)
        if x:
            lead_doc = x[0].get("lead") or ""

    elif sel == "Sales Order" and nm:
        so_doc = nm
        x = sq("SELECT lead, proposal, project FROM `tabSales Order` WHERE name=%s LIMIT 1", (nm,), as_dict=True)
        if x:
            lead_doc = x[0].get("lead") or ""
            proposal_doc = x[0].get("proposal") or ""
            if not project_doc:
                project_doc = x[0].get("project") or ""

    elif sel == "Project" and nm:
        project_doc = nm

    elif sel == "Synchronization" and nm and st:
        sync_doc = nm
        x = sq("SELECT project, sales_order FROM `" + st + "` WHERE name=%s LIMIT 1", (nm,), as_dict=True)
        if x:
            if not project_doc:
                project_doc = x[0].get("project") or ""
            so_doc = x[0].get("sales_order") or ""

    # If user selected Project stage + name, ensure project_doc is set
    if sel == "Project" and nm and not project_doc:
        project_doc = nm

    # central linking through Sales Order
    if project_doc and not so_doc:
        x = sq("SELECT name, lead, proposal FROM `tabSales Order` WHERE project=%s AND docstatus=1 ORDER BY modified DESC LIMIT 1", (project_doc,), as_dict=True)
        if x:
            so_doc = x[0].get("name") or ""
            if not lead_doc:
                lead_doc = x[0].get("lead") or ""
            if not proposal_doc:
                proposal_doc = x[0].get("proposal") or ""

    # direct pull from project custom link fields (IMPORTANT for your setup)
    if project_doc:
        px = sq("""
            SELECT
                COALESCE(lead,'') AS lead,
                COALESCE(site_survey,'') AS site_survey,
                COALESCE(proposal,'') AS proposal,
                COALESCE(sales_order,'') AS sales_order,
                COALESCE(liaisoning_and_sync,'') AS liaisoning_and_sync
            FROM `tabProject`
            WHERE name=%s
            LIMIT 1
        """, (project_doc,), as_dict=True)

        if px:
            if not lead_doc:
                lead_doc = px[0].get("lead") or ""
            if not survey_doc:
                survey_doc = px[0].get("site_survey") or ""
            if not proposal_doc:
                proposal_doc = px[0].get("proposal") or ""
            if not so_doc:
                so_doc = px[0].get("sales_order") or ""
            if not sync_doc:
                sync_doc = px[0].get("liaisoning_and_sync") or ""

    if so_doc and not project_doc:
        x = sq("SELECT project FROM `tabSales Order` WHERE name=%s LIMIT 1", (so_doc,), as_dict=True)
        if x:
            project_doc = x[0].get("project") or ""

    if proposal_doc and not lead_doc:
        x = sq("SELECT lead FROM `tabQuotation` WHERE name=%s LIMIT 1", (proposal_doc,), as_dict=True)
        if x:
            lead_doc = x[0].get("lead") or ""

    if lead_doc and not proposal_doc:
        x = sq("SELECT name FROM `tabQuotation` WHERE lead=%s AND docstatus!=2 ORDER BY modified DESC LIMIT 1", (lead_doc,), as_dict=True)
        if x:
            proposal_doc = x[0].get("name") or ""

    if lead_doc and not survey_doc and table_exists("tabSite Survey"):
        x = sq("SELECT name FROM `tabSite Survey` WHERE lead=%s ORDER BY modified DESC LIMIT 1", (lead_doc,), as_dict=True)
        if x:
            survey_doc = x[0].get("name") or ""

    if project_doc and not dispatch_doc:
        x = sq("SELECT name FROM `tabDelivery Note` WHERE project=%s AND docstatus=1 ORDER BY modified DESC LIMIT 1", (project_doc,), as_dict=True)
        if x:
            dispatch_doc = x[0].get("name") or ""

    if (not dispatch_doc) and so_doc:
        x = sq("""
            SELECT DISTINCT dn.name
            FROM `tabDelivery Note` dn
            JOIN `tabDelivery Note Item` dni ON dni.parent=dn.name
            WHERE dn.docstatus=1 AND dni.against_sales_order=%s
            ORDER BY dn.modified DESC LIMIT 1
        """, (so_doc,), as_dict=True)
        if x:
            dispatch_doc = x[0].get("name") or ""

    if project_doc and st and not sync_doc:
        x = sq("SELECT name FROM `" + st + "` WHERE project=%s ORDER BY modified DESC LIMIT 1", (project_doc,), as_dict=True)
        if x:
            sync_doc = x[0].get("name") or ""

    out = {
        "lead": {"reached": 0},
        "survey": {"reached": 0},
        "proposal": {"reached": 0},
        "sales_order": {"reached": 0},
        "dispatch": {"reached": 0},
        "project": {"reached": 0},
        "sync": {"reached": 0},

        "lead_doc": lead_doc,
        "survey_doc": survey_doc,
        "proposal_doc": proposal_doc,
        "sales_order_doc": so_doc,
        "dispatch_doc": dispatch_doc,
        "project_doc": project_doc,
        "sync_doc": sync_doc
    }

    # Lead
    if lead_doc:
        q = (
            "SELECT COALESCE(l.lead_name,l.name) AS customer, "
            "COALESCE(l.mobile_no,'—') AS mobile, "
            "COALESCE(l.source,'—') AS source, "
            + user_full_name("l","lead_owner") + " AS actor, "
            "COALESCE(l.status,'—') AS status, "
            "DATE(l.creation) AS date, "
            "COALESCE(DATE(l.exp_nxstp_dt),'—') AS next_step "
            "FROM `tabLead` l WHERE l.name=%s LIMIT 1"
        )
        r = sq(q, (lead_doc,), as_dict=True)
        if r:
            out["lead"] = {
                "reached": 1,
                "customer": r[0].get("customer"),
                "mobile": r[0].get("mobile"),
                "source": r[0].get("source"),
                "actor": r[0].get("actor"),
                "status": r[0].get("status"),
                "date": r[0].get("date"),
                "next_step": r[0].get("next_step")
            }

    # Survey
    if survey_doc and table_exists("tabSite Survey"):
        q = (
            "SELECT COALESCE(ss.lead_name,ss.name) AS customer, "
            + user_full_name("ss","surveyed_by") + " AS actor, "
            "COALESCE(ss.solar_capacity,'—') AS capacity, "
            "COALESCE(ss.site_type,'—') AS site_type, "
            "COALESCE(ss.location_details,'—') AS location, "
            "DATE(ss.survey_date) AS date, "
            "COALESCE(ss.status,'—') AS status "
            "FROM `tabSite Survey` ss WHERE ss.name=%s LIMIT 1"
        )
        r = sq(q, (survey_doc,), as_dict=True)
        if r:
            out["survey"] = {
                "reached": 1,
                "customer": r[0].get("customer"),
                "actor": r[0].get("actor"),
                "capacity": r[0].get("capacity"),
                "site_type": r[0].get("site_type"),
                "location": r[0].get("location"),
                "date": r[0].get("date"),
                "status": r[0].get("status")
            }

    # Proposal
    if proposal_doc:
        q = (
            "SELECT COALESCE(q.customer_name,q.name) AS customer, "
            + user_full_name("q","manager") + " AS actor, "
            "COALESCE(q.solar_capacity,'—') AS capacity, "
            "q.grand_total AS amount, "
            "DATE(q.transaction_date) AS date, "
            "COALESCE(q.stage_status,'—') AS status, "
            "COALESCE(DATE(q.next_followup_date),'—') AS next_step "
            "FROM `tabQuotation` q WHERE q.name=%s LIMIT 1"
        )
        r = sq(q, (proposal_doc,), as_dict=True)
        if r:
            out["proposal"] = {
                "reached": 1,
                "customer": r[0].get("customer"),
                "actor": r[0].get("actor"),
                "capacity": r[0].get("capacity"),
                "amount": r[0].get("amount"),
                "date": r[0].get("date"),
                "status": r[0].get("status"),
                "next_step": r[0].get("next_step")
            }

    # Sales Order
    if so_doc:
        q = (
            "SELECT COALESCE(so.customer_name,so.name) AS customer, "
            + user_full_name("so","manager") + " AS actor, "
            "so.grand_total AS amount, "
            "COALESCE(so.advance_paid,0) AS advance, "
            "(so.grand_total - COALESCE(so.advance_paid,0)) AS outstanding, "
            "COALESCE(so.per_advance,'0') AS adv_pct, "
            "DATE(so.transaction_date) AS date, "
            "COALESCE(so.status,'—') AS status "
            "FROM `tabSales Order` so WHERE so.name=%s LIMIT 1"
        )
        r = sq(q, (so_doc,), as_dict=True)
        if r:
            out["sales_order"] = {
                "reached": 1,
                "customer": r[0].get("customer"),
                "actor": r[0].get("actor"),
                "amount": r[0].get("amount"),
                "advance": r[0].get("advance"),
                "outstanding": r[0].get("outstanding"),
                "adv_pct": r[0].get("adv_pct"),
                "date": r[0].get("date"),
                "status": r[0].get("status")
            }

    # Dispatch
    if dispatch_doc:
        q = (
            "SELECT COALESCE(dn.customer_name,dn.title,dn.name) AS customer, "
            + user_full_name("dn","manager") + " AS actor, "
            "DATE(dn.posting_date) AS date, "
            "COALESCE(dn.status,'—') AS status, "
            "COALESCE(dn.late_remark,'—') AS remark "
            "FROM `tabDelivery Note` dn WHERE dn.name=%s LIMIT 1"
        )
        r = sq(q, (dispatch_doc,), as_dict=True)
        if r:
            out["dispatch"] = {
                "reached": 1,
                "customer": r[0].get("customer"),
                "actor": r[0].get("actor"),
                "date": r[0].get("date"),
                "status": r[0].get("status"),
                "remark": r[0].get("remark")
            }

    # Project
    if project_doc:
        qpm = "p.owner"
        if column_exists("tabProject", "custom_project_manager"):
            qpm = "p.custom_project_manager"
        elif column_exists("tabProject", "project_manager"):
            qpm = "p.project_manager"

        # status word-based; date from creation; end from p_end_date then expected_end_date
        q = (
            "SELECT "
            "COALESCE(p.project_name,p.name) AS customer, "
            "COALESCE((SELECT u.full_name FROM `tabUser` u WHERE u.name=" + qpm + " LIMIT 1), " + qpm + ", '—') AS actor, "
            "COALESCE(p.status,'Open') AS status, "
            "CASE "
            " WHEN LOWER(COALESCE(p.status,''))='completed' THEN 100 "
            " WHEN LOWER(COALESCE(p.status,''))='open' THEN 0 "
            " WHEN LOWER(COALESCE(p.status,'')) IN ('cancelled','canceled') THEN 0 "
            " ELSE COALESCE(p.percent_complete,0) "
            "END AS pct, "
            "DATE(p.creation) AS date, "
            "COALESCE(DATE(p.p_end_date), DATE(p.expected_end_date), '—') AS end_date "
            "FROM `tabProject` p WHERE p.name=%s LIMIT 1"
        )
        r = sq(q, (project_doc,), as_dict=True)
        if r:
            out["project"] = {
                "reached": 1,
                "customer": r[0].get("customer"),
                "actor": r[0].get("actor"),
                "status": r[0].get("status"),
                "pct": r[0].get("pct"),
                "date": r[0].get("date"),
                "remark": "Expected End: " + str(r[0].get("end_date") or "—")
            }

    # Sync
    if sync_doc and st:
        q = (
            "SELECT COALESCE(s.customer_name,s.name) AS customer, "
            + user_full_name("s","owner") + " AS actor, "
            "COALESCE(s.liaisoning_status,'—') AS status, "
            "DATE(s.posting_date) AS date, "
            "COALESCE(DATE(s.synchronization_don_dt),'Pending') AS sync_done, "
            "COALESCE(s.delay_log,'—') AS remark "
            "FROM `" + st + "` s WHERE s.name=%s LIMIT 1"
        )
        r = sq(q, (sync_doc,), as_dict=True)
        if r:
            out["sync"] = {
                "reached": 1,
                "customer": r[0].get("customer"),
                "actor": r[0].get("actor"),
                "status": r[0].get("status"),
                "date": r[0].get("date"),
                "sync_done": r[0].get("sync_done"),
                "remark": r[0].get("remark")
            }

    return out


# ══════════════════════════════════════════════════════════════
# Stage Drilldown Modal
# ══════════════════════════════════════════════════════════════

def get_stage_data(stage, preset=None, from_date=None, to_date=None, project=None, project_type=None, stage_filter=None, name_filter=None):
    dr = get_date_range(preset, from_date, to_date)
    fd = dr[0]
    td = dr[1]
    st = get_sync_table()
    rows = []
    ptype = (project_type or "").strip()

    un_lo = user_full_name("l", "lead_owner")
    un_ss = user_full_name("ss", "surveyed_by")
    un_q = user_full_name("q", "manager")
    un_so = user_full_name("so", "manager")
    un_dn = user_full_name("dn", "manager")
    un_i = user_full_name("i", "owner")
    un_s = user_full_name("s", "owner")

    if stage == "Lead":
        sql = (
            "SELECT l.name, COALESCE(l.lead_name,l.name), COALESCE(l.mobile_no,'—'), "
            "CONCAT(COALESCE(l.city,'—'), ', ', COALESCE(l.state,'—')), "
            "COALESCE(l.source,'—'), " + un_lo + ", DATE(l.creation), COALESCE(l.status,'—') "
            "FROM `tabLead` l "
            "WHERE DATE(l.creation) BETWEEN %s AND %s"
        )
        args = [fd, td]
        if ptype:
            sql = sql + " AND COALESCE(l.plant_category,'')=%s "
            args.append(ptype)
        if name_filter:
            sql = sql + " AND l.name=%s "
            args.append(name_filter)
        rows = sq(sql + " ORDER BY l.creation DESC LIMIT 200", tuple(args))

    elif stage == "Site Survey":
        if not table_exists("tabSite Survey"):
            return [[None, "Site Survey DocType not found."]]
        sql = (
            "SELECT ss.name, COALESCE(ss.lead_name,ss.name), DATE(ss.survey_date), "
            + un_ss + ", COALESCE(ss.solar_capacity,'—'), COALESCE(ss.plant_category,'—'), "
            "COALESCE(ss.location_details,'—'), COALESCE(DATE(ss.completed_date),'—') "
            "FROM `tabSite Survey` ss "
            "WHERE DATE(ss.survey_date) BETWEEN %s AND %s"
        )
        args = [fd, td]
        if ptype:
            sql = sql + " AND COALESCE(ss.plant_category,'')=%s "
            args.append(ptype)
        if project:
            sql = sql + " AND (ss.name IN (SELECT site_survey FROM `tabSales Order` WHERE project=%s) OR ss.lead IN (SELECT lead FROM `tabSales Order` WHERE project=%s)) "
            args.append(project)
            args.append(project)
        if name_filter:
            sql = sql + " AND ss.name=%s "
            args.append(name_filter)
        rows = sq(sql + " ORDER BY ss.survey_date DESC LIMIT 200", tuple(args))

    elif stage == "Proposal":
        sql = (
            "SELECT q.name, COALESCE(q.customer_name,q.name), COALESCE(q.solar_capacity,'—'), "
            + un_q + ", DATE(q.transaction_date), q.grand_total, COALESCE(q.stage_status,'—') "
            "FROM `tabQuotation` q "
            "WHERE q.docstatus!=2 AND DATE(q.transaction_date) BETWEEN %s AND %s"
        )
        args = [fd, td]
        if ptype:
            sql = sql + " AND COALESCE(q.plant_category,'')=%s "
            args.append(ptype)
        if project:
            sql = sql + " AND q.name IN (SELECT proposal FROM `tabSales Order` WHERE project=%s) "
            args.append(project)
        if name_filter:
            sql = sql + " AND q.name=%s "
            args.append(name_filter)
        rows = sq(sql + " ORDER BY q.transaction_date DESC LIMIT 200", tuple(args))

    elif stage == "Sales Order":
        sql = (
            "SELECT so.name, COALESCE(so.customer_name,so.name), so.grand_total, "
            "COALESCE(so.advance_paid,0), (so.grand_total - COALESCE(so.advance_paid,0)), "
            "COALESCE(so.per_advance,'0'), DATE(so.transaction_date), " + un_so + ", COALESCE(so.status,'—') "
            "FROM `tabSales Order` so "
            "WHERE so.docstatus=1 AND DATE(so.transaction_date) BETWEEN %s AND %s"
        )
        args = [fd, td]
        if ptype:
            sql = sql + " AND COALESCE(so.plant_category,'')=%s "
            args.append(ptype)
        if project:
            sql = sql + " AND so.project=%s "
            args.append(project)
        if name_filter:
            sql = sql + " AND so.name=%s "
            args.append(name_filter)
        rows = sq(sql + " ORDER BY so.transaction_date DESC LIMIT 200", tuple(args))

    elif stage == "Dispatch":
        sql = (
            "SELECT dn.name, COALESCE(dn.title,dn.customer_name,dn.name), COALESCE(dn.customer_name,'—'), "
            "SUM(dni.qty), DATE(dn.posting_date), " + un_dn + ", COALESCE(dn.late_remark,'—'), COALESCE(dn.status,'—') "
            "FROM `tabDelivery Note` dn "
            "LEFT JOIN `tabDelivery Note Item` dni ON dni.parent=dn.name "
            "WHERE dn.docstatus=1 AND DATE(dn.posting_date) BETWEEN %s AND %s"
        )
        args = [fd, td]
        if ptype:
            sql = sql + " AND dn.project IN (SELECT p.name FROM `tabProject` p WHERE COALESCE(p.plant_category,'')=%s) "
            args.append(ptype)
        if project:
            sql = sql + " AND dn.project=%s "
            args.append(project)
        if name_filter:
            sql = sql + " AND dn.name=%s "
            args.append(name_filter)
        rows = sq(sql + " GROUP BY dn.name ORDER BY dn.posting_date DESC LIMIT 200", tuple(args))

    elif stage == "Installation":
        if table_exists("tabInstallation Note"):
            sql = (
                "SELECT i.name, COALESCE(i.customer_name,i.name), DATE(i.inst_date), "
                "COALESCE(i.territory,'—'), COALESCE(i.status,'—'), COALESCE(i.remarks,'—'), " + un_i + " "
                "FROM `tabInstallation Note` i "
                "WHERE DATE(i.inst_date) BETWEEN %s AND %s"
            )
            args = [fd, td]
            if ptype:
                sql = sql + " AND i.project IN (SELECT p.name FROM `tabProject` p WHERE COALESCE(p.plant_category,'')=%s) "
                args.append(ptype)
            if project:
                sql = sql + " AND i.project=%s "
                args.append(project)
            if name_filter:
                sql = sql + " AND i.name=%s "
                args.append(name_filter)
            rows = sq(sql + " ORDER BY i.inst_date DESC LIMIT 200", tuple(args))
        else:
            return [[None, "Installation Note DocType not found."]]

    elif stage == "Synchronization":
        if not st:
            return [[None, "Synchronization DocType not found."]]
        sql = (
            "SELECT s.name, COALESCE(s.customer_name,s.name), DATE(s.posting_date), "
            "COALESCE(s.liaisoning_status,'—'), COALESCE(DATE(s.synchronization_don_dt),'Pending'), "
            + un_s + ", COALESCE(s.delay_log,'—') "
            "FROM `" + st + "` s "
            "WHERE DATE(s.posting_date) BETWEEN %s AND %s"
        )
        args = [fd, td]
        if ptype:
            sql = sql + " AND s.project IN (SELECT p.name FROM `tabProject` p WHERE COALESCE(p.plant_category,'')=%s) "
            args.append(ptype)
        if project:
            sql = sql + " AND s.project=%s "
            args.append(project)
        if name_filter:
            sql = sql + " AND s.name=%s "
            args.append(name_filter)
        rows = sq(sql + " ORDER BY s.posting_date DESC LIMIT 200", tuple(args))

    elif stage == "Project":
        pm_expr = "COALESCE((SELECT u.full_name FROM `tabUser` u WHERE u.name=p.custom_project_manager LIMIT 1), p.custom_project_manager, '—')"
        if not column_exists("tabProject", "custom_project_manager"):
            pm_expr = "COALESCE((SELECT u.full_name FROM `tabUser` u WHERE u.name=p.owner LIMIT 1), p.owner, '—')"

        sql = (
            "SELECT p.name, COALESCE(p.project_name,p.name), COALESCE(p.status,'—'), "
            "CASE "
            " WHEN LOWER(COALESCE(p.status,''))='completed' THEN 100 "
            " WHEN LOWER(COALESCE(p.status,''))='open' THEN 0 "
            " WHEN LOWER(COALESCE(p.status,'')) IN ('cancelled','canceled') THEN 0 "
            " ELSE COALESCE(p.percent_complete,0) END, "
            "DATE(p.creation), COALESCE(DATE(p.p_end_date), DATE(p.expected_end_date), '—'), " + pm_expr + " "
            "FROM `tabProject` p WHERE 1=1"
        )
        args = []
        if ptype:
            sql = sql + " AND COALESCE(p.plant_category,'')=%s "
            args.append(ptype)
        if project:
            sql = sql + " AND p.name=%s "
            args.append(project)
        if name_filter:
            sql = sql + " AND p.name=%s "
            args.append(name_filter)
        rows = sq(sql + " ORDER BY p.modified DESC LIMIT 200", tuple(args))

    if not rows:
        return [[None, "No records found for this stage in selected period."]]

    return [list(r) for r in rows]


# ══════════════════════════════════════════════════════════════
# Project Hero Data (Project Tab Header Card)
# Mapping exactly as requested by you
# ══════════════════════════════════════════════════════════════

def get_project_data(project):
    if not project:
        frappe.throw("Project name required")

    has_custom_pm = column_exists("tabProject", "custom_project_manager")
    pm_col = "p.owner"
    if has_custom_pm:
        pm_col = "p.custom_project_manager"

    q = (
        "SELECT "
        "p.name, "
        "COALESCE(p.project_name,p.name) AS project_name, "
        "COALESCE(p.status,'Open') AS status, "
        "COALESCE(p.percent_complete,0) AS percent_complete, "
        "COALESCE(p.bill_amt,0) AS bill_amt, "
        "COALESCE(p.advance_amt,0) AS advance_amt, "
        "DATE(p.creation) AS start_date, "
        "p.p_end_date, "
        "p.expected_end_date, "
        "COALESCE(p.customer,p.project_name,p.name,'—') AS customer, "
        "COALESCE((SELECT u.full_name FROM `tabUser` u WHERE u.name=" + pm_col + " LIMIT 1), " + pm_col + ", '—') AS project_manager, "
        "COALESCE(p.solar_capacity,'—') AS capacity, "
        "COALESCE(p.plant_category,'—') AS project_type "
        "FROM `tabProject` p "
        "WHERE p.name=%s LIMIT 1"
    )

    r = sq(q, (project,), as_dict=True)
    d = r[0] if r else {}

    fin_total = safe_float(d.get("bill_amt") or 0)
    fin_recv  = safe_float(d.get("advance_amt") or 0)
    fin_out   = fin_total - fin_recv
    if fin_out < 0:
        fin_out = 0

    proj_status = (d.get("status") or "open").strip().lower()
    pct = safe_float(d.get("percent_complete") or 0)
    if proj_status == "completed":
        pct = 100
    elif proj_status == "cancelled" or proj_status == "canceled":
        pct = 0

    if fin_total <= 0:
        fso = sq("SELECT COALESCE(grand_total,0) FROM `tabSales Order` WHERE project=%s AND docstatus=1 ORDER BY modified DESC LIMIT 1", (project,))
        fin_total = safe_float(fso[0][0] if fso else 0)
        fin_out = fin_total - fin_recv
        if fin_out < 0:
            fin_out = 0

    if (not d.get("capacity") or d.get("capacity") == "—") or (not d.get("project_type") or d.get("project_type") == "—"):
        so = sq("SELECT COALESCE(solar_capacity,'—') AS cap, COALESCE(plant_category,'—') AS cat FROM `tabSales Order` WHERE project=%s AND docstatus=1 ORDER BY modified DESC LIMIT 1", (project,), as_dict=True)
        if so:
            if not d.get("capacity") or d.get("capacity") == "—":
                d["capacity"] = so[0].get("cap")
            if not d.get("project_type") or d.get("project_type") == "—":
                d["project_type"] = so[0].get("cat")

    return {
        "project_name":        d.get("project_name") or project,
        "status":              d.get("status") or "Open",
        "percent_complete":    pct,
        "expected_start_date": d.get("start_date"),
        "expected_end_date":   d.get("p_end_date") or d.get("expected_end_date"),
        "actual_end_date":     None,
        "customer":            d.get("customer") or "—",
        "project_manager":     d.get("project_manager") or "—",
        "capacity":            d.get("capacity") or "—",
        "project_type":        d.get("project_type") or "—",
        "fin_total":           fin_total,
        "fin_recv":            fin_recv,
        "fin_out":             fin_out
    }


# ══════════════════════════════════════════════════════════════
# Project Search
# ══════════════════════════════════════════════════════════════

def search_projects(query):
    q = (query or "").strip()
    if not q:
        return sq("SELECT name, status, customer FROM `tabProject` WHERE status NOT IN ('Cancelled') ORDER BY modified DESC LIMIT 20", as_dict=True)
    like = "%" + q + "%"
    return sq("SELECT name, status, customer FROM `tabProject` WHERE (name LIKE %s OR project_name LIKE %s OR customer LIKE %s) AND status NOT IN ('Cancelled') ORDER BY modified DESC LIMIT 20", (like, like, like), as_dict=True)


# ══════════════════════════════════════════════════════════════
# Router
# ══════════════════════════════════════════════════════════════

action = frappe.form_dict.get("action", "")
preset_ = frappe.form_dict.get("preset")
fd_ = frappe.form_dict.get("from_date")
td_ = frappe.form_dict.get("to_date")
proj_ = frappe.form_dict.get("project")
pt_ = frappe.form_dict.get("project_type")
stage_ = frappe.form_dict.get("stage")
query_ = frappe.form_dict.get("query")
sf_ = frappe.form_dict.get("stage_filter")
nf_ = frappe.form_dict.get("name_filter")
name_ = frappe.form_dict.get("name")

if action == "get_dashboard_data":
    frappe.response["message"] = get_dashboard_data(preset_, fd_, td_, pt_, sf_, nf_)

elif action == "get_process_view":
    nm = name_ or nf_
    frappe.response["message"] = get_process_view(stage_, nm, proj_)

elif action == "get_stage_data":
    frappe.response["message"] = get_stage_data(stage_, preset_, fd_, td_, proj_, pt_, sf_, nf_)

elif action == "get_names_by_stage":
    frappe.response["message"] = get_names_by_stage(stage_)

elif action == "get_project_data":
    frappe.response["message"] = get_project_data(proj_)

elif action == "search_projects":
    frappe.response["message"] = search_projects(query_)
    
elif action == "get_site_images":
    nm = name_ or nf_
    frappe.response["message"] = get_site_images(stage_, nm, proj_)

else:
    frappe.response["message"] = get_dashboard_data(preset_, fd_, td_, pt_, sf_, nf_)
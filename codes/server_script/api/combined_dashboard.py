# ============================================================
#  COMBINED DASHBOARD — SERVER SCRIPT (RESTRICTED-PYTHON SAFE)
#  API Method Name: combined_dashboard
# ============================================================

user     = frappe.session.user
now_date = frappe.utils.today()
today    = str(now_date)

past_history_start = str(frappe.utils.add_months(now_date, -6))
month_start        = str(frappe.utils.get_first_day(now_date))
today_mm_dd        = today[5:10]
month_names_list = ["","January","February","March","April","May","June","July","August","September","October","November","December"]
try:
    current_month_name = month_names_list[int(today[5:7])]
except Exception:
    current_month_name = "This Month"

REMARK_LOG_DOCTYPE = "Remark-Delay Log"

def safe_int(v):
    if not v: return 0
    try: return int(v)
    except Exception: return 0

def safe_flt(v):
    try: return frappe.utils.flt(v or 0)
    except Exception: return 0.0

def safe_date(v):
    if not v: return None
    try: return str(v)[:10]
    except Exception: return None

def safe_pct(n, d):
    if not d: return 0
    return round((n * 100.0) / d, 1)

def fmt_money(v):
    return frappe.utils.fmt_money(safe_flt(v))

def get_avg_tat(doctype, filters):
    records = frappe.db.get_all(doctype, filters=filters, fields=["tat_days"])
    valid = []
    for r in records:
        if r.get("tat_days") is not None:
            valid.append(r.get("tat_days"))
    if not valid: return 0
    return round(sum(valid) / len(valid), 1)

def count_todays_followups():
    try:
        return frappe.db.count(
            "Remark-Delay Log",
            filters=[
                ["parenttype", "in", ["Lead", "Site Survey", "Quotation", "Sales Order", "Delivery Note", "Project", "Liaisoning And Synchronization"]],
                ["log_time", ">=", frappe.utils.today() + " 00:00:00"],
                ["log_time", "<=", frappe.utils.today() + " 23:59:59"]
            ]
        )
    except Exception:
        return 0

def get_followup_logs(from_dt, to_dt, stage_filter=None):
    REMARK_LOG_DOCTYPE_INNER  = "Remark-Delay Log"
    FOLLOWUP_DOCTYPES_INNER   = ["Lead", "Site Survey", "Quotation", "Sales Order", "Delivery Note", "Project", "Liaisoning And Synchronization"]
    FOLLOWUP_NAME_FIELD_INNER = {
        "Lead":                           "lead_name",
        "Site Survey":                    "lead_name",
        "Quotation":                      "customer_name",
        "Sales Order":                    "customer_name",
        "Delivery Note":                  "customer_name",
        "Project":                        "project_name",
        "Liaisoning And Synchronization": "customer_name"
    }
    doctypes_to_query = stage_filter if stage_filter else FOLLOWUP_DOCTYPES_INNER
    rows = []
    for dt in doctypes_to_query:
        try:
            name_field = FOLLOWUP_NAME_FIELD_INNER.get(dt, "name")
            child_rows = frappe.get_all(
                REMARK_LOG_DOCTYPE_INNER,
                filters=[
                    ["parenttype", "=", dt],
                    ["log_time", ">=", from_dt + " 00:00:00"],
                    ["log_time", "<=", to_dt   + " 23:59:59"]
                ],
                fields=["*"],
                order_by="log_time desc",
                limit_page_length=500,
                ignore_permissions=True
            )
            parent_ids = list(set([r.get("parent") for r in child_rows if r.get("parent")]))
            name_map = {}
            if parent_ids:
                parent_rows = frappe.get_all(dt, filters=[["name", "in", parent_ids]], fields=["name", name_field], ignore_permissions=True)
                for pr in parent_rows:
                    name_map[pr.get("name")] = pr.get(name_field) or ""
            for r in child_rows:
                rows.append({
                    "log_id":        r.get("name") or "",
                    "doc_id":        r.get("parent") or "",
                    "stage":         dt,
                    "customer_name": name_map.get(r.get("parent"), ""),
                    "remark":        r.get("remark") or "",
                    "category":      r.get("logreason_category") or r.get("category") or "",
                    "status":        r.get("status") or "",
                    "log_user":      r.get("user") or r.get("owner") or "",
                    "log_time":      str(r.get("log_time") or r.get("creation") or "")
                })
        except Exception:
            pass
    rows.sort(key=lambda x: x.get("log_time") or "", reverse=True)
    return rows

def get_all_names():
    result = []
    try:
        rows = frappe.get_all("Lead", filters={"docstatus": ["<", 2]}, fields=["name", "lead_name"], order_by="creation desc", limit_page_length=500)
        for r in rows: result.append({"name": r.name, "label": r.get("lead_name") or r.name, "stage": "Lead"})
    except Exception: pass
    try:
        rows = frappe.get_all("Site Survey", filters={"docstatus": ["<", 2]}, fields=["name", "lead_name"], order_by="creation desc", limit_page_length=500)
        for r in rows: result.append({"name": r.name, "label": r.get("lead_name") or r.name, "stage": "Site Survey"})
    except Exception: pass
    try:
        rows = frappe.get_all("Quotation", filters={"docstatus": ["<", 2]}, fields=["name", "customer_name"], order_by="creation desc", limit_page_length=500)
        for r in rows: result.append({"name": r.name, "label": r.get("customer_name") or r.name, "stage": "Proposal"})
    except Exception: pass
    try:
        rows = frappe.get_all("Sales Order", filters={"docstatus": ["<", 2]}, fields=["name", "customer_name"], order_by="creation desc", limit_page_length=500)
        for r in rows: result.append({"name": r.name, "label": r.get("customer_name") or r.name, "stage": "Sales Order"})
    except Exception: pass
    try:
        rows = frappe.get_all("Project", filters={"docstatus": ["<", 2]}, fields=["name", "project_name", "customer"], order_by="creation desc", limit_page_length=500)
        for r in rows:
            cust_label = frappe.db.get_value("Customer", r.get("customer"), "customer_name") if r.get("customer") else r.get("project_name")
            result.append({"name": r.name, "label": cust_label or r.name, "stage": "Project"})
    except Exception: pass
    try:
        rows = frappe.get_all("Liaisoning And Synchronization", filters={"docstatus": ["<", 2]}, fields=["name", "customer_name"], order_by="creation desc", limit_page_length=500)
        for r in rows: result.append({"name": r.name, "label": r.get("customer_name") or r.name, "stage": "Synchronization"})
    except Exception: pass
    return result

def get_process_view(stage, name, project):
    result = {}
    customer_id = ""
    project_id  = project or ""
    so_id       = ""
    sync_id     = ""
    lead_id     = ""
    survey_id   = ""

    if project_id and frappe.db.exists("Project", project_id):
        pdata = frappe.db.get_value("Project", project_id, ["customer", "sales_order", "liaisoning_and_sync", "lead", "site_survey"], as_dict=1) or {}
        customer_id = pdata.get("customer") or ""
        so_id       = pdata.get("sales_order") or ""
        sync_id     = pdata.get("liaisoning_and_sync") or ""
        lead_id     = pdata.get("lead") or ""
        survey_id   = pdata.get("site_survey") or ""
    elif name:
        if stage == "Lead":
            lead_id = name
            lead_name_val = frappe.db.get_value("Lead", name, "lead_name") or ""
            if lead_name_val:
                cust = frappe.db.get_value("Customer", {"customer_name": lead_name_val}, "name")
                customer_id = cust or ""
        elif stage == "Site Survey":
            survey_id = name
            lead_id = frappe.db.get_value("Site Survey", name, "lead") or ""
            if lead_id:
                ln = frappe.db.get_value("Lead", lead_id, "lead_name") or ""
                cust = frappe.db.get_value("Customer", {"customer_name": ln}, "name")
                customer_id = cust or ""
        elif stage == "Proposal":
            qt = frappe.db.get_value("Quotation", name, ["party_name", "quotation_to", "lead", "site_survey"], as_dict=1) or {}
            if qt.get("quotation_to") == "Customer": customer_id = qt.get("party_name") or ""
            elif qt.get("quotation_to") == "Lead": lead_id = qt.get("party_name") or ""
            if not lead_id: lead_id = qt.get("lead") or ""
            survey_id = qt.get("site_survey") or ""
        elif stage == "Sales Order":
            so_id = name
            so_data = frappe.db.get_value("Sales Order", name, ["customer", "project", "lead", "site_survey"], as_dict=1) or {}
            customer_id = so_data.get("customer") or ""
            project_id  = so_data.get("project") or ""
            lead_id     = so_data.get("lead") or ""
            survey_id   = so_data.get("site_survey") or ""
        elif stage == "Project":
            project_id = name
            pdata = frappe.db.get_value("Project", name, ["customer", "sales_order", "liaisoning_and_sync", "lead", "site_survey"], as_dict=1) or {}
            customer_id = pdata.get("customer") or ""
            so_id       = pdata.get("sales_order") or ""
            sync_id     = pdata.get("liaisoning_and_sync") or ""
            lead_id     = pdata.get("lead") or ""
            survey_id   = pdata.get("site_survey") or ""
        elif stage == "Synchronization":
            sync_id = name
            sy = frappe.db.get_value("Liaisoning And Synchronization", name, ["customer", "sales_order", "project", "lead", "site_survey"], as_dict=1) or {}
            customer_id = sy.get("customer") or ""
            so_id       = sy.get("sales_order") or ""
            project_id  = sy.get("project") or ""
            lead_id     = sy.get("lead") or ""
            survey_id   = sy.get("site_survey") or ""

    result["lead"] = {"reached": False}
    result["lead_doc"] = ""
    try:
        lead_rows = []
        if lead_id: lead_rows = frappe.get_all("Lead", filters={"name": lead_id}, fields=["name","lead_name","mobile_no","source","lead_owner","status","creation_date","stage_status"], limit_page_length=1)
        cust_name = frappe.db.get_value("Customer", customer_id, "customer_name") if customer_id else ""
        if not lead_rows and cust_name:
            parts = [p for p in cust_name.split(" ") if p]
            fuzzy_name = ("%" + parts[0] + "%" + parts[-1] + "%") if len(parts) >= 2 else ("%" + cust_name + "%")
            lead_rows = frappe.get_all("Lead", filters=[["lead_name", "like", fuzzy_name]], fields=["name","lead_name","mobile_no","source","lead_owner","status","creation_date","stage_status"], order_by="creation desc", limit_page_length=1)
        if not lead_rows and customer_id: lead_rows = frappe.get_all("Lead", filters={"customer": customer_id}, fields=["name","lead_name","mobile_no","source","lead_owner","status","creation_date","stage_status"], order_by="creation desc", limit_page_length=1)
        if lead_rows:
            ld = lead_rows[0]
            result["lead_doc"] = ld.get("name") or ""
            lead_id = result["lead_doc"]
            result["lead"] = {"reached": True, "customer": ld.get("lead_name") or "—", "mobile": ld.get("mobile_no") or "—", "source": ld.get("source") or "—", "actor": ld.get("lead_owner") or "—", "status": ld.get("status") or "—", "date": safe_date(ld.get("creation_date")), "next_step": ld.get("stage_status") or "—"}
    except Exception: pass

    result["survey"] = {"reached": False}
    result["survey_doc"] = ""
    try:
        sv_rows = []
        if survey_id: sv_rows = frappe.get_all("Site Survey", filters={"name": survey_id}, fields=["name","lead_name","surveyed_by","solar_capacity","site_type","plant_category","location_details","survey_date","status"], limit_page_length=1)
        if not sv_rows and lead_id: sv_rows = frappe.get_all("Site Survey", filters={"lead": lead_id}, fields=["name","lead_name","surveyed_by","solar_capacity","site_type","plant_category","location_details","survey_date","status"], order_by="creation desc", limit_page_length=1)
        if not sv_rows and cust_name:
            parts = [p for p in cust_name.split(" ") if p]
            fuzzy_name = ("%" + parts[0] + "%" + parts[-1] + "%") if len(parts) >= 2 else ("%" + cust_name + "%")
            sv_rows = frappe.get_all("Site Survey", filters=[["lead_name", "like", fuzzy_name]], fields=["name","lead_name","surveyed_by","solar_capacity","site_type","plant_category","location_details","survey_date","status"], order_by="creation desc", limit_page_length=1)
        if sv_rows:
            sv = sv_rows[0]
            result["survey_doc"] = sv.get("name") or ""
            result["survey"] = {"reached": True, "customer": sv.get("lead_name") or "—", "actor": sv.get("surveyed_by") or "—", "plant_category": sv.get("plant_category") or "—", "capacity": sv.get("solar_capacity") or "—", "site_type": sv.get("site_type") or "—", "location": sv.get("location_details") or "—", "date": safe_date(sv.get("survey_date")), "status": sv.get("status") or "—"}
    except Exception: pass

    result["proposal"] = {"reached": False}
    result["proposal_doc"] = ""
    try:
        qt_rows = []
        if customer_id: qt_rows = frappe.get_all("Quotation", filters={"party_name": customer_id, "docstatus": ["<", 2]}, fields=["name","customer_name","manager","solar_capacity","rounded_total","transaction_date","status","next_followup_date"], order_by="creation desc", limit_page_length=1)
        if not qt_rows and cust_name: qt_rows = frappe.get_all("Quotation", filters=[["customer_name","like","%" + cust_name + "%"],["docstatus","<",2]], fields=["name","customer_name","manager","solar_capacity","rounded_total","transaction_date","status","next_followup_date"], order_by="creation desc", limit_page_length=1)
        if not qt_rows and name and stage == "Proposal": qt_rows = frappe.get_all("Quotation", filters={"name": name, "docstatus": ["<", 2]}, fields=["name","customer_name","manager","solar_capacity","rounded_total","transaction_date","status","next_followup_date"], limit_page_length=1)
        if qt_rows:
            qt = qt_rows[0]
            result["proposal"] = {"reached": True, "customer": qt.get("customer_name") or "—", "actor": qt.get("manager") or "—", "capacity": qt.get("solar_capacity") or "—", "amount": safe_flt(qt.get("rounded_total")), "date": safe_date(qt.get("transaction_date")), "status": qt.get("status") or "—", "next_step": safe_date(qt.get("next_followup_date"))}
            result["proposal_doc"] = qt.get("name") or ""
    except Exception: pass

    result["sales_order"] = {"reached": False}
    result["sales_order_doc"] = ""
    try:
        so_rows = []
        if so_id and frappe.db.exists("Sales Order", so_id): so_rows = frappe.get_all("Sales Order", filters={"name": so_id}, fields=["name","customer_name","manager","rounded_total","advance_paid","per_advance","transaction_date","status"], limit_page_length=1)
        elif customer_id: so_rows = frappe.get_all("Sales Order", filters={"customer": customer_id, "docstatus": ["<", 2]}, fields=["name","customer_name","manager","rounded_total","advance_paid","per_advance","transaction_date","status"], order_by="creation desc", limit_page_length=1)
        elif lead_id: so_rows = frappe.get_all("Sales Order", filters={"lead": lead_id, "docstatus": ["<", 2]}, fields=["name","customer_name","manager","rounded_total","advance_paid","per_advance","transaction_date","status"], order_by="creation desc", limit_page_length=1)
        if not so_rows and name and stage == "Sales Order": so_rows = frappe.get_all("Sales Order", filters={"name": name}, fields=["name","customer_name","manager","rounded_total","advance_paid","per_advance","transaction_date","status"], limit_page_length=1)
        if so_rows:
            so = so_rows[0]
            if not so_id: so_id = so.get("name") or ""
            out = safe_flt(so.get("rounded_total")) - safe_flt(so.get("advance_paid"))
            result["sales_order"] = {"reached": True, "customer": so.get("customer_name") or "—", "actor": so.get("manager") or "—", "amount": safe_flt(so.get("rounded_total")), "advance": safe_flt(so.get("advance_paid")), "outstanding": out, "adv_pct": str(so.get("per_advance") or 0) + "%", "date": safe_date(so.get("transaction_date")), "status": so.get("status") or "—"}
            result["sales_order_doc"] = so.get("name") or ""
    except Exception: pass

    result["dispatch"] = {"reached": False}
    result["dispatch_doc"] = ""
    try:
        dn_rows = []
        if project_id: dn_rows = frappe.get_all("Delivery Note", filters={"project": project_id, "docstatus": ["<", 2]}, fields=["name","customer_name","manager","posting_date","status","late_remark"], order_by="creation desc", limit_page_length=1)
        if not dn_rows and so_id: dn_rows = frappe.get_all("Delivery Note", filters={"against_sales_order": so_id, "docstatus": ["<", 2]}, fields=["name","customer_name","manager","posting_date","status","late_remark"], order_by="creation desc", limit_page_length=1)
        if not dn_rows and customer_id: dn_rows = frappe.get_all("Delivery Note", filters={"customer": customer_id, "docstatus": ["<", 2]}, fields=["name","customer_name","manager","posting_date","status","late_remark"], order_by="creation desc", limit_page_length=1)
        if dn_rows:
            dn = dn_rows[0]
            result["dispatch"] = {"reached": True, "customer": dn.get("customer_name") or "—", "actor": dn.get("manager") or "—", "date": safe_date(dn.get("posting_date")), "status": dn.get("status") or "—", "remark": dn.get("late_remark") or "—"}
            result["dispatch_doc"] = dn.get("name") or ""
    except Exception: pass

    result["project"] = {"reached": False}
    result["project_doc"] = ""
    try:
        pj_rows = []
        if project_id and frappe.db.exists("Project", project_id): pj_rows = frappe.get_all("Project", filters={"name": project_id}, fields=["name","project_name","custom_project_manager","percent_complete","expected_start_date","status"], limit_page_length=1)
        elif customer_id: pj_rows = frappe.get_all("Project", filters={"customer": customer_id, "docstatus": ["<", 2]}, fields=["name","project_name","custom_project_manager","percent_complete","expected_start_date","status"], order_by="creation desc", limit_page_length=1)
        elif lead_id: pj_rows = frappe.get_all("Project", filters={"lead": lead_id, "docstatus": ["<", 2]}, fields=["name","project_name","custom_project_manager","percent_complete","expected_start_date","status"], order_by="creation desc", limit_page_length=1)
        if pj_rows:
            pj = pj_rows[0]
            if not project_id: project_id = pj.get("name") or ""
            pm = pj.get("custom_project_manager") or ""
            pm_name = frappe.db.get_value("User", pm, "full_name") or pm if pm else "—"
            result["project"] = {"reached": True, "customer": pj.get("project_name") or project_id, "actor": pm_name, "pct": str(safe_flt(pj.get("percent_complete"))) + "%", "date": safe_date(pj.get("expected_start_date")), "status": pj.get("status") or "—"}
            result["project_doc"] = pj.get("name") or ""
    except Exception: pass

    result["sync"] = {"reached": False}
    result["sync_doc"] = ""
    try:
        sy_rows = []
        if sync_id and frappe.db.exists("Liaisoning And Synchronization", sync_id): sy_rows = frappe.get_all("Liaisoning And Synchronization", filters={"name": sync_id}, fields=["name","customer_name","customer","liaisoning_status","posting_date","synchronization_don_dt","delay_log"], limit_page_length=1)
        elif project_id: sy_rows = frappe.get_all("Liaisoning And Synchronization", filters={"project": project_id, "docstatus": ["<", 2]}, fields=["name","customer_name","customer","liaisoning_status","posting_date","synchronization_don_dt","delay_log"], order_by="creation desc", limit_page_length=1)
        elif so_id: sy_rows = frappe.get_all("Liaisoning And Synchronization", filters={"sales_order": so_id, "docstatus": ["<", 2]}, fields=["name","customer_name","customer","liaisoning_status","posting_date","synchronization_don_dt","delay_log"], order_by="creation desc", limit_page_length=1)
        elif customer_id: sy_rows = frappe.get_all("Liaisoning And Synchronization", filters={"customer": customer_id, "docstatus": ["<", 2]}, fields=["name","customer_name","customer","liaisoning_status","posting_date","synchronization_don_dt","delay_log"], order_by="creation desc", limit_page_length=1)
        elif lead_id: sy_rows = frappe.get_all("Liaisoning And Synchronization", filters={"lead": lead_id, "docstatus": ["<", 2]}, fields=["name","customer_name","customer","liaisoning_status","posting_date","synchronization_don_dt","delay_log"], order_by="creation desc", limit_page_length=1)
        if not sy_rows and name and stage == "Synchronization": sy_rows = frappe.get_all("Liaisoning And Synchronization", filters={"name": name}, fields=["name","customer_name","customer","liaisoning_status","posting_date","synchronization_don_dt","delay_log"], limit_page_length=1)
        if sy_rows:
            sy = sy_rows[0]
            result["sync"] = {"reached": True, "customer": sy.get("customer_name") or "—", "actor": sy.get("customer") or "—", "status": sy.get("liaisoning_status") or "—", "date": safe_date(sy.get("posting_date")), "sync_done": safe_date(sy.get("synchronization_don_dt")) or "Pending", "remark": sy.get("delay_log") or "—"}
            result["sync_doc"] = sy.get("name") or ""
    except Exception: pass

    return result

def get_site_images(stage, name, project):
    images = []
    doctypes_to_check = []
    if project and frappe.db.exists("Project", project):
        pdata = frappe.db.get_value("Project", project, ["site_survey", "liaisoning_and_sync"], as_dict=1) or {}
        doctypes_to_check = [("Site Survey", pdata.get("site_survey")), ("Project", project), ("Liaisoning And Synchronization", pdata.get("liaisoning_and_sync"))]
        dn_rows = frappe.get_all("Delivery Note", filters={"project": project, "docstatus": ["<", 2]}, fields=["name"], limit_page_length=5)
        for dn in dn_rows: doctypes_to_check.append(("Delivery Note", dn.name))
    elif name:
        if stage == "Site Survey": doctypes_to_check = [("Site Survey", name)]
        elif stage == "Project": doctypes_to_check = [("Project", name)]
        elif stage == "Dispatch": doctypes_to_check = [("Delivery Note", name)]
        elif stage == "Synchronization": doctypes_to_check = [("Liaisoning And Synchronization", name)]
        else:
            doctypes_to_check = [("Site Survey", None), ("Project", None)]
            lead_val = None
            if stage == "Lead": lead_val = frappe.db.get_value("Site Survey", {"lead": name}, "name")
            if lead_val: doctypes_to_check = [("Site Survey", lead_val)]
    exts = (".jpg", ".jpeg", ".png", ".gif", ".webp")
    seen = set()
    for item in doctypes_to_check:
        dt = item[0]
        dn = item[1]
        if not dn: continue
        try:
            files = frappe.get_all("File", filters={"attached_to_doctype": dt, "attached_to_name": dn, "is_folder": 0}, fields=["file_name", "file_url", "creation"], order_by="creation asc", limit_page_length=30)
            for f in files:
                fu = (f.get("file_url") or "").lower()
                fn = (f.get("file_name") or "").lower()
                if any(fu.endswith(e) or fn.endswith(e) for e in exts):
                    key = f.get("file_url")
                    if key and key not in seen:
                        seen.add(key)
                        images.append({"file_name": f.get("file_name"), "file_url": f.get("file_url"), "doctype": dt, "docname": dn})
        except Exception: pass
    return images

# ────────────────────────────────────────────────────────────
#  EMPLOYEE LOOKUP
# ────────────────────────────────────────────────────────────
employee = frappe.db.get_value(
    "Employee",
    {"company_email": user, "status": "Active"},
    ["name", "employee_name", "designation", "department", "holiday_list", "date_of_joining"],
    as_dict=True
)

if not employee:
    ui = frappe.db.get_value("User", user, ["full_name", "first_name"], as_dict=True)
    user_prefix = user.split("@")[0].capitalize()
    employee = {
        "name": "", "employee_name": ui.get("full_name") if ui else user_prefix,
        "designation": "Employee", "department": "", "holiday_list": "", "date_of_joining": ""
    }

emp_id       = employee.get("name")
emp_name     = employee.get("employee_name") or user.split("@")[0].capitalize()
display_name = emp_name

# ────────────────────────────────────────────────────────────
#  ATTENDANCE
# ────────────────────────────────────────────────────────────
attendance = {"today_status": "Not Marked", "month_present": 0, "absent": 0, "half_day": 0, "wfh": 0, "records": []}
if emp_id:
    today_att = frappe.db.get_value("Attendance", {"employee": emp_id, "attendance_date": today, "docstatus": 1}, "status")
    attendance["today_status"] = today_att or "Not Marked"
    att_logs = frappe.db.get_all("Attendance", filters={"employee": emp_id, "attendance_date": [">=", past_history_start], "docstatus": 1}, fields=["attendance_date", "status"], order_by="attendance_date desc")
    for a in att_logs:
        status = a.get("status") or ""
        log_date_str = str(a.get("attendance_date") or "")
        if log_date_str >= month_start:
            if status == "Present":
                attendance["month_present"] = attendance.get("month_present", 0) + 1
            elif status == "Absent":
                attendance["absent"] = attendance.get("absent", 0) + 1
            elif status == "Half Day":
                attendance["half_day"] = attendance.get("half_day", 0) + 1
            elif status in ["Work From Home", "WFH", "Work from Home"]:
                attendance["wfh"] = attendance.get("wfh", 0) + 1
        attendance["records"].append({"date": log_date_str, "status": status})

# ────────────────────────────────────────────────────────────
#  LEAVES
# ────────────────────────────────────────────────────────────
leaves = []
if emp_id:
    allocations = frappe.db.get_all("Leave Allocation", filters={"employee": emp_id, "docstatus": 1}, fields=["leave_type", "total_leaves_allocated"])
    for a in allocations:
        lt = a.get("leave_type")
        total = safe_int(a.get("total_leaves_allocated"))
        used = frappe.db.count("Leave Application", {"employee": emp_id, "leave_type": lt, "status": "Approved", "docstatus": 1})
        avail = total - used
        leaves.append({"leave_type": lt, "total_leaves": total, "used_leaves": used, "unused_leaves": max(avail, 0)})

# ────────────────────────────────────────────────────────────
#  PAYSLIPS
# ────────────────────────────────────────────────────────────
payslips = []
if emp_id:
    month_names = ["","January","February","March","April","May","June","July","August","September","October","November","December"]
    slips = frappe.db.get_all("Salary Slip", filters={"employee": emp_id, "docstatus": 1}, fields=["name","start_date","net_pay"], order_by="start_date desc", limit=12)
    for s in slips:
        sd = str(s.get("start_date") or "")
        y_str = sd[0:4] if len(sd) >= 10 else "-"
        m_idx = safe_int(sd[5:7]) if len(sd) >= 10 else 0
        payslips.append({"name": s.get("name"), "amount": round(s.get("net_pay") or 0), "month": month_names[m_idx] if 0 < m_idx < 13 else "-", "year": y_str})

# ────────────────────────────────────────────────────────────
#  HOLIDAYS
# ────────────────────────────────────────────────────────────
holidays = []
hl = employee.get("holiday_list")
if hl:
    h_list = frappe.db.get_all("Holiday", filters={"parent": hl, "holiday_date": [">=", today]}, fields=["holiday_date","description"], order_by="holiday_date asc", limit=25)
    for h in h_list: holidays.append({"holiday_date": str(h.get("holiday_date") or ""), "description": h.get("description") or ""})

# ────────────────────────────────────────────────────────────
#  NOTIFICATIONS
# ────────────────────────────────────────────────────────────
notifications = []

active_colleagues = frappe.db.get_all(
    "Employee",
    filters={"status": "Active"},
    fields=["employee_name", "company_email", "date_of_birth", "date_of_joining"]
)
for c in active_colleagues:
    c_name  = c.get("employee_name") or "Colleague"
    c_first = c_name.split(" ")[0].capitalize()
    is_self = (c.get("company_email") == user)
    dob = str(c.get("date_of_birth") or "")
    if len(dob) >= 10 and dob[5:10] == today_mm_dd:
        notifications.append({
            "type":    "birthday",
            "subject": "Happy Birthday to You! Have a wonderful day!" if is_self else "It's " + c_first + "'s Birthday today!"
        })
    doj = str(c.get("date_of_joining") or "")
    if len(doj) >= 10 and doj[5:10] == today_mm_dd:
        years_spent = safe_int(today[0:4]) - safe_int(doj[0:4]) or 0
        if years_spent > 0:
            notifications.append({
                "type":    "anniversary",
                "subject": "Happy Work Anniversary! Thank you for " + str(years_spent) + " years!" if is_self else c_first + " is celebrating " + str(years_spent) + " years today!"
            })

open_leads_notif = frappe.db.count("Lead", {"lead_owner": user, "status": "Open"})
if open_leads_notif:
    notifications.append({"type": "system", "subject": str(open_leads_notif) + " leads need follow-up", "date": today})

pending_surveys_notif = frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Open"})
if pending_surveys_notif:
    notifications.append({"type": "system", "subject": str(pending_surveys_notif) + " site surveys pending", "date": today})

pending_quotes_notif = frappe.db.count("Quotation", {"status": "Open", "owner": user})
if pending_quotes_notif:
    notifications.append({"type": "system", "subject": str(pending_quotes_notif) + " pipeline proposals open", "date": today})

# ── ToDo Notifications — ALL users see their own todos ──
try:
    todo_notifs = frappe.db.get_all(
        "ToDo",
        filters=[["allocated_to", "=", user], ["status", "=", "Open"]],
        fields=["name", "description", "date", "priority", "reference_type", "reference_name"],
        order_by="date asc",
        limit_page_length=5
    )
    for t in todo_notifs:
        raw_desc = str(t.get("description") or "Task")
        clean_desc = raw_desc
        while "<" in clean_desc and ">" in clean_desc:
            start = clean_desc.find("<")
            end = clean_desc.find(">")
            if start < end:
                clean_desc = clean_desc[:start] + clean_desc[end+1:]
            else:
                break
        clean_desc = clean_desc.strip()
        if not clean_desc: clean_desc = "Task"
        due_date = str(t.get("date") or "")
        notifications.append({
            "type":           "system",
            "subject":        clean_desc,
            "date":           due_date,
            "reference_type": t.get("reference_type") or "",
            "reference_name": t.get("reference_name") or ""
        })
except Exception:
    pass

# ────────────────────────────────────────────────────────────
#  ROLE BLOCKS
# ────────────────────────────────────────────────────────────
kpi_data            = []
plan_data           = []
pending_tasks       = []
performance         = {}
actions             = {}
process_label       = ""
quick_link_report   = {}
purchase_date_range = {}

sync_exists = frappe.db.exists("DocType", "Liaisoning And Synchronization")

# ── MANISHA (CRM & Sales) ──────────────────────────────────
if user == "manisha.sadbhavrenewable@gmail.com":
    process_label = display_name + " - CRM & Sales"

    def fmt_r(v):
        n = frappe.utils.flt(v or 0)
        if n >= 10000000: return "Rs." + str(round(n / 10000000.0, 2)) + " Cr"
        if n >= 100000: return "Rs." + str(round(n / 100000.0, 2)) + " L"
        return "Rs." + str(int(n)) if n > 0 else "Rs.0"

    open_leads_no_proposal_count = 0
    leads_with_proposal = []
    try:
        qt_rows = frappe.db.sql(
            """SELECT DISTINCT
                CASE
                    WHEN lead IS NOT NULL AND lead != '' THEN lead
                    ELSE party_name
                END as lead_id
            FROM `tabQuotation`
            WHERE quotation_to = 'Lead'
            AND (
                (lead IS NOT NULL AND lead != '')
                OR
                (party_name IS NOT NULL AND party_name != '')
            )""",
            as_dict=True
        )
        for qt in qt_rows:
            if qt.get("lead_id"):
                leads_with_proposal.append(qt.get("lead_id"))
        total_leads = frappe.db.sql("SELECT COUNT(name) as cnt FROM `tabLead` WHERE docstatus < 2", as_dict=True)
        total_count = (total_leads[0].get("cnt") or 0) if total_leads else 0
        open_leads_no_proposal_count = total_count - len(leads_with_proposal)
    except Exception:
        open_leads_no_proposal_count = 0

    adv_recd_so_draft_count = 0
    try:
        adv_recd_so_draft_count = frappe.db.count("Sales Order", {"manager": user, "advance_paid": [">", 0], "docstatus": 0}) or 0
    except Exception: pass

    so_created_by_me = 0
    try:
        so_created_by_me = frappe.db.count("Sales Order", {"owner": user}) or 0
    except Exception: pass

    ongoing_projects_count = 0
    try:
        ongoing_projects_count = frappe.db.count("Project", {"status": "Open", "docstatus": ["<", 2]}) or 0
    except Exception: pass

    total_invoice_amt  = 0.0
    total_received_amt = 0.0
    total_pending_amt  = 0.0
    try:
        res = frappe.db.sql(
            "SELECT SUM(IFNULL(rounded_total, IFNULL(grand_total, 0))) as inv, SUM(IFNULL(advance_paid, 0)) as rec FROM `tabSales Order` WHERE manager = %s AND docstatus = 1",
            (user,), as_dict=True
        )
        if res:
            total_invoice_amt  = res[0].get("inv") or 0.0
            total_received_amt = res[0].get("rec") or 0.0
            total_pending_amt  = max(frappe.utils.flt(total_invoice_amt) - frappe.utils.flt(total_received_amt), 0.0)
    except Exception: pass

    assigned_proposals = 0
    try:
        assigned_proposals = frappe.db.count("Quotation", {"manager": user, "docstatus": ["<", 2]}) or 0
    except Exception: pass

    followups_done_today = 0
    try:
        followups_done_today = count_todays_followups()
    except Exception: pass

    Total_proposal_made = 0
    try:
        Total_proposal_made = frappe.db.count("Quotation", {"docstatus": ["<", 2]}) or 0
    except Exception: pass

    billing_pending_count = 0
    try:
        billing_pending_count = frappe.db.count("Sales Order", {"manager": user, "docstatus": 1, "status": "To Bill"}) or 0
    except Exception: pass

    kpi_data = [
        {"title": "Open Leads (No Proposal)", "count": open_leads_no_proposal_count, "route": "Lead",         "filter": {"name": ["not in", leads_with_proposal or ["NONE"]]}},
        {"title": "Sales Order Pending",       "count": adv_recd_so_draft_count,      "route": "Sales Order", "filter": {"manager": user, "advance_paid": [">", 0], "docstatus": 0}},
        {"title": "Sales Orders Created",      "count": so_created_by_me,             "route": "Sales Order", "filter": {"owner": user}},
        {"title": "Ongoing Projects",          "count": ongoing_projects_count,        "route": "Project",     "filter": {"status": "Open"}},
        {"title": "Invoice Amount (Total)",    "count": fmt_r(total_invoice_amt),      "route": "Sales Order", "filter": {"manager": user, "docstatus": 1}},
        {"title": "Amount Received",           "count": fmt_r(total_received_amt),     "route": "Sales Order", "filter": {"manager": user, "docstatus": 1, "advance_paid": [">", 0]}},
        {"title": "Amount Pending",            "count": fmt_r(total_pending_amt),      "route": "Sales Order", "filter": {"manager": user, "docstatus": 1, "advance_paid": ["<", "grand_total"]}},
        {"title": "Assigned Proposals",        "count": assigned_proposals,            "route": "Quotation",   "filter": {"manager": user, "docstatus": ["<", 2]}},
        {"title": "Follow Ups Done Today",     "count": followups_done_today,          "route": "",            "filter": {}, "action": "followup_modal"},
        {"title": "Total Proposal Made",       "count": Total_proposal_made,           "route": "Quotation",   "filter": {"docstatus": ["<", 2]}},
        {"title": "Billing Pending",           "count": billing_pending_count,         "route": "Sales Order", "filter": {"manager": user, "docstatus": 1, "status": "To Bill"}}
    ]

    plan_data = [
        {"title": "Deliveries Sent Today", "count": frappe.db.count("Sales Order", {"manager": user, "docstatus": 1, "delivery_date": today, "status": "To Deliver and Bill"}), "route": "Sales Order", "filter": {"manager": user, "docstatus": 1, "delivery_date": today, "status": "To Deliver and Bill"}},
        {"title": "Billing Due Today",     "count": frappe.db.count("Sales Order", {"manager": user, "docstatus": 1, "delivery_date": today, "status": "To Bill"}),             "route": "Sales Order", "filter": {"manager": user, "docstatus": 1, "delivery_date": today, "status": "To Bill"}}
    ]

    try:
        for d in frappe.db.get_all("Sales Order", filters={"manager": user, "docstatus": 1, "delivery_date": [">=", today], "status": "To Deliver and Bill"}, fields=["name", "customer_name", "delivery_date", "transaction_date"], order_by="delivery_date asc", limit_page_length=4):
            del_date_str = str(d.get("delivery_date") or "")
            tat_days = "-"
            if del_date_str and del_date_str < today:
                try:
                    tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(del_date_str)).days
                except Exception: tat_days = "-"
            pending_tasks.append({"doctype": "Sales Order", "type": "Delivery Pending", "client": d.get("customer_name") or "-", "ref": d.get("name"), "date": del_date_str, "assigned_date": str(d.get("transaction_date") or ""), "tat": tat_days, "is_delayed": tat_days != "-" and tat_days > 0})

        for d in frappe.db.get_all("Sales Order", filters={"manager": user, "docstatus": 1, "delivery_date": [">=", today], "status": "To Bill"}, fields=["name", "customer_name", "delivery_date", "transaction_date"], order_by="delivery_date asc", limit_page_length=3):
            del_date_str = str(d.get("delivery_date") or "")
            tat_days = "-"
            if del_date_str and del_date_str < today:
                try:
                    tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(del_date_str)).days
                except Exception: tat_days = "-"
            pending_tasks.append({"doctype": "Sales Order", "type": "Billing Pending", "client": d.get("customer_name") or "-", "ref": d.get("name"), "date": del_date_str, "assigned_date": str(d.get("transaction_date") or ""), "tat": tat_days, "is_delayed": tat_days != "-" and tat_days > 0})

        for d in frappe.db.get_all("Sales Order", filters={"manager": user, "docstatus": 1, "project_status": "Not Created"}, fields=["name", "customer_name", "delivery_date", "transaction_date"], order_by="delivery_date asc", limit_page_length=3):
            del_date_str = str(d.get("delivery_date") or "")
            tat_days = "-"
            if del_date_str and del_date_str < today:
                try:
                    tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(del_date_str)).days
                except Exception: tat_days = "-"
            pending_tasks.append({"doctype": "Sales Order", "type": "Project Not Started", "client": d.get("customer_name") or "-", "ref": d.get("name"), "date": del_date_str, "assigned_date": str(d.get("transaction_date") or ""), "tat": tat_days, "is_delayed": tat_days != "-" and tat_days > 0})

        for d in frappe.db.get_all("Sales Order", filters={"manager": user, "advance_paid": [">", 0], "docstatus": 0}, fields=["name", "customer_name", "delivery_date", "transaction_date"], order_by="delivery_date asc", limit_page_length=3):
            del_date_str = str(d.get("delivery_date") or "")
            tat_days = "-"
            if del_date_str and del_date_str < today:
                try:
                    tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(del_date_str)).days
                except Exception: tat_days = "-"
            pending_tasks.append({"doctype": "Sales Order", "type": "Advance Rcvd, SO Draft", "client": d.get("customer_name") or "-", "ref": d.get("name"), "date": del_date_str, "assigned_date": str(d.get("transaction_date") or ""), "tat": tat_days, "is_delayed": tat_days != "-" and tat_days > 0})
    except Exception: pass

    month_followups = 0
    try:
        month_followups = frappe.db.count("Remark-Delay Log", filters=[["parenttype", "in", ["Lead","Site Survey","Quotation","Sales Order","Delivery Note","Project","Liaisoning And Synchronization"]], ["log_time", ">=", month_start + " 00:00:00"]]) or 0
    except Exception: pass

    performance = {
        "label1": "Proposals Converted", "value1": frappe.db.count("Sales Order", {"manager": user, "docstatus": 1, "transaction_date": [">=", month_start]}),
        "label2": "Follow Ups Done",     "value2": month_followups
    }
    actions = {"btn1_label": "New Sales Order", "btn1_type": "new_doc", "btn1_target": "Sales Order", "btn2_label": "View Pipeline", "btn2_type": "list_route", "btn2_target": "Quotation", "btn2_filter": {"status": "Open"}, "btn2_visible": True}

# ── MANAGEMENT ─────────────────────────────────────────────
elif user in ["mp@sadbhavrenewables.com","ksk@sadbhavrenewables.com","sandeep@sadbhavrenewables.com"]:
    process_label = display_name + " - Management Overview"
    kpi_data = [
        {"title":"Open Leads",          "count":frappe.db.count("Lead",{"status":"Open"}),                                                                                                               "tat":get_avg_tat("Lead",{"status":"Open"}),           "route":"Lead",                            "filter":{"status":"Open"}},
        {"title":"Site Surveys Pending","count":frappe.db.count("Site Survey",{"status":"Open"}),                                                                                                         "tat":get_avg_tat("Site Survey",{"status":"Open"}),    "route":"Site Survey",                     "filter":{"status":"Open"}},
        {"title":"Proposals Pending",   "count":frappe.db.count("Quotation",{"status":"Draft"}),                                                                                                          "tat":get_avg_tat("Quotation",{"status":"Draft"}),     "route":"Quotation",                       "filter":{"status":"Draft"}},
        {"title":"Proposals in Follow-up","count":frappe.db.count("Quotation",{"status":"Open"}),                                                                                                         "tat":get_avg_tat("Quotation",{"status":"Open"}),      "route":"Quotation",                       "filter":{"status":"Open"}},
        {"title":"Sales Orders Active", "count":frappe.db.count("Sales Order",{"status":"To Deliver and Bill"}),                                                                                          "tat":0,                                               "route":"Sales Order",                     "filter":{"status":"To Deliver and Bill"}},
        {"title":"Dispatch Pending",    "count":frappe.db.count("Delivery Note",{"status":"Draft"}),                                                                                                      "tat":0,                                               "route":"Delivery Note",                   "filter":{"status":"Draft"}},
        {"title":"Liaisoning Pending",  "count":frappe.db.count("Liaisoning And Synchronization",{"liaisoning_status":["in",["New","In Process"]]}) if sync_exists else 0, "tat":0, "route":"Liaisoning And Synchronization" if sync_exists else "", "filter":{"liaisoning_status":"New"}}
    ]
    plan_data = [
        {"title":"Proposal Follow-ups Due","count":frappe.db.count("Quotation",{"exp_nxstp_dt":today,"status":"Open"}), "route":"Quotation",     "filter":{"exp_nxstp_dt":today,"status":"Open"}},
        {"title":"Payments to Verify",     "count":frappe.db.count("Sales Order",{"status":"Draft"}),                   "route":"Sales Order",   "filter":{"status":"Draft"}},
        {"title":"Dispatches Today",       "count":frappe.db.count("Delivery Note",{"posting_date":today}),              "route":"Delivery Note", "filter":{"posting_date":today}}
    ]
    for d in frappe.db.get_all("Lead",filters={"status":"Open"},fields=["name","lead_name","exp_nxstp_dt","tat_days"],limit=3):
        pending_tasks.append({"doctype":"Lead","type":"Lead Follow-up","client":d.get("lead_name"),"ref":d.get("name"),"date":str(d.get("exp_nxstp_dt") or ""),"assigned_date":"","tat":d.get("tat_days") or "-","is_delayed": (d.get("tat_days") or 0) > 0})
    for d in frappe.db.get_all("Sales Order",filters={"status":"Draft"},fields=["name","customer_name","transaction_date","tat_days"],limit=3):
        pending_tasks.append({"doctype":"Sales Order","type":"Payment Verification","client":d.get("customer_name"),"ref":d.get("name"),"date":str(d.get("transaction_date") or ""),"assigned_date":"","tat":d.get("tat_days") or "-","is_delayed": (d.get("tat_days") or 0) > 0})
    performance = {
        "label1":"Leads This Month",        "value1":frappe.db.count("Lead",{"creation":[">=",month_start]}),
        "label2":"Sales Orders This Month", "value2":frappe.db.count("Sales Order",{"transaction_date":[">=",month_start]}),
        "label3":"Dispatched This Month",   "value3":frappe.db.count("Delivery Note",{"status":"Submitted","posting_date":[">=",month_start]})
    }

# ── STOCK MANAGER ──────────────────────────────────────────
elif frappe.db.exists("Has Role", {"parent": user, "role": "Stock Manager"}):
    process_label = display_name + " - Stock & Dispatch Overview"

    dispatch_pending_count = 0
    try:
        dispatch_pending_count = frappe.db.count(
            "Sales Order",
            filters={"stage_status": "Completed", "per_delivered": ["<", 100]}
        ) or 0
    except Exception: pass

    dispatched_count = 0
    try:
        dispatched_count = frappe.db.count("Delivery Note", filters={"docstatus": 1}) or 0
    except Exception: pass

    supplier_materials_count = 0
    try:
        supplier_materials_count = frappe.db.count("Purchase Receipt", filters={"status": "Completed"}) or 0
    except Exception: pass

    kpi_data = [
        {"title": "Dispatch Pending",   "count": dispatch_pending_count,   "route": "Sales Order",      "filter": {"stage_status": "Completed", "per_delivered": ["<", 100]}},
        {"title": "Dispatched",         "count": dispatched_count,         "route": "Delivery Note",    "filter": {"docstatus": 1}},
        {"title": "Supplier Materials", "count": supplier_materials_count, "route": "Purchase Receipt", "filter": {"status": "Completed"}}
    ]

    material_requested_list = []
    try:
        mr_rows = frappe.db.get_all(
            "Material Request",
            filters=[
                ["status", "in", ["Pending", "Partially Ordered"]],
                ["material_request_type", "in", ["Material Issue", "Material Transfer"]]
            ],
            fields=["name", "title", "material_request_type", "transaction_date", "schedule_date", "status", "per_ordered"],
            order_by="transaction_date desc",
            limit_page_length=20
        )
        for m in mr_rows:
            material_requested_list.append({
                "name":        m.get("name"),
                "title":       m.get("title") or m.get("name"),
                "purpose":     m.get("material_request_type") or "",
                "date":        str(m.get("transaction_date") or ""),
                "required_by": str(m.get("schedule_date") or ""),
                "status":      m.get("status") or "",
                "per_ordered": m.get("per_ordered") or 0
            })
    except Exception: pass

    plan_data = []
    try:
        todo_count = frappe.db.count("ToDo", filters={"allocated_to": user, "status": "Open"}) or 0
        plan_data = [{"title": "Actions for Stores", "count": todo_count, "route": "ToDo", "filter": {"allocated_to": user, "status": "Open"}}]
    except Exception: pass

    pending_tasks = []
    try:
        for m in material_requested_list[:10]:
            req_date_str = m.get("required_by") or ""
            tat_days = "-"
            if req_date_str and req_date_str < today:
                try:
                    tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(req_date_str)).days
                except Exception: tat_days = "-"
            pending_tasks.append({
                "doctype":       "Material Request",
                "type":          m.get("status") or "Pending",
                "client":        m.get("title"),
                "ref":           m.get("name"),
                "date":          req_date_str,
                "assigned_date": m.get("date") or "",
                "tat":           tat_days,
                "is_delayed":    tat_days != "-" and tat_days > 0
            })
    except Exception: pass

    dispatched_month = 0
    try:
        dispatched_month = frappe.db.count("Delivery Note", filters={"docstatus": 1, "posting_date": [">=", month_start]}) or 0
    except Exception: pass

    dispatch_pending_month = 0
    try:
        dispatch_pending_month = frappe.db.count("Sales Order", filters={"stage_status": "Completed", "per_delivered": ["<", 100], "transaction_date": [">=", month_start]}) or 0
    except Exception: pass

    performance = {
        "label1": "Dispatched",       "value1": dispatched_month,
        "route1": "Delivery Note",    "filter1": {"docstatus": 1, "posting_date": [">=", month_start]},
        "label2": "Dispatch Pending", "value2": dispatch_pending_month,
        "route2": "Sales Order",      "filter2": {"stage_status": "Completed", "per_delivered": ["<", 100], "transaction_date": [">=", month_start]}
    }

    actions = {
        "btn1_label":  "View Material Requests",
        "btn1_type":   "list_route",
        "btn1_target": "Material Request",
        "btn1_filter": {"status": ["in", ["Pending", "Partially Ordered"]], "material_request_type": ["in", ["Material Issue", "Material Transfer"]]},
        "btn2_label":   "Stock In and Out",
        "btn2_type":    "external_link",
        "btn2_target":  "https://sadbhavuat.getmyerp.com/app/query-report/Stock%20Ledger?company=Sadbhav+Renewable+Ltd&from_date=" + month_start + "&to_date=" + today + "&valuation_field_type=Currency",
        "btn2_visible": True
    }

# ── PROJECTS MANAGER ───────────────────────────────────────
elif frappe.db.exists("Has Role", {"parent": user, "role": "Projects Manager"}):
    process_label = display_name + " - Project Execution"

    user_project_list = []
    try:
        for p in frappe.get_all("Project", filters={"custom_project_manager": user, "docstatus": ["<", 2]}, fields=["name"]):
            user_project_list.append(p.get("name"))
    except Exception: pass

    project_assigned_count = 0
    try:
        project_assigned_count = len(frappe.db.get_all(
            "Sales Order",
            filters=[["project_manager", "=", user], ["project_status", "=", "Not Created"], ["docstatus", "=", 1]],
            fields=["name"],
            limit_page_length=500
        ))
    except Exception: pass

    # ── Dispatched KPI ──
    dispatch_count = 0
    dispatch_so_names = []
    try:
        result_dn = frappe.db.sql(
            """SELECT DISTINCT so.name FROM `tabSales Order` so
            INNER JOIN `tabDelivery Note Item` dni ON dni.against_sales_order = so.name
            INNER JOIN `tabDelivery Note` dn ON dn.name = dni.parent
            WHERE dn.docstatus = 1
            AND so.docstatus = 1
            AND so.project_status = 'Not Created'
            AND so.per_delivered > 0""",
            as_dict=True
        )
        dispatch_so_names = [r.get("name") for r in result_dn]
        dispatch_count = len(dispatch_so_names)
    except Exception: pass

    in_progress_count = 0
    try:
        for p in frappe.get_all("Project", filters={"custom_project_manager": user, "status": "Open", "docstatus": ["<", 2]}, fields=["percent_complete"]):
            if frappe.utils.flt(p.get("percent_complete") or 0) < 100:
                in_progress_count = in_progress_count + 1
    except Exception: pass

    completed_count = 0
    try:
        completed_count = frappe.db.count("Project", {"custom_project_manager": user, "status": "Completed", "docstatus": ["<", 2]}) or 0
    except Exception: pass

    delayed_count = 0
    try:
        delayed_count = frappe.db.count("Project", {"custom_project_manager": user, "stage_status": "Overdue", "docstatus": ["<", 2]}) or 0
    except Exception: pass

    kpi_data = [
        {"title": "Upcoming Projects",    "count": project_assigned_count, "route": "Sales Order",   "filter": {"project_manager": user, "project_status": "Not Created", "docstatus": 1}},
        {"title": "Dispatched",           "count": dispatch_count,         "route": "Sales Order",   "filter": {"docstatus": 1, "project_status": "Not Created", "per_delivered": [">", 0]}},
        {"title": "Projects In Progress", "count": in_progress_count,      "route": "Project",       "filter": {"custom_project_manager": user, "status": "Open"}},
        {"title": "Projects Completed",   "count": completed_count,        "route": "Project",       "filter": {"custom_project_manager": user, "status": "Completed"}},
        {"title": "Delayed Projects",     "count": delayed_count,          "route": "Project",       "filter": {"custom_project_manager": user, "stage_status": "Overdue"}}
    ]

    plan_data = [
        {"title": "All Ongoing Projects", "count": in_progress_count, "route": "Project", "filter": {"custom_project_manager": user, "status": "Open"}}
    ]

    pending_tasks = []
    try:
        for d in frappe.get_all(
            "Project",
            filters={"custom_project_manager": user, "status": "Open", "docstatus": ["<", 2]},
            fields=["name", "project_name", "expected_end_date", "expected_start_date", "percent_complete", "stage_status", "delay_log"],
            order_by="expected_end_date asc",
            limit=10
        ):
            if frappe.utils.flt(d.get("percent_complete") or 0) < 100:
                end_date_str = str(d.get("expected_end_date") or "")
                tat_days = "-"
                if end_date_str and end_date_str < today:
                    try:
                        tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(end_date_str)).days
                    except Exception: tat_days = "-"
                pending_tasks.append({
                    "doctype":       "Project",
                    "type":          "Overdue Project" if d.get("stage_status") == "Overdue" else "In Progress",
                    "client":        d.get("project_name") or d.get("name"),
                    "ref":           d.get("name"),
                    "date":          end_date_str,
                    "assigned_date": str(d.get("expected_start_date") or ""),
                    "tat":           tat_days,
                    "is_delayed":    tat_days != "-" and tat_days > 0
                })
    except Exception: pass

    material_dispatched_count = 0
    try:
        if user_project_list:
            material_dispatched_count = len(frappe.db.sql(
                "SELECT DISTINCT dn.name FROM `tabDelivery Note` dn WHERE dn.project IN %s AND dn.docstatus = 1 AND dn.posting_date >= %s",
                (tuple(user_project_list), month_start), as_dict=True
            ))
    except Exception: pass

    installation_completed_count = 0
    try:
        installation_completed_count = frappe.db.count("Project", {"custom_project_manager": user, "status": "Completed", "actual_end_date": [">=", month_start], "docstatus": ["<", 2]}) or 0
    except Exception: pass

    pending_installations_count = 0
    try:
        pending_installations_count = frappe.db.count("Project", {"custom_project_manager": user, "status": "Open", "docstatus": ["<", 2]}) or 0
    except Exception: pass

    performance = {
        "label1": "Material Dispatched",    "value1": material_dispatched_count,
        "label2": "Installation Completed", "value2": installation_completed_count,
        "label3": "Pending Installations",  "value3": pending_installations_count
    }

    actions = {
        "btn1_label":  "View My Projects",
        "btn1_type":   "list_route",
        "btn1_target": "Project",
        "btn1_filter": {"custom_project_manager": user},
        "btn2_label":   "View Overdue",
        "btn2_type":    "list_route",
        "btn2_target":  "Project",
        "btn2_filter":  {"custom_project_manager": user, "stage_status": "Overdue"},
        "btn2_visible": True
    }

# ── SYNCHRONIZATION USER ───────────────────────────────────
elif frappe.db.exists("Has Role", {"parent": user, "role": "Synchronization User"}):
    process_label = display_name + " - Liaisoning & Sync"

    current_projects_count = 0
    try:
        current_projects_count = frappe.db.count(
            "Sales Order",
            filters={"lias_sync_manager": user, "liaison_sync_status": "Not Created"}
        ) or 0
    except Exception: pass

    ongoing_count = 0
    try:
        ongoing_count = frappe.db.count(
            "Liaisoning And Synchronization",
            filters={"sync_manager": user, "status": ["in", ["Open", "Overdue"]]}
        ) or 0
    except Exception: pass

    docs_collected_count = 0
    try:
        docs_collected_count = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "status": "Docs Collected"}) or 0
    except Exception: pass

    registered_count = 0
    try:
        registered_count = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "status": "Docs Registered"}) or 0
    except Exception: pass

    docs_signed_count = 0
    try:
        docs_signed_count = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "status": "Docs Sign-Submit"}) or 0
    except Exception: pass

    meter_issued_count = 0
    try:
        meter_issued_count = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "status": "Meter Issue"}) or 0
    except Exception: pass

    sync_done_count = 0
    try:
        sync_done_count = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "status": "Completed"}) or 0
    except Exception: pass

    kpi_data = [
        {"title": "My Projects",    "count": current_projects_count, "route": "Sales Order",                    "filter": {"lias_sync_manager": user, "liaison_sync_status": "Not Created"}},
        {"title": "Ongoing",        "count": ongoing_count,          "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "status": ["in", ["Open", "Overdue"]]}},
        {"title": "Docs Collected", "count": docs_collected_count,   "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "status": "Docs Collected"}},
        {"title": "Registered",     "count": registered_count,       "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "status": "Docs Registered"}},
        {"title": "Docs Signed",    "count": docs_signed_count,      "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "status": "Docs Sign-Submit"}},
        {"title": "Meter Issued",   "count": meter_issued_count,     "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "status": "Meter Issue"}},
        {"title": "Sync Done",      "count": sync_done_count,        "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "status": "Completed"}}
    ]

    project_assigned_today = 0
    try:
        project_assigned_today = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "posting_date": today}) or 0
    except Exception: pass

    docs_collected_today = 0
    try:
        docs_collected_today = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "doc_collected_dt": today}) or 0
    except Exception: pass

    docs_registered_today = 0
    try:
        docs_registered_today = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "portal_registration_dt": today}) or 0
    except Exception: pass

    docs_signed_today = 0
    try:
        docs_signed_today = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "doc_submit_dt": today}) or 0
    except Exception: pass

    meter_issued_today = 0
    try:
        meter_issued_today = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "meter_issue_dt": today}) or 0
    except Exception: pass

    sync_done_today = 0
    try:
        sync_done_today = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "synchronization_done_dt": today}) or 0
    except Exception: pass

    plan_data = [
        {"title": "Project Assigned Today", "count": project_assigned_today,  "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "posting_date": today}},
        {"title": "Docs Collected Today",   "count": docs_collected_today,    "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "doc_collected_dt": today}},
        {"title": "Docs Registered Today",  "count": docs_registered_today,   "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "portal_registration_dt": today}},
        {"title": "Docs Signed Today",      "count": docs_signed_today,       "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "doc_submit_dt": today}},
        {"title": "Meter Issued Today",     "count": meter_issued_today,      "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "meter_issue_dt": today}},
        {"title": "Sync Done Today",        "count": sync_done_today,         "route": "Liaisoning And Synchronization", "filter": {"sync_manager": user, "synchronization_done_dt": today}}
    ]

    pending_tasks = []

    # ToDo tasks for this user
    try:
        todo_rows = frappe.db.get_all(
            "ToDo",
            filters=[["allocated_to", "=", user], ["status", "=", "Open"]],
            fields=["name", "description", "date", "reference_type", "reference_name", "creation"],
            order_by="date asc",
            limit_page_length=5
        )
        for t in todo_rows:
            raw_desc = str(t.get("description") or "Task")
            clean_desc = raw_desc
            while "<" in clean_desc and ">" in clean_desc:
                start = clean_desc.find("<")
                end = clean_desc.find(">")
                if start < end:
                    clean_desc = clean_desc[:start] + clean_desc[end+1:]
                else:
                    break
            clean_desc = clean_desc.strip() or "Task"
            due_date_str = str(t.get("date") or "")
            tat_days = "-"
            if due_date_str and due_date_str < today:
                try:
                    tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(due_date_str)).days
                except Exception: tat_days = "-"
            pending_tasks.append({
                "doctype":       t.get("reference_type") or "ToDo",
                "type":          clean_desc,
                "client":        t.get("reference_name") or "—",
                "ref":           t.get("reference_name") or t.get("name"),
                "date":          due_date_str,
                "assigned_date": str(t.get("creation") or "")[:10],
                "tat":           tat_days,
                "is_delayed":    tat_days != "-" and tat_days > 0
            })
    except Exception: pass

    # Overdue Liaisoning records
    try:
        overdue_rows = frappe.db.get_all(
            "Liaisoning And Synchronization",
            filters={"sync_manager": user, "status": "Overdue"},
            fields=["name", "customer_name", "sla_due_date", "posting_date"],
            order_by="sla_due_date asc",
            limit_page_length=10
        )
        for d in overdue_rows:
            due_str = str(d.get("sla_due_date") or "")
            tat_days = "-"
            if due_str and due_str < today:
                try:
                    tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(due_str)).days
                except Exception: tat_days = "-"
            pending_tasks.append({
                "doctype":       "Liaisoning And Synchronization",
                "type":          "Overdue",
                "client":        d.get("customer_name") or d.get("name"),
                "ref":           d.get("name"),
                "date":          due_str,
                "assigned_date": str(d.get("posting_date") or ""),
                "tat":           tat_days,
                "is_delayed":    tat_days != "-" and tat_days > 0
            })
    except Exception: pass

    sync_pending_month = 0
    try:
        sync_pending_month = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "status": ["!=", "Completed"], "posting_date": [">=", month_start]}) or 0
    except Exception: pass

    sync_completed_month = 0
    try:
        sync_completed_month = frappe.db.count("Liaisoning And Synchronization", filters={"sync_manager": user, "status": "Completed", "posting_date": [">=", month_start]}) or 0
    except Exception: pass

    performance = {
        "label1": "Sync Pending",   "value1": sync_pending_month,
        "route1": "Liaisoning And Synchronization",
        "filter1": {"sync_manager": user, "status": ["!=", "Completed"], "posting_date": [">=", month_start]},
        "label2": "Sync Completed", "value2": sync_completed_month,
        "route2": "Liaisoning And Synchronization",
        "filter2": {"sync_manager": user, "status": "Completed", "posting_date": [">=", month_start]}
    }

    actions = {
        "btn1_label":  "Liaisoning List",
        "btn1_type":   "list_route",
        "btn1_target": "Liaisoning And Synchronization",
        "btn1_filter": {"sync_manager": user},
        "btn2_label":   "Report",
        "btn2_type":    "external_link",
        "btn2_target":  "https://sadbhavuat.getmyerp.com/app/liaisoning-and-synchronization/view/report",
        "btn2_visible": True
    }

# ── TARA / GAYATRI / DAMINI ────────────────────────────────
elif user in ["tara.sadbhavrenewable@gmail.com", "ergayatrisadbhav01@gmail.com", "daminisadbhavrenewable7@gmail.com"]:
    process_label = display_name + " - Residential Pipeline"

    THREE_USERS = [
        "tara.sadbhavrenewable@gmail.com",
        "ergayatrisadbhav01@gmail.com",
        "daminisadbhavrenewable7@gmail.com"
    ]

    current_year  = safe_int(today[0:4])
    current_month = safe_int(today[5:7])
    if current_month >= 4:
        fiscal_year_start = str(current_year) + "-04-01"
    else:
        fiscal_year_start = str(current_year - 1) + "-04-01"

    assigned_survey_names = []
    try:
        survey_rows = frappe.db.get_all(
            "Site Survey",
            filters=[["status", "=", "Completed"], ["creation", ">=", fiscal_year_start]],
            fields=["name", "lead"],
            limit_page_length=2000
        )
        for s in survey_rows:
            rn = s.get("name") or ""
            if rn:
                assigned_survey_names.append(rn)
    except Exception: pass

    proposal_assigned_count = len(assigned_survey_names)

    surveys_with_proposal = []
    try:
        if assigned_survey_names:
            ph = ",".join(["%s"] * len(assigned_survey_names))
            sq_rows = frappe.db.sql(
                "SELECT DISTINCT site_survey FROM `tabQuotation` WHERE site_survey IN (" + ph + ") AND docstatus != 2",
                tuple(assigned_survey_names), as_dict=True
            )
            for s in sq_rows:
                sv = s.get("site_survey") or ""
                if sv:
                    surveys_with_proposal.append(sv)
    except Exception: pass

    proposal_pending_count = 0
    try:
        if assigned_survey_names:
            ph = ",".join(["%s"] * len(assigned_survey_names))
            pend_res = frappe.db.sql(
                "SELECT COUNT(*) FROM `tabSite Survey` ss WHERE ss.name IN (" + ph + ") AND ss.name NOT IN (SELECT DISTINCT site_survey FROM `tabQuotation` WHERE docstatus != 2 AND site_survey IS NOT NULL AND site_survey != '')",
                tuple(assigned_survey_names)
            )
            proposal_pending_count = safe_int(pend_res[0][0]) if pend_res else 0
    except Exception: pass

    proposals_shared_count = 0
    try:
        proposals_shared_count = frappe.db.count(
            "Quotation",
            filters=[["docstatus", "!=", 2], ["creation", ">=", fiscal_year_start], ["site_survey", "is", "set"]]
        ) or 0
    except Exception: pass

    proposal_converted_count = 0
    try:
        if assigned_survey_names:
            ph = ",".join(["%s"] * len(assigned_survey_names))
            so_res = frappe.db.sql(
                "SELECT COUNT(*) FROM `tabSales Order` WHERE site_survey IN (" + ph + ") AND docstatus = 1 AND transaction_date >= %s",
                tuple(assigned_survey_names) + (fiscal_year_start,)
            )
            proposal_converted_count = safe_int(so_res[0][0]) if so_res else 0
    except Exception: pass

    completed_proposals_count = len(surveys_with_proposal)

    kpi_data = [
        {"title": "Proposal Assigned",   "count": proposal_assigned_count,   "route": "Site Survey", "filter": {"status": "Completed", "creation": [">=", fiscal_year_start]}},
        {"title": "Proposal Pending",    "count": proposal_pending_count,    "route": "Site Survey", "filter": {"name": ["in", [s for s in assigned_survey_names if s not in surveys_with_proposal] or ["NONE"]]}},
        {"title": "Completed Proposals", "count": completed_proposals_count, "route": "Site Survey", "filter": {"name": ["in", surveys_with_proposal or ["NONE"]]}},
        {"title": "Proposals Shared",    "count": proposals_shared_count,    "route": "Quotation",   "filter": {"docstatus": ["!=", 2], "creation": [">=", fiscal_year_start], "site_survey": ["is", "set"]}},
        {"title": "Proposal Converted",  "count": proposal_converted_count,  "route": "Sales Order", "filter": {"site_survey": ["in", assigned_survey_names or ["NONE"]], "docstatus": 1, "transaction_date": [">=", fiscal_year_start]}}
    ]

    assigned_today_surveys = []
    try:
        today_rows = frappe.db.sql(
            "SELECT name FROM `tabSite Survey` WHERE status = 'Completed' AND completed_date = %s",
            (today,), as_dict=True
        )
        for s in today_rows:
            rn = s.get("name") or ""
            if rn:
                assigned_today_surveys.append(rn)
    except Exception: pass

    proposal_assigned_today = len(assigned_today_surveys)

    surveys_with_proposal_today = []
    proposal_completed_today = 0
    try:
        if assigned_today_surveys:
            ph = ",".join(["%s"] * len(assigned_today_surveys))
            qt_today = frappe.db.sql(
                "SELECT DISTINCT site_survey FROM `tabQuotation` WHERE docstatus != 2 AND site_survey IN (" + ph + ")",
                tuple(assigned_today_surveys), as_dict=True
            )
            for q in qt_today:
                sv = q.get("site_survey") or ""
                if sv:
                    surveys_with_proposal_today.append(sv)
    except Exception: pass

    proposal_completed_today = 0
    try:
        proposal_completed_today = frappe.db.count(
            "Quotation",
            filters=[["docstatus", "!=", 2], ["creation", ">=", today + " 00:00:00"], ["creation", "<=", today + " 23:59:59"]]
        ) or 0
    except Exception: pass

    proposal_pending_today = 0
    try:
        if assigned_today_surveys:
            ph = ",".join(["%s"] * len(assigned_today_surveys))
            pend_today = frappe.db.sql(
                "SELECT COUNT(*) FROM `tabSite Survey` WHERE name IN (" + ph + ") AND name NOT IN (SELECT DISTINCT site_survey FROM `tabQuotation` WHERE docstatus != 2 AND site_survey IS NOT NULL AND site_survey != '')",
                tuple(assigned_today_surveys)
            )
            proposal_pending_today = safe_int(pend_today[0][0]) if pend_today else 0
    except Exception: pass

    plan_data = [
        {"title": "Proposals Assigned Today", "count": proposal_assigned_today,  "route": "Site Survey", "filter": {"name": ["in", assigned_today_surveys or ["NONE"]], "status": "Completed", "completed_date": today}},
        {"title": "Proposals Completed Today","count": proposal_completed_today, "route": "Quotation",   "filter": {"docstatus": ["!=", 2], "creation": [">=", today + " 00:00:00"]}},
        {"title": "Proposals Pending Today",  "count": proposal_pending_today,   "route": "Site Survey", "filter": {"name": ["in", [s for s in assigned_today_surveys if s not in surveys_with_proposal_today] or ["NONE"]]}}
    ]

    pending_tasks = []
    try:
        pending_survey_names = [s for s in assigned_survey_names if s not in surveys_with_proposal]
        if pending_survey_names:
            ph = ",".join(["%s"] * len(pending_survey_names))
            pending_rows = frappe.db.sql(
                "SELECT name, lead_name, survey_date FROM `tabSite Survey` WHERE name IN (" + ph + ") ORDER BY survey_date asc LIMIT 10",
                tuple(pending_survey_names), as_dict=True
            )
            for d in pending_rows:
                survey_date_str = str(d.get("survey_date") or "")
                tat_days = "-"
                if survey_date_str and survey_date_str < today:
                    try:
                        tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(survey_date_str)).days
                    except Exception: tat_days = "-"
                pending_tasks.append({
                    "doctype":       "Site Survey",
                    "type":          "Proposal Pending",
                    "client":        d.get("lead_name") or d.get("name"),
                    "ref":           d.get("name"),
                    "date":          survey_date_str,
                    "assigned_date": survey_date_str,
                    "tat":           tat_days,
                    "is_delayed":    tat_days != "-" and tat_days > 0
                })
    except Exception: pass

    survey_done_month = 0
    completed_surveys_this_month = []
    try:
        md_rows = frappe.db.sql(
            "SELECT name FROM `tabSite Survey` WHERE status = 'Completed' AND creation >= %s",
            (month_start,), as_dict=True
        )
        for s in md_rows:
            rn = s.get("name") or ""
            if rn:
                completed_surveys_this_month.append(rn)
        survey_done_month = len(completed_surveys_this_month)
    except Exception: pass

    proposals_created_month = 0
    try:
        if completed_surveys_this_month:
            ph = ",".join(["%s"] * len(completed_surveys_this_month))
            pc_res = frappe.db.sql(
                "SELECT COUNT(DISTINCT site_survey) FROM `tabQuotation` WHERE docstatus != 2 AND site_survey IN (" + ph + ")",
                tuple(completed_surveys_this_month)
            )
            proposals_created_month = safe_int(pc_res[0][0]) if pc_res else 0
    except Exception: pass

    proposals_shared_month = 0
    try:
        if completed_surveys_this_month:
            ph = ",".join(["%s"] * len(completed_surveys_this_month))
            ps_res = frappe.db.sql(
                "SELECT COUNT(*) FROM `tabQuotation` WHERE docstatus != 2 AND site_survey IN (" + ph + ")",
                tuple(completed_surveys_this_month)
            )
            proposals_shared_month = safe_int(ps_res[0][0]) if ps_res else 0
    except Exception: pass

    converted_clients_month = 0
    try:
        if completed_surveys_this_month:
            ph = ",".join(["%s"] * len(completed_surveys_this_month))
            cc_res = frappe.db.sql(
                "SELECT COUNT(*) FROM `tabSales Order` WHERE site_survey IN (" + ph + ") AND docstatus = 1 AND transaction_date >= %s",
                tuple(completed_surveys_this_month) + (month_start,)
            )
            converted_clients_month = safe_int(cc_res[0][0]) if cc_res else 0
    except Exception: pass

    performance = {
        "label1": "Survey Done",       "value1": survey_done_month,
        "route1": "Site Survey",       "filter1": {"name": ["in", completed_surveys_this_month or ["NONE"]], "status": "Completed", "creation": [">=", month_start]},
        "label2": "Proposals Created", "value2": proposals_created_month,
        "route2": "Quotation",         "filter2": {"site_survey": ["in", completed_surveys_this_month or ["NONE"]], "docstatus": ["!=", 2]},
        "label3": "Proposals Shared",  "value3": proposals_shared_month,
        "route3": "Quotation",         "filter3": {"site_survey": ["in", completed_surveys_this_month or ["NONE"]], "docstatus": ["!=", 2]},
        "label4": "Converted Clients", "value4": converted_clients_month,
        "route4": "Sales Order",       "filter4": {"site_survey": ["in", completed_surveys_this_month or ["NONE"]], "docstatus": 1, "transaction_date": [">=", month_start]}
    }

    actions = {
        "btn1_label":  "View Total Process Report",
        "btn1_type":   "external_link",
        "btn1_target": "https://sadbhavuat.getmyerp.com/app/query-report/Total%20Process?from_date=" + fiscal_year_start + "&to_date=" + today,
        "btn2_visible": False
    }

# ── DEFAULT ─────────────────────────────────────────────────
else:
    process_label = display_name + " - Site Survey & Lead Gen"
    kpi_data = [
        {"title":"Leads Generated","count":frappe.db.count("Lead",{"lead_owner":user}),                              "route":"Lead",       "filter":{"lead_owner":user}},
        {"title":"Surveys Pending", "count":frappe.db.count("Site Survey",{"surveyed_by":user,"status":"Open"}),     "route":"Site Survey","filter":{"surveyed_by":user,"status":"Open"}},
        {"title":"Surveys Done",    "count":frappe.db.count("Site Survey",{"surveyed_by":user,"status":"Completed"}), "route":"Site Survey","filter":{"surveyed_by":user,"status":"Completed"}}
    ]
    plan_data = [
        {"title":"Surveys Today",   "count":frappe.db.count("Site Survey",{"survey_date":today,"surveyed_by":user}),    "route":"Site Survey","filter":{"survey_date":today,"surveyed_by":user}},
        {"title":"Open Leads",      "count":frappe.db.count("Lead",{"lead_owner":user,"status":"Open"}),                "route":"Lead",       "filter":{"lead_owner":user,"status":"Open"}},
        {"title":"Follow Ups",      "count":frappe.db.count("Site Survey",{"completed_date":today,"surveyed_by":user}), "route":"Site Survey","filter":{"completed_date":today,"surveyed_by":user}}
    ]

    # Site Survey pending tasks
    for d in frappe.db.get_all("Site Survey", filters={"surveyed_by": user, "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days", "survey_date"]):
        exp_date_str = str(d.get("exp_nxstp_dt") or "")
        tat_days = "-"
        if exp_date_str and exp_date_str < today:
            try:
                tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(exp_date_str)).days
            except Exception: tat_days = "-"
        pending_tasks.append({
            "doctype":       "Site Survey",
            "type":          "Conduct Survey",
            "client":        d.get("lead_name"),
            "ref":           d.get("name"),
            "date":          exp_date_str,
            "assigned_date": str(d.get("survey_date") or ""),
            "tat":           tat_days,
            "is_delayed":    tat_days != "-" and tat_days > 0
        })

    # Lead ToDo pending tasks
    try:
        todo_leads = frappe.db.get_all(
            "ToDo",
            filters=[["allocated_to", "=", user], ["status", "=", "Open"], ["reference_type", "=", "Lead"]],
            fields=["reference_name", "description", "date", "creation"],
            order_by="date asc",
            limit_page_length=10
        )
        for t in todo_leads:
            lead_name = frappe.db.get_value("Lead", t.get("reference_name"), "lead_name") or t.get("reference_name")
            raw_desc = str(t.get("description") or "Follow Up")
            clean_desc = raw_desc
            while "<" in clean_desc and ">" in clean_desc:
                start = clean_desc.find("<")
                end = clean_desc.find(">")
                if start < end:
                    clean_desc = clean_desc[:start] + clean_desc[end+1:]
                else:
                    break
            clean_desc = clean_desc.strip() or "Follow Up"
            due_date_str = str(t.get("date") or "")
            tat_days = "-"
            if due_date_str and due_date_str < today:
                try:
                    tat_days = (frappe.utils.getdate(today) - frappe.utils.getdate(due_date_str)).days
                except Exception: tat_days = "-"
            pending_tasks.append({
                "doctype":       "Lead",
                "type":          clean_desc,
                "client":        lead_name,
                "ref":           t.get("reference_name"),
                "date":          due_date_str,
                "assigned_date": str(t.get("creation") or "")[:10],
                "tat":           tat_days,
                "is_delayed":    tat_days != "-" and tat_days > 0
            })
    except Exception: pass

    surveys_this_month = frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Completed", "completed_date": [">=", month_start]}) or 0
    leads_this_month   = frappe.db.count("Lead", {"lead_owner": user, "creation": [">=", month_start]}) or 0
    performance = {
        "label1": "Surveys Done",    "value1": surveys_this_month,
        "label2": "Leads Generated", "value2": leads_this_month,
        "label3": "Conversion %",    "value3": safe_pct(surveys_this_month, leads_this_month) if leads_this_month > 0 else 0
    }
    actions = {"btn1_label":"Generate Lead","btn1_type":"new_doc","btn1_target":"Lead","btn2_label":"Conduct Survey","btn2_type":"new_doc","btn2_target":"Site Survey","btn2_visible":True}

# ── Sort & dedup pending tasks ──────────────────────────────
n = len(pending_tasks)
for i in range(n):
    for j in range(0, n - i - 1):
        s1 = pending_tasks[j].get("date") if pending_tasks[j].get("date") else "9999-12-31"
        s2 = pending_tasks[j+1].get("date") if pending_tasks[j+1].get("date") else "9999-12-31"
        if s1 > s2:
            temp = pending_tasks[j]
            pending_tasks[j] = pending_tasks[j+1]
            pending_tasks[j+1] = temp
seen = []
dedup = []
for t in pending_tasks:
    key = str(t.get("ref") or "") + "|" + str(t.get("type") or "")
    if key not in seen:
        seen.append(key)
        dedup.append(t)
pending_tasks = dedup

# ── Recent Activity ─────────────────────────────────────────
activities = []
try:
    act_raw = frappe.db.get_all("Version", filters={"owner": user}, fields=["ref_doctype","docname","creation"], limit=6, order_by="creation desc")
    for a in act_raw:
        activities.append({"ref_doctype": a.get("ref_doctype") or "", "docname": a.get("docname") or "", "creation": str(a.get("creation") or "")})
except Exception: pass

# ────────────────────────────────────────────────────────────
#  ROUTING
# ────────────────────────────────────────────────────────────
try:
    action   = (frappe.form_dict.get("action") or "").strip()
    f_from   = (frappe.form_dict.get("from_date") or "").strip()
    f_to     = (frappe.form_dict.get("to_date") or "").strip()
    f_stages = (frappe.form_dict.get("stages") or "").strip()
    stage    = (frappe.form_dict.get("stage") or "").strip()
    name     = (frappe.form_dict.get("name") or "").strip()
    project  = (frappe.form_dict.get("project") or "").strip()

    if action == "get_all_names":
        frappe.response["message"] = get_all_names()
    elif action == "get_process_view":
        frappe.response["message"] = get_process_view(stage, name, project)
    elif action == "get_site_images":
        frappe.response["message"] = get_site_images(stage, name, project)
    elif action == "get_followup_logs":
        parsed_stages = [s.strip() for s in f_stages.split(",") if s.strip()] if f_stages else None
        frappe.response["message"] = get_followup_logs(from_dt=f_from or today, to_dt=f_to or today, stage_filter=parsed_stages)
    elif action == "get_recent_leads":
        two_days_ago = str(frappe.utils.add_days(now_date, -2))
        lead_rows = frappe.db.get_all(
            "Lead",
            filters=[["creation", ">=", two_days_ago + " 00:00:00"]],
            fields=["name", "lead_name", "mobile_no", "status", "source", "creation"],
            order_by="creation desc",
            limit_page_length=100
        )
        frappe.response["message"] = lead_rows
    else:
        frappe.response["message"] = {
            "role":              process_label,
            "employee":          {"employee_id": emp_id, "employee_name": emp_name, "designation": employee.get("designation") or "", "department": employee.get("department") or ""},
            "attendance":        attendance,
            "leaves":            leaves,
            "payslips":          payslips,
            "holidays":          holidays,
            "notifications":     notifications,
            "kpi":               kpi_data,
            "plan":              plan_data,
            "tasks":             pending_tasks[:10],
            "performance":       performance,
            "activities":        activities,
            "actions":           actions,
            "quick_link_report": quick_link_report,
            "purchase_date_range": purchase_date_range,
            "performance_label": current_month_name + "'s Performance"
        }
except Exception:
    frappe.log_error("Dashboard routing error", "combined_dashboard")
    frappe.response["message"] = {"error": "Server execution error"}
# ============================================================
# COMBINED ESS + OPERATIONS DASHBOARD — SERVER SCRIPT
# API METHOD: user
# RestrictedPython compliant — no imports, no f-strings.
# ============================================================

user     = frappe.session.user
now_date = frappe.utils.today()
today    = str(now_date)

# Fetch data up to 6 months back so frontend filters actually show historical data
past_history_start = str(frappe.utils.add_months(now_date, -6))
month_start = str(frappe.utils.get_first_day(now_date))

# Get today's month and day digits for milestone checking (MM-DD string slice format)
today_mm_dd = today[5:10] 

# ============================================================
# HELPERS
# ============================================================

def safe_int(v):
    if not v:
        return 0
    try:
        return int(v)
    except:
        return 0

def get_avg_tat(doctype, filters):
    records = frappe.db.get_all(doctype, filters=filters, fields=["tat_days"])
    valid = []
    for r in records:
        if r.get("tat_days") is not None:
            valid.append(r.get("tat_days"))
    if not valid:
        return 0
    return round(sum(valid) / len(valid), 1)

def safe_pct(n, d):
    if not d:
        return 0
    return round((n * 100.0) / d, 1)

# ============================================================
# EMPLOYEE LOOKUP
# ============================================================

employee = frappe.db.get_value(
    "Employee",
    {"company_email": user, "status": "Active"},
    ["name", "employee_name", "designation", "department", "holiday_list", "date_of_joining"],
    as_dict=True
)

if not employee:
    ui = frappe.db.get_value("User", user, ["full_name", "first_name", "user_image"], as_dict=True)
    user_prefix = user.split("@")[0].capitalize()
    employee = {
        "name": "",
        "employee_name": ui.get("full_name") if ui else user_prefix,
        "designation": "Employee",
        "department": "",
        "holiday_list": "",
        "date_of_joining": ""
    }

emp_id       = employee.get("name")
emp_name     = employee.get("employee_name") or user.split("@")[0].capitalize()
display_name = emp_name.split(" ")[0].capitalize()

# ============================================================
# ── ESS DATA (Attendance / Leave / Payslips / Holidays) ──
# ============================================================

# ── ATTENDANCE ──────────────────────────────────────────────
attendance = {"today_status": "Not Marked", "month_present": 0, "absent": 0, "half_day": 0, "wfh": 0, "records": []}

if emp_id:
    # Today's Status
    today_att = frappe.db.get_value("Attendance", {"employee": emp_id, "attendance_date": today, "docstatus": 1}, "status")
    attendance["today_status"] = today_att or "Not Marked"

    # Fetch 6 months of historical logs to make month filtering work perfectly on frontend dropdowns
    att_logs = frappe.db.get_all(
        "Attendance",
        filters={"employee": emp_id, "attendance_date": [">=", past_history_start], "docstatus": 1},
        fields=["attendance_date", "status"],
        order_by="attendance_date desc"
    )
    for a in att_logs:
        status = a.get("status") or ""
        log_date_str = str(a.get("attendance_date") or "")
        
        # Calculate current month overview metric counters strictly for this month
        if log_date_str >= month_start:
            if status == "Present":
                attendance["month_present"] = attendance.get("month_present", 0) + 1
            elif status == "Absent":
                attendance["absent"] = attendance.get("absent", 0) + 1
            elif status == "Half Day":
                attendance["half_day"] = attendance.get("half_day", 0) + 1
            elif status in ["Work From Home", "WFH", "Work from Home"]:
                attendance["wfh"] = attendance.get("wfh", 0) + 1

        # Store logs to map filter lookups
        attendance["records"].append({
            "date": log_date_str,
            "status": status
        })

# ── LEAVE BALANCES ──────────────────────────────────────────
leaves = []
if emp_id:
    allocations = frappe.db.get_all(
        "Leave Allocation",
        filters={"employee": emp_id, "docstatus": 1},
        fields=["leave_type", "total_leaves_allocated"]
    )
    for a in allocations:
        lt    = a.get("leave_type")
        total = safe_int(a.get("total_leaves_allocated"))
        used  = frappe.db.count("Leave Application", {"employee": emp_id, "leave_type": lt, "status": "Approved", "docstatus": 1})
        avail = total - used
        if avail < 0:
            avail = 0
        leaves.append({
            "leave_type": lt,
            "total_leaves": total,
            "used_leaves": used,
            "unused_leaves": avail
        })

# ── PAYSLIPS ────────────────────────────────────────────────
payslips = []
if emp_id:
    month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    slips = frappe.db.get_all(
        "Salary Slip",
        filters={"employee": emp_id, "docstatus": 1},
        fields=["name", "start_date", "net_pay"],
        order_by="start_date desc",
        limit=12
    )
    for s in slips:
        sd = str(s.get("start_date") or "")
        if len(sd) >= 10:
            y_str = sd[0:4]
            m_idx = safe_int(sd[5:7])
        else:
            y_str = "-"
            m_idx = 0
            
        payslips.append({
            "name": s.get("name"),
            "amount": round(s.get("net_pay") or 0),
            "month": month_names[m_idx] if 0 < m_idx < 13 else "-",
            "year": y_str
        })

# ── HOLIDAYS ────────────────────────────────────────────────
holidays = []
hl = employee.get("holiday_list")
if hl:
    h_list = frappe.db.get_all(
        "Holiday",
        filters={"parent": hl, "holiday_date": [">=", today]},
        fields=["holiday_date", "description"],
        order_by="holiday_date asc",
        limit=25
    )
    for h in h_list:
        holidays.append({
            "holiday_date": str(h.get("holiday_date") or ""),
            "description": h.get("description") or ""
        })

# ── NOTIFICATIONS (SYSTEM + BIRTHDAYS + ANNIVERSARIES) ──────
notifications = []

# Milestone Checks: Fetch active employees to catch birthdays and company anniversaries
active_colleagues = frappe.db.get_all(
    "Employee", 
    filters={"status": "Active"}, 
    fields=["employee_name", "company_email", "date_of_birth", "date_of_joining"]
)

for c in active_colleagues:
    c_name = c.get("employee_name") or "Colleague"
    c_first_name = c_name.split(" ")[0].capitalize()
    is_self = (c.get("company_email") == user)
    
    # 1. Birthday Lookups
    dob = str(c.get("date_of_birth") or "")
    if len(dob) >= 10 and dob[5:10] == today_mm_dd:
        label = "Happy Birthday to You! Have a wonderful day!" if is_self else "It's " + c_first_name + "'s Birthday today! Wish them well!"
        notifications.append({"type": "birthday", "subject": label})
        
    # 2. Work Anniversary Lookups
    doj = str(c.get("date_of_joining") or "")
    if len(doj) >= 10 and doj[5:10] == today_mm_dd:
        try:
            years_spent = safe_int(today[0:4]) - safe_int(doj[0:4])
        except:
            years_spent = 0
            
        if years_spent > 0:
            label = "Happy Work Anniversary! Thank you for " + str(years_spent) + " years with us!" if is_self else c_first_name + " is celebrating " + str(years_spent) + " years at the company today!"
            notifications.append({"type": "anniversary", "subject": label})

# 3. Process Pending Action Warnings (Marked as system type)
open_leads = frappe.db.count("Lead", {"lead_owner": user, "status": "Open"})
if open_leads:
    notifications.append({"type": "system", "subject": str(open_leads) + " proposals / leads need follow-up", "date": today})

pending_surveys = frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Open"})
if pending_surveys:
    notifications.append({"type": "system", "subject": str(pending_surveys) + " site surveys pending execution", "date": today})

pending_quotes = frappe.db.count("Quotation", {"status": "Open"})
if pending_quotes:
    notifications.append({"type": "system", "subject": str(pending_quotes) + " pipeline proposals open", "date": today})


# ============================================================
# ── OPERATIONS / ROLE-BASED KPI DATA ──
# ============================================================

kpi_data      = []
plan_data     = []
pending_tasks = []
performance   = {}
actions       = {}
process_label = ""

SYNC_DOCTYPE = "Liaisoning And Synchronization"
sync_exists  = frappe.db.exists("DocType", SYNC_DOCTYPE)


# ── 1. MANISHA — CRM & Sales ────────────────────────────────
if user == "manisha.sadbhavrenewable@gmail.com":
    process_label = display_name + " - CRM & Sales"

    kpi_data = [
        {"title": "Pending Follow-ups", "count": frappe.db.count("Quotation", {"status": "Open", "proposal_sent": 1}), "tat": get_avg_tat("Quotation", {"status": "Open"}), "route": "Quotation", "filter": {"status": "Open", "proposal_sent": 1}},
        {"title": "Proposals in Pipeline", "count": frappe.db.count("Quotation", {"status": "Open"}), "tat": get_avg_tat("Quotation", {"status": "Open"}), "route": "Quotation", "filter": {"status": "Open"}},
        {"title": "Sales Orders Created", "count": frappe.db.count("Sales Order", {"owner": user}), "tat": 0, "route": "Sales Order", "filter": {"owner": user}},
        {"title": "Dispatch Notify Pending", "count": frappe.db.count("Delivery Note", {"status": "Submitted"}), "tat": 0, "route": "Delivery Note", "filter": {"status": "Submitted"}}
    ]

    plan_data = [
        {"title": "Follow-ups Due Today", "count": frappe.db.count("Quotation", {"exp_nxstp_dt": today, "status": "Open"}), "route": "Quotation", "filter": {"exp_nxstp_dt": today, "status": "Open"}},
        {"title": "Dispatch Alerts to Send", "count": frappe.db.count("Delivery Note", {"status": "Submitted"}), "route": "Delivery Note", "filter": {"status": "Submitted"}}
    ]

    for d in frappe.db.get_all("Quotation", filters={"status": "Open"}, fields=["name", "customer_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({
            "doctype": "Quotation", "type": "Proposal Follow-up", "client": d.get("customer_name"), "ref": d.get("name"), "date": str(d.get("exp_nxstp_dt") or ""), "tat": d.get("tat_days") or 0
        })

    performance = {
        "label1": "Follow-ups Done", "value1": frappe.db.count("Quotation", {"status": ["!=", "Open"], "owner": user, "transaction_date": [">=", month_start]}),
        "label2": "Sales Orders", "value2": frappe.db.count("Sales Order", {"owner": user, "transaction_date": [">=", month_start]}),
        "label3": "Lost Proposals", "value3": frappe.db.count("Quotation", {"status": "Lost", "transaction_date": [">=", month_start]})
    }
    actions = {"btn1_label": "New Sales Order", "btn1_type": "new_doc", "btn1_target": "Sales Order", "btn2_label": "View Pipeline", "btn2_type": "list_route", "btn2_target": "Quotation", "btn2_filter": {"status": "Open"}, "btn2_visible": True}


# ── 2. MANAGEMENT OVERVIEW ──────────────────────────────────
elif user in ["mp@sadbhavrenewables.com", "ksk@sadbhavrenewables.com", "sandeep@sadbhavrenewables.com"]:
    process_label = display_name + " - Management Overview"

    kpi_data = [
        {"title": "Open Leads", "count": frappe.db.count("Lead", {"status": "Open"}), "tat": get_avg_tat("Lead", {"status": "Open"}), "route": "Lead", "filter": {"status": "Open"}},
        {"title": "Site Surveys Pending", "count": frappe.db.count("Site Survey", {"status": "Open"}), "tat": get_avg_tat("Site Survey", {"status": "Open"}), "route": "Site Survey", "filter": {"status": "Open"}},
        {"title": "Proposals Pending (Draft)", "count": frappe.db.count("Quotation", {"status": "Draft"}), "tat": get_avg_tat("Quotation", {"status": "Draft"}), "route": "Quotation", "filter": {"status": "Draft"}},
        {"title": "Proposals in Follow-up", "count": frappe.db.count("Quotation", {"status": "Open"}), "tat": get_avg_tat("Quotation", {"status": "Open"}), "route": "Quotation", "filter": {"status": "Open"}},
        {"title": "Sales Orders Active", "count": frappe.db.count("Sales Order", {"status": "To Deliver and Bill"}), "tat": 0, "route": "Sales Order", "filter": {"status": "To Deliver and Bill"}},
        {"title": "Dispatch Pending", "count": frappe.db.count("Delivery Note", {"status": "Draft"}), "tat": 0, "route": "Delivery Note", "filter": {"status": "Draft"}},
        {"title": "Liaisoning Pending", "count": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": ["in", ["New", "In Process"]]}) if sync_exists else 0, "tat": 0, "route": SYNC_DOCTYPE if sync_exists else "", "filter": {"liaisoning_status": "New"}}
    ]

    plan_data = [
        {"title": "Proposal Follow-ups Due", "count": frappe.db.count("Quotation", {"exp_nxstp_dt": today, "status": "Open"}), "route": "Quotation", "filter": {"exp_nxstp_dt": today, "status": "Open"}},
        {"title": "Payments to Verify", "count": frappe.db.count("Sales Order", {"status": "Draft"}), "route": "Sales Order", "filter": {"status": "Draft"}},
        {"title": "Dispatches Today", "count": frappe.db.count("Delivery Note", {"posting_date": today}), "route": "Delivery Note", "filter": {"posting_date": today}}
    ]

    for d in frappe.db.get_all("Lead", filters={"status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"], limit=3):
        pending_tasks.append({"doctype": "Lead", "type": "Lead Follow-up", "client": d.get("lead_name"), "ref": d.get("name"), "date": str(d.get("exp_nxstp_dt") or ""), "tat": d.get("tat_days") or 0})
    for d in frappe.db.get_all("Sales Order", filters={"status": "Draft"}, fields=["name", "customer_name", "transaction_date", "tat_days"], limit=3):
        pending_tasks.append({"doctype": "Sales Order", "type": "Payment Verification", "client": d.get("customer_name"), "ref": d.get("name"), "date": str(d.get("transaction_date") or ""), "tat": d.get("tat_days") or 0})

    performance = {
        "label1": "Leads This Month", "value1": frappe.db.count("Lead", {"creation": [">=", month_start]}),
        "label2": "Sales Orders This Month", "value2": frappe.db.count("Sales Order", {"transaction_date": [">=", month_start]}),
        "label3": "Dispatched This Month", "value3": frappe.db.count("Delivery Note", {"status": "Submitted", "posting_date": [">=", month_start]})
    }


# ── 3. TARA — Residential Pipeline ─────────────────────────
elif user == "tara.sadbhavrenewable@gmail.com":
    process_label = display_name + " - Residential Pipeline"

    kpi_data = [
        {"title": "Leads Created (Open)", "count": frappe.db.count("Lead", {"lead_owner": user, "status": "Open"}), "tat": 0, "route": "Lead", "filter": {"lead_owner": user, "status": "Open"}},
        {"title": "Surveys Pending", "count": frappe.db.count("Site Survey", {"plant_category": "Residential", "status": "Open"}), "tat": get_avg_tat("Site Survey", {"plant_category": "Residential", "status": "Open"}), "route": "Site Survey", "filter": {"plant_category": "Residential", "status": "Open"}},
        {"title": "Proposals Pending", "count": frappe.db.count("Quotation", {"plant_category": "Residential", "status": "Draft"}), "tat": get_avg_tat("Quotation", {"plant_category": "Residential", "status": "Draft"}), "route": "Quotation", "filter": {"plant_category": "Residential", "status": "Draft"}}
    ]

    plan_data = [
        {"title": "Proposals to Complete", "count": frappe.db.count("Quotation", {"plant_category": "Residential", "status": "Draft"}), "route": "Quotation", "filter": {"plant_category": "Residential", "status": "Draft"}},
        {"title": "Drawings Needed", "count": frappe.db.count("Site Survey", {"plant_category": "Residential", "status": "Open"}), "route": "Site Survey", "filter": {"plant_category": "Residential", "status": "Open"}}
    ]

    for d in frappe.db.get_all("Site Survey", filters={"plant_category": "Residential", "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Site Survey", "type": "Attach Drawing", "client": d.get("lead_name"), "ref": d.get("name"), "date": str(d.get("exp_nxstp_dt") or ""), "tat": d.get("tat_days") or 0})
    for d in frappe.db.get_all("Quotation", filters={"plant_category": "Residential", "status": "Draft"}, fields=["name", "customer_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Quotation", "type": "Create Proposal", "client": d.get("customer_name"), "ref": d.get("name"), "date": str(d.get("exp_nxstp_dt") or ""), "tat": d.get("tat_days") or 0})

    sent = frappe.db.count("Quotation", {"plant_category": "Residential", "proposal_sent": 1, "transaction_date": [">=", month_start]})
    performance = {
        "label1": "Proposals Sent", "value1": sent,
        "label2": "Drawings Done", "value2": frappe.db.count("Site Survey", {"plant_category": "Residential", "status": "Completed", "completed_date": [">=", month_start]}),
        "label3": "Conversion %", "value3": safe_pct(sent, frappe.db.count("Lead", {"status": "Site Survey"}))
    }
    actions = {"btn1_label": "New Lead", "btn1_type": "new_doc", "btn1_target": "Lead", "btn2_label": "New Proposal", "btn2_type": "new_doc", "btn2_target": "Quotation", "btn2_visible": True}

# ── 4. FIELD TEAM / DEFAULT ──────────────────────────────────
else:
    process_label = display_name + " - Site Survey & Lead Gen"

    kpi_data = [
        {"title": "Leads Generated", "count": frappe.db.count("Lead", {"lead_owner": user}), "tat": get_avg_tat("Lead", {"lead_owner": user}), "route": "Lead", "filter": {"lead_owner": user}},
        {"title": "Surveys Pending", "count": frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Open"}), "tat": get_avg_tat("Site Survey", {"surveyed_by": user, "status": "Open"}), "route": "Site Survey", "filter": {"surveyed_by": user, "status": "Open"}},
        {"title": "Surveys Done", "count": frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Completed"}), "tat": 0, "route": "Site Survey", "filter": {"surveyed_by": user, "status": "Completed"}}
    ]

    plan_data = [
        {"title": "Surveys Today", "count": frappe.db.count("Site Survey", {"survey_date": today, "surveyed_by": user}), "route": "Site Survey", "filter": {"survey_date": today, "surveyed_by": user}},
        {"title": "Open Leads", "count": frappe.db.count("Lead", {"lead_owner": user, "status": "Open"}), "route": "Lead", "filter": {"lead_owner": user, "status": "Open"}},
        {"title": "Completed Today", "count": frappe.db.count("Site Survey", {"completed_date": today, "surveyed_by": user}), "route": "Site Survey", "filter": {"completed_date": today, "surveyed_by": user}}
    ]

    for d in frappe.db.get_all("Site Survey", filters={"surveyed_by": user, "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Site Survey", "type": "Conduct Survey", "client": d.get("lead_name"), "ref": d.get("name"), "date": str(d.get("exp_nxstp_dt") or ""), "tat": d.get("tat_days") or 0})

    tl = frappe.db.count("Lead", {"lead_owner": user})
    ts = frappe.db.count("Site Survey", {"surveyed_by": user})
    performance = {
        "label1": "Surveys Done", "value1": frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Completed", "completed_date": [">=", month_start]}),
        "label2": "Leads Generated", "value2": frappe.db.count("Lead", {"lead_owner": user, "creation": [">=", month_start]}),
        "label3": "Conversion %", "value3": safe_pct(ts, tl)
    }
    actions = {"btn1_label": "Generate Lead", "btn1_type": "new_doc", "btn1_target": "Lead", "btn2_label": "Conduct Survey", "btn2_type": "new_doc", "btn2_target": "Site Survey", "btn2_visible": True}

# ============================================================
# SORT & DEDUPLICATE PENDING QUEUE
# ============================================================

# Manual Sort (replaces restricted .sort() method)
n = len(pending_tasks)
for i in range(n):
    for j in range(0, n - i - 1):
        d1 = pending_tasks[j].get("date")
        d2 = pending_tasks[j + 1].get("date")
        s1 = d1 if d1 else "9999-12-31"
        s2 = d2 if d2 else "9999-12-31"
        if s1 > s2:
            temp = pending_tasks[j]
            pending_tasks[j] = pending_tasks[j + 1]
            pending_tasks[j + 1] = temp

# Deduplicate
seen = []
dedup = []
for t in pending_tasks:
    key = str(t.get("ref") or "") + "|" + str(t.get("type") or "")
    if key not in seen:
        seen.append(key)
        dedup.append(t)
pending_tasks = dedup

# ── RECENT ACTIVITY ─────────────────────────────────────────
activities = []
act_raw = frappe.db.get_all(
    "Version",
    filters={"owner": user},
    fields=["ref_doctype", "docname", "creation"],
    limit=6,
    order_by="creation desc"
)
for a in act_raw:
    activities.append({
        "ref_doctype": a.get("ref_doctype") or "",
        "docname":     a.get("docname")     or "",
        "creation":    str(a.get("creation") or "")
    })

# ============================================================
# FINAL RESPONSE
# ============================================================

frappe.response["message"] = {
    "role":         process_label,
    "employee": {
        "employee_id":   emp_id,
        "employee_name": emp_name,
        "designation":   employee.get("designation") or "",
        "department":    employee.get("department")  or ""
    },
    "attendance":   attendance,
    "leaves":       leaves,
    "payslips":     payslips,
    "holidays":     holidays,
    "notifications": notifications,
    "kpi":          kpi_data,
    "plan":         plan_data,
    "tasks":        pending_tasks[:10],
    "performance":  performance,
    "activities":   activities,
    "actions":      actions
}
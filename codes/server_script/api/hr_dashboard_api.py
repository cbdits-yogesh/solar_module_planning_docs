# ================================================================
# SERVER SCRIPT — hr_dashboard_api  (100% SAFE EXEC COMPLIANT)
# Type        : API
# Method Name : hr_dashboard_api
# ================================================================

DEMO_MODE = False

action   = frappe.form_dict.get("action")     or ""
f_month  = int(frappe.form_dict.get("month")  or frappe.utils.getdate().month)
f_year   = int(frappe.form_dict.get("year")   or frappe.utils.getdate().year)
f_dept   = frappe.form_dict.get("department") or ""
f_branch = frappe.form_dict.get("branch")     or ""
f_date   = frappe.form_dict.get("date")       or frappe.utils.today()

# ================================================================
# ACTION: overview
# ================================================================
if action == "overview":
    if DEMO_MODE:
        frappe.response["message"] = {}

    else:
        company    = frappe.db.get_single_value("Global Defaults", "default_company") or ""
        today_date = frappe.utils.today()
        today_dt   = frappe.utils.getdate(today_date)

        emp_f_ov = {"status": "Active", "company": company}
        if f_dept:   emp_f_ov["department"] = f_dept
        if f_branch: emp_f_ov["branch"]     = f_branch
        total_employees = frappe.db.count("Employee", emp_f_ov)

        checkin_query = """
            SELECT count(*) as count, sum(late_entry) as late
            FROM `tabEmployee Checkin` ec
            LEFT JOIN `tabEmployee` e ON ec.employee = e.name
            WHERE DATE(ec.time) = %s AND ec.log_type = 'IN'
        """
        params = [today_date]
        if f_dept:
            checkin_query = checkin_query + " AND e.department = %s"
            params.append(f_dept)
        if f_branch:
            checkin_query = checkin_query + " AND e.branch = %s"
            params.append(f_branch)

        checkin_res    = frappe.db.sql(checkin_query, params, as_dict=True)[0]
        today_checkins = checkin_res.count or 0
        today_late     = int(checkin_res.late or 0)

        # REPLACED "On Leave" with "Pending Attendance" KPI
        att_req_f = {
        "docstatus": 0,
        "company": company
        }
        if f_dept: att_req_f["department"] = f_dept
        pending_attendance = frappe.db.count("Attendance Request", att_req_f)

        leave_f_ov = {
        "status": ["in", ["Open", "Pending"]],
        "company": company
        }
        if f_dept: leave_f_ov["department"] = f_dept
        pending_leaves = frappe.db.count("Leave Application", leave_f_ov)

        exp_f_ov = {
        "approval_status": ["in", ["Draft", "Pending"]],
        "company": company
        }
        if f_dept: exp_f_ov["department"] = f_dept
        
        # 1. Get the count of pending expenses
        pending_expenses_count = frappe.db.count("Expense Claim", exp_f_ov)
        
        # 2. Get the total amount of those pending expenses (this fixes your NameError)
        exp_draft = frappe.db.get_all("Expense Claim", filters=exp_f_ov, fields=["total_claimed_amount"])
        pending_expense_amount = sum((e.total_claimed_amount or 0) for e in exp_draft)

        try:
            active_onboardings = frappe.db.count("Employee Onboarding",
                {"status": ["in", ["Pending", "In Process"]]})
        except Exception:
            active_onboardings = 0

        try:
            thirty_ahead = frappe.utils.add_days(today_dt, 30)
            upcoming_separations = frappe.db.count("Employee", {
                "status":         "Active",
                "relieving_date": ["between", [today_date, str(thirty_ahead)]]
            })
        except Exception:
            upcoming_separations = 0

        try:
            incomplete_docs = frappe.db.count("Employee", {
                "status":     "Active",
                "company":    company,
                "pan_number": ["is", "not set"]
            })
        except Exception:
            incomplete_docs = 0

        today_mmdd = "-" + str(today_dt.month).zfill(2) + "-" + str(today_dt.day).zfill(2)
        all_emps_cel = frappe.db.get_all("Employee",
            filters={"status": "Active", "company": company},
            fields=["name", "employee_name", "date_of_birth", "date_of_joining"])
        birthdays_today     = []
        anniversaries_today = []
        for ec in all_emps_cel:
            if ec.date_of_birth and str(ec.date_of_birth)[4:] == today_mmdd:
                birthdays_today.append({"employee": ec.name, "employee_name": ec.employee_name})
            if ec.date_of_joining and str(ec.date_of_joining)[4:] == today_mmdd:
                yrs = today_dt.year - frappe.utils.getdate(ec.date_of_joining).year
                if yrs > 0:
                    anniversaries_today.append({
                        "employee": ec.name,
                        "employee_name": ec.employee_name,
                        "years": yrs
                    })

        departments = [d.name for d in frappe.db.get_all("Department",
            filters={"is_group": 0, "company": company}, fields=["name"])]
        branches    = [b.name for b in frappe.db.get_all("Branch", fields=["name"])]

        frappe.response["message"] = {
            "company_name": company,
            "kpi": {
                "total_employees":        total_employees,
                "today_checkins":         today_checkins,
                "today_late":             today_late,
                "pending_attendance":     pending_attendance, # Updated here
                "pending_leaves":         pending_leaves,
                "pending_expenses":       pending_expenses_count,
                "pending_expense_amount": pending_expense_amount,
                "active_onboardings":     active_onboardings,
                "upcoming_separations":   upcoming_separations,
                "incomplete_docs":        incomplete_docs
            },
            "celebrations": {
                "birthdays":     birthdays_today,
                "anniversaries": anniversaries_today
            },
            "departments": departments,
            "branches":    branches
        }

# ================================================================
# ACTION: daily_counts
# ================================================================
elif action == "daily_counts":
    base_f = {"attendance_date": f_date, "docstatus": 1}
    if f_dept:   base_f["department"] = f_dept
    if f_branch: base_f["branch"]     = f_branch

    # --- Present sub-counts ---
    present_f = base_f.copy()
    present_f["status"] = "Present"
    present_count = frappe.db.count("Attendance", present_f)

    half_f = base_f.copy()
    half_f["status"] = "Half Day"
    half_day_count = frappe.db.count("Attendance", half_f)

    wfh_f = base_f.copy()
    wfh_f["status"] = "Work From Home"
    wfh_count = frappe.db.count("Attendance", wfh_f)

    # --- Absent sub-counts ---
    absent_f = base_f.copy()
    absent_f["status"] = "Absent"
    absent_count = frappe.db.count("Attendance", absent_f)

    leave_f = base_f.copy()
    leave_f["status"] = ["in", ["On Leave", "Leave"]]
    leave_count = frappe.db.count("Attendance", leave_f)

    frappe.response["message"] = {
        "present_total":  present_count + half_day_count + wfh_count,
        "absent_total":   absent_count + leave_count,
        "present_count":  present_count,
        "half_day_count": half_day_count,
        "wfh_count":      wfh_count,
        "absent_count":   absent_count,
        "leave_count":    leave_count
    }

# ================================================================
# ACTION: daily_list (UPDATED TO SHARE FIELDS)
# ================================================================
elif action == "daily_list":
    mode       = frappe.form_dict.get("mode")       or "present"
    sub_status = frappe.form_dict.get("sub_status") or ""

    base_f = {"attendance_date": f_date, "docstatus": 1}
    if f_dept:   base_f["department"] = f_dept
    if f_branch: base_f["branch"]     = f_branch

    fields = ["employee", "employee_name", "status", "working_hours",
              "late_entry", "early_exit", "in_time", "out_time", "shift"]

    if mode == "present":
        if sub_status and sub_status not in ["all", "", "All Present"]:
            base_f["status"] = sub_status
        else:
            base_f["status"] = ["in", ["Present", "Half Day", "Work From Home"]]
    else:
        if sub_status == "Absent":
            base_f["status"] = "Absent"
        elif sub_status in ["On Leave", "Leave"]:
            base_f["status"] = ["in", ["On Leave", "Leave"]]
        else:
            base_f["status"] = ["in", ["Absent", "On Leave", "Leave"]]

    data = frappe.db.get_all(
        "Attendance",
        filters=base_f,
        fields=fields,
        order_by="employee_name asc"
    )

    # ── Enrich with late minutes + penalty (same logic as checkin_details) ──
    emp_ids_dl = list(set(d.employee for d in data if d.employee))
    rate_map   = {}
    if emp_ids_dl:
        emp_rates = frappe.db.get_all("Employee",
            filters={"name": ["in", emp_ids_dl]},
            fields=["name", "lateearly_rate"])
        for er in emp_rates:
            rate_map[er.name] = er.lateearly_rate or 0

    shift_ids_dl = list(set(d.shift for d in data if d.shift))
    shift_map    = {}
    if shift_ids_dl:
        shift_rows = frappe.db.get_all("Shift Type",
            filters={"name": ["in", shift_ids_dl]},
            fields=["name", "start_time", "enable_late_entry_marking", "late_entry_grace_period"])
        for sr in shift_rows:
            shift_map[sr.name] = sr

    for d in data:
        d["late_minutes"]   = 0
        d["penalty_amount"] = 0

        if d.get("late_entry") == 1 and d.get("in_time") and d.get("shift") in shift_map:
            in_dt      = d.get("in_time")
            shift_info = shift_map[d.get("shift")]

            in_secs           = in_dt.hour * 3600 + in_dt.minute * 60 + in_dt.second
            shift_start_secs  = shift_info.start_time.total_seconds() if shift_info.start_time else 0

            grace_secs = 0
            if shift_info.enable_late_entry_marking:
                grace_secs = (shift_info.late_entry_grace_period or 0) * 60

            late_secs = in_secs - (shift_start_secs + grace_secs)
            late_minutes_dl = int(late_secs // 60) if late_secs > 0 else 0

            d["late_entry"]     = 1 if late_minutes_dl > 0 else 0
            d["late_minutes"]   = late_minutes_dl
            d["penalty_amount"] = late_minutes_dl * rate_map.get(d.employee, 0)
        else:
            d["late_entry"] = 0 if d.get("late_entry") == 1 else d.get("late_entry")

        if "shift" in d: del d["shift"]

    frappe.response["message"] = {
        "data": data
    }

# ================================================================
# ACTION: checkin_details
# ================================================================
elif action == "checkin_details":
    from_date  = frappe.form_dict.get("from_date") or frappe.utils.today()
    to_date    = frappe.form_dict.get("to_date")   or frappe.utils.today()
    company_ci = frappe.db.get_single_value("Global Defaults", "default_company") or ""

    query = """
        SELECT ec.employee, ec.employee_name, ec.time, ec.log_type,
               ec.custom_area_name, ec.late_entry, ec.shift,
               st.start_time as shift_start_time,
               st.enable_late_entry_marking as grace_enabled,
               st.late_entry_grace_period as grace_minutes,
               e.lateearly_rate as late_rate
        FROM `tabEmployee Checkin` ec
        LEFT JOIN `tabEmployee` e ON ec.employee = e.name
        LEFT JOIN `tabShift Type` st ON ec.shift = st.name
        WHERE DATE(ec.time) BETWEEN %s AND %s
          AND ec.log_type = 'IN'
    """
    params = [from_date, to_date]
    if f_dept:
        query = query + " AND e.department = %s"
        params.append(f_dept)
    if f_branch:
        query = query + " AND e.branch = %s"
        params.append(f_branch)
    query = query + " ORDER BY ec.time DESC LIMIT 500"

    data = frappe.db.sql(query, params, as_dict=True)

    late_count     = 0
    ontime_count   = 0
    checked_in_ids = set()

    for row in data:
        checkin_dt = row.get("time")

        late_minutes   = 0
        penalty_amount = 0

        if row.get("late_entry") == 1 and checkin_dt and row.get("shift_start_time") is not None:
            checkin_secs      = checkin_dt.hour * 3600 + checkin_dt.minute * 60 + checkin_dt.second
            shift_start_secs  = row.get("shift_start_time").total_seconds()
        
            grace_secs = 0
            if row.get("grace_enabled"):
                grace_secs = (row.get("grace_minutes") or 0) * 60
        
            late_threshold_secs = shift_start_secs + grace_secs
            late_secs = checkin_secs - late_threshold_secs
        
            if late_secs > 0:
                late_minutes = int(late_secs // 60)
        
            rate = row.get("late_rate") or 0
            penalty_amount = late_minutes * rate
        
            # Override Frappe's boundary flag with our own strict "> grace period" rule
            row["late_entry"] = 1 if late_minutes > 0 else 0
        
        row["late_minutes"]   = late_minutes
        row["penalty_amount"] = penalty_amount

        for helper_field in ["shift_start_time", "grace_enabled", "grace_minutes", "late_rate", "shift"]:
            if helper_field in row:
                del row[helper_field]

        if checkin_dt:
            row["time"] = frappe.utils.format_datetime(checkin_dt, "hh:mm a")
        if row.get("late_entry") == 1:
            late_count = late_count + 1
        else:
            ontime_count = ontime_count + 1
        checked_in_ids.add(row.get("employee"))

    emp_f_ci = {"status": "Active", "company": company_ci}
    if f_dept:   emp_f_ci["department"] = f_dept
    if f_branch: emp_f_ci["branch"]     = f_branch
    all_emps = frappe.db.get_all("Employee", filters=emp_f_ci,
        fields=["name as employee", "employee_name", "department"])
    not_checked_in = [e for e in all_emps if e.employee not in checked_in_ids]

    frappe.response["message"] = {
        "data":           data,
        "total":          len(data),
        "late_count":     late_count,
        "ontime_count":   ontime_count,
        "not_in_count":   len(not_checked_in),
        "not_checked_in": not_checked_in
    }

# ================================================================
# ACTION: checkout_details
# ================================================================
elif action == "checkout_details":
    from_date  = frappe.form_dict.get("from_date") or frappe.utils.today()
    to_date    = frappe.form_dict.get("to_date")   or frappe.utils.today()
    company_co = frappe.db.get_single_value("Global Defaults", "default_company") or ""

    query = """
        SELECT ec.employee, ec.employee_name, ec.time, ec.shift,
               ec.custom_area_name,
               st.end_time as shift_end_time,
               st.enable_early_exit_marking as grace_enabled,
               st.early_exit_grace_period as grace_minutes
        FROM `tabEmployee Checkin` ec
        LEFT JOIN `tabEmployee` e ON ec.employee = e.name
        LEFT JOIN `tabShift Type` st ON ec.shift = st.name
        WHERE DATE(ec.time) BETWEEN %s AND %s
          AND ec.log_type = 'OUT'
    """
    params = [from_date, to_date]
    if f_dept:
        query = query + " AND e.department = %s"
        params.append(f_dept)
    if f_branch:
        query = query + " AND e.branch = %s"
        params.append(f_branch)
    query = query + " ORDER BY ec.time DESC LIMIT 500"

    data = frappe.db.sql(query, params, as_dict=True)

    early_count     = 0
    ontime_count    = 0
    checked_out_ids = set()

    for row in data:
        checkout_dt = row.get("time")

        early_minutes = 0
        is_early      = False

        if checkout_dt and row.get("shift_end_time") is not None:
            checkout_secs = checkout_dt.hour * 3600 + checkout_dt.minute * 60 + checkout_dt.second
            shift_end_secs = row.get("shift_end_time").total_seconds()

            grace_secs = 0
            if row.get("grace_enabled"):
                grace_secs = (row.get("grace_minutes") or 0) * 60

            early_threshold_secs = shift_end_secs - grace_secs
            early_secs = early_threshold_secs - checkout_secs

            if early_secs > 0:
                early_minutes = int(early_secs // 60)
                is_early = True

        row["early_exit"]     = 1 if is_early else 0
        row["early_minutes"]  = early_minutes

        for helper_field in ["shift_end_time", "grace_enabled", "grace_minutes", "shift"]:
            if helper_field in row:
                del row[helper_field]

        if checkout_dt:
            row["time"] = frappe.utils.format_datetime(checkout_dt, "hh:mm a")
        if is_early:
            early_count = early_count + 1
        else:
            ontime_count = ontime_count + 1
        checked_out_ids.add(row.get("employee"))

    ci_params = [from_date, to_date]
    ci_query  = """
        SELECT DISTINCT ec.employee
        FROM `tabEmployee Checkin` ec
        LEFT JOIN `tabEmployee` e ON ec.employee = e.name
        WHERE DATE(ec.time) BETWEEN %s AND %s
          AND ec.log_type = 'IN'
    """
    if f_dept:
        ci_query = ci_query + " AND e.department = %s"
        ci_params.append(f_dept)
    if f_branch:
        ci_query = ci_query + " AND e.branch = %s"
        ci_params.append(f_branch)

    ci_rows           = frappe.db.sql(ci_query, ci_params, as_dict=True)
    checked_in_ids_co = set(r.employee for r in ci_rows)
    not_out_ids       = checked_in_ids_co - checked_out_ids

    not_co_emps = []
    if not_out_ids:
        not_co_emps = frappe.db.get_all("Employee",
            filters={"name": ["in", list(not_out_ids)]},
            fields=["name as employee", "employee_name", "department"])

    frappe.response["message"] = {
        "data":            data,
        "total":           len(data),
        "early_count":     early_count,
        "ontime_count":    ontime_count,
        "not_out_count":   len(not_co_emps),
        "not_checked_out": not_co_emps
    }

# ================================================================
# ACTION: attendance
# ================================================================
elif action == "attendance":
    company_att   = frappe.db.get_single_value("Global Defaults", "default_company") or ""
    last_day_att  = frappe.utils.get_last_day(str(f_year) + "-" + str(f_month).zfill(2) + "-01")
    days_in_month = last_day_att.day
    start_str     = str(f_year) + "-" + str(f_month).zfill(2) + "-01"
    end_str       = str(f_year) + "-" + str(f_month).zfill(2) + "-" + str(days_in_month).zfill(2)

    emp_f_att = {"status": "Active", "company": company_att}
    if f_dept:   emp_f_att["department"] = f_dept
    if f_branch: emp_f_att["branch"]     = f_branch
    employees_att = frappe.db.get_all("Employee", filters=emp_f_att,
        fields=["name", "employee_name"])

    att_f_month = {"attendance_date": ["between", [start_str, end_str]], "docstatus": 1}
    if f_dept: att_f_month["department"] = f_dept
    attendance_records = frappe.db.get_all("Attendance", filters=att_f_month,
        fields=["employee", "attendance_date", "status"])

    att_map_b      = {}
    mc_present  = 0
    mc_on_leave = 0
    mc_absent   = 0
    mc_half_day = 0

    for rec_a in attendance_records:
        rec_day_a  = frappe.utils.getdate(rec_a.attendance_date).day
        rec_key_a  = rec_a.employee + "|" + str(rec_day_a)
        rec_code_a = "p"
        if rec_a.status == "Absent":
            rec_code_a = "a"
            mc_absent   = mc_absent + 1
        elif rec_a.status == "Half Day":
            rec_code_a = "h"
            mc_half_day = mc_half_day + 1
        elif rec_a.status in ["On Leave", "Leave"]:
            rec_code_a  = "l"
            mc_on_leave = mc_on_leave + 1
        else:
            mc_present = mc_present + 1
        att_map_b[rec_key_a] = rec_code_a

    monthly_counts = {
        "present":  mc_present,
        "on_leave": mc_on_leave,
        "absent":   mc_absent,
        "half_day": mc_half_day
    }

    time_map = {}
    checkins = frappe.db.sql("""
        SELECT employee, DATE(time) as date,
               MIN(time) as in_time, MAX(time) as out_time
        FROM `tabEmployee Checkin`
        WHERE time BETWEEN %s AND %s
        GROUP BY employee, DATE(time)
    """, (start_str + " 00:00:00", end_str + " 23:59:59"), as_dict=True)

    for c in checkins:
        day   = c.date.day
        key   = c.employee + "|" + str(day)
        in_t  = frappe.utils.format_datetime(c.in_time,  "HH:mm") if c.in_time else ""
        out_t = frappe.utils.format_datetime(c.out_time, "HH:mm") if c.out_time and c.out_time != c.in_time else ""
        time_map[key] = {"in": in_t, "out": out_t}

    heatmap_data_b = []
    for emp_b in employees_att:
        days_b = {}
        for db in range(1, days_in_month + 1):
            date_str_b = str(f_year) + "-" + str(f_month).zfill(2) + "-" + str(db).zfill(2)
            dow_b      = frappe.utils.getdate(date_str_b).weekday()
            key        = emp_b.name + "|" + str(db)
            
            # 1. Try to get the actual attendance record first (Present, Half Day, Absent, etc.)
            status = att_map_b.get(key)
            
            # 2. If there is NO attendance data for this specific day, then assign fallbacks
            if not status:
                # If it's Saturday (5) or Sunday (6), mark it as 'w' (Weekend)
                if dow_b >= 5:
                    status = "w"
                # If it's a normal weekday with missing data, leave it blank (or you can use "a" for default absent)
                else:
                    status = "-"
            day_obj    = {"status": status}
            if key in time_map:
                day_obj["in"]  = time_map[key]["in"]
                day_obj["out"] = time_map[key]["out"]
            days_b[db] = day_obj
        heatmap_data_b.append({
            "employee_id":   emp_b.name,
            "employee_name": emp_b.employee_name,
            "days":          days_b
        })

    frappe.response["message"] = {
        "heatmap":        heatmap_data_b,
        "monthly_counts": monthly_counts
    }

# ================================================================
# ACTION: leaves
# ================================================================
elif action == "leaves":
    company_lv     = frappe.db.get_single_value("Global Defaults", "default_company") or ""
    last_day_lv    = frappe.utils.get_last_day(str(f_year) + "-" + str(f_month).zfill(2) + "-01")
    month_start_lv = str(f_year) + "-" + str(f_month).zfill(2) + "-01"
    month_end_lv   = str(f_year) + "-" + str(f_month).zfill(2) + "-" + str(last_day_lv.day).zfill(2)

    la_f_lv = {
        "status":    ["in", ["Open", "Approved", "Rejected"]],
        "from_date": ["<=", month_end_lv],
        "to_date":   [">=", month_start_lv],
        "docstatus": ["in", [0, 1]]
    }
    if f_dept: la_f_lv["department"] = f_dept
    leave_apps_lv = frappe.db.get_all("Leave Application", filters=la_f_lv,
        fields=["name", "employee", "employee_name", "leave_type", "from_date",
                "to_date", "total_leave_days", "status", "leave_approver", "leave_approver_name"],
        order_by="from_date desc", limit=20)

    emp_count_lv  = frappe.db.count("Employee", {"status": "Active", "company": company_lv}) or 1
    year_start_lv = str(f_year) + "-01-01"

    cl_rows_lv = frappe.db.get_all("Leave Ledger Entry", filters={"leave_type": "Casual Leave",    "transaction_type": "Leave Application", "from_date": [">=", year_start_lv], "is_expired": 0, "docstatus": 1}, fields=["leaves"])
    sl_rows_lv = frappe.db.get_all("Leave Ledger Entry", filters={"leave_type": "Sick Leave",      "transaction_type": "Leave Application", "from_date": [">=", year_start_lv], "is_expired": 0, "docstatus": 1}, fields=["leaves"])
    pl_rows_lv = frappe.db.get_all("Leave Ledger Entry", filters={"leave_type": "Privilege Leave", "transaction_type": "Leave Application", "from_date": [">=", year_start_lv], "is_expired": 0, "docstatus": 1}, fields=["leaves"])
    co_rows_lv = frappe.db.get_all("Leave Ledger Entry", filters={"leave_type": "Comp Off",        "transaction_type": "Leave Application", "from_date": [">=", year_start_lv], "is_expired": 0, "docstatus": 1}, fields=["leaves"])

    cl_avg_lv = str(round(sum(abs(r.leaves or 0) for r in cl_rows_lv) / emp_count_lv, 1)) + " / 12"
    sl_avg_lv = str(round(sum(abs(r.leaves or 0) for r in sl_rows_lv) / emp_count_lv, 1)) + " / 12"
    pl_avg_lv = str(round(sum(abs(r.leaves or 0) for r in pl_rows_lv) / emp_count_lv, 1)) + " / 18"
    co_avg_lv = str(round(sum(abs(r.leaves or 0) for r in co_rows_lv) / emp_count_lv, 1)) + " / 10"

    lb_all_rows = frappe.db.get_all("Leave Ledger Entry",
        filters={
            "leave_type": ["in", ["Casual Leave", "Sick Leave", "Privilege Leave"]],
            "from_date":  [">=", str(f_year) + "-01-01"],
            "is_expired": 0,
            "docstatus":  1
        },
        fields=["employee", "leave_type", "leaves"])

    lb_totals_map = {}
    for lba in lb_all_rows:
        if lba.employee not in lb_totals_map:
            lb_totals_map[lba.employee] = {"cl": 0.0, "sl": 0.0, "pl": 0.0}
        if lba.leave_type == "Casual Leave":
            lb_totals_map[lba.employee]["cl"] = lb_totals_map[lba.employee]["cl"] + (lba.leaves or 0)
        elif lba.leave_type == "Sick Leave":
            lb_totals_map[lba.employee]["sl"] = lb_totals_map[lba.employee]["sl"] + (lba.leaves or 0)
        elif lba.leave_type == "Privilege Leave":
            lb_totals_map[lba.employee]["pl"] = lb_totals_map[lba.employee]["pl"] + (lba.leaves or 0)

    lb_emp_ids  = list(lb_totals_map.keys())
    lb_name_map = {}
    if lb_emp_ids:
        for lbe in frappe.db.get_all("Employee", filters={"name": ["in", lb_emp_ids]},
                fields=["name", "employee_name", "department"]):
            lb_name_map[lbe.name] = {"employee_name": lbe.employee_name, "department": lbe.department or ""}

    lb_list_build = []
    for lb_emp_id in lb_totals_map:
        cl_b    = max(0, round(lb_totals_map[lb_emp_id]["cl"], 1))
        sl_b    = max(0, round(lb_totals_map[lb_emp_id]["sl"], 1))
        pl_b    = max(0, round(lb_totals_map[lb_emp_id]["pl"], 1))
        total_b = cl_b + sl_b + pl_b
        emp_info_b = lb_name_map.get(lb_emp_id, {"employee_name": lb_emp_id, "department": ""})
        lb_list_build.append({
            "employee": lb_emp_id, "employee_name": emp_info_b["employee_name"],
            "department": emp_info_b["department"], "cl": cl_b, "sl": sl_b, "pl": pl_b, "total": total_b
        })

    lb_overview = sorted(lb_list_build, key=lambda x: x["total"], reverse=True)[:8]

    today_lv  = frappe.utils.today()
    two_weeks = frappe.utils.add_days(frappe.utils.getdate(today_lv), 14)
    upcoming_lv = frappe.db.get_all("Leave Application",
        filters={"status": "Approved", "from_date": ["between", [today_lv, str(two_weeks)]], "docstatus": 1},
        fields=["name", "employee", "employee_name", "leave_type", "from_date", "to_date", "total_leave_days"],
        order_by="from_date asc", limit=10)

    frappe.response["message"] = {
        "leave_applications":     leave_apps_lv,
        "leave_summary":          {"cl_avg": cl_avg_lv, "sl_avg": sl_avg_lv, "pl_avg": pl_avg_lv, "comp_off_avg": co_avg_lv},
        "leave_balance_overview": lb_overview,
        "upcoming_leaves":        upcoming_lv
    }

# ================================================================
# ACTION: payroll
# ================================================================
elif action == "payroll":
    company_py     = frappe.db.get_single_value("Global Defaults", "default_company") or ""
    last_day_py    = frappe.utils.get_last_day(str(f_year) + "-" + str(f_month).zfill(2) + "-01")
    month_start_py = str(f_year) + "-" + str(f_month).zfill(2) + "-01"
    month_end_py   = str(f_year) + "-" + str(f_month).zfill(2) + "-" + str(last_day_py.day).zfill(2)

    emp_f_py = {"status": "Active", "company": company_py}
    if f_dept: emp_f_py["department"] = f_dept
    total_emp_py = frappe.db.count("Employee", emp_f_py)

    slips_py = frappe.db.get_all("Salary Slip",
        filters={"start_date": [">=", month_start_py], "end_date": ["<=", month_end_py], "docstatus": ["in", [0, 1]]},
        fields=["employee", "employee_name", "net_pay", "gross_pay", "docstatus"])
    submitted_py  = [s for s in slips_py if s.docstatus == 1]
    total_payroll = sum(s.net_pay or 0 for s in submitted_py)

    sorted_slips_py = sorted(submitted_py, key=lambda s: (s.net_pay or 0), reverse=True)[:9]
    salary_bars_py  = [{"employee_name": s.employee_name, "base": s.net_pay or 0} for s in sorted_slips_py]
    if not salary_bars_py:
        sorted_all_py  = sorted(slips_py, key=lambda s: (s.gross_pay or 0), reverse=True)[:9]
        salary_bars_py = [{"employee_name": s.employee_name, "base": s.gross_pay or 0} for s in sorted_all_py]

    frappe.response["message"] = {
        "payroll_summary": {
            "total_payroll":   total_payroll,
            "slips_generated": len(slips_py),
            "submitted":       len(submitted_py),
            "total_employees": total_emp_py
        },
        "salary_bars": salary_bars_py
    }

# ================================================================
# ACTION: expenses
# ================================================================
elif action == "expenses":
    company_ex     = frappe.db.get_single_value("Global Defaults", "default_company") or ""
    last_day_ex    = frappe.utils.get_last_day(str(f_year) + "-" + str(f_month).zfill(2) + "-01")
    month_start_ex = str(f_year) + "-" + str(f_month).zfill(2) + "-01"
    month_end_ex   = str(f_year) + "-" + str(f_month).zfill(2) + "-" + str(last_day_ex.day).zfill(2)

    expenses_ex = frappe.db.get_all("Expense Claim",
        filters={"posting_date": ["between", [month_start_ex, month_end_ex]], "docstatus": ["in", [0, 1]]},
        fields=["name", "employee", "employee_name", "total_claimed_amount", "approval_status"],
        order_by="creation desc", limit=15)
    for exp_ex in expenses_ex:
        exp_det = frappe.db.get_all("Expense Claim Detail", filters={"parent": exp_ex.name},
            fields=["expense_type"], limit=1)
        exp_ex["expense_type"] = exp_det[0].expense_type if exp_det else "-"

    today_ex      = frappe.utils.getdate()
    week_start_ex = frappe.utils.add_days(today_ex, -today_ex.weekday())
    week_end_ex   = frappe.utils.add_days(week_start_ex, 6)
    ts_raw_ex = frappe.db.get_all("Timesheet",
        filters={"start_date": [">=", str(week_start_ex)], "end_date": ["<=", str(week_end_ex)], "docstatus": ["in", [0, 1]]},
        fields=["name", "employee", "employee_name", "start_date", "end_date",
                "total_hours", "total_billable_hours", "status"],
        order_by="employee asc")
    ts_list_ex = []
    for tex in ts_raw_ex:
        ts_list_ex.append({
            "name":                 tex.name,
            "employee":             tex.employee,
            "employee_name":        tex.employee_name,
            "period":               frappe.utils.formatdate(tex.start_date, "d MMM") + " - " + frappe.utils.formatdate(tex.end_date, "d MMM"),
            "total_hours":          round(tex.total_hours or 0, 1),
            "total_billable_hours": round(tex.total_billable_hours or 0, 1),
            "status":               tex.status or "Draft"
        })

    frappe.response["message"] = {
        "expenses":   expenses_ex,
        "timesheets": ts_list_ex
    }

# ================================================================
# ACTION: recruitment
# ================================================================
elif action == "recruitment":
    company_rc = frappe.db.get_single_value("Global Defaults", "default_company") or ""
    today_rc   = frappe.utils.today()

    applied_rc     = frappe.db.count("Job Applicant", {"status": "Open"})
    interviewed_rc = frappe.db.count("Interview",     {"status": "Cleared"})
    offered_rc     = frappe.db.count("Job Offer",     {"status": "Awaiting Response"})
    joined_rc      = frappe.db.count("Job Offer",     {"status": "Accepted"})
    open_roles_raw = frappe.db.get_all("Job Opening", filters={"status": "Open"}, fields=["name", "job_title"])
    open_roles_rc  = [{"job_title": r.job_title, "vacancies": 1} for r in open_roles_raw]

    total_app_rc = frappe.db.count("Appraisal", {"docstatus": ["in", [0, 1]], "company": company_rc})
    done_app_rc  = frappe.db.count("Appraisal", {"docstatus": 1, "company": company_rc})
    pct_rc       = round((done_app_rc / total_app_rc * 100), 0) if total_app_rc else 0

    recent_app_rc = frappe.db.get_all("Appraisal",
        filters={"docstatus": 1, "company": company_rc},
        fields=["employee", "employee_name"],
        order_by="modified desc", limit=5)
    for arc in recent_app_rc:
        arc["score"] = 0

    upcoming_tr_rc = []
    try:
        tr_raw_rc = frappe.db.get_all("Training Event",
            filters={"start_time": [">=", today_rc]},
            fields=["name", "start_time", "end_time"],
            order_by="start_time asc", limit=3)
        for trec in tr_raw_rc:
            upcoming_tr_rc.append({
                "name":         trec.name,
                "dates":        frappe.utils.formatdate(trec.start_time, "d MMM yyyy") + " - " + frappe.utils.formatdate(trec.end_time, "d MMM yyyy"),
                "participants": frappe.db.count("Training Event Employee", {"parent": trec.name})
            })
    except Exception:
        upcoming_tr_rc = []

    grievances_raw_rc = frappe.db.get_all("Employee Grievance",
        filters={"status": ["in", ["Open", "In Progress", "Resolved"]]},
        fields=["name", "subject", "status"],
        order_by="status asc, creation desc", limit=5)
    grievances_rc = []
    for grc in grievances_raw_rc:
        grievances_rc.append({
            "name":              grc.name,
            "employee":          grc.name,
            "employee_name":     "",
            "grievance_subject": grc.subject or "Grievance",
            "status":            grc.status,
            "priority":          "Medium"
        })

    frappe.response["message"] = {
        "recruitment": {
            "applied":     applied_rc,
            "interviewed": interviewed_rc,
            "offered":     offered_rc,
            "joined":      joined_rc,
            "open_roles":  open_roles_rc
        },
        "performance": {
            "completion_pct":     int(pct_rc),
            "completed":          done_app_rc,
            "total":              total_app_rc,
            "recent_appraisals":  recent_app_rc,
            "upcoming_trainings": upcoming_tr_rc
        },
        "grievances": grievances_rc
    }

# ================================================================
# UNKNOWN ACTION
# ================================================================
else:
    frappe.response["message"] = {
        "error": "Unknown action: '" + action + "'. Valid: overview | daily_counts | daily_list | checkin_details | checkout_details | attendance | leaves | payroll | expenses | recruitment"
    }
# ─────────────────────────────────────────────────────────────
#  TOGGLE:  True = demo data  |  False = real ERPNext data
# ─────────────────────────────────────────────────────────────
USE_DEMO_DATA = False

# ═════════════════════════════════════════════════════════════
#  DEMO DATA
# ═════════════════════════════════════════════════════════════
if USE_DEMO_DATA:
    frappe.response["message"] = {
        "employee": {
            "employee_id":   "HR-EMP-00001",
            "employee_name": "Riya Sharma",
            "designation":   "Software Engineer",
            "department":    "Technology"
        },
        "attendance": {
            "today_status":  "Present",
            "month_present": 21,
            "records": [
                # March 2026 — full month (31 days)
                {"date": "2026-03-01", "status": "Present"},
                {"date": "2026-03-02", "status": "Present"},
                {"date": "2026-03-03", "status": "Present"},
                {"date": "2026-03-04", "status": "Present"},
                {"date": "2026-03-05", "status": "Present"},
                {"date": "2026-03-06", "status": "Absent"},
                {"date": "2026-03-07", "status": "WFH"},
                {"date": "2026-03-08", "status": "WFH"},
                {"date": "2026-03-09", "status": "Present"},
                {"date": "2026-03-10", "status": "Present"},
                {"date": "2026-03-11", "status": "Present"},
                {"date": "2026-03-12", "status": "Half Day"},
                {"date": "2026-03-13", "status": "Present"},
                {"date": "2026-03-14", "status": "Absent"},
                {"date": "2026-03-15", "status": "WFH"},
                {"date": "2026-03-16", "status": "Present"},
                {"date": "2026-03-17", "status": "Present"},
                {"date": "2026-03-18", "status": "Present"},
                {"date": "2026-03-19", "status": "Present"},
                {"date": "2026-03-20", "status": "Present"},
                {"date": "2026-03-21", "status": "WFH"},
                {"date": "2026-03-22", "status": "WFH"},
                {"date": "2026-03-23", "status": "Present"},
                {"date": "2026-03-24", "status": "Present"},
                {"date": "2026-03-25", "status": "Absent"},
                {"date": "2026-03-26", "status": "Present"},
                {"date": "2026-03-27", "status": "Present"},
                {"date": "2026-03-28", "status": "Half Day"},
                {"date": "2026-03-29", "status": "WFH"},
                {"date": "2026-03-30", "status": "Present"},
                {"date": "2026-03-31", "status": "Present"},
                # February 2026 — sample data for filter testing
                {"date": "2026-02-01", "status": "Present"},
                {"date": "2026-02-02", "status": "Present"},
                {"date": "2026-02-03", "status": "WFH"},
                {"date": "2026-02-04", "status": "Absent"},
                {"date": "2026-02-05", "status": "Present"},
                {"date": "2026-02-06", "status": "Present"},
                {"date": "2026-02-07", "status": "WFH"},
                {"date": "2026-02-08", "status": "Present"},
                {"date": "2026-02-09", "status": "Present"},
                {"date": "2026-02-10", "status": "Present"},
                {"date": "2026-02-11", "status": "Half Day"},
                {"date": "2026-02-12", "status": "Present"},
                {"date": "2026-02-13", "status": "Present"},
                {"date": "2026-02-14", "status": "Present"},
                {"date": "2026-02-15", "status": "WFH"},
                {"date": "2026-02-16", "status": "Present"},
                {"date": "2026-02-17", "status": "Present"},
                {"date": "2026-02-18", "status": "Absent"},
                {"date": "2026-02-19", "status": "Present"},
                {"date": "2026-02-20", "status": "Present"},
                {"date": "2026-02-21", "status": "WFH"},
                {"date": "2026-02-22", "status": "WFH"},
                {"date": "2026-02-23", "status": "Present"},
                {"date": "2026-02-24", "status": "Present"},
                {"date": "2026-02-25", "status": "Present"},
                {"date": "2026-02-26", "status": "Present"},
                {"date": "2026-02-27", "status": "Present"},
                {"date": "2026-02-28", "status": "Half Day"}
            ]
        },
        "leaves": [
            {"leave_type": "Casual Leave",  "unused_leaves": 5,  "total_leaves": 12},
            {"leave_type": "Sick Leave",    "unused_leaves": 3,  "total_leaves": 6},
            {"leave_type": "Earned Leave",  "unused_leaves": 10, "total_leaves": 15},
            {"leave_type": "Comp Off",      "unused_leaves": 1,  "total_leaves": 3}
        ],
        "expenses": [
            {"name": "EXP-2026-0041", "total_claimed_amount": 1200, "approval_status": "Pending"},
            {"name": "EXP-2026-0038", "total_claimed_amount": 850,  "approval_status": "Approved"},
            {"name": "EXP-2026-0031", "total_claimed_amount": 3400, "approval_status": "Submitted"}
        ],
        "timesheets": [
            {"name": "TS-2026-0021", "total_hours": 8.5},
            {"name": "TS-2026-0019", "total_hours": 7.0},
            {"name": "TS-2026-0015", "total_hours": 9.0}
        ],
        "payslips": [
            {"start_date": "2026-02-01", "net_pay": 52000},
            {"start_date": "2026-01-01", "net_pay": 52000},
            {"start_date": "2025-12-01", "net_pay": 50500}
        ],
        "holidays": [
            {"holiday_date": "2026-03-25", "description": "Holi"},
            {"holiday_date": "2026-04-14", "description": "Ambedkar Jayanti"},
            {"holiday_date": "2026-04-18", "description": "Good Friday"},
            {"holiday_date": "2026-05-01", "description": "Maharashtra Day"},
            {"holiday_date": "2026-08-15", "description": "Independence Day"},
            {"holiday_date": "2026-10-02", "description": "Gandhi Jayanti"},
            {"holiday_date": "2026-10-24", "description": "Dussehra"},
            {"holiday_date": "2026-11-12", "description": "Diwali"}
        ],
        "notifications": [
            {"type": "system",      "subject": "Your leave application for 10-Mar has been approved.",  "date": "2026-03-14"},
            {"type": "system",      "subject": "Salary slip for February 2026 is now available.",        "date": "2026-03-10"},
            {"type": "system",      "subject": "Expense claim EXP-2026-0041 is under review.",           "date": "2026-03-12"},
            {"type": "birthday",    "subject": "Amit Verma's birthday is today! 🎂",                     "date": "2026-03-16", "person": "Amit Verma"},
            {"type": "birthday",    "subject": "Sneha Patil's birthday is in 3 days 🎂",                 "date": "2026-03-19", "person": "Sneha Patil"},
            {"type": "anniversary", "subject": "Rohan Mehta completes 5 years at the company today! 🎉", "date": "2026-03-16", "person": "Rohan Mehta", "years": 5},
            {"type": "anniversary", "subject": "Your 2nd work anniversary is this week! 🎉",             "date": "2026-03-18", "person": "Riya Sharma",  "years": 2, "self": True},
            {"type": "company",     "subject": "TechCorp was founded 12 years ago today! 🏢",            "date": "2026-03-16", "years": 12}
        ]
    }

# ═════════════════════════════════════════════════════════════
#  REAL DATA
# ═════════════════════════════════════════════════════════════
else:
    # ── Set your Employee ID here ────────────────────────────
    emp_id = "SRPL-GME-00081"
    # ────────────────────────────────────────────────────────

    emp_doc = frappe.get_all(
        "Employee",
        filters={"name": emp_id},
        fields=["name", "employee_name", "designation", "department", "holiday_list"],
        limit=1
    )

    if not emp_doc:
        frappe.response["message"] = {"error": "Employee " + emp_id + " not found."}
    else:
        emp    = emp_doc[0]
        emp_id = emp["name"]
        today       = frappe.utils.today()
        month_start = frappe.utils.get_first_day(today)
        month_end   = frappe.utils.get_last_day(today)
        # Fetch whole year for attendance filter
        year_start  = str(today)[:4] + "-01-01"
        year_end    = str(today)[:4] + "-12-31"

        # ── 2. Today's attendance ────────────────────────────
        today_att = frappe.get_all(
            "Attendance",
            filters={"employee": emp_id, "attendance_date": today, "docstatus": 1},
            fields=["status"],
            limit=1
        )
        today_status = today_att[0]["status"] if today_att else "Not Marked"

        # ── 3. Whole-year attendance records (for month filter) ─
        att_records = frappe.get_all(
            "Attendance",
            filters={
                "employee":        emp_id,
                "attendance_date": ["between", [year_start, year_end]],
                "docstatus":       1
            },
            fields=["attendance_date as date", "status"],
            order_by="attendance_date desc",
            limit=400
        )
        month_present = sum(
            1 for a in att_records
            if a.get("status") == "Present"
            and str(a.get("date", ""))[:7] == str(today)[:7]
        )

        # ── 4. Leave balances ─────────────────────────────────
        # Query active allocations; calculate balance = allocated - taken
        leave_allocs = frappe.get_all(
            "Leave Allocation",
            filters={
                "employee":  emp_id,
                "docstatus": 1,
                "from_date": ["<=", today],
                "to_date":   [">=", today]
            },
            fields=["leave_type", "total_leaves_allocated", "carry_forwarded_leaves_count"]
        )

        leave_balances = []
        for alloc in leave_allocs:
            lt = alloc["leave_type"]
            # Sum approved/taken leaves for this type in this allocation period
            taken_result = frappe.db.sql("""
                SELECT COALESCE(SUM(total_leave_days), 0) as taken
                FROM `tabLeave Application`
                WHERE employee    = %(emp)s
                  AND leave_type  = %(lt)s
                  AND status      = 'Approved'
                  AND docstatus   = 1
            """, {"emp": emp_id, "lt": lt}, as_dict=True)

            taken      = taken_result[0]["taken"] if taken_result else 0
            allocated  = (alloc.get("total_leaves_allocated") or 0)
            balance    = max(allocated - taken, 0)

            leave_balances.append({
                "leave_type":    lt,
                "unused_leaves": balance,
                "total_leaves":  allocated
            })

        # ── 5. Expense claims ─────────────────────────────────
        expenses = frappe.get_all(
            "Expense Claim",
            filters={"employee": emp_id, "docstatus": ["!=", 2]},
            fields=["name", "total_claimed_amount", "approval_status"],
            order_by="creation desc",
            limit=10
        )

        # ── 6. Timesheets ─────────────────────────────────────
        timesheets = frappe.get_all(
            "Timesheet",
            filters={"employee": emp_id, "docstatus": ["!=", 2]},
            fields=["name", "total_hours"],
            order_by="creation desc",
            limit=10
        )

        # ── 7. Payslips ───────────────────────────────────────
        payslips = frappe.get_all(
            "Salary Slip",
            filters={"employee": emp_id, "docstatus": 1},
            fields=["start_date", "net_pay"],
            order_by="start_date desc",
            limit=6
        )

        # ── 8. Upcoming holidays ──────────────────────────────
        holidays = []
        holiday_list_name = emp.get("holiday_list") or frappe.db.get_value(
            "Employee", emp_id, "holiday_list"
        )
        if holiday_list_name:
            holidays = frappe.get_all(
                "Holiday",
                filters={
                    "parent":       holiday_list_name,
                    "holiday_date": [">=", today]
                },
                fields=["holiday_date", "description"],
                order_by="holiday_date asc",
                limit=5
            )

        # ── 9. Notifications (ERPNext log) ────────────────────
        notifications = []
        try:
            notifications = frappe.get_all(
                "Notification Log",
                filters={"for_user": user_email, "read": 0},
                fields=["subject"],
                order_by="creation desc",
                limit=10
            )
        except Exception:
            try:
                notifications = frappe.get_all(
                    "Notification Log",
                    filters={"for_user": user_email},
                    fields=["subject"],
                    order_by="creation desc",
                    limit=10
                )
            except Exception:
                notifications = []

        # Tag existing system notifications
        for n in notifications:
            n["type"] = "system"
            n["date"] = str(today)

        # ── 10. Birthdays & Work Anniversaries (±7 days) ─────
        today_dt    = frappe.utils.getdate(today)
        today_md    = (today_dt.month, today_dt.day)
        window_days = 7

        all_employees = frappe.get_all(
            "Employee",
            filters={"status": "Active"},
            fields=["name", "employee_name", "date_of_birth", "date_of_joining"],
            limit=500
        )

        for e in all_employees:
            # ── Birthday ──────────────────────────────────────
            dob = e.get("date_of_birth")
            if dob:
                try:
                    dob_dt   = frappe.utils.getdate(dob)
                    # Build this year's occurrence
                    this_year_bday = frappe.utils.getdate(
                        str(today_dt.year) + "-" + str(dob_dt.month).zfill(2) + "-" + str(dob_dt.day).zfill(2)
                    )
                    diff = (this_year_bday - today_dt).days
                    if 0 <= diff <= window_days:
                        if diff == 0:
                            msg = e["employee_name"] + "'s birthday is today! 🎂"
                        elif diff == 1:
                            msg = e["employee_name"] + "'s birthday is tomorrow 🎂"
                        else:
                            msg = e["employee_name"] + "'s birthday is in " + str(diff) + " days 🎂"
                        notifications.append({
                            "type":    "birthday",
                            "subject": msg,
                            "date":    str(this_year_bday),
                            "person":  e["employee_name"]
                        })
                except Exception:
                    pass

            # ── Work Anniversary ──────────────────────────────
            doj = e.get("date_of_joining")
            if doj:
                try:
                    doj_dt   = frappe.utils.getdate(doj)
                    years    = today_dt.year - doj_dt.year
                    if years > 0:
                        this_year_anniv = frappe.utils.getdate(
                            str(today_dt.year) + "-" + str(doj_dt.month).zfill(2) + "-" + str(doj_dt.day).zfill(2)
                        )
                        diff = (this_year_anniv - today_dt).days
                        if 0 <= diff <= window_days:
                            yr_word = str(years) + (" year" if years == 1 else " years")
                            is_self = (e["name"] == emp_id)
                            if diff == 0:
                                if is_self:
                                    msg = "Happy " + yr_word + " work anniversary to you! 🎉"
                                else:
                                    msg = e["employee_name"] + " completes " + yr_word + " today! 🎉"
                            else:
                                day_word = "tomorrow" if diff == 1 else "in " + str(diff) + " days"
                                if is_self:
                                    msg = "Your " + yr_word + " work anniversary is " + day_word + " 🎉"
                                else:
                                    msg = e["employee_name"] + "'s " + yr_word + " anniversary is " + day_word + " 🎉"
                            notifications.append({
                                "type":    "anniversary",
                                "subject": msg,
                                "date":    str(this_year_anniv),
                                "person":  e["employee_name"],
                                "years":   years,
                                "self":    is_self
                            })
                except Exception:
                    pass

        # ── 11. Company founding anniversary ──────────────────
        try:
            company_doc = frappe.get_all(
                "Company",
                fields=["name", "date_of_establishment"],
                limit=1
            )
            if company_doc and company_doc[0].get("date_of_establishment"):
                est = frappe.utils.getdate(company_doc[0]["date_of_establishment"])
                years = today_dt.year - est.year
                if years > 0:
                    this_year_co = frappe.utils.getdate(
                        str(today_dt.year) + "-" + str(est.month).zfill(2) + "-" + str(est.day).zfill(2)
                    )
                    diff = (this_year_co - today_dt).days
                    if 0 <= diff <= window_days:
                        yr_word = str(years) + (" year" if years == 1 else " years")
                        if diff == 0:
                            msg = company_doc[0]["name"] + " turns " + yr_word + " old today! 🏢"
                        elif diff == 1:
                            msg = company_doc[0]["name"] + "'s " + yr_word + " anniversary is tomorrow 🏢"
                        else:
                            msg = company_doc[0]["name"] + "'s " + yr_word + " anniversary is in " + str(diff) + " days 🏢"
                        notifications.append({
                            "type":    "company",
                            "subject": msg,
                            "date":    str(this_year_co),
                            "years":   years
                        })
        except Exception:
            pass

        # ── 12. Build response ────────────────────────────────
        frappe.response["message"] = {
            "employee": {
                "employee_id":   emp_id,
                "employee_name": emp["employee_name"],
                "designation":   emp.get("designation") or "—",
                "department":    emp.get("department")  or "—"
            },
            "attendance": {
                "today_status":  today_status,
                "month_present": month_present,
                "records":       att_records
            },
            "leaves":        leave_balances,
            "expenses":      expenses,
            "timesheets":    timesheets,
            "payslips":      payslips,
            "holidays":      holidays,
            "notifications": notifications
        }
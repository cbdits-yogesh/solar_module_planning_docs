'''
Reference Document Type: Employee OT
DocType Event: Before Save
'''

CUTOFF_HOUR = 19  # 07:00 PM
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- Fieldnames on Employee OT ---
DATE_FIELD = "date"
IN_TIME_FIELD = "in_time"     # Datetime
OUT_TIME_FIELD = "out_time"   # Datetime
EMPLOYEE_FIELD = "emp_id"
SALARY_LIMIT = 40000
EMPLOYEE_NAME_FIELD = "emp_name"
OT_HOURS_FIELD = "over_time_hours"
# ----------------------------------


# ===========================================================
# MANDATORY FIELD CHECKS
# ===========================================================
if not doc.get(DATE_FIELD):
    frappe.throw(_("Please set the Date before saving."))

if not doc.get(EMPLOYEE_FIELD):
    frappe.throw(_("Employee (Emp. ID) is mandatory."))

employee = doc.get(EMPLOYEE_FIELD)
employee_label = doc.get(EMPLOYEE_NAME_FIELD) or employee
ot_date = frappe.utils.getdate(doc.get(DATE_FIELD))
weekday = WEEKDAY_NAMES[ot_date.weekday()]   # 0=Monday ... 6=Sunday
is_sunday = (weekday == "Sunday")
# ===========================================================
# DUPLICATE ENTRY CHECK (one OT entry per employee per date)
# ===========================================================
duplicate_exists = frappe.db.exists(
     "Employee OT",
     {
         EMPLOYEE_FIELD: employee,
         DATE_FIELD: ot_date,
         "name": ["!=", doc.name],
     }
 )
if duplicate_exists:
 frappe.throw(_(
     f"An OT entry already exists for <b>{employee_label}</b> on <b>{ot_date}</b>. "
 ))

in_time_val = doc.get(IN_TIME_FIELD)
out_time_val = doc.get(OUT_TIME_FIELD)

# Fetch employee data ONCE (used by day/salary rules + OT amount calc)
emp_data = frappe.db.get_value(
    "Employee", employee, ["status", "ctc", "employee_name"], as_dict=True
)

if not emp_data:
    frappe.throw(_(f"Employee record for <b>{employee_label}</b> not found."))

emp_status = emp_data.status
emp_ctc = emp_data.ctc
emp_name = emp_data.employee_name

# ===========================================================
# STEP 1: DAY CONDITION (Sunday bypass / Mon-Sat cutoff time)
# ===========================================================
if is_sunday:
    # Sunday: all employees allowed, no cutoff time / salary / status checks
    pass
else:
    if in_time_val:
        in_time_dt = frappe.utils.get_datetime(in_time_val)
        if in_time_dt.hour < CUTOFF_HOUR:
            time_str = f"{in_time_dt.hour:02d}:{in_time_dt.minute:02d}"
            frappe.throw(
                _(f"Overtime on {weekday} is only applicable after 07:00 PM. "
                  f"In Time entered: {time_str}")
            )

    # ===========================================================
    # STEP 2: SALARY / STATUS CONDITION
    # ===========================================================
    if emp_status != "Active":
        frappe.throw(_(f"Employee {emp_name} is not Active. OT cannot be filed."))

    if emp_ctc and emp_ctc > SALARY_LIMIT:
        frappe.throw(_(f"Employee {emp_name} is not eligible for Overtime on {weekday} "))

# ===========================================================
# STEP 3: CHECKOUT TIME CONDITION
# ===========================================================

# Date sanity: In Time date must exactly match OT Date
if in_time_val:
    in_time_dt = frappe.utils.get_datetime(in_time_val)
    if frappe.utils.getdate(in_time_dt) != ot_date:
        frappe.throw(_("IN Time: Date Mismatch"))

# Date sanity: Out Time date must match OT Date
if out_time_val:
    out_time_dt = frappe.utils.get_datetime(out_time_val)
    if frappe.utils.getdate(out_time_dt) != ot_date:
        frappe.throw(_("Out Time: Date Mismatch"))

# Employee must have an actual OUT checkin logged for the OT date
# (skipped on Sunday — all employees allowed to file OT without a checkout)
if in_time_val and not is_sunday:
    checkout_exists = frappe.db.exists(
        "Employee Checkin",
        {
            "employee": employee,
            "log_type": "OUT",
            "time": ["between", [f"{ot_date} 00:00:00", f"{ot_date} 23:59:59"]]
        }
    )
    if not checkout_exists:
        frappe.throw(_(
            f"Cannot proceed. Employee <b>{employee_label}</b> has not checked out "
            f"(<span style='color:red; font-weight:bold;'>no OUT entry</span> in Employee Checkin) "
            f"for the OT date <b>{ot_date}</b>."
        ))

# Out Time must be after In Time, then compute OT hours/amount
if in_time_val and out_time_val:
    in_time_dt = frappe.utils.get_datetime(in_time_val)
    out_time_dt = frappe.utils.get_datetime(out_time_val)

    if out_time_dt <= in_time_dt:
        frappe.throw(_("Out Time must be after In Time."))

    diff = out_time_dt - in_time_dt
    total_seconds = int(diff.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    doc.over_time_hours = f"{hours:02}:{minutes:02}:{seconds:02}"

    if not emp_ctc:
        frappe.throw(_(f"CTC is not set for employee {emp_name}. Cannot calculate OT amount."))

    # NOTE: avoid tuple-unpacking assignment (e.g. "a, b = x, y")
    # RestrictedPython's safe_exec sandbox does not define _unpack_sequence_
    # for it, and it throws: NameError: name '_unpack_sequence_' is not defined
    date_value = frappe.utils.getdate(doc.date)

    year = date_value.year
    month = date_value.month
   
    if month == 2:
        total_days = 29 if (year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)) else 28
    elif month in (4, 6, 9, 11):
        total_days = 30
    else:
        total_days = 31

    daily_salary = emp_ctc / total_days
    
    hourly_rate = daily_salary / 8.5
   
    actual_ot_hours = total_seconds / 3600
    
    doc.over_time_hours = round(actual_ot_hours, 2)
    doc.ot_amount = round(hourly_rate * actual_ot_hours)
    
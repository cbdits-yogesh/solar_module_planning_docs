# Server Script Type: API
# API Method: get_ot_dashboard_data

start_date = frappe.form_dict.get('start_date')
end_date = frappe.form_dict.get('end_date')
department = frappe.form_dict.get('department')
employee = frappe.form_dict.get('employee')
# Fetching directly from DocType Department
departments_list = frappe.get_all("Department", fields=["name", "department_name"], order_by="name asc")
employee_filters = {}

employees_list = frappe.get_all(
    "Employee",
    filters=employee_filters,
    fields=["name", "employee_name"],
    order_by="employee_name asc"
)
# Build WHERE conditions dynamically
conditions_list = []
filters = {}

# 1. Add Date Filters only if explicitly provided
if start_date and end_date:
    conditions_list.append("ot.date BETWEEN %(start_date)s AND %(end_date)s")
    filters["start_date"] = start_date
    filters["end_date"] = end_date
elif start_date:
    conditions_list.append("ot.date >= %(start_date)s")
    filters["start_date"] = start_date
elif end_date:
    conditions_list.append("ot.date <= %(end_date)s")
    filters["end_date"] = end_date

# 2. Add Department Filter
if department:
    conditions_list.append("emp.department = %(department)s")
    filters["department"] = department
# 3. Add Employee Filter
if employee:
    conditions_list.append("ot.emp_id = %(employee)s")
    filters["employee"] = employee    

# Construct final WHERE clause
if conditions_list:
    conditions = "WHERE " + " AND ".join(conditions_list)
else:
    conditions = ""

# -------------------------------------------------------------
# 1. KPI METRICS CALCULATIONS
# -------------------------------------------------------------
kpi_query = f"""
    SELECT 
        COALESCE(SUM(CAST(ot.over_time_hours AS DECIMAL(10,2))), 0) AS total_ot_hours,
        COALESCE(SUM(CAST(ot.ot_amount AS DECIMAL(10,2))), 0) AS total_payable,
        COUNT(ot.emp_id) AS total_employees,
        CASE 
            WHEN COUNT(DISTINCT ot.emp_id) > 0 
            THEN COALESCE(SUM(CAST(ot.over_time_hours AS DECIMAL(10,2))), 0) / COUNT(DISTINCT ot.emp_id) 
            ELSE 0 
        END AS avg_ot_per_employee
    FROM `tabEmployee OT` ot
    LEFT JOIN `tabEmployee` emp ON ot.emp_id = emp.name
    {conditions}
"""
kpi_data = frappe.db.sql(kpi_query, filters, as_dict=True)[0]

# -------------------------------------------------------------
# 2. CHART METRICS (OT Hours by Department)
# -------------------------------------------------------------
chart_query = f"""
    SELECT 
        COALESCE(emp.department, 'Unassigned') AS department,
        SUM(CAST(ot.over_time_hours AS DECIMAL(10,2))) AS ot_hours
    FROM `tabEmployee OT` ot
    LEFT JOIN `tabEmployee` emp ON ot.emp_id = emp.name
    {conditions}
    GROUP BY emp.department
    ORDER BY ot_hours DESC
"""
chart_data = frappe.db.sql(chart_query, filters, as_dict=True)

# -------------------------------------------------------------
# 3. DETAILED TABLE REPORT
# -------------------------------------------------------------
table_query = f"""
    SELECT 
        ot.emp_id,
        ot.emp_name AS name,
        ot.workflow_state AS status,
        COALESCE(emp.department, '-') AS dept,
        ot.date,
        TIME_FORMAT(ot.in_time, '%%H:%%i') AS punch_in,
        TIME_FORMAT(ot.out_time, '%%H:%%i') AS punch_out,
        COALESCE(att.working_hours, 0) AS reg_hrs,
        COALESCE(CAST(ot.over_time_hours AS DECIMAL(10,2)), 0) AS ot_hours,
        COALESCE(CAST(ot.ot_amount AS DECIMAL(10,2)), 0) AS payable,
        CASE 
            WHEN CAST(ot.over_time_hours AS DECIMAL(10,2)) > 0 
            THEN COALESCE(CAST(ot.ot_amount AS DECIMAL(10,2)), 0) / CAST(ot.over_time_hours AS DECIMAL(10,2))
            ELSE 0 
        END AS rate,
        ot.docstatus
    FROM `tabEmployee OT` ot
    LEFT JOIN `tabEmployee` emp ON ot.emp_id = emp.name
    LEFT JOIN `tabAttendance` att ON ot.emp_id = att.employee AND ot.date = att.attendance_date
    {conditions}
    ORDER BY ot.creation DESC,ot.date DESC
    LIMIT 100
"""
table_data = frappe.db.sql(table_query, filters, as_dict=True)

for row in table_data:
    # row['status'] = "Approved" if row['docstatus'] == 1 else "Pending"
    row['rate'] = f"₹{row['rate']:.2f}/hr"
    row['payable'] = f"₹{row['payable']:,.2f}"

# Return structured response
frappe.response["message"] = {
    "departments": departments_list, 
    "employees": employees_list,
    "kpis": {
        "total_ot_hours": f"{round(kpi_data.total_ot_hours, 1)} hrs",
        "total_payable": f"₹{kpi_data.total_payable:,.2f}",
        "total_employees": kpi_data.total_employees,
        "avg_ot_per_employee": f"{round(kpi_data.avg_ot_per_employee, 1)} hrs"
    },
    "chart": {
        "labels": [d.department for d in chart_data],
        "values": [d.ot_hours for d in chart_data]
    },
    "logs": table_data
}
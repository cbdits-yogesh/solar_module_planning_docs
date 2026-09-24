month = frappe.form_dict.get('month')  # "2026-08"
department = frappe.form_dict.get('department')

if not month:
    frappe.throw(_("Month is required."))

month_parts = month.split('-')
year = month_parts[0]
mon = month_parts[1]
# Fetch Department list (for populating the filter dropdown)
departments_list = frappe.get_all("Department", fields=["name", "department_name"], order_by="name asc")

conditions_list = ["YEAR(ot.date) = %(year)s", "MONTH(ot.date) = %(mon)s"]
filters = {"year": year, "mon": mon}
conditions_list.append("ot.workflow_state = 'Approved'")

if department:
    conditions_list.append("emp.department = %(department)s")
    filters["department"] = department
    

conditions = "WHERE " + " AND ".join(conditions_list)

query = f"""
    SELECT
        ot.emp_id,
        ot.emp_name,
        ot.workflow_state AS status,
        COALESCE(emp.department, '-') AS department,
        COUNT(*) AS total_days,
        SUM(CAST(ot.over_time_hours AS DECIMAL(10,2))) AS total_ot_hours,
        SUM(CAST(ot.ot_amount AS DECIMAL(10,2))) AS total_payable,
        CASE
            WHEN SUM(CAST(ot.over_time_hours AS DECIMAL(10,2))) > 0
            THEN SUM(CAST(ot.ot_amount AS DECIMAL(10,2))) / SUM(CAST(ot.over_time_hours AS DECIMAL(10,2)))
            ELSE 0
        END AS avg_rate
    FROM `tabEmployee OT` ot
    LEFT JOIN `tabEmployee` emp ON ot.emp_id = emp.name
    {conditions}
    GROUP BY ot.emp_id
    ORDER BY total_payable DESC
"""

data = frappe.db.sql(query, filters, as_dict=True)

frappe.response["message"] = {
    "departments": departments_list,
    "rows":data
    }
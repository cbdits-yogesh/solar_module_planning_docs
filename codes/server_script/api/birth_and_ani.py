my_date = frappe.db.get_all("Employee", filters={"status": "Active"}, fields=["date_of_birth", "date_of_joining", "employee_name"])

emp_brt_ani = []
for emp in my_date:
    emp_brt_ani.append({
        "emp_name" : emp.employee_name,
        "birth" : emp.date_of_birth,
        "anniversary" : emp.date_of_joining
    })

frappe.response['data'] = emp_brt_ani

# Fetch all active employees with their name, birth date, and joining date
# employees = frappe.db.get_all(
#     "Employee",
#     filters={"status": "Active"},
#     fields=["employee_name", "date_of_birth", "date_of_joining"]
# )

# # Prepare the response
# emp_brt_ani = []

# for emp in employees:
#     emp_brt_ani.append({
#         "Name": emp.employee_name,
#         "Birth Date": emp.date_of_birth,
#         "Anniversary": emp.date_of_joining
#     })

# frappe.response['data'] = emp_brt_ani

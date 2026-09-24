# Extract the employee ID passed from the frontend
emp_id = frappe.form_dict.get('emp_id')

# Mock Database
mock_db = {
    "emp001": {
        "id": "emp001",
        "name": "Prachi Shreyans Upadhyay",
        "department": "Information Technology",
        "designation": "Software Developer",
        "branch": "Dombivli Head Office",
        "attendance": [
            {"date": "01 Apr 2026", "status": "P"},  
            {"date": "02 Apr 2026", "status": "A"},  
            {"date": "03 Apr 2026", "status": "PL"}, 
            {"date": "04 Apr 2026", "status": "HD"}, 
            {"date": "05 Apr 2026", "status": "WO"}  
        ]
    }
}

# Ensure an ID was actually sent
if not emp_id:
    frappe.response['http_status_code'] = 400
    frappe.response['message'] = {"error": "Missing emp_id parameter"}

else:
    employee = mock_db.get(emp_id)
    
    if employee:
        # Return the data successfully
        frappe.response['message'] = employee
    else:
        # Return an error if employee doesn't exist
        frappe.response['http_status_code'] = 404
        frappe.response['message'] = {"error": "Employee not found"}
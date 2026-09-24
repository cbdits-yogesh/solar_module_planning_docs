'''
Reference Document Type: Employee Checkin
DocType Event: Before Save
'''

if doc.log_type == "IN" and doc.employee:
    default_shift = frappe.db.get_value("Employee", doc.employee, "default_shift")
    if default_shift:
        shift = frappe.db.get_value(
            "Shift Type",
            default_shift,
            ["start_time", "late_entry_grace_period"],
            as_dict=True
        )
        if shift and shift.start_time:
            # Combine date of checkin + shift start time
            shift_start_datetime = frappe.utils.get_datetime(str(doc.time.date()) + " " + str(shift.start_time))
            
            # Add grace period (in minutes)
            grace_limit = frappe.utils.add_to_date(shift_start_datetime, minutes=(shift.late_entry_grace_period or 0))
            
            # Compare and set late flag
            if doc.time > grace_limit:
                doc.late_entry = 1
            else:
                doc.late_entry = 0

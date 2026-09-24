'''
Reference Document Type: Leave Application
DocType Event: Before Save
'''

if doc.leave_type == "Casual Leave" and doc.docstatus != 2:

    month_start = frappe.utils.get_first_day(doc.from_date)
    month_end = frappe.utils.get_last_day(doc.from_date)

    result = frappe.db.sql("""
        SELECT IFNULL(SUM(total_leave_days), 0) as total
        FROM `tabLeave Application`
        WHERE employee = %s
          AND leave_type = 'Casual Leave'
          AND docstatus != 2
          AND name != %s
          AND (
              from_date BETWEEN %s AND %s
              OR to_date BETWEEN %s AND %s
              OR (from_date <= %s AND to_date >= %s)
          )
    """, (
        doc.employee,
        doc.name,
        month_start, month_end,
        month_start, month_end,
        month_start, month_end
    ), as_dict=True)

    already_used = frappe.utils.flt(result[0].total) if result else 0
    applying_now = frappe.utils.flt(doc.total_leave_days)

    if already_used + applying_now > 4:
        remaining = frappe.utils.flt(4 - already_used)
        if remaining < 0:
            remaining = 0

        msg = "Casual Leave limit exceeded! Used: " + str(already_used) + " day(s) this month. Remaining allowed: " + str(remaining) + " day(s). Max allowed: 4 days/month."
        frappe.throw(msg)
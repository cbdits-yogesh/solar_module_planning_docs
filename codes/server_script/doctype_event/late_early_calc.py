'''
Reference Document Type: Salary SLip
DocType Event: Before Validate
'''

if doc.employee and doc.start_date and doc.end_date:
    result = frappe.db.sql("""
        SELECT
            COALESCE(SUM(late_entry_minutes), 0) AS total_late,
            COALESCE(SUM(early_exit_minutes), 0) AS total_early
        FROM `tabAttendance`
        WHERE
            employee = %s
            AND attendance_date BETWEEN %s AND %s
            AND docstatus = 1
    """, (doc.employee, doc.start_date, doc.end_date), as_dict=True)

    if result:
        doc.total_late_minute = int(result[0].total_late)
        doc.total_early_minute = int(result[0].total_early)
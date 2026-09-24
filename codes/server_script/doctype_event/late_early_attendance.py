'''
Reference Document Type: Attendance
DocType Event: Before Save
'''

# Skip unwanted statuses
if doc.status in ("On Leave", "Absent", "Half Day"):
    doc.late_entry_minutes = 0
    doc.early_exit_minutes = 0

elif doc.shift and doc.attendance_date:
    shift = frappe.db.get_value(
        "Shift Type",
        doc.shift,
        ["start_time", "end_time", "late_entry_grace_period", "early_exit_grace_period"],
        as_dict=True,
    )

    doc.late_entry_minutes = 0
    doc.early_exit_minutes = 0

    if shift and shift.start_time is not None and shift.end_time is not None:
        attendance_date = frappe.utils.getdate(doc.attendance_date)

        shift_start_dt = frappe.utils.add_to_date(
            attendance_date,
            hours=shift.start_time.seconds // 3600,
            minutes=(shift.start_time.seconds % 3600) // 60,
            seconds=shift.start_time.seconds % 60,
            as_datetime=True,
        )

        shift_end_dt = frappe.utils.add_to_date(
            attendance_date,
            hours=shift.end_time.seconds // 3600,
            minutes=(shift.end_time.seconds % 3600) // 60,
            seconds=shift.end_time.seconds % 60,
            as_datetime=True,
        )

        if shift.end_time < shift.start_time:
            shift_end_dt = frappe.utils.add_to_date(shift_end_dt, days=1, as_datetime=True)

        late_grace = int(shift.late_entry_grace_period or 0)
        early_grace = int(shift.early_exit_grace_period or 0)

        if doc.in_time:
            late_cutoff = frappe.utils.add_to_date(shift_start_dt, minutes=late_grace, as_datetime=True)
            if doc.in_time > late_cutoff:
                doc.late_entry_minutes = int((doc.in_time - late_cutoff).total_seconds() // 60)

        if doc.out_time:
            out_time = doc.out_time

            if shift.end_time < shift.start_time and out_time < shift_start_dt:
                out_time = frappe.utils.add_to_date(out_time, days=1, as_datetime=True)

            early_cutoff = frappe.utils.add_to_date(shift_end_dt, minutes=-early_grace, as_datetime=True)
            if out_time < early_cutoff:
                doc.early_exit_minutes = int((early_cutoff - out_time).total_seconds() // 60)
else:
    doc.late_entry_minutes = 0
    doc.early_exit_minutes = 0


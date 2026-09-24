'''
Event Frequency: Cron
Cron Format: 0 22 * * *

*  *  *  *  *
┬  ┬  ┬  ┬  ┬
│  │  │  │  │
│  │  │  │  └ day of week (0 - 6) (0 is Sunday)
│  │  │  └───── month (1 - 12)
│  │  └────────── day of month (1 - 31)
│  └─────────────── hour (0 - 23)
└──────────────────── minute (0 - 59)

---

* - Any value
/ - Step values
'''

employees = frappe.get_all("Employee",
        filters={"custom_auto_attendance_enable": 1, "status": "Active"},
        fields=["name"]
    )

for emp in employees:
        # Check if attendance already marked
        existing = frappe.db.exists("Attendance", {
            "employee": emp.name,
            "attendance_date": frappe.utils.today()
        })

        if not existing:
            attendance = frappe.get_doc({
                "doctype": "Attendance",
                "employee": emp.name,
                "attendance_date": frappe.utils.today(),
                "status": "Present",
                "docstatus": 1  # Submit the document
            })
            attendance.insert(ignore_permissions=True)
            attendance.submit()
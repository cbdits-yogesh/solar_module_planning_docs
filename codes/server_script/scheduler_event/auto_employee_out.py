'''
Event Frequency: Cron
Cron Format: */10 * * * *

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

auto_checkout = frappe.db.get_single_value("HRMS Advance Setting", "auto_checkout")
checkout_time = frappe.db.get_single_value("HRMS Advance Setting", "checkout_time")

if auto_checkout and checkout_time:

    today = frappe.utils.nowdate()
    now = frappe.utils.now_datetime()

    checkout_time_str = str(checkout_time)
    auto_out_datetime = frappe.utils.get_datetime(today + " " + checkout_time_str)

    # Calculate difference in seconds between now and checkout_time
    diff = now - auto_out_datetime
    diff_seconds = diff.days * 86400 + diff.seconds

    # Only process if checkout_time is within the past 10 minutes (0 to 600 seconds ago)
    if diff_seconds >= 0 and diff_seconds < 600:

        employees_today = frappe.db.sql("""
            SELECT DISTINCT employee
            FROM `tabEmployee Checkin`
            WHERE DATE(time) = %s
        """, today, as_dict=True)

        for row in employees_today:
            emp = row.employee

            checkins = frappe.db.sql("""
                SELECT name, log_type, time
                FROM `tabEmployee Checkin`
                WHERE employee = %s
                  AND DATE(time) = %s
                ORDER BY time ASC
            """, (emp, today), as_dict=True)

            if not checkins:
                continue

            last_checkin = checkins[-1]

            if last_checkin.log_type == "IN" and last_checkin.time < auto_out_datetime:

                already_exists = frappe.db.exists("Employee Checkin", {
                    "employee": emp,
                    "log_type": "OUT",
                    "time": auto_out_datetime,
                    "device_id": "AUTO_SYSTEM"
                })

                if not already_exists:
                    doc = frappe.get_doc({
                        "doctype": "Employee Checkin",
                        "employee": emp,
                        "log_type": "OUT",
                        "time": auto_out_datetime,
                        "latitude": "21.24310",
                        "longitude": "81.65210",
                        "custom_area_name": "House No. 84, Anand Nagar, Telibandha, Raipur, Chhattisgarh, 492001",
                        "device_id": "AUTO_SYSTEM"
                    })
                    doc.insert(ignore_permissions=True)
                    frappe.db.commit()
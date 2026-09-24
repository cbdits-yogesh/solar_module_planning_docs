'''
Reference Document Type: Employee Checkin
DocType Event: After Insert
'''

if doc.latitude and doc.longitude and doc.device_id != "AUTO_SYSTEM":
    GOOGLE_API_KEY = "AIzaSyAll1SygpBBDDQBXTFsh3vQDp19gYjW0jg"  # Store key in site_config.json
    url = (
        f"https://maps.googleapis.com/maps/api/geocode/json"
        f"?latlng={doc.latitude},{doc.longitude}&key={GOOGLE_API_KEY}"
    )
    try:
        resp = frappe.make_get_request(url)
        if resp and resp.get("status") == "OK" and resp.get("results"):
            formatted_address = resp["results"][0]["formatted_address"]
            frappe.db.set_value("Employee Checkin", doc.name, "custom_area_name", formatted_address)
        else:
            frappe.log_error(
                f"Google Geocoding failed: {resp.get('status')} - {resp.get('error_message', '')}",
                "Location Err"
            )
    except Exception as e:
        frappe.log_error(str(e), "Location Err")
        frappe.response["message"] = str(e)
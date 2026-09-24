'''
Reference Document Type: Lead
DocType Event: After Insert
'''

CHANNEL_ID = "Raven-lead-notification"

lead_name = doc.name
lead_url = frappe.utils.get_url_to_form("Lead", doc.name)

first_name = doc.get("first_name") or "—"
email_id = doc.get("email_id") or "—"
source = doc.get("source") or "—"
mobile_no = doc.get("mobile_no") or "—"
surveyed_by = doc.get("surveyed_by") or "—"
description = doc.get("description") or "—"
solar_capacity = doc.get("solar_capacity") or "—"
custom_address = doc.get("custom_address") or "—"
state = doc.get("state") or "—"
country = doc.get("country") or "—"
city = doc.get("city") or "—"
creation_date = doc.get("creation_date") or str(doc.get("creation") or "—")
stage_status = doc.get("stage_status") or "—"
created_by = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner

message_text = """
<div style="font-family:Arial,Helvetica,sans-serif;max-width:680px;margin:auto;background:#fef9f0;padding:18px;border-radius:14px;border:1px solid #e8d5a3;">

  <div style="background:linear-gradient(135deg,#b5711c,#d4a96a);padding:18px 20px;border-radius:12px;color:#fff;">
    <div style="font-size:12px;letter-spacing:1px;text-transform:uppercase;opacity:0.9;">Lead Notification</div>
    <div style="font-size:22px;font-weight:700;margin-top:4px;">📬 New Lead Created</div>
  </div>

  <div style="padding:20px 6px 6px;color:#1f2937;">
    <p style="margin:0 0 14px;font-size:15px;line-height:1.7;">
      A new lead has been created by <strong>""" + str(created_by) + """</strong> in the system.
    </p>

    <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #e8d5a3;border-radius:12px;overflow:hidden;font-size:14px;">
      <tr style="background:#fef0d0;">
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;width:40%;font-weight:600;">👤 First Name</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(first_name) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">✉️ Email ID</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(email_id) + """</td>
      </tr>
      <tr style="background:#fef0d0;">
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">📡 Reference From</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(source) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">📱 Mobile No</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(mobile_no) + """</td>
      </tr>
      <tr style="background:#fef0d0;">
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">💼 Surveyed By</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(surveyed_by) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">📝 Description</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(description) + """</td>
      </tr>
      <tr style="background:#fef0d0;">
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">🔆 Solar Capacity</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(solar_capacity) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">🏠 Address</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(custom_address) + """</td>
      </tr>
      <tr style="background:#fef0d0;">
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">🗺️ State</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(state) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">🌍 Country</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(country) + """</td>
      </tr>
      <tr style="background:#fef0d0;">
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">🏙️ City</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(city) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#8a6a3a;font-weight:600;">📅 Creation Date</td>
        <td style="padding:12px 14px;border-bottom:1px solid #f0e4c8;color:#111827;">""" + str(creation_date) + """</td>
      </tr>
      <tr style="background:#fef0d0;">
        <td style="padding:12px 14px;color:#8a6a3a;font-weight:600;">📌 Stage Status</td>
        <td style="padding:12px 14px;color:#111827;">""" + str(stage_status) + """</td>
      </tr>
    </table>

    <div style="margin-top:16px;text-align:center;">
      <a href='""" + str(lead_url) + """'
         style="display:inline-block;background:#b5711c;color:#fff;text-decoration:none;padding:12px 28px;border-radius:10px;font-size:14px;font-weight:700;">
        👁️ View Lead
      </a>
    </div>

  </div>
</div>
"""

frappe.get_doc({
    "doctype": "Raven Message",
    "channel_id": CHANNEL_ID,
    "text": message_text,
    "message_type": "Text",
    "is_bot_message": 1
}).insert(ignore_permissions=True)
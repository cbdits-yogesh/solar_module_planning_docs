'''
Reference Document Type: Proposal
DocType Event: After Insert
'''

CHANNEL_ID = "Raven-sitesurvey-notification"

lead_url = frappe.utils.get_url_to_form(doc.doctype, doc.name)
created_by = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner

quotation_to      = doc.get("quotation_to") or "—"
transaction_date  = doc.get("transaction_date") or "—"
manager           = doc.get("manager") or "—"
site_survey       = doc.get("site_survey") or "—"
party_name        = doc.get("party_name") or "—"
valid_till        = doc.get("valid_till") or "—"
plant_category    = doc.get("plant_category") or "—"
solar_capacity    = doc.get("solar_capacity") or "—"
customer_name     = doc.get("customer_name") or "—"
proposal_id       = doc.get("proposal_id") or "—"
solar_system_type = doc.get("solar_system_type") or "—"
site_type         = doc.get("site_type") or "—"
type_of_mounting  = doc.get("type_of_mounting") or "—"
proposal_type     = doc.get("proposal_type") or "—"

message_text = """
<div style="font-family:Arial,Helvetica,sans-serif;max-width:680px;margin:auto;background:#f0f7ff;padding:18px;border-radius:14px;border:1px solid #bfdbfe;">

  <div style="background:linear-gradient(135deg,#1d4ed8,#0369a1);padding:18px 20px;border-radius:12px;color:#fff;">
    <div style="font-size:12px;letter-spacing:1px;text-transform:uppercase;opacity:0.85;">Site Survey Notification</div>
    <div style="font-size:22px;font-weight:700;margin-top:4px;">🏗️ New Site Survey Created</div>
    <div style="font-size:13px;margin-top:6px;opacity:0.85;">Created by: <strong>""" + str(created_by) + """</strong></div>
  </div>

  <div style="padding:20px 4px 6px;color:#1f2937;">

    <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #bfdbfe;border-radius:12px;overflow:hidden;font-size:14px;">
      <tr style="background:#eff6ff;">
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;width:42%;font-weight:600;">📋 Quotation To</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(quotation_to) + """</td>
      </tr>
      <tr>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">📅 Transaction Date</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(transaction_date) + """</td>
      </tr>
      <tr style="background:#eff6ff;">
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">👨‍💼 Manager</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(manager) + """</td>
      </tr>
      <tr>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">🔍 Site Survey</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(site_survey) + """</td>
      </tr>
      <tr style="background:#eff6ff;">
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">🏢 Party Name</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(party_name) + """</td>
      </tr>
      <tr>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">📆 Valid Till</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(valid_till) + """</td>
      </tr>
      <tr style="background:#eff6ff;">
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">🏭 Plant Category</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(plant_category) + """</td>
      </tr>
      <tr>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">🔆 Solar Capacity</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(solar_capacity) + """</td>
      </tr>
      <tr style="background:#eff6ff;">
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">👤 Customer Name</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(customer_name) + """</td>
      </tr>
      <tr>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">🆔 Proposal ID</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(proposal_id) + """</td>
      </tr>
      <tr style="background:#eff6ff;">
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">☀️ Solar System Type</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(solar_system_type) + """</td>
      </tr>
      <tr>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">🏠 Site Type</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(site_type) + """</td>
      </tr>
      <tr style="background:#eff6ff;">
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#1e40af;font-weight:600;">🔩 Type of Mounting</td>
        <td style="padding:11px 14px;border-bottom:1px solid #dbeafe;color:#111827;">""" + str(type_of_mounting) + """</td>
      </tr>
      <tr>
        <td style="padding:11px 14px;color:#1e40af;font-weight:600;">📁 Proposal Type</td>
        <td style="padding:11px 14px;color:#111827;">""" + str(proposal_type) + """</td>
      </tr>
    </table>

    <div style="margin-top:16px;text-align:center;">
      <a href='""" + str(lead_url) + """'
         style="display:inline-block;background:#1d4ed8;color:#fff;text-decoration:none;padding:12px 28px;border-radius:10px;font-size:14px;font-weight:700;">
        👁️ View Site Survey
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
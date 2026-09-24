'''
Reference Document Type: Payment Entry
DocType Event: After Submit
'''

# CHANNEL_ID = "Raven-payment-notification"

# payment_name = doc.name
# payment_amount = doc.get("paid_amount") or 0
# party_name = doc.get("party_name") or doc.get("party") or "Unknown"
# posting_date = doc.get("posting_date") or "—"
# mode_of_payment = doc.get("mode_of_payment") or "—"
# payment_type = doc.get("payment_type") or "—"
# reference_no = doc.get("reference_no") or "—"
# reference_date = doc.get("reference_date") or "—"
# project = doc.get("project") or "—"

# message_text = (
#     "<b>New Payment Created</b><br><br>"
#     "<b>Payment No:</b> " + str(payment_name) + "<br>"
#     "<b>Party:</b> " + str(party_name) + "<br>"
#     "<b>Posting Date:</b> " + str(posting_date) + "<br>"
#     "<b>Mode Of Payment:</b> " + str(mode_of_payment) + "<br>"
#     "<b>Payment Type:</b> " + str(payment_type) + "<br>"
#     "<b>Reference No:</b> " + str(reference_no) + "<br>"
#     "<b>Reference Date:</b> " + str(reference_date) + "<br>"
#     "<b>Project:</b> " + str(project) + "<br>"
#     "<b>Amount:</b> " + str(payment_amount)
# )

# frappe.get_doc({
#     "doctype": "Raven Message",
#     "channel_id": CHANNEL_ID,
#     "text": message_text,
#     "message_type": "Text",
#     "is_bot_message": 1
# }).insert(ignore_permissions=True)



















CHANNEL_ID = "Raven-payment-notification"

payment_name = doc.name
payment_amount = doc.get("paid_amount") or 0
party_name = doc.get("party_name") or doc.get("party") or "Unknown"
posting_date = doc.get("posting_date") or "—"
mode_of_payment = doc.get("mode_of_payment") or "—"
payment_type = doc.get("payment_type") or "—"
reference_no = doc.get("reference_no") or "—"
reference_date = doc.get("reference_date") or "—"
project = doc.get("project") or "—"

payment_url = frappe.utils.get_url_to_form(doc.doctype, doc.name)

message_text = """
<div style="font-family:Arial,Helvetica,sans-serif;max-width:680px;margin:auto;background:#f6f8fb;padding:18px;border-radius:14px;border:1px solid #e5e7eb;">
  <div style="background:linear-gradient(135deg,#2563eb,#0f766e);padding:18px 20px;border-radius:12px;color:#fff;">
    <div style="font-size:12px;letter-spacing:1px;text-transform:uppercase;opacity:0.9;">Payment Notification</div>
    <div style="font-size:22px;font-weight:700;margin-top:4px;">💰 New Payment Received</div>
  </div>

  <div style="padding:20px 6px 6px;color:#1f2937;">
    <p style="margin:0 0 14px;font-size:15px;line-height:1.7;">
      A new payment has been recorded in the system.
    </p>

    <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;font-size:14px;">
      <tr style="background:#f9fafb;">
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#6b7280;width:40%;font-weight:600;">Payment No.</td>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#111827;">""" + str(payment_name) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#6b7280;font-weight:600;">Party</td>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#111827;">""" + str(party_name) + """</td>
      </tr>
      <tr style="background:#f9fafb;">
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#6b7280;font-weight:600;">Posting Date</td>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#111827;">""" + str(posting_date) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#6b7280;font-weight:600;">Mode of Payment</td>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#111827;">""" + str(mode_of_payment) + """</td>
      </tr>
      <tr style="background:#f9fafb;">
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#6b7280;font-weight:600;">Payment Type</td>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#111827;">""" + str(payment_type) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#6b7280;font-weight:600;">Reference No.</td>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#111827;">""" + str(reference_no) + """</td>
      </tr>
      <tr style="background:#f9fafb;">
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#6b7280;font-weight:600;">Reference Date</td>
        <td style="padding:12px 14px;border-bottom:1px solid #eef2f7;color:#111827;">""" + str(reference_date) + """</td>
      </tr>
      <tr>
        <td style="padding:12px 14px;color:#6b7280;font-weight:600;">Project</td>
        <td style="padding:12px 14px;color:#111827;">""" + str(project) + """</td>
      </tr>
    </table>

    <div style="margin-top:14px;background:#ecfdf5;border:1px solid #bbf7d0;border-radius:12px;padding:14px 16px;color:#166534;font-size:16px;font-weight:700;">
      ₹ Amount Received: """ + str(payment_amount) + """
    </div>

    <div style="margin-top:16px;text-align:center;">
      <a href='""" + str(payment_url) + """'
         style="display:inline-block;background:#111827;color:#fff;text-decoration:none;padding:12px 18px;border-radius:10px;font-size:14px;font-weight:700;">
        View Payment
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
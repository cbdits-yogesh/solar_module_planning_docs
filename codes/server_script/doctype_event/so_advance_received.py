'''
Reference Document Type: Sales Order
DocType Event: Before Save
'''

# Check if proposal_sent checkbox is checked
if doc.adv_recv_msg_to_client:
    # If proposal_sent_date is not already set, set it to current date
    if not doc.adv_receive_msg_date:
        doc.adv_receive_msg_date = frappe.utils.today()
else:
    # If unchecked, clear the proposal_sent_date field
    doc.adv_receive_msg_date = None

'''
Reference Document Type: Site Survey
DocType Event: After Insert
'''

# Check if lead is linked
if doc.lead:
    # Update the Lead's status field to "Site Survey"
    frappe.db.set_value("Lead", doc.lead, "status", "Site Survey")
    # frappe.db.commit()
    
    # Optional: Show a message
    frappe.msgprint(f"Lead {doc.lead} status updated to Site Survey")

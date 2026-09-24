'''
Reference Document Type: Proposal
DocType Event: Before Insert
'''

if doc.site_survey:
    existing = frappe.db.exists(
        "Quotation",
        {
            "site_survey": doc.site_survey,
            "name": ["!=", doc.name or ""],
            "docstatus": ["!=", 2]
        }
    )

    if existing:
        message = f"Quotation <b>{existing}</b> already exists for Site Survey <b>{doc.site_survey}</b>. Please cancel it before creating a new quotation."
        
        frappe.throw(message, title="Duplicate Quotation for Site Survey")
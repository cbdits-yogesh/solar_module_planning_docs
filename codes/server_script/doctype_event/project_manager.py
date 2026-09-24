'''
Reference Document Type: Project
DocType Event: Before Save
'''

if not doc.custom_project_manager:
    sales_order = doc.get("sales_order")
    if sales_order:
        so_project_manager = frappe.db.get_value("Sales Order", sales_order, "project_manager")
        if so_project_manager:
            doc.custom_project_manager = so_project_manager

    if not doc.custom_project_manager:
        doc.custom_project_manager = doc.owner or frappe.session.user
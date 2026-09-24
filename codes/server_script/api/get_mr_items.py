mr_items = frappe.db.sql("""
    SELECT
        mri.parent AS parent,
        mri.item_code AS item_code,
        mri.qty AS qty
    FROM `tabMaterial Request Item` mri
    INNER JOIN `tabMaterial Request` mr
        ON mr.name = mri.parent
    WHERE mr.docstatus = 1
      AND mr.material_request_type = 'Material Transfer'
""", as_dict=True)

frappe.response['message'] = mr_items
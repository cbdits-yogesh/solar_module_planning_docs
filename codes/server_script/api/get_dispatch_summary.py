# Server Script Type: API
# API Method: get_dispatch_summary
# Allow Guest: No

if not frappe.session.user or frappe.session.user == "Guest":
	frappe.throw("Login required", frappe.PermissionError)
if "Store Manager" not in frappe.get_roles(frappe.session.user) and "System Manager" not in frappe.get_roles(frappe.session.user):
	frappe.throw("Insufficient role permission", frappe.PermissionError)

rows = frappe.db.sql("""
	SELECT dni.item_code, dni.item_name, so.name AS sales_order,
		dn.name AS delivery_note, dn.posting_date, SUM(dni.qty) AS qty
	FROM `tabDelivery Note Item` dni
	JOIN `tabDelivery Note` dn ON dn.name = dni.parent
	LEFT JOIN `tabSales Order` so ON so.name = dni.against_sales_order
	WHERE dn.docstatus = 1
	GROUP BY dni.item_code, dn.name
	ORDER BY dn.posting_date DESC
	LIMIT 100
""", as_dict=True)

frappe.response["message"] = rows
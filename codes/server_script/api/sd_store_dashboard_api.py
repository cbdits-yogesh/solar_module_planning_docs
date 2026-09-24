# ============================================================================
# SERVER SCRIPT: Store Dashboard API
# Type: API  |  Method: sd_store_dashboard_api
# ERPNext v15  |  Sadbhav Renewables Limited
#
# NOTE: Do NOT add "import frappe" / "import json" here.
# The Frappe Server Script sandbox already injects `frappe` (and other
# safe globals) automatically. Explicit `import` statements are blocked
# by safe_exec() and will raise "ImportError: __import__ not found".
#
# SANDBOX-SAFE RULES APPLIED IN THIS FILE:
#   - No tuple-unpacking assignment (e.g. "a, b = func()") -- RestrictedPython
#     blocks this with NameError: _unpack_sequence_ not defined.
#   - No "_leading_underscore" variable names -- blocked as invalid.
#   - No ".format()" string method -- blocked as an unsafe attribute.
#     String building uses plain "+" concatenation and str() instead.
#
# Usage from client:
#   frappe.call({ method: "sd_store_dashboard_api", args: { action: "...", ...filters } })
#
# All read-only. No data is created/modified. Uses real ERPNext doctypes:
#   Item, Bin, Warehouse, Purchase Receipt / Purchase Receipt Item,
#   Stock Entry / Stock Entry Detail, Delivery Note / Delivery Note Item,
#   Stock Ledger Entry
#
# CHANGELOG (this revision):
#   - Removed the "category" filter parameter entirely. It duplicated
#     item_group and mapped to the SAME SQL column, so selecting both
#     a Category and an Item Group at once produced an impossible
#     "AND" condition (silently zero rows = "filter not working").
#   - get_recent_issue() now includes multiple Stock Entry purposes
#     (Material Issue, Material Transfer, Send to Subcontractor)
#     instead of only "Material Issue" -- fixes empty "Recent Stock
#     Out" table when actual entries use a different purpose.
#   - get_stock_in_out_monthly() now zero-fills every month in the
#     requested range so months with zero activity (e.g. June) still
#     appear on the chart instead of being skipped entirely.
#   - get_stock_value_trend() same zero-fill fix applied.
# ============================================================================


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def flt(val):
	try:
		return round(float(val or 0), 2)
	except Exception:
		return 0


def get_filters_cond():
	# Read common filters passed from the dashboard (all optional).
	# NOTE: "category" filter removed -- it was a duplicate of item_group.
	item_group = frappe.form_dict.get("item_group")
	warehouse = frappe.form_dict.get("warehouse")

	conditions = ["1=1"]
	values = {}

	if item_group and item_group != "All":
		conditions.append("i.item_group = %(item_group)s")
		values["item_group"] = item_group

	if warehouse and warehouse != "All":
		conditions.append("b.warehouse = %(warehouse)s")
		values["warehouse"] = warehouse

	return " AND ".join(conditions), values


def get_month_range(months):
	# Build a zero-filled, chronological list of "YYYY-MM" periods for the
	# last `months` months (including the current month).
	#
	# NOTE: deliberately avoids frappe.utils.add_months() / date.strftime() --
	# both trigger a lazy import inside Frappe's Restricted Server Script
	# sandbox and raise "KeyError: '__import__'". Pure integer arithmetic
	# + string concatenation is used instead, matching the same safe style
	# as the rest of this script.
	today = frappe.utils.getdate()
	year = today.year
	month = today.month

	periods = []
	idx = int(months) - 1
	while idx >= 0:
		mm = month - idx
		yy = year
		while mm <= 0:
			mm = mm + 12
			yy = yy - 1
		mm_str = str(mm) if mm >= 10 else "0" + str(mm)
		periods.append(str(yy) + "-" + mm_str)
		idx = idx - 1
	return periods


def get_kpis():
	cv_result = get_filters_cond()
	cond = cv_result[0]
	values = cv_result[1]

	totals = frappe.db.sql(
		"SELECT COUNT(DISTINCT i.item_code) AS total_items, "
		"COALESCE(SUM(b.actual_qty), 0) AS total_qty, "
		"COALESCE(SUM(b.stock_value), 0) AS total_value "
		"FROM `tabItem` i "
		"LEFT JOIN `tabBin` b ON b.item_code = i.item_code "
		"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond,
		values, as_dict=True)[0]

	stock_status = get_stock_status_counts(cond, values)

	# FIX: Store Location (warehouse) filter now applied to pending GRN count too.
	warehouse = frappe.form_dict.get("warehouse")
	pgrn_values = {}
	pgrn_wh_cond = ""
	if warehouse and warehouse != "All":
		pgrn_values["warehouse"] = warehouse
		pgrn_wh_cond = " AND pri.warehouse = %(warehouse)s"

	pending_grn = frappe.db.sql(
		"SELECT COUNT(DISTINCT pr.name) AS cnt "
		"FROM `tabPurchase Receipt` pr "
		"INNER JOIN `tabPurchase Receipt Item` pri ON pri.parent = pr.name "
		"INNER JOIN `tabItem` i ON i.item_code = pri.item_code "
		"WHERE pr.docstatus = 1 "
		"AND pr.per_billed < 100 "
		"AND pr.status NOT IN ('Completed', 'Closed', 'Cancelled')"
		+ pgrn_wh_cond,
		pgrn_values, as_dict=True)[0]

	return {
		"total_items": totals.total_items or 0,
		"total_qty": flt(totals.total_qty),
		"total_value": flt(totals.total_value),
		"low_stock_items": stock_status.get("low_stock", 0),
		"out_of_stock_items": stock_status.get("out_of_stock", 0),
		"pending_grn": pending_grn.cnt or 0,
	}


def get_stock_status_counts(cond=None, values=None):
	if cond is None:
		cv_result = get_filters_cond()
		cond = cv_result[0]
		values = cv_result[1]

	rows = frappe.db.sql(
		"SELECT b.item_code, b.warehouse, b.actual_qty, "
		"COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0) AS reorder_level "
		"FROM `tabBin` b "
		"INNER JOIN `tabItem` i ON i.item_code = b.item_code "
		"LEFT JOIN `tabItem Reorder` ir ON ir.parent = i.item_code AND ir.warehouse = b.warehouse "
		"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond,
		values, as_dict=True)

	in_stock = 0
	low_stock = 0
	out_of_stock = 0
	for r in rows:
		qty = flt(r.actual_qty)
		reorder = flt(r.reorder_level)
		if qty <= 0:
			out_of_stock = out_of_stock + 1
		elif reorder and qty <= reorder:
			low_stock = low_stock + 1
		else:
			in_stock = in_stock + 1

	return {"in_stock": in_stock, "low_stock": low_stock, "out_of_stock": out_of_stock}


def get_stock_status():
	cv_result = get_filters_cond()
	cond = cv_result[0]
	values = cv_result[1]
	data = get_stock_status_counts(cond, values)

	rows = frappe.db.sql(
		"SELECT b.actual_qty, "
		"COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0) AS reorder_level "
		"FROM `tabBin` b "
		"INNER JOIN `tabItem` i ON i.item_code = b.item_code "
		"LEFT JOIN `tabItem Reorder` ir ON ir.parent = i.item_code AND ir.warehouse = b.warehouse "
		"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond,
		values, as_dict=True)

	qty_in = 0
	qty_low = 0
	qty_out = 0
	for r in rows:
		qty = flt(r.actual_qty)
		reorder = flt(r.reorder_level)
		if qty <= 0:
			qty_out = qty_out + qty
		elif reorder and qty <= reorder:
			qty_low = qty_low + qty
		else:
			qty_in = qty_in + qty

	return {
		"counts": data,
		"qty": {"in_stock": qty_in, "low_stock": qty_low, "out_of_stock": qty_out},
	}


def get_category_stock_value():
	cv_result = get_filters_cond()
	cond = cv_result[0]
	values = cv_result[1]
	rows = frappe.db.sql(
		"SELECT i.item_group AS category, COALESCE(SUM(b.stock_value), 0) AS value "
		"FROM `tabItem` i "
		"LEFT JOIN `tabBin` b ON b.item_code = i.item_code "
		"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond + " "
		"GROUP BY i.item_group "
		"HAVING value > 0 "
		"ORDER BY value DESC",
		values, as_dict=True)
	return [{"category": r.category, "value": flt(r.value)} for r in rows]


def get_category_item_count():
	cv_result = get_filters_cond()
	cond = cv_result[0]
	values = cv_result[1]
	rows = frappe.db.sql(
		"SELECT i.item_group AS category, COUNT(DISTINCT i.item_code) AS cnt "
		"FROM `tabItem` i "
		"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond + " "
		"GROUP BY i.item_group "
		"ORDER BY cnt DESC",
		values, as_dict=True)
	return [{"category": r.category, "count": r.cnt} for r in rows]


def get_top_low_stock(limit=5):
	cv_result = get_filters_cond()
	cond = cv_result[0]
	values = cv_result[1]
	rows = frappe.db.sql(
		"SELECT b.item_code, i.item_name, b.warehouse, b.actual_qty, "
		"COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0) AS reorder_level "
		"FROM `tabBin` b "
		"INNER JOIN `tabItem` i ON i.item_code = b.item_code "
		"LEFT JOIN `tabItem Reorder` ir ON ir.parent = i.item_code AND ir.warehouse = b.warehouse "
		"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond + " "
		"AND COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0) > 0 "
		"AND b.actual_qty <= COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0) "
		"ORDER BY (b.actual_qty / NULLIF(COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0), 0)) ASC "
		"LIMIT " + str(int(limit)),
		values, as_dict=True)

	return [{
		"item_code": r.item_code,
		"item_name": r.item_name,
		"available_qty": flt(r.actual_qty),
		"min_qty": flt(r.reorder_level),
	} for r in rows]


def get_stock_in_out_monthly(months=6):
	# FIX: zero-fill every month in range so gaps (e.g. June with no
	# postings) still show up on the chart instead of disappearing.
	# FIX: Store Location (warehouse) filter now applied here too --
	# previously this chart ignored the warehouse dropdown entirely.
	warehouse = frappe.form_dict.get("warehouse")
	values = {"months": months}
	wh_cond_in = ""
	wh_cond_out = ""
	if warehouse and warehouse != "All":
		values["warehouse"] = warehouse
		wh_cond_in = " AND pri.warehouse = %(warehouse)s"
		wh_cond_out = " AND sed.s_warehouse = %(warehouse)s"

	stock_in_rows = frappe.db.sql(
		"SELECT DATE_FORMAT(pr.posting_date, '%%Y-%%m') AS period, COALESCE(SUM(pri.qty), 0) AS qty "
		"FROM `tabPurchase Receipt` pr "
		"INNER JOIN `tabPurchase Receipt Item` pri ON pri.parent = pr.name "
		"WHERE pr.docstatus = 1 AND pr.posting_date >= DATE_SUB(CURDATE(), INTERVAL %(months)s MONTH)"
		+ wh_cond_in +
		" GROUP BY period",
		values, as_dict=True)

	stock_out_rows = frappe.db.sql(
		"SELECT DATE_FORMAT(se.posting_date, '%%Y-%%m') AS period, COALESCE(SUM(sed.qty), 0) AS qty "
		"FROM `tabStock Entry` se "
		"INNER JOIN `tabStock Entry Detail` sed ON sed.parent = se.name "
		"WHERE se.docstatus = 1 "
		"AND se.purpose IN ('Material Issue', 'Material Transfer', 'Send to Subcontractor') "
		"AND se.posting_date >= DATE_SUB(CURDATE(), INTERVAL %(months)s MONTH)"
		+ wh_cond_out +
		" GROUP BY period",
		values, as_dict=True)

	in_map = {}
	for r in stock_in_rows:
		in_map[r.period] = flt(r.qty)

	out_map = {}
	for r in stock_out_rows:
		out_map[r.period] = flt(r.qty)

	periods = get_month_range(months)

	stock_in = [{"period": p, "qty": in_map.get(p, 0)} for p in periods]
	stock_out = [{"period": p, "qty": out_map.get(p, 0)} for p in periods]

	return {"stock_in": stock_in, "stock_out": stock_out}


def get_stock_value_trend(months=6):
	# FIX: zero-fill every month in range (same pattern as stock in/out).
	# FIX: Store Location (warehouse) filter now applied here too.
	warehouse = frappe.form_dict.get("warehouse")
	values = {"months": months}
	wh_cond = ""
	if warehouse and warehouse != "All":
		values["warehouse"] = warehouse
		wh_cond = " AND sle.warehouse = %(warehouse)s"

	rows = frappe.db.sql(
		"SELECT DATE_FORMAT(sle.posting_date, '%%Y-%%m') AS period, "
		"SUM(sle.stock_value_difference) AS diff "
		"FROM `tabStock Ledger Entry` sle "
		"WHERE sle.is_cancelled = 0 "
		"AND sle.posting_date >= DATE_SUB(CURDATE(), INTERVAL %(months)s MONTH)"
		+ wh_cond +
		" GROUP BY period",
		values, as_dict=True)

	diff_map = {}
	for r in rows:
		diff_map[r.period] = flt(r.diff)

	periods = get_month_range(months)

	cumulative = 0
	out = []
	for p in periods:
		cumulative = cumulative + diff_map.get(p, 0)
		out.append({"period": p, "value": cumulative})
	return out


def get_recent_grn(limit=5):
	# FIX: Store Location (warehouse) filter now applied here too.
	warehouse = frappe.form_dict.get("warehouse")
	values = {}
	wh_cond = ""
	if warehouse and warehouse != "All":
		values["warehouse"] = warehouse
		wh_cond = " AND pri.warehouse = %(warehouse)s"

	rows = frappe.db.sql(
		"SELECT pr.name AS grn_no, pr.posting_date, pr.supplier AS vendor, "
		"COUNT(pri.name) AS items, SUM(pri.qty) AS qty "
		"FROM `tabPurchase Receipt` pr "
		"INNER JOIN `tabPurchase Receipt Item` pri ON pri.parent = pr.name "
		"WHERE pr.docstatus = 1"
		+ wh_cond +
		" GROUP BY pr.name "
		"ORDER BY pr.posting_date DESC, pr.creation DESC "
		"LIMIT " + str(int(limit)),
		values, as_dict=True)

	return [{
		"grn_no": r.grn_no,
		"date": str(r.posting_date) if r.posting_date else "",
		"vendor": r.vendor,
		"items": r.items,
		"qty": flt(r.qty),
	} for r in rows]


def get_recent_issue(limit=5):
	# FIX: widened purpose list -- was only "Material Issue" before, which
	# left the table empty if actual stock-out entries used a different
	# purpose (Material Transfer, Send to Subcontractor, etc).
	# If your org uses still other purpose values for "stock out", add
	# them to the IN(...) list below.
	# FIX: Store Location (warehouse) filter now applied here too
	# (matched against the source warehouse, since stock is going OUT).
	warehouse = frappe.form_dict.get("warehouse")
	values = {}
	wh_cond = ""
	if warehouse and warehouse != "All":
		values["warehouse"] = warehouse
		wh_cond = " AND sed.s_warehouse = %(warehouse)s"

	rows = frappe.db.sql(
		"SELECT se.name AS issue_no, se.posting_date, "
		"COALESCE(se.project, se.remarks, '-') AS reference, "
		"COUNT(sed.name) AS items, SUM(sed.qty) AS qty "
		"FROM `tabStock Entry` se "
		"INNER JOIN `tabStock Entry Detail` sed ON sed.parent = se.name "
		"WHERE se.docstatus = 1 "
		"AND se.purpose IN ('Material Issue', 'Material Transfer', 'Send to Subcontractor')"
		+ wh_cond +
		" GROUP BY se.name "
		"ORDER BY se.posting_date DESC, se.creation DESC "
		"LIMIT " + str(int(limit)),
		values, as_dict=True)

	return [{
		"issue_no": r.issue_no,
		"date": str(r.posting_date) if r.posting_date else "",
		"reference": r.reference,
		"items": r.items,
		"qty": flt(r.qty),
	} for r in rows]


def get_dispatch_status(limit=8):
	# FIX: Store Location (warehouse) filter now applied here too.
	warehouse = frappe.form_dict.get("warehouse")
	values = {}
	wh_cond = ""
	if warehouse and warehouse != "All":
		values["warehouse"] = warehouse
		wh_cond = " AND dni.warehouse = %(warehouse)s"

	rows = frappe.db.sql(
		"SELECT dn.name AS dn_no, dn.posting_date, dn.customer, "
		"COALESCE(dn.project, '-') AS project, "
		"dn.status, dn.per_billed, "
		"COUNT(dni.name) AS items, SUM(dni.qty) AS qty "
		"FROM `tabDelivery Note` dn "
		"INNER JOIN `tabDelivery Note Item` dni ON dni.parent = dn.name "
		"WHERE dn.docstatus IN (0, 1)"
		+ wh_cond +
		" GROUP BY dn.name "
		"ORDER BY dn.posting_date DESC, dn.creation DESC "
		"LIMIT " + str(int(limit)),
		values, as_dict=True)

	return [{
		"dn_no": r.dn_no,
		"date": str(r.posting_date) if r.posting_date else "",
		"customer": r.customer,
		"project": r.project,
		"status": r.status,
		"per_billed": flt(r.per_billed),
		"items": r.items,
		"qty": flt(r.qty),
	} for r in rows]


def get_filter_options():
	# NOTE: "categories" key removed -- Category filter dropped from UI
	# since it duplicated item_group.
	item_groups = frappe.db.sql("""SELECT name FROM `tabItem Group` WHERE is_group = 0 ORDER BY name""", as_dict=True)
	warehouses = frappe.db.sql("""SELECT name FROM `tabWarehouse` WHERE disabled = 0 AND is_group = 0 ORDER BY name""", as_dict=True)
	return {
		"item_groups": [d.name for d in item_groups],
		"warehouses": [d.name for d in warehouses],
	}


def get_alerts():
	cv_result = get_filters_cond()
	cond = cv_result[0]
	values = cv_result[1]
	status = get_stock_status_counts(cond, values)
	pending_grn = frappe.db.sql("""
		SELECT COUNT(*) AS cnt FROM `tabPurchase Receipt`
		WHERE docstatus = 1 AND per_billed < 100 AND status NOT IN ('Completed', 'Closed', 'Cancelled')
	""", as_dict=True)[0]

	alerts = []
	if status["out_of_stock"] > 0:
		alerts.append({"type": "danger", "message": str(status["out_of_stock"]) + " item(s) are Out of Stock"})
	if status["low_stock"] > 0:
		alerts.append({"type": "warning", "message": str(status["low_stock"]) + " item(s) are running Low on Stock"})
	if pending_grn.cnt > 0:
		alerts.append({"type": "info", "message": str(pending_grn.cnt) + " GRN(s) pending completion"})
	return alerts


# ----------------------------------------------------------------------------
# Router (must be defined last, after all functions above)
# ----------------------------------------------------------------------------

def get_drilldown(kpi):
	cv_result = get_filters_cond()
	cond = cv_result[0]
	values = cv_result[1]

	columns = []
	data = []

	if kpi == "total_items":
		rows = frappe.db.sql(
			"SELECT i.item_code, i.item_name, i.item_group, "
			"COALESCE(SUM(b.actual_qty), 0) AS qty, "
			"COALESCE(SUM(b.stock_value), 0) AS value "
			"FROM `tabItem` i "
			"LEFT JOIN `tabBin` b ON b.item_code = i.item_code "
			"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond + " "
			"GROUP BY i.item_code "
			"ORDER BY i.item_name",
			values, as_dict=True)
		columns = [
			{"key": "item_code", "label": "Item Code"},
			{"key": "item_name", "label": "Item Name"},
			{"key": "item_group", "label": "Category"},
			{"key": "qty", "label": "Qty", "type": "qty"},
			{"key": "value", "label": "Value", "type": "currency"},
		]
		data = [{"item_code": r.item_code, "item_name": r.item_name, "item_group": r.item_group,
			"qty": flt(r.qty), "value": flt(r.value)} for r in rows]

	elif kpi == "total_value":
		rows = frappe.db.sql(
			"SELECT i.item_code, i.item_name, i.item_group, "
			"COALESCE(SUM(b.actual_qty), 0) AS qty, "
			"COALESCE(SUM(b.stock_value), 0) AS value "
			"FROM `tabItem` i "
			"LEFT JOIN `tabBin` b ON b.item_code = i.item_code "
			"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond + " "
			"GROUP BY i.item_code "
			"HAVING value > 0 "
			"ORDER BY value DESC",
			values, as_dict=True)
		columns = [
			{"key": "item_code", "label": "Item Code"},
			{"key": "item_name", "label": "Item Name"},
			{"key": "item_group", "label": "Category"},
			{"key": "value", "label": "Stock Value", "type": "currency"},
		]
		data = [{"item_code": r.item_code, "item_name": r.item_name, "item_group": r.item_group,
			"value": flt(r.value)} for r in rows]

	elif kpi == "total_qty":
		rows = frappe.db.sql(
			"SELECT i.item_code, i.item_name, i.item_group, i.stock_uom, "
			"COALESCE(SUM(b.actual_qty), 0) AS qty "
			"FROM `tabItem` i "
			"LEFT JOIN `tabBin` b ON b.item_code = i.item_code "
			"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond + " "
			"GROUP BY i.item_code "
			"HAVING qty > 0 "
			"ORDER BY qty DESC",
			values, as_dict=True)
		columns = [
			{"key": "item_code", "label": "Item Code"},
			{"key": "item_name", "label": "Item Name"},
			{"key": "item_group", "label": "Category"},
			{"key": "qty", "label": "Qty", "type": "qty"},
			{"key": "stock_uom", "label": "UOM"},
		]
		data = [{"item_code": r.item_code, "item_name": r.item_name, "item_group": r.item_group,
			"qty": flt(r.qty), "stock_uom": r.stock_uom} for r in rows]

	elif kpi in ("low_stock", "out_of_stock", "in_stock"):
		rows = frappe.db.sql(
			"SELECT b.item_code, i.item_name, i.item_group, b.warehouse, b.actual_qty, "
			"COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0) AS reorder_level "
			"FROM `tabBin` b "
			"INNER JOIN `tabItem` i ON i.item_code = b.item_code "
			"LEFT JOIN `tabItem Reorder` ir ON ir.parent = i.item_code AND ir.warehouse = b.warehouse "
			"WHERE i.disabled = 0 AND i.is_stock_item = 1 AND " + cond + " "
			"ORDER BY b.actual_qty ASC",
			values, as_dict=True)

		for r in rows:
			qty = flt(r.actual_qty)
			reorder = flt(r.reorder_level)
			if kpi == "out_of_stock" and qty > 0:
				continue
			if kpi == "low_stock" and not (reorder and 0 < qty <= reorder):
				continue
			if kpi == "in_stock" and not (qty > 0 and (not reorder or qty > reorder)):
				continue
			data.append({
				"item_code": r.item_code, "item_name": r.item_name, "item_group": r.item_group,
				"warehouse": r.warehouse, "qty": qty, "reorder_level": reorder,
			})
		columns = [
			{"key": "item_code", "label": "Item Code"},
			{"key": "item_name", "label": "Item Name"},
			{"key": "warehouse", "label": "Warehouse"},
			{"key": "qty", "label": "Available Qty", "type": "qty"},
			{"key": "reorder_level", "label": "Min Qty", "type": "qty"},
		]

	elif kpi == "pending_grn":
		rows = frappe.db.sql("""
			SELECT pr.name AS grn_no, pr.posting_date, pr.supplier AS vendor,
				pr.status, pr.per_billed, pr.grand_total
			FROM `tabPurchase Receipt` pr
			WHERE pr.docstatus = 1 AND pr.per_billed < 100
				AND pr.status NOT IN ('Completed', 'Closed', 'Cancelled')
			ORDER BY pr.posting_date DESC
		""", {}, as_dict=True)
		columns = [
			{"key": "grn_no", "label": "GRN No."},
			{"key": "posting_date", "label": "Date"},
			{"key": "vendor", "label": "Vendor"},
			{"key": "status", "label": "Status", "type": "status"},
			{"key": "grand_total", "label": "Value", "type": "currency"},
		]
		data = [{"grn_no": r.grn_no, "posting_date": str(r.posting_date) if r.posting_date else "",
			"vendor": r.vendor, "status": r.status, "grand_total": flt(r.grand_total)} for r in rows]

	elif kpi == "stock_in_detail":
		rows = frappe.db.sql("""
			SELECT pr.name AS grn_no, pr.posting_date, pr.supplier AS vendor,
				pr.status, COUNT(pri.name) AS items, SUM(pri.qty) AS qty, pr.grand_total
			FROM `tabPurchase Receipt` pr
			INNER JOIN `tabPurchase Receipt Item` pri ON pri.parent = pr.name
			WHERE pr.docstatus = 1
			GROUP BY pr.name
			ORDER BY pr.posting_date DESC, pr.creation DESC
			LIMIT 200
		""", {}, as_dict=True)
		columns = [
			{"key": "grn_no", "label": "GRN No."},
			{"key": "posting_date", "label": "Date"},
			{"key": "vendor", "label": "Vendor"},
			{"key": "qty", "label": "Qty", "type": "qty"},
			{"key": "status", "label": "Status", "type": "status"},
			{"key": "grand_total", "label": "Value", "type": "currency"},
		]
		data = [{"grn_no": r.grn_no, "posting_date": str(r.posting_date) if r.posting_date else "",
			"vendor": r.vendor, "qty": flt(r.qty), "status": r.status,
			"grand_total": flt(r.grand_total)} for r in rows]

	elif kpi == "stock_out_detail":
		# FIX: widened purpose list (see get_recent_issue note above)
		rows = frappe.db.sql("""
			SELECT se.name AS issue_no, se.posting_date,
				COALESCE(se.project, se.remarks, '-') AS reference,
				COUNT(sed.name) AS items, SUM(sed.qty) AS qty
			FROM `tabStock Entry` se
			INNER JOIN `tabStock Entry Detail` sed ON sed.parent = se.name
			WHERE se.docstatus = 1
				AND se.purpose IN ('Material Issue', 'Material Transfer', 'Send to Subcontractor')
			GROUP BY se.name
			ORDER BY se.posting_date DESC, se.creation DESC
			LIMIT 200
		""", {}, as_dict=True)
		columns = [
			{"key": "issue_no", "label": "Issue No."},
			{"key": "posting_date", "label": "Date"},
			{"key": "reference", "label": "Reference"},
			{"key": "qty", "label": "Qty", "type": "qty"},
		]
		data = [{"issue_no": r.issue_no, "posting_date": str(r.posting_date) if r.posting_date else "",
			"reference": r.reference, "qty": flt(r.qty)} for r in rows]

	return {"columns": columns, "rows": data}


action = frappe.form_dict.get("action")

result = {}

if action == "get_kpis":
	result = get_kpis()
elif action == "get_stock_status":
	result = get_stock_status()
elif action == "get_category_stock_value":
	result = get_category_stock_value()
elif action == "get_category_item_count":
	result = get_category_item_count()
elif action == "get_top_low_stock":
	result = get_top_low_stock(frappe.form_dict.get("limit") or 5)
elif action == "get_stock_in_out_monthly":
	result = get_stock_in_out_monthly(frappe.form_dict.get("months") or 6)
elif action == "get_stock_value_trend":
	result = get_stock_value_trend(frappe.form_dict.get("months") or 6)
elif action == "get_recent_grn":
	result = get_recent_grn(frappe.form_dict.get("limit") or 5)
elif action == "get_recent_issue":
	result = get_recent_issue(frappe.form_dict.get("limit") or 5)
elif action == "get_dispatch_status":
	result = get_dispatch_status(frappe.form_dict.get("limit") or 8)
elif action == "get_filter_options":
	result = get_filter_options()
elif action == "get_alerts":
	result = get_alerts()
elif action == "get_drilldown":
	result = get_drilldown(frappe.form_dict.get("kpi"))
elif action == "get_all":
	# single call for initial page load (reduces round trips)
	result = {
		"kpis": get_kpis(),
		"stock_status": get_stock_status(),
		"category_stock_value": get_category_stock_value(),
		"category_item_count": get_category_item_count(),
		"top_low_stock": get_top_low_stock(5),
		"stock_in_out_monthly": get_stock_in_out_monthly(6),
		"stock_value_trend": get_stock_value_trend(6),
		"recent_grn": get_recent_grn(5),
		"recent_issue": get_recent_issue(5),
		"dispatch_status": get_dispatch_status(8),
		"filter_options": get_filter_options(),
		"alerts": get_alerts(),
	}
else:
	result = {"error": "Unknown action: " + str(action)}

frappe.response["message"] = result
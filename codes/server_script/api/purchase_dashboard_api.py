# ================================================================
# ERPNext v15 - Server Script (Type: API)
# Method Name: purchase_dashboard_api
#
# Single script handling all dashboard needs via "action" param:
#   action = "dashboard"     -> KPIs, donut, trend, top vendors, recent POs, approvals, insights
#   action = "item_master"   -> Item-wise Vendor Master List
#   action = "pl_statement"  -> Month-wise P/L Statement
#   action = "drilldown"     -> popup detail rows (includes global_search)
#
# CHANGELOG (this revision):
# 1. Date range filter now applied consistently to EVERY dashboard query
#    (invoices_pending, payments_due, recent_pos, pending_approvals,
#    overdue_pos were previously unfiltered - now all respect from_date/to_date)
# 2. po_trend "values" now sent as raw rupee amounts (not pre-divided by
#    crore) so the frontend can auto-format in Lac/Cr
# 3. quick_insights expanded from 3 to 5 items to match frontend's
#    insightKeyMap (on_time, overdue, cycle_time, savings, green)
# 4. po_by_status / po_by_vendor drilldowns now also honor the active
#    date range filter passed from the frontend
# ================================================================

action = frappe.form_dict.get("action") or "dashboard"


# ================================================================
# Shared helper: resolve date_range -> (from_date, to_date)
# Supports: Today, This Week, This Month, Custom Range, Last 7 Days,
# Last 30 Days, This Quarter, All Time  (old values kept for safety)
# ================================================================
def pmd_resolve_range():
	# NOTE: safe_exec sandbox does not allow tuple unpacking (e.g. "a, b = func()"),
	# so this returns a dict and callers must use ["from_date"] / ["to_date"].
	dr = frappe.form_dict.get("date_range") or "All Time"
	today = frappe.utils.nowdate()

	if dr == "Today":
		fd = today
	elif dr == "This Week":
		fd = frappe.utils.get_first_day_of_week(today)
	elif dr == "This Month":
		fd = frappe.utils.get_first_day(today)
	elif dr == "This Quarter":
		fd = frappe.utils.add_months(today, -3)
	elif dr == "Last 7 Days":
		fd = frappe.utils.add_days(today, -7)
	elif dr == "Last 30 Days":
		fd = frappe.utils.add_days(today, -30)
	elif dr == "All Time":
		fd = "2000-01-01"
	elif dr == "Custom Range":
		custom_from = frappe.form_dict.get("custom_from")
		custom_to = frappe.form_dict.get("custom_to")
		fd = custom_from or frappe.utils.add_days(today, -7)
		return {"from_date": fd, "to_date": (custom_to or today)}
	else:
		fd = frappe.utils.add_days(today, -7)

	return {"from_date": fd, "to_date": today}


# ================================================================
# ACTION 1: dashboard
# ================================================================
if action == "dashboard":

	pmd_range = pmd_resolve_range()
	from_date = pmd_range["from_date"]
	to_date = pmd_range["to_date"]

	# ---- KPI: Total POs & PO Value (includes Draft + Submitted, excludes Cancelled) ----
	po_summary = frappe.db.sql("""
		SELECT COUNT(*) as total_pos, COALESCE(SUM(grand_total),0) as total_value
		FROM `tabPurchase Order`
		WHERE docstatus IN (0, 1) AND transaction_date BETWEEN %s AND %s
	""", (from_date, to_date), as_dict=True)[0]

	# ---- KPI: GRN Completed (filtered by range) ----
	grn_count = frappe.db.count("Purchase Receipt", {
		"docstatus": 1,
		"posting_date": ["between", [from_date, to_date]]
	})

	# ---- KPI: Invoices Pending (FIX: now filtered by range) ----
	invoices_pending = frappe.db.count("Purchase Invoice", {
		"docstatus": 1,
		"status": ["in", ["Unpaid", "Overdue", "Partly Paid"]],
		"posting_date": ["between", [from_date, to_date]]
	})

	# ---- KPI: Payments Due (FIX: now filtered by range) ----
	payments_due = frappe.db.sql("""
		SELECT COALESCE(SUM(outstanding_amount),0) as due
		FROM `tabPurchase Invoice`
		WHERE docstatus = 1 AND outstanding_amount > 0
		  AND posting_date BETWEEN %s AND %s
	""", (from_date, to_date), as_dict=True)[0].due

	kpis = [
		{"label": "Total POs", "value": po_summary.total_pos, "delta": 0, "icon": "📋", "bg": "#dcfce7"},
		{"label": "PO Value", "value": po_summary.total_value, "isCurrency": True, "exact": True, "delta": 0, "icon": "📦", "bg": "#dbeafe"},
		{"label": "GRN Completed", "value": grn_count, "delta": 0, "icon": "🚚", "bg": "#fef3c7"},
		{"label": "Invoices Pending", "value": invoices_pending, "delta": 0, "icon": "🧾", "bg": "#ede9fe"},
		{"label": "Payments Due", "value": payments_due, "isCurrency": True, "delta": 0, "icon": "💰", "bg": "#dcfce7"},
	]

	# ---- PO Status Overview (donut) ----
	status_rows = frappe.db.sql("""
		SELECT status, COUNT(*) as cnt
		FROM `tabPurchase Order`
		WHERE transaction_date BETWEEN %s AND %s
		GROUP BY status
	""", (from_date, to_date), as_dict=True)

	status_colors = {
		"Draft": "#3b82f6", "Pending Approval": "#f59e0b", "To Receive and Bill": "#22c55e",
		"To Bill": "#eab308", "To Receive": "#eab308", "Completed": "#16a34a", "Cancelled": "#ef4444"
	}
	total_status = sum([r.cnt for r in status_rows]) or 1
	po_status = [{
		"label": r.status, "count": r.cnt,
		"pct": round(r.cnt / total_status * 100),
		"color": status_colors.get(r.status, "#94a3b8")
	} for r in status_rows]

	# ---- PO Value Trend ----
	# FIX: values sent as raw rupees now (frontend decides Lac vs Cr display)
	trend_rows = frappe.db.sql("""
		SELECT transaction_date as dt, SUM(grand_total) as val
		FROM `tabPurchase Order`
		WHERE docstatus IN (0, 1) AND transaction_date BETWEEN %s AND %s
		GROUP BY transaction_date
		ORDER BY transaction_date
	""", (from_date, to_date), as_dict=True)

	po_trend = {
		"labels": [frappe.utils.formatdate(r.dt, "dd MMM") for r in trend_rows],
		"values": [round(r.val or 0, 2) for r in trend_rows]
	}

	# ---- Top Vendors ----
	vendor_rows = frappe.db.sql("""
		SELECT supplier, supplier_name, SUM(grand_total) as val
		FROM `tabPurchase Order`
		WHERE docstatus IN (0, 1) AND transaction_date BETWEEN %s AND %s
		GROUP BY supplier
		ORDER BY val DESC
		LIMIT 5
	""", (from_date, to_date), as_dict=True)

	max_val = max([r.val for r in vendor_rows]) if vendor_rows else 1
	top_vendors = [{
		"name": r.supplier_name or r.supplier, "value": r.val,
		"pct": round((r.val / max_val) * 100)
	} for r in vendor_rows]

	# ---- Recent Purchase Orders (FIX: now filtered by range) ----
	recent_rows = frappe.db.sql("""
		SELECT name, supplier_name, transaction_date, grand_total, status
		FROM `tabPurchase Order`
		WHERE transaction_date BETWEEN %s AND %s
		ORDER BY creation DESC
		LIMIT 5
	""", (from_date, to_date), as_dict=True)

	recent_pos = [{
		"po": r.name, "vendor": r.supplier_name, "date": frappe.utils.formatdate(r.transaction_date, "dd MMM yyyy"),
		"value": r.grand_total, "status": r.status
	} for r in recent_rows]

	# ---- Pending Approvals (FIX: now filtered by range) ----
	pending_pos = frappe.db.sql("""
		SELECT name, supplier_name, grand_total, transaction_date
		FROM `tabPurchase Order`
		WHERE (status = 'Pending Approval' OR docstatus = 0)
		  AND transaction_date BETWEEN %s AND %s
		ORDER BY creation DESC
		LIMIT 5
	""", (from_date, to_date), as_dict=True)

	pending_approvals = [{
		"ref": r.name, "desc": "Vendor: " + (r.supplier_name or ""),
		"value": r.grand_total, "date": frappe.utils.formatdate(r.transaction_date, "dd MMM yyyy"),
		"icon": "📦"
	} for r in pending_pos]

	# ---- Overdue POs (FIX: now filtered by range) ----
	overdue_pos = frappe.db.count("Purchase Order", {
		"docstatus": 1, "status": ["not in", ["Completed", "Closed", "Cancelled"]],
		"schedule_date": ["<", frappe.utils.nowdate()],
		"transaction_date": ["between", [from_date, to_date]]
	})

	# ---- Avg GRN cycle time (PO -> GRN, days) within range ----
	avg_cycle_row = frappe.db.sql("""
		SELECT AVG(DATEDIFF(pr.posting_date, po.transaction_date)) as avg_days
		FROM `tabPurchase Receipt Item` pri
		INNER JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
		INNER JOIN `tabPurchase Order` po ON po.name = pri.purchase_order
		WHERE pr.docstatus = 1 AND pr.posting_date BETWEEN %s AND %s
	""", (from_date, to_date), as_dict=True)
	avg_cycle = avg_cycle_row[0].avg_days if avg_cycle_row and avg_cycle_row[0].avg_days else 0

	# ---- Total discount/savings within range ----
	total_discount = frappe.db.sql("""
		SELECT COALESCE(SUM(discount_amount),0) as disc
		FROM `tabPurchase Order`
		WHERE docstatus = 1 AND transaction_date BETWEEN %s AND %s
	""", (from_date, to_date), as_dict=True)[0].disc

	# ---- Quick Insights (FIX: expanded to 5 items to match frontend insightKeyMap) ----
	quick_insights = [
		{"label": "On-Time GRNs", "value": str(grn_count), "sub": "Received in selected period", "icon": "✅"},
		{"label": "Overdue POs", "value": str(overdue_pos), "sub": "Past schedule date", "icon": "⚠️"},
		{"label": "Avg Cycle Time", "value": str(round(avg_cycle, 1)) + " days", "sub": "PO to GRN", "icon": "⏱️"},
		{"label": "Savings", "value": "₹" + str(round(total_discount, 0)), "sub": "From discounts in period", "icon": "💹"},
		{"label": "Digital POs", "value": str(po_summary.total_pos), "sub": "Processed this period", "icon": "🌱"},
	]

	frappe.response["message"] = {
		"kpis": kpis,
		"poStatus": po_status,
		"poTrend": po_trend,
		"topVendors": top_vendors,
		"recentPOs": recent_pos,
		"pendingApprovals": pending_approvals,
		"quickInsights": quick_insights
	}


# ================================================================
# ACTION 2: item_master
# ================================================================
elif action == "item_master":

	items = frappe.db.sql("""
		SELECT
			poi.item_code,
			poi.item_name,
			po.supplier_name as vendor,
			poi.rate as last_po_rate,
			po.transaction_date as last_po_date
		FROM `tabPurchase Order Item` poi
		INNER JOIN `tabPurchase Order` po ON po.name = poi.parent
		INNER JOIN (
			SELECT item_code, MAX(po.transaction_date) as max_date
			FROM `tabPurchase Order Item` poi2
			INNER JOIN `tabPurchase Order` po ON po.name = poi2.parent
			WHERE po.docstatus = 1
			GROUP BY item_code
		) latest ON latest.item_code = poi.item_code AND latest.max_date = po.transaction_date
		WHERE po.docstatus = 1
		GROUP BY poi.item_code
		ORDER BY poi.item_code
		LIMIT 200
	""", as_dict=True)

	result = []
	for it in items:
		inv_rate = frappe.db.sql("""
			SELECT pii.rate
			FROM `tabPurchase Invoice Item` pii
			INNER JOIN `tabPurchase Invoice` pi ON pi.name = pii.parent
			WHERE pii.item_code = %s AND pi.docstatus = 1
			ORDER BY pi.posting_date DESC
			LIMIT 1
		""", (it.item_code,), as_dict=True)

		val_rate = frappe.db.get_value("Item", it.item_code, "valuation_rate") or 0
		if not val_rate:
			bin_row = frappe.db.sql("""
				SELECT AVG(valuation_rate) as vr FROM `tabBin` WHERE item_code = %s
			""", (it.item_code,), as_dict=True)
			val_rate = bin_row[0].vr or 0 if bin_row else 0

		result.append({
			"item_code": it.item_code,
			"item_name": it.item_name,
			"vendor": it.vendor,
			"last_po_rate": it.last_po_rate,
			"last_po_date": frappe.utils.formatdate(it.last_po_date, "dd MMM yyyy") if it.last_po_date else "",
			"last_invoiced_rate": inv_rate[0].rate if inv_rate else 0,
			"valuation_rate": round(val_rate, 2)
		})

	frappe.response["message"] = result


# ================================================================
# ACTION 3: pl_statement
# ================================================================
elif action == "pl_statement":

	fiscal_year = frappe.form_dict.get("fiscal_year") or None

	fy_filter_po = ""
	fy_filter_pi = ""
	params = []
	if fiscal_year:
		try:
			start_year = int(fiscal_year.replace("FY ", "").split("-")[0])
			fy_start = "%s-04-01" % start_year
			fy_end = "%s-03-31" % (start_year + 1)
			fy_filter_po = "AND po.transaction_date BETWEEN %s AND %s"
			fy_filter_pi = "AND pi.posting_date BETWEEN %s AND %s"
			params = [fy_start, fy_end]
		except Exception:
			pass

	po_monthly = frappe.db.sql("""
		SELECT
			DATE_FORMAT(po.transaction_date, '%%b %%Y') as month,
			DATE_FORMAT(po.transaction_date, '%%Y-%%m') as month_key,
			SUM(po.grand_total) as po_value,
			COUNT(*) as cnt
		FROM `tabPurchase Order` po
		WHERE po.docstatus = 1 """ + fy_filter_po + """
		GROUP BY month_key
		ORDER BY month_key
	""", tuple(params), as_dict=True)

	inv_monthly = frappe.db.sql("""
		SELECT
			DATE_FORMAT(pi.posting_date, '%%Y-%%m') as month_key,
			SUM(pi.grand_total) as invoiced_value
		FROM `tabPurchase Invoice` pi
		WHERE pi.docstatus = 1 """ + fy_filter_pi + """
		GROUP BY month_key
	""", tuple(params), as_dict=True)

	inv_map = {r.month_key: r.invoiced_value for r in inv_monthly}

	pl_rows = []
	for r in po_monthly:
		pl_rows.append({
			"month": r.month,
			"po_value": r.po_value,
			"invoiced_value": inv_map.get(r.month_key, 0),
			"count": r.cnt
		})

	frappe.response["message"] = pl_rows


# ================================================================
# ACTION 4: drilldown
# Handles all popup click details (KPI cards, donut segments,
# trend points, vendor rows, item history, PL month rows,
# global search, etc.)
# ================================================================
elif action == "drilldown":

	drill_type = frappe.form_dict.get("drill_type")

	def po_row(r):
		return {
			"po": r.name, "vendor": r.supplier_name, "date": frappe.utils.formatdate(r.transaction_date, "dd MMM yyyy"),
			"value": r.grand_total, "status": r.status
		}

	if drill_type in ("total_pos", "po_value"):
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT name, supplier_name, transaction_date, grand_total, status
			FROM `tabPurchase Order`
			WHERE docstatus IN (0, 1) AND transaction_date BETWEEN %s AND %s
			ORDER BY transaction_date DESC
		""", (fd, td), as_dict=True)
		frappe.response["message"] = [po_row(r) for r in rows]

	elif drill_type == "grn":
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT name, supplier_name, posting_date,
				(SELECT COUNT(*) FROM `tabPurchase Receipt Item` pri WHERE pri.parent = pr.name) as item_count
			FROM `tabPurchase Receipt` pr
			WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s
			ORDER BY posting_date DESC
		""", (fd, td), as_dict=True)
		frappe.response["message"] = [{
			"name": r.name, "vendor": r.supplier_name,
			"date": frappe.utils.formatdate(r.posting_date, "dd MMM yyyy"), "items": r.item_count
		} for r in rows]

	elif drill_type == "invoices":
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT pi.name, pi.supplier_name, pi.posting_date, pi.grand_total, pi.status,
				(SELECT GROUP_CONCAT(pii.item_name SEPARATOR ', ')
					FROM `tabPurchase Invoice Item` pii
					WHERE pii.parent = pi.name) as items
			FROM `tabPurchase Invoice` pi
			WHERE pi.docstatus = 1 AND pi.status IN ('Unpaid', 'Overdue', 'Partly Paid')
			  AND pi.posting_date BETWEEN %s AND %s
			ORDER BY pi.posting_date DESC
			LIMIT 200
		""", (fd, td), as_dict=True)
		frappe.response["message"] = [{
			"name": r.name, "vendor": r.supplier_name,
			"date": frappe.utils.formatdate(r.posting_date, "dd MMM yyyy"),
			"items": r.items or "",
			"value": r.grand_total, "status": r.status
		} for r in rows]

	elif drill_type == "payments_due":
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT name, supplier_name, due_date, outstanding_amount
			FROM `tabPurchase Invoice`
			WHERE docstatus = 1 AND outstanding_amount > 0
			  AND posting_date BETWEEN %s AND %s
			ORDER BY due_date ASC
			LIMIT 200
		""", (fd, td), as_dict=True)
		frappe.response["message"] = [{
			"name": r.name, "vendor": r.supplier_name,
			"date": frappe.utils.formatdate(r.due_date, "dd MMM yyyy") if r.due_date else "",
			"value": r.outstanding_amount
		} for r in rows]

	elif drill_type == "po_by_status":
		status = frappe.form_dict.get("status")
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT name, supplier_name, transaction_date, grand_total, status
			FROM `tabPurchase Order`
			WHERE status = %s AND transaction_date BETWEEN %s AND %s
			ORDER BY transaction_date DESC
			LIMIT 100
		""", (status, fd, td), as_dict=True)
		frappe.response["message"] = [po_row(r) for r in rows]

	elif drill_type == "po_by_vendor":
		vendor = frappe.form_dict.get("vendor")
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT name, supplier_name, transaction_date, grand_total, status
			FROM `tabPurchase Order`
			WHERE supplier_name = %s AND docstatus IN (0, 1)
			  AND transaction_date BETWEEN %s AND %s
			ORDER BY transaction_date DESC
			LIMIT 100
		""", (vendor, fd, td), as_dict=True)
		frappe.response["message"] = [po_row(r) for r in rows]

	elif drill_type == "po_by_date":
		date_label = frappe.form_dict.get("date_label")  # e.g. "19 May"
		try:
			parsed = frappe.utils.getdate(date_label + " " + str(frappe.utils.nowdate()[:4]))
		except Exception:
			parsed = None
		rows = []
		if parsed:
			rows = frappe.db.sql("""
				SELECT name, supplier_name, transaction_date, grand_total, status
				FROM `tabPurchase Order`
				WHERE transaction_date = %s AND docstatus IN (0, 1)
				ORDER BY grand_total DESC
			""", (parsed,), as_dict=True)
		frappe.response["message"] = [po_row(r) for r in rows]

	elif drill_type == "po_by_month":
		month = frappe.form_dict.get("month")  # e.g. "Jan 2025"
		try:
			dt = frappe.utils.getdate("01 " + month)
			month_start = dt
			month_end = frappe.utils.get_last_day(dt)
			rows = frappe.db.sql("""
				SELECT name, supplier_name, transaction_date, grand_total, status
				FROM `tabPurchase Order`
				WHERE transaction_date BETWEEN %s AND %s AND docstatus IN (0, 1)
				ORDER BY transaction_date DESC
			""", (month_start, month_end), as_dict=True)
			frappe.response["message"] = [po_row(r) for r in rows]
		except Exception:
			frappe.response["message"] = []

	elif drill_type == "approval_detail":
		ref = frappe.form_dict.get("ref")
		row = frappe.db.sql("""
			SELECT name, supplier_name, transaction_date, grand_total, status
			FROM `tabPurchase Order` WHERE name = %s
		""", (ref,), as_dict=True)
		frappe.response["message"] = [po_row(r) for r in row] if row else []

	elif drill_type == "item_history":
		item_code = frappe.form_dict.get("item_code")
		po_hist = frappe.db.sql("""
			SELECT po.name, po.supplier_name as vendor, po.transaction_date as dt, poi.rate as rate
			FROM `tabPurchase Order Item` poi
			INNER JOIN `tabPurchase Order` po ON po.name = poi.parent
			WHERE poi.item_code = %s AND po.docstatus = 1
			ORDER BY po.transaction_date DESC
			LIMIT 25
		""", (item_code,), as_dict=True)
		pi_hist = frappe.db.sql("""
			SELECT pi.name, pi.supplier_name as vendor, pi.posting_date as dt, pii.rate as rate
			FROM `tabPurchase Invoice Item` pii
			INNER JOIN `tabPurchase Invoice` pi ON pi.name = pii.parent
			WHERE pii.item_code = %s AND pi.docstatus = 1
			ORDER BY pi.posting_date DESC
			LIMIT 25
		""", (item_code,), as_dict=True)

		combined = []
		for r in po_hist:
			combined.append({"name": r.name, "vendor": r.vendor, "date": frappe.utils.formatdate(r.dt, "dd MMM yyyy"), "type": "Purchase Order", "value": r.rate})
		for r in pi_hist:
			combined.append({"name": r.name, "vendor": r.vendor, "date": frappe.utils.formatdate(r.dt, "dd MMM yyyy"), "type": "Purchase Invoice", "value": r.rate})
		frappe.response["message"] = combined

	elif drill_type == "insight_overdue":
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT name, supplier_name, transaction_date, grand_total, status
			FROM `tabPurchase Order`
			WHERE docstatus = 1 AND status NOT IN ('Completed', 'Closed', 'Cancelled')
				AND schedule_date < %s
				AND transaction_date BETWEEN %s AND %s
			ORDER BY schedule_date ASC
			LIMIT 100
		""", (frappe.utils.nowdate(), fd, td), as_dict=True)
		frappe.response["message"] = [po_row(r) for r in rows]

	elif drill_type in ("insight_on_time", "insight_cycle_time"):
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT po.name, po.supplier_name, po.transaction_date, po.grand_total, po.status
			FROM `tabPurchase Order` po
			INNER JOIN `tabPurchase Receipt Item` pri ON pri.purchase_order = po.name
			INNER JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
			WHERE pr.docstatus = 1 AND pr.posting_date BETWEEN %s AND %s
			GROUP BY po.name
			ORDER BY po.transaction_date DESC
			LIMIT 100
		""", (fd, td), as_dict=True)
		frappe.response["message"] = [po_row(r) for r in rows]

	elif drill_type == "insight_savings":
		pmd_range = pmd_resolve_range()
		fd = pmd_range["from_date"]
		td = pmd_range["to_date"]
		rows = frappe.db.sql("""
			SELECT name, supplier_name, transaction_date, grand_total, status
			FROM `tabPurchase Order`
			WHERE docstatus = 1 AND discount_amount > 0
			  AND transaction_date BETWEEN %s AND %s
			ORDER BY discount_amount DESC
			LIMIT 100
		""", (fd, td), as_dict=True)
		frappe.response["message"] = [po_row(r) for r in rows]

	elif drill_type == "global_search":
		q = (frappe.form_dict.get("q") or "").strip()
		if not q:
			frappe.response["message"] = []
		else:
			like_q = "%" + frappe.db.escape(q, percent=False).strip("'") + "%"
			rows = frappe.db.sql("""
				SELECT DISTINCT po.name, po.supplier_name, po.transaction_date, po.grand_total, po.status
				FROM `tabPurchase Order` po
				LEFT JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
				WHERE po.docstatus IN (0, 1)
					AND (
						po.name LIKE %(q)s
						OR po.supplier_name LIKE %(q)s
						OR poi.item_code LIKE %(q)s
						OR poi.item_name LIKE %(q)s
					)
				ORDER BY po.transaction_date DESC
				LIMIT 100
			""", {"q": like_q}, as_dict=True)
			frappe.response["message"] = [po_row(r) for r in rows]

	else:
		frappe.response["message"] = []


# ================================================================
# Fallback
# ================================================================
else:
	frappe.response["message"] = {"error": "Invalid action: " + str(action)}
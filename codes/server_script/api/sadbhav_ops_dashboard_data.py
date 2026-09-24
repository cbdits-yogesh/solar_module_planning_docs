# Server Script
# Script Type: API
# Method Name / Name: sadbhav_ops_dashboard_data
# Allow Guest: unchecked (must be logged in)
#
# Called from the Web Page JS as:
#   frappe.call({ method: "sadbhav_ops_dashboard_data", type: "GET", args: {...} })
#
# args.action decides what is returned:
#   "counts"     -> today / overall / tat (overdue) counts for every pipeline stage
#   "mystats"    -> same counts scoped to the logged in user
#   "clients"    -> paginated consolidated client table (Lead -> ... -> Sync)
#   "drilldown"  -> record list for a single stage + kind, for the KPI popup table

action = frappe.form_dict.get("action")

stage_keys = ["lead", "site_survey", "proposal", "sales_order", "dispatch", "installation", "sync"]
stage_doctypes = ["Lead", "Site Survey", "Quotation", "Sales Order", "Delivery Note", "Project", "Liaisoning And Synchronization"]
stage_label_fields = ["lead_name", "lead", "party_name", "customer_name", "customer_name", "project_name", "customer_name"]
# The field that represents "when this record was actually generated" per stage — NOT the system
# creation timestamp. Project has no dedicated equivalent field, so it stays on "creation" until told otherwise.
stage_date_fields = ["creation_date", "survey_date", "transaction_date", "transaction_date", "posting_date", "p_start_date", "posting_date"]

def extra_where(stage_doctype):
	if stage_doctype == "Quotation":
		return " AND quotation_to = 'Lead'"
	if stage_doctype == "Project":
		return " AND ifnull(lead, '') != ''"
	return ""

def build_counts(owner_filter):
	result = {}
	i = 0
	while i < len(stage_keys):
		key = stage_keys[i]
		dt = stage_doctypes[i]
		date_field = stage_date_fields[i]
		where_extra = extra_where(dt)
		owner_clause = ""
		params = []
		if owner_filter:
			owner_clause = " AND owner = %s"
			params.append(owner_filter)

		today_sql = "SELECT COUNT(*) FROM `tab" + dt + "` WHERE DATE(" + date_field + ") = CURDATE()" + where_extra + owner_clause
		overall_sql = "SELECT COUNT(*) FROM `tab" + dt + "` WHERE 1=1" + where_extra + owner_clause
		tat_sql = "SELECT COUNT(*) FROM `tab" + dt + "` WHERE stage_status = 'Overdue'" + where_extra + owner_clause

		today_count = frappe.db.sql(today_sql, tuple(params))[0][0]
		overall_count = frappe.db.sql(overall_sql, tuple(params))[0][0]
		tat_count = frappe.db.sql(tat_sql, tuple(params))[0][0]

		result[key] = {
			"today": today_count,
			"overall": overall_count,
			"tat": tat_count
		}
		i = i + 1
	return result

if action == "whoami":
	full_name = frappe.db.get_value("User", frappe.session.user, "full_name")
	role_rows = frappe.db.sql(
		"SELECT role FROM `tabHas Role` WHERE parent = %s AND parenttype = 'User'",
		(frappe.session.user,)
	)
	roles = []
	i = 0
	while i < len(role_rows):
		roles.append(role_rows[i][0])
		i = i + 1
	frappe.response["message"] = {
		"user": frappe.session.user,
		"fullname": full_name or frappe.session.user,
		"roles": roles
	}

elif action == "counts":
	frappe.response["message"] = build_counts(None)

elif action == "mystats":
	frappe.response["message"] = build_counts(frappe.session.user)

elif action == "drilldown":
	stage = frappe.form_dict.get("stage")
	kind = frappe.form_dict.get("kind")  # today | overall | tat
	search = frappe.form_dict.get("search") or ""

	if stage not in stage_keys:
		frappe.response["message"] = {"rows": [], "error": "unknown stage"}
	else:
		idx = stage_keys.index(stage)
		dt = stage_doctypes[idx]
		label_field = stage_label_fields[idx]
		date_field = stage_date_fields[idx]
		where_extra = extra_where(dt)

		# Detect which optional columns actually exist on this doctype, rather than
		# assuming — schema differs stage to stage.
		has_mobile = False
		has_capacity = False
		has_sla_due = False
		try:
			meta = frappe.get_meta(dt)
			has_mobile = meta.has_field("mobile_no")
			has_capacity = meta.has_field("solar_capacity")
			has_sla_due = meta.has_field("sla_due_date")
		except Exception:
			pass

		if kind == "today":
			cond = "DATE(" + date_field + ") = CURDATE()" + where_extra
		elif kind == "tat":
			cond = "stage_status = 'Overdue'" + where_extra
		else:
			cond = "1=1" + where_extra

		params = []
		if search:
			search_cols = ["name", label_field, "owner", "stage_status"]
			if has_mobile:
				search_cols.append("mobile_no")
			search_or = ""
			j = 0
			while j < len(search_cols):
				if j > 0:
					search_or = search_or + " OR "
				search_or = search_or + search_cols[j] + " LIKE %s"
				params.append("%" + search + "%")
				j = j + 1
			cond = cond + " AND (" + search_or + ")"

		select_cols = "name, " + label_field + ", " + date_field + " AS gen_date, owner, stage_status"
		if has_mobile:
			select_cols = select_cols + ", mobile_no"
		if has_capacity:
			select_cols = select_cols + ", solar_capacity"
		if has_sla_due:
			select_cols = select_cols + ", sla_due_date"

		sql = "SELECT " + select_cols + " FROM `tab" + dt + "` WHERE " + cond + " ORDER BY " + date_field + " DESC LIMIT 100"
		rows = frappe.db.sql(sql, tuple(params), as_dict=True)

		out_rows = []
		i = 0
		while i < len(rows):
			r = rows[i]
			status = r.get("stage_status") or "-"

			tat_delay = "-"
			if has_sla_due and status == "Overdue" and r.get("sla_due_date"):
				days_over = frappe.utils.date_diff(frappe.utils.nowdate(), r.get("sla_due_date"))
				if days_over and days_over > 0:
					tat_delay = str(days_over) + " days"

			gen_date = r.get("gen_date")
			out_rows.append({
				"name": r.get("name"),
				"label": r.get(label_field) or r.get("name"),
				"mobile": r.get("mobile_no") or "-",
				"capacity": r.get("solar_capacity") or "-",
				"date": frappe.utils.formatdate(gen_date) if gen_date else "-",
				"assigned_to": r.get("owner"),
				"status": status,
				"tat_delay": tat_delay,
				"doctype": dt
			})
			i = i + 1
		frappe.response["message"] = {"rows": out_rows, "doctype": dt}

elif action == "clients":
	search = frappe.form_dict.get("search") or ""
	limit = frappe.utils.cint(frappe.form_dict.get("limit") or 25)
	offset = frappe.utils.cint(frappe.form_dict.get("offset") or 0)

	search_clause = ""
	params = []
	if search:
		search_clause = " WHERE l.lead_name LIKE %s "
		params.append("%" + search + "%")

	sql = """
		SELECT
			l.name AS lead_name_id,
			l.lead_name AS client_name,
			l.status AS lead_status,
			COALESCE(so.solar_capacity, p.solar_capacity, ss.solar_capacity, l.solar_capacity) AS capacity,
			so.order_type AS order_type,
			so.name AS so_name,
			so.grand_total AS order_value,
			so.advance_paid AS amount_received,
			ss.name AS ss_name,
			q.name AS q_name,
			dn.name AS dn_name,
			dn.posting_date AS dispatch_date,
			p.name AS project_name_id,
			p.status AS install_status,
			p.actual_end_date AS install_end_date,
			sync.name AS sync_name,
			sync.synchronization_don_dt AS sync_done_date
		FROM `tabLead` l
		LEFT JOIN `tabSite Survey` ss ON ss.lead = l.name
		LEFT JOIN `tabQuotation` q ON q.site_survey = ss.name AND q.quotation_to = 'Lead'
		LEFT JOIN `tabSales Order` so ON so.lead = l.name
		LEFT JOIN `tabProject` p ON p.sales_order = so.name
		LEFT JOIN `tabDelivery Note` dn ON dn.project = p.name
		LEFT JOIN `tabLiaisoning And Synchronization` sync ON sync.sales_order = so.name
		""" + search_clause + """
		ORDER BY l.creation DESC
		LIMIT %s OFFSET %s
	"""
	params.append(limit)
	params.append(offset)
	rows = frappe.db.sql(sql, tuple(params), as_dict=True)

	out_rows = []
	i = 0
	while i < len(rows):
		r = rows[i]
		order_value = r.get("order_value") or 0
		received = r.get("amount_received") or 0
		pending = order_value - received

		if r.get("sync_name") and r.get("sync_done_date"):
			status = "Synchronized"
		elif r.get("dn_name"):
			status = "Dispatched"
		elif r.get("so_name"):
			status = "Sales Order Done"
		elif r.get("q_name"):
			status = "Proposal Completed"
		elif r.get("ss_name"):
			status = "Site Survey Done"
		else:
			status = r.get("lead_status") or "Lead"

		out_rows.append({
			"lead": r.get("lead_name_id"),
			"name": r.get("client_name") or r.get("lead_name_id"),
			"type": r.get("order_type") or "-",
			"capacity": r.get("capacity") or "-",
			"order_value": order_value,
			"received": received,
			"pending": pending,
			"dispatch_date": frappe.utils.formatdate(r.get("dispatch_date")) if r.get("dispatch_date") else "-",
			"install_done": frappe.utils.formatdate(r.get("install_end_date")) if r.get("install_end_date") else "-",
			"sync_done": frappe.utils.formatdate(r.get("sync_done_date")) if r.get("sync_done_date") else "-",
			"status": status
		})
		i = i + 1

	count_sql = "SELECT COUNT(*) FROM `tabLead` l" + search_clause
	count_params = tuple(params[0:1]) if search else tuple()
	total = frappe.db.sql(count_sql, count_params)[0][0]

	frappe.response["message"] = {"rows": out_rows, "total": total}

elif action == "doctype_list":
	rows = frappe.db.sql("SELECT name FROM `tabDocType` WHERE istable = 0", as_dict=True)
	names = []
	i = 0
	while i < len(rows):
		names.append(rows[i].get("name"))
		i = i + 1
	frappe.response["message"] = {"doctypes": names}

else:
	frappe.response["message"] = {"error": "unknown action"}
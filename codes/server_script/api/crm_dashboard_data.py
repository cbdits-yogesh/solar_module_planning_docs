# ============================================================
# Server Script: crm_dashboard_data
# Script Type : API
# API Method  : crm_dashboard_data
# ============================================================
# Frappe sandbox rules followed:
#   - No `import` statements (frappe, nowdate, flt, cint etc. are pre-injected)
#   - No `.format()` — string concatenation only
#   - No augmented assignment on dict items where sandbox blocks it
#   - All functions defined BEFORE the router / execution block
#   - Output via frappe.response["message"]
#   - ignore_permissions=True on every get_list call
#
# ============================================================
# CHANGELOG v7 (this version):
#
# 1) MASTER LIST CHANGED: Lead -> instead of Project.
#    Lead is the true starting point of the pipeline (Lead -> Survey ->
#    Proposal -> Sales Order -> Project -> Dispatch -> Sync). Previously
#    the dashboard looped over `Project` records, which meant any client
#    who had a Lead/Quotation/Sales Order but NO Project record yet was
#    completely invisible on the dashboard. Now every Lead produces a
#    row, walking FORWARD: Lead -> Quotation -> Sales Order -> Project,
#    with fuzzy-name fallbacks at each hop (same pattern already proven
#    for Delivery Note matching).
#
# 2) CAPACITY PARSING BUG FIXED: previously scanned the ENTIRE capacity
#    string for digits and concatenated them blindly, so "4 kw 6'
#    elevated" became "46" (wrongly landing in "Above 10 kW" filter).
#    Now only the FIRST whitespace-separated token is scanned for
#    digits, so "4 kw 6' elevated" -> 4.0 correctly, "3.3 kW" -> 3.3,
#    "200 kWp" -> 200.0, etc. Display label is untouched (still shows
#    the full original string).
#
# 3) (carried over from v6) Delivery Note docstatus loosened to "!= 2",
#    fuzzy match checks both `customer` and `customer_name`, "remarks"
#    field removed (doesn't exist on this instance's Delivery Note and
#    was silently killing all 4 Delivery Note queries), Installation
#    sourced from Project with a `modified`-date fallback when
#    actual_end_date is blank on a Completed project.
# ============================================================

def norm_name(s):
    v = (s or "")
    v = v.strip().lower()

    out = []
    depth = 0
    for ch in v:
        if ch == "(":
            depth = depth + 1
            continue
        if ch == ")":
            if depth > 0:
                depth = depth - 1
            continue
        if depth == 0:
            out.append(ch)
    v = "".join(out)

    for ch in [".", ",", "-", "_"]:
        v = v.replace(ch, " ")

    words = v.split()
    salutations = ["mr", "mrs", "ms", "shri", "smt", "dr", "ji", "sir", "madam"]
    cleaned_words = []
    for w in words:
        if w in salutations:
            continue
        if w.isdigit() and len(w) >= 6:
            continue
        cleaned_words.append(w)

    return " ".join(cleaned_words).strip()


def find_by_partial_name(name_map, key):
    if key in name_map:
        return name_map[key]
    if not key:
        return None
    best = None
    best_len = 0
    for map_key in name_map:
        if not map_key:
            continue
        if (map_key in key) or (key in map_key):
            l = min(len(map_key), len(key))
            if l > best_len:
                best_len = l
                best = name_map[map_key]
    if best_len >= 4:
        return best
    return None


DEBUG_ERRORS = {}

def get_list_safe(doctype, filters, fields, limit=0, order_by=None):
    try:
        if order_by:
            return frappe.db.get_list(
                doctype,
                filters=filters,
                fields=fields,
                limit_page_length=limit,
                order_by=order_by,
                ignore_permissions=True
            )
        else:
            return frappe.db.get_list(
                doctype,
                filters=filters,
                fields=fields,
                limit_page_length=limit,
                ignore_permissions=True
            )
    except Exception as e:
        DEBUG_ERRORS[doctype] = str(e)
        return []


def resolve_employee_names(emails):
    unique_emails = []
    seen = {}
    for e in emails:
        if e and e not in seen:
            seen[e] = True
            unique_emails.append(e)

    if not unique_emails:
        return {}

    users = get_list_safe("User", {"name": ["in", unique_emails]}, ["name", "full_name"], 0)
    m = {}
    for u in users:
        m[u.get("name")] = u.get("full_name") or u.get("name")
    return m


def fmt_date(d):
    if not d:
        return "-"
    return str(d).split(" ")[0]


# FIX: only parse digits from the FIRST token (split on whitespace), so
# stray numbers later in the string (e.g. "4 kw 6' elevated") don't get
# concatenated into a wrong value ("46"). Falls back to scanning the
# whole string only if the first token has no digits at all.
def parse_capacity_kw(capacity_raw):
    s = str(capacity_raw or "").strip()
    if not s:
        return 0.0

    first_token = s.split(" ")[0]
    digits = ""
    for ch in first_token:
        if ch.isdigit() or ch == ".":
            digits = digits + ch

    if not digits:
        # fallback: first token had no digits (e.g. starts with a word) —
        # scan the whole string but stop at the first space AFTER the
        # first digit run is found, to still avoid concatenating unrelated
        # numbers later in the string.
        started = False
        for ch in s:
            if ch.isdigit() or ch == ".":
                digits = digits + ch
                started = True
            elif ch == " " and started:
                break

    if not digits:
        return 0.0
    try:
        return float(digits)
    except Exception:
        return 0.0


def build_row(lead,
              survey_by_id, survey_by_lead, survey_by_name,
              quote_by_id, quote_by_customer_name, quote_by_lead_id,
              so_by_lead, so_by_proposal, so_by_customer_name,
              proj_by_name, proj_by_so, proj_by_customer_name,
              dn_by_so, dn_by_project, dn_by_customer, dn_by_customer_name,
              liaison_by_id, liaison_by_so, liaison_by_lead,
              liaison_by_project, liaison_by_customer,
              payment_by_customer, employee_name_map):

    cust_key = norm_name(lead.get("lead_name") or lead.get("company_name"))

    row = {
        "lead_id": lead.get("name"),
        "lead_name_id": None,   # filled below once/if a Project is found
        "client_name": lead.get("lead_name") or lead.get("company_name") or lead.get("name"),
        "phone": lead.get("mobile_no") or lead.get("phone") or "-",
        "status": "-",
        "location": "-",
        "capacity_kw": 0.0,
        "capacity_label": "-",
        "structure_type": "-",
        "creation_date": fmt_date(lead.get("creation")),
        "category": "Residential",
        "reference": employee_name_map.get(lead.get("owner")) or lead.get("owner") or "-",
        "documents": str(lead.get("lead_name") or ""),
        "drive": "Complete",
        "pay_mode": "-",
        "adv_rcvd_date": "-",
        "pay_50_date": "-",
        "pay_40_date": "-",
        "pay_remarks": "-",
        "invoice_amount": 0,
        "amount_received": 0,
        "material_status": "Pending",
        "survey": None,
        "proposal": None,
        "sales_order": None,
        "delivery": None,
        "install": None,
        "liaison": None
    }

    # ── STEP 1: Quotation — exact via lead's party_name link, fuzzy fallback ──
    q = quote_by_lead_id.get(lead.get("name"))
    if not q:
        q = find_by_partial_name(quote_by_customer_name, cust_key)

    if q:
        row["proposal"] = {
            "id": q.get("name"),
            "date": fmt_date(q.get("creation")),
            "by": employee_name_map.get(q.get("owner")) or q.get("owner") or "-",
            "stage_status": q.get("stage_status") or "-",
            "complete_status": q.get("complete_status") or "-",
            "complete_date": q.get("complete_date") or "-",
            "sla_due_date": q.get("sla_due_date") or "-",
            "delay_log": q.get("delay_log") or "-"
        }

    # ── STEP 2: Sales Order — via Quotation.proposal link, then Lead's own
    # "lead" field on Sales Order, then fuzzy customer-name fallback ──────
    so = None
    if q:
        so = so_by_proposal.get(q.get("name"))
    if not so:
        so = so_by_lead.get(lead.get("name"))
    if not so:
        so = find_by_partial_name(so_by_customer_name, cust_key)

    # ── STEP 3: Site Survey ───────────────────────────────────────
    s = None
    if so and so.get("site_survey"):
        s = survey_by_id.get(so.get("site_survey"))
    if not s:
        s = survey_by_lead.get(lead.get("name"))
    if not s:
        s = find_by_partial_name(survey_by_name, cust_key)

    if s:
        row["structure_type"] = s.get("type_of_mounting") or "-"
        row["survey"] = {
            "id": s.get("name"),
            "date": fmt_date(s.get("creation")),
            "by": employee_name_map.get(s.get("surveyed_by") or s.get("owner")) or s.get("surveyed_by") or s.get("owner") or "-",
            "stage_status": s.get("stage_status") or "-",
            "complete_status": s.get("complete_status") or "-",
            "complete_date": s.get("complete_date") or "-",
            "sla_due_date": s.get("sla_due_date") or "-",
            "delay_log": s.get("delay_log") or "-"
        }

    proj = None
    if so:
        row["invoice_amount"] = so.get("grand_total") or 0
        row["sales_order_id"] = so.get("name")
        row["pay_mode"] = "Finance" if so.get("without_pay_reason") == "BANK FINANCE" else "Cash"
        row["adv_rcvd_date"] = fmt_date(so.get("creation"))
        row["sales_order"] = {
            "id": so.get("name"),
            "date": fmt_date(so.get("creation")),
            "by": employee_name_map.get(so.get("owner")) or so.get("owner") or "-",
            "stage_status": so.get("stage_status") or "-",
            "complete_status": so.get("complete_status") or "-",
            "complete_date": so.get("complete_date") or "-",
            "sla_due_date": so.get("sla_due_date") or "-",
            "delay_log": so.get("delay_log") or "-"
        }

        pm = payment_by_customer.get(so.get("customer"))
        if pm:
            row["amount_received"] = pm.get("total") or 0
            dates = pm.get("dates") or []
            remarks = pm.get("remarks") or []
            if len(dates) > 0:
                row["pay_50_date"] = dates[0]
            if len(dates) > 1:
                row["pay_40_date"] = dates[1]
            if len(remarks) > 0:
                row["pay_remarks"] = " | ".join(remarks)

        # ── STEP 4: Project — via Sales Order.project link, then fuzzy ──
        if so.get("project"):
            proj = proj_by_name.get(so.get("project"))
        if not proj:
            proj = proj_by_so.get(so.get("name"))
    if not proj:
        proj = find_by_partial_name(proj_by_customer_name, cust_key)

    # ── Capacity: full priority chain across every doctype confirmed to
    # carry solar_capacity. Quotation is the most reliably-filled source
    # per real-world data entry habits, so it's checked first.
    capacity_raw = ""
    for val in [q.get("solar_capacity") if q else None,
                so.get("solar_capacity") if so else None,
                s.get("solar_capacity") if s else None,
                lead.get("solar_capacity"),
                proj.get("solar_capacity") if proj else None]:
        c = str(val or "").strip()
        if c and c not in ["", "None", "null", "-", "N/A", "0", "0.0"]:
            capacity_raw = c
            break

    row["capacity_kw"] = parse_capacity_kw(capacity_raw)
    row["capacity_label"] = capacity_raw if capacity_raw else "-"
    row["location"] = capacity_raw if capacity_raw else "-"
    row["documents"] = str(capacity_raw) + ", " + str(row["client_name"])

    if proj:
        row["lead_name_id"] = proj.get("name")
        row["status"] = proj.get("status") or "-"

        proj_status = str(proj.get("status") or "").strip()
        proj_is_completed = proj_status == "Completed"
        # Installation dates come from the MANUAL fields p_start_date /
        # p_end_date ("Project(Start Date)" / "Project(End Date)") --
        # confirmed via System Console these are the fields actually
        # filled in day-to-day. actual_start_date/actual_end_date are
        # Timesheet-driven and almost always blank, so kept only as a
        # secondary fallback; expected_start_date/expected_end_date are
        # no longer used at all per user confirmation.
        install_start_date = fmt_date(proj.get("p_start_date") or proj.get("actual_start_date"))
        if proj_is_completed:
            install_complete_date = fmt_date(proj.get("p_end_date") or proj.get("actual_end_date") or proj.get("modified"))
        else:
            install_complete_date = "-"
        install_display_date = install_complete_date if proj_is_completed else install_start_date
        install_stage_status = proj.get("stage_status") or ("Completed" if proj_is_completed else ("Open" if install_start_date != "-" else "-"))

        row["install"] = {
            "id": proj.get("name"),
            "start_date": install_start_date,
            "complete_date": install_complete_date,
            "date": install_display_date,
            "by": employee_name_map.get(proj.get("owner")) or proj.get("owner") or "-",
            "stage_status": install_stage_status,
            "complete_status": proj.get("complete_status") or "-",
            "sla_due_date": proj.get("sla_due_date") or "-",
            "delay_log": proj.get("delay_log") or "-"
        }
    else:
        # No Project yet — Installation node stays "Not Started" (grey/Pending)
        row["lead_name_id"] = None
        row["install"] = {
            "id": None, "start_date": "-", "complete_date": "-", "date": "-",
            "by": "-", "stage_status": "-", "complete_status": "-",
            "sla_due_date": "-", "delay_log": "-"
        }

    # ── STEP 5: Delivery Note ──────────────────────────────────────
    # PRIORITY 1: exact via Delivery Note Item.against_sales_order
    # PRIORITY 2: exact via Delivery Note.project
    # PRIORITY 3: exact via Delivery Note.customer
    # PRIORITY 4: FUZZY match on customer / customer_name
    dn = None
    if so and so.get("name"):
        dn = dn_by_so.get(so.get("name"))
    if not dn and proj:
        dn = dn_by_project.get(proj.get("name"))
    if not dn:
        cust_for_dn = (so.get("customer") if so else None) or (proj.get("customer") if proj else None)
        if cust_for_dn:
            dn = dn_by_customer.get(cust_for_dn)
    if not dn:
        dn = find_by_partial_name(dn_by_customer_name, cust_key)

    if dn:
        row["material_status"] = "SENT"
        row["dispatch_msg"] = "Dispatched successfully"
        row["material_remark"] = dn.get("late_remark") or "-"
        row["delivery"] = {
            "id": dn.get("name"),
            "date": fmt_date(dn.get("creation")),
            "by": employee_name_map.get(dn.get("manager") or dn.get("owner")) or dn.get("manager") or dn.get("owner") or "-",
            "stage_status": dn.get("stage_status") or "-",
            "complete_status": dn.get("complete_status") or "-",
            "complete_date": dn.get("complete_date") or "-",
            "sla_due_date": dn.get("sla_due_date") or "-",
            "delay_log": dn.get("delay_log") or "-"
        }

    # ── STEP 6: Liaisoning And Synchronization (Sync only) ──────────
    li = None
    if so and so.get("liaisoning_and_sync"):
        li = liaison_by_id.get(so.get("liaisoning_and_sync"))
    if not li and so and so.get("name"):
        li = liaison_by_so.get(so.get("name"))
    if not li:
        li = liaison_by_lead.get(lead.get("name"))
    if not li and proj:
        li = liaison_by_project.get(proj.get("name"))
    if not li:
        cust_for_li = (so.get("customer") if so else None) or (proj.get("customer") if proj else None)
        if cust_for_li:
            li = liaison_by_customer.get(cust_for_li)

    if li:
        li_creation = fmt_date(li.get("creation"))
        row["liaison"] = {
            "id": li.get("name"),
            "sync_date": li_creation,
            "by": employee_name_map.get(li.get("owner")) or li.get("owner") or "-",
            "stage_status": li.get("stage_status") or "-",
            "complete_status": li.get("complete_status") or "-",
            "complete_date": li.get("complete_date") or "-",
            "sla_due_date": li.get("sla_due_date") or "-",
            "delay_log": li.get("delay_log") or "-"
        }

    return row


# ------------------------------------------------------------
# MAIN (router) — Server Script API entry point
# LEAD is now the master driving list.
# ------------------------------------------------------------

debug_error = None
try:
    leads_res = frappe.db.get_list(
        "Lead",
        filters={},
        fields=["name", "lead_name", "company_name", "mobile_no", "phone", "owner",
                 "creation", "solar_capacity"],
        limit_page_length=1000,
        order_by="creation desc",
        ignore_permissions=True
    )
except Exception as e:
    leads_res = []
    debug_error = str(e)

if debug_error:
    frappe.response["message"] = {"rows": [], "debug_error": debug_error}
elif not leads_res:
    frappe.response["message"] = {"rows": []}
else:
    surveys_res = get_list_safe(
        "Site Survey", {},
        ["name", "lead", "lead_name", "type_of_mounting", "survey_date", "completed_date", "surveyed_by",
         "solar_capacity",
         "owner", "stage_status", "complete_status", "complete_date", "sla_due_date", "delay_log", "creation"],
        0
    )
    quotes_res = get_list_safe(
        "Quotation", {},
        ["name", "party_name", "customer_name", "quotation_to", "site_survey", "transaction_date", "owner",
         "solar_capacity",
         "stage_status", "complete_status", "complete_date", "sla_due_date", "delay_log", "creation"],
        0
    )
    sales_orders_res = get_list_safe(
        "Sales Order", {},
        ["name", "project", "grand_total", "customer", "customer_name", "without_pay_reason", "transaction_date",
         "proposal", "site_survey", "lead", "liaisoning_and_sync", "solar_capacity",
         "owner", "stage_status", "complete_status", "complete_date", "sla_due_date", "delay_log", "creation"],
        0
    )
    projects_res = get_list_safe(
        "Project", {},
        ["name", "project_name", "customer", "status", "solar_capacity", "creation", "owner",
         "actual_start_date", "actual_end_date", "expected_start_date", "expected_end_date",
         "p_start_date", "p_end_date", "modified",
         "stage_status", "complete_status", "complete_date", "sla_due_date", "delay_log"],
        0
    )

    so_names = []
    for so_row in sales_orders_res:
        so_names.append(so_row.get("name"))

    project_names = []
    seen_proj = {}
    for p in projects_res:
        n = p.get("name")
        if n and n not in seen_proj:
            seen_proj[n] = True
            project_names.append(n)

    customer_names = []
    seen_cust = {}
    for so_row in sales_orders_res:
        c = so_row.get("customer")
        if c and c not in seen_cust:
            seen_cust[c] = True
            customer_names.append(c)
    for p in projects_res:
        c = p.get("customer")
        if c and c not in seen_cust:
            seen_cust[c] = True
            customer_names.append(c)

    dn_item_links = []
    if so_names:
        dn_item_links = get_list_safe(
            "Delivery Note Item",
            {"against_sales_order": ["in", so_names]},
            ["parent", "against_sales_order"],
            0
        )

    dn_names_from_items = []
    seen_dn_names = {}
    so_name_by_dn_name = {}
    for item in dn_item_links:
        dn_n = item.get("parent")
        so_n = item.get("against_sales_order")
        if dn_n and dn_n not in seen_dn_names:
            seen_dn_names[dn_n] = True
            dn_names_from_items.append(dn_n)
        if dn_n and so_n:
            so_name_by_dn_name[dn_n] = so_n

    # "remarks" is NOT a real column on Delivery Note in this instance
    # (confirmed via System Console: "Unknown column 'remarks'"), which
    # was silently killing ALL Delivery Note queries. Removed.
    dn_fields = ["name", "project", "customer", "customer_name", "posting_date", "manager", "late_remark",
                 "owner", "stage_status", "complete_status", "complete_date", "sla_due_date",
                 "delay_log", "creation", "docstatus"]

    delivery_notes_via_items = []
    if dn_names_from_items:
        delivery_notes_via_items = get_list_safe(
            "Delivery Note", {"name": ["in", dn_names_from_items], "docstatus": ["!=", 2]},
            dn_fields, 0
        )

    delivery_notes_by_project = get_list_safe(
        "Delivery Note", {"project": ["in", project_names], "docstatus": ["!=", 2]},
        dn_fields, 0
    ) if project_names else []

    delivery_notes_by_customer = []
    if customer_names:
        delivery_notes_by_customer = get_list_safe(
            "Delivery Note", {"customer": ["in", customer_names], "docstatus": ["!=", 2]},
            dn_fields, 0
        )

    # Fetch ALL non-cancelled Delivery Notes for fuzzy fallback matching.
    delivery_notes_all = get_list_safe(
        "Delivery Note", {"docstatus": ["!=", 2]},
        dn_fields, 0
    )

    liaison_res = get_list_safe(
        "Liaisoning And Synchronization", {},
        ["name", "project", "sales_order", "lead", "customer",
         "posting_date", "completed_date", "synchronization_don_dt",
         "liaisoning_status", "owner", "stage_status", "complete_status", "complete_date",
         "sla_due_date", "delay_log", "creation"],
        0
    )

    payment_entries_res = []
    if customer_names:
        payment_entries_res = get_list_safe(
            "Payment Entry", {"party": ["in", customer_names], "docstatus": 1},
            ["party", "received_amount", "posting_date", "remarks"],
            0
        )

    owner_email_pool = []
    for l in leads_res:
        owner_email_pool.append(l.get("owner"))
    for s in surveys_res:
        owner_email_pool.append(s.get("surveyed_by") or s.get("owner"))
    for q in quotes_res:
        owner_email_pool.append(q.get("owner"))
    for so in sales_orders_res:
        owner_email_pool.append(so.get("owner"))
    for p in projects_res:
        owner_email_pool.append(p.get("owner"))
    for dn in delivery_notes_all:
        owner_email_pool.append(dn.get("manager") or dn.get("owner"))
    for li in liaison_res:
        owner_email_pool.append(li.get("owner"))

    employee_name_map = resolve_employee_names(owner_email_pool)

    survey_by_id = {}
    for s in surveys_res:
        survey_by_id[s.get("name")] = s

    survey_by_lead = {}
    for s in surveys_res:
        ld = s.get("lead")
        if ld:
            survey_by_lead[ld] = s

    survey_by_name = {}
    for s in surveys_res:
        survey_by_name[norm_name(s.get("lead_name"))] = s

    quote_by_id = {}
    for q in quotes_res:
        quote_by_id[q.get("name")] = q

    quote_by_lead_id = {}
    for q in quotes_res:
        pn = q.get("party_name")
        if pn:
            quote_by_lead_id[pn] = q

    quote_by_customer_name = {}
    for q in quotes_res:
        quote_by_customer_name[norm_name(q.get("customer_name"))] = q

    so_by_proposal = {}
    for so in sales_orders_res:
        pr = so.get("proposal")
        if pr:
            so_by_proposal[pr] = so

    so_by_lead = {}
    for so in sales_orders_res:
        ld = so.get("lead")
        if ld:
            so_by_lead[ld] = so

    so_by_customer_name = {}
    for so in sales_orders_res:
        key1 = norm_name(so.get("customer"))
        key2 = norm_name(so.get("customer_name"))
        if key1:
            so_by_customer_name[key1] = so
        if key2 and key2 != key1:
            so_by_customer_name[key2] = so

    proj_by_name = {}
    for p in projects_res:
        proj_by_name[p.get("name")] = p

    proj_by_so = {}
    for so in sales_orders_res:
        pj = so.get("project")
        if pj and pj in proj_by_name:
            proj_by_so[so.get("name")] = proj_by_name[pj]

    proj_by_customer_name = {}
    for p in projects_res:
        key1 = norm_name(p.get("customer"))
        key2 = norm_name(p.get("project_name"))
        if key1:
            proj_by_customer_name[key1] = p
        if key2 and key2 != key1:
            proj_by_customer_name[key2] = p

    dn_by_so = {}
    for dn in delivery_notes_via_items:
        so_n = so_name_by_dn_name.get(dn.get("name"))
        if so_n:
            dn_by_so[so_n] = dn

    dn_by_project = {}
    for dn in delivery_notes_by_project:
        dn_by_project[dn.get("project")] = dn

    dn_by_customer = {}
    for dn in delivery_notes_by_customer:
        dn_by_customer[dn.get("customer")] = dn

    dn_by_customer_name = {}
    for dn in delivery_notes_all:
        key1 = norm_name(dn.get("customer"))
        key2 = norm_name(dn.get("customer_name"))
        if key1:
            dn_by_customer_name[key1] = dn
        if key2 and key2 != key1:
            dn_by_customer_name[key2] = dn

    liaison_by_id = {}
    for li in liaison_res:
        liaison_by_id[li.get("name")] = li

    liaison_by_so = {}
    for li in liaison_res:
        so_ref = li.get("sales_order")
        if so_ref:
            liaison_by_so[so_ref] = li

    liaison_by_lead = {}
    for li in liaison_res:
        ld_ref = li.get("lead")
        if ld_ref:
            liaison_by_lead[ld_ref] = li

    liaison_by_project = {}
    for li in liaison_res:
        pj_ref = li.get("project")
        if pj_ref:
            liaison_by_project[pj_ref] = li

    liaison_by_customer = {}
    for li in liaison_res:
        cu_ref = li.get("customer")
        if cu_ref:
            liaison_by_customer[cu_ref] = li

    payment_by_customer = {}
    for pe in payment_entries_res:
        party = pe.get("party")
        if party not in payment_by_customer:
            payment_by_customer[party] = {"total": 0, "dates": [], "remarks": []}
        payment_by_customer[party]["total"] = payment_by_customer[party]["total"] + (pe.get("received_amount") or 0)
        if pe.get("posting_date"):
            payment_by_customer[party]["dates"].append(pe.get("posting_date"))
        if pe.get("remarks"):
            payment_by_customer[party]["remarks"].append(pe.get("remarks"))

    rows = []
    for lead in leads_res:
        rows.append(build_row(
            lead,
            survey_by_id, survey_by_lead, survey_by_name,
            quote_by_id, quote_by_customer_name, quote_by_lead_id,
            so_by_lead, so_by_proposal, so_by_customer_name,
            proj_by_name, proj_by_so, proj_by_customer_name,
            dn_by_so, dn_by_project, dn_by_customer, dn_by_customer_name,
            liaison_by_id, liaison_by_so, liaison_by_lead,
            liaison_by_project, liaison_by_customer,
            payment_by_customer, employee_name_map
        ))

    frappe.response["message"] = {
        "rows": rows,
        "debug_errors": DEBUG_ERRORS,
        "debug_counts": {
            "leads": len(leads_res),
            "surveys": len(surveys_res),
            "quotes": len(quotes_res),
            "sales_orders": len(sales_orders_res),
            "projects": len(projects_res),
            "delivery_notes_via_items": len(delivery_notes_via_items),
            "delivery_notes_by_project": len(delivery_notes_by_project),
            "delivery_notes_by_customer": len(delivery_notes_by_customer),
            "delivery_notes_all": len(delivery_notes_all),
            "liaison": len(liaison_res),
            "payment_entries": len(payment_entries_res)
        }
    }
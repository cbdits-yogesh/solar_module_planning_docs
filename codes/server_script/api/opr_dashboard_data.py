import frappe

@frappe.whitelist()
def get_days_delayed_data():
    # Example: fetch data from Lead
    leads = frappe.get_all("Lead",
        fields=["name","customer","site","current_stage","expected_delivery_date as expected","days_delayed as delay","assigned_to","priority"])
    # Example: fetch Purchase Orders
    pos = frappe.get_all("Purchase Order",
        fields=["name as po","supplier as vendor","item_code as item","transaction_date as orderDate","schedule_date as expected","days_delayed as delay","base_net_total as value","status"])
    # Example: fetch Stock Entries for kits (Material Transfer)
    stores = frappe.get_all("Stock Entry",
        filters={"purpose": "Material Transfer"},
        fields=["name as id","to_warehouse as project","item","material_request_date as request","schedule_date as target","days_delayed as delay","delay_reason as reason","owner as incharge"])
    return {"leadsData": leads, "poData": pos, "storeData": stores}


# ═══════════════════════════════════════════════════════════════════════════════
# OPR DASHBOARD — Server Script (LIVE DATA · RestrictedPython-safe)
# Type: API  |  Method Name: opr_dashboard_data
# ═══════════════════════════════════════════════════════════════════════════════

action      = frappe.form_dict.get("action",      "summary")
tab         = frappe.form_dict.get("tab",         "OPEN")
kpi_key     = frappe.form_dict.get("kpi_key",     "")
sub_filter  = frappe.form_dict.get("sub_filter",  "")
user_filter = frappe.form_dict.get("user_filter", "")
date_from   = frappe.form_dict.get("date_from",   "")
date_to     = frappe.form_dict.get("date_to",     "")
page        = int(frappe.form_dict.get("page", 1) or 1)

PAGE  = 20
OFF   = (page - 1) * PAGE
today = frappe.utils.today()
out   = {}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Utility helpers
# ══════════════════════════════════════════════════════════════════════════════

def df_eq(rows, field, val):
    return [x for x in rows if x.get(field) == val]

def df_in(rows, field, vals):
    return [x for x in rows if x.get(field) in vals]

def df_not_in(rows, field, vals):
    return [x for x in rows if x.get(field) not in vals]

def df_lt(rows, field, val):
    return [x for x in rows if x.get(field) and str(x.get(field)) < str(val)]

def df_user(rows, field, user):
    if not user:
        return rows
    return [x for x in rows if x.get(field) == user]

def df_grp(rows, field):
    result = {}
    for x in rows:
        k = x.get(field, "") or ""
        result[k] = result.get(k, 0) + 1
    return result

def sum_field(rows, field):
    total = 0
    for x in rows:
        total = total + (x.get(field) or 0)
    return total

def fmt_dur(secs):
    if not secs:
        return "00:00:00"
    s = int(secs)
    hh = s // 3600
    mm = (s % 3600) // 60
    ss = s % 60
    return str(hh).zfill(2) + ":" + str(mm).zfill(2) + ":" + str(ss).zfill(2)

def dur_bucket(secs):
    if secs < 120:
        return "dur_short"
    if secs < 600:
        return "dur_mid"
    return "dur_long"

def mk_col(f, l, t="text", dt=None):
    col = {"field": f, "label": l, "type": t}
    if dt:
        col["doctype"] = dt
    return col

def seg_card(kpi, label, cnt, color, icon, fk, nxt="userwise", amt=0):
    return {"key": kpi, "label": label, "count": cnt, "color": color,
            "icon": icon, "parent_key": kpi, "filter_key": fk,
            "next": nxt, "has_drill": nxt != "table", "amount": amt}

def make_uw_cards(kpi, rows, uf, clr, icon, sf, amt_field=""):
    grp = df_grp(rows, uf)
    all_amt = sum_field(rows, amt_field) if amt_field else 0
    cards = [{"key": kpi, "label": "All Users", "count": len(rows),
              "color": "#3b82f6", "icon": "👥", "parent_key": kpi,
              "filter_key": sf, "user": "", "next": "table", "has_drill": False,
              "amount": all_amt}]
    for uname in sorted(grp.keys()):
        u_rows = df_user(rows, uf, uname)
        cards.append({"key": kpi, "label": uname, "count": grp[uname],
                      "color": clr, "icon": icon, "parent_key": kpi,
                      "filter_key": sf, "user": uname,
                      "next": "table", "has_drill": False,
                      "amount": sum_field(u_rows, amt_field) if amt_field else 0})
    return cards

def make_drill(groups, uw_rows, uf, kpi, clr, icon, sf, amt_field=""):
    return {"groups": groups, "user_cards": make_uw_cards(kpi, uw_rows, uf, clr, icon, sf, amt_field)}

def live_page(rows):
    return rows[OFF: OFF + PAGE]

def live_tbl(rows, cols, title):
    return {"columns": cols, "rows": live_page(rows), "total": len(rows), "title": title}

def safe_cnt(dt, ff=None):
    try:
        return frappe.db.count(dt, ff or {}) or 0
    except Exception:
        return 0

def safe_get_list(doctype, filters, fields, limit=500, order_by="creation desc"):
    try:
        return frappe.db.get_list(doctype, filters=filters, fields=fields,
                                  limit=limit, order_by=order_by,
                                  ignore_permissions=True) or []
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Column sets
# ══════════════════════════════════════════════════════════════════════════════

COLS_ACT = [
    mk_col("reference_name","Record"), mk_col("reference_doctype","Module"),
    mk_col("activity_type","Type"), mk_col("assigned_to","Assigned To"),
    mk_col("due_date","Due Date"), mk_col("days_overdue","Days Overdue"),
    mk_col("status","Status","status"), mk_col("notes","Notes"),
]
COLS_TODAY_ACT = [
    mk_col("subject","Subject"), mk_col("activity_type","Type"),
    mk_col("assigned_to","Assigned To"), mk_col("scheduled_time","Time"),
    mk_col("status","Status","status"), mk_col("reference_doctype","Module"),
    mk_col("reference_name","Linked Record"), mk_col("priority","Priority"),
]
COLS_LEAD = [
    mk_col("lead_name","Lead Name"), mk_col("company","Company"),
    mk_col("source","Source"), mk_col("status","Status","status"),
    mk_col("lead_owner","Owner"), mk_col("creation","Created"),
    mk_col("contact_date","Follow-up"), mk_col("lead_value","Lead Value","currency"),
    mk_col("city","City"),
]
COLS_OPP = [
    mk_col("opportunity_name","Opportunity"), mk_col("customer","Account"),
    mk_col("sales_stage","Stage"), mk_col("opportunity_owner","Owner"),
    mk_col("opportunity_amount","Amount","currency"),
    mk_col("expected_closing","Close Date"), mk_col("probability","Prob %"),
]
COLS_CONTACT = [
    mk_col("full_name","Name"), mk_col("company_name","Company"),
    mk_col("contact_type","Type"), mk_col("owner","Owner"),
    mk_col("mobile_no","Phone"), mk_col("email_id","Email"),
    mk_col("last_activity","Last Activity"), mk_col("last_activity_date","Last Active"),
]
COLS_CALL = [
    mk_col("subject","Subject"), mk_col("direction","Direction"),
    mk_col("status","Status","status"), mk_col("caller","Caller"),
    mk_col("receiver","Receiver"), mk_col("duration_fmt","Duration"),
    mk_col("creation","Date"), mk_col("reference_name","Linked Record"),
]
COLS_MSG = [
    mk_col("communication_medium","Channel"), mk_col("direction","Direction"),
    mk_col("status","Status","status"), mk_col("recipients","Contact"),
    mk_col("sender","Sender"), mk_col("creation","Sent At"),
    mk_col("reference_name","Linked Record"),
]
COLS_TICKET = [
    mk_col("name","Ticket ID"), mk_col("subject","Subject"),
    mk_col("customer","Account"), mk_col("status","Status","status"),
    mk_col("priority","Priority"), mk_col("support_mode","Mode"),
    mk_col("raised_by","Assigned To"), mk_col("opening_date","Created"),
    mk_col("resolution_by","Due"), mk_col("sla_status","SLA","status"),
]
COLS_ACCOUNT = [
    mk_col("customer_name","Account Name"), mk_col("customer_type","Type"),
    mk_col("industry","Industry"), mk_col("account_manager","Owner"),
    mk_col("territory","Region"), mk_col("city","City"),
    mk_col("last_activity","Last Activity"),
]
COLS_PROJ = [
    mk_col("project_name","Project"), mk_col("status","Status","status"),
    mk_col("project_manager","Manager"), mk_col("expected_start_date","Start"),
    mk_col("expected_end_date","Planned End"), mk_col("actual_end_date","Actual End"),
    mk_col("percent_complete","% Done"), mk_col("customer","Customer"),
]
COLS_TASK = [
    mk_col("subject","Task"), mk_col("project","Project"),
    mk_col("status","Status","status"), mk_col("priority","Priority"),
    mk_col("assigned_to","Assigned To"), mk_col("exp_end_date","Due"),
]
COLS_BUG = [
    mk_col("name","Bug ID"), mk_col("subject","Title"),
    mk_col("severity","Severity","status"), mk_col("bug_module","Module"),
    mk_col("raised_by","Reporter"), mk_col("assigned_to","Assigned To"),
    mk_col("status","Status","status"), mk_col("opening_date","Reported"),
]
COLS_WON = [
    mk_col("opportunity_name","Opportunity"), mk_col("customer","Account"),
    mk_col("opportunity_owner","Owner"),
    mk_col("opportunity_amount","Amount","currency"),
    mk_col("expected_closing","Won On"), mk_col("source","Source"),
    mk_col("days_to_close","Days to Close"),
]
COLS_LOST = [
    mk_col("opportunity_name","Opportunity"), mk_col("customer","Account"),
    mk_col("opportunity_owner","Owner"),
    mk_col("opportunity_amount","Amount","currency"),
    mk_col("expected_closing","Lost On"), mk_col("lost_reason","Lost Reason"),
    mk_col("competitor","Competitor"), mk_col("sales_stage","Stage at Loss"),
]
COLS_ACT_COMP = [
    mk_col("subject","Subject"), mk_col("activity_type","Type"),
    mk_col("reference_doctype","Module"), mk_col("reference_name","Linked Record"),
    mk_col("assigned_to","Completed By"), mk_col("due_date","Scheduled"),
    mk_col("completed_on","Completed On"),
]
COLS_ACT_NH = [
    mk_col("subject","Subject"), mk_col("activity_type","Type"),
    mk_col("assigned_to","Assigned To"), mk_col("due_date","Scheduled"),
    mk_col("cancel_reason","Reason"), mk_col("reference_name","Linked Record"),
]
COLS_TKT_CLOSED = [
    mk_col("name","Ticket ID"), mk_col("subject","Subject"),
    mk_col("customer","Account"), mk_col("priority","Priority"),
    mk_col("raised_by","Resolved By"), mk_col("opening_date","Opened"),
    mk_col("resolution_date","Closed"), mk_col("resolution_time","Resolution Time"),
    mk_col("sla_status","SLA","status"), mk_col("csat","CSAT"),
]
COLS_LEAD_CONV = [
    mk_col("lead_name","Lead Name"), mk_col("company","Company"),
    mk_col("source","Source"), mk_col("lead_owner","Owner"),
    mk_col("creation","Lead Created"), mk_col("converted_on","Converted"),
    mk_col("days_to_convert","Days to Convert"),
    mk_col("opp_value","Opp Value","currency"),
]
COLS_LEAD_DEAD = [
    mk_col("lead_name","Lead Name"), mk_col("company","Company"),
    mk_col("source","Source"), mk_col("lead_owner","Owner"),
    mk_col("creation","Created"), mk_col("dead_date","Dead Date"),
    mk_col("dead_reason","Reason"), mk_col("status","Status","status"),
]
COLS_CALL_COMP = [
    mk_col("subject","Subject"), mk_col("direction","Direction"),
    mk_col("caller","Caller"), mk_col("receiver","Receiver"),
    mk_col("duration_fmt","Duration"), mk_col("creation","Date"),
    mk_col("reference_name","Linked Record"),
]
COLS_PROJ_COMP = [
    mk_col("project_name","Project"), mk_col("customer","Customer"),
    mk_col("project_manager","PM"), mk_col("expected_start_date","Start"),
    mk_col("expected_end_date","Planned End"), mk_col("actual_end_date","Actual End"),
    mk_col("delay_days","Delay (days)"), mk_col("percent_complete","% Done"),
]

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Lookup maps
# ══════════════════════════════════════════════════════════════════════════════

LD_ST = {
    "st_new":"New","st_contacted":"Contacted","st_follow_up":"Follow Up",
    "st_interested":"Interested","st_not_interested":"Not Interested","st_junk":"Junk",
}
OPP_FK = {
    "st_prospecting":"Prospecting","st_qualification":"Qualification",
    "st_demo":"Demo/Presentation","st_proposal":"Proposal/Price Quote",
    "st_negotiation":"Negotiation/Review","st_commit":"Commit",
}
TK_ST   = {"st_open":"Open","st_inprogress":"In Progress","st_waiting":"Waiting on Customer","st_escalated":"Escalated","st_onhold":"On Hold"}
TK_PRI  = {"pri_critical":"Critical","pri_high":"High","pri_medium":"Medium","pri_low":"Low"}
TK_MODE = {"mode_email":"Email","mode_phone":"Phone","mode_whatsapp":"WhatsApp","mode_chat":"Chat","mode_walkin":"Walk-in/Manual"}
CL_ST   = {"st_scheduled":"Scheduled","st_missed":"Missed","st_ongoing":"Ongoing","st_completed":"Completed"}
MSG_CH  = {"ch_whatsapp":"WhatsApp","ch_email":"Email","ch_sms":"SMS","ch_inapp":"In-App"}
ACT_TYPE = {
    "type_call":"Call","type_meeting":"Meeting","type_demo":"Demo",
    "type_email":"Email","type_followup":"Follow Up","type_sitevisit":"Site Visit",
}
BUG_SEV  = {"sev_critical":"Critical","sev_major":"Major","sev_minor":"Minor","sev_trivial":"Trivial"}
LOST_RSN = {"r_price":"Price","r_competition":"Competition","r_noneed":"No Need","r_timeline":"Timeline","r_noresponse":"No Response","r_other":"Other"}
ACT_NH_RSN = {"r_cancelled":"Cancelled","r_noshow":"No Show","r_rescheduled":"Rescheduled","r_unavailable":"Client Unavailable"}
DEAD_RSN   = {"r_notinterested":"Not Interested","r_nobudget":"No Budget","r_duplicate":"Duplicate","r_wrongnumber":"Wrong Number","r_other":"Other"}
MOD_MAP    = {"mod_lead":"Lead","mod_opportunity":"Opportunity","mod_crm_activity":"CRM Activity","mod_project":"Project","mod_issue":"Issue","mod_crm_call_log":"CRM Call Log"}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — LIVE DATA FETCH  (no underscore variable names)
# ══════════════════════════════════════════════════════════════════════════════

df_lead = []
df_opp  = []
df_act  = []
df_call = []
df_msg  = []
df_tkt  = []
df_proj = []
df_task = []

if tab != "OPEN" and date_from and date_to:
    df_lead = [["creation",    "between", [date_from, date_to]]]
    df_opp  = [["creation",    "between", [date_from, date_to]]]
    df_act  = [["due_date",    "between", [date_from, date_to]]]
    df_call = [["creation",    "between", [date_from, date_to]]]
    df_msg  = [["creation",    "between", [date_from, date_to]]]
    df_tkt  = [["opening_date","between", [date_from, date_to]]]
    df_proj = [["creation",    "between", [date_from, date_to]]]
    df_task = [["creation",    "between", [date_from, date_to]]]
elif tab != "OPEN":
    mth_start = str(frappe.utils.get_first_day(today))
    mth_end   = str(frappe.utils.get_last_day(today))
    df_lead = [["creation",    "between", [mth_start, mth_end]]]
    df_opp  = [["creation",    "between", [mth_start, mth_end]]]
    df_act  = [["due_date",    "between", [mth_start, mth_end]]]
    df_call = [["creation",    "between", [mth_start, mth_end]]]
    df_msg  = [["creation",    "between", [mth_start, mth_end]]]
    df_tkt  = [["opening_date","between", [mth_start, mth_end]]]
    df_proj = [["creation",    "between", [mth_start, mth_end]]]
    df_task = [["creation",    "between", [mth_start, mth_end]]]

# ── LEADS ──────────────────────────────────────────────────────────────────────
LIVE_LEADS_ALL = safe_get_list("Lead",
    filters=df_lead,
    fields=["name","lead_name","company","source","status","lead_owner",
            "creation","contact_date","city","lead_value","modified"],
    limit=1000)
for row in LIVE_LEADS_ALL:
    cre_date = str(row.get("creation","") or "")[:10]
    mod_date = str(row.get("modified","") or "")[:10]
    row["converted_on"]    = mod_date
    row["days_to_convert"] = frappe.utils.date_diff(mod_date, cre_date) if cre_date and mod_date else 0
    row["opp_value"]       = row.get("lead_value", 0) or 0
    row["dead_date"]       = mod_date
    row["dead_reason"]     = ""

LIVE_LEADS      = df_not_in(LIVE_LEADS_ALL, "status", ["Converted","Dead","Junk"])
LIVE_LEADS_CONV = df_eq(LIVE_LEADS_ALL, "status", "Converted")
LIVE_LEADS_DEAD = df_in(LIVE_LEADS_ALL, "status", ["Dead","Junk","Not Interested"])

# ── OPPORTUNITIES ──────────────────────────────────────────────────────────────
LIVE_OPP_ALL = safe_get_list("Opportunity",
    filters=df_opp,
    fields=["name","opportunity_from as customer","opportunity_owner",
            "opportunity_amount","sales_stage","status",
            "expected_closing","probability","source","lost_reason","competitor","creation"],
    limit=1000)
for row in LIVE_OPP_ALL:
    row["opportunity_name"] = row.get("name","")
    cre2 = str(row.get("creation","") or "")[:10]
    cls2 = str(row.get("expected_closing","") or "")
    row["days_to_close"] = frappe.utils.date_diff(cls2, cre2) if cre2 and cls2 else 0

LIVE_OPP      = df_not_in(LIVE_OPP_ALL, "status", ["Closed Won","Closed Lost"])
LIVE_OPP_WON  = df_eq(LIVE_OPP_ALL, "status", "Closed Won")
LIVE_OPP_LOST = df_eq(LIVE_OPP_ALL, "status", "Closed Lost")

# ── CRM ACTIVITIES ─────────────────────────────────────────────────────────────
LIVE_ACTIVITIES = safe_get_list("CRM Activity",
    filters=df_act,
    fields=["name","subject","activity_type","status","assigned_to",
            "due_date","reference_doctype","reference_name","priority","notes","modified"],
    limit=1000, order_by="due_date asc")
for row in LIVE_ACTIVITIES:
    due_str = str(row.get("due_date","") or "")
    row["days_overdue"]   = frappe.utils.date_diff(today, due_str) if due_str and due_str < today else 0
    row["scheduled_time"] = ""
    row["cancel_reason"]  = ""
    row["completed_on"]   = str(row.get("modified","") or "")[:10] if row.get("status") == "Completed" else ""
    row["linked_amount"]  = 0

# ── CRM CALLS ──────────────────────────────────────────────────────────────────
LIVE_CALLS = safe_get_list("CRM Call Log",
    filters=df_call,
    fields=["name","id as subject","from as caller","to as receiver",
            "type as direction","status","duration","creation",
            "reference_docname as reference_name"],
    limit=1000)
for row in LIVE_CALLS:
    row["duration_fmt"] = fmt_dur(row.get("duration") or 0)
    if not row.get("subject"):
        row["subject"] = "Call - " + str(row.get("caller",""))

# ── COMMUNICATIONS ─────────────────────────────────────────────────────────────
LIVE_MESSAGES = safe_get_list("Communication",
    filters=df_msg + [["communication_type","=","Communication"]],
    fields=["name","communication_medium","sent_or_received as direction",
            "status","sender","recipients","creation","reference_name"],
    limit=1000)
for row in LIVE_MESSAGES:
    row["direction"] = "Outbound" if row.get("direction") == "Sent" else "Inbound"

# ── ISSUES / TICKETS ───────────────────────────────────────────────────────────
LIVE_TICKETS_ALL = safe_get_list("Issue",
    filters=df_tkt,
    fields=["name","subject","customer","raised_by","status","priority",
            "support_type as support_mode","opening_date","resolution_by",
            "resolution_date","resolution_time"],
    limit=1000)
for row in LIVE_TICKETS_ALL:
    row["support_mode"] = row.get("support_mode","") or ""
    res_by = str(row.get("resolution_by","") or "")
    row["sla_status"] = "Breached" if res_by and res_by < today else ("Within SLA" if res_by else "—")
    row["csat"] = ""

LIVE_TICKETS        = df_not_in(LIVE_TICKETS_ALL, "status", ["Resolved","Closed"])
LIVE_TICKETS_CLOSED = df_in(LIVE_TICKETS_ALL,     "status", ["Resolved","Closed"])

# ── BUGS ───────────────────────────────────────────────────────────────────────
LIVE_BUGS = safe_get_list("Issue",
    filters=df_tkt + [["issue_type","=","Bug"]],
    fields=["name","subject","issue_type as bug_module","raised_by",
            "assigned_to","status","opening_date","priority as severity"],
    limit=500)

# ── CUSTOMERS / ACCOUNTS ───────────────────────────────────────────────────────
LIVE_ACCOUNTS = safe_get_list("Customer",
    filters=[],
    fields=["name","customer_name","customer_type","industry",
            "account_manager","territory"],
    limit=1000)
for row in LIVE_ACCOUNTS:
    row["city"]               = ""
    row["last_activity"]      = ""
    row["last_activity_date"] = ""

# ── PROJECTS ───────────────────────────────────────────────────────────────────
LIVE_PROJECTS = safe_get_list("Project",
    filters=df_proj,
    fields=["name","project_name","status","project_manager",
            "expected_start_date","expected_end_date","actual_end_date",
            "percent_complete","customer"],
    limit=500)
for row in LIVE_PROJECTS:
    ae = str(row.get("actual_end_date","") or "")
    ee = str(row.get("expected_end_date","") or "")
    if ae and ee and ae > ee:
        row["delay_days"] = frappe.utils.date_diff(ae, ee)
    elif not ae and ee and ee < today:
        row["delay_days"] = frappe.utils.date_diff(today, ee)
    else:
        row["delay_days"] = 0

# ── TASKS ──────────────────────────────────────────────────────────────────────
LIVE_TASKS = safe_get_list("Task",
    filters=df_task,
    fields=["name","subject","project","status","priority",
            "exp_start_date","exp_end_date","assigned_to"],
    limit=1000)

# ── CONTACTS ───────────────────────────────────────────────────────────────────
LIVE_CONTACTS = safe_get_list("Contact",
    filters=[],
    fields=["name","full_name","company_name","mobile_no","email_id","owner"],
    limit=1000)
for row in LIVE_CONTACTS:
    row["contact_type"]       = "Contact"
    row["last_activity"]      = ""
    row["last_activity_date"] = ""

# ── Resolve linked_amount on activities ────────────────────────────────────────
opp_amt_map  = {}
for ox in LIVE_OPP_ALL:
    opp_amt_map[ox.get("name","")] = ox.get("opportunity_amount",0)
lead_val_map = {}
for lx in LIVE_LEADS_ALL:
    lead_val_map[lx.get("name","")] = lx.get("lead_value",0)
for ax in LIVE_ACTIVITIES:
    if ax.get("reference_doctype") == "Opportunity":
        ax["linked_amount"] = opp_amt_map.get(ax.get("reference_name",""), 0)
    elif ax.get("reference_doctype") == "Lead":
        ax["linked_amount"] = lead_val_map.get(ax.get("reference_name",""), 0)

# ── Derived subsets ────────────────────────────────────────────────────────────
overdue_acts = [x for x in LIVE_ACTIVITIES if x.get("status") not in ["Completed","Cancelled"] and x.get("due_date") and str(x.get("due_date","")) < today]
today_acts   = [x for x in LIVE_ACTIVITIES if str(x.get("due_date","") or "") == today]
open_leads   = LIVE_LEADS
open_opps    = LIVE_OPP
open_acts    = df_not_in(LIVE_ACTIVITIES, "status", ["Completed","Cancelled"])
open_tks     = LIVE_TICKETS
open_calls   = df_in(LIVE_CALLS, "status", ["Scheduled","Missed"])
comp_acts    = df_eq(LIVE_ACTIVITIES, "status", "Completed")
canc_acts    = df_eq(LIVE_ACTIVITIES, "status", "Cancelled")
comp_calls   = df_eq(LIVE_CALLS, "status", "Completed")
comp_projs   = df_eq(LIVE_PROJECTS, "status", "Completed")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Row-filter functions
# ══════════════════════════════════════════════════════════════════════════════

def rows_open(k, sf, uf):
    rd = {"rows":[], "uf":"owner", "clr":"#555", "icon":"📊"}
    if k == "overdue_activities":
        rd["rows"] = list(overdue_acts)
        if sf in MOD_MAP:
            rd["rows"] = df_eq(rd["rows"], "reference_doctype", MOD_MAP[sf])
        rd["uf"] = "assigned_to"; rd["clr"] = "#E53935"; rd["icon"] = "⚠️"
    elif k == "todays_activities":
        rd["rows"] = list(today_acts)
        if sf in MOD_MAP:
            rd["rows"] = df_eq(rd["rows"], "reference_doctype", MOD_MAP[sf])
        rd["uf"] = "assigned_to"; rd["clr"] = "#1E88E5"; rd["icon"] = "📅"
    elif k == "leads":
        rd["rows"] = list(open_leads)
        if sf in LD_ST:
            rd["rows"] = df_eq(rd["rows"], "status", LD_ST[sf])
        elif sf == "src_digital":
            rd["rows"] = df_in(rd["rows"], "source", ["Website","Social Media"])
        elif sf == "src_referral":
            rd["rows"] = df_in(rd["rows"], "source", ["Referral","Reference"])
        elif sf == "src_direct":
            rd["rows"] = df_in(rd["rows"], "source", ["Cold Call","Trade Show","Walk-in"])
        elif sf == "src_others":
            rd["rows"] = df_in(rd["rows"], "source", ["Campaign","Unknown"])
        rd["uf"] = "lead_owner"; rd["clr"] = "#43A047"; rd["icon"] = "👤"
    elif k == "opportunities":
        rd["rows"] = list(open_opps)
        if sf in OPP_FK:
            rd["rows"] = df_eq(rd["rows"], "sales_stage", OPP_FK[sf])
        elif sf == "cd_overdue":
            rd["rows"] = df_lt(rd["rows"], "expected_closing", today)
        elif sf == "cd_today":
            rd["rows"] = df_eq(rd["rows"], "expected_closing", today)
        elif sf == "cd_month":
            lm = str(frappe.utils.get_last_day(today))
            rd["rows"] = [x for x in rd["rows"] if x.get("expected_closing","") > today and x.get("expected_closing","") <= lm]
        elif sf == "cd_future":
            lm2 = str(frappe.utils.get_last_day(today))
            rd["rows"] = [x for x in rd["rows"] if x.get("expected_closing","") > lm2]
        elif sf == "amt_lt1l":
            rd["rows"] = [x for x in rd["rows"] if x.get("opportunity_amount",0) < 100000]
        elif sf == "amt_1_5l":
            rd["rows"] = [x for x in rd["rows"] if 100000 <= x.get("opportunity_amount",0) < 500000]
        elif sf == "amt_5_25l":
            rd["rows"] = [x for x in rd["rows"] if 500000 <= x.get("opportunity_amount",0) < 2500000]
        elif sf == "amt_gt25l":
            rd["rows"] = [x for x in rd["rows"] if x.get("opportunity_amount",0) >= 2500000]
        rd["uf"] = "opportunity_owner"; rd["clr"] = "#8E24AA"; rd["icon"] = "💼"
    elif k == "contacts":
        rd["rows"] = list(LIVE_CONTACTS)
        if sf.startswith("ct_"):
            rd["rows"] = df_eq(rd["rows"], "contact_type", sf[3:].title())
        elif sf == "stale_7d":
            cutoff = str(frappe.utils.add_days(today, -7))
            rd["rows"] = [x for x in rd["rows"] if not x.get("last_activity_date") or x.get("last_activity_date","") < cutoff]
        elif sf == "stale_30d":
            cutoff = str(frappe.utils.add_days(today, -30))
            rd["rows"] = [x for x in rd["rows"] if not x.get("last_activity_date") or x.get("last_activity_date","") < cutoff]
        rd["uf"] = "owner"; rd["clr"] = "#F4511E"; rd["icon"] = "📇"
    elif k == "activities":
        rd["rows"] = list(open_acts)
        if sf in ACT_TYPE:
            rd["rows"] = df_eq(rd["rows"], "activity_type", ACT_TYPE[sf])
        elif sf == "ast_open":
            rd["rows"] = df_eq(rd["rows"], "status", "Open")
        elif sf == "ast_planned":
            rd["rows"] = df_in(rd["rows"], "status", ["Planned"])
        elif sf == "ast_overdue":
            rd["rows"] = [x for x in rd["rows"] if x.get("due_date") and str(x.get("due_date","")) < today]
        rd["uf"] = "assigned_to"; rd["clr"] = "#00ACC1"; rd["icon"] = "🎯"
    elif k == "calls":
        rd["rows"] = list(open_calls)
        if sf in CL_ST:
            rd["rows"] = df_eq(rd["rows"], "status", CL_ST[sf])
        elif sf == "dir_inbound":
            rd["rows"] = df_eq(rd["rows"], "direction", "Inbound")
        elif sf == "dir_outbound":
            rd["rows"] = df_eq(rd["rows"], "direction", "Outbound")
        elif sf.startswith("dur_"):
            rd["rows"] = [x for x in rd["rows"] if dur_bucket(x.get("duration",0)) == sf]
        rd["uf"] = "caller"; rd["clr"] = "#3949AB"; rd["icon"] = "📞"
    elif k == "messages":
        rd["rows"] = list(LIVE_MESSAGES)
        if sf in MSG_CH:
            rd["rows"] = df_eq(rd["rows"], "communication_medium", MSG_CH[sf])
        elif sf == "mst_delivered":
            rd["rows"] = df_eq(rd["rows"], "status", "Delivered")
        elif sf == "mst_read":
            rd["rows"] = df_eq(rd["rows"], "status", "Read")
        elif sf == "mst_failed":
            rd["rows"] = df_eq(rd["rows"], "status", "Failed")
        elif sf == "mst_unread":
            rd["rows"] = df_eq(rd["rows"], "status", "Unread")
        rd["uf"] = "sender"; rd["clr"] = "#7CB342"; rd["icon"] = "💬"
    elif k == "tickets":
        rd["rows"] = list(open_tks)
        if sf in TK_ST:
            rd["rows"] = df_eq(rd["rows"], "status", TK_ST[sf])
        elif sf in TK_PRI:
            rd["rows"] = df_eq(rd["rows"], "priority", TK_PRI[sf])
        elif sf in TK_MODE:
            rd["rows"] = df_eq(rd["rows"], "support_mode", TK_MODE[sf])
        elif sf == "sla_breached":
            rd["rows"] = df_eq(rd["rows"], "sla_status", "Breached")
        elif sf == "sla_atrisk":
            rd["rows"] = df_eq(rd["rows"], "sla_status", "At Risk")
        elif sf == "sla_ok":
            rd["rows"] = df_eq(rd["rows"], "sla_status", "Within SLA")
        rd["uf"] = "raised_by"; rd["clr"] = "#C62828"; rd["icon"] = "🎫"
    elif k == "accounts":
        rd["rows"] = list(LIVE_ACCOUNTS)
        if sf == "at_company":
            rd["rows"] = df_eq(rd["rows"], "customer_type", "Company")
        elif sf == "at_prospect":
            rd["rows"] = df_eq(rd["rows"], "customer_type", "Prospect")
        elif sf == "at_partner":
            rd["rows"] = df_eq(rd["rows"], "customer_type", "Partner")
        elif sf.startswith("ind_"):
            ind_lc = sf[4:].replace("_"," ").lower()
            rd["rows"] = [x for x in rd["rows"] if x.get("industry","").lower() == ind_lc]
        rd["uf"] = "account_manager"; rd["clr"] = "#5E35B1"; rd["icon"] = "🏢"
    if uf:
        rd["rows"] = df_user(rd["rows"], rd["uf"], uf)
    return rd


def rows_periodic(k, sf, uf):
    rd = {"rows":[], "uf":"owner", "clr":"#555", "icon":"📊", "cols":[], "title":"Records"}
    if k == "lc":
        rd["rows"] = list(LIVE_LEADS_ALL)
        if sf in LD_ST:
            rd["rows"] = df_eq(rd["rows"], "status", LD_ST[sf])
        elif sf == "src_digital":
            rd["rows"] = df_in(rd["rows"], "source", ["Website","Social Media"])
        elif sf == "src_referral":
            rd["rows"] = df_in(rd["rows"], "source", ["Referral","Reference"])
        elif sf == "src_direct":
            rd["rows"] = df_in(rd["rows"], "source", ["Cold Call","Trade Show","Walk-in"])
        elif sf == "src_others":
            rd["rows"] = df_in(rd["rows"], "source", ["Campaign","Unknown"])
        rd["uf"] = "lead_owner"; rd["clr"] = "#43A047"; rd["icon"] = "👤"; rd["cols"] = COLS_LEAD; rd["title"] = "Leads Created"
    elif k == "oc":
        rd["rows"] = list(LIVE_OPP_ALL)
        if sf in OPP_FK:
            rd["rows"] = df_eq(rd["rows"], "sales_stage", OPP_FK[sf])
        elif sf == "amt_lt1l":
            rd["rows"] = [x for x in rd["rows"] if x.get("opportunity_amount",0) < 100000]
        elif sf == "amt_1_5l":
            rd["rows"] = [x for x in rd["rows"] if 100000 <= x.get("opportunity_amount",0) < 500000]
        elif sf == "amt_5_25l":
            rd["rows"] = [x for x in rd["rows"] if 500000 <= x.get("opportunity_amount",0) < 2500000]
        elif sf == "amt_gt25l":
            rd["rows"] = [x for x in rd["rows"] if x.get("opportunity_amount",0) >= 2500000]
        rd["uf"] = "opportunity_owner"; rd["clr"] = "#8E24AA"; rd["icon"] = "💼"; rd["cols"] = COLS_OPP; rd["title"] = "Opportunities Created"
    elif k == "as":
        rd["rows"] = list(LIVE_ACTIVITIES)
        if sf in ACT_TYPE:
            rd["rows"] = df_eq(rd["rows"], "activity_type", ACT_TYPE[sf])
        elif sf == "ast_planned":
            rd["rows"] = df_in(rd["rows"], "status", ["Planned"])
        elif sf == "ast_completed":
            rd["rows"] = df_eq(rd["rows"], "status", "Completed")
        elif sf == "ast_overdue":
            rd["rows"] = [x for x in rd["rows"] if x.get("status") not in ["Completed","Cancelled"] and x.get("due_date") and str(x.get("due_date","")) < today]
        rd["uf"] = "assigned_to"; rd["clr"] = "#00ACC1"; rd["icon"] = "🎯"; rd["cols"] = COLS_TODAY_ACT; rd["title"] = "Activities Scheduled"
    elif k == "cp":
        rd["rows"] = list(LIVE_CALLS)
        if sf in CL_ST:
            rd["rows"] = df_eq(rd["rows"], "status", CL_ST[sf])
        elif sf == "dir_inbound":
            rd["rows"] = df_eq(rd["rows"], "direction", "Inbound")
        elif sf == "dir_outbound":
            rd["rows"] = df_eq(rd["rows"], "direction", "Outbound")
        elif sf.startswith("dur_"):
            rd["rows"] = [x for x in rd["rows"] if dur_bucket(x.get("duration",0)) == sf]
        rd["uf"] = "caller"; rd["clr"] = "#3949AB"; rd["icon"] = "📞"; rd["cols"] = COLS_CALL; rd["title"] = "Calls"
    elif k == "mp":
        rd["rows"] = [x for x in LIVE_MESSAGES if x.get("direction") == "Outbound"]
        if sf in MSG_CH:
            rd["rows"] = df_eq(rd["rows"], "communication_medium", MSG_CH[sf])
        elif sf == "mst_delivered":
            rd["rows"] = df_eq(rd["rows"], "status", "Delivered")
        elif sf == "mst_read":
            rd["rows"] = df_eq(rd["rows"], "status", "Read")
        elif sf == "mst_failed":
            rd["rows"] = df_eq(rd["rows"], "status", "Failed")
        rd["uf"] = "sender"; rd["clr"] = "#7CB342"; rd["icon"] = "💬"; rd["cols"] = COLS_MSG; rd["title"] = "Messages Sent"
    elif k == "pj":
        rd["rows"] = list(LIVE_PROJECTS)
        if sf.startswith("pst_"):
            rd["rows"] = df_eq(rd["rows"], "status", sf[4:].title())
        rd["uf"] = "project_manager"; rd["clr"] = "#F4511E"; rd["icon"] = "📁"; rd["cols"] = COLS_PROJ; rd["title"] = "Projects"
    elif k == "pt":
        rd["rows"] = list(LIVE_TASKS)
        if sf.startswith("tst_"):
            rd["rows"] = df_eq(rd["rows"], "status", sf[4:].replace("_"," ").title())
        elif sf.startswith("tpri_"):
            rd["rows"] = df_eq(rd["rows"], "priority", sf[5:].title())
        rd["uf"] = "assigned_to"; rd["clr"] = "#BF360C"; rd["icon"] = "✅"; rd["cols"] = COLS_TASK; rd["title"] = "Project Tasks"
    elif k == "tc":
        rd["rows"] = list(LIVE_TICKETS_ALL)
        if sf in TK_ST:
            rd["rows"] = df_eq(rd["rows"], "status", TK_ST[sf])
        elif sf in TK_PRI:
            rd["rows"] = df_eq(rd["rows"], "priority", TK_PRI[sf])
        elif sf == "sla_breached":
            rd["rows"] = df_eq(rd["rows"], "sla_status", "Breached")
        elif sf == "sla_ok":
            rd["rows"] = df_eq(rd["rows"], "sla_status", "Within SLA")
        rd["uf"] = "raised_by"; rd["clr"] = "#E53935"; rd["icon"] = "🎫"; rd["cols"] = COLS_TICKET; rd["title"] = "Tickets Created"
    elif k == "bg":
        rd["rows"] = list(LIVE_BUGS)
        if sf in BUG_SEV:
            rd["rows"] = df_eq(rd["rows"], "severity", BUG_SEV[sf])
        rd["uf"] = "raised_by"; rd["clr"] = "#880E4F"; rd["icon"] = "🐛"; rd["cols"] = COLS_BUG; rd["title"] = "Bugs / Issues"
    if uf:
        rd["rows"] = df_user(rd["rows"], rd["uf"], uf)
    return rd


def rows_result(k, sf, uf):
    rd = {"rows":[], "uf":"owner", "clr":"#555", "icon":"📊", "cols":[], "title":"Records"}
    if k == "cw":
        rd["rows"] = list(LIVE_OPP_WON)
        if sf.startswith("src_"):
            rd["rows"] = df_eq(rd["rows"], "source", sf[4:].replace("_"," ").title())
        elif sf == "amt_lt1l":
            rd["rows"] = [x for x in rd["rows"] if x.get("opportunity_amount",0) < 100000]
        elif sf == "amt_1_5l":
            rd["rows"] = [x for x in rd["rows"] if 100000 <= x.get("opportunity_amount",0) < 500000]
        elif sf == "amt_5_25l":
            rd["rows"] = [x for x in rd["rows"] if 500000 <= x.get("opportunity_amount",0) < 2500000]
        elif sf == "amt_gt25l":
            rd["rows"] = [x for x in rd["rows"] if x.get("opportunity_amount",0) >= 2500000]
        rd["uf"] = "opportunity_owner"; rd["clr"] = "#2E7D32"; rd["icon"] = "🏆"; rd["cols"] = COLS_WON; rd["title"] = "Closed Won"
    elif k == "cl":
        rd["rows"] = list(LIVE_OPP_LOST)
        if sf in LOST_RSN:
            rd["rows"] = df_eq(rd["rows"], "lost_reason", LOST_RSN[sf])
        rd["uf"] = "opportunity_owner"; rd["clr"] = "#C62828"; rd["icon"] = "❌"; rd["cols"] = COLS_LOST; rd["title"] = "Closed Lost"
    elif k == "ac":
        rd["rows"] = list(comp_acts)
        if sf in ACT_TYPE:
            rd["rows"] = df_eq(rd["rows"], "activity_type", ACT_TYPE[sf])
        rd["uf"] = "assigned_to"; rd["clr"] = "#00695C"; rd["icon"] = "✅"; rd["cols"] = COLS_ACT_COMP; rd["title"] = "Activities Completed"
    elif k == "nh":
        rd["rows"] = list(canc_acts)
        if sf in ACT_TYPE:
            rd["rows"] = df_eq(rd["rows"], "activity_type", ACT_TYPE[sf])
        elif sf in ACT_NH_RSN:
            rd["rows"] = df_eq(rd["rows"], "cancel_reason", ACT_NH_RSN[sf])
        rd["uf"] = "assigned_to"; rd["clr"] = "#880E4F"; rd["icon"] = "🚫"; rd["cols"] = COLS_ACT_NH; rd["title"] = "Activities Not Held"
    elif k == "tk":
        rd["rows"] = list(LIVE_TICKETS_CLOSED)
        if sf in TK_PRI:
            rd["rows"] = df_eq(rd["rows"], "priority", TK_PRI[sf])
        elif sf == "sla_breached":
            rd["rows"] = df_eq(rd["rows"], "sla_status", "Breached")
        elif sf == "sla_ok":
            rd["rows"] = df_eq(rd["rows"], "sla_status", "Within SLA")
        rd["uf"] = "raised_by"; rd["clr"] = "#1565C0"; rd["icon"] = "🔒"; rd["cols"] = COLS_TKT_CLOSED; rd["title"] = "Tickets Closed"
    elif k == "lv":
        rd["rows"] = list(LIVE_LEADS_CONV)
        if sf.startswith("src_"):
            rd["rows"] = df_eq(rd["rows"], "source", sf[4:].replace("_"," ").title())
        rd["uf"] = "lead_owner"; rd["clr"] = "#2E7D32"; rd["icon"] = "🔄"; rd["cols"] = COLS_LEAD_CONV; rd["title"] = "Leads Converted"
    elif k == "ld":
        rd["rows"] = list(LIVE_LEADS_DEAD)
        if sf in DEAD_RSN:
            rd["rows"] = df_eq(rd["rows"], "dead_reason", DEAD_RSN[sf])
        rd["uf"] = "lead_owner"; rd["clr"] = "#C62828"; rd["icon"] = "💀"; rd["cols"] = COLS_LEAD_DEAD; rd["title"] = "Leads Dead / Lost"
    elif k == "cc":
        rd["rows"] = list(comp_calls)
        if sf == "dir_inbound":
            rd["rows"] = df_eq(rd["rows"], "direction", "Inbound")
        elif sf == "dir_outbound":
            rd["rows"] = df_eq(rd["rows"], "direction", "Outbound")
        elif sf.startswith("dur_"):
            rd["rows"] = [x for x in rd["rows"] if dur_bucket(x.get("duration",0)) == sf]
        rd["uf"] = "caller"; rd["clr"] = "#1565C0"; rd["icon"] = "📲"; rd["cols"] = COLS_CALL_COMP; rd["title"] = "Calls Completed"
    elif k == "pc":
        rd["rows"] = list(comp_projs)
        if sf == "pc_ontime":
            rd["rows"] = [x for x in rd["rows"] if x.get("delay_days",0) <= 0]
        elif sf == "pc_delayed":
            rd["rows"] = [x for x in rd["rows"] if x.get("delay_days",0) > 0]
        rd["uf"] = "project_manager"; rd["clr"] = "#E65100"; rd["icon"] = "🏁"; rd["cols"] = COLS_PROJ_COMP; rd["title"] = "Projects Completed"
    if uf:
        rd["rows"] = df_user(rd["rows"], rd["uf"], uf)
    return rd

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Main routing
# ══════════════════════════════════════════════════════════════════════════════

if tab == "OPEN":

    if action == "summary":
        out = {"cards":[
            {"key":"overdue_activities","label":"Overdue Activities","count":len(overdue_acts),"color":"#E53935","icon":"⚠️","has_drill":True,"amount":sum_field(overdue_acts,"linked_amount")},
            {"key":"todays_activities", "label":"Today's Activities","count":len(today_acts),  "color":"#1E88E5","icon":"📅","has_drill":True,"amount":sum_field(today_acts,"linked_amount")},
            {"key":"leads",             "label":"Leads",             "count":len(open_leads),  "color":"#43A047","icon":"👤","has_drill":True,"amount":sum_field(open_leads,"lead_value")},
            {"key":"opportunities",     "label":"Opportunities",     "count":len(open_opps),   "color":"#8E24AA","icon":"💼","has_drill":True,"amount":sum_field(open_opps,"opportunity_amount")},
            {"key":"contacts",          "label":"Contacts",          "count":len(LIVE_CONTACTS),"color":"#F4511E","icon":"📇","has_drill":True},
            {"key":"activities",        "label":"Activities",        "count":len(open_acts),   "color":"#00ACC1","icon":"🎯","has_drill":True,"amount":sum_field(open_acts,"linked_amount")},
            {"key":"calls",             "label":"Calls",             "count":len(open_calls),  "color":"#3949AB","icon":"📞","has_drill":True},
            {"key":"messages",          "label":"Messages",          "count":len(LIVE_MESSAGES),"color":"#7CB342","icon":"💬","has_drill":True},
            {"key":"tickets",           "label":"Tickets",           "count":len(open_tks),    "color":"#C62828","icon":"🎫","has_drill":True},
            {"key":"accounts",          "label":"Accounts",          "count":len(LIVE_ACCOUNTS),"color":"#5E35B1","icon":"🏢","has_drill":True},
        ]}

    elif action == "drill":
        if kpi_key == "overdue_activities":
            mods = [["Lead","Leads","👤"],["Opportunity","Opportunities","💼"],["Issue","Tickets","🎫"],["Project","Projects","📁"]]
            gc = []
            for m in mods:
                m_rows = df_eq(overdue_acts,"reference_doctype",m[0])
                gc.append(seg_card("overdue_activities",m[1],len(m_rows),"#E53935",m[2],"mod_"+m[0].lower(),amt=sum_field(m_rows,"linked_amount")))
            out = make_drill([{"label":"By Module","cards":gc}], overdue_acts,"assigned_to","overdue_activities","#E53935","⚠️","all",amt_field="linked_amount")
        elif kpi_key == "todays_activities":
            mods2 = [["Lead","Leads","👤"],["Opportunity","Opportunities","💼"],["Issue","Tickets","🎫"]]
            gc2 = []
            for m2 in mods2:
                m2_rows = df_eq(today_acts,"reference_doctype",m2[0])
                gc2.append(seg_card("todays_activities",m2[1],len(m2_rows),"#1E88E5",m2[2],"mod_"+m2[0].lower(),amt=sum_field(m2_rows,"linked_amount")))
            out = make_drill([{"label":"By Module","cards":gc2}], today_acts,"assigned_to","todays_activities","#1E88E5","📅","all",amt_field="linked_amount")
        elif kpi_key == "leads":
            st_clr = {"st_new":"#1E88E5","st_contacted":"#43A047","st_follow_up":"#FB8C00","st_interested":"#8E24AA","st_not_interested":"#E53935","st_junk":"#757575"}
            sc = []
            for fk in LD_ST:
                fk_rows = df_eq(open_leads,"status",LD_ST[fk])
                sc.append(seg_card("leads",LD_ST[fk],len(fk_rows),st_clr.get(fk,"#555"),"👤",fk,amt=sum_field(fk_rows,"lead_value")))
            src_map = {"src_digital":["Website","Social Media"],"src_referral":["Referral","Reference"],"src_direct":["Cold Call","Trade Show"],"src_others":["Campaign"]}
            src_c = []
            for sfk in src_map:
                sfk_rows = df_in(open_leads,"source",src_map[sfk])
                src_c.append(seg_card("leads",sfk.replace("src_","").replace("_"," ").title(),len(sfk_rows),"#43A047","🌐",sfk,amt=sum_field(sfk_rows,"lead_value")))
            out = make_drill([{"label":"By Status","cards":sc},{"label":"By Source","cards":src_c}], open_leads,"lead_owner","leads","#43A047","👤","all",amt_field="lead_value")
        elif kpi_key == "opportunities":
            ld2 = str(frappe.utils.get_last_day(today))
            ov_rows = df_lt(open_opps,"expected_closing",today)
            td_rows = df_eq(open_opps,"expected_closing",today)
            mo_rows = [x for x in open_opps if x.get("expected_closing","") > today and x.get("expected_closing","") <= ld2]
            fu_rows = [x for x in open_opps if x.get("expected_closing","") > ld2]
            nd_rows = [x for x in open_opps if not x.get("expected_closing")]
            dc = [
                seg_card("opportunities","Overdue",       len(ov_rows),"#E53935","💼","cd_overdue",amt=sum_field(ov_rows,"opportunity_amount")),
                seg_card("opportunities","Due Today",      len(td_rows),"#FB8C00","💼","cd_today",  amt=sum_field(td_rows,"opportunity_amount")),
                seg_card("opportunities","Due This Month", len(mo_rows),"#8E24AA","💼","cd_month",  amt=sum_field(mo_rows,"opportunity_amount")),
                seg_card("opportunities","Future",         len(fu_rows),"#43A047","💼","cd_future", amt=sum_field(fu_rows,"opportunity_amount")),
                seg_card("opportunities","No Close Date",  len(nd_rows),"#757575","💼","cd_nodate", amt=sum_field(nd_rows,"opportunity_amount")),
            ]
            sc_clr = {"st_prospecting":"#1E88E5","st_qualification":"#8E24AA","st_demo":"#FB8C00","st_proposal":"#43A047","st_negotiation":"#E65100","st_commit":"#2E7D32"}
            stc = []
            for sfk2 in OPP_FK:
                sfk2_rows = df_eq(open_opps,"sales_stage",OPP_FK[sfk2])
                stc.append(seg_card("opportunities",OPP_FK[sfk2],len(sfk2_rows),sc_clr.get(sfk2,"#555"),"💼",sfk2,amt=sum_field(sfk2_rows,"opportunity_amount")))
            o1 = [x for x in open_opps if x.get("opportunity_amount",0) < 100000]
            o2 = [x for x in open_opps if 100000 <= x.get("opportunity_amount",0) < 500000]
            o3 = [x for x in open_opps if 500000 <= x.get("opportunity_amount",0) < 2500000]
            o4 = [x for x in open_opps if x.get("opportunity_amount",0) >= 2500000]
            amc = [
                seg_card("opportunities","< ₹1L", len(o1),"#757575","💰","amt_lt1l",amt=sum_field(o1,"opportunity_amount")),
                seg_card("opportunities","₹1-5L", len(o2),"#1E88E5","💰","amt_1_5l",amt=sum_field(o2,"opportunity_amount")),
                seg_card("opportunities","₹5-25L",len(o3),"#8E24AA","💰","amt_5_25l",amt=sum_field(o3,"opportunity_amount")),
                seg_card("opportunities","₹25L+", len(o4),"#2E7D32","💰","amt_gt25l",amt=sum_field(o4,"opportunity_amount")),
            ]
            out = make_drill([{"label":"By Close Date","cards":dc},{"label":"By Stage","cards":stc},{"label":"By Amount","cards":amc}], open_opps,"opportunity_owner","opportunities","#8E24AA","💼","all",amt_field="opportunity_amount")
        elif kpi_key == "contacts":
            tc2 = [
                seg_card("contacts","Customer",len(df_eq(LIVE_CONTACTS,"contact_type","Customer")),"#1E88E5","📇","ct_customer"),
                seg_card("contacts","Prospect", len(df_eq(LIVE_CONTACTS,"contact_type","Prospect")),"#43A047","📇","ct_prospect"),
                seg_card("contacts","Partner",  len(df_eq(LIVE_CONTACTS,"contact_type","Partner")), "#8E24AA","📇","ct_partner"),
            ]
            s7cut  = str(frappe.utils.add_days(today, -7))
            s30cut = str(frappe.utils.add_days(today, -30))
            stale7  = [x for x in LIVE_CONTACTS if not x.get("last_activity_date") or x.get("last_activity_date","") < s7cut]
            stale30 = [x for x in LIVE_CONTACTS if not x.get("last_activity_date") or x.get("last_activity_date","") < s30cut]
            ac2 = [
                seg_card("contacts","No activity >7d", len(stale7), "#F4511E","📇","stale_7d","table"),
                seg_card("contacts","No activity >30d",len(stale30),"#E53935","📇","stale_30d","table"),
            ]
            out = make_drill([{"label":"By Type","cards":tc2},{"label":"By Activity","cards":ac2}], LIVE_CONTACTS,"owner","contacts","#F4511E","📇","all")
        elif kpi_key == "activities":
            at_clr = {"type_call":"#3949AB","type_meeting":"#1E88E5","type_demo":"#8E24AA","type_email":"#7CB342","type_followup":"#FB8C00","type_sitevisit":"#00ACC1"}
            tyc = []
            for afk in ACT_TYPE:
                afk_rows = df_eq(open_acts,"activity_type",ACT_TYPE[afk])
                tyc.append(seg_card("activities",ACT_TYPE[afk],len(afk_rows),at_clr.get(afk,"#555"),"🎯",afk,amt=sum_field(afk_rows,"linked_amount")))
            op_rows  = df_eq(open_acts,"status","Open")
            pl_rows  = df_in(open_acts,"status",["Planned"])
            nd_rows2 = [x for x in open_acts if not x.get("due_date")]
            stc2 = [
                seg_card("activities","Open",       len(op_rows), "#1E88E5","🎯","ast_open",   amt=sum_field(op_rows,"linked_amount")),
                seg_card("activities","Planned",    len(pl_rows), "#8E24AA","🎯","ast_planned",amt=sum_field(pl_rows,"linked_amount")),
                seg_card("activities","No Due Date",len(nd_rows2),"#757575","🎯","ast_nodue",  amt=sum_field(nd_rows2,"linked_amount")),
            ]
            duec = [seg_card("activities","Overdue",len(overdue_acts),"#E53935","🎯","ast_overdue",amt=sum_field(overdue_acts,"linked_amount"))]
            out = make_drill([{"label":"By Type","cards":tyc},{"label":"By Status","cards":stc2},{"label":"By Due Date","cards":duec}], open_acts,"assigned_to","activities","#00ACC1","🎯","all",amt_field="linked_amount")
        elif kpi_key == "calls":
            csc = [
                seg_card("calls","Scheduled",len(df_eq(open_calls,"status","Scheduled")),"#1E88E5","📞","st_scheduled"),
                seg_card("calls","Missed",   len(df_eq(open_calls,"status","Missed")),   "#E53935","📞","st_missed"),
            ]
            cdir = [
                seg_card("calls","Inbound", len(df_eq(open_calls,"direction","Inbound")), "#43A047","📞","dir_inbound"),
                seg_card("calls","Outbound",len(df_eq(open_calls,"direction","Outbound")),"#3949AB","📞","dir_outbound"),
            ]
            out = make_drill([{"label":"By Status","cards":csc},{"label":"By Direction","cards":cdir}], open_calls,"caller","calls","#3949AB","📞","all")
        elif kpi_key == "messages":
            ch_clr = {"ch_whatsapp":"#43A047","ch_email":"#1E88E5","ch_sms":"#FB8C00","ch_inapp":"#8E24AA"}
            chc = []
            for cfk in MSG_CH:
                chc.append(seg_card("messages",MSG_CH[cfk],len(df_eq(LIVE_MESSAGES,"communication_medium",MSG_CH[cfk])),ch_clr.get(cfk,"#555"),"💬",cfk))
            mst_c = [
                seg_card("messages","Delivered",len(df_eq(LIVE_MESSAGES,"status","Delivered")),"#43A047","💬","mst_delivered"),
                seg_card("messages","Read",      len(df_eq(LIVE_MESSAGES,"status","Read")),     "#1E88E5","💬","mst_read"),
                seg_card("messages","Failed",    len(df_eq(LIVE_MESSAGES,"status","Failed")),   "#E53935","💬","mst_failed"),
                seg_card("messages","Unread",    len(df_eq(LIVE_MESSAGES,"status","Unread")),   "#FB8C00","💬","mst_unread"),
            ]
            out = make_drill([{"label":"By Channel","cards":chc},{"label":"By Status","cards":mst_c}], LIVE_MESSAGES,"sender","messages","#7CB342","💬","all")
        elif kpi_key == "tickets":
            pr_clr = {"Critical":"#C62828","High":"#E53935","Medium":"#FB8C00","Low":"#43A047"}
            prc = []
            for pr in ["Critical","High","Medium","Low"]:
                prc.append(seg_card("tickets",pr,len(df_eq(open_tks,"priority",pr)),pr_clr.get(pr,"#555"),"🎫","pri_"+pr.lower()))
            stc3 = []
            for fk3 in TK_ST:
                stc3.append(seg_card("tickets",TK_ST[fk3],len(df_eq(open_tks,"status",TK_ST[fk3])),"#C62828","🎫",fk3))
            slac = [
                seg_card("tickets","Breached",  len(df_eq(open_tks,"sla_status","Breached")),  "#C62828","🔴","sla_breached","table"),
                seg_card("tickets","At Risk",   len(df_eq(open_tks,"sla_status","At Risk")),   "#FB8C00","🟡","sla_atrisk","table"),
                seg_card("tickets","Within SLA",len(df_eq(open_tks,"sla_status","Within SLA")),"#43A047","🟢","sla_ok","table"),
            ]
            out = make_drill([{"label":"By Priority","cards":prc},{"label":"By Status","cards":stc3},{"label":"By SLA","cards":slac}], open_tks,"raised_by","tickets","#C62828","🎫","all")
        elif kpi_key == "accounts":
            atc = [
                seg_card("accounts","Company", len(df_eq(LIVE_ACCOUNTS,"customer_type","Company")), "#5E35B1","🏢","at_company"),
                seg_card("accounts","Prospect",len(df_eq(LIVE_ACCOUNTS,"customer_type","Prospect")),"#3949AB","🏢","at_prospect"),
                seg_card("accounts","Partner", len(df_eq(LIVE_ACCOUNTS,"customer_type","Partner")), "#00ACC1","🏢","at_partner"),
            ]
            inds = list(set([x.get("industry","") for x in LIVE_ACCOUNTS if x.get("industry")]))
            inc = []
            for ind in sorted(inds):
                inc.append(seg_card("accounts",ind,len(df_eq(LIVE_ACCOUNTS,"industry",ind)),"#5E35B1","🏢","ind_"+ind.lower().replace(" ","_")))
            out = make_drill([{"label":"By Type","cards":atc},{"label":"By Industry","cards":inc}], LIVE_ACCOUNTS,"account_manager","accounts","#5E35B1","🏢","all")
        else:
            out = {"groups":[],"user_cards":[]}

    elif action == "userwise":
        rd_uw = rows_open(kpi_key, sub_filter, "")
        out = {"cards": make_uw_cards(kpi_key, rd_uw["rows"], rd_uw["uf"], rd_uw["clr"], rd_uw["icon"], sub_filter)}

    elif action == "table":
        rd_tbl = rows_open(kpi_key, sub_filter, user_filter)
        col_map = {
            "overdue_activities":COLS_ACT,"todays_activities":COLS_TODAY_ACT,
            "leads":COLS_LEAD,"opportunities":COLS_OPP,"contacts":COLS_CONTACT,
            "activities":COLS_TODAY_ACT,"calls":COLS_CALL,"messages":COLS_MSG,
            "tickets":COLS_TICKET,"accounts":COLS_ACCOUNT,
        }
        title_map = {
            "overdue_activities":"Overdue Activities","todays_activities":"Today's Activities",
            "leads":"Leads","opportunities":"Opportunities","contacts":"Contacts",
            "activities":"Activities","calls":"Calls","messages":"Messages",
            "tickets":"Tickets","accounts":"Accounts",
        }
        out = live_tbl(rd_tbl["rows"], col_map.get(kpi_key,[]), title_map.get(kpi_key,"Records"))
    else:
        out = {"cards":[]}

elif tab == "PERIODIC":

    if action == "summary":
        out = {"cards":[
            {"key":"lc","label":"Leads Created",       "count":len(LIVE_LEADS_ALL),  "color":"#43A047","icon":"👤","has_drill":True,"amount":sum_field(LIVE_LEADS_ALL,"lead_value")},
            {"key":"oc","label":"Opportunities Created","count":len(LIVE_OPP_ALL),   "color":"#8E24AA","icon":"💼","has_drill":True,"amount":sum_field(LIVE_OPP_ALL,"opportunity_amount")},
            {"key":"as","label":"Activities Scheduled", "count":len(LIVE_ACTIVITIES),"color":"#00ACC1","icon":"🎯","has_drill":True},
            {"key":"cp","label":"Calls",                "count":len(LIVE_CALLS),     "color":"#3949AB","icon":"📞","has_drill":True},
            {"key":"mp","label":"Messages Sent",        "count":len([x for x in LIVE_MESSAGES if x.get("direction")=="Outbound"]),"color":"#7CB342","icon":"💬","has_drill":True},
            {"key":"pj","label":"Projects",             "count":len(LIVE_PROJECTS),  "color":"#F4511E","icon":"📁","has_drill":True},
            {"key":"pt","label":"Project Tasks",        "count":len(LIVE_TASKS),     "color":"#BF360C","icon":"✅","has_drill":True},
            {"key":"tc","label":"Tickets Created",      "count":len(LIVE_TICKETS_ALL),"color":"#E53935","icon":"🎫","has_drill":True},
            {"key":"bg","label":"Bugs / Issues",        "count":len(LIVE_BUGS),      "color":"#880E4F","icon":"🐛","has_drill":True},
        ]}

    elif action == "drill":
        rd_p = rows_periodic(kpi_key, "", "")
        grps_p = []
        if kpi_key == "lc":
            sc_p = []
            for fk_p in LD_ST:
                fkp_rows = df_eq(LIVE_LEADS_ALL,"status",LD_ST[fk_p])
                sc_p.append(seg_card("lc",LD_ST[fk_p],len(fkp_rows),"#43A047","👤",fk_p,amt=sum_field(fkp_rows,"lead_value")))
            dig_rows = df_in(LIVE_LEADS_ALL,"source",["Website","Social Media"])
            ref_rows = df_in(LIVE_LEADS_ALL,"source",["Referral","Reference"])
            dir_rows = df_in(LIVE_LEADS_ALL,"source",["Cold Call","Trade Show","Walk-in"])
            oth_rows = df_in(LIVE_LEADS_ALL,"source",["Campaign","Unknown"])
            src_p = [
                seg_card("lc","Digital", len(dig_rows),"#43A047","🌐","src_digital", amt=sum_field(dig_rows,"lead_value")),
                seg_card("lc","Referral",len(ref_rows),"#2E7D32","🌐","src_referral",amt=sum_field(ref_rows,"lead_value")),
                seg_card("lc","Direct",  len(dir_rows),"#FB8C00","🌐","src_direct",  amt=sum_field(dir_rows,"lead_value")),
                seg_card("lc","Others",  len(oth_rows),"#757575","🌐","src_others",  amt=sum_field(oth_rows,"lead_value")),
            ]
            grps_p = [{"label":"By Status","cards":sc_p},{"label":"By Source","cards":src_p}]
        elif kpi_key == "oc":
            stg_p = []
            for sfk_p in OPP_FK:
                sfkp_rows = df_eq(LIVE_OPP_ALL,"sales_stage",OPP_FK[sfk_p])
                stg_p.append(seg_card("oc",OPP_FK[sfk_p],len(sfkp_rows),"#8E24AA","💼",sfk_p,amt=sum_field(sfkp_rows,"opportunity_amount")))
            grps_p = [{"label":"By Stage","cards":stg_p}]
        elif kpi_key == "as":
            tyc_p = []
            for afk_p in ACT_TYPE:
                tyc_p.append(seg_card("as",ACT_TYPE[afk_p],len(df_eq(LIVE_ACTIVITIES,"activity_type",ACT_TYPE[afk_p])),"#00ACC1","🎯",afk_p))
            stc_p = [
                seg_card("as","Planned",  len(df_in(LIVE_ACTIVITIES,"status",["Planned"])),"#1E88E5","🎯","ast_planned"),
                seg_card("as","Completed",len(df_eq(LIVE_ACTIVITIES,"status","Completed")),"#43A047","🎯","ast_completed"),
                seg_card("as","Overdue",  len([x for x in LIVE_ACTIVITIES if x.get("status") not in ["Completed","Cancelled"] and x.get("due_date") and str(x.get("due_date","")) < today]),"#E53935","🎯","ast_overdue"),
            ]
            grps_p = [{"label":"By Type","cards":tyc_p},{"label":"By Status","cards":stc_p}]
        elif kpi_key == "cp":
            cst_p = []
            for fk_cp in CL_ST:
                cst_p.append(seg_card("cp",CL_ST[fk_cp],len(df_eq(rd_p["rows"],"status",CL_ST[fk_cp])),"#3949AB","📞",fk_cp))
            cdir_p = [
                seg_card("cp","Inbound", len(df_eq(rd_p["rows"],"direction","Inbound")), "#43A047","📞","dir_inbound"),
                seg_card("cp","Outbound",len(df_eq(rd_p["rows"],"direction","Outbound")),"#3949AB","📞","dir_outbound"),
            ]
            grps_p = [{"label":"By Status","cards":cst_p},{"label":"By Direction","cards":cdir_p}]
        elif kpi_key == "mp":
            ch_p = []
            for fk_mp in MSG_CH:
                ch_p.append(seg_card("mp",MSG_CH[fk_mp],len(df_eq(rd_p["rows"],"communication_medium",MSG_CH[fk_mp])),"#7CB342","💬",fk_mp))
            grps_p = [{"label":"By Channel","cards":ch_p}]
        elif kpi_key == "pj":
            pj_stc = [
                seg_card("pj","Open",     len(df_eq(LIVE_PROJECTS,"status","Open")),     "#1E88E5","📁","pst_open"),
                seg_card("pj","Overdue",  len(df_eq(LIVE_PROJECTS,"status","Overdue")),  "#E53935","📁","pst_overdue"),
                seg_card("pj","Completed",len(df_eq(LIVE_PROJECTS,"status","Completed")),"#43A047","📁","pst_completed"),
            ]
            grps_p = [{"label":"By Status","cards":pj_stc}]
        elif kpi_key == "pt":
            pt_stc = [
                seg_card("pt","Open",          len(df_eq(LIVE_TASKS,"status","Open")),          "#1E88E5","✅","tst_open"),
                seg_card("pt","Working",        len(df_eq(LIVE_TASKS,"status","Working")),       "#FB8C00","✅","tst_working"),
                seg_card("pt","Pending Review", len(df_eq(LIVE_TASKS,"status","Pending Review")),"#8E24AA","✅","tst_pending_review"),
            ]
            grps_p = [{"label":"By Status","cards":pt_stc}]
        elif kpi_key == "tc":
            tc_vals = list(set([x.get("status","") for x in LIVE_TICKETS_ALL if x.get("status")]))
            tc_stc = []
            for v_tc in sorted(tc_vals):
                tc_stc.append(seg_card("tc",v_tc,len(df_eq(LIVE_TICKETS_ALL,"status",v_tc)),"#E53935","🎫","st_"+v_tc.lower().replace(" ","_")))
            grps_p = [{"label":"By Status","cards":tc_stc}]
        elif kpi_key == "bg":
            bg_vals = list(set([x.get("severity","") for x in LIVE_BUGS if x.get("severity")]))
            bg_stc = []
            for v_bg in sorted(bg_vals):
                bg_stc.append(seg_card("bg",v_bg,len(df_eq(LIVE_BUGS,"severity",v_bg)),"#880E4F","🐛","sev_"+v_bg.lower()))
            grps_p = [{"label":"By Severity","cards":bg_stc}]
        else:
            grps_p = []
        periodic_amt_map = {"lc":"lead_value","oc":"opportunity_amount"}
        out = make_drill(grps_p, rd_p["rows"], rd_p["uf"], kpi_key, rd_p["clr"], rd_p["icon"], "all", amt_field=periodic_amt_map.get(kpi_key,""))

    elif action == "userwise":
        rd_uw_p = rows_periodic(kpi_key, sub_filter, "")
        periodic_amt_map2 = {"lc":"lead_value","oc":"opportunity_amount"}
        out = {"cards": make_uw_cards(kpi_key, rd_uw_p["rows"], rd_uw_p["uf"], rd_uw_p["clr"], rd_uw_p["icon"], sub_filter, amt_field=periodic_amt_map2.get(kpi_key,""))}

    elif action == "table":
        rd_tbl_p = rows_periodic(kpi_key, sub_filter, user_filter)
        out = live_tbl(rd_tbl_p["rows"], rd_tbl_p["cols"], rd_tbl_p["title"])
    else:
        out = {"cards":[]}

elif tab == "RESULT":

    if action == "summary":
        out = {"cards":[
            {"key":"cw","label":"Closed Won",          "count":len(LIVE_OPP_WON),       "color":"#2E7D32","icon":"🏆","has_drill":True,"amount":sum_field(LIVE_OPP_WON,"opportunity_amount")},
            {"key":"cl","label":"Closed Lost",         "count":len(LIVE_OPP_LOST),      "color":"#C62828","icon":"❌","has_drill":True,"amount":sum_field(LIVE_OPP_LOST,"opportunity_amount")},
            {"key":"ac","label":"Activities Completed","count":len(comp_acts),           "color":"#00695C","icon":"✅","has_drill":True},
            {"key":"nh","label":"Activities Not Held", "count":len(canc_acts),           "color":"#880E4F","icon":"🚫","has_drill":True},
            {"key":"tk","label":"Tickets Closed",      "count":len(LIVE_TICKETS_CLOSED), "color":"#1565C0","icon":"🔒","has_drill":True},
            {"key":"lv","label":"Leads Converted",     "count":len(LIVE_LEADS_CONV),     "color":"#2E7D32","icon":"🔄","has_drill":True},
            {"key":"ld","label":"Leads Dead / Lost",   "count":len(LIVE_LEADS_DEAD),     "color":"#C62828","icon":"💀","has_drill":True},
            {"key":"cc","label":"Calls Completed",     "count":len(comp_calls),          "color":"#1565C0","icon":"📲","has_drill":True},
            {"key":"pc","label":"Projects Completed",  "count":len(comp_projs),          "color":"#E65100","icon":"🏁","has_drill":True},
        ]}

    elif action == "drill":
        rd_r = rows_result(kpi_key, "", "")
        grps_r = []
        if kpi_key == "cw":
            src_vals = list(set([x.get("source","") for x in LIVE_OPP_WON if x.get("source")]))
            sr_c = []
            for sv in sorted(src_vals):
                sv_rows = df_eq(LIVE_OPP_WON,"source",sv)
                sr_c.append(seg_card("cw",sv,len(sv_rows),"#2E7D32","🏆","src_"+sv.lower().replace(" ","_"),amt=sum_field(sv_rows,"opportunity_amount")))
            o1r = [x for x in LIVE_OPP_WON if x.get("opportunity_amount",0) < 100000]
            o2r = [x for x in LIVE_OPP_WON if 100000 <= x.get("opportunity_amount",0) < 500000]
            o3r = [x for x in LIVE_OPP_WON if 500000 <= x.get("opportunity_amount",0) < 2500000]
            o4r = [x for x in LIVE_OPP_WON if x.get("opportunity_amount",0) >= 2500000]
            amc_r = [
                seg_card("cw","< ₹1L", len(o1r),"#757575","💰","amt_lt1l",amt=sum_field(o1r,"opportunity_amount")),
                seg_card("cw","₹1-5L", len(o2r),"#1E88E5","💰","amt_1_5l",amt=sum_field(o2r,"opportunity_amount")),
                seg_card("cw","₹5-25L",len(o3r),"#8E24AA","💰","amt_5_25l",amt=sum_field(o3r,"opportunity_amount")),
                seg_card("cw","₹25L+", len(o4r),"#2E7D32","💰","amt_gt25l",amt=sum_field(o4r,"opportunity_amount")),
            ]
            grps_r = [{"label":"By Source","cards":sr_c},{"label":"By Amount","cards":amc_r}]
        elif kpi_key == "cl":
            rsn_vals = list(set([x.get("lost_reason","") for x in LIVE_OPP_LOST if x.get("lost_reason")]))
            rsn_c = []
            for rv in sorted(rsn_vals):
                rv_rows = df_eq(LIVE_OPP_LOST,"lost_reason",rv)
                rsn_c.append(seg_card("cl",rv,len(rv_rows),"#C62828","❌","r_"+rv.lower().replace(" ","_"),amt=sum_field(rv_rows,"opportunity_amount")))
            grps_r = [{"label":"By Reason","cards":rsn_c}]
        elif kpi_key == "ac":
            tyc_r = []
            for afk_r in ACT_TYPE:
                tyc_r.append(seg_card("ac",ACT_TYPE[afk_r],len(df_eq(comp_acts,"activity_type",ACT_TYPE[afk_r])),"#00695C","✅",afk_r))
            grps_r = [{"label":"By Type","cards":tyc_r}]
        elif kpi_key == "nh":
            tyc_nh = []
            for afk_nh in ACT_TYPE:
                tyc_nh.append(seg_card("nh",ACT_TYPE[afk_nh],len(df_eq(canc_acts,"activity_type",ACT_TYPE[afk_nh])),"#880E4F","🚫",afk_nh))
            grps_r = [{"label":"By Type","cards":tyc_nh}]
        elif kpi_key == "tk":
            tpr_c = []
            for pr_tk in ["Critical","High","Medium","Low"]:
                tpr_c.append(seg_card("tk",pr_tk,len(df_eq(LIVE_TICKETS_CLOSED,"priority",pr_tk)),"#1565C0","🔒","pri_"+pr_tk.lower()))
            sla_c = [
                seg_card("tk","Breached",  len(df_eq(LIVE_TICKETS_CLOSED,"sla_status","Breached")),  "#C62828","🔴","sla_breached","table"),
                seg_card("tk","Within SLA",len(df_eq(LIVE_TICKETS_CLOSED,"sla_status","Within SLA")),"#43A047","🟢","sla_ok","table"),
            ]
            grps_r = [{"label":"By Priority","cards":tpr_c},{"label":"By SLA","cards":sla_c}]
        elif kpi_key == "lv":
            src_lv = list(set([x.get("source","") for x in LIVE_LEADS_CONV if x.get("source")]))
            src_lv_c = []
            for slv in sorted(src_lv):
                slv_rows = df_eq(LIVE_LEADS_CONV,"source",slv)
                src_lv_c.append(seg_card("lv",slv,len(slv_rows),"#2E7D32","🔄","src_"+slv.lower().replace(" ","_")))
            grps_r = [{"label":"By Source","cards":src_lv_c}]
        elif kpi_key == "ld":
            dr_vals = list(set([x.get("dead_reason","") for x in LIVE_LEADS_DEAD if x.get("dead_reason")]))
            dr_c = []
            for dv in sorted(dr_vals):
                dr_c.append(seg_card("ld",dv,len(df_eq(LIVE_LEADS_DEAD,"dead_reason",dv)),"#C62828","💀","r_"+dv.lower().replace(" ","_")))
            if not dr_c:
                st_ld = list(set([x.get("status","") for x in LIVE_LEADS_DEAD if x.get("status")]))
                for sv_ld in sorted(st_ld):
                    dr_c.append(seg_card("ld",sv_ld,len(df_eq(LIVE_LEADS_DEAD,"status",sv_ld)),"#C62828","💀","st_"+sv_ld.lower().replace(" ","_")))
            grps_r = [{"label":"By Reason","cards":dr_c}]
        elif kpi_key == "cc":
            cdir_r = [
                seg_card("cc","Inbound", len(df_eq(comp_calls,"direction","Inbound")), "#43A047","📲","dir_inbound"),
                seg_card("cc","Outbound",len(df_eq(comp_calls,"direction","Outbound")),"#1565C0","📲","dir_outbound"),
            ]
            grps_r = [{"label":"By Direction","cards":cdir_r}]
        elif kpi_key == "pc":
            on_time = [x for x in comp_projs if x.get("delay_days",0) <= 0]
            delayed  = [x for x in comp_projs if x.get("delay_days",0) > 0]
            grps_r = [{"label":"By Delivery","cards":[
                seg_card("pc","On Time",len(on_time),"#43A047","🏁","pc_ontime"),
                seg_card("pc","Delayed", len(delayed),"#E53935","🏁","pc_delayed"),
            ]}]
        else:
            grps_r = []
        result_amt_map = {"cw":"opportunity_amount","cl":"opportunity_amount"}
        out = make_drill(grps_r, rd_r["rows"], rd_r["uf"], kpi_key, rd_r["clr"], rd_r["icon"], "all", amt_field=result_amt_map.get(kpi_key,""))

    elif action == "userwise":
        rd_uw_r = rows_result(kpi_key, sub_filter, "")
        result_amt_map3 = {"cw":"opportunity_amount","cl":"opportunity_amount"}
        out = {"cards": make_uw_cards(kpi_key, rd_uw_r["rows"], rd_uw_r["uf"], rd_uw_r["clr"], rd_uw_r["icon"], sub_filter, amt_field=result_amt_map3.get(kpi_key,""))}

    elif action == "table":
        rd_tbl_r = rows_result(kpi_key, sub_filter, user_filter)
        out = live_tbl(rd_tbl_r["rows"], rd_tbl_r["cols"], rd_tbl_r["title"])
    else:
        out = {"cards":[]}

else:
    out = {"cards":[]}

frappe.response["message"] = out

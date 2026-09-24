# ============================================================
# Server Script — API Method
# Name        : get_dashboard_data
# Type        : API
# RestrictedPython compliant — no imports, no f-strings
# ============================================================

user        = frappe.session.user
now_date    = frappe.utils.today()
month_start = frappe.utils.get_first_day(now_date)

def get_avg_tat(doctype, filters):
    records = frappe.db.get_all(doctype, filters=filters, fields=["tat_days"])
    valid   = [r.tat_days for r in records if r.tat_days is not None]
    return round(sum(valid) / len(valid), 1) if valid else 0

def safe_pct(n, d):
    return round((n * 100.0) / d, 1) if d else 0

# ── Employee lookup ──────────────────────────────────────────
employee = frappe.db.get_value("Employee", {"company_email": user, "status": "Active"}, ["first_name", "employee_name", "designation", "department", "image"], as_dict=True)

if not employee:
    ui = frappe.db.get_value("User", user, ["full_name", "first_name", "user_image"], as_dict=True)
    employee = {
        "employee_name": ui.get("full_name") if ui else user.split("@")[0].capitalize(),
        "designation":   "ERP Consultant",
        "department":    "CBD IT Solutions",
        "image":         ui.get("user_image") if ui else "/assets/frappe/images/default-avatar.png"
    }

name_display  = employee.get("first_name", "").capitalize() if employee.get("first_name") else user.split("@")[0].capitalize()
kpi_data      = []
plan_data     = []
pending_tasks = []
performance   = {}
actions       = {}
process_label = ""
tasks_route   = ""
tasks_filter  = {}

# ════════════════════════════════════════════════════════════
# 1. MANISHA  —  CRM & Sales  (Steps 6, 7, 10)
# ════════════════════════════════════════════════════════════
if user == "manisha.sadbhavrenewable@gmail.com":
    process_label = name_display + " - CRM & Sales"
    kpi_data = [
        {"title": "Pending Follow-ups",      "count": frappe.db.count("Quotation",     {"status": "Open", "proposal_sent": 1}),      "tat": get_avg_tat("Quotation", {"status": "Open"}),    "route": "Quotation",     "filter": {"status": "Open", "proposal_sent": 1}},
        {"title": "Proposals in Pipeline",   "count": frappe.db.count("Quotation",     {"status": "Open"}),                           "tat": get_avg_tat("Quotation", {"status": "Open"}),    "route": "Quotation",     "filter": {"status": "Open"}},
        {"title": "Sales Orders Created",    "count": frappe.db.count("Sales Order",   {"owner": user}),                              "tat": 0,                                               "route": "Sales Order",   "filter": {"owner": user}},
        {"title": "Dispatch Notify Pending", "count": frappe.db.count("Delivery Note", {"status": "Submitted"}),                      "tat": 0,                                               "route": "Delivery Note", "filter": {"status": "Submitted"}}
    ]
    plan_data = [
        {"title": "Follow-ups Due Today",    "count": frappe.db.count("Quotation",     {"exp_nxstp_dt": now_date, "status": "Open"}), "route": "Quotation",     "filter": {"exp_nxstp_dt": now_date, "status": "Open"}},
        {"title": "Sales Orders to Create",  "count": frappe.db.count("Quotation",     {"status": "Open", "exp_nxstp_dt": now_date}), "route": "Quotation",     "filter": {"status": "Open"}},
        {"title": "Dispatch Alerts to Send", "count": frappe.db.count("Delivery Note", {"status": "Submitted"}),                      "route": "Delivery Note", "filter": {"status": "Submitted"}}
    ]
    for d in frappe.db.get_all("Quotation", filters={"status": "Open"}, fields=["name", "customer_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Quotation", "type": "Proposal Follow-up", "client": d.customer_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    tasks_route  = "Quotation"
    tasks_filter = {"status": "Open"}
    performance  = {
        "label1": "Follow-ups Done",  "value1": frappe.db.count("Quotation",   {"status": ["!=", "Open"], "owner": user, "transaction_date": [">=", month_start]}),
        "label2": "Sales Orders",     "value2": frappe.db.count("Sales Order", {"owner": user, "transaction_date": [">=", month_start]}),
        "label3": "Lost Proposals",   "value3": frappe.db.count("Quotation",   {"status": "Lost", "transaction_date": [">=", month_start]})
    }
    actions = {"btn1_label": "New Sales Order", "btn1_type": "new_doc", "btn1_target": "Sales Order", "btn2_label": "View Pipeline", "btn2_type": "list_route", "btn2_target": "Quotation", "btn2_filter": {"status": "Open"}, "btn2_visible": True}


# ════════════════════════════════════════════════════════════
# 2. MEENAKSHI / KHURANA / SANDEEP  —  Full Management View
#    Step 1 originators — see the entire pipeline, all stages
#    No user filter: they oversee everything
# ════════════════════════════════════════════════════════════
elif user in ["mp@sadbhavrenewables.com", "ksk@sadbhavrenewables.com", "sandeep@sadbhavrenewables.com"]:
    process_label = name_display + " - Management Overview"

    SYNC_DOCTYPE = "Liaisoning And Synchronization"
    sync_exists  = frappe.db.exists("DocType", SYNC_DOCTYPE)

    kpi_data = [
        # Step 1-2: Lead & Survey
        {"title": "Open Leads",                  "count": frappe.db.count("Lead",             {"status": "Open"}),                                    "tat": get_avg_tat("Lead",         {"status": "Open"}),    "route": "Lead",             "filter": {"status": "Open"}},
        {"title": "Site Surveys Pending",        "count": frappe.db.count("Site Survey",      {"status": "Open"}),                                    "tat": get_avg_tat("Site Survey",  {"status": "Open"}),    "route": "Site Survey",      "filter": {"status": "Open"}},
        # Step 5: Proposals
        {"title": "Proposals Pending (Draft)",   "count": frappe.db.count("Quotation",        {"status": "Draft"}),                                   "tat": get_avg_tat("Quotation",    {"status": "Draft"}),   "route": "Quotation",        "filter": {"status": "Draft"}},
        {"title": "Proposals in Follow-up",      "count": frappe.db.count("Quotation",        {"status": "Open"}),                                    "tat": get_avg_tat("Quotation",    {"status": "Open"}),    "route": "Quotation",        "filter": {"status": "Open"}},
        # Step 7-8: Sales Order & Payment
        {"title": "Sales Orders Pending",        "count": frappe.db.count("Sales Order",      {"status": "Draft"}),                                   "tat": get_avg_tat("Sales Order",  {"status": "Draft"}),   "route": "Sales Order",      "filter": {"status": "Draft"}},
        {"title": "Sales Orders Active",         "count": frappe.db.count("Sales Order",      {"status": "To Deliver and Bill"}),                     "tat": 0,                                                  "route": "Sales Order",      "filter": {"status": "To Deliver and Bill"}},
        # Step 9-10: Dispatch
        {"title": "Dispatch Pending",            "count": frappe.db.count("Delivery Note",    {"status": "Draft"}),                                   "tat": 0,                                                  "route": "Delivery Note",    "filter": {"status": "Draft"}},
        # Step 11: Installation
        {"title": "Installations Pending",       "count": frappe.db.count("Installation Note",{"status": "Draft"}),                                   "tat": 0,                                                  "route": "Installation Note","filter": {"status": "Draft"}},
        # Step 12: Liaisoning
        {"title": "Liaisoning Pending",          "count": frappe.db.count(SYNC_DOCTYPE,       {"liaisoning_status": ["in", ["New", "In Process"]]}) if sync_exists else 0, "tat": 0, "route": SYNC_DOCTYPE if sync_exists else "", "filter": {"liaisoning_status": "New"}}
    ]

    plan_data = [
        {"title": "Proposal Follow-ups Due Today", "count": frappe.db.count("Quotation",     {"exp_nxstp_dt": now_date, "status": "Open"}),      "route": "Quotation",     "filter": {"exp_nxstp_dt": now_date, "status": "Open"}},
        {"title": "Payments to Verify",            "count": frappe.db.count("Sales Order",   {"status": "Draft"}),                               "route": "Sales Order",   "filter": {"status": "Draft"}},
        {"title": "Dispatches Today",              "count": frappe.db.count("Delivery Note", {"posting_date": now_date}),                        "route": "Delivery Note", "filter": {"posting_date": now_date}}
    ]

    # Pending queue — top critical items across all stages
    for d in frappe.db.get_all("Lead", filters={"status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"], limit=3):
        pending_tasks.append({"doctype": "Lead", "type": "Lead Follow-up", "client": d.lead_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    for d in frappe.db.get_all("Quotation", filters={"status": "Open"}, fields=["name", "customer_name", "exp_nxstp_dt", "tat_days"], limit=3):
        pending_tasks.append({"doctype": "Quotation", "type": "Proposal Follow-up", "client": d.customer_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    for d in frappe.db.get_all("Sales Order", filters={"status": "Draft"}, fields=["name", "customer_name", "transaction_date", "tat_days"], limit=2):
        pending_tasks.append({"doctype": "Sales Order", "type": "Payment Verification", "client": d.customer_name, "ref": d.name, "date": d.transaction_date, "tat": d.tat_days or 0})
    for d in frappe.db.get_all("Delivery Note", filters={"status": "Draft"}, fields=["name", "customer_name", "posting_date"], limit=2):
        pending_tasks.append({"doctype": "Delivery Note", "type": "Dispatch Pending", "client": d.customer_name, "ref": d.name, "date": d.posting_date, "tat": 0})

    tasks_route  = "Lead"
    tasks_filter = {"status": "Open"}

    performance = {
        "label1": "Leads This Month",        "value1": frappe.db.count("Lead",         {"creation": [">=", month_start]}),
        "label2": "Sales Orders This Month",  "value2": frappe.db.count("Sales Order", {"transaction_date": [">=", month_start]}),
        "label3": "Dispatched This Month",    "value3": frappe.db.count("Delivery Note",{"status": "Submitted", "posting_date": [">=", month_start]})
    }

    actions = {"btn1_label": "New Lead", "btn1_type": "new_doc", "btn1_target": "Lead", "btn2_label": "View All Leads", "btn2_type": "list_route", "btn2_target": "Lead", "btn2_filter": {}, "btn2_visible": True}


# ════════════════════════════════════════════════════════════
# 3. TARA  —  Residential Pipeline  (Steps 2, 3, 4, 5)
# ════════════════════════════════════════════════════════════
elif user == "tara.sadbhavrenewable@gmail.com":
    process_label = "Tara - Residential Pipeline"
    kpi_data = [
        {"title": "Leads Created (Open)",     "count": frappe.db.count("Lead",        {"lead_owner": user, "status": "Open"}),                                                             "tat": 0,                                                                          "route": "Lead",        "filter": {"lead_owner": user, "status": "Open"}},
        {"title": "Surveys Pending",          "count": frappe.db.count("Site Survey", {"plant_category": "Residential", "status": "Open"}),                                                "tat": get_avg_tat("Site Survey", {"plant_category": "Residential", "status": "Open"}), "route": "Site Survey", "filter": {"plant_category": "Residential", "status": "Open"}},
        {"title": "Drawings Pending",         "count": frappe.db.count("Site Survey", {"plant_category": "Residential", "status": "Open"}),                                                "tat": get_avg_tat("Site Survey", {"plant_category": "Residential", "status": "Open"}), "route": "Site Survey", "filter": {"plant_category": "Residential", "status": "Open"}},
        {"title": "Proposals Pending",        "count": frappe.db.count("Quotation",   {"plant_category": "Residential", "status": "Draft"}),                                               "tat": get_avg_tat("Quotation",   {"plant_category": "Residential", "status": "Draft"}), "route": "Quotation",   "filter": {"plant_category": "Residential", "status": "Draft"}},
        {"title": "Proposals Sent (Month)",   "count": frappe.db.count("Quotation",   {"plant_category": "Residential", "proposal_sent": 1, "transaction_date": [">=", month_start]}),     "tat": 0,                                                                          "route": "Quotation",   "filter": {"plant_category": "Residential", "proposal_sent": 1}}
    ]
    plan_data = [
        {"title": "Proposals to Complete", "count": frappe.db.count("Quotation",   {"plant_category": "Residential", "status": "Draft"}),                                              "route": "Quotation",   "filter": {"plant_category": "Residential", "status": "Draft"}},
        {"title": "Drawings Needed",       "count": frappe.db.count("Site Survey", {"plant_category": "Residential", "status": "Open"}),                                               "route": "Site Survey", "filter": {"plant_category": "Residential", "status": "Open"}},
        {"title": "Sent to CRM (Month)",   "count": frappe.db.count("Quotation",   {"plant_category": "Residential", "proposal_sent": 1, "transaction_date": [">=", month_start]}),    "route": "Quotation",   "filter": {"plant_category": "Residential", "proposal_sent": 1}}
    ]
    for d in frappe.db.get_all("Site Survey", filters={"plant_category": "Residential", "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Site Survey", "type": "Attach Drawing", "client": d.lead_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    for d in frappe.db.get_all("Quotation", filters={"plant_category": "Residential", "status": "Draft"}, fields=["name", "customer_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Quotation", "type": "Create Proposal", "client": d.customer_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    tasks_route  = "Quotation"
    tasks_filter = {"plant_category": "Residential", "status": "Draft"}
    perf_p = frappe.db.count("Quotation", {"plant_category": "Residential", "proposal_sent": 1, "transaction_date": [">=", month_start]})
    performance = {
        "label1": "Proposals Sent",  "value1": perf_p,
        "label2": "Drawings Done",   "value2": frappe.db.count("Site Survey", {"plant_category": "Residential", "status": "Completed", "completed_date": [">=", month_start]}),
        "label3": "Conversion %",    "value3": safe_pct(perf_p, frappe.db.count("Lead", {"status": "Site Survey"}))
    }
    actions = {"btn1_label": "New Lead", "btn1_type": "new_doc", "btn1_target": "Lead", "btn2_label": "New Proposal", "btn2_type": "new_doc", "btn2_target": "Quotation", "btn2_visible": True}


# ════════════════════════════════════════════════════════════
# 4. GAYATRI  —  Commercial Pipeline  (Steps 2, 3, 4, 5)
# ════════════════════════════════════════════════════════════
elif user == "ergayatrisadbhav01@gmail.com":
    process_label = "Gayatri - Commercial Pipeline"
    kpi_data = [
        {"title": "Leads Created (Open)",     "count": frappe.db.count("Lead",        {"lead_owner": user, "status": "Open"}),                                                             "tat": 0,                                                                           "route": "Lead",        "filter": {"lead_owner": user, "status": "Open"}},
        {"title": "Surveys Pending",          "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Open"}),                                                 "tat": get_avg_tat("Site Survey", {"plant_category": "Commercial", "status": "Open"}), "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Open"}},
        {"title": "Drawings Pending",         "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Open"}),                                                 "tat": get_avg_tat("Site Survey", {"plant_category": "Commercial", "status": "Open"}), "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Open"}},
        {"title": "Proposals Pending",        "count": frappe.db.count("Quotation",   {"plant_category": "Commercial", "status": "Draft"}),                                                "tat": get_avg_tat("Quotation",   {"plant_category": "Commercial", "status": "Draft"}), "route": "Quotation",   "filter": {"plant_category": "Commercial", "status": "Draft"}},
        {"title": "Proposals Sent (Month)",   "count": frappe.db.count("Quotation",   {"plant_category": "Commercial", "proposal_sent": 1, "transaction_date": [">=", month_start]}),      "tat": 0,                                                                           "route": "Quotation",   "filter": {"plant_category": "Commercial", "proposal_sent": 1}}
    ]
    plan_data = [
        {"title": "Proposals to Complete", "count": frappe.db.count("Quotation",   {"plant_category": "Commercial", "status": "Draft"}),                                              "route": "Quotation",   "filter": {"plant_category": "Commercial", "status": "Draft"}},
        {"title": "Drawings Needed",       "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Open"}),                                               "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Open"}},
        {"title": "Sent to CRM (Month)",   "count": frappe.db.count("Quotation",   {"plant_category": "Commercial", "proposal_sent": 1, "transaction_date": [">=", month_start]}),    "route": "Quotation",   "filter": {"plant_category": "Commercial", "proposal_sent": 1}}
    ]
    for d in frappe.db.get_all("Site Survey", filters={"plant_category": "Commercial", "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Site Survey", "type": "Attach Drawing", "client": d.lead_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    for d in frappe.db.get_all("Quotation", filters={"plant_category": "Commercial", "status": "Draft"}, fields=["name", "customer_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Quotation", "type": "Create Proposal", "client": d.customer_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    tasks_route  = "Quotation"
    tasks_filter = {"plant_category": "Commercial", "status": "Draft"}
    perf_p = frappe.db.count("Quotation", {"plant_category": "Commercial", "proposal_sent": 1, "transaction_date": [">=", month_start]})
    performance = {
        "label1": "Proposals Sent",  "value1": perf_p,
        "label2": "Drawings Done",   "value2": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Completed", "completed_date": [">=", month_start]}),
        "label3": "Conversion %",    "value3": safe_pct(perf_p, frappe.db.count("Lead", {"status": "Site Survey"}))
    }
    actions = {"btn1_label": "New Lead", "btn1_type": "new_doc", "btn1_target": "Lead", "btn2_label": "New Proposal", "btn2_type": "new_doc", "btn2_target": "Quotation", "btn2_visible": True}


# ════════════════════════════════════════════════════════════
# 5. DAMINI  —  Commercial Arka Drawings  (Step 4)
# ════════════════════════════════════════════════════════════
elif user == "daminisadbhavrenewable@gmail.com":
    process_label = "Damini - Commercial Drawings"
    kpi_data = [
        {"title": "Drawings Pending",       "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Open"}),                                                "tat": get_avg_tat("Site Survey", {"plant_category": "Commercial", "status": "Open"}), "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Open"}},
        {"title": "Drawings Completed",     "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Completed"}),                                           "tat": 0,                                                                              "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Completed"}},
        {"title": "Completed This Month",   "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Completed", "completed_date": [">=", month_start]}),   "tat": 0,                                                                              "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Completed"}}
    ]
    plan_data = [
        {"title": "Pending Commercial Drawings", "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Open"}),                                               "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Open"}},
        {"title": "Completed Today",             "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "completed_date": now_date}),                                     "route": "Site Survey", "filter": {"plant_category": "Commercial", "completed_date": now_date}},
        {"title": "Done This Month",             "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Completed", "completed_date": [">=", month_start]}),   "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Completed"}}
    ]
    for d in frappe.db.get_all("Site Survey", filters={"plant_category": "Commercial", "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Site Survey", "type": "Attach Drawing", "client": d.lead_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    tasks_route  = "Site Survey"
    tasks_filter = {"plant_category": "Commercial", "status": "Open"}
    performance  = {
        "label1": "Drawings Done",    "value1": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Completed", "completed_date": [">=", month_start]}),
        "label2": "Pending Now",      "value2": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Open"}),
        "label3": "Avg TAT (Days)",   "value3": get_avg_tat("Site Survey", {"plant_category": "Commercial", "status": "Open"})
    }
    actions = {"btn1_label": "Open Drawings Queue", "btn1_type": "list_route", "btn1_target": "Site Survey", "btn1_filter": {"plant_category": "Commercial", "status": "Open"}, "btn2_visible": False}


# ════════════════════════════════════════════════════════════
# 6. DINESH  —  Commercial Survey + AutoCAD Drawings  (Steps 2, 4)
# ════════════════════════════════════════════════════════════
elif user == "dinesh.sadbhavrenewables@gmail.com":
    process_label = "Dinesh - Commercial Survey & Drawings"
    kpi_data = [
        {"title": "Leads Generated",       "count": frappe.db.count("Lead",        {"lead_owner": user}),                                                                               "tat": get_avg_tat("Lead",        {"lead_owner": user}),                                   "route": "Lead",        "filter": {"lead_owner": user}},
        {"title": "Surveys Pending",       "count": frappe.db.count("Site Survey", {"surveyed_by": user, "plant_category": "Commercial", "status": "Open"}),                           "tat": get_avg_tat("Site Survey", {"surveyed_by": user, "plant_category": "Commercial", "status": "Open"}), "route": "Site Survey", "filter": {"surveyed_by": user, "plant_category": "Commercial", "status": "Open"}},
        {"title": "Drawings Pending",      "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Open"}),                                                "tat": get_avg_tat("Site Survey", {"plant_category": "Commercial", "status": "Open"}),     "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Open"}},
        {"title": "Surveys Done",          "count": frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Completed"}),                                                      "tat": 0,                                                                                  "route": "Site Survey", "filter": {"surveyed_by": user, "status": "Completed"}}
    ]
    plan_data = [
        {"title": "Surveys Today",      "count": frappe.db.count("Site Survey", {"survey_date": now_date, "surveyed_by": user}),                  "route": "Site Survey", "filter": {"survey_date": now_date, "surveyed_by": user}},
        {"title": "Drawings to Do",     "count": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Open"}),              "route": "Site Survey", "filter": {"plant_category": "Commercial", "status": "Open"}},
        {"title": "Completed Today",    "count": frappe.db.count("Site Survey", {"completed_date": now_date, "surveyed_by": user}),               "route": "Site Survey", "filter": {"completed_date": now_date, "surveyed_by": user}}
    ]
    for d in frappe.db.get_all("Site Survey", filters={"surveyed_by": user, "plant_category": "Commercial", "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Site Survey", "type": "Conduct Survey", "client": d.lead_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    for d in frappe.db.get_all("Site Survey", filters={"plant_category": "Commercial", "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Site Survey", "type": "Attach Drawing", "client": d.lead_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    tasks_route  = "Site Survey"
    tasks_filter = {"plant_category": "Commercial", "status": "Open"}
    performance  = {
        "label1": "Surveys Done",    "value1": frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Completed", "completed_date": [">=", month_start]}),
        "label2": "Drawings Done",   "value2": frappe.db.count("Site Survey", {"plant_category": "Commercial", "status": "Completed", "completed_date": [">=", month_start]}),
        "label3": "Leads Generated", "value3": frappe.db.count("Lead",        {"lead_owner": user, "creation": [">=", month_start]})
    }
    actions = {"btn1_label": "Generate Lead", "btn1_type": "new_doc", "btn1_target": "Lead", "btn2_label": "Conduct Survey", "btn2_type": "new_doc", "btn2_target": "Site Survey", "btn2_visible": True}


# ════════════════════════════════════════════════════════════
# 7. TIKAM  —  Accounts & Payment Verification  (Step 8)
# ════════════════════════════════════════════════════════════
elif user == "tikam.sadbhavrenewable@gmail.com":
    process_label = name_display + " - Accounts & Payments"
    kpi_data = [
        {"title": "Pending Verification",  "count": frappe.db.count("Sales Order", {"status": "Draft"}),                                                                       "tat": get_avg_tat("Sales Order", {"status": "Draft"}), "route": "Sales Order", "filter": {"status": "Draft"}},
        {"title": "Goodwill Approvals",    "count": frappe.db.count("Sales Order", {"without_pay_reason": "GOODWILL APPROVAL"}),                                               "tat": 0,                                               "route": "Sales Order", "filter": {"without_pay_reason": "GOODWILL APPROVAL"}},
        {"title": "Finance Approvals",     "count": frappe.db.count("Sales Order", {"without_pay_reason": "BANK FINANCE"}),                                                    "tat": 0,                                               "route": "Sales Order", "filter": {"without_pay_reason": "BANK FINANCE"}},
        {"title": "Verified This Month",   "count": frappe.db.count("Sales Order", {"status": ["!=", "Draft"], "transaction_date": [">=", month_start]}),                      "tat": 0,                                               "route": "Sales Order", "filter": {"status": ["!=", "Draft"], "transaction_date": [">=", month_start]}}
    ]
    plan_data = [
        {"title": "Verify Advance Payments", "count": frappe.db.count("Sales Order", {"per_advance": [">", 0], "status": "Draft"}),           "route": "Sales Order", "filter": {"status": "Draft"}},
        {"title": "Verify Goodwill Cases",   "count": frappe.db.count("Sales Order", {"without_advance": 1}),                                 "route": "Sales Order", "filter": {"without_advance": 1}},
        {"title": "Verify Finance Cases",    "count": frappe.db.count("Sales Order", {"without_pay_reason": "BANK FINANCE"}),                 "route": "Sales Order", "filter": {"without_pay_reason": "BANK FINANCE"}}
    ]
    for d in frappe.db.get_all("Sales Order", filters={"status": "Draft"}, fields=["name", "customer_name", "transaction_date", "tat_days"]):
        pending_tasks.append({"doctype": "Sales Order", "type": "Payment Verification", "client": d.customer_name, "ref": d.name, "date": d.transaction_date, "tat": d.tat_days or 0})
    tasks_route  = "Sales Order"
    tasks_filter = {"status": "Draft"}
    performance  = {
        "label1": "Payments Verified",  "value1": frappe.db.count("Sales Order", {"status": ["!=", "Draft"], "transaction_date": [">=", month_start]}),
        "label2": "Goodwill Cases",     "value2": frappe.db.count("Sales Order", {"without_pay_reason": "GOODWILL APPROVAL", "transaction_date": [">=", month_start]}),
        "label3": "Finance Cases",      "value3": frappe.db.count("Sales Order", {"without_pay_reason": "BANK FINANCE", "transaction_date": [">=", month_start]})
    }
    actions = {"btn1_label": "Pending Payments", "btn1_type": "list_route", "btn1_target": "Sales Order", "btn1_filter": {"status": "Draft"}, "btn2_visible": False}


# ════════════════════════════════════════════════════════════
# 8. SUBODH  —  Stores & Material Dispatch  (Steps 9, 10)
# ════════════════════════════════════════════════════════════
elif user == "subodh.sadbhavrenewable@gmail.com":
    process_label = "Subodh - Stores & Dispatch"
    kpi_data = [
        {"title": "Pending Dispatch",        "count": frappe.db.count("Delivery Note", {"status": "Draft"}),                                                                "tat": 0, "route": "Delivery Note", "filter": {"status": "Draft"}},
        {"title": "Dispatched Today",        "count": frappe.db.count("Delivery Note", {"posting_date": now_date, "status": "Submitted"}),                                   "tat": 0, "route": "Delivery Note", "filter": {"posting_date": now_date, "status": "Submitted"}},
        {"title": "Orders Ready to Send",    "count": frappe.db.count("Sales Order",   {"status": "To Deliver and Bill"}),                                                   "tat": 0, "route": "Sales Order",   "filter": {"status": "To Deliver and Bill"}},
        {"title": "Dispatched This Month",   "count": frappe.db.count("Delivery Note", {"status": "Submitted", "posting_date": [">=", month_start]}),                        "tat": 0, "route": "Delivery Note", "filter": {"status": "Submitted", "posting_date": [">=", month_start]}}
    ]
    plan_data = [
        {"title": "Dispatches Today",    "count": frappe.db.count("Delivery Note", {"posting_date": now_date}),                                     "route": "Delivery Note", "filter": {"posting_date": now_date}},
        {"title": "Packing In Progress", "count": frappe.db.count("Delivery Note", {"status": "Draft"}),                                            "route": "Delivery Note", "filter": {"status": "Draft"}},
        {"title": "Completed Today",     "count": frappe.db.count("Delivery Note", {"posting_date": now_date, "status": "Submitted"}),               "route": "Delivery Note", "filter": {"posting_date": now_date, "status": "Submitted"}}
    ]
    for d in frappe.db.get_all("Delivery Note", filters={"status": "Draft"}, fields=["name", "customer_name", "posting_date"]):
        pending_tasks.append({"doctype": "Delivery Note", "type": "Pack & Dispatch", "client": d.customer_name, "ref": d.name, "date": d.posting_date, "tat": 0})
    tasks_route  = "Delivery Note"
    tasks_filter = {"status": "Draft"}
    performance  = {
        "label1": "Dispatched (Month)",  "value1": frappe.db.count("Delivery Note", {"status": "Submitted", "posting_date": [">=", month_start]}),
        "label2": "Pending Packing",     "value2": frappe.db.count("Delivery Note", {"status": "Draft"}),
        "label3": "Completed Today",     "value3": frappe.db.count("Delivery Note", {"posting_date": now_date, "status": "Submitted"})
    }
    actions = {"btn1_label": "New Delivery Note", "btn1_type": "new_doc", "btn1_target": "Delivery Note", "btn2_label": "Pending Dispatch", "btn2_type": "list_route", "btn2_target": "Delivery Note", "btn2_filter": {"status": "Draft"}, "btn2_visible": True}


# ════════════════════════════════════════════════════════════
# 9. SUYASH  —  Purchase
# ════════════════════════════════════════════════════════════
elif user == "purchase.sadbhavrenewable@gmail.com":
    process_label = "Suyash - Purchase"
    kpi_data = [
        {"title": "Purchase Orders Pending",  "count": frappe.db.count("Purchase Order",   {"status": "Draft"}),                                                              "tat": 0, "route": "Purchase Order",   "filter": {"status": "Draft"}},
        {"title": "Items to Receive",         "count": frappe.db.count("Purchase Receipt", {"status": "Draft"}),                                                              "tat": 0, "route": "Purchase Receipt", "filter": {"status": "Draft"}},
        {"title": "Completed This Month",     "count": frappe.db.count("Purchase Order",   {"status": "Submitted", "transaction_date": [">=", month_start]}),                 "tat": 0, "route": "Purchase Order",   "filter": {"status": "Submitted", "transaction_date": [">=", month_start]}}
    ]
    plan_data = [
        {"title": "Purchase Orders to Approve", "count": frappe.db.count("Purchase Order",   {"status": "Draft"}),                                                            "route": "Purchase Order",   "filter": {"status": "Draft"}},
        {"title": "Receipts Pending",           "count": frappe.db.count("Purchase Receipt", {"status": "Draft"}),                                                            "route": "Purchase Receipt", "filter": {"status": "Draft"}},
        {"title": "Orders Placed (Month)",      "count": frappe.db.count("Purchase Order",   {"status": "Submitted", "transaction_date": [">=", month_start]}),               "route": "Purchase Order",   "filter": {"status": "Submitted", "transaction_date": [">=", month_start]}}
    ]
    for d in frappe.db.get_all("Purchase Order", filters={"status": "Draft"}, fields=["name", "supplier_name", "transaction_date"]):
        pending_tasks.append({"doctype": "Purchase Order", "type": "Approve Purchase Order", "client": d.supplier_name, "ref": d.name, "date": d.transaction_date, "tat": 0})
    tasks_route  = "Purchase Order"
    tasks_filter = {"status": "Draft"}
    performance  = {
        "label1": "Purchase Orders Approved",  "value1": frappe.db.count("Purchase Order",   {"status": "Submitted", "transaction_date": [">=", month_start]}),
        "label2": "Receipts Completed",        "value2": frappe.db.count("Purchase Receipt", {"status": "Submitted", "posting_date": [">=", month_start]}),
        "label3": "Pending Purchase Orders",   "value3": frappe.db.count("Purchase Order",   {"status": "Draft"})
    }
    actions = {"btn1_label": "New Purchase Order", "btn1_type": "new_doc", "btn1_target": "Purchase Order", "btn2_label": "Pending Receipts", "btn2_type": "list_route", "btn2_target": "Purchase Receipt", "btn2_filter": {"status": "Draft"}, "btn2_visible": True}


# ════════════════════════════════════════════════════════════
# 10. AJAY & ASHISH  —  Project Execution  (Step 11)
# ════════════════════════════════════════════════════════════
elif user in ["ajay.sadbhavrenewable@gmail.com", "ashish.sadbhavrenewables@gmail.com"]:
    process_label = name_display + " - Project Execution"
    kpi_data = [
        {"title": "Open Projects",          "count": frappe.db.count("Project",           {"status": "Open"}),                                                               "tat": 0, "route": "Project",           "filter": {"status": "Open"}},
        {"title": "Pending Installations",  "count": frappe.db.count("Installation Note", {"status": "Draft"}),                                                              "tat": 0, "route": "Installation Note", "filter": {"status": "Draft"}},
        {"title": "Material Ready",         "count": frappe.db.count("Delivery Note",     {"status": "Submitted"}),                                                          "tat": 0, "route": "Delivery Note",     "filter": {"status": "Submitted"}},
        {"title": "Installations (Month)",  "count": frappe.db.count("Installation Note", {"status": "Submitted", "inst_date": [">=", month_start]}),                        "tat": 0, "route": "Installation Note", "filter": {"status": "Submitted", "inst_date": [">=", month_start]}}
    ]
    plan_data = [
        {"title": "Scheduled Today",          "count": frappe.db.count("Installation Note", {"inst_date": now_date}),                                     "route": "Installation Note", "filter": {"inst_date": now_date}},
        {"title": "Project Tasks Due",        "count": frappe.db.count("Task",              {"status": "Open", "exp_end_date": now_date}),                 "route": "Task",              "filter": {"status": "Open", "exp_end_date": now_date}},
        {"title": "In Progress Installations","count": frappe.db.count("Installation Note", {"status": "Draft"}),                                          "route": "Installation Note", "filter": {"status": "Draft"}}
    ]
    for d in frappe.db.get_all("Project", filters={"status": "Open"}, fields=["name", "project_name", "expected_end_date"]):
        pending_tasks.append({"doctype": "Project", "type": "Project Execution", "client": d.project_name, "ref": d.name, "date": d.expected_end_date, "tat": 0})
    for d in frappe.db.get_all("Installation Note", filters={"status": "Draft"}, fields=["name", "customer_name", "inst_date"]):
        pending_tasks.append({"doctype": "Installation Note", "type": "Install System", "client": d.customer_name, "ref": d.name, "date": d.inst_date, "tat": 0})
    tasks_route  = "Project"
    tasks_filter = {"status": "Open"}
    performance  = {
        "label1": "Projects Open",          "value1": frappe.db.count("Project",           {"status": "Open"}),
        "label2": "Pending Installations",  "value2": frappe.db.count("Installation Note", {"status": "Draft"}),
        "label3": "Completed Today",        "value3": frappe.db.count("Installation Note", {"inst_date": now_date, "status": "Submitted"})
    }
    actions = {"btn1_label": "New Installation", "btn1_type": "new_doc", "btn1_target": "Installation Note", "btn2_label": "View Projects", "btn2_type": "list_route", "btn2_target": "Project", "btn2_filter": {"status": "Open"}, "btn2_visible": True}


# ════════════════════════════════════════════════════════════
# 11. OM PRAKASH / AMAN / OMKAR  —  Liaisoning & Sync  (Step 12)
# ════════════════════════════════════════════════════════════
elif user in ["omprakash.sadbhavrenewables@gmail.com", "aman.sadbhavrenewable@gmail.com", "omkar.sadbhav@gmail.com"]:
    process_label = name_display + " - Liaisoning & Sync"
    SYNC_DOCTYPE  = "Liaisoning And Synchronization"

    if frappe.db.exists("DocType", SYNC_DOCTYPE):
        kpi_data = [
            {"title": "Pending Sync",          "count": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "New"}),            "tat": 0, "route": SYNC_DOCTYPE, "filter": {"liaisoning_status": "New"}},
            {"title": "In Process",            "count": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "In Process"}),     "tat": 0, "route": SYNC_DOCTYPE, "filter": {"liaisoning_status": "In Process"}},
            {"title": "Docs Action Needed",    "count": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "Docs Completed"}), "tat": 0, "route": SYNC_DOCTYPE, "filter": {"liaisoning_status": "Docs Completed"}},
            {"title": "Govt Sync Completed",   "count": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "Completed"}),      "tat": 0, "route": SYNC_DOCTYPE, "filter": {"liaisoning_status": "Completed"}}
        ]
        plan_data = [
            {"title": "Docs to Upload",       "count": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "Docs Completed"}),      "route": SYNC_DOCTYPE, "filter": {"liaisoning_status": "Docs Completed"}},
            {"title": "Meter Change Pending", "count": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "Submit to Division"}),   "route": SYNC_DOCTYPE, "filter": {"liaisoning_status": "Submit to Division"}},
            {"title": "Agreements Pending",   "count": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "Agreement Signed"}),     "route": SYNC_DOCTYPE, "filter": {"liaisoning_status": "Agreement Signed"}}
        ]
        for d in frappe.db.get_all(SYNC_DOCTYPE, filters={"liaisoning_status": ["in", ["New", "In Process"]]}, fields=["name", "customer_name", "posting_date"]):
            pending_tasks.append({"doctype": SYNC_DOCTYPE, "type": "Liaisoning Task", "client": d.customer_name, "ref": d.name, "date": d.posting_date, "tat": 0})
        tasks_route  = SYNC_DOCTYPE
        tasks_filter = {"liaisoning_status": "New"}
        performance  = {
            "label1": "Syncs Completed",    "value1": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "Completed", "completed_date": [">=", month_start]}),
            "label2": "In Process Now",     "value2": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "In Process"}),
            "label3": "Agreements Signed",  "value3": frappe.db.count(SYNC_DOCTYPE, {"liaisoning_status": "Agreement Signed", "completed_date": [">=", month_start]})
        }
        actions = {"btn1_label": "Open Sync Queue", "btn1_type": "list_route", "btn1_target": SYNC_DOCTYPE, "btn1_filter": {"liaisoning_status": "New"}, "btn2_visible": False}
    else:
        kpi_data   = [{"title": "Doctype Not Found", "count": 0, "tat": 0, "route": "", "filter": {}}]
        plan_data  = [{"title": "Check Doctype Name", "count": 0, "route": "", "filter": {}}]
        performance = {"label1": "Error", "value1": "0", "label2": "Error", "value2": "0", "label3": "Error", "value3": "0"}
        actions    = {"btn2_visible": False}


# ════════════════════════════════════════════════════════════
# 12. FIELD TEAM  —  Catch-All  (Step 2)
#     Daneshwar, Ravikant, Prahlad, Vivek + any unknown user
# ════════════════════════════════════════════════════════════
else:
    process_label = name_display + " - Site Survey & Lead Gen"
    kpi_data = [
        {"title": "Leads Generated",  "count": frappe.db.count("Lead",        {"lead_owner": user}),                        "tat": get_avg_tat("Lead",        {"lead_owner": user}),                        "route": "Lead",        "filter": {"lead_owner": user}},
        {"title": "Surveys Pending",  "count": frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Open"}),     "tat": get_avg_tat("Site Survey", {"surveyed_by": user, "status": "Open"}),     "route": "Site Survey", "filter": {"surveyed_by": user, "status": "Open"}},
        {"title": "Surveys Done",     "count": frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Completed"}),"tat": 0,                                                                        "route": "Site Survey", "filter": {"surveyed_by": user, "status": "Completed"}}
    ]
    plan_data = [
        {"title": "Surveys Today",    "count": frappe.db.count("Site Survey", {"survey_date": now_date, "surveyed_by": user}),        "route": "Site Survey", "filter": {"survey_date": now_date, "surveyed_by": user}},
        {"title": "Open Leads",       "count": frappe.db.count("Lead",        {"lead_owner": user, "status": "Open"}),                "route": "Lead",        "filter": {"lead_owner": user, "status": "Open"}},
        {"title": "Completed Today",  "count": frappe.db.count("Site Survey", {"completed_date": now_date, "surveyed_by": user}),     "route": "Site Survey", "filter": {"completed_date": now_date, "surveyed_by": user}}
    ]
    for d in frappe.db.get_all("Site Survey", filters={"surveyed_by": user, "status": "Open"}, fields=["name", "lead_name", "exp_nxstp_dt", "tat_days"]):
        pending_tasks.append({"doctype": "Site Survey", "type": "Conduct Survey", "client": d.lead_name, "ref": d.name, "date": d.exp_nxstp_dt, "tat": d.tat_days or 0})
    tasks_route  = "Site Survey"
    tasks_filter = {"surveyed_by": user, "status": "Open"}
    tl = frappe.db.count("Lead",        {"lead_owner": user})
    ts = frappe.db.count("Site Survey", {"surveyed_by": user})
    performance  = {
        "label1": "Surveys Done",     "value1": frappe.db.count("Site Survey", {"surveyed_by": user, "status": "Completed", "completed_date": [">=", month_start]}),
        "label2": "Leads Generated",  "value2": frappe.db.count("Lead",        {"lead_owner": user, "creation": [">=", month_start]}),
        "label3": "Conversion %",     "value3": safe_pct(ts, tl)
    }
    actions = {"btn1_label": "Generate Lead", "btn1_type": "new_doc", "btn1_target": "Lead", "btn2_label": "Conduct Survey", "btn2_type": "new_doc", "btn2_target": "Site Survey", "btn2_visible": True}


# ── Sort pending queue by date — fix: convert to str to avoid
#    TypeError when db returns datetime.date instead of string
def get_sort_key(task):
    d = task.get("date")
    if d is None:
        return "9999-12-31"
    return str(d)

pending_tasks.sort(key=get_sort_key)

# ── Deduplicate by ref + task type ───────────────────────────
seen_keys     = []
deduped_tasks = []
for t in pending_tasks:
    key = (t.get("ref") or "") + "|" + (t.get("type") or "")
    if key not in seen_keys:
        seen_keys.append(key)
        deduped_tasks.append(t)

# ── Recent Activity ───────────────────────────────────────────
activities = frappe.db.get_all("Version", filters={"owner": user}, fields=["ref_doctype", "docname", "creation"], limit=5, order_by="creation desc")

# ── Final Response ────────────────────────────────────────────
frappe.response["message"] = {
    "role":          process_label,
    "employee":      employee,
    "kpi":           kpi_data,
    "plan":          plan_data,
    "tasks":         deduped_tasks[:10],
    "tasks_route":   tasks_route,
    "tasks_filter":  tasks_filter,
    "activities":    activities,
    "performance":   performance,
    "actions":       actions
}
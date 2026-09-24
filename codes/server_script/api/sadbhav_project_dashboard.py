# =====================================================
# SADBHAV RENEWABLE ERP — PROJECT DASHBOARD API
# Script Type : API  |  Method Name : project_test
# =====================================================

action     = frappe.form_dict.get("action", "get_dashboard")
project_id = frappe.form_dict.get("project_id", "")

# ─────────────────────────────────────────────────────
# HELPER: safe format date
# ─────────────────────────────────────────────────────
def fmt(d):
    if d:
        try:
            return frappe.utils.formatdate(str(d)[:10])
        except Exception:
            return str(d)[:10]
    return "Pending"

def safe_int(v):
    try:
        return int(v or 0)
    except Exception:
        return 0

# ─────────────────────────────────────────────────────
# ACTION 1: GET DASHBOARD LIST + STATS
# ─────────────────────────────────────────────────────
if action == "get_dashboard":

    projects = frappe.db.get_all(
        "Project",
        fields=["name", "customer", "status", "expected_end_date",
                "percent_complete", "modified"],
        order_by="creation desc"
    )

    ongoing_list   = []
    completed_list = []
    delayed_list   = []
    pending_list   = []
    received_list  = []
    result         = []
    today_date     = frappe.utils.getdate(frappe.utils.today())

    for p in projects:

        so = frappe.db.get_value(
            "Sales Order",
            {"project": p.name, "docstatus": 1},
            ["solar_capacity", "grand_total", "per_billed", "customer_name"],
            as_dict=True
        )
        if not so:
            so = {}

        cap_raw  = so.get("solar_capacity") or ""
        grand    = so.get("grand_total") or 0
        billed   = so.get("per_billed")  or 0
        pending  = grand * (100.0 - billed) / 100.0
        received = grand - pending
        cust     = so.get("customer_name") or p.customer or ""

        pending_list.append(pending)
        received_list.append(received)

        proj_status = p.status or "Open"
        if proj_status == "Open" and p.expected_end_date:
            if frappe.utils.getdate(p.expected_end_date) < today_date:
                proj_status = "Delayed"

        if proj_status == "Completed":
            completed_list.append(p.name)
        elif proj_status == "Delayed":
            delayed_list.append(p.name)
        else:
            ongoing_list.append(p.name)

        last_act = fmt(str(p.modified)[:10]) if p.modified else ""

        result.append({
            "name":               p.name,
            "customer":           cust,
            "status":             proj_status,
            "expected_end_date":  fmt(p.expected_end_date),
            "percent_complete":   p.percent_complete or 0,
            "solar_capacity":     str(cap_raw),
            "solar_capacity_raw": cap_raw,
            "pending_payment":    round(pending, 2),
            "last_activity":      last_act
        })

    frappe.response["message"] = {
        "projects": result,
        "stats": {
            "total":          len(result),
            "ongoing":        len(ongoing_list),
            "completed":      len(completed_list),
            "delayed":        len(delayed_list),
            "total_pending":  round(sum(pending_list), 2),
            "total_received": round(sum(received_list), 2),
            "overdue":        0
        }
    }

# ─────────────────────────────────────────────────────
# ACTION 2: GET PROJECT DETAIL
# ─────────────────────────────────────────────────────
elif action == "get_project_detail":

    if not project_id:
        frappe.response["message"] = {"error": "No project ID provided"}

    else:
        proj = frappe.db.get_value(
            "Project",
            project_id,
            ["name", "customer", "status", "expected_end_date",
             "percent_complete", "project_type", "owner"],
            as_dict=True
        )

        if not proj:
            frappe.response["message"] = {"error": "Project not found: " + project_id}

        else:
            project_owner_email = proj.owner or ""
            created_by_name = "N/A"
            if project_owner_email:
                fn = frappe.db.get_value("User", project_owner_email, "full_name")
                if fn:
                    created_by_name = fn

            so = frappe.db.get_value(
                "Sales Order",
                {"project": project_id, "docstatus": 1},
                ["name", "customer_name", "solar_capacity", "grand_total",
                 "per_billed", "per_advance", "plant_category", "manager",
                 "contact_mobile", "without_pay_reason", "transaction_date",
                 "lead", "site_survey", "proposal", "liaisoning_and_sync",
                 "delivery_date", "tat_days"],
                as_dict=True
            )
            if not so:
                so = {}

            # 🟢 Strictly initializing as dict to prevent Line 165 error
            lead = {}
            if so.get("lead"):
                ld = frappe.db.get_value(
                    "Lead",
                    so.get("lead"),
                    ["name", "lead_name", "mobile_no", "city", "state",
                     "creation_date", "company_name", "email_id",
                     "custom_address", "custom_pincode"],
                    as_dict=True
                )
                if ld:
                    lead = ld

            lead_address = ""
            addr_parts = []
            if lead.get("custom_address"):
                addr_parts.append(str(lead.get("custom_address")))
            if lead.get("city"):
                addr_parts.append(str(lead.get("city")))
            if lead.get("state"):
                addr_parts.append(str(lead.get("state")))
            if lead.get("custom_pincode"):
                addr_parts.append(str(lead.get("custom_pincode")))
            if addr_parts:
                lead_address = ", ".join(addr_parts)

            survey = {}
            ss_name = so.get("site_survey") or ""
            if ss_name:
                ss = frappe.db.get_value(
                    "Site Survey", ss_name,
                    ["name", "survey_date", "completed_date", "solar_capacity",
                     "location_details", "site_type", "plant_category"],
                    as_dict=True
                )
                if ss:
                    survey = ss
                    
            if not survey and lead.get("name"):
                ss2 = frappe.db.get_value(
                    "Site Survey",
                    {"lead": lead.get("name")},
                    ["name", "survey_date", "completed_date", "solar_capacity",
                     "location_details", "site_type", "plant_category"],
                    as_dict=True
                )
                if ss2:
                    survey = ss2

            if not lead_address and survey.get("location_details"):
                lead_address = str(survey.get("location_details"))

            quotation = {}
            q_name = so.get("proposal") or ""
            if q_name:
                qt = frappe.db.get_value(
                    "Quotation", q_name,
                    ["name", "transaction_date", "grand_total", "status"],
                    as_dict=True
                )
                if qt:
                    quotation = qt

            installation = {}
            if proj.get("customer"):
                try:
                    inst = frappe.db.get_value(
                        "Installation Note",
                        {"customer": proj.get("customer"), "docstatus": ["!=", 2]},
                        ["name", "inst_date", "status", "sla_due_date",
                         "complete_date", "stage_status", "complete_status", "tat_days"],
                        as_dict=True
                    )
                    if inst:
                        installation = inst
                except Exception:
                    pass

            sync_doc = {}
            if so.get("name"):
                try:
                    sd = frappe.db.get_value(
                        "Synchronization",
                        {"sales_order": so.get("name")},
                        ["name", "posting_date", "completed_date",
                         "liaisoning_status", "sla_due_date", "tat_days"],
                        as_dict=True
                    )
                    if sd: sync_doc = sd
                except Exception:
                    sd = frappe.db.get_value(
                        "Synchronization",
                        {"sales_order": so.get("name")},
                        ["name", "posting_date", "completed_date", "liaisoning_status"],
                        as_dict=True
                    )
                    if sd: sync_doc = sd

            dn_doc = {}
            if so.get("name"):
                dn_items = frappe.db.get_all(
                    "Delivery Note Item",
                    filters={"against_sales_order": so.get("name")},
                    fields=["parent"],
                    limit=1
                )
                if dn_items:
                    dn_name = dn_items[0].get("parent", "")
                    if dn_name:
                        try:
                            dn_raw = frappe.db.get_value(
                                "Delivery Note", dn_name,
                                ["name", "posting_date", "sla_due_date", "complete_date",
                                 "tat_days", "stage_status", "complete_status", "docstatus"],
                                as_dict=True
                            )
                        except Exception:
                            dn_raw = frappe.db.get_value(
                                "Delivery Note", dn_name,
                                ["name", "posting_date", "docstatus"],
                                as_dict=True
                            )
                        
                        if dn_raw and (dn_raw.get("docstatus") or 0) != 2:
                            dn_doc = dn_raw

            today_date = frappe.utils.getdate(frappe.utils.today())

            purchase_delay_days = 0
            if dn_doc.get("complete_status") == "Delayed":
                purchase_delay_days = safe_int(dn_doc.get("tat_days"))
            elif dn_doc.get("sla_due_date") and not dn_doc.get("complete_date"):
                due = frappe.utils.getdate(str(dn_doc.get("sla_due_date"))[:10])
                if due < today_date:
                    purchase_delay_days = frappe.utils.date_diff(today_date, due)

            install_delay_days = 0
            if installation.get("complete_status") == "Delayed":
                install_delay_days = safe_int(installation.get("tat_days"))
            elif installation.get("sla_due_date") and not installation.get("complete_date"):
                due_i = frappe.utils.getdate(str(installation.get("sla_due_date"))[:10])
                if due_i < today_date:
                    install_delay_days = frappe.utils.date_diff(today_date, due_i)

            sync_delay_days = safe_int(sync_doc.get("tat_days")) if sync_doc else 0

            # 🟢 FIX: Avoid += to bypass _inplacevar_ error
            total_delay_days = purchase_delay_days + install_delay_days + sync_delay_days

            expected_days_val = "N/A"
            if so.get("tat_days"):
                expected_days_val = str(safe_int(so.get("tat_days"))) + " Days"

            payments = []
            if so.get("name"):
                payments = frappe.db.get_all(
                    "Payment Schedule",
                    filters={"parent": so.get("name"), "parenttype": "Sales Order"},
                    fields=["due_date", "payment_amount", "outstanding", "invoice_portion"],
                    order_by="idx asc"
                )

            payment_received_count = 0
            payment_received_amt   = 0
            for pay in payments:
                amt  = pay.get("payment_amount") or 0
                out  = pay.get("outstanding") or 0
                paid = amt - out
                if paid > 0:
                    # 🟢 FIX: Avoid += operator
                    payment_received_count = payment_received_count + 1
                    payment_received_amt = payment_received_amt + paid

            followups = []
            if lead.get("name"):
                notes = frappe.db.get_all(
                    "CRM Note",
                    filters={"parent": lead.get("name"), "parenttype": "Lead"},
                    fields=["name", "note", "added_on", "added_by"],
                    order_by="added_on desc",
                    limit=6
                )
                for n in notes:
                    n["fu_type"] = "Lead Note"
                    followups.append(n)

            if so.get("name"):
                rdl = frappe.db.get_all(
                    "Remark-Delay Log",
                    filters={"parent": so.get("name"), "parenttype": "Sales Order"},
                    fields=["name", "creation", "owner"],
                    order_by="creation desc",
                    limit=4
                )
                for dl in rdl:
                    followups.append({
                        "name":     dl.get("name"),
                        "note":     "Remark / Delay recorded",
                        "added_on": dl.get("creation"),
                        "added_by": dl.get("owner"),
                        "fu_type":  "Delay Alert"
                    })

            # 🟢 TEAM FIX: Fetch from custom_team_members table
            team = []
            try:
                p_doc = frappe.get_doc("Project", project_id)
                child_table = p_doc.get("custom_team_members") or []
                
                for t_row in child_table:
                    team.append({
                        "user": t_row.get("member") or "",
                        "full_name": t_row.get("member_name") or "Unknown",
                        "role": t_row.get("category") or "Team Member"
                    })
            except Exception as e:
                pass

            project_photos = frappe.db.get_all(
                "File",
                filters={"attached_to_doctype": "Project", "attached_to_name": project_id},
                fields=["name", "file_name", "file_url", "creation"],
                order_by="creation desc", limit=20
            )

            survey_photos = []
            if survey.get("name"):
                survey_photos = frappe.db.get_all(
                    "File",
                    filters={"attached_to_doctype": "Site Survey", "attached_to_name": survey.get("name")},
                    fields=["name", "file_name", "file_url", "creation"],
                    order_by="creation desc", limit=20
                )

            all_photos = []
            seen_names = []
            for ph in survey_photos:
                all_photos.append(ph)
                seen_names.append(ph.get("name"))
            for ph in project_photos:
                if ph.get("name") not in seen_names:
                    all_photos.append(ph)

            # 🟢 MANAGER FIX: Fetching Manager safely
            manager_display = so.get("manager") or ""
            if not manager_display:
                try:
                    p_doc_m = frappe.get_doc("Project", project_id)
                    manager_display = p_doc_m.get("custom_project_manager") or ""
                except Exception:
                    pass

            if manager_display:
                m_name = frappe.db.get_value("User", manager_display, "full_name")
                if m_name:
                    manager_display = m_name

            key_dates = {
                "Lead Generated":   fmt(str(lead.get("creation_date",""))[:10]) if lead.get("creation_date") else "Pending",
                "Survey Completed": fmt(survey.get("completed_date")),
                "PO Created":       fmt(so.get("transaction_date")),
                "Purchase Done":    fmt(dn_doc.get("posting_date")) if dn_doc else "Pending",
                "Install Started":  fmt(installation.get("inst_date")) if installation else "Pending",
                "Sync Process":     fmt(sync_doc.get("posting_date")) if sync_doc else "Pending",
                "O&M Started":      "Pending",
                "Finance Clearance":"Pending"
            }

            # 🟢 STAGES FIXED: Renamed to match exactly what you asked for
            stages = [
                {"label": "Lead",            "done": bool(lead), "current": False, "sub": "Generated"},
                {"label": "Survey",          "done": bool(survey), "current": False, "sub": "Site Visit"},
                {"label": "Proposal",        "done": bool(quotation), "current": False, "sub": "Sent"},
                {"label": "Sales Order",     "done": bool(so.get("name")), "current": False, "sub": "Order"},
                {"label": "Dispatch",        "done": bool(dn_doc), "current": (bool(so.get("name")) and not bool(dn_doc)), "sub": "Material"},
                {"label": "Installation",    "done": bool(installation) and installation.get("status") == "Submitted", "current": (bool(dn_doc) and not installation), "sub": "On Site"},
                {"label": "Synchronization", "done": bool(sync_doc) and sync_doc.get("liaisoning_status") in ["Synchronized","Completed"], "current": (bool(installation) and not sync_doc), "sub": "DISCOM"},
                {"label": "Finance",         "done": False, "current": False, "sub": "Billing"},
                {"label": "O&M",             "done": False, "current": False, "sub": "Service"}
            ]

            current_stage = "Lead"
            for sg in stages:
                if sg["done"]:
                    current_stage = sg["label"]

            project_detail = {
                "name":              proj.get("name"),
                "customer":          so.get("customer_name") or proj.get("customer") or "N/A",
                "created_by":        created_by_name,
                "address":           lead_address or "N/A",
                "status":            proj.get("status") or "Open",
                "expected_end_date": fmt(proj.get("expected_end_date")),
                "percent_complete":  proj.get("percent_complete") or 0,
                "project_type":      proj.get("project_type") or "N/A",
                "solar_capacity":    str(so.get("solar_capacity") or "N/A"),
                "plant_category":    str(so.get("plant_category") or "N/A"),
                "contact_mobile":    str(so.get("contact_mobile") or lead.get("mobile_no") or "N/A"),
                "grand_total":       so.get("grand_total") or 0,
                "per_advance":       so.get("per_advance") or 0,
                "finance_type":      str(so.get("without_pay_reason") or "N/A"),
                "manager":           manager_display or "N/A",
                "lead_id":           lead.get("name", ""),
                "so_id":             so.get("name", ""),
                "survey_id":         survey.get("name", ""),
                "quotation_id":      quotation.get("name", ""),
                "installation_id":   installation.get("name", "") if installation else "",
                "sync_id":           sync_doc.get("name", "") if sync_doc else ""
            }

            delay_data = {
                "purchase_delay":       purchase_delay_days,
                "purchase_status":      str(dn_doc.get("complete_status") or "N/A") if dn_doc else "N/A",
                "install_delay":        install_delay_days,
                "install_status":       str(installation.get("complete_status") or "N/A") if installation else "N/A",
                "install_date":         fmt(installation.get("inst_date")) if installation else "Pending",
                "sync_delay":           sync_delay_days,
                "sync_status":          str(sync_doc.get("liaisoning_status") or "N/A") if sync_doc else "N/A",
                "total_delay":          total_delay_days
            }

            summary_data = {
                "expected_days":     expected_days_val,
                "payment_received":  payment_received_count,
                "payment_recv_amt":  round(payment_received_amt, 2),
                "purchase_delay":    purchase_delay_days,
                "site_delay":        install_delay_days,
                "grand_total":       so.get("grand_total") or 0
            }

            frappe.response["message"] = {
                "project":       project_detail,
                "stages":        stages,
                "key_dates":     key_dates,
                "followups":     followups,
                "payments":      payments,
                "team":          team,
                "photos":        all_photos,
                "current_stage": current_stage,
                "delay_data":    delay_data,
                "summary_data":  summary_data
            }

# ─────────────────────────────────────────────────────
# ACTION 3: GET STAGE FOLLOWUPS (CRM Sidebar)
# ─────────────────────────────────────────────────────
elif action == "get_stage_followups":
    stage = frappe.form_dict.get("stage")
    data = []

    if stage == "Lead":
        data = frappe.db.get_all("CRM Note",
            filters={"parenttype": "Lead"},
            fields=["parent", "added_on", "note", "added_by"],
            order_by="added_on desc", limit=20)
        for d in data:
            lead_name = frappe.db.get_value("Lead", d.get("parent"), "lead_name")
            d["parent_name"] = lead_name or d.get("parent")
    else:
        data = frappe.db.get_all("Remark-Delay Log",
            filters={"parenttype": stage},
            fields=["parent", "creation as added_on", "remark as note", "owner as added_by"],
            order_by="creation desc", limit=20)
        for d in data:
            p_name = None
            if stage == "Site Survey":
                p_name = frappe.db.get_value("Site Survey", d.get("parent"), "lead_name")
            elif stage == "Quotation":
                p_name = frappe.db.get_value("Quotation", d.get("parent"), "customer_name")
            elif stage == "Sales Order":
                p_name = frappe.db.get_value("Sales Order", d.get("parent"), "customer_name")
            elif stage == "Project":
                p_name = frappe.db.get_value("Project", d.get("parent"), "customer")
            d["parent_name"] = p_name or d.get("parent")

    # 🟢 FIX: Fetching User Full Name for the "By" Column
    for d in data:
        user_email = d.get("added_by")
        if user_email:
            full_name = frappe.db.get_value("User", user_email, "full_name")
            d["added_by_name"] = full_name or user_email
        else:
            d["added_by_name"] = "Unknown"

    frappe.response["message"] = data

# ─────────────────────────────────────────────────────
# ACTION 4: GET ALL PHOTOS (for modal View All)
# ─────────────────────────────────────────────────────
elif action == "get_all_photos":
    survey_id_param = frappe.form_dict.get("survey_id", "")
    all_ph = []

    if survey_id_param:
        sv_ph = frappe.db.get_all(
            "File",
            filters={"attached_to_doctype": "Site Survey", "attached_to_name": survey_id_param},
            fields=["name", "file_name", "file_url", "creation"],
            order_by="creation desc"
        )
        all_ph = sv_ph

    if project_id:
        pr_ph = frappe.db.get_all(
            "File",
            filters={"attached_to_doctype": "Project", "attached_to_name": project_id},
            fields=["name", "file_name", "file_url", "creation"],
            order_by="creation desc"
        )
        existing = [p.get("name") for p in all_ph]
        for ph in pr_ph:
            if ph.get("name") not in existing:
                all_ph.append(ph)

    frappe.response["message"] = all_ph

else:
    frappe.response["message"] = {"error": "Unknown action: " + str(action)}
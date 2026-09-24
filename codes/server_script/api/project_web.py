# =====================================================
# SADBHAV RENEWABLE ERP — PROJECT DASHBOARD API
# Script Type : API
# Version     : v11 (Sync Status Edition)
# =====================================================

action     = frappe.form_dict.get("action", "get_dashboard")
project_id = frappe.form_dict.get("project_id", "")

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

def get_user_name(email):
    if not email:
        return email
    try:
        fn = frappe.db.get_value("User", email, "full_name")
        return fn or email
    except Exception:
        return email

def get_sales_order(project_id, customer=None):
    so_fields = [
        "name", "customer", "customer_name", "grand_total", "rounded_total",
        "per_billed", "per_advance", "transaction_date", "docstatus",
        "proposal", "site_survey", "liaisoning_and_sync", "project",
        "solar_capacity", "plant_category", "without_pay_reason",
        "delivery_date", "manager", "lead",
    ]
    so_optional = ["contact_mobile", "tat_days", "project_manager"]
    for f in so_optional:
        try:
            exists = frappe.db.sql(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tabSales Order' "
                "AND COLUMN_NAME=%s", (f,))[0][0]
            if exists:
                so_fields.append(f)
        except Exception:
            pass

    so = {}
    if project_id:
        s1 = frappe.db.get_value("Sales Order",
            {"project": project_id, "docstatus": ["!=", 2]},
            so_fields, as_dict=True)
        if s1:
            return s1
    if customer:
        s2 = frappe.db.get_value("Sales Order",
            {"customer": customer, "docstatus": ["!=", 2]},
            so_fields, as_dict=True)
        if s2:
            return s2
    return so or {}

def get_quotation(so):
    quot_fields = [
        "name", "transaction_date", "grand_total", "status",
        "solar_capacity", "customer_name", "party_name", "quotation_to"
    ]
    quot_id = so.get("proposal") or ""
    if quot_id:
        qt = frappe.db.get_value("Quotation", quot_id, quot_fields, as_dict=True)
        if qt:
            return qt
    if so.get("customer_name"):
        qt2 = frappe.db.get_value("Quotation",
            {"customer_name": so.get("customer_name"), "docstatus": ["!=", 2]},
            quot_fields, as_dict=True)
        if qt2:
            return qt2
    return {}

def get_lead(quotation, so, customer=None):
    lead_fields = [
        "name", "lead_name", "mobile_no", "city", "state", "creation_date",
        "company_name", "email_id", "custom_address", "custom_pincode",
        "solar_capacity"
    ]
    lead_id = ""
    if quotation.get("quotation_to") == "Lead" and quotation.get("party_name"):
        lead_id = quotation.get("party_name")
    if not lead_id and quotation.get("party_name"):
        lead_id = quotation.get("party_name")
    if lead_id:
        ld = frappe.db.get_value("Lead", lead_id, lead_fields, as_dict=True)
        if ld:
            return ld
    if so.get("lead"):
        ld2 = frappe.db.get_value("Lead", so.get("lead"), lead_fields, as_dict=True)
        if ld2:
            return ld2
    if so.get("customer_name"):
        qt_rows = frappe.db.get_all("Quotation",
            filters={"customer_name": so.get("customer_name"),
                     "quotation_to": "Lead", "docstatus": ["!=", 2]},
            fields=["name", "party_name"], limit=5)
        for qt_row in qt_rows:
            if qt_row.get("party_name"):
                ld5 = frappe.db.get_value("Lead", qt_row.get("party_name"),
                    lead_fields, as_dict=True)
                if ld5:
                    return ld5
    if so.get("customer") or customer:
        cust = so.get("customer") or customer
        try:
            ld6 = frappe.db.sql("""
                SELECT """ + ", ".join(lead_fields) + """
                FROM `tabLead`
                WHERE lead_name LIKE %s OR company_name LIKE %s
                LIMIT 1
            """, ("%" + cust + "%", "%" + cust + "%"), as_dict=1)
            if ld6:
                return ld6[0]
        except Exception:
            pass
    return {}

def get_survey(so, lead):
    survey_fields = [
        "name", "survey_date", "completed_date", "solar_capacity",
        "location_details", "lead_name", "contact_number", "lead"
    ]
    ss_id = so.get("site_survey") or ""
    if ss_id:
        ss = frappe.db.get_value("Site Survey", ss_id, survey_fields, as_dict=True)
        if ss:
            return ss
    if lead.get("name"):
        ss2 = frappe.db.get_value("Site Survey",
            {"lead": lead.get("name")}, survey_fields, as_dict=True)
        if ss2:
            return ss2
    return {}

def get_delivery_note(so, customer=None):
    dn_base  = ["name", "posting_date", "docstatus"]
    dn_extra = ["sla_due_date", "complete_date", "tat_days", "stage_status", "complete_status"]

    def fetch_dn(dn_name):
        try:
            dn_raw = frappe.db.get_value("Delivery Note", dn_name,
                dn_base + dn_extra, as_dict=True)
        except Exception:
            dn_raw = frappe.db.get_value("Delivery Note", dn_name,
                dn_base, as_dict=True)
        if dn_raw and (dn_raw.get("docstatus") or 0) != 2:
            return dn_raw
        return {}

    dn_doc = {}
    if so.get("name"):
        dn_items = frappe.db.get_all("Delivery Note Item",
            filters={"against_sales_order": so.get("name")},
            fields=["parent"], limit=1)
        if dn_items:
            dn_doc = fetch_dn(dn_items[0].get("parent", ""))
    if not dn_doc.get("name") and customer:
        dn_name = frappe.db.get_value("Delivery Note",
            {"customer": customer, "docstatus": ["!=", 2]}, "name")
        if dn_name:
            dn_doc = fetch_dn(dn_name)
    return dn_doc

def get_sync(so, lead, project_id=None, customer=None):
    sync_base = [
        "name", "posting_date", "completed_date", "liaisoning_status",
        "customer", "customer_name", "sales_order",
        "lead", "project", "site_survey", "solar_capacity",
        "stage_status", "complete_status", "complete_date", "sla_due_date",
    ]
    sync_extra = ["tat_days"]

    def safe_sync_fields():
        fields = sync_base[:]
        for f in sync_extra:
            try:
                exists = frappe.db.sql(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA=DATABASE() "
                    "AND TABLE_NAME='tabLiaisoning And Synchronization' "
                    "AND COLUMN_NAME=%s", (f,))[0][0]
                if exists:
                    fields.append(f)
            except Exception:
                pass
        return fields

    def fetch_sync(filters):
        try:
            return frappe.db.get_value("Liaisoning And Synchronization",
                filters, safe_sync_fields(), as_dict=True) or {}
        except Exception:
            try:
                return frappe.db.get_value("Liaisoning And Synchronization",
                    filters, sync_base, as_dict=True) or {}
            except Exception:
                return {}

    sync_doc = {}
    sync_id = so.get("liaisoning_and_sync") or ""
    if sync_id:
        sd = fetch_sync({"name": sync_id})
        if sd.get("name"):
            return sd
    if so.get("name"):
        sd2 = fetch_sync({"sales_order": so.get("name")})
        if sd2.get("name"):
            return sd2
    if lead.get("name"):
        sd3 = fetch_sync({"lead": lead.get("name")})
        if sd3.get("name"):
            return sd3
    if project_id:
        sd4 = fetch_sync({"project": project_id})
        if sd4.get("name"):
            return sd4
    if customer:
        sd5 = fetch_sync({"customer": customer})
        if sd5.get("name"):
            return sd5
    return sync_doc

def build_address(lead, survey):
    addr_parts = []
    for f in ["custom_address", "city", "state", "custom_pincode"]:
        v = lead.get(f, "")
        if v:
            addr_parts.append(str(v))
    addr = ", ".join(addr_parts)
    if not addr and survey.get("location_details"):
        addr = str(survey.get("location_details"))
    return addr or "N/A"

def resolve_capacity(proj, so, lead=None, survey=None, quotation=None):
    lead      = lead      or {}
    survey    = survey    or {}
    quotation = quotation or {}
    for val in [
        so.get("solar_capacity"),
        lead.get("solar_capacity"),
        survey.get("solar_capacity"),
        quotation.get("solar_capacity"),
        proj.get("solar_capacity"),
        proj.get("custom_project_capacity"),
        proj.get("custom_solar_capacity"),
        proj.get("capacity_kw")
    ]:
        cap = str(val or "").strip()
        if cap and cap not in ["", "None", "null", "-", "\u2014", "N/A"]:
            return cap
    return ""

# ─────────────────────────────────────────────────────────────────
# HELPER: Resolve status
# ─────────────────────────────────────────────────────────────────
def resolve_status(stage_status, complete_status, raw_status, expected_end_date, today_date):
    stage_status    = str(stage_status or "").strip().title()
    complete_status = str(complete_status or "").strip().title()
    proj_status     = str(raw_status or "Open").strip().title()

    if stage_status == "Completed":
        return "Completed (Delayed)" if complete_status == "Delayed" else "Completed"
    elif stage_status == "Overdue":
        return "Delayed"
    elif stage_status == "Open":
        return "Open"
    elif stage_status:
        return stage_status
    else:
        if proj_status in ["Completed", "Cancelled"]:
            return proj_status
        if expected_end_date:
            try:
                if frappe.utils.getdate(expected_end_date) < today_date:
                    return "Delayed"
            except Exception:
                pass
        return proj_status or "Open"

try:
    # ─────────────────────────────────────────────────────
    # ACTION 1: GET DASHBOARD
    # STATUS LOGIC:
    #   sync doc EXISTS  → use sync_doc.stage_status
    #   sync doc MISSING → always "Open" (project not yet
    #                      reached synchronization stage)
    # ─────────────────────────────────────────────────────
    if action == "get_dashboard":

        fetch_fields = [
            "name", "customer", "status", "expected_end_date",
            "percent_complete", "modified", "stage_status", "complete_status"
        ]
        for f in ["solar_capacity", "custom_solar_capacity", "custom_project_capacity", "capacity_kw"]:
            try:
                exists = frappe.db.sql(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tabProject' "
                    "AND COLUMN_NAME=%s", (f,))[0][0]
                if exists:
                    fetch_fields.append(f)
            except Exception:
                pass

        projects = frappe.db.get_all(
            "Project",
            fields=fetch_fields,
            order_by="creation desc",
            limit_page_length=5000
        )

        ongoing_list               = []
        completed_list             = []
        delayed_list               = []
        pending_list               = []
        received_list              = []
        overdue_list               = []
        installation_completed_list = []
        sync_completed_list         = []
        ongoing_kpi_list            = []
        delayed_kpi_list            = []
        result                     = []
        today_date     = frappe.utils.getdate(frappe.utils.today())

        for p in projects:
            so        = get_sales_order(p.name, customer=p.customer)
            quotation = get_quotation(so)
            lead      = get_lead(quotation, so, customer=p.customer)
            sync_doc  = get_sync(so, lead, project_id=p.name, customer=p.customer)

            cap_str  = resolve_capacity(p, so, lead=lead, quotation=quotation)
            grand    = so.get("grand_total") or 0
            billed   = so.get("per_billed") or 0
            pending  = grand * (100.0 - billed) / 100.0
            received = grand - pending
            cust     = so.get("customer_name") or p.customer or ""

            pending_list.append(pending)
            received_list.append(received)

            proj_overdue = 0
            if so.get("name"):
                try:
                    pay_schedules = frappe.db.get_all("Payment Schedule",
                        filters={"parent": so.get("name"), "parenttype": "Sales Order"},
                        fields=["due_date", "outstanding"])
                    for ps in pay_schedules:
                        p_due = ps.get("due_date")
                        p_out = ps.get("outstanding")
                        if p_due and p_out:
                            if frappe.utils.getdate(p_due) < today_date:
                                try:
                                    proj_overdue = proj_overdue + float(p_out)
                                except Exception:
                                    pass
                except Exception:
                    pass

            overdue_list.append(proj_overdue)

            # ── STATUS BADGE LOGIC ─────────────────────────────
            # Table + list view: use Project doctype status directly
            proj_status = (p.status or "Open").strip()

            if proj_status == "Completed":
                completed_list.append(p.name)
            elif proj_status in ["Delayed", "Completed (Delayed)", "Overdue"]:
                delayed_list.append(p.name)
            else:
                ongoing_list.append(p.name)

            # ── KPI COUNTS — match exactly what list filters show ──
            # Ongoing KPI   → Project.status == "Open"
            if (p.status or "").strip() == "Open":
                ongoing_kpi_list.append(p.name)

            # Delayed KPI   → Project.complete_status == "Delayed"
            if (p.complete_status or "").strip() == "Delayed":
                delayed_kpi_list.append(p.name)

            # Installation Completed KPI → Project.status == "Completed"
            if (p.status or "").strip() == "Completed":
                installation_completed_list.append(p.name)

            last_act = fmt(str(p.modified)[:10]) if p.modified else ""

            # Payment received % — directly from SO.per_advance (already in percent)
            pay_pct = round(float(so.get("per_advance") or 0), 1)

            result.append({
                "name":               p.name,
                "customer":           cust,
                "status":             proj_status,
                "complete_status":    str(p.complete_status or ""),
                "expected_end_date":  fmt(p.expected_end_date),
                "percent_complete":   p.percent_complete or 0,
                "solar_capacity":     cap_str,
                "solar_capacity_raw": cap_str,
                "pending_payment":    round(pending, 2),
                "payment_received":   round(received, 2),
                "payment_pct":        pay_pct,
                "plant_category":     str(so.get("plant_category") or ""),
                "last_activity":      last_act
            })

        # Sync completed — direct SQL count to match list filter exactly
        # "complete_status Is Set" = complete_status is not null and not empty
        sync_completed_count = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabLiaisoning And Synchronization`
            WHERE complete_status IS NOT NULL AND complete_status != ''
        """)[0][0] or 0

        frappe.response["message"] = {
            "projects": result,
            "stats": {
                "total":                    len(result),
                "ongoing":                  len(ongoing_kpi_list),
                "completed":                len(completed_list),
                "delayed":                  len(delayed_kpi_list),
                "total_pending":            round(sum(pending_list), 2),
                "total_received":           round(sum(received_list), 2),
                "overdue":                  round(sum(overdue_list), 2),
                "installation_completed":   len(installation_completed_list),
                "sync_completed":           sync_completed_count
            }
        }

    # ─────────────────────────────────────────────────────
    # ACTION 2: GET PROJECT DETAIL
    # STATUS BADGE:
    #   sync doc EXISTS  → sync_doc.stage_status
    #   sync doc MISSING → "Open"
    # ─────────────────────────────────────────────────────
    elif action == "get_project_detail":

        if not project_id:
            frappe.response["message"] = {"error": "No project ID provided"}

        elif not frappe.db.exists("Project", project_id):
            frappe.response["message"] = {"error": "Project not found: " + project_id}

        else:
            pfields = [
                "name", "customer", "status", "expected_end_date",
                "percent_complete", "project_type", "owner", "bill_amt",
                "stage_status", "complete_status", "actual_start_date",
                "actual_end_date", "expected_start_date"
            ]
            for f in ["solar_capacity", "custom_solar_capacity", "custom_project_capacity", "capacity_kw"]:
                try:
                    exists = frappe.db.sql(
                        "SELECT COUNT(*) FROM information_schema.COLUMNS "
                        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tabProject' "
                        "AND COLUMN_NAME=%s", (f,))[0][0]
                    if exists:
                        pfields.append(f)
                except Exception:
                    pass

            proj = frappe.db.get_value("Project", project_id, pfields, as_dict=True)

            created_by_name    = get_user_name(proj.owner or "")
            proj_manager_email = ""
            proj_manager_name  = "N/A"
            try:
                p_doc = frappe.get_doc("Project", project_id)
                proj_manager_email = p_doc.get("custom_project_manager") or ""
            except Exception:
                pass
            if proj_manager_email:
                proj_manager_name = get_user_name(proj_manager_email)

            customer   = proj.get("customer") or ""
            today_date = frappe.utils.getdate(frappe.utils.today())

            so        = get_sales_order(project_id, customer=customer)
            quotation = get_quotation(so)
            lead      = get_lead(quotation, so, customer=customer)
            survey    = get_survey(so, lead)
            dn_doc    = get_delivery_note(so, customer=customer)
            sync_doc  = get_sync(so, lead, project_id=project_id, customer=customer)

            proj_is_completed = (proj.get("status") or "").strip().title() == "Completed"
            sync_is_done = (
                bool(sync_doc.get("name")) and
                str(sync_doc.get("stage_status") or "").strip().title() == "Completed"
            )

            lead_address     = build_address(lead, survey)
            cap_str2         = resolve_capacity(proj, so, lead=lead, survey=survey, quotation=quotation)
            project_bill_amt = proj.get("bill_amt") or 0

            # Delay calculations
            purchase_delay_days = 0
            if dn_doc.get("complete_status") == "Delayed":
                purchase_delay_days = safe_int(dn_doc.get("tat_days"))
            elif dn_doc.get("sla_due_date") and not dn_doc.get("complete_date"):
                due = frappe.utils.getdate(str(dn_doc.get("sla_due_date"))[:10])
                if due < today_date:
                    purchase_delay_days = frappe.utils.date_diff(today_date, due)

            install_delay_days = 0
            if proj.get("stage_status") == "Overdue":
                install_delay_days = safe_int(proj.get("tat_days") if proj.get("tat_days") else 0)
            elif proj.get("expected_end_date") and not proj_is_completed:
                exp_end = frappe.utils.getdate(proj.get("expected_end_date"))
                if exp_end < today_date:
                    install_delay_days = frappe.utils.date_diff(today_date, exp_end)

            sync_delay_days  = safe_int(sync_doc.get("tat_days")) if sync_doc.get("name") else 0
            total_delay_days = purchase_delay_days + install_delay_days + sync_delay_days

            expected_days_val = "N/A"
            if so.get("tat_days"):
                expected_days_val = str(safe_int(so.get("tat_days"))) + " Days"

            # Payments
            payments = []
            if so.get("name"):
                payments = frappe.db.get_all("Payment Schedule",
                    filters={"parent": so.get("name"), "parenttype": "Sales Order"},
                    fields=["due_date", "payment_amount", "outstanding", "invoice_portion"],
                    order_by="idx asc")

            payment_received_count = 0
            payment_received_amt   = 0
            payment_entries        = []
            if so.get("name"):
                try:
                    pe_count_refs = frappe.db.get_all("Payment Entry Reference",
                        filters={"reference_doctype": "Sales Order", "reference_name": so.get("name")},
                        fields=["parent", "allocated_amount"])
                    seen_pe = {}
                    for ref in pe_count_refs:
                        pe_n = ref.get("parent")
                        if pe_n:
                            seen_pe[pe_n] = seen_pe.get(pe_n, 0) + float(ref.get("allocated_amount") or 0)
                    for pe_n, amt in seen_pe.items():
                        ds = frappe.db.get_value("Payment Entry", pe_n, "docstatus")
                        if ds == 1:
                            payment_received_count = payment_received_count + 1
                            payment_received_amt   = payment_received_amt + amt
                except Exception:
                    for pay in payments:
                        a    = pay.get("payment_amount") or 0
                        o    = pay.get("outstanding") or 0
                        paid = a - o
                        if paid > 0:
                            payment_received_count = payment_received_count + 1
                            payment_received_amt   = payment_received_amt + paid

                pe_refs = frappe.db.get_all("Payment Entry Reference",
                    filters={"reference_doctype": "Sales Order", "reference_name": so.get("name")},
                    fields=["parent", "allocated_amount"])
                pe_totals = {}
                for ref in pe_refs:
                    pe_name = ref.get("parent")
                    amt     = float(ref.get("allocated_amount") or 0)
                    if pe_name:
                        pe_totals[pe_name] = pe_totals.get(pe_name, 0) + amt
                for pe_name, total_allocated in pe_totals.items():
                    pe = frappe.db.get_value("Payment Entry", pe_name,
                        ["name", "posting_date", "paid_amount", "mode_of_payment",
                         "payment_type", "docstatus"], as_dict=True)
                    if pe and pe.get("docstatus") == 1:
                        payment_entries.append({
                            "name":   pe.get("name"),
                            "date":   fmt(pe.get("posting_date")),
                            "amount": total_allocated or pe.get("paid_amount") or 0,
                            "mode":   pe.get("mode_of_payment") or "N/A",
                            "type":   pe.get("payment_type") or "Receive"
                        })
                payment_entries.sort(key=lambda x: x.get("date") or "")

            # CRM Follow-ups
            followups = []
            if lead.get("name"):
                # CRM Notes on Lead
                notes = frappe.db.get_all("CRM Note",
                    filters={"parent": lead.get("name"), "parenttype": "Lead"},
                    fields=["name", "note", "added_on", "added_by"],
                    order_by="added_on desc", limit=5)
                for n in notes:
                    n["fu_type"] = "Lead Note"
                    n["stage"]   = "Lead"
                    n["added_by_name"] = get_user_name(n.get("added_by"))
                    raw_note = n.get("note")
                    n["note"] = frappe.utils.strip_html(str(raw_note)) if raw_note else ""
                    followups.append(n)

                # Remark-Delay Log on Lead (shown in Follow Up tab)
                lead_rdl = frappe.db.sql("""
                    SELECT name, creation, owner, remark, status
                    FROM `tabRemark-Delay Log`
                    WHERE parent = %s AND parenttype = 'Lead'
                    ORDER BY creation DESC LIMIT 10
                """, (lead.get("name"),), as_dict=1)
                for d in lead_rdl:
                    raw_rem = d.get("remark")
                    followups.append({
                        "name":          d.get("name"),
                        "note":          frappe.utils.strip_html(str(raw_rem)) if raw_rem else "Lead remark",
                        "added_on":      d.get("creation"),
                        "added_by":      d.get("owner"),
                        "added_by_name": get_user_name(d.get("owner")),
                        "fu_type":       "Remark",
                        "stage":         "Lead"
                    })

            for stage_name, doc_name, doc_type in [
                ("Site Survey",  survey.get("name"),    "Site Survey"),
                ("Proposal",     quotation.get("name"), "Quotation"),
                ("Sales Order",  so.get("name"),        "Sales Order"),
                ("Project",      project_id,             "Project"),
            ]:
                if doc_name:
                    rdl = frappe.db.sql("""
                        SELECT name, creation, owner, remark
                        FROM `tabRemark-Delay Log`
                        WHERE parent = %s AND parenttype = %s
                        ORDER BY creation DESC LIMIT 3
                    """, (doc_name, doc_type), as_dict=1)
                    for d in rdl:
                        raw_rem = d.get("remark")
                        followups.append({
                            "name":          d.get("name"),
                            "note":          frappe.utils.strip_html(str(raw_rem)) if raw_rem else stage_name + " remark",
                            "added_on":      d.get("creation"),
                            "added_by":      d.get("owner"),
                            "added_by_name": get_user_name(d.get("owner")),
                            "fu_type":       "Delay Alert" if stage_name in ["Sales Order", "Project"] else "Remark",
                            "stage":         stage_name
                        })

            # Team
            team = []
            try:
                p_doc2      = frappe.get_doc("Project", project_id)
                child_table = p_doc2.get("custom_team_members") or []
                for t_row in child_table:
                    team.append({
                        "user":      t_row.get("member") or "",
                        "full_name": t_row.get("member_name") or "Unknown",
                        "role":      t_row.get("category") or "Staff"
                    })
            except Exception:
                pass

            # Photos
            photos_survey = []
            if survey.get("name"):
                photos_survey = frappe.db.get_all("File",
                    filters={"attached_to_doctype": "Site Survey",
                             "attached_to_name": survey.get("name")},
                    fields=["name", "file_name", "file_url", "creation"],
                    order_by="creation desc")

            photos_delivery = []
            if dn_doc.get("name"):
                photos_delivery = frappe.db.get_all("File",
                    filters={"attached_to_doctype": "Delivery Note",
                             "attached_to_name": dn_doc.get("name")},
                    fields=["name", "file_name", "file_url", "creation"],
                    order_by="creation desc")

            photos_completed = frappe.db.get_all("File",
                filters={"attached_to_doctype": "Project", "attached_to_name": project_id},
                fields=["name", "file_name", "file_url", "creation"],
                order_by="creation desc", limit=20)

            # Key Dates
            key_dates = {
                "Lead Generated":    fmt(str(lead.get("creation_date", ""))[:10]) if lead.get("creation_date") else "Pending",
                "Survey Completed":  fmt(survey.get("completed_date")) if survey.get("name") else "N/A (Skipped)",
                "Proposal Sent":     fmt(quotation.get("transaction_date")) if quotation.get("name") else "Pending",
                "Sales Order":       fmt(so.get("transaction_date")),
                "Dispatch Done":     fmt(dn_doc.get("posting_date")) if dn_doc.get("name") else "Pending",
                "Install Started":   fmt(proj.get("actual_start_date") or proj.get("expected_start_date")),
                "Install Completed": fmt(proj.get("actual_end_date")) if proj_is_completed else "In Progress",
                "Sync Process":      fmt(sync_doc.get("posting_date")) if sync_doc.get("name") else "Pending",
                "Finance Clearance": "Pending",
                "O&M Started":       "Pending"
            }

            # Pipeline Stages
            stages = [
                {"label": "Lead",            "done": bool(lead.get("name")),
                 "current": not bool(lead.get("name")),                                                        "sub": "Generated"},
                {"label": "Survey",          "done": bool(survey.get("name")),
                 "current": bool(lead.get("name")) and not bool(survey.get("name")) and not bool(quotation.get("name")),
                 "sub": "Site Visit"},
                {"label": "Proposal",        "done": bool(quotation.get("name")),
                 "current": bool(lead.get("name")) and not bool(quotation.get("name")),                        "sub": "Sent"},
                {"label": "Sales Order",     "done": bool(so.get("name")),
                 "current": bool(quotation.get("name")) and not bool(so.get("name")),                          "sub": "Order"},
                {"label": "Dispatch",        "done": bool(dn_doc.get("name")),
                 "current": bool(so.get("name")) and not bool(dn_doc.get("name")),                             "sub": "Material"},
                {"label": "Installation",    "done": proj_is_completed,
                 "current": bool(dn_doc.get("name")) and not proj_is_completed,                                "sub": "On Site"},
                {"label": "Synchronization", "done": sync_is_done,
                 "current": proj_is_completed and not sync_is_done,                                            "sub": "DISCOM"},
                {"label": "Finance",         "done": False, "current": False,                                  "sub": "Billing"},
                {"label": "O&M",             "done": False, "current": False,                                  "sub": "Service"}
            ]

            current_stage = "Lead"
            for sg in stages:
                if sg["done"]:
                    current_stage = sg["label"]

            # ── STATUS BADGE — detail view ─────────────────────
            # sync doc EXISTS  → use sync_doc.stage_status
            # sync doc MISSING → "Open"
            if sync_doc.get("name"):
                detail_status = resolve_status(
                    sync_doc.get("stage_status"),
                    sync_doc.get("complete_status"),
                    proj.get("status"), proj.get("expected_end_date"), today_date
                )
            else:
                detail_status = "Open"

            project_detail = {
                "name":              proj.get("name"),
                "customer":          so.get("customer_name") or proj.get("customer") or "N/A",
                "created_by":        created_by_name,
                "address":           lead_address,
                "status":            detail_status,
                "expected_end_date": fmt(proj.get("expected_end_date")),
                "percent_complete":  proj.get("percent_complete") or 0,
                "project_type":      proj.get("project_type") or "N/A",
                "solar_capacity":    cap_str2,
                "plant_category":    str(so.get("plant_category") or "N/A"),
                "contact_mobile":    str(so.get("contact_mobile") or lead.get("mobile_no") or "N/A"),
                "grand_total":       so.get("grand_total") or 0,
                "finance_type":      str(so.get("without_pay_reason") or "N/A"),
                "project_manager":   proj_manager_name,
                "manager":           proj_manager_name,
                "lead_id":           lead.get("name", ""),
                "so_id":             so.get("name", ""),
                "survey_id":         survey.get("name", ""),
                "quotation_id":      quotation.get("name", ""),
                "installation_id":   project_id,
                "sync_id":           sync_doc.get("name", ""),
                "dispatch_id":       dn_doc.get("name", "")
            }

            delay_data = {
                "purchase_delay": purchase_delay_days,
                "install_delay":  install_delay_days,
                "install_date":   fmt(proj.get("actual_start_date") or proj.get("expected_start_date")),
                "sync_delay":     sync_delay_days,
                "sync_status":    str(sync_doc.get("liaisoning_status") or "N/A") if sync_doc.get("name") else "N/A",
                "total_delay":    total_delay_days
            }

            summary_data = {
                "expected_days":    expected_days_val,
                "payment_received": payment_received_count,
                "payment_recv_amt": round(payment_received_amt, 2),
                "purchase_delay":   purchase_delay_days,
                "site_delay":       install_delay_days,
                "bill_amt":         project_bill_amt,
                "rounded_total":    so.get("rounded_total") or so.get("grand_total") or 0
            }

            frappe.response["message"] = {
                "project":          project_detail,
                "stages":           stages,
                "key_dates":        key_dates,
                "followups":        followups,
                "payments":         payments,
                "payment_entries":  payment_entries,
                "team":             team,
                "photos_survey":    photos_survey,
                "photos_delivery":  photos_delivery,
                "photos_completed": photos_completed,
                "current_stage":    current_stage,
                "delay_data":       delay_data,
                "summary_data":     summary_data
            }

    elif action == "get_stage_followups":
        stage     = frappe.form_dict.get("stage", "Lead")
        parent_id = frappe.form_dict.get("parent_id", "").strip()
        data      = []

        if stage == "Lead":
            filters = {"parenttype": "Lead"}
            if parent_id:
                filters["parent"] = parent_id
            data = frappe.db.get_all("CRM Note",
                filters=filters,
                fields=["parent", "added_on", "note", "added_by"],
                order_by="added_on desc", limit=25)
            for d in data:
                d["parent_name"] = frappe.db.get_value("Lead", d.get("parent"), "lead_name") or d.get("parent")
                raw_note = d.get("note")
                d["note"] = frappe.utils.strip_html(str(raw_note)) if raw_note else ""
        else:
            parent_doctype = stage
            if parent_id:
                data = frappe.db.sql("""
                    SELECT parent, creation as added_on, owner as added_by, remark
                    FROM `tabRemark-Delay Log`
                    WHERE parenttype = %s AND parent = %s
                    ORDER BY creation DESC LIMIT 25
                """, (parent_doctype, parent_id), as_dict=1)
            else:
                data = frappe.db.sql("""
                    SELECT parent, creation as added_on, owner as added_by, remark
                    FROM `tabRemark-Delay Log`
                    WHERE parenttype = %s
                    ORDER BY creation DESC LIMIT 25
                """, (parent_doctype,), as_dict=1)

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
                raw_rem = d.get("remark")
                d["note"] = frappe.utils.strip_html(str(raw_rem)) if raw_rem else "Remark / Delay recorded"

        for d in data:
            d["added_by_name"] = get_user_name(d.get("added_by"))

        frappe.response["message"] = data

    elif action == "get_all_photos":
        survey_id_param = frappe.form_dict.get("survey_id", "")
        all_ph = []

        if survey_id_param:
            sv_ph = frappe.db.get_all("File",
                filters={"attached_to_doctype": "Site Survey", "attached_to_name": survey_id_param},
                fields=["name", "file_name", "file_url", "creation"],
                order_by="creation desc")
            all_ph = sv_ph

        if project_id:
            pr_ph = frappe.db.get_all("File",
                filters={"attached_to_doctype": "Project", "attached_to_name": project_id},
                fields=["name", "file_name", "file_url", "creation"],
                order_by="creation desc")
            existing = [p.get("name") for p in all_ph]
            for ph in pr_ph:
                if ph.get("name") not in existing:
                    all_ph.append(ph)

        frappe.response["message"] = all_ph

    elif action == "search":
        query = frappe.form_dict.get("query", "").strip()

        if not query or len(query) < 2:
            frappe.response["message"] = []
        else:
            q = "%" + query + "%"

            stage_rank = {
                "Project": 5, "Sales Order": 4, "Proposal": 3,
                "Site Survey": 2, "Lead": 1
            }

            raw = []

            for r in frappe.db.sql("""
                SELECT name AS doc_id, lead_name AS customer, creation AS date
                FROM `tabLead`
                WHERE name LIKE %s OR lead_name LIKE %s OR company_name LIKE %s
                LIMIT 30
            """, (q, q, q), as_dict=1):
                raw.append({"dtype": "Lead", "doc_id": r.doc_id,
                    "customer": r.customer, "date": str(r.date or "")[:10],
                    "lead_id": r.doc_id, "project_id": "", "so_id": "", "proposal_id": ""})

            for r in frappe.db.sql("""
                SELECT name AS doc_id, customer_name AS customer,
                       transaction_date AS date, party_name AS lead_id
                FROM `tabQuotation`
                WHERE quotation_to = 'Lead' AND docstatus != 2
                  AND (name LIKE %s OR customer_name LIKE %s OR party_name LIKE %s)
                LIMIT 30
            """, (q, q, q), as_dict=1):
                raw.append({"dtype": "Proposal", "doc_id": r.doc_id,
                    "customer": r.customer, "date": str(r.date or "")[:10],
                    "lead_id": r.lead_id or "", "project_id": "", "so_id": r.doc_id, "proposal_id": r.doc_id})

            for r in frappe.db.sql("""
                SELECT name AS doc_id, customer_name AS customer,
                       transaction_date AS date, project AS project_id,
                       proposal AS proposal_id, lead AS so_lead
                FROM `tabSales Order`
                WHERE docstatus != 2
                  AND (name LIKE %s OR customer_name LIKE %s OR customer LIKE %s)
                LIMIT 30
            """, (q, q, q), as_dict=1):
                raw.append({"dtype": "Sales Order", "doc_id": r.doc_id,
                    "customer": r.customer, "date": str(r.date or "")[:10],
                    "lead_id": r.so_lead or "", "project_id": r.project_id or "",
                    "so_id": r.doc_id, "proposal_id": r.proposal_id or ""})

            for r in frappe.db.sql("""
                SELECT name AS doc_id, customer AS customer, creation AS date
                FROM `tabProject`
                WHERE name LIKE %s OR customer LIKE %s
                LIMIT 30
            """, (q, q), as_dict=1):
                raw.append({"dtype": "Project", "doc_id": r.doc_id,
                    "customer": r.customer, "date": str(r.date or "")[:10],
                    "lead_id": "", "project_id": r.doc_id, "so_id": "", "proposal_id": ""})

            for r in frappe.db.sql("""
                SELECT name AS doc_id, lead_name AS customer,
                       survey_date AS date, lead AS lead_id
                FROM `tabSite Survey`
                WHERE name LIKE %s OR lead_name LIKE %s OR lead LIKE %s
                LIMIT 20
            """, (q, q, q), as_dict=1):
                raw.append({"dtype": "Site Survey", "doc_id": r.doc_id,
                    "customer": r.customer, "date": str(r.date or "")[:10],
                    "lead_id": r.lead_id or "", "project_id": "", "so_id": "", "proposal_id": ""})

            proposal_ids = list(set([
                m["proposal_id"] for m in raw
                if m["proposal_id"] and not m["lead_id"]
            ]))
            proposal_to_lead = {}
            if proposal_ids:
                placeholders = ",".join(["%s"] * len(proposal_ids))
                qt_rows = frappe.db.sql(
                    "SELECT name, party_name FROM `tabQuotation` "
                    "WHERE quotation_to='Lead' AND docstatus!=2 "
                    "AND name IN (" + placeholders + ")",
                    tuple(proposal_ids), as_dict=1)
                for qt in qt_rows:
                    if qt.party_name:
                        proposal_to_lead[qt.name] = qt.party_name

            project_ids_no_lead = list(set([
                m["project_id"] for m in raw
                if m["project_id"] and not m["lead_id"] and not m["proposal_id"]
            ]))
            project_to_lead = {}
            if project_ids_no_lead:
                placeholders = ",".join(["%s"] * len(project_ids_no_lead))
                so_rows = frappe.db.sql(
                    "SELECT project, proposal, lead FROM `tabSales Order` "
                    "WHERE docstatus!=2 AND project IN (" + placeholders + ")",
                    tuple(project_ids_no_lead), as_dict=1)
                proj_proposal_ids = [s.proposal for s in so_rows if s.proposal]
                proj_proposal_to_lead = {}
                if proj_proposal_ids:
                    placeholders2 = ",".join(["%s"] * len(proj_proposal_ids))
                    qt_rows2 = frappe.db.sql(
                        "SELECT name, party_name FROM `tabQuotation` "
                        "WHERE quotation_to='Lead' AND docstatus!=2 "
                        "AND name IN (" + placeholders2 + ")",
                        tuple(proj_proposal_ids), as_dict=1)
                    for qt in qt_rows2:
                        if qt.party_name:
                            proj_proposal_to_lead[qt.name] = qt.party_name
                for so in so_rows:
                    lead_id = ""
                    if so.proposal and so.proposal in proj_proposal_to_lead:
                        lead_id = proj_proposal_to_lead[so.proposal]
                    elif so.lead:
                        lead_id = so.lead
                    if lead_id and so.project:
                        project_to_lead[so.project] = lead_id

            so_missing = [m for m in raw
                if m["dtype"] == "Sales Order" and not m["lead_id"] and not m["proposal_id"]]
            customer_to_lead = {}
            cust_names = list(set([m["customer"] for m in so_missing if m["customer"]]))
            if cust_names:
                ph3 = ",".join(["%s"] * len(cust_names))
                qt_c = frappe.db.sql(
                    "SELECT customer_name, party_name FROM `tabQuotation` "
                    "WHERE quotation_to='Lead' AND docstatus!=2 "
                    "AND customer_name IN (" + ph3 + ") ORDER BY creation DESC",
                    tuple(cust_names), as_dict=1)
                for qt in qt_c:
                    if qt.party_name and qt.customer_name not in customer_to_lead:
                        customer_to_lead[qt.customer_name] = qt.party_name

            for m in raw:
                if not m["lead_id"]:
                    if m["proposal_id"] and m["proposal_id"] in proposal_to_lead:
                        m["lead_id"] = proposal_to_lead[m["proposal_id"]]
                    elif m["project_id"] and m["project_id"] in project_to_lead:
                        m["lead_id"] = project_to_lead[m["project_id"]]
                    elif m["customer"] and m["customer"] in customer_to_lead:
                        m["lead_id"] = customer_to_lead[m["customer"]]

            result_map = {}
            for m in raw:
                rank    = stage_rank.get(m["dtype"], 1)
                lead_id = m["lead_id"].strip() if m["lead_id"] else ""
                key     = lead_id if lead_id else m["doc_id"]

                existing = result_map.get(key)
                if not existing:
                    result_map[key] = {
                        "lead_id":    lead_id or m["doc_id"],
                        "customer":   m["customer"] or "",
                        "stage_rank": rank,
                        "stage":      m["dtype"],
                        "project_id": m["project_id"] or "",
                        "date":       m["date"]
                    }
                else:
                    if rank > existing["stage_rank"]:
                        existing["stage_rank"] = rank
                        existing["stage"]      = m["dtype"]
                        existing["date"]       = m["date"]
                    if m["project_id"] and not existing["project_id"]:
                        existing["project_id"] = m["project_id"]
                    if lead_id and existing["lead_id"] != lead_id:
                        existing["lead_id"] = lead_id

            final_map = {}
            for key, val in result_map.items():
                canonical = val["lead_id"] if val["lead_id"] else key
                existing  = final_map.get(canonical)
                if not existing:
                    final_map[canonical] = dict(val)
                else:
                    if val["stage_rank"] > existing["stage_rank"]:
                        existing["stage_rank"] = val["stage_rank"]
                        existing["stage"]      = val["stage"]
                        existing["date"]       = val["date"]
                    if val["project_id"] and not existing["project_id"]:
                        existing["project_id"] = val["project_id"]

            final = sorted(final_map.values(),
                key=lambda x: (x["stage_rank"], x["date"]), reverse=True)

            frappe.response["message"] = final[:40]

    elif action == "get_lead_detail":
        lead_id = frappe.form_dict.get("lead_id", "").strip()

        if not lead_id:
            frappe.response["message"] = {"error": "No lead ID provided"}
        elif not frappe.db.exists("Lead", lead_id):
            frappe.response["message"] = {"error": "Lead not found: " + lead_id}
        else:
            lead_fields = [
                "name", "lead_name", "mobile_no", "city", "state", "creation_date",
                "company_name", "email_id", "custom_address", "custom_pincode",
                "solar_capacity", "owner", "creation"
            ]
            lead = frappe.db.get_value("Lead", lead_id, lead_fields, as_dict=True)

            today_date = frappe.utils.getdate(frappe.utils.today())

            survey = frappe.db.get_value("Site Survey",
                {"lead": lead_id},
                ["name", "survey_date", "completed_date", "solar_capacity",
                 "location_details", "lead_name", "contact_number"],
                as_dict=True) or {}

            quotation = frappe.db.get_value("Quotation",
                {"party_name": lead_id, "quotation_to": "Lead", "docstatus": ["!=", 2]},
                ["name", "transaction_date", "grand_total", "status",
                 "solar_capacity", "customer_name"],
                as_dict=True) or {}

            so = {}
            so_fields = [
                "name", "customer", "customer_name", "grand_total", "rounded_total",
                "per_billed", "per_advance", "transaction_date", "docstatus",
                "proposal", "site_survey", "liaisoning_and_sync", "project",
                "solar_capacity", "plant_category", "without_pay_reason", "lead"
            ]
            so_optional = ["contact_mobile", "tat_days", "manager", "project_manager"]
            so_all = so_fields[:]
            for f in so_optional:
                try:
                    exists = frappe.db.sql(
                        "SELECT COUNT(*) FROM information_schema.COLUMNS "
                        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tabSales Order' "
                        "AND COLUMN_NAME=%s", (f,))[0][0]
                    if exists:
                        so_all.append(f)
                except Exception:
                    pass

            if quotation.get("name"):
                so = frappe.db.get_value("Sales Order",
                    {"proposal": quotation.get("name"), "docstatus": ["!=", 2]},
                    so_all, as_dict=True) or {}
            if not so.get("name"):
                so = frappe.db.get_value("Sales Order",
                    {"lead": lead_id, "docstatus": ["!=", 2]},
                    so_all, as_dict=True) or {}
            if not so.get("name") and quotation.get("customer_name"):
                so = frappe.db.get_value("Sales Order",
                    {"customer_name": quotation.get("customer_name"), "docstatus": ["!=", 2]},
                    so_all, as_dict=True) or {}
            if not so.get("name") and lead.get("lead_name"):
                so = frappe.db.get_value("Sales Order",
                    {"customer_name": lead.get("lead_name"), "docstatus": ["!=", 2]},
                    so_all, as_dict=True) or {}
            if not so.get("name") and quotation.get("name"):
                so_raw = frappe.db.sql("""
                    SELECT name FROM `tabSales Order`
                    WHERE TRIM(proposal) = %s AND docstatus != 2
                    LIMIT 1
                """, (quotation.get("name"),), as_dict=1)
                if so_raw:
                    so = frappe.db.get_value("Sales Order",
                        so_raw[0].name, so_all, as_dict=True) or {}
            so = so or {}

            proj = {}
            proj_id = so.get("project") or ""
            if proj_id and frappe.db.exists("Project", proj_id):
                pfields = [
                    "name", "customer", "status", "expected_end_date",
                    "percent_complete", "project_type", "owner", "bill_amt",
                    "stage_status", "complete_status", "actual_start_date",
                    "actual_end_date", "expected_start_date"
                ]
                proj = frappe.db.get_value("Project", proj_id, pfields, as_dict=True) or {}

            dn_doc = {}
            if so.get("name"):
                dn_items = frappe.db.get_all("Delivery Note Item",
                    filters={"against_sales_order": so.get("name")},
                    fields=["parent"], limit=1)
                if dn_items:
                    dn_name = dn_items[0].get("parent", "")
                    try:
                        dn_doc = frappe.db.get_value("Delivery Note", dn_name,
                            ["name", "posting_date", "docstatus", "sla_due_date",
                             "complete_date", "tat_days", "stage_status", "complete_status"],
                            as_dict=True) or {}
                    except Exception:
                        dn_doc = frappe.db.get_value("Delivery Note", dn_name,
                            ["name", "posting_date", "docstatus"], as_dict=True) or {}
                    if dn_doc and (dn_doc.get("docstatus") or 0) == 2:
                        dn_doc = {}

            sync_doc = get_sync(so, lead, project_id=proj_id, customer=lead.get("lead_name"))

            proj_is_completed = (proj.get("status") or "").strip().title() == "Completed" if proj else False
            sync_is_done = (
                bool(sync_doc.get("name")) and
                str(sync_doc.get("stage_status") or "").strip().title() == "Completed"
            )

            addr_parts = []
            for f in ["custom_address", "city", "state", "custom_pincode"]:
                v = lead.get(f, "")
                if v:
                    addr_parts.append(str(v))
            lead_address = ", ".join(addr_parts)
            if not lead_address and survey.get("location_details"):
                lead_address = str(survey.get("location_details"))
            lead_address = lead_address or "N/A"

            cap_str = ""
            for val in [so.get("solar_capacity"), lead.get("solar_capacity"),
                        survey.get("solar_capacity"), quotation.get("solar_capacity"),
                        proj.get("solar_capacity") if proj else None]:
                c = str(val or "").strip()
                if c and c not in ["", "None", "null", "-", "N/A"]:
                    cap_str = c
                    break

            purchase_delay_days = 0
            if dn_doc.get("complete_status") == "Delayed":
                purchase_delay_days = safe_int(dn_doc.get("tat_days"))
            elif dn_doc.get("sla_due_date") and not dn_doc.get("complete_date"):
                due = frappe.utils.getdate(str(dn_doc.get("sla_due_date"))[:10])
                if due < today_date:
                    purchase_delay_days = frappe.utils.date_diff(today_date, due)

            install_delay_days = 0
            if proj:
                if proj.get("stage_status") == "Overdue":
                    install_delay_days = safe_int(proj.get("tat_days", 0))
                elif proj.get("expected_end_date") and not proj_is_completed:
                    exp_end = frappe.utils.getdate(proj.get("expected_end_date"))
                    if exp_end < today_date:
                        install_delay_days = frappe.utils.date_diff(today_date, exp_end)

            sync_delay_days  = safe_int(sync_doc.get("tat_days")) if sync_doc.get("name") else 0
            total_delay_days = purchase_delay_days + install_delay_days + sync_delay_days

            payments = []
            payment_entries = []
            payment_received_count = 0
            payment_received_amt   = 0

            if so.get("name"):
                payments = frappe.db.get_all("Payment Schedule",
                    filters={"parent": so.get("name"), "parenttype": "Sales Order"},
                    fields=["due_date", "payment_amount", "outstanding", "invoice_portion"],
                    order_by="idx asc")
                pe_refs = frappe.db.get_all("Payment Entry Reference",
                    filters={"reference_doctype": "Sales Order", "reference_name": so.get("name")},
                    fields=["parent", "allocated_amount"])
                pe_totals = {}
                for ref in pe_refs:
                    pe_name = ref.get("parent")
                    amt     = float(ref.get("allocated_amount") or 0)
                    if pe_name:
                        pe_totals[pe_name] = pe_totals.get(pe_name, 0) + amt
                for pe_name, total_allocated in pe_totals.items():
                    pe = frappe.db.get_value("Payment Entry", pe_name,
                        ["name", "posting_date", "paid_amount", "mode_of_payment",
                         "payment_type", "docstatus"], as_dict=True)
                    if pe and pe.get("docstatus") == 1:
                        payment_received_count = payment_received_count + 1
                        payment_received_amt   = payment_received_amt + total_allocated
                        payment_entries.append({
                            "name":   pe.get("name"),
                            "date":   fmt(pe.get("posting_date")),
                            "amount": total_allocated or pe.get("paid_amount") or 0,
                            "mode":   pe.get("mode_of_payment") or "N/A",
                            "type":   pe.get("payment_type") or "Receive"
                        })
                payment_entries.sort(key=lambda x: x.get("date") or "")

            followups = []
            # CRM Notes on Lead
            notes = frappe.db.get_all("CRM Note",
                filters={"parent": lead_id, "parenttype": "Lead"},
                fields=["name", "note", "added_on", "added_by"],
                order_by="added_on desc", limit=5)
            for n in notes:
                n["fu_type"] = "Lead Note"
                n["stage"]   = "Lead"
                n["added_by_name"] = get_user_name(n.get("added_by"))
                raw_note = n.get("note")
                n["note"] = frappe.utils.strip_html(str(raw_note)) if raw_note else ""
                followups.append(n)

            # Remark-Delay Log on Lead (shown in Follow Up tab)
            lead_rdl = frappe.db.sql("""
                SELECT name, creation, owner, remark, status
                FROM `tabRemark-Delay Log`
                WHERE parent = %s AND parenttype = 'Lead'
                ORDER BY creation DESC LIMIT 10
            """, (lead_id,), as_dict=1)
            for d in lead_rdl:
                raw_rem = d.get("remark")
                followups.append({
                    "name":          d.get("name"),
                    "note":          frappe.utils.strip_html(str(raw_rem)) if raw_rem else "Lead remark",
                    "added_on":      d.get("creation"),
                    "added_by":      d.get("owner"),
                    "added_by_name": get_user_name(d.get("owner")),
                    "fu_type":       "Remark",
                    "stage":         "Lead"
                })

            for stage_name, doc_name, doc_type in [
                ("Site Survey", survey.get("name"),    "Site Survey"),
                ("Proposal",    quotation.get("name"), "Quotation"),
                ("Sales Order", so.get("name"),        "Sales Order"),
                ("Project",     proj_id,               "Project"),
            ]:
                if doc_name:
                    rdl = frappe.db.sql("""
                        SELECT name, creation, owner, remark
                        FROM `tabRemark-Delay Log`
                        WHERE parent = %s AND parenttype = %s
                        ORDER BY creation DESC LIMIT 3
                    """, (doc_name, doc_type), as_dict=1)
                    for d in rdl:
                        raw_rem = d.get("remark")
                        followups.append({
                            "name":          d.get("name"),
                            "note":          frappe.utils.strip_html(str(raw_rem)) if raw_rem else stage_name + " remark",
                            "added_on":      d.get("creation"),
                            "added_by":      d.get("owner"),
                            "added_by_name": get_user_name(d.get("owner")),
                            "fu_type":       "Delay Alert" if stage_name in ["Sales Order", "Project"] else "Remark",
                            "stage":         stage_name
                        })

            photos_survey = []
            if survey.get("name"):
                photos_survey = frappe.db.get_all("File",
                    filters={"attached_to_doctype": "Site Survey",
                             "attached_to_name": survey.get("name")},
                    fields=["name", "file_name", "file_url", "creation"],
                    order_by="creation desc")

            photos_delivery = []
            if dn_doc.get("name"):
                photos_delivery = frappe.db.get_all("File",
                    filters={"attached_to_doctype": "Delivery Note",
                             "attached_to_name": dn_doc.get("name")},
                    fields=["name", "file_name", "file_url", "creation"],
                    order_by="creation desc")

            photos_completed = []
            if proj_id:
                photos_completed = frappe.db.get_all("File",
                    filters={"attached_to_doctype": "Project", "attached_to_name": proj_id},
                    fields=["name", "file_name", "file_url", "creation"],
                    order_by="creation desc", limit=20)

            key_dates = {
                "Lead Generated":    fmt(str(lead.get("creation_date") or lead.get("creation") or "")[:10]),
                "Survey Completed":  fmt(survey.get("completed_date")) if survey.get("name") else "N/A (Skipped)",
                "Proposal Sent":     fmt(quotation.get("transaction_date")) if quotation.get("name") else "Pending",
                "Sales Order":       fmt(so.get("transaction_date")) if so.get("name") else "Pending",
                "Dispatch Done":     fmt(dn_doc.get("posting_date")) if dn_doc.get("name") else "Pending",
                "Install Started":   fmt(proj.get("actual_start_date") or proj.get("expected_start_date")) if proj else "Pending",
                "Install Completed": fmt(proj.get("actual_end_date")) if proj_is_completed else "In Progress" if proj else "Pending",
                "Sync Process":      fmt(sync_doc.get("posting_date")) if sync_doc.get("name") else "Pending",
                "Finance Clearance": "Pending",
                "O&M Started":       "Pending"
            }

            stages = [
                {"label": "Lead",            "done": True,
                 "current": False,                                                                      "sub": "Generated"},
                {"label": "Survey",          "done": bool(survey.get("name")),
                 "current": not bool(survey.get("name")) and not bool(quotation.get("name")),           "sub": "Site Visit"},
                {"label": "Proposal",        "done": bool(quotation.get("name")),
                 "current": bool(survey.get("name") or True) and not bool(quotation.get("name")),       "sub": "Sent"},
                {"label": "Sales Order",     "done": bool(so.get("name")),
                 "current": bool(quotation.get("name")) and not bool(so.get("name")),                   "sub": "Order"},
                {"label": "Dispatch",        "done": bool(dn_doc.get("name")),
                 "current": bool(so.get("name")) and not bool(dn_doc.get("name")),                      "sub": "Material"},
                {"label": "Installation",    "done": proj_is_completed,
                 "current": bool(dn_doc.get("name")) and not proj_is_completed,                         "sub": "On Site"},
                {"label": "Synchronization", "done": sync_is_done,
                 "current": proj_is_completed and not sync_is_done,                                     "sub": "DISCOM"},
                {"label": "Finance",         "done": False, "current": False,                           "sub": "Billing"},
                {"label": "O&M",             "done": False, "current": False,                           "sub": "Service"}
            ]

            current_stage = "Lead"
            for sg in stages:
                if sg["done"]:
                    current_stage = sg["label"]

            proj_manager_name  = "N/A"
            proj_manager_email = ""
            if proj_id:
                try:
                    p_doc3 = frappe.get_doc("Project", proj_id)
                    proj_manager_email = p_doc3.get("custom_project_manager") or ""
                except Exception:
                    pass
            if proj_manager_email:
                proj_manager_name = get_user_name(proj_manager_email)

            team = []
            if proj_id:
                try:
                    p_doc4      = frappe.get_doc("Project", proj_id)
                    child_table = p_doc4.get("custom_team_members") or []
                    for t_row in child_table:
                        team.append({
                            "user":      t_row.get("member") or "",
                            "full_name": t_row.get("member_name") or "Unknown",
                            "role":      t_row.get("category") or "Staff"
                        })
                except Exception:
                    pass

            # ── STATUS BADGE — lead detail view ───────────────
            # sync doc EXISTS  → use sync_doc.stage_status
            # sync doc MISSING → "Open"
            if sync_doc.get("name"):
                detail_status = resolve_status(
                    sync_doc.get("stage_status"),
                    sync_doc.get("complete_status"),
                    proj.get("status") if proj else None,
                    proj.get("expected_end_date") if proj else None,
                    today_date
                )
            else:
                detail_status = "Open"

            proj_display_id = proj_id if proj_id else lead_id

            project_detail = {
                "name":              proj_display_id,
                "customer":          so.get("customer_name") or lead.get("lead_name") or "N/A",
                "created_by":        get_user_name(lead.get("owner") or ""),
                "address":           lead_address,
                "status":            detail_status,
                "expected_end_date": fmt(proj.get("expected_end_date")) if proj else "N/A",
                "percent_complete":  proj.get("percent_complete") or 0 if proj else 0,
                "project_type":      proj.get("project_type") or "N/A" if proj else "N/A",
                "solar_capacity":    cap_str,
                "plant_category":    str(so.get("plant_category") or "N/A"),
                "contact_mobile":    str(so.get("contact_mobile") if so.get("contact_mobile") else lead.get("mobile_no") or "N/A"),
                "grand_total":       so.get("grand_total") or 0,
                "finance_type":      str(so.get("without_pay_reason") or "N/A"),
                "project_manager":   proj_manager_name,
                "manager":           proj_manager_name,
                "lead_id":           lead_id,
                "so_id":             so.get("name", ""),
                "survey_id":         survey.get("name", ""),
                "quotation_id":      quotation.get("name", ""),
                "installation_id":   proj_id,
                "sync_id":           sync_doc.get("name", ""),
                "dispatch_id":       dn_doc.get("name", "")
            }

            delay_data = {
                "purchase_delay": purchase_delay_days,
                "install_delay":  install_delay_days,
                "install_date":   fmt(proj.get("actual_start_date") or proj.get("expected_start_date")) if proj else "Pending",
                "sync_delay":     sync_delay_days,
                "sync_status":    str(sync_doc.get("liaisoning_status") or "N/A") if sync_doc.get("name") else "N/A",
                "total_delay":    total_delay_days
            }

            summary_data = {
                "expected_days":    str(safe_int(so.get("tat_days"))) + " Days" if so.get("tat_days") else "N/A",
                "payment_received": payment_received_count,
                "payment_recv_amt": round(payment_received_amt, 2),
                "purchase_delay":   purchase_delay_days,
                "site_delay":       install_delay_days,
                "bill_amt":         proj.get("bill_amt") or 0 if proj else 0,
                "rounded_total":    so.get("rounded_total") or so.get("grand_total") or 0
            }

            frappe.response["message"] = {
                "project":          project_detail,
                "stages":           stages,
                "key_dates":        key_dates,
                "followups":        followups,
                "payments":         payments,
                "payment_entries":  payment_entries,
                "team":             team,
                "photos_survey":    photos_survey,
                "photos_delivery":  photos_delivery,
                "photos_completed": photos_completed,
                "current_stage":    current_stage,
                "delay_data":       delay_data,
                "summary_data":     summary_data,
                "source":           "lead"
            }

    else:
        frappe.response["message"] = {"error": "Unknown action: " + str(action)}

except Exception as e:
    frappe.log_error(str(e), "Dashboard Error")
    frappe.response["message"] = {"error": str(e)}
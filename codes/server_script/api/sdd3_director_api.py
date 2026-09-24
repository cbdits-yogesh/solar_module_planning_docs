# ================================================================
# SERVER SCRIPT: sdd3_director_api
# Method Name: sdd3_director_api
# Type: API
# Allow Guest: NO
# ================================================================
# DocTypes Used:
#   - CRM Lead          (tabCRM Lead)
#   - Site Survey       (tabSite Survey)         -- adjust if custom
#   - Quotation         (tabQuotation)           -- Proposal
#   - Sales Order       (tabSales Order)
#   - Delivery Note     (tabDelivery Note)       -- Dispatch
#   - Project           (tabProject)             -- Installation
#   - Sale Stage SLA    (tabSale Stage SLA)      -- SLA config
#   - Employee          (tabEmployee)
# ================================================================
# FIELD ASSUMPTIONS (verify with INFORMATION_SCHEMA if errors):
#   CRM Lead: name, lead_name, status, lead_owner, creation, custom_stage
#   Site Survey: name, lead, status, surveyor, survey_date, custom_completion_date
#   Quotation: name, party_name, status, owner, transaction_date, valid_till
#   Sales Order: name, customer, status, owner, transaction_date, delivery_date
#   Delivery Note: name, customer, status, owner, posting_date, lr_date
#   Project: name, customer, status, percent_complete, expected_start_date, expected_end_date, project_manager
# ================================================================

block = frappe.form_dict.get("block", "init")
from_date = frappe.form_dict.get("from_date", "2026-04-01")
to_date = frappe.form_dict.get("to_date", str(frappe.utils.today()))
employee = frappe.form_dict.get("employee", "")
stage = frappe.form_dict.get("stage", "")
customer = frappe.form_dict.get("customer", "")

safe_from = frappe.db.escape(from_date)
safe_to = frappe.db.escape(to_date)
safe_emp = frappe.db.escape(employee)
safe_customer = frappe.db.escape(customer)

# ================================================================
# BLOCK: init — Load dropdowns (employees + period defaults)
# ================================================================
if block == "init":
    # Get employees who have any CRM role
    emp_list = frappe.db.sql("""
        SELECT DISTINCT
            e.name as emp_id,
            e.employee_name,
            e.designation
        FROM `tabEmployee` e
        WHERE e.status = 'Active'
          AND (e.disabled = 0 OR e.disabled IS NULL)
        ORDER BY e.employee_name
    """, as_dict=True)

    # Get SLA config
    sla_config = frappe.db.sql("""
        SELECT for_doctype, days
        FROM `tabSale Stage SLA Detail`
        ORDER BY idx
    """, as_dict=True)

    frappe.response["message"] = {
        "employees": emp_list,
        "sla_config": sla_config,
        "today": str(frappe.utils.today()),
        "default_from": "2026-04-01"
    }

# ================================================================
# BLOCK: overview — Top KPI cards
# ================================================================
elif block == "overview":
    date_cond_lead = " AND DATE(creation) BETWEEN " + safe_from + " AND " + safe_to
    date_cond_so = " AND DATE(transaction_date) BETWEEN " + safe_from + " AND " + safe_to

    emp_cond_lead = ""
    if employee:
        emp_cond_lead = " AND lead_owner = " + safe_emp

    # Leads count
    lead_data = frappe.db.sql("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status IN ('Open','Lead') THEN 1 ELSE 0 END) as new_leads,
               SUM(CASE WHEN status = 'Interested' THEN 1 ELSE 0 END) as qualified
        FROM `tabCRM Lead`
        WHERE docstatus IN (0,1)
        """ + date_cond_lead + emp_cond_lead, as_dict=True)

    # Quotations (Proposals)
    proposal_data = frappe.db.sql("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'Submitted' THEN 1 ELSE 0 END) as sent,
               SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as pending
        FROM `tabQuotation`
        WHERE docstatus IN (0,1)
          AND DATE(transaction_date) BETWEEN """ + safe_from + " AND " + safe_to + """
    """, as_dict=True)

    # Sales Orders
    so_data = frappe.db.sql("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status IN ('To Deliver and Bill','To Bill') THEN 1 ELSE 0 END) as active
        FROM `tabSales Order`
        WHERE docstatus = 1
          AND DATE(transaction_date) BETWEEN """ + safe_from + " AND " + safe_to + """
    """, as_dict=True)

    # Delivery Notes (Dispatch)
    dispatch_data = frappe.db.sql("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'To Bill' THEN 1 ELSE 0 END) as dispatched
        FROM `tabDelivery Note`
        WHERE docstatus = 1
          AND DATE(posting_date) BETWEEN """ + safe_from + " AND " + safe_to + """
    """, as_dict=True)

    # Projects (Installation)
    install_data = frappe.db.sql("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
               SUM(CASE WHEN expected_end_date < CURDATE() AND status != 'Completed' THEN 1 ELSE 0 END) as delayed
        FROM `tabProject`
        WHERE docstatus IN (0,1)
          AND DATE(expected_start_date) BETWEEN """ + safe_from + " AND " + safe_to + """
    """, as_dict=True)

    frappe.response["message"] = {
        "leads": lead_data[0] if lead_data else {},
        "proposals": proposal_data[0] if proposal_data else {},
        "sales_orders": so_data[0] if so_data else {},
        "dispatch": dispatch_data[0] if dispatch_data else {},
        "installation": install_data[0] if install_data else {}
    }

# ================================================================
# BLOCK: pipeline — Stage-wise funnel counts
# ================================================================
elif block == "pipeline":
    lead_count = frappe.db.sql("""
        SELECT COUNT(*) as cnt FROM `tabCRM Lead`
        WHERE docstatus IN (0,1)
          AND DATE(creation) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

    survey_count = frappe.db.sql("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN (expected_end_date IS NOT NULL AND expected_end_date != ''
                          AND expected_end_date < CURDATE()
                          AND status != 'Completed') THEN 1 ELSE 0 END) as delayed
        FROM `tabSite Survey`
        WHERE docstatus IN (0,1)
          AND DATE(creation) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

    proposal_count = frappe.db.sql("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'Submitted' THEN 1 ELSE 0 END) as sent
        FROM `tabQuotation`
        WHERE docstatus IN (0,1)
          AND DATE(transaction_date) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

    so_count = frappe.db.sql("""
        SELECT COUNT(*) as total
        FROM `tabSales Order`
        WHERE docstatus = 1
          AND DATE(transaction_date) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

    dispatch_count = frappe.db.sql("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'To Bill' THEN 1 ELSE 0 END) as completed
        FROM `tabDelivery Note`
        WHERE docstatus = 1
          AND DATE(posting_date) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

    install_count = frappe.db.sql("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
               SUM(CASE WHEN expected_end_date < CURDATE() AND status != 'Completed' THEN 1 ELSE 0 END) as delayed
        FROM `tabProject`
        WHERE docstatus IN (0,1)
          AND DATE(expected_start_date) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

    frappe.response["message"] = {
        "lead": lead_count[0] if lead_count else {"cnt": 0},
        "survey": survey_count[0] if survey_count else {},
        "proposal": proposal_count[0] if proposal_count else {},
        "sales_order": so_count[0] if so_count else {},
        "dispatch": dispatch_count[0] if dispatch_count else {},
        "installation": install_count[0] if install_count else {}
    }

# ================================================================
# BLOCK: stage_detail — Per-stage popup data
# ================================================================
elif block == "stage_detail":
    safe_stage = frappe.db.escape(stage)

    if stage == "Lead":
        rows = frappe.db.sql("""
            SELECT
                l.name,
                l.lead_name,
                l.status,
                l.lead_owner,
                l.mobile_no,
                l.email_id,
                l.city,
                l.industry,
                DATE(l.creation) as created_date,
                DATEDIFF(CURDATE(), DATE(l.creation)) as age_days
            FROM `tabCRM Lead` l
            WHERE l.docstatus IN (0,1)
              AND DATE(l.creation) BETWEEN """ + safe_from + " AND " + safe_to + """
            ORDER BY l.creation DESC
            LIMIT 100
        """, as_dict=True)

        kpis = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status IN ('Open','Lead') THEN 1 ELSE 0 END) as new_leads,
                SUM(CASE WHEN status = 'Interested' THEN 1 ELSE 0 END) as interested,
                SUM(CASE WHEN status = 'Replied' THEN 1 ELSE 0 END) as replied,
                AVG(DATEDIFF(CURDATE(), DATE(creation))) as avg_age
            FROM `tabCRM Lead`
            WHERE docstatus IN (0,1)
              AND DATE(creation) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

        frappe.response["message"] = {"rows": rows, "kpis": kpis[0] if kpis else {}}

    elif stage == "Site Survey":
        rows = frappe.db.sql("""
            SELECT
                s.name,
                s.lead as customer,
                s.status,
                s.surveyor,
                DATE(s.survey_date) as survey_date,
                DATE(s.expected_end_date) as expected_end,
                DATEDIFF(CURDATE(), DATE(s.expected_end_date)) as delay_days,
                CASE WHEN s.expected_end_date < CURDATE() AND s.status != 'Completed'
                     THEN 1 ELSE 0 END as is_delayed
            FROM `tabSite Survey` s
            WHERE s.docstatus IN (0,1)
              AND DATE(s.creation) BETWEEN """ + safe_from + " AND " + safe_to + """
            ORDER BY is_delayed DESC, s.creation DESC
            LIMIT 100
        """, as_dict=True)

        kpis = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status != 'Completed' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN expected_end_date < CURDATE() AND status != 'Completed'
                         THEN 1 ELSE 0 END) as delayed,
                AVG(DATEDIFF(completion_date, survey_date)) as avg_tat
            FROM `tabSite Survey`
            WHERE docstatus IN (0,1)
              AND DATE(creation) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

        frappe.response["message"] = {"rows": rows, "kpis": kpis[0] if kpis else {}}

    elif stage == "Proposal":
        rows = frappe.db.sql("""
            SELECT
                q.name,
                q.party_name as customer,
                q.status,
                q.owner,
                DATE(q.transaction_date) as sent_date,
                q.valid_till,
                q.grand_total,
                DATEDIFF(CURDATE(), DATE(q.transaction_date)) as age_days
            FROM `tabQuotation` q
            WHERE q.docstatus IN (0,1)
              AND DATE(q.transaction_date) BETWEEN """ + safe_from + " AND " + safe_to + """
            ORDER BY q.creation DESC
            LIMIT 100
        """, as_dict=True)

        kpis = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Submitted' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as pending,
                SUM(grand_total) as total_value,
                AVG(grand_total) as avg_value
            FROM `tabQuotation`
            WHERE docstatus IN (0,1)
              AND DATE(transaction_date) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

        frappe.response["message"] = {"rows": rows, "kpis": kpis[0] if kpis else {}}

    elif stage == "Sales Order":
        rows = frappe.db.sql("""
            SELECT
                so.name,
                so.customer,
                so.status,
                so.owner,
                DATE(so.transaction_date) as order_date,
                so.delivery_date,
                so.grand_total,
                so.advance_paid,
                ROUND((so.advance_paid / so.grand_total)*100, 1) as payment_pct
            FROM `tabSales Order` so
            WHERE so.docstatus = 1
              AND DATE(so.transaction_date) BETWEEN """ + safe_from + " AND " + safe_to + """
            ORDER BY so.creation DESC
            LIMIT 100
        """, as_dict=True)

        kpis = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(grand_total) as total_value,
                SUM(advance_paid) as collected,
                SUM(CASE WHEN status IN ('To Deliver and Bill') THEN 1 ELSE 0 END) as pending_delivery
            FROM `tabSales Order`
            WHERE docstatus = 1
              AND DATE(transaction_date) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

        frappe.response["message"] = {"rows": rows, "kpis": kpis[0] if kpis else {}}

    elif stage == "Delivery Note":
        rows = frappe.db.sql("""
            SELECT
                dn.name,
                dn.customer,
                dn.status,
                dn.owner,
                DATE(dn.posting_date) as dispatch_date,
                dn.lr_date,
                dn.lr_no,
                dn.transporter_name
            FROM `tabDelivery Note` dn
            WHERE dn.docstatus = 1
              AND DATE(dn.posting_date) BETWEEN """ + safe_from + " AND " + safe_to + """
            ORDER BY dn.posting_date DESC
            LIMIT 100
        """, as_dict=True)

        kpis = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'To Bill' THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN status = 'Draft' THEN 1 ELSE 0 END) as pending
            FROM `tabDelivery Note`
            WHERE docstatus = 1
              AND DATE(posting_date) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

        frappe.response["message"] = {"rows": rows, "kpis": kpis[0] if kpis else {}}

    elif stage == "Project":
        rows = frappe.db.sql("""
            SELECT
                p.name,
                p.project_name,
                p.customer,
                p.status,
                p.project_manager,
                p.percent_complete,
                DATE(p.expected_start_date) as start_date,
                DATE(p.expected_end_date) as end_date,
                DATEDIFF(CURDATE(), DATE(p.expected_end_date)) as delay_days,
                CASE WHEN p.expected_end_date < CURDATE() AND p.status != 'Completed'
                     THEN 1 ELSE 0 END as is_delayed
            FROM `tabProject` p
            WHERE p.docstatus IN (0,1)
              AND DATE(p.expected_start_date) BETWEEN """ + safe_from + " AND " + safe_to + """
            ORDER BY is_delayed DESC, p.expected_end_date ASC
            LIMIT 100
        """, as_dict=True)

        kpis = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN expected_end_date < CURDATE() AND status != 'Completed'
                         THEN 1 ELSE 0 END) as delayed,
                AVG(percent_complete) as avg_progress
            FROM `tabProject`
            WHERE docstatus IN (0,1)
              AND DATE(expected_start_date) BETWEEN """ + safe_from + " AND " + safe_to, as_dict=True)

        frappe.response["message"] = {"rows": rows, "kpis": kpis[0] if kpis else {}}

    elif stage == "Liaisoning And Synchronization":
        # Assuming a custom DocType or using Project with custom fields
        rows = frappe.db.sql("""
            SELECT
                p.name,
                p.project_name,
                p.customer,
                p.status,
                p.project_manager,
                p.percent_complete,
                DATE(p.expected_end_date) as sync_due,
                DATEDIFF(CURDATE(), DATE(p.expected_end_date)) as delay_days
            FROM `tabProject` p
            WHERE p.docstatus IN (0,1)
              AND p.project_type = 'Synchronization'
              AND DATE(p.expected_start_date) BETWEEN """ + safe_from + " AND " + safe_to + """
            ORDER BY p.expected_end_date ASC
            LIMIT 100
        """, as_dict=True)
        frappe.response["message"] = {"rows": rows, "kpis": {}}

    else:
        frappe.response["message"] = {"rows": [], "kpis": {}}

# ================================================================
# BLOCK: customer_journey — Search customer across all stages
# ================================================================
elif block == "customer_journey":
    safe_c = frappe.db.escape("%" + customer + "%")

    journey = {}

    # Stage 1: Lead
    lead = frappe.db.sql("""
        SELECT name, lead_name, status, DATE(creation) as date, lead_owner
        FROM `tabCRM Lead`
        WHERE (lead_name LIKE """ + safe_c + """ OR company_name LIKE """ + safe_c + """)
          AND docstatus IN (0,1)
        ORDER BY creation DESC LIMIT 1
    """, as_dict=True)
    journey["lead"] = lead[0] if lead else None

    # Stage 2: Site Survey
    survey = frappe.db.sql("""
        SELECT name, lead as customer, status, DATE(survey_date) as date, surveyor
        FROM `tabSite Survey`
        WHERE lead LIKE """ + safe_c + """
          AND docstatus IN (0,1)
        ORDER BY creation DESC LIMIT 1
    """, as_dict=True)
    journey["survey"] = survey[0] if survey else None

    # Stage 3: Proposal
    proposal = frappe.db.sql("""
        SELECT name, party_name as customer, status, DATE(transaction_date) as date,
               owner, grand_total
        FROM `tabQuotation`
        WHERE party_name LIKE """ + safe_c + """
          AND docstatus IN (0,1)
        ORDER BY creation DESC LIMIT 1
    """, as_dict=True)
    journey["proposal"] = proposal[0] if proposal else None

    # Stage 4: Sales Order
    so = frappe.db.sql("""
        SELECT name, customer, status, DATE(transaction_date) as date,
               grand_total, advance_paid
        FROM `tabSales Order`
        WHERE customer LIKE """ + safe_c + """
          AND docstatus = 1
        ORDER BY creation DESC LIMIT 1
    """, as_dict=True)
    journey["sales_order"] = so[0] if so else None

    # Stage 5: Delivery Note
    dn = frappe.db.sql("""
        SELECT name, customer, status, DATE(posting_date) as date, transporter_name
        FROM `tabDelivery Note`
        WHERE customer LIKE """ + safe_c + """
          AND docstatus = 1
        ORDER BY posting_date DESC LIMIT 1
    """, as_dict=True)
    journey["dispatch"] = dn[0] if dn else None

    # Stage 6: Project (Installation)
    proj = frappe.db.sql("""
        SELECT name, project_name, customer, status, percent_complete,
               DATE(expected_start_date) as date, project_manager
        FROM `tabProject`
        WHERE customer LIKE """ + safe_c + """
          AND docstatus IN (0,1)
        ORDER BY creation DESC LIMIT 1
    """, as_dict=True)
    journey["installation"] = proj[0] if proj else None

    # Stage 7: Liaisoning
    sync = frappe.db.sql("""
        SELECT name, project_name, customer, status, percent_complete,
               DATE(expected_end_date) as date
        FROM `tabProject`
        WHERE customer LIKE """ + safe_c + """
          AND project_type = 'Synchronization'
          AND docstatus IN (0,1)
        ORDER BY creation DESC LIMIT 1
    """, as_dict=True)
    journey["sync"] = sync[0] if sync else None

    frappe.response["message"] = {"journey": journey, "customer": customer}

# ================================================================
# BLOCK: employees_by_stage — Employee filter dropdown
# ================================================================
elif block == "employees_by_stage":
    safe_stage = frappe.db.escape(stage)
    emp_list = frappe.db.sql("""
        SELECT DISTINCT
            e.name as emp_id,
            e.employee_name,
            e.designation
        FROM `tabEmployee` e
        WHERE e.status = 'Active'
          AND (e.disabled = 0 OR e.disabled IS NULL)
        ORDER BY e.employee_name
    """, as_dict=True)
    frappe.response["message"] = {"employees": emp_list}

else:
    frappe.response["message"] = {"error": "Invalid block: " + block}
# frappe and json are already available in Server Script context
# No need to import

# Get filters from request
filters_json = frappe.form_dict.get('filters', '{}')

# Parse filters safely
try:
    if isinstance(filters_json, str):
        filters = frappe.parse_json(filters_json)
    else:
        filters = filters_json
except:
    filters = {}

# Get date range with default values
from_date = filters.get('from_date') or frappe.utils.get_first_day(frappe.utils.today()).strftime('%Y-%m-%d')
to_date = filters.get('to_date') or frappe.utils.today()
employee = filters.get('employee', '')
stage = filters.get('stage', '')

# Get today's date
today = frappe.utils.today()

# ========== KPIs ==========

# Leads
leads_today = frappe.db.count('Lead', {'creation': ['>=', today]})
total_leads = frappe.db.count('Lead', {'creation': ['between', [from_date, to_date]]})

# Surveys (check if doctype exists)
surveys_assigned = 0
surveys_completed = 0

try:
    if frappe.db.exists('DocType', 'Site Survey'):
        surveys_assigned = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabSite Survey` 
            WHERE creation BETWEEN %s AND %s
        """, (from_date, to_date))[0][0] or 0
        
        surveys_completed = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabSite Survey` 
            WHERE completed_date BETWEEN %s AND %s 
            AND completed_date IS NOT NULL
        """, (from_date, to_date))[0][0] or 0
except:
    pass

# Proposals
proposals_sent = frappe.db.count('Quotation', {
    'transaction_date': ['between', [from_date, to_date]],
    'docstatus': ['!=', 2]
})

proposals_pending = frappe.db.count('Quotation', {
    'transaction_date': ['between', [from_date, to_date]],
    'status': ['in', ['Draft', 'Open', 'Submitted']]
})

# Sales Orders
sales_orders = frappe.db.count('Sales Order', {
    'transaction_date': ['between', [from_date, to_date]],
    'docstatus': 1
})

order_value_result = frappe.db.sql("""
    SELECT COALESCE(SUM(grand_total), 0) 
    FROM `tabSales Order` 
    WHERE transaction_date BETWEEN %s AND %s 
    AND docstatus = 1
""", (from_date, to_date))

order_value = float(order_value_result[0][0]) if order_value_result else 0

# Projects
active_projects = frappe.db.count('Project', {
    'status': ['in', ['Open', 'Resumed']],
    'expected_start_date': ['<=', to_date]
})

completed_projects = frappe.db.count('Project', {
    'status': 'Completed',
    'expected_end_date': ['between', [from_date, to_date]]
})

# Payments Received
payment_received_result = frappe.db.sql("""
    SELECT COALESCE(SUM(paid_amount), 0) 
    FROM `tabPayment Entry` 
    WHERE posting_date BETWEEN %s AND %s 
    AND docstatus = 1 
    AND payment_type = 'Receive'
""", (from_date, to_date))

payment_received = float(payment_received_result[0][0]) if payment_received_result else 0

# Payments Pending
payment_pending_result = frappe.db.sql("""
    SELECT COALESCE(SUM(outstanding_amount), 0) 
    FROM `tabSales Invoice` 
    WHERE posting_date <= %s 
    AND docstatus = 1 
    AND outstanding_amount > 0
""", (to_date,))

payment_pending = float(payment_pending_result[0][0]) if payment_pending_result else 0

# Build KPIs dictionary
kpis = {
    'leads_today': leads_today,
    'total_leads': total_leads,
    'surveys_assigned': surveys_assigned,
    'surveys_completed': surveys_completed,
    'proposals_sent': proposals_sent,
    'proposals_pending': proposals_pending,
    'sales_orders': sales_orders,
    'order_value': order_value,
    'active_projects': active_projects,
    'completed_projects': completed_projects,
    'payment_received': payment_received,
    'payment_pending': payment_pending
}

# ========== LEADS DATA ==========
leads_query = """
    SELECT 
        l.name as lead_id,
        l.lead_name,
        l.mobile_no,
        l.creation as date,
        l.lead_owner as survey_assigned_to,
        l.status as survey_status,
        DATEDIFF(CURDATE(), l.creation) as tat_days
    FROM `tabLead` l
    WHERE l.creation BETWEEN %s AND %s
"""

leads_params = [from_date, to_date]

if employee:
    leads_query += " AND l.lead_owner = %s"
    leads_params.append(employee)

leads_query += " ORDER BY l.creation DESC LIMIT 100"

leads_data = frappe.db.sql(leads_query, tuple(leads_params), as_dict=True)

# Add proposal status to each lead
for lead in leads_data:
    try:
        quotation = frappe.db.get_value('Quotation', 
            {'party_name': lead.lead_id, 'docstatus': ['!=', 2]}, 
            ['name', 'status'], as_dict=True)
        
        if quotation:
            lead['proposal_status'] = quotation.status
            lead['quotation_id'] = quotation.name
        else:
            lead['proposal_status'] = 'Not Sent'
            lead['quotation_id'] = None
    except:
        lead['proposal_status'] = 'Not Sent'
        lead['quotation_id'] = None
    
    # Format date for display
    if lead.get('date'):
        lead['date'] = str(lead['date'])

# ========== PROPOSALS DATA ==========
proposals_query = """
    SELECT 
        q.name as quotation_id,
        q.customer_name as customer,
        q.owner as staff_name,
        q.transaction_date as sent_date,
        DATEDIFF(CURDATE(), q.transaction_date) as tat_days,
        q.status,
        q.grand_total
    FROM `tabQuotation` q
    WHERE q.transaction_date BETWEEN %s AND %s
    AND q.docstatus != 2
"""

proposals_params = [from_date, to_date]

if employee:
    proposals_query += " AND q.owner = %s"
    proposals_params.append(employee)

proposals_query += " ORDER BY q.transaction_date DESC LIMIT 100"

proposals_data = frappe.db.sql(proposals_query, tuple(proposals_params), as_dict=True)

# Format dates
for prop in proposals_data:
    if prop.get('sent_date'):
        prop['sent_date'] = str(prop['sent_date'])

# ========== SALES ORDERS DATA ==========
orders_data = frappe.db.sql("""
    SELECT 
        so.name as order_id,
        so.customer,
        so.transaction_date,
        so.grand_total,
        so.status,
        COALESCE(so.advance_paid, 0) as advance_paid
    FROM `tabSales Order` so
    WHERE so.transaction_date BETWEEN %s AND %s
    AND so.docstatus = 1
    ORDER BY so.transaction_date DESC
    LIMIT 100
""", (from_date, to_date), as_dict=True)

# Format dates
for order in orders_data:
    if order.get('transaction_date'):
        order['transaction_date'] = str(order['transaction_date'])

# ========== PROJECTS DATA ==========
projects_query = """
    SELECT 
        p.name as project_id,
        p.project_name,
        p.status,
        p.expected_start_date,
        p.expected_end_date,
        COALESCE(p.percent_complete, 0) as percent_complete
    FROM `tabProject` p
    WHERE p.creation BETWEEN %s AND %s
"""

projects_params = [from_date, to_date]

if employee:
    # Check if project_manager field exists
    try:
        if frappe.db.has_column('Project', 'project_manager'):
            projects_query += " AND p.project_manager = %s"
            projects_params.append(employee)
    except:
        pass

projects_query += " ORDER BY p.creation DESC LIMIT 100"

projects_data = frappe.db.sql(projects_query, tuple(projects_params), as_dict=True)

# Format dates
for proj in projects_data:
    if proj.get('expected_start_date'):
        proj['expected_start_date'] = str(proj['expected_start_date'])
    if proj.get('expected_end_date'):
        proj['expected_end_date'] = str(proj['expected_end_date'])

# ========== PAYMENTS DATA ==========
payments_data = frappe.db.sql("""
    SELECT 
        pe.name as payment_id,
        pe.party as customer,
        pe.posting_date,
        pe.paid_amount,
        pe.payment_type,
        pe.status
    FROM `tabPayment Entry` pe
    WHERE pe.posting_date BETWEEN %s AND %s
    AND pe.docstatus = 1
    ORDER BY pe.posting_date DESC
    LIMIT 100
""", (from_date, to_date), as_dict=True)

# Format dates
for payment in payments_data:
    if payment.get('posting_date'):
        payment['posting_date'] = str(payment['posting_date'])

# ========== EMPLOYEES DATA ==========
employees_data = frappe.db.sql("""
    SELECT 
        emp.name as employee_id,
        emp.employee_name,
        emp.designation,
        emp.status
    FROM `tabEmployee` emp
    WHERE emp.status = 'Active'
    ORDER BY emp.employee_name
    LIMIT 100
""", as_dict=True)

# ========== BUILD RESPONSE ==========
response_data = {
    'success': True,
    'kpis': kpis,
    'leads': leads_data,
    'proposals': proposals_data,
    'orders': orders_data,
    'projects': projects_data,
    'payments': payments_data,
    'employees': employees_data
}

# Set response
frappe.response['message'] = response_data

def is_permitted():
    rows = frappe.db.sql("""
        SELECT COUNT(*) as cnt FROM `tabHas Role`
        WHERE parent = %(user)s
          AND role IN ('Administrator','System Manager','Purchase Manager',
                       'Store Manager','Stock Manager','Accounts Manager')
    """, {"user": frappe.session.user}, as_dict=True)
    return rows and rows[0].cnt > 0


def get_kpis():
    total_items = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabItem` WHERE disabled = 0
    """)[0][0] or 0

    stock_value = frappe.db.sql("""
        SELECT COALESCE(SUM(IFNULL(actual_qty,0) * IFNULL(valuation_rate,0)), 0)
        FROM `tabBin`
    """)[0][0] or 0

    reserved_value = frappe.db.sql("""
        SELECT COALESCE(SUM(IFNULL(reserved_qty,0)), 0)
        FROM `tabBin`
    """)[0][0] or 0

    available_value = frappe.db.sql("""
        SELECT COALESCE(SUM(GREATEST(IFNULL(actual_qty,0) - IFNULL(reserved_qty,0), 0)), 0)
        FROM `tabBin`
    """)[0][0] or 0

    dispatching_projects = frappe.db.sql("""
        SELECT COUNT(DISTINCT project)
        FROM `tabDelivery Note`
        WHERE docstatus IN (0, 1)
          AND IFNULL(project, '') != ''
    """)[0][0] or 0

    low_stock = frappe.db.sql("""
        SELECT COUNT(DISTINCT i.name)
        FROM `tabItem` i
        LEFT JOIN `tabBin` b ON b.item_code = i.name
        WHERE i.disabled = 0
          AND IFNULL(i.safety_stock, 0) > 0
        GROUP BY i.name, i.safety_stock
        HAVING COALESCE(SUM(b.actual_qty), 0) <= i.safety_stock
    """)
    low_stock_count = len(low_stock) if low_stock else 0

    pending_dispatch = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabDelivery Note`
        WHERE docstatus = 0
           OR (docstatus = 1 AND status IN ('To Bill','To Deliver and Bill'))
    """)[0][0] or 0

    pending_grn = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabPurchase Order`
        WHERE docstatus = 1 AND IFNULL(per_received, 0) < 100
    """)[0][0] or 0

    return {
        "total_items": int(total_items),
        "stock_value": float(stock_value),
        "reserved_value": float(reserved_value),
        "available_value": float(available_value),
        "dispatching_projects": int(dispatching_projects),
        "low_stock": int(low_stock_count),
        "pending_dispatch": int(pending_dispatch),
        "pending_grn": int(pending_grn)
    }


def get_tasks():
    current_user = frappe.session.user
    mgr_check = frappe.db.sql("""
        SELECT COUNT(*) as cnt FROM `tabHas Role`
        WHERE parent = %(u)s
          AND role IN ('Projects Manager','Purchase Manager','Stock Manager',
                       'System Manager','Store Manager','Administrator')
    """, {"u": current_user}, as_dict=True)
    is_manager = mgr_check and mgr_check[0].cnt > 0

    if is_manager:
        rows = frappe.db.sql("""
            SELECT name, subject, priority, status, exp_end_date, project
            FROM `tabTask`
            WHERE status NOT IN ('Cancelled','Completed')
            ORDER BY FIELD(priority,'High','Medium','Low'),
                     IFNULL(exp_end_date,'9999-12-31') ASC
            LIMIT 10
        """, as_dict=True) or []
    else:
        rows = frappe.db.sql("""
            SELECT name, subject, priority, status, exp_end_date, project
            FROM `tabTask`
            WHERE status NOT IN ('Cancelled','Completed')
              AND _assign LIKE %(u)s
            ORDER BY FIELD(priority,'High','Medium','Low'),
                     IFNULL(exp_end_date,'9999-12-31') ASC
            LIMIT 10
        """, {"u": "%" + current_user + "%"}, as_dict=True) or []

    today = frappe.utils.today()
    tomorrow = frappe.utils.add_days(today, 1)
    out = []
    seen = {}
    for r in rows:
        if r.name in seen:
            continue
        seen[r.name] = 1
        due = str(r.exp_end_date) if r.exp_end_date else ""
        if due == today:
            due_label = "Due Today"
        elif due == tomorrow:
            due_label = "Due Tomorrow"
        elif due and due < today:
            due_label = "Overdue"
        elif due:
            due_label = due
        else:
            due_label = "--"
        out.append({
            "name": r.name,
            "subject": r.subject or r.name,
            "priority": r.priority or "Medium",
            "status": r.status or "",
            "due": due_label,
            "project": r.project or ""
        })
    return out


def get_projects():
    rows = frappe.db.sql("""
        SELECT name, project_name, status,
               expected_start_date, expected_end_date
        FROM `tabProject`
        WHERE status NOT IN ('Cancelled','Completed')
        ORDER BY IFNULL(expected_end_date,'9999-12-31') ASC
        LIMIT 10
    """, as_dict=True) or []

    out = []
    for r in rows:
        out.append({
            "name": r.name,
            "project_name": r.project_name or r.name,
            "status": r.status or "Open",
            "pending": r.status or "Open",
            "dispatched": 0,
            "total": 0
        })
    return out


def get_low_stock():
    rows = frappe.db.sql("""
        SELECT
            i.name,
            i.item_name,
            i.item_group,
            i.stock_uom,
            i.safety_stock,
            COALESCE(SUM(b.actual_qty), 0) AS actual_qty
        FROM `tabItem` i
        LEFT JOIN `tabBin` b ON b.item_code = i.name
        WHERE i.disabled = 0
          AND IFNULL(i.safety_stock, 0) > 0
        GROUP BY i.name, i.item_name, i.item_group, i.stock_uom, i.safety_stock
        HAVING actual_qty <= i.safety_stock
        ORDER BY actual_qty ASC
        LIMIT 50
    """, as_dict=True) or []

    out = []
    for r in rows:
        avail = float(r.actual_qty or 0)
        minq = float(r.safety_stock or 0)
        out.append({
            "name": r.name,
            "item_name": r.item_name or r.name,
            "item_group": r.item_group or "",
            "stock_uom": r.stock_uom or "",
            "avail": avail,
            "min": minq,
            "status": "Out of Stock" if avail <= 0 else "Low Stock"
        })
    return out


def get_dispatches():
    rows = frappe.db.sql("""
        SELECT name, customer, project, posting_date, total_qty, status
        FROM `tabDelivery Note`
        WHERE docstatus IN (0,1)
        ORDER BY posting_date DESC
        LIMIT 50
    """, as_dict=True) or []

    out = []
    for r in rows:
        status = r.status or "Draft"
        if status in ("To Bill", "To Deliver and Bill"):
            status = "Invoice Pending"
        out.append({
            "name": r.name,
            "customer": r.customer or "",
            "project": r.project or "",
            "posting_date": str(r.posting_date) if r.posting_date else "",
            "total_qty": float(r.total_qty or 0),
            "status": status
        })
    return out


def get_grns():
    rows = frappe.db.sql("""
        SELECT name, supplier, posting_date, grand_total, status
        FROM `tabPurchase Receipt`
        WHERE docstatus IN (0,1)
        ORDER BY posting_date DESC
        LIMIT 50
    """, as_dict=True) or []

    out = []
    for r in rows:
        out.append({
            "name": r.name,
            "supplier": r.supplier or "",
            "posting_date": str(r.posting_date) if r.posting_date else "",
            "grand_total": float(r.grand_total or 0),
            "status": r.status or "Draft"
        })
    return out


def get_purchase_orders():
    rows = frappe.db.sql("""
        SELECT name, supplier, transaction_date, schedule_date,
               grand_total, per_received, status
        FROM `tabPurchase Order`
        WHERE docstatus IN (0,1)
        ORDER BY transaction_date DESC
        LIMIT 50
    """, as_dict=True) or []

    out = []
    for r in rows:
        out.append({
            "name": r.name,
            "supplier": r.supplier or "",
            "transaction_date": str(r.transaction_date) if r.transaction_date else "",
            "schedule_date": str(r.schedule_date) if r.schedule_date else "",
            "grand_total": float(r.grand_total or 0),
            "per_received": float(r.per_received or 0),
            "status": r.status or "Draft"
        })
    return out


def get_purchase_summary():
    rows = frappe.db.sql("""
        SELECT
            MONTH(transaction_date) AS month_no,
            MONTHNAME(transaction_date) AS month_name,
            COUNT(*) AS total_po,
            COALESCE(SUM(grand_total), 0) AS total_amount,
            COALESCE(SUM(CASE WHEN per_received = 100 THEN grand_total ELSE 0 END), 0) AS received_amount
        FROM `tabPurchase Order`
        WHERE transaction_date IS NOT NULL
          AND YEAR(transaction_date) = YEAR(CURDATE())
        GROUP BY MONTH(transaction_date), MONTHNAME(transaction_date)
        ORDER BY month_no DESC
        LIMIT 12
    """, as_dict=True) or []

    out = []
    for r in rows:
        out.append({
            "month": r.month_name or "",
            "month_no": int(r.month_no or 0),
            "total_po": int(r.total_po or 0),
            "total_amount": float(r.total_amount or 0),
            "received_amount": float(r.received_amount or 0)
        })
    return out


def get_inventory_rows():
    rows = frappe.db.sql("""
        SELECT
            i.name,
            i.item_name,
            i.item_group,
            i.stock_uom,
            IFNULL(b.actual_qty, 0) AS opening_stock,
            IFNULL(b.reserved_qty, 0) AS reserved_qty,
            GREATEST(IFNULL(b.actual_qty, 0) - IFNULL(b.reserved_qty, 0), 0) AS available_qty
        FROM `tabItem` i
        LEFT JOIN `tabBin` b ON b.item_code = i.name
        WHERE i.disabled = 0
        ORDER BY i.modified DESC
        LIMIT 200
    """, as_dict=True) or []

    out = []
    for r in rows:
        out.append({
            "name": r.name,
            "item_name": r.item_name or r.name,
            "item_group": r.item_group or "",
            "stock_uom": r.stock_uom or "",
            "opening_stock": float(r.opening_stock or 0),
            "reserved_qty": float(r.reserved_qty or 0),
            "available_qty": float(r.available_qty or 0)
        })
    return out


def get_stock_rows():
    rows = frappe.db.sql("""
        SELECT
            name,
            posting_date,
            stock_entry_type,
            docstatus,
            IFNULL(total_incoming_value, 0) AS qty_in,
            IFNULL(total_outgoing_value, 0) AS qty_out,
            purpose AS warehouse
        FROM `tabStock Entry`
        WHERE docstatus IN (0,1)
        ORDER BY posting_date DESC
        LIMIT 50
    """, as_dict=True) or []

    out = []
    for r in rows:
        out.append({
            "name": r.name,
            "posting_date": str(r.posting_date) if r.posting_date else "",
            "type": r.stock_entry_type or "",
            "docstatus": int(r.docstatus or 0),
            "qty_in": float(r.qty_in or 0),
            "qty_out": float(r.qty_out or 0),
            "warehouse": r.warehouse or "",
            "status": "Submitted" if int(r.docstatus or 0) == 1 else "Draft"
        })
    return out


block = frappe.form_dict.get("block", "summary")

if not is_permitted():
    frappe.response["message"] = {"error": "not permitted"}

elif block == "summary":
    frappe.response["message"] = {
        "kpis": get_kpis(),
        "tasks": get_tasks(),
        "projects": get_projects(),
        "low_stocklist": get_low_stock(),
        "dispatches": get_dispatches(),
        "grns": get_grns(),
        "purchase_orders": get_purchase_orders(),
        "purchase_summary": get_purchase_summary()
    }

elif block == "kpis":
    frappe.response["message"] = get_kpis()

elif block == "tasks":
    frappe.response["message"] = get_tasks()

elif block == "projects":
    frappe.response["message"] = get_projects()

elif block == "low_stock":
    frappe.response["message"] = get_low_stock()

elif block == "dispatches":
    frappe.response["message"] = get_dispatches()

elif block == "grns":
    frappe.response["message"] = get_grns()

elif block == "purchase_orders":
    frappe.response["message"] = get_purchase_orders()

elif block == "purchase_summary":
    frappe.response["message"] = get_purchase_summary()

elif block == "inventory":
    frappe.response["message"] = get_inventory_rows()

elif block == "stock":
    frappe.response["message"] = get_stock_rows()

else:
    frappe.response["message"] = {"error": "invalid block"}
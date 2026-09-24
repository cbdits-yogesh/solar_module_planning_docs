def get_command_center_data():

    def nval(v):
        try:
            return float(v or 0)
        except:
            return 0

    def money(v):
        try:
            return "₹{:,.0f}".format(float(v or 0))
        except:
            return "₹0"

    # ── KPI 1: Total Items ─────────────────────────────────────────
    # FIX: use count directly instead of len(get_all) which is capped at 5000
    total_items_count = frappe.db.sql("""
        SELECT COUNT(*) as cnt FROM `tabItem` WHERE disabled = 0
    """, as_dict=True)
    total_items_count = total_items_count[0].cnt if total_items_count else 0

    # still fetch items for bin calculations (keep limit for performance)
    items = frappe.db.get_all(
        "Item",
        filters={"disabled": 0},
        fields=["name", "item_name", "item_group", "stock_uom", "image", "is_stock_item", "safety_stock"],
        order_by="modified desc",
        limit_page_length=5000
    )

    item_names = [d.name for d in items if d.name]

    bins = []
    if item_names:
        bins = frappe.db.sql("""
            SELECT
                item_code,
                SUM(actual_qty) AS actual_qty,
                SUM(reserved_qty) AS reserved_qty,
                SUM(reserved_stock) AS reserved_stock,
                SUM(projected_qty) AS projected_qty,
                SUM(stock_value) AS stock_value
            FROM `tabBin`
            WHERE item_code IN %(items)s
            GROUP BY item_code
        """, {"items": tuple(item_names)}, as_dict=True)

    bin_map = {}
    for b in bins:
        bin_map[b.item_code] = b

    valuation_map = {}
    if item_names:
        val_rows = frappe.db.sql("""
            SELECT name, valuation_rate
            FROM `tabItem`
            WHERE name IN %(items)s
        """, {"items": tuple(item_names)}, as_dict=True)
        for v in val_rows:
            valuation_map[v.name] = nval(v.valuation_rate)

    total_stock_value = 0
    total_reserved_qty = 0
    total_available_qty = 0
    total_low_stock = 0
    low_stock_list = []

    for it in items:
        b = bin_map.get(it.name, {})
        actual_qty = nval(b.get("actual_qty"))
        reserved_qty = nval(b.get("reserved_qty")) or nval(b.get("reserved_stock"))
        available_qty = max(actual_qty - reserved_qty, 0)

        bin_stock_val = nval(b.get("stock_value"))
        if bin_stock_val > 0:
            item_stock_value = bin_stock_val
        else:
            item_stock_value = actual_qty * valuation_map.get(it.name, 0)

        total_stock_value = total_stock_value + item_stock_value
        total_reserved_qty = total_reserved_qty + reserved_qty
        total_available_qty = total_available_qty + available_qty

        # ── KPI 5 / Low Stock List FIX ────────────────────────────
        # Use safety_stock field. Item is low stock if:
        # actual_qty <= safety_stock (and safety_stock > 0)
        # OR actual_qty <= 0 (out of stock regardless)
        safety_stock = nval(it.get("safety_stock"))
        is_out_of_stock = actual_qty <= 0
        is_low_stock = (safety_stock > 0 and actual_qty <= safety_stock)

        if is_out_of_stock or is_low_stock:
            total_low_stock = total_low_stock + 1
            stock_status = "Out of Stock" if is_out_of_stock else "Low Stock"
            low_stock_list.append({
                "item": it.name,
                "item_name": it.item_name or "",
                "item_group": it.item_group or "",
                "stock_uom": it.stock_uom or "",
                "avail": actual_qty,
                "min": safety_stock,
                "status": stock_status
            })

    # sort: out of stock first, then by biggest shortage
    low_stock_list = sorted(
        low_stock_list,
        key=lambda x: (0 if x["status"] == "Out of Stock" else 1, x["avail"] - x["min"])
    )

    dispatches = frappe.db.get_all(
        "Delivery Note",
        filters={"docstatus": 1},
        fields=["name", "customer", "posting_date", "status", "modified"],
        order_by="modified desc",
        limit_page_length=10
    )

    total_dispatching_projects = frappe.db.count("Delivery Note", {"docstatus": 1})

    # ── KPI 6: Pending Dispatch FIX ───────────────────────────────
    # Count Draft (docstatus=0) AND submitted but status = "To Bill"
    # so we catch everything that hasn't been fully completed
    pending_dispatch_rows = frappe.db.sql("""
        SELECT COUNT(*) as cnt FROM `tabDelivery Note`
        WHERE docstatus = 0
           OR (docstatus = 1 AND status IN ('To Bill', 'To Deliver and Bill', 'Draft'))
    """, as_dict=True)
    total_pending_dispatch = pending_dispatch_rows[0].cnt if pending_dispatch_rows else 0

    grns = frappe.db.get_all(
        "Purchase Receipt",
        filters={"docstatus": 1},
        fields=["name", "supplier", "posting_date", "status", "modified"],
        order_by="modified desc",
        limit_page_length=10
    )

    total_pending_grn = frappe.db.count("Purchase Receipt", {"docstatus": 0})

    stock_entries = frappe.db.get_all(
        "Stock Entry",
        filters={"docstatus": 1},
        fields=["name", "stock_entry_type", "posting_date", "modified"],
        order_by="modified desc",
        limit_page_length=10
    )

    material_requests = frappe.db.get_all(
        "Material Request",
        filters={"docstatus": ["in", [0, 1]]},
        fields=["name", "transaction_date", "material_request_type", "status", "modified"],
        order_by="modified desc",
        limit_page_length=10
    )

    purchase_orders = frappe.db.get_all(
        "Purchase Order",
        filters={"docstatus": ["in", [0, 1]]},
        fields=["name", "supplier", "transaction_date", "status", "modified"],
        order_by="modified desc",
        limit_page_length=10
    )

    suppliers = frappe.db.get_all(
        "Supplier",
        filters={"disabled": 0},
        fields=["name", "supplier_name", "modified"],
        order_by="modified desc",
        limit_page_length=10
    )

    # ── KPI 3: Reserved from Sales Orders ────────────────────────
    # FIX: was using reserved_qty from Bin (warehouse-level).
    # Use Sales Order items for project-level reserved qty
    reserved_so_rows = frappe.db.sql("""
        SELECT COALESCE(SUM(soi.qty - soi.delivered_qty), 0) as reserved_qty
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE so.docstatus = 1
          AND so.status NOT IN ('Closed', 'Cancelled', 'Completed')
          AND soi.delivered_qty < soi.qty
    """, as_dict=True)
    reserved_so_qty = reserved_so_rows[0].reserved_qty if reserved_so_rows else total_reserved_qty

    kpis = {
        "total_items": total_items_count,
        "stock_value": money(total_stock_value),
        "reserved_value": str(int(reserved_so_qty)),
        "available_value": str(int(total_available_qty)),
        "low_stock": total_low_stock,
        "pending_dispatch": total_pending_dispatch,
        "pending_grn": total_pending_grn
    }

    # ── Tasks FIX: real data, role-aware ──────────────────────────
    # Was hardcoded. Now fetches from tabTask.
    # Managers see all open tasks; others see only their own.
    current_user = frappe.session.user
    user_roles = frappe.get_roles(current_user)
    is_manager = (
        "Projects Manager" in user_roles or
        "Purchase Manager" in user_roles or
        "Stock Manager" in user_roles or
        "System Manager" in user_roles or
        "Store Manager" in user_roles
    )

    if is_manager:
        task_rows = frappe.db.sql("""
            SELECT name, subject, priority, exp_end_date, status, project
            FROM `tabTask`
            WHERE status NOT IN ('Cancelled', 'Completed')
            ORDER BY FIELD(priority,'High','Medium','Low'), exp_end_date ASC
            LIMIT 20
        """, as_dict=True)
    else:
        task_rows = frappe.db.sql("""
            SELECT name, subject, priority, exp_end_date, status, project
            FROM `tabTask`
            WHERE status NOT IN ('Cancelled', 'Completed')
              AND _assign LIKE """ + frappe.db.escape("%" + current_user + "%") + """
            ORDER BY FIELD(priority,'High','Medium','Low'), exp_end_date ASC
            LIMIT 20
        """, as_dict=True)

    tasks = []
    today = frappe.utils.today()
    tomorrow = frappe.utils.add_days(today, 1)
    seen_tasks = {}
    for t in task_rows:
        if t.name in seen_tasks:
            continue
        seen_tasks[t.name] = 1
        due = t.exp_end_date
        if due:
            due_str = str(due)
            if due_str == today:
                due_label = "Due Today"
            elif due_str == tomorrow:
                due_label = "Due Tomorrow"
            elif due_str < today:
                due_label = "Overdue"
            else:
                due_label = due_str
        else:
            due_label = "--"
        tasks.append({
            "name": t.subject or t.name,
            "priority": t.priority or "Medium",
            "due": due_label,
            "project": t.project or ""
        })

    # ── Projects FIX: real data with project names ────────────────
    # Was hardcoded. Now fetches open projects with pending/dispatched qty.
    project_rows = frappe.db.sql("""
        SELECT
            p.name as project_id,
            p.project_name,
            p.status,
            COALESCE(so_data.pending_qty, 0) as pending,
            COALESCE(dn_data.dispatched_qty, 0) as dispatched
        FROM `tabProject` p
        LEFT JOIN (
            SELECT so.project,
                   SUM(soi.qty - soi.delivered_qty) as pending_qty
            FROM `tabSales Order Item` soi
            INNER JOIN `tabSales Order` so ON so.name = soi.parent
            WHERE so.docstatus = 1
              AND so.status NOT IN ('Closed','Cancelled','Completed')
              AND soi.delivered_qty < soi.qty
              AND so.project IS NOT NULL AND so.project != ''
            GROUP BY so.project
        ) so_data ON so_data.project = p.name
        LEFT JOIN (
            SELECT dn.project,
                   SUM(dni.qty) as dispatched_qty
            FROM `tabDelivery Note Item` dni
            INNER JOIN `tabDelivery Note` dn ON dn.name = dni.parent
            WHERE dn.docstatus = 1
              AND dn.project IS NOT NULL AND dn.project != ''
            GROUP BY dn.project
        ) dn_data ON dn_data.project = p.name
        WHERE p.status = 'Open'
        ORDER BY p.creation DESC
        LIMIT 20
    """, as_dict=True)

    projects = []
    for p in project_rows:
        pending = int(p.pending or 0)
        dispatched = int(p.dispatched or 0)
        total = pending + dispatched
        disp_str = str(dispatched) + "/" + str(total) if total > 0 else "0/0"
        # derive a simple status label
        if pending == 0 and dispatched > 0:
            proj_status = "Completed"
        elif dispatched == 0:
            proj_status = "Not Started"
        else:
            pct = int((dispatched / total) * 100) if total > 0 else 0
            proj_status = "On Track" if pct >= 50 else "Partial"
        projects.append({
            "id": p.project_id,
            "site": p.project_name or p.project_id,
            "pending": pending,
            "disp": disp_str,
            "status": proj_status
        })

    return {
        "kpis": kpis,
        "tasks": tasks,
        "projects": projects,
        "low_stock_list": low_stock_list,
        "dispatches": dispatches,
        "grns": grns,
        "stock_entries": stock_entries,
        "material_requests": material_requests,
        "purchase_orders": purchase_orders,
        "suppliers": suppliers,
        "dispatching_projects": total_dispatching_projects
    }

frappe.response["message"] = get_command_center_data()
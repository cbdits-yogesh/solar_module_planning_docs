# Server Script: get_store_dashboard_data
# Type: API

def get_data(block, kpi_type=None):
    user = frappe.session.user
    
    if block == "user_info":
        emp_name = frappe.db.get_value("Employee", {"user_id": user}, "employee_name")
        if not emp_name:
            emp_name = frappe.db.get_value("User", user, "full_name")
        return {"name": emp_name}

    elif block == "metrics":
        total_items = frappe.db.count("Item", {"disabled": 0})
        bin_stats = frappe.db.sql("""
            SELECT SUM(stock_value) as val, SUM(reserved_qty) as res, SUM(actual_qty) as avail 
            FROM `tabBin`
        """, as_dict=1)[0]
        
        low_stock = frappe.db.sql("SELECT COUNT(name) FROM `tabBin` WHERE actual_qty > 0 AND actual_qty <= projected_qty")[0][0]
        pending_dispatch = frappe.db.count("Delivery Note", {"docstatus": 0})
        pending_grn = frappe.db.count("Purchase Receipt", {"docstatus": 0})
        
        return {
            "total_items": str(total_items or 0),
            "stock_value": "₹ " + str(round(bin_stats.val or 0, 2)),
            "reserved": str(bin_stats.res or 0) + " Nos",
            "available": str(bin_stats.avail or 0) + " Nos",
            "low_stock": str(low_stock or 0) + " Items",
            "pending_dispatch": str(pending_dispatch or 0) + " Dispatches",
            "pending_grn": str(pending_grn or 0) + " PR"
        }
        
    elif block == "kpi_table":
        # Har KPI ke liye alag query taaki proper data list me aaye
        if kpi_type == "total_items":
            return frappe.db.sql("SELECT item_code, item_name, item_group, stock_uom FROM `tabItem` WHERE disabled=0", as_dict=1)
        
        elif kpi_type == "stock_value" or kpi_type == "available":
            return frappe.db.sql("SELECT item_code, warehouse, actual_qty, stock_value FROM `tabBin` WHERE actual_qty > 0", as_dict=1)
            
        elif kpi_type == "reserved":
            return frappe.db.sql("SELECT item_code, warehouse, reserved_qty FROM `tabBin` WHERE reserved_qty > 0", as_dict=1)
            
        elif kpi_type == "low_stock":
            return frappe.db.sql("SELECT item_code, warehouse, actual_qty, projected_qty FROM `tabBin` WHERE actual_qty > 0 AND actual_qty <= projected_qty", as_dict=1)
            
        elif kpi_type == "pending_dispatch":
            return frappe.db.sql("SELECT name as dispatch_id, customer, posting_date, grand_total FROM `tabDelivery Note` WHERE docstatus=0", as_dict=1)
            
        elif kpi_type == "pending_grn":
            return frappe.db.sql("SELECT name as receipt_id, supplier, posting_date, grand_total FROM `tabPurchase Receipt` WHERE docstatus=0", as_dict=1)
            
        elif kpi_type == "quick_entry":
            return frappe.db.sql("SELECT name, stock_entry_type, purpose, posting_date FROM `tabStock Entry` ORDER BY creation DESC LIMIT 50", as_dict=1)
            
        return []

    elif block == "project_status":
        return [
            {"id": "PRJ-2024-0012", "site": "ABC Pvt Ltd", "pending": 30, "dispatched": "200/230", "status": "On Track", "color": "green"},
            {"id": "PRJ-2024-0011", "site": "Sunshine Hotel", "pending": 7, "dispatched": "400/407", "status": "Partial", "color": "orange"}
        ]
        
    elif block == "low_stock_alerts":
        return frappe.db.sql("SELECT item_code as item, actual_qty as qty, 'Low Stock' as alert FROM `tabBin` WHERE actual_qty > 0 AND actual_qty <= projected_qty LIMIT 5", as_dict=1)

frappe.response["message"] = get_data(frappe.form_dict.get("block"), frappe.form_dict.get("kpi_type"))
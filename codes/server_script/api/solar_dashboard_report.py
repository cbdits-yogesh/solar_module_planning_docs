import frappe
from frappe.utils import nowdate, add_months
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum, IfNull

@frappe.whitelist()
def solar_dashboard_data(
    doctype,
    time_range="all",
    group_by="status",
    trend="",
    from_date=None,
    to_date=None,
    chart_type="pie"
):

    if doctype == "Payment":
        doctype = "Payment Entry"

    if not frappe.db.table_exists(f"tab{doctype}"):
        frappe.throw(f"Invalid DocType: {doctype}")

    dt = DocType(doctype)

    # -------------------------
    # DATE FILTER
    # -------------------------
    cond = (dt.docstatus < 2)

    if time_range == "today":
        cond &= (dt.creation == nowdate())

    elif time_range == "month":
        cond &= (dt.creation >= add_months(nowdate(), -1))

    elif time_range == "year":
        cond &= (dt.creation >= add_months(nowdate(), -12))

    elif time_range == "custom" and from_date and to_date:
        cond &= (dt.creation.between(from_date, to_date))

    # -------------------------
    # GROUP BY
    # -------------------------
    allowed = ["status", "owner", "source"]
    if group_by not in allowed:
        group_by = "status"

    group_col = getattr(dt, group_by)

    # -------------------------
    # TILES
    # -------------------------
    rows = (
        frappe.qb
        .from_(dt)
        .select(group_col.as_("label"), Count(dt.name).as_("count"))
        .where(cond)
        .groupby(group_col)
    ).run(as_dict=True)

    labels = [r.label or "Not Set" for r in rows]
    counts = [r.count for r in rows]

    # -------------------------
    # TOTAL
    # -------------------------
    total = (
        frappe.qb
        .from_(dt)
        .select(Count(dt.name))
        .where(cond)
    ).run()[0][0]

    # -------------------------
    # SALES ORDER EXTRA
    # -------------------------
    grand_total = advance_paid = pending_amount = 0

    if doctype == "Sales Order":
        res = (
            frappe.qb
            .from_(dt)
            .select(
                Sum(dt.grand_total),
                Sum(dt.advance_paid),
                Sum(dt.grand_total - IfNull(dt.advance_paid, 0))
            )
            .where(cond)
        ).run()[0]

        grand_total = res[0] or 0
        advance_paid = res[1] or 0
        pending_amount = res[2] or 0

    return {
        "data": rows,
        "labels": labels,
        "counts": counts,
        "total": total,
        "grand_total": grand_total,
        "advance_paid": advance_paid,
        "pending_amount": pending_amount
    }

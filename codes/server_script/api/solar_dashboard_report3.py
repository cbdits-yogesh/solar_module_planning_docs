# doctype = frappe.form_dict.get("doctype")
# time_range = frappe.form_dict.get("time_range")
# group_by = frappe.form_dict.get("group_by") or "status"

# # ✅ FIX 1: Payment is not a real DocType
# if doctype == "Payment":
#     doctype = "Payment Entry"

# # ✅ FIX 2: Payment Entry has no status field
# if doctype == "Payment Entry" and group_by == "status":
#     group_by = "mode_of_payment"

# if not doctype:
#     frappe.throw("Doctype is required")

# date_filter = ""
# today = frappe.utils.today()

# if time_range == "today":
#     date_filter = " AND DATE(creation) = '%s'" % today

# elif time_range == "month":
#     date_filter = " AND MONTH(creation)=MONTH(CURDATE()) AND YEAR(creation)=YEAR(CURDATE())"

# elif time_range == "year":
#     date_filter = " AND YEAR(creation)=YEAR(CURDATE())"

# # ---------------- OWNER SPECIAL HANDLING ----------------
# if group_by == "owner":

#     query = (
#         " SELECT IFNULL(u.first_name, t.owner) AS label, "
#         " COUNT(t.name) AS count "
#         " FROM `tab" + doctype + "` t "
#         " LEFT JOIN `tabUser` u ON u.name = t.owner "
#         " WHERE t.docstatus < 2 "
#         + date_filter +
#         " GROUP BY label "
#     )

# # ---------------- SOURCE FIELD (CRM SAFE) ----------------
# elif group_by == "source":

#     query = (
#         " SELECT source AS label, COUNT(name) AS count "
#         " FROM `tab" + doctype + "` "
#         " WHERE docstatus < 2 "
#         + date_filter +
#         " GROUP BY source "
#     )

# # ---------------- DEFAULT GROUP BY ----------------
# else:

#     query = (
#         " SELECT " + group_by + " AS label, COUNT(name) AS count "
#         " FROM `tab" + doctype + "` "
#         " WHERE docstatus < 2 "
#         + date_filter +
#         " GROUP BY " + group_by
#     )

# data = frappe.db.sql(query, as_dict=True)

# labels = []
# counts = []
# total = 0

# for row in data:
#     labels.append(row.get("label"))
#     counts.append(row.get("count"))
#     total = total + row.get("count")

# frappe.response["message"] = {
#     "data": data,
#     "labels": labels,
#     "counts": counts,
#     "total": total
# }


doctype = frappe.form_dict.get("doctype")
time_range = frappe.form_dict.get("time_range")
group_by = frappe.form_dict.get("group_by") or "status"

if doctype == "Payment":
    doctype = "Payment Entry"

if doctype == "Payment Entry" and group_by == "status":
    group_by = "mode_of_payment"

if not doctype:
    frappe.throw("Doctype is required")

is_sales_order = doctype == "Sales Order"
today = frappe.utils.today()

data = []
params = []

# ---------------- LEAD / GENERIC ----------------
if doctype != "Sales Order":

    if group_by == "owner":
        query = """
            SELECT IFNULL(u.first_name, t.owner) AS label,
                   COUNT(t.name) AS count
            FROM `tab{}` t
            LEFT JOIN `tabUser` u ON u.name = t.owner
            WHERE t.docstatus < 2
            GROUP BY label
        """.format(doctype)

    elif group_by == "source":
        query = """
            SELECT source AS label,
                   COUNT(name) AS count
            FROM `tab{}`
            WHERE docstatus < 2
            GROUP BY source
        """.format(doctype)

    else:
        query = """
            SELECT {} AS label,
                   COUNT(name) AS count
            FROM `tab{}`
            WHERE docstatus < 2
            GROUP BY {}
        """.format(group_by, doctype, group_by)

    data = frappe.db.sql(query, as_dict=True)

# ---------------- SALES ORDER ----------------
else:
    query = """
        SELECT {} AS label,
               COUNT(name) AS count,
               SUM(grand_total) AS grand_total,
               SUM(advance_paid) AS advance_paid
        FROM `tabSales Order`
        WHERE docstatus < 2
        GROUP BY {}
    """.format(group_by, group_by)

    data = frappe.db.sql(query, as_dict=True)

# ---------------- AGGREGATE ----------------
labels = []
counts = []
total = 0
grand_total = 0
advance_paid = 0

for row in data:
    labels.append(row.get("label"))
    counts.append(row.get("count"))
    total += row.get("count") or 0

    if is_sales_order:
        grand_total += row.get("grand_total") or 0
        advance_paid += row.get("advance_paid") or 0

frappe.response["message"] = {
    "data": data,
    "labels": labels,
    "counts": counts,
    "total": total,
    "grand_total": grand_total,
    "advance_paid": advance_paid,
    "pending_amount": grand_total - advance_paid
}

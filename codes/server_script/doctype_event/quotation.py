'''
Reference Document Type: Proposal
DocType Event: Before Save
'''

total_cable_amt = 0

if doc.extra_cable_calculation:
    for row in doc.extra_cable_calculation:
        row.amt = frappe.utils.flt(row.length) * frappe.utils.flt(row.cable_rate)
        total_cable_amt = total_cable_amt + frappe.utils.flt(row.amt)

if doc.items:
    for item in doc.items:
        if item.item_code == "Solar Power Plant":
            if not item.solar_base_rate:
                item.solar_base_rate = frappe.utils.flt(item.rate)

            item.rate = frappe.utils.flt(item.solar_base_rate) + total_cable_amt
            item.amount = frappe.utils.flt(item.qty) * frappe.utils.flt(item.rate)
            break

total_cable_amt = 0

if doc.extra_cable_calculation:
    for row in doc.extra_cable_calculation:
        row.amt = frappe.utils.flt(row.length) * frappe.utils.flt(row.cable_rate)
        total_cable_amt = total_cable_amt + frappe.utils.flt(row.amt)

solar_cable_share = total_cable_amt * 0.70
installation_cable_share = total_cable_amt * 0.30

if doc.items:
    for item in doc.items:
        if item.item_code == "Solar Power Plant":
            if not item.solar_base_rate:
                item.solar_base_rate = frappe.utils.flt(item.rate)

            item.rate = frappe.utils.flt(item.solar_base_rate) + solar_cable_share
            item.amount = frappe.utils.flt(item.qty) * frappe.utils.flt(item.rate)

        elif item.item_code == "Installation & Commissioning":
            if not item.solar_base_rate:
                item.solar_base_rate = frappe.utils.flt(item.rate)

            item.rate = frappe.utils.flt(item.solar_base_rate) + installation_cable_share
            item.amount = frappe.utils.flt(item.qty) * frappe.utils.flt(item.rate)
/**
 * DocType: Proposal
 * Apply To: Form
 */

frappe.ui.form.on('Quotation', {
    party_name: function(frm) {
        if (frm.doc.quotation_to === 'Lead') {
            frm.set_value('lead', frm.doc.party_name);
        }
    }
});


function update_cable_and_item_rates(frm) {
    let total_cable_amt = 0;

    (frm.doc.extra_cable_calculation || []).forEach(row => {
        row.amt = flt(row.length) * flt(row.cable_rate);
        total_cable_amt += flt(row.amt);
    });

    frm.refresh_field("extra_cable_calculation");

    let solar_cable_share = total_cable_amt * 0.70;
    let installation_cable_share = total_cable_amt * 0.30;

    (frm.doc.items || []).forEach(item => {
        if (item.item_code === "Solar Power Plant") {
            if (!item.solar_base_rate) {
                item.solar_base_rate = flt(item.rate);
            }
            item.rate = flt(item.solar_base_rate) + solar_cable_share;
            item.amount = flt(item.qty) * flt(item.rate);
        }

        if (item.item_code === "Installation & Commissioning") {
            if (!item.solar_base_rate) {
                item.solar_base_rate = flt(item.rate);
            }
            item.rate = flt(item.solar_base_rate) + installation_cable_share;
            item.amount = flt(item.qty) * flt(item.rate);
        }
    });

    frm.refresh_field("items");
}

frappe.ui.form.on("Quotation", {
    refresh(frm) {
        update_cable_and_item_rates(frm);
    }
});

frappe.ui.form.on("Cable Calculation Table", {
    length(frm) {
        update_cable_and_item_rates(frm);
    },
    cable_rate(frm) {
        update_cable_and_item_rates(frm);
    }
});

frappe.ui.form.on("Quotation Item", {
    rate(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code === "Solar Power Plant" || row.item_code === "Installation & Commissioning") {
            row.solar_base_rate = flt(row.rate);
            update_cable_and_item_rates(frm);
        }
    },
    qty(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code === "Solar Power Plant" || row.item_code === "Installation & Commissioning") {
            update_cable_and_item_rates(frm);
        }
    }
});




// _______________ Duplicate Quotation Check______________

frappe.ui.form.on('Quotation', {
    onload: function(frm) {
        // If it's a new document and site_survey is pre-filled (from clicking "Create" on Site Survey)
        if (frm.doc.__islocal && frm.doc.site_survey) {
            check_existing_quotation(frm);
        }
    },
    
    site_survey: function(frm) {
        // If they manually select/change the Site Survey field
        if (frm.doc.site_survey) {
            check_existing_quotation(frm);
        }
    }
});

function check_existing_quotation(frm) {
    frappe.db.count("Quotation", {
        filters: {
            "site_survey": frm.doc.site_survey,
            "docstatus": ["!=", 2],  // Not Cancelled
            "name": ["!=", frm.doc.name] // Exclude current doc
        }
    }).then(count => {
        if (count > 0) {
            // 1. Show instant error message
            frappe.msgprint({
                title: __("Cannot Create Quotation"),
                message: __("An active Quotation already exists for Site Survey <b>{0}</b>. Please cancel the existing one first.").replace("{0}", frm.doc.site_survey),
                indicator: "red"
            });
            
            // 2. Clear the field so they cannot save the form
            frm.set_value("site_survey", "");
        }
    });
}
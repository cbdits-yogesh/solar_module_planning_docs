/**
 * DocType: Site Survey
 * Apply To: Form
 */

frappe.ui.form.on("Site Survey", {
    surveyed_by: function(frm) {
        if (frm.doc.surveyed_by) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "User",
                    filters: { name: frm.doc.surveyed_by },
                    fieldname: ["full_name"]
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint("Surveyed By: " + r.message.full_name);
                        // OR if you want to set it into another field:
                        // frm.set_value("surveyed_by_name", r.message.full_name);
                    }
                }
            });
        }
    }
});

frappe.ui.form.on('Site Survey', {
    refresh(frm) {
        setTimeout(() => {
            $(`.document-link[data-doctype="Quotation"] .btn-new`).hide();
        }, 10);
    }
});

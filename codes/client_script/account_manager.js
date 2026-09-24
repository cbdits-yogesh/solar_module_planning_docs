/**
 * DocType: Project
 * Apply To: Form
 */

frappe.ui.form.on("Project", {
    onload: function(frm) {
        if (frm.is_new() && frm.doc.sales_order && !frm.doc.custom_project_manager) {
            frappe.db.get_value("Sales Order", frm.doc.sales_order, "project_manager")
                .then(r => {
                    if (r.message && r.message.project_manager) {
                        frm.set_value("custom_project_manager", r.message.project_manager);
                    }
                });
        }
    },

    refresh(frm) {
        if (frm.doc.custom_upload_document) {
            frm.add_custom_button("Download Documents", () => {
                const a = document.createElement("a");
                a.href = frm.doc.custom_upload_document;
                a.download = "";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }, "Actions");
        }
    },
});
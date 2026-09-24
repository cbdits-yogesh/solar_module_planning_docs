/**
 * DocType: Sales Order
 * Apply To: Form
 */

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus !== 1) return;

        setTimeout(() => {
            $(`.document-link[data-doctype="Project"] .btn-new`).hide();
            $(`.document-link[data-doctype="Liaisoning And Synchronization"] .btn-new`).hide();
        }, 500);

        frappe.db.count('Project', { filters: { sales_order: frm.doc.name } }).then(count => {
            if (count > 0) {
                setTimeout(() => frm.remove_custom_button('Project', 'Create'), 300);
            }
        });

        if (frappe.boot.user.can_read.includes('Liaisoning And Synchronization')) {
            frappe.db.count('Liaisoning And Synchronization', {
                filters: { sales_order: frm.doc.name }
            }).then(count => {
                if (count === 0) {
                    frm.add_custom_button('Liaisoning And Synchronization', function() {
                        frappe.new_doc('Liaisoning And Synchronization', { sales_order: frm.doc.name });
                    }, 'Create');
                }
            }).catch(() => {});
        }
    }
});

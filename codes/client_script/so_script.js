/**
 * DocType: Sales Order
 * Apply To: Form
 */

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        setTimeout(function() {
            // --- Material Availability Checks ---
            if (frm.doc.custom_material_availability !== 'Available') {
                frm.remove_custom_button('Project', 'Create');
                frm.remove_custom_button('Delivery Note', 'Create');
                frm.remove_custom_button('Pick List', 'Create');

                if (frm.doc.docstatus === 1 && frm.doc.status !== 'Closed') {
                    frm.dashboard.set_headline_alert(
                        'Project and Delivery Note creation is disabled until Material is Not Available',
                        'orange'
                    );
                }
            }

            // --- Work Order Button Logic ---
            if (frm.doc.docstatus === 1) {
                const without_advance = frm.doc.without_advance;
                const advance_paid = flt(frm.doc.advance_paid);
                const rounded_total = flt(frm.doc.rounded_total);
                const advance_percent = rounded_total > 0 ? (advance_paid / rounded_total) * 100 : 0;

                const can_show_work_order = without_advance || advance_percent >= 45;

                if (!can_show_work_order) {
                    frm.remove_custom_button('Work Order', 'Create');

                    const paid_str = rounded_total > 0
                        ? `Current advance: ${advance_percent.toFixed(1)}% of order total.`
                        : '';
                    frm.dashboard.set_headline_alert(
                        `Work Order creation is disabled until advance paid is at least 45% of order total. ${paid_str}`,
                        'orange'
                    );
                }
            }
        }, 100);
    },

    // custom_material_availability: function(frm) {
    //     frm.reload_doc();
    // }
});
/**
 * DocType: Lead
 * Apply To: Form
 */

frappe.ui.form.on('Lead', {
    refresh(frm) {
        setTimeout(() => {
            // Hide Create dropdown buttons
            frm.remove_custom_button('Customer', 'Create');
            frm.remove_custom_button('Opportunity', 'Create');
            frm.remove_custom_button('Quotation', 'Create');
            frm.remove_custom_button('Prospect', 'Create');
            frm.remove_custom_button('Add to Prospect', 'Action');
            


            // Hide Connections section document links
            const doctypes_to_hide = ['Opportunity', 'Prospect'];
            doctypes_to_hide.forEach(dt => {
                $(`.document-link[data-doctype="${dt}"]`).hide();
            });

            // Hide 'New' buttons for Site Survey and Quotation in Connections
            $(`.document-link[data-doctype="Site Survey"] .btn-new`).hide();
            $(`.document-link[data-doctype="Quotation"] .btn-new`).hide();
        }, 500);
    },

    validate: function(frm) {
        if (frm.doc.mobile_no) {
            // Remove spaces
            let mobile = frm.doc.mobile_no.replace(/\s+/g, '');

            // Check if exactly 10 digits
            if (!/^\d{10}$/.test(mobile)) {
                frappe.throw(__('Mobile number must be exactly 10 digits.'));
            }

            // Update cleaned value
            frm.set_value('mobile_no', mobile);
        }
    }
});

/**
 * DocType: Employee Checkin
 * Apply To: Form
 */

frappe.ui.form.on('Employee Checkin', {
    validate: function(frm) {
        if (frm.doc.shift_start && frm.doc.time && frm.doc.custom_late_entry_grace_period) {

            // Convert all to JavaScript Date objects
            let shift_start = new Date(frm.doc.shift_start);
            let checkin_time = new Date(frm.doc.time);

            // Add grace period (in minutes) to shift_start
            let grace_milliseconds = frm.doc.custom_late_entry_grace_period * 60 * 1000;
            let allowed_time = new Date(shift_start.getTime() + grace_milliseconds);

            // Compare checkin time with allowed time
            if (checkin_time > allowed_time) {
                frm.set_value('custom_late_entry', 1);
            } else {
                frm.set_value('custom_late_entry', 0);
            }
        }
    }
});

/**
 * DocType: Task
 * Apply To: Form
 */

frappe.ui.form.on('Task', {
    refresh: function(frm) {
        // Show Start button only if task not started yet
        if (!frm.doc.actual_sd && frm.doc.docstatus < 2) {
            frm.add_custom_button(__('Start'), function() {
                let start_datetime = frappe.datetime.now_datetime();
                frm.set_value('actual_sd', start_datetime);
                frm.save();
            }).addClass('btn-primary');
        }
        
        // Show Complete button only if task started but not completed
        if (frm.doc.actual_sd && !frm.doc.actual_ed && frm.doc.docstatus < 2) {
            frm.add_custom_button(__('Complete'), function() {
                let end_datetime = frappe.datetime.now_datetime();
                let start_datetime = frm.doc.actual_sd;
                
                // IMPORTANT: Convert to moment objects for accurate calculation
                let start_moment = moment(start_datetime);
                let end_moment = moment(end_datetime);
                
                // Calculate duration in seconds
                let duration_seconds = end_moment.diff(start_moment, 'seconds');
                duration_seconds = Math.abs(duration_seconds); // Ensure positive
                
                console.log('Start DateTime:', start_datetime);
                console.log('End DateTime:', end_datetime);
                console.log('Duration (seconds):', duration_seconds);
                
                // Set values directly on the form
                frm.doc.actual_ed = end_datetime;
                frm.doc.total_time = duration_seconds;
                frm.doc.status = 'Completed';
                frm.doc.completed_on = frappe.datetime.nowdate();
                
                // Refresh the fields to show updated values
                frm.refresh_field('actual_ed');
                frm.refresh_field('total_time');
                frm.refresh_field('status');
                frm.refresh_field('completed_on');
                
                // Mark form as dirty
                frm.dirty();
                
                // Save the form
                frm.save().then(() => {
                    let hours = Math.floor(duration_seconds / 3600);
                    let minutes = Math.floor((duration_seconds % 3600) / 60);
                    let seconds = duration_seconds % 60;
                    
                    let time_msg = '';
                    if (hours > 0) {
                        time_msg = __('Task Completed! Total Time: {0}h {1}m {2}s', [hours, minutes, seconds]);
                    } else if (minutes > 0) {
                        time_msg = __('Task Completed! Total Time: {0}m {1}s', [minutes, seconds]);
                    } else {
                        time_msg = __('Task Completed! Total Time: {0}s', [seconds]);
                    }
                    
                    frappe.show_alert({
                        message: time_msg,
                        indicator: 'green'
                    });
                });
            }).addClass('btn-success');
        }
        
        // Show Reopen button only if task is completed
        if (frm.doc.actual_ed && frm.doc.status === 'Completed' && frm.doc.docstatus < 2) {
            frm.add_custom_button(__('Reopen'), function() {
                frappe.confirm(
                    __('Are you sure you want to reopen this task? This will clear all timing data and you can start fresh.'),
                    function() {
                        // Clear ALL timing fields for fresh start
                        frm.set_value('actual_sd', '');
                        frm.set_value('actual_ed', '');
                        frm.set_value('total_time', 0);
                        frm.set_value('status', 'Open');
                        frm.set_value('completed_on', '');
                        
                        // Save after setting values
                        frm.save().then(() => {
                            frappe.show_alert({
                                message: __('Task Reopened - Click Start to begin timing again'),
                                indicator: 'orange'
                            });
                        });
                    }
                );
            }).addClass('btn-warning');
        }
    }
});

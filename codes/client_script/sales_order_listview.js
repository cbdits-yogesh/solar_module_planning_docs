/**
 * DocType: Sales Order
 * Apply To: List
 */

frappe.listview_settings['Sales Order'] = {
    hide_name_column: true,
    hide_name_filter: true,

    add_fields: ['without_advance', 'without_pay_reason', 'docstatus'],

    onload: function(listview) {
        // Remove status column from header and rows
        listview.columns = listview.columns.filter(
            col => col.df && col.df.fieldname !== 'status'
        );
        listview.render_header(listview.columns);
    },

    refresh: function(listview) {
        // CSS fallback - hide status column
        $(listview.wrapper).find('.list-row-head [data-fieldname="status"]').hide();
        $(listview.wrapper).find('.list-row [data-fieldname="status"]').hide();
    },

    formatters: {

        // "% Advance Amt" column -> shows percentage only
        per_advance: function(value, df, doc) {
            // If Cancelled
            if (doc.docstatus === 2) {
                return `<span class="badge" style="background-color:#ff5858; color:white; padding:3px 8px; border-radius:4px;">Cancelled</span>`;
            }

            const val = flt(value, 2);

            let bg_color = '#ff5858';   // red   — less than 20
            if (val > 90) { bg_color = '#36ba6b'; }
            else if (val >= 46) { bg_color = '#5e64ff'; }
            else if (val >= 21) { bg_color = '#ff9800'; }

            return `<span class="badge" style="background-color:${bg_color}; color:white; padding:3px 8px; border-radius:4px;">${val}%</span>`;
        },

        // "Without Pay Reason" column -> shows only the reason, independently
        without_pay_reason: function(value, df, doc) {
            if (parseInt(doc.without_advance) === 1) {
                const reason = value || 'No Reason';
                return `<span class="badge" style="background-color:#6c757d; color:white; padding:3px 8px; border-radius:4px;">${reason}</span>`;
            }
            return '';
        },

        liaison_sync_status: function(value) {
            if (!value || value === 'Not Created' || value === 'Not Create') {
                return `<span class="badge" style="background-color:#ff5858; color:white; padding:3px 8px; border-radius:4px;">${value || 'Not Created'}</span>`;
            } else if (value === 'Completed') {
                return `<span class="badge" style="background-color:#36ba6b; color:white; padding:3px 8px; border-radius:4px;">${value}</span>`;
            } else {
                return `<span class="badge" style="background-color:#5e64ff; color:white; padding:3px 8px; border-radius:4px;">${value}</span>`;
            }
        },

        project_status: function(value) {
            if (!value || value === 'Not Created' || value === 'Not Create') {
                return `<span class="badge" style="background-color:#ff5858; color:white; padding:3px 8px; border-radius:4px;">${value || 'Not Created'}</span>`;
            } else if (value === 'Completed') {
                return `<span class="badge" style="background-color:#36ba6b; color:white; padding:3px 8px; border-radius:4px;">${value}</span>`;
            } else {
                return `<span class="badge" style="background-color:#5e64ff; color:white; padding:3px 8px; border-radius:4px;">${value}</span>`;
            }
        }
    }
};


// frappe.listview_settings['Sales Order'] = {
//     hide_name_column: true,
//     hide_name_filter: true,
    
//     add_fields: ['without_advance', 'without_pay_reason', 'docstatus'],

//     onload: function(listview) {
//         // Remove status column from header and rows
//         listview.columns = listview.columns.filter(
//             col => col.df && col.df.fieldname !== 'status'
//         );
//         listview.render_header(listview.columns);
//     },

//     refresh: function(listview) {
//         // CSS fallback - hide status column
//         $(listview.wrapper).find('.list-row-head [data-fieldname="status"]').hide();
//         $(listview.wrapper).find('.list-row [data-fieldname="status"]').hide();
//     },

//     formatters: {
        
//         per_advance: function(value, df, doc) {
//             // If Cancelled
//             if (doc.docstatus === 2) {
//                 return `<span class="badge" style="background-color:#ff5858; color:white; padding:3px 8px; border-radius:4px;">Cancelled</span>`;
//             }

//             // If without_advance is checked
//             if (parseInt(doc.without_advance) === 1) {
//                 const reason = doc.without_pay_reason || 'No Reason';
//                 return `<span class="badge" style="background-color:#6c757d; color:white; padding:3px 8px; border-radius:4px;">${reason}</span>`;
//             }

//             // Normal per_advance color logic
//             const val = flt(value, 2);

//             let bg_color = '#ff5858';   // red   — less than 20
//             if (val > 90) {bg_color = '#36ba6b';} 
//             else if (val >= 46) {bg_color = '#5e64ff';} 
//             else if (val >= 21) {bg_color = '#ff9800';}

//             return `<span class="badge" style="background-color:${bg_color}; color:white; padding:3px 8px; border-radius:4px;">${val}%</span>`;
//         },

//         liaison_sync_status: function(value) {
//             if (!value || value === 'Not Created' || value === 'Not Create' ) {
//                 return `<span class="badge" style="background-color:#ff5858; color:white; padding:3px 8px; border-radius:4px;">${value || 'Not Created'}</span>`;
//             } else if (value === 'Completed') {
//                 return `<span class="badge" style="background-color:#36ba6b; color:white; padding:3px 8px; border-radius:4px;">${value}</span>`;
//             } else {
//                 return `<span class="badge" style="background-color:#5e64ff; color:white; padding:3px 8px; border-radius:4px;">${value}</span>`;
//             }
//         },

//         project_status: function(value) {
//             if (!value || value === 'Not Created' || value === 'Not Create') {
//                 return `<span class="badge" style="background-color:#ff5858; color:white; padding:3px 8px; border-radius:4px;">${value || 'Not Created'}</span>`;
//             } else if (value === 'Completed') {
//                 return `<span class="badge" style="background-color:#36ba6b; color:white; padding:3px 8px; border-radius:4px;">${value}</span>`;
//             } else {
//                 return `<span class="badge" style="background-color:#5e64ff; color:white; padding:3px 8px; border-radius:4px;">${value}</span>`;
//             }
//         }
//     }
// };

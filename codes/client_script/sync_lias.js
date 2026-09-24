/**
 * DocType: Liaisoning And Synchronization
 * Apply To: Form
 */

frappe.ui.form.on('Liaisoning And Synchronization', {
    refresh: function(frm) {
        render_advance_status(frm);
    },
    sales_order: function(frm) {
        render_advance_status(frm);
    }
});

function render_advance_status(frm) {
    // Clear if no sales order linked
    if (!frm.doc.sales_order) {
        frm.fields_dict['advance_status_html'].$wrapper.html(`
            <div style="color: #999; font-size: 12px; padding: 6px 0;">
                No Sales Order linked.
            </div>
        `);
        return;
    }

    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Sales Order',
            filters: { name: frm.doc.sales_order },
            fieldname: ['rounded_total', 'advance_paid']
        },
        callback: function(r) {
            if (!r.message) return;

            let bill_amount   = r.message.rounded_total || 0;
            let advance_paid  = r.message.advance_paid  || 0;
            let percent       = bill_amount > 0 ? flt((advance_paid / bill_amount) * 100, 2) : 0;
            let capped_pct    = Math.min(percent, 100); // cap bar at 100%

            // Color logic
            let bar_color = percent < 30 ? '#e74c3c'   // red
                          : percent < 70 ? '#f39c12'   // orange
                          : '#27ae60';                  // green

            let html = `
                <div style="padding: 8px 0px 12px 0px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-size: 12px; color: #6c757d; font-weight: 500;">
                            💰 Advance Received
                        </span>
                        <span style="font-size: 13px; font-weight: 700; color: ${bar_color};">
                            ${percent}%
                        </span>
                    </div>

                    <!-- Progress Bar -->
                    <div style="background: #e9ecef; border-radius: 20px; height: 10px; width: 100%; overflow: hidden;">
                        <div style="
                            width: ${capped_pct}%;
                            height: 100%;
                            background: ${bar_color};
                            border-radius: 20px;
                            transition: width 0.5s ease;
                        "></div>
                    </div>

                    <!-- Amount Details -->
                    <div style="display: flex; justify-content: space-between; margin-top: 6px;">
                        <span style="font-size: 11px; color: #888;">
                            Advance: <strong style="color: #333;">
                                ${format_currency(advance_paid, frappe.defaults.get_default('currency'))}
                            </strong>
                        </span>
                        <span style="font-size: 11px; color: #888;">
                            Bill Amount: <strong style="color: #333;">
                                ${format_currency(bill_amount, frappe.defaults.get_default('currency'))}
                            </strong>
                        </span>
                    </div>
                </div>
            `;

            frm.fields_dict['advance_status_html'].$wrapper.html(html);
        }
    });
}
/**
 * DocType: Sales Order
 * Apply To: Form
 */

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.fields_dict.items && frm.fields_dict.items.grid) {
            frm.fields_dict.items.grid.df.cannot_add_rows = true;
            frm.fields_dict.items.grid.df.cannot_delete_rows = true;
            frm.fields_dict.items.grid.refresh();
        }

        if (frm.doc.docstatus === 1) {
            frm.add_custom_button('Manage Site Materials', function() {
                open_materials_dialog(frm);
            }, 'Site Materials');
        }
    }
});

function open_materials_dialog(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Solar BOM Template',
            filters: { is_active: 1 },
            fields: ['name', 'kilowatt'],
            order_by: 'kilowatt asc'
        },
        callback: function(r) {
            let templates = r.message || [];
            let template_options = [''].concat(templates.map(t => t.name));

            let existing = (frm.doc.items || [])
                .filter(row => row.is_site_material)
                .map(row => ({
                    item_code: row.item_code,
                    item_name: row.item_name,
                    qty: row.qty,
                    uom: row.uom,
                    description: row.description,
                    delivered_qty: row.delivered_qty || 0
                }));

            let dialog = new frappe.ui.Dialog({
                title: 'Manage Site Materials',
                size: 'extra-large',
                fields: [
                    {
                        fieldtype: 'Section Break',
                        label: 'Load from Template (Optional)'
                    },
                    {
                        fieldtype: 'Select',
                        fieldname: 'template',
                        label: 'Plant Template',
                        options: template_options.join('\n'),
                        description: 'Select a template to auto-populate materials below'
                    },
                    {
                        fieldtype: 'Button',
                        fieldname: 'load_btn',
                        label: 'Load Template Items'
                    },
                    { fieldtype: 'Column Break' },

                    {
                        fieldtype: 'Section Break',
                        label: 'Site Materials'
                    },
                    {
                        fieldtype: 'Table',
                        fieldname: 'materials',
                        label: 'Materials',
                        cannot_add_rows: false,
                        cannot_delete_rows: false,
                        in_place_edit: true,
                        data: existing,
                        fields: [
                            {
                                fieldtype: 'Link',
                                fieldname: 'item_code',
                                label: 'Item',
                                options: 'Item',
                                in_list_view: 1,
                                reqd: 1,
                                columns: 3,
                                change: function() {
                                    let row = this.doc;
                                    let item_code = this.get_value();
                                    if (!item_code) return;

                                    frappe.db.get_value(
                                        'Item',
                                        item_code,
                                        ['item_name', 'stock_uom', 'description'],
                                        function(val) {
                                            if (!val) return;

                                            frappe.model.set_value(row.doctype, row.name, 'item_name', val.item_name || '');
                                            frappe.model.set_value(row.doctype, row.name, 'uom', val.stock_uom || '');
                                            frappe.model.set_value(row.doctype, row.name, 'description', val.description || val.item_name || '');
                                        }
                                    );
                                }
                            },
                            {
                                fieldtype: 'Data',
                                fieldname: 'item_name',
                                label: 'Item Name',
                                in_list_view: 1,
                                read_only: 1,
                                columns: 3
                            },
                            {
                                fieldtype: 'Float',
                                fieldname: 'qty',
                                label: 'Planned Qty',
                                in_list_view: 1,
                                reqd: 1,
                                columns: 2
                            },
                            {
                                fieldtype: 'Link',
                                fieldname: 'uom',
                                label: 'UOM',
                                options: 'UOM',
                                in_list_view: 1,
                                columns: 2
                            },
                            {
                                fieldtype: 'Float',
                                fieldname: 'delivered_qty',
                                label: 'Dispatched',
                                in_list_view: 1,
                                read_only: 1,
                                columns: 2
                            },
                            {
                                fieldtype: 'Small Text',
                                fieldname: 'description',
                                label: 'Description'
                            }
                        ]
                    }
                ],
                primary_action_label: 'Save to Sales Order',
                primary_action: function(values) {
                    let mats = values.materials || [];
                    let seen = new Set();

                    for (let mat of mats) {
                        if (!mat.item_code) {
                            frappe.msgprint({
                                message: 'Item is required for all rows.',
                                indicator: 'red'
                            });
                            return;
                        }

                        if (seen.has(mat.item_code)) {
                            frappe.msgprint({
                                message: `Duplicate item not allowed: ${mat.item_code}`,
                                indicator: 'red'
                            });
                            return;
                        }
                        seen.add(mat.item_code);

                        if (!mat.qty || flt(mat.qty) <= 0) {
                            frappe.msgprint({
                                message: `${mat.item_code}: Qty must be greater than 0.`,
                                indicator: 'red'
                            });
                            return;
                        }

                        if (flt(mat.qty) < flt(mat.delivered_qty || 0)) {
                            frappe.msgprint({
                                message: `${mat.item_code}: Qty (${mat.qty}) cannot be less than already dispatched qty (${mat.delivered_qty}).`,
                                indicator: 'red'
                            });
                            return;
                        }
                    }

                    frappe.call({
                        method: 'manoj.custom_scripts.solar_bom.update_so_materials',
                        args: {
                            so_name: frm.doc.name,
                            materials: mats
                        },
                        freeze: true,
                        freeze_message: 'Saving site materials to Sales Order...',
                        callback: function(res) {
                            if (!res.exc) {
                                dialog.hide();
                                frm.reload_doc();
                                frappe.show_alert({
                                    message: `${mats.length} site material(s) saved successfully!`,
                                    indicator: 'green'
                                });
                            }
                        }
                    });
                }
            });

            dialog.fields_dict.load_btn.$input.on('click', function() {
                let tmpl = dialog.get_value('template');

                if (!tmpl) {
                    frappe.msgprint({
                        message: 'Please select a template first.',
                        indicator: 'orange'
                    });
                    return;
                }

                frappe.call({
                    method: 'manoj.custom_scripts.solar_bom.get_plant_template_items',
                    args: { template_name: tmpl },
                    callback: function(res) {
                        let items = res.message || [];
                        if (!items.length) {
                            frappe.msgprint('No items found in this template.');
                            return;
                        }

                        let grid = dialog.fields_dict.materials.grid;
                        dialog.fields_dict.materials.df.data = items.map(item => ({
                            item_code: item.item_code,
                            item_name: item.item_name,
                            qty: item.qty,
                            uom: item.uom,
                            description: item.description || '',
                            delivered_qty: 0
                        }));
                        grid.refresh();

                        frappe.show_alert({
                            message: `${items.length} items loaded from "${tmpl}".`,
                            indicator: 'green'
                        });
                    }
                });
            });

            dialog.show();
        }
    });
}
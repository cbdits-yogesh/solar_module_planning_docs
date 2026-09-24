'''
Reference Document Type: Supplier
DocType Event: After Insert
'''

if doc.add_line1 and doc.custom_state and doc.custom_pincode:
            address = frappe.get_doc({
                'doctype': 'Address',
                'address_title': doc.supplier_name,
                'address_type': 'Billing',
                'address_line1': doc.add_line1,
                'address_line2': doc.add_line2,
                'email_id': doc.email_id,
                'phone': doc.mobile_no,
                'gstin': doc.gstin,
                'city': doc.custom_city,
                'state': doc.custom_state,
                'country': doc.country,
                'pincode': doc.custom_pincode,
                'is_primary_address': 1,
                'links': [{
                    'link_doctype': 'Supplier',
                    'link_name': doc.name
                }]
            })
            address.insert(ignore_permissions=True)
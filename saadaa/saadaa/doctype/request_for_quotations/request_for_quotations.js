// Copyright (c) 2026, Ram and contributors
// For license information, please see license.txt

frappe.ui.form.on('Request For Quotations', {
    onload: function (frm) {
        // 1. Fetch Items Automatically from Material Requisition
        let source_mr_id = frm.doc.material_requisition;

        if (frm.is_new() && source_mr_id) {
            frappe.db.get_doc('Material Requisition', source_mr_id).then(mr_doc => {
                // Clear the default empty row in the items table
                frm.clear_table('items');

                if (mr_doc.items && mr_doc.items.length > 0) {
                    mr_doc.items.forEach(mr_item => {
                        let rfq_item = frm.add_child('items');

                        // Map Item Identity
                        rfq_item.item_code = mr_item.item_code;
                        rfq_item.uom = mr_item.uom;

                        // Extract quantity from MR safely
                        let source_qty = mr_item.quantity || mr_item.qty || 0;
                        rfq_item.qty = source_qty;
                        rfq_item.quantity = source_qty;

                        // Map Dates
                        rfq_item.required_date = mr_item.required_by || mr_doc.required_by;
                    });

                    // Render changes to the user interface item table
                    frm.refresh_field('items');
                }
            });
        }
    },

    refresh: function (frm) {
        // --- 2. GET ITEMS FROM MENU (Available when document is in Draft status) ---
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Material Request'), function () {
                erpnext.utils.map_current_doc({
                    method: "saadaa.saadaa.doctype.material_requisition.material_requisition.make_request_for_quotation",
                    source_doctype: "Material Requisition",
                    target_doc: frm
                });
            }, __('Get Items From'));
        }

        // --- 3. OPERATIONAL MENUS (Show as long as the document has been saved at least once) ---
        if (!frm.is_new()) {

            // FIX: Allow "Vendor Quotation" creation on saved documents (Draft or Submitted)
            frm.add_custom_button(__('Vendor Quotation'), function () {
                // Pre-load the target Doctype structure to receive mapped child rows cleanly
                // Inside your "Vendor Quotation" button logic in RFQ:
                frappe.model.with_doctype('Vendor Quotation', function () {
                    let target_doc = frappe.model.make_new_doc_and_get_name('Vendor Quotation');
                    let new_vq = locals['Vendor Quotation'][target_doc];

                    new_vq.request_for_quotation = frm.doc.name;
                    new_vq.company = frm.doc.company;
                    new_vq.material_requisition = frm.doc.material_requisition;

                    if (frm.doc.items && frm.doc.items.length > 0) {
                        frm.doc.items.forEach(rfq_item => {
                            // Use frappe.model.add_child and immediately populate 
                            // without triggering auto-refresh logic
                            let child_row = frappe.model.add_child(new_vq, 'Vendor Quotation Item', 'items');

                            // Set fields directly. Use the 'true' parameter in set_value if possible, 
                            // but for initial child creation, simple assignment is safer.
                            frappe.model.set_value(child_row.doctype, child_row.name, 'item_code', rfq_item.item_code);
                            frappe.model.set_value(child_row.doctype, child_row.name, 'uom', rfq_item.uom);
                            frappe.model.set_value(child_row.doctype, child_row.name, 'qty', rfq_item.qty || rfq_item.quantity);
                        });
                    }

                    // Trigger a refresh only once at the very end
                    cur_frm.refresh_fields('items');
                    frappe.set_route('Form', 'Vendor Quotation', target_doc);
                });
            }, __('Create'));

            // Menus restricted to SUBMITTED state (docstatus === 1)
            if (frm.doc.docstatus === 1) {
                // TOOLS MENU: Add "Send Emails to Suppliers" 
                frm.add_custom_button(__('Send Emails to Suppliers'), function () {
                    frappe.confirm(__('Are you sure you want to send emails to all listed suppliers?'), function () {
                        frappe.call({
                            method: "saadaa.saadaa.doctype.request_for_quotations.request_for_quotations.send_supplier_emails",
                            args: { rfq_name: frm.doc.name },
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.msgprint(__('Emails queued successfully.'));
                                }
                            }
                        });
                    });
                }, __('Tools'));

                // TOOLS MENU: Add "Download PDF"
                frm.add_custom_button(__('Download PDF'), function () {
                    const w = window.open(frappe.urllib.get_full_url(`/api/method/frappe.utils.print_format.download_pdf?doctype=Request%20For%20Quotations&name=${frm.doc.name}&format=Standard`));
                    if (!w) {
                        frappe.msgprint(__('Please allow pop-ups for this site'));
                    }
                }, __('Tools'));

                // VIEW MENU: Add "Supplier Quotation Comparison"
                frm.add_custom_button(__('Supplier Quotation Comparison'), function () {
                    frappe.set_route('query-report', 'Supplier Quotation Comparison', {
                        'request_for_quotation': frm.doc.name
                    });
                }, __('View'));
            }
        }
    }
});
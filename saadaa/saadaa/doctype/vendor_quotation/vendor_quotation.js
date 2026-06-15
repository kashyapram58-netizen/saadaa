// Copyright (c) 2026, Ram and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vendor Quotation', {
	refresh: function (frm) {
		// 1. Fallback check: If the field is empty, check if it was passed via route options context
		if (!frm.doc.request_for_quotation && frappe.route_options && frappe.route_options.request_for_quotation) {
			frm.set_value('request_for_quotation', frappe.route_options.request_for_quotation);
		}

		let source_rfq_id = frm.doc.request_for_quotation;

		// 2. Run mapping only for a brand-new document that has a valid source RFQ
		if (frm.is_new() && source_rfq_id) {
			frappe.db.get_doc('Request For Quotations', source_rfq_id).then(rfq_doc => {

				// Map the Material Requisition tracking link if it exists
				if (rfq_doc.material_requisition && !frm.doc.material_requisition) {
					frm.set_value('material_requisition', rfq_doc.material_requisition);
				}

				// Map company details
				if (rfq_doc.company) {
					frm.set_value('company', rfq_doc.company);
				}

				// Clear the default single empty line seen in image_845382.jpg
				frm.clear_table('items');

				// Map items, quantities, and UOMs directly
				if (rfq_doc.items && rfq_doc.items.length > 0) {
					rfq_doc.items.forEach(rfq_item => {
						let row = frm.add_child('items');

						row.item_code = rfq_item.item_code;
						row.uom = rfq_item.uom;

						// Ensure compatibility with both fieldname variations (qty or quantity)
						let target_qty = rfq_item.qty || rfq_item.quantity || 0;
						row.qty = target_qty;
						row.quantity = target_qty;
					});

					// Refresh table display UI grid view
					frm.refresh_field('items');
					frappe.show_alert({ message: __('Items pulled from RFQ successfully'), indicator: 'green' });
				}
			});
		}
	}
});
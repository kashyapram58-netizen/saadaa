// apps/saadaa/saadaa/saadaa/doctype/vendor_quotation/vendor_quotation.js

frappe.ui.form.on('Vendor Quotation', {
	refresh: function (frm) {
		// --- YOUR EXISTING RFQ MAPPING LOGIC ---
		if (!frm.is_new() && !frm.doc.__already_mapped) {
			let source_rfq_id = frm.doc.request_for_quotation;
			if (source_rfq_id) {
				frm.doc.__already_mapped = true;
				frappe.db.get_doc('Request For Quotations', source_rfq_id).then(rfq_doc => {
					frm.set_value('material_requisition', rfq_doc.material_requisition);
					frm.set_value('company', rfq_doc.company);
					frm.clear_table('items');
					if (rfq_doc.items && rfq_doc.items.length > 0) {
						rfq_doc.items.forEach(rfq_item => {
							let row = frm.add_child('items');
							row.item_code = rfq_item.item_code;
							row.uom = rfq_item.uom;
							row.qty = rfq_item.qty || rfq_item.quantity || 0;
						});
						frm.refresh_field('items');
						frappe.show_alert({ message: __('Items pulled from RFQ'), indicator: 'green' });
					}
				});
			}
		}

		// --- NEW: PURCHASE ORDER CREATION BUTTON LOGIC ---
		// Ensure you use the field name you actually defined (e.g., vq_workflow_state)
		if (frm.doc.workflow_state === 'Audited') {
			frm.add_custom_button(__('Create Purchase Order'), function () {
				frappe.model.open_mapped_doc({
					method: "saadaa.saadaa.doctype.vendor_quotation.vendor_quotation.make_purchase_order",
					frm: frm
				});
			}, __('Create'));
		}
	}
});

// Auto-calculation for child table items
frappe.ui.form.on('Vendor Quotation Item', {
	qty: function (frm, cdt, cdn) {
		calculate_amount(cdt, cdn);
	},
	rate: function (frm, cdt, cdn) {
		calculate_amount(cdt, cdn);
	}
});

function calculate_amount(cdt, cdn) {
	let row = locals[cdt][cdn];
	let amount = flt(row.qty) * flt(row.rate);
	if (row.amount !== amount) {
		frappe.model.set_value(cdt, cdn, 'amount', amount);
	}
}
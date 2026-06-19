frappe.listview_settings['Purchase Orders'] = {
	onload: function (listview) {
		listview.page.add_field({
			fieldname: "status",
			fieldtype: "Select",
			label: __("Status"),
			options: "\nDraft\nPending\nAudited\nSubmitted\nApproved\nRejected\nCancelled",
			onchange: function () {
				listview.filter_area.add([["Purchase Orders", "status", "=", this.value]]);
				listview.run();
			}
		});
	}
};
frappe.ui.form.on('Purchase Order', {
	refresh: function (frm) {
		// If your child table has data, pull the first requisition ID
		if (frm.doc.linked_purchase_orders && frm.doc.linked_purchase_orders.length > 0) {
			// Logic to set your Link field
			frm.set_value('material_requisition', frm.doc.linked_purchase_orders[0].parent);
		}
	}
});
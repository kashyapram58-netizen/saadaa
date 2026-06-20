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
		// 1. Only show our custom button if the document is Submitted
		if (frm.doc.docstatus === 1) {

			// 2. Hide the default Cancel button
			frm.page.btn_cancel.hide();

			// 3. Add our own button that triggers the backend-safe cancellation
			frm.add_custom_button(__('Cancel PO'), function () {
				frappe.confirm(__('Are you sure you want to cancel this Purchase Order?'), () => {
					// This calls the server directly to cancel without UI interference
					frm.call({
						method: "frappe.client.cancel",
						args: {
							doctype: frm.doc.doctype,
							name: frm.doc.name
						},
						callback: function (r) {
							if (!r.exc) {
								frm.reload_doc();
								frappe.msgprint(__('Purchase Order Cancelled Successfully'));
							}
						}
					});
				});
			}, __('Actions'));
		}
	}
});
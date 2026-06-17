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
// Copyright (c) 2026, Ram and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Requisition', {
    refresh: function (frm) {
        if (!frm.is_new() && !frm.is_dirty()) {

            // Add Create menu
            frm.add_custom_button(__('Request for Quotations'), function () {
                // frappe.new_doc opens a blank form with pre-filled fields
                frappe.new_doc('Request For Quotations', {
                    'material_requisition': frm.doc.name
                });
            }, __('Create'));

            frm.add_custom_button(__('Purchase Order'), function () {
                frappe.new_doc('Purchase Orders', {
                    'material_requisition': frm.doc.name
                });
            }, __('Create'));
        }
    }
});
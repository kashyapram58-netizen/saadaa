// Copyright (c) 2026, Ram and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Requisition', {
    refresh: function (frm) {
        if (!frm.is_new() && !frm.is_dirty()) {
            // Add Create menu
            frm.add_custom_button(__('Request for Quotations'), function () {
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
    },

    // --- NEW: Date Automation Requirements ---
    onload: function (frm) {
        // Auto-set Transaction Date on new forms
        if (frm.is_new()) {
            frm.set_value('transaction_date', frappe.datetime.get_today());
        }
    },

    required_by: function (frm) {
        // Auto-populate 'required_by_date' in the items table when header changes
        if (frm.doc.required_by) {
            frm.doc.items.forEach(function (row) {
                frappe.model.set_value(row.doctype, row.name, 'required_by_date', frm.doc.required_by);
            });
            frm.refresh_field('items');
        }
    }
});

// Auto-populate when adding a new row to the table
frappe.ui.form.on('Material Requisition Item', {
    form_render: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (frm.doc.required_by && !row.required_by_date) {
            frappe.model.set_value(cdt, cdn, 'required_by_date', frm.doc.required_by);
        }
    }
});
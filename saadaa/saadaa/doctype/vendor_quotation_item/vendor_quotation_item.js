frappe.ui.form.on('Vendor Quotation Item', {
    rate: function (frm, cdt, cdn) {
        calculate_amount(cdt, cdn);
    },
    quantity: function (frm, cdt, cdn) {
        calculate_amount(cdt, cdn);
    }
});

function calculate_amount(cdt, cdn) {
    let row = locals[cdt][cdn];
    // Ensure the fieldname matches exactly what is in your DocType
    if (row.rate && row.quantity) {
        frappe.model.set_value(cdt, cdn, 'amount', row.quantity * row.rate);
    }
}
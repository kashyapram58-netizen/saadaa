# Copyright (c) 2026, Ram and contributors
# For license information, please see license.txt

import frappe
from frappe import _  
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from frappe.model.mapper import get_mapped_doc


class RequestForQuotations(Document):
    pass


@frappe.whitelist()
def send_supplier_emails(rfq_name):
    # Fetch the custom Request for Quotations document
    rfq = frappe.get_doc("Request For Quotations", rfq_name)
    
    # Check if the child table contains any rows
    if not hasattr(rfq, 'suppliers') or not rfq.suppliers:
        frappe.throw(_("No suppliers selected in the table list."))
        
    for supplier in rfq.suppliers:
        # Check if the supplier email field has a value
        if getattr(supplier, 'email_id', None):
            try:
                # Generate the standard transaction PDF attachment
                attachments = [{
                    "fname": f"{rfq.name}.pdf",
                    "fcontent": get_pdf(frappe.get_print("Request For Quotations", rfq.name, "Standard"))
                }]
                
                # Send email communication via Frappe background queue
                frappe.sendmail(
                    recipients=supplier.email_id,
                    subject=f"Request For Quotation: {rfq.name}",
                    message=f"Dear {getattr(supplier, 'supplier_name', supplier.supplier)},\n\nPlease find attached our request for quotation. We look forward to your response.",
                    attachments=attachments,
                    reference_doctype="Request For Quotations",
                    reference_name=rfq.name
                )
            except Exception as e:
                frappe.log_error(title=_("RFQ Email Send Failure"), message=frappe.get_traceback())
                frappe.throw(_("Failed to send email to {0}. Check Error Logs for details.").format(supplier.supplier))


@frappe.whitelist()
def make_vendor_quotation(source_name):
    # This officially maps child tables from the RFQ to Vendor Quotation cleanly
    doclist = get_mapped_doc("Request For Quotations", source_name, {
        "Request For Quotations": {
            "doctype": "Vendor Quotation",
            "field_map": {
                "name": "request_for_quotation",
                "material_requisition": "material_requisition",
                "company": "company"
            }
        },
        "Request For Quotations Item": {
            "doctype": "Vendor Quotation Item", # <-- Replace with your exact Vendor Quotation Child Table DocType name if different
            "field_map": {
                "item_code": "item_code",
                "uom": "uom",
                "qty": "qty"
            }
        }
    })
    return doclist                
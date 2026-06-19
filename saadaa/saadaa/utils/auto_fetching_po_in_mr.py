import frappe

# --- Main Logic ---
def sync_mr_child_table(doc, method, child_table_field, link_field_name):
    frappe.log_error(f"DEBUG: Triggered sync for {doc.doctype} : {doc.name}", "DEBUG_SYNC")
    # Debug: Check if MR is present
    if not doc.get("material_requisition"):
        return

    try:
        mr = frappe.get_doc("Material Requisition", doc.material_requisition)
        
        # Check if already linked
        is_linked = any(row.get(link_field_name) == doc.name for row in mr.get(child_table_field))
        
        if not is_linked:
            # Append new row
            row = mr.append(child_table_field, {})
            row.set(link_field_name, doc.name)
            row.parentfield = child_table_field
            mr.save(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Sync Error: {str(e)}", "MR Sync")

def remove_mr_child_row(doc, method, child_table_field, link_field_name):
    if not doc.get("material_requisition"):
        return
        
    try:
        mr = frappe.get_doc("Material Requisition", doc.material_requisition)
        # Filter out the row
        new_rows = [d for d in mr.get(child_table_field) if d.get(link_field_name) != doc.name]
        
        if len(new_rows) != len(mr.get(child_table_field)):
            mr.set(child_table_field, new_rows)
            mr.save(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Unlink Error: {str(e)}", "MR Unlink")

# --- Wrapper Functions ---
# IMPORTANT: 'linked_rfq_section', 'linked_vendor_quotation', 'linked_purchase_orders'
# MUST match the exact Fieldname of the table in your MR DocType.

def link_rfq_to_mr(doc, method): 
    sync_mr_child_table(doc, method, "linked_rfq_section", "request_for_quotations")
def unlink_rfq_from_mr(doc, method): 
    remove_mr_child_row(doc, method, "linked_rfq_section", "request_for_quotations")

def link_vq_to_mr(doc, method): 
    sync_mr_child_table(doc, method, "linked_vendor_quotation", "vendor_quotation")
def unlink_vq_from_mr(doc, method): 
    remove_mr_child_row(doc, method, "linked_vendor_quotation", "vendor_quotation")

def link_po_to_mr(doc, method): 
    sync_mr_child_table(doc, method, "linked_purchase_orders", "purchase_order")
def unlink_po_from_mr(doc, method): 
    remove_mr_child_row(doc, method, "linked_purchase_orders", "purchase_order")
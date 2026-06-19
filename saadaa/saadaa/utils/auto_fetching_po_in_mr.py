import frappe

def link_po_to_mr(doc, method):
    frappe.msgprint("Link function running")
    if doc.material_requisition:  # Ensure this field name matches your PO
        mr = frappe.get_doc("Material Requisition", doc.material_requisition)
        
        # Check if already linked to prevent duplicate rows
        if not any(row.purchase_order == doc.name for row in mr.linked_purchase_orders):
            mr.append("linked_purchase_orders", {
                "purchase_order": doc.name,
                # "posting_date": doc.posting_date,
                # "supplier": doc.supplier,
                # "total_amount": doc.grand_total,
                # "status": doc.status
            })
            mr.save(ignore_permissions=True)

def unlink_po_from_mr(doc, method):
    if doc.material_requisition:
        mr = frappe.get_doc("Material Requisition", doc.material_requisition)
        # Remove the row where purchase_order matches this doc
        mr.set("linked_purchase_orders", [d for d in mr.linked_purchase_orders if d.purchase_order != doc.name])
        mr.save(ignore_permissions=True)
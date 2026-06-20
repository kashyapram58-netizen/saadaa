# In your saadaa/utils.py or similar file
import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_vendor_quotation(source_name, target_doc=None):
    doc = get_mapped_doc("Request For Quotations", source_name, {
        "Request for Quotation": {
            "doctype": "Vendor Quotation",
            "field_map": {
                "name": "request_for_quotations", # Mapping RFQ name to VQ field
                "material_requisition": "material_requisition"
            }
        }
    }, target_doc)
    return doc


def run_all_syncs(doc, method):

    if method in ["on_cancel", "on_trash"]:
        delink_downstream(doc, method)
    # This ensures both your MR and RFQ chain logic run whenever any of these docs are saved
    sync_mr_chain(doc, method)
    sync_rfq_chain(doc, method)
    sync_vq_chain(doc, method)

def sync_mr_chain(doc, method):
    """
    Generic function to sync links from PO, RFQ, and VQ back to 
    the Material Requisition (MR).
    """
    # Ensure the document has a material_requisition field
    if not doc.get("material_requisition"):
        return

    # Check if the document is being active (submit) or removed (cancel/trash)
    is_active = method not in ["on_cancel", "on_trash"]
    
    # Map the current Doctype to the corresponding field in the Material Requisition
    # Ensure these fieldnames match your MR DocType exactly
    sync_map = {
        "Purchase Orders": "purchase_orders",
        "Request For Quotations": "request_for_quotations",
        "Vendor Quotation": "vendor_quotation"
    }

    target_field = sync_map.get(doc.doctype)

    if target_field:
        # If active, set the name, otherwise set to None to clear the link
        value = doc.name if is_active else None
        update_mr_field(doc.material_requisition, target_field, value)

def update_mr_field(mr_name, fieldname, value):
    if mr_name:
        frappe.db.set_value("Material Requisition", mr_name, fieldname, value)
        frappe.db.commit()
    else:
        # This will show up in your Error Log if a doc is submitted without an MR link
        frappe.log_error(f"Sync failed: No MR linked to {fieldname}", "P2P Sync Debug")


def sync_rfq_chain(doc, method):
    """
    Generic function to sync links from PO, RFQ, and VQ back to 
    the Request For Quotation(RFQ).
    """
    # Ensure the document has a material_requisition field
    if not doc.get("request_for_quotations"):
        return

    # Check if the document is being active (submit) or removed (cancel/trash)
    is_active = method not in ["on_cancel", "on_trash"]

    # Map the current Doctype to the corsresponding field in the Material Requisition
    # Ensure these fieldnames match your MR DocType exactly
    sync_map = {
        "Purchase Orders": "purchase_orders",
        "Vendor Quotation": "vendor_quotation"
    }

    target_field = sync_map.get(doc.doctype)

    if target_field:
        # If active, set the name, otherwise set to None to clear the link
        value = doc.name if is_active else None
        update_rfq_field(doc.request_for_quotations, target_field, value)

def update_rfq_field(mr_name, fieldname, value):
    if mr_name:
        frappe.db.set_value("Request For Quotations", mr_name, fieldname, value)
        frappe.db.commit()
    else:
        # This will show up in your Error Log if a doc is submitted without an MR link
        frappe.log_error(f"Sync failed: No MR linked to {fieldname}", "P2P Sync Debug")


def sync_vq_chain(doc, method):
    """
    Generic function to sync links from PO, RFQ, and VQ back to 
    the Request For Quotation(RFQ).
    """
    # Ensure the document has a material_requisition field
    if not doc.get("vendor_quotation"):
        return

    # Check if the document is being active (submit) or removed (cancel/trash)
    is_active = method not in ["on_cancel", "on_trash"]
   
    # Map the current Doctype to the corresponding field in the Material Requisition
    # Ensure these fieldnames match your MR DocType exactly
    sync_map = {
        "Purchase Orders": "purchase_orders",
    }

    target_field = sync_map.get(doc.doctype)

    if target_field:
        # If active, set the name, otherwise set to None to clear the link
        value = doc.name if is_active else None
        update_vq_field(doc.vendor_quotation, target_field, value)

def update_vq_field(mr_name, fieldname, value):
    if mr_name:
        frappe.db.set_value("Vendor Quotation", mr_name, fieldname, value)
        frappe.db.commit()
    else:
        # This will show up in your Error Log if a doc is submitted without an MR link
        frappe.log_error(f"Sync failed: No MR linked to {fieldname}", "P2P Sync Debug")

def delink_downstream(doc, method):
    """
    Clears references in child documents when a parent is cancelled.
    This prevents LinkExistsError because the children no longer 'link' to the parent.
    """
    if method not in ["on_cancel", "on_trash"]:
        return

    # Define the hierarchy: { ParentDocType: { ChildDocType: FieldNameInChild } }
    delink_map = {
        "Material Requisition": {
            "Request For Quotations": "material_requisition",
            "Vendor Quotation": "material_requisition",
            "Purchase Orders": "material_requisition"
        },
        "Request For Quotation": {
            "Vendor Quotation": "request_for_quotations",
            "Purchase Order": "request_for_quotation"
        },
        "Vendor Quotation": {
            "Purchase Orders": "vendor_quotation"
        }
    }

    children = delink_map.get(doc.doctype, {})
    
    for child_dt, child_field in children.items():
        # Find all active (submitted) children pointing to this doc
        child_docs = frappe.get_all(child_dt, filters={
            child_field: doc.name,
            "docstatus": 1
        })
        
        for child in child_docs:
            # Clear the link field directly in the database
            frappe.db.set_value(child_dt, child.name, child_field, None, update_modified=False)
            frappe.db.commit()


def before_cancel_override(doc, method):
    """
    1. Check for 'Hard Blockers' (PI/PR). If found, block everything.
    2. If no Hard Blockers, force-unlink any 'Soft Blockers' (PO/RFQ/VQ) 
       to allow the parent to cancel without triggering the LinkExistsError.
    """
    # 1. Look for documents that MUST block cancellation
    hard_blockers = ["Purchase Invoice", "Purchase Recipt"]
    
    # Check all linked docs
    from frappe.desk.form.linked_with import get_linked_docs
    linked_data = get_linked_docs(doc.doctype, doc.name)
    
    for doctype, docs in linked_data.items():
        if doctype in hard_blockers and docs:
            frappe.throw(f"Cannot cancel {doc.doctype}: {doctype} {docs[0]['name']} is linked.")

    # 2. If we reach here, no hard blockers exist. 
    # Manually 'sever' the link to the PO/RFQ/VQ so the system doesn't try to cancel them.
    # This prevents the LinkExistsError.
    
    # Mapping of parent fields to child doctypes
    # When cancelling an MR, we must clear the field 'material_requisition' in the PO
    link_fields = {
        "Material Requisition": [("Purchase Orders", "material_requisition"), ("Request For Quotations", "material_requisition")],
        "Request For Quotations": [("Purchase Orders", "request_for_quotations"), ("Vendor Quotation", "request_for_quotations")],
        "Vendor Quotation": [("Purchase Orders", "vendor_quotation")]
    }
    
    if doc.doctype in link_fields:
        for child_dt, fieldname in link_fields[doc.doctype]:
            # Update all child docs to remove the link to this parent
            frappe.db.sql(f"""UPDATE `tab{child_dt}` SET `{fieldname}` = NULL 
                              WHERE `{fieldname}` = %s""", (doc.name,))
            
    # 3. Tell Frappe to ignore links because we just manually fixed them
    doc.flags.ignore_links = True

@frappe.whitelist()
def get_custom_linked_docs(doctype, docname):
    """
    Override or filter the linked documents list.
    If you don't want the dialog to appear for these specific links,
    this function returns an empty dictionary.
    """
    # Simply return an empty dict to make Frappe think nothing is linked
    return {}
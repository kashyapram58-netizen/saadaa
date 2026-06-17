import frappe
from frappe.model.document import Document

class PurchaseOrders(Document):
	pass
def get_dashboard_info(doc):
    return {
        "fieldname": "purchase_orders",
        "transactions": [
            {"label": "Reference", "items": ["Vendor Quotation"]}
        ]
    }
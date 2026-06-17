# apps/saadaa/saadaa/saadaa/doctype/vendor_quotation/vendor_quotation.py

import frappe
from frappe.utils import flt
from erpnext.controllers.buying_controller import BuyingController
from frappe.model.mapper import get_mapped_doc

class VendorQuotation(BuyingController):
    def validate(self):
        for item in self.items:
            if item.rate > 0:
                item.flags.ignore_pricing_rule = True 
        
        self.calculate_totals_manually()
        super().validate()
        
    def calculate_totals_manually(self):
        self.total = 0.0
        self.base_total = 0.0
        conversion_rate = flt(self.conversion_rate) or 1.0
        
        for item in self.items:
            item.amount = flt(item.qty) * flt(item.rate)
            item.base_amount = item.amount * conversion_rate
            self.total += item.amount
            self.base_total += item.base_amount
        
        self.grand_total = self.total
        self.base_grand_total = self.base_total
        self.rounded_total = self.total
        self.base_rounded_total = self.base_total
        
    def calculate_taxes_and_totals(self):
        self.calculate_totals_manually()

    def before_save(self):
        self.calculate_totals_manually()

# --- ADDED WHITELISTED FUNCTION FOR PURCHASE ORDER MAPPING ---

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
    doclist = get_mapped_doc(
        "Vendor Quotation",
        source_name,
        {
            "Vendor Quotation": {
                "doctype": "Purchase Orders",
                "field_map": {
                    "name": "vendor_quotation",
                    "supplier": "supplier",
                    "company": "company"
                }
            },
            "Vendor Quotation Item": {
                "doctype": "Purchase Order Items",
                "field_map": {
                    "item_code": "item_code",
                    "uom": "uom",
                    "qty": "qty",
                    "rate": "rate",
                    "amount": "amount"
                }
            }
        },
        target_doc
    )
    return doclist

def get_dashboard_info(doc):
    return {
        "fieldname": "purchase_orders",
        "transactions": [
            {"label": "Reference", "items": ["Vendor Quotation"]}
        ]
    }
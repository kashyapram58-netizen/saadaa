# apps/saadaa/saadaa/saadaa/doctype/vendor_quotation/vendor_quotation.py

import frappe
from frappe.utils import flt
from erpnext.controllers.buying_controller import BuyingController

class VendorQuotation(BuyingController):
    def validate(self):
        # 1. Protect manual rates from being wiped
        for item in self.items:
            if item.rate > 0:
                item.flags.ignore_pricing_rule = True 
        
        # 2. Calculate totals manually
        self.calculate_totals_manually()
        
        # 3. Proceed with standard validation
        super().validate()
        
    def calculate_totals_manually(self):
        # Initialize
        self.total = 0.0
        self.base_total = 0.0
        conversion_rate = flt(self.conversion_rate) or 1.0
        
        for item in self.items:
            # Sync rates and amounts
            item.amount = flt(item.qty) * flt(item.rate)
            item.base_amount = item.amount * conversion_rate
            
            self.total += item.amount
            self.base_total += item.base_amount
        
        self.grand_total = self.total
        self.base_grand_total = self.base_total
        self.rounded_total = self.total
        self.base_rounded_total = self.base_total
        
    def calculate_taxes_and_totals(self):
        # Override to prevent the buggy 'round_floats_in' 
        self.calculate_totals_manually()

    def before_save(self):
        # Ensure totals are correct before saving
        self.calculate_totals_manually()
        # Removed super().before_save() as it does not exist in the controller hierarchy
    
def get_dashboard_info(doc):
    # This explicit hook ensures the dashboard registers the link
    return {
        "fieldname": "request_for_quotations",
        "transactions": [
            {"label": "Reference", "items": ["Vendor Quotation"]}
        ]
    }    
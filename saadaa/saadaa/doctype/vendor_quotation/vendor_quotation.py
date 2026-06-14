# Copyright (c) 2026, Ram and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.model.document import Document
from erpnext.controllers.buying_controller import BuyingController

class VendorQuotation(BuyingController):
    def before_validate(self):
        # Add custom logic here
        pass

    def validate(self):
        super().validate()
        
        if not self.status:
            self.status = "Draft"
            
    def on_submit(self):
        self.db_set("status", "Submitted")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

# Note: I have removed the auto-generated types block and 
# hardcoded SQL methods from the original file to prevent
# ImportError and Database Table errors.
import frappe
frappe.init(site="saadaa.") # Ensure this matches your site name exactly
frappe.connect()

doc = frappe.get_doc({
    "doctype": "Workspace",
    "label": "Saadaa",
    "title": "Saadaa",
    "name": "Saadaa",
    "module": "Saadaa",
    "is_standard": 0,
    "public": 1
})

doc.insert(ignore_permissions=True)
frappe.db.commit()
print("Workspace created successfully!")

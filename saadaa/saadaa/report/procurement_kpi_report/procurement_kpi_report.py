import frappe
from frappe import _
from frappe.query_builder.functions import Count
from frappe.query_builder import CustomFunction
from frappe.query_builder.functions import Min
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    # Summary cards calculation
    summary = [
        {"label": _("Total MRs"), "value": len(data), "datatype": "Int"},
        {"label": _("Avg MR to PO TAT"), "value": get_avg(data, "mr_po_tat"), "datatype": "Float", "indicator": "blue"},
    ]

    return columns, data, None, chart, summary

def get_avg(data, field):
    values = [d.get(field) for d in data if d.get(field) is not None]
    return round(sum(values) / len(values), 2) if values else 0

def get_columns():
    return [
        {"label": _("MR"), "fieldname": "mr_name", "fieldtype": "Link", "options": "Material Requisition", "width": 300},
        {"label": _("Creation Date"), "fieldname": "mr_date", "fieldtype": "Date", "width": 170},
        {"label": _("RFQ Count"), "fieldname": "rfq_count", "fieldtype": "Int", "width": 300},
        # {"label": _("MR to RFQ TAT (Days)"), "fieldname": "mr_rfq_tat", "fieldtype": "Float", "width": 300},
        # {"label": _("MR to PO TAT (Days)"), "fieldname": "mr_po_tat", "fieldtype": "Float", "width": 300},
        {"label": _("MR to RFQ TAT (Minutes)"), "fieldname": "mr_rfq_tat", "fieldtype": "Float", "width": 300},
        {"label": _("MR to PO TAT (Minutes)"), "fieldname": "mr_po_tat", "fieldtype": "Float", "width": 300},
    ]

def get_data(filters):
    # DateDiff = CustomFunction("DATEDIFF", ["end_date", "start_date"])
    from pypika.terms import LiteralValue

    DateDiffMinutes = CustomFunction("TIMESTAMPDIFF", ["unit", "start_date", "end_date"])
    mr = frappe.qb.DocType("Material Requisition")
    rfq = frappe.qb.DocType("Request For Quotations")
    po = frappe.qb.DocType("Purchase Orders")
    
    # Use Count() function from frappe.query_builder.functions
    query = (
        frappe.qb.from_(mr)
        .left_join(rfq).on(rfq.material_requisition == mr.name)
        .left_join(po).on(po.material_requisition == mr.name)
        .select(
            mr.name.as_("mr_name"),
            mr.creation.as_("mr_date"),
            Count(rfq.name).as_("rfq_count"),
            # DateDiff(rfq.creation, mr.creation).as_("mr_rfq_tat"),
            # DateDiff(po.creation, mr.creation).as_("mr_po_tat")
           Min(DateDiffMinutes(LiteralValue("MINUTE"), mr.creation, rfq.creation)).as_("mr_rfq_tat"),
           Min(DateDiffMinutes(LiteralValue("MINUTE"), mr.creation, po.creation)).as_("mr_po_tat")
        )
        .groupby(mr.name)
    )
    return query.run(as_dict=True)

def get_chart_data(data):
    return {
        "data": {
            "labels": [d.get("mr_name") for d in data],
            "datasets": [
                {"name": "MR to RFQ", "values": [d.get("mr_rfq_tat") or 0 for d in data]},
                {"name": "MR to PO", "values": [d.get("mr_po_tat") or 0 for d in data]}
            ]
        },
        "type": "bar",
        "colors": ["#ffa07a", "#20b2aa"]
    }
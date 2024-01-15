from emdad import model, api, fields

class EmdadSalesOrder(models.Model):
    _name = "emdad.sales"

    name = fields.Char(string="Sales ID")
    
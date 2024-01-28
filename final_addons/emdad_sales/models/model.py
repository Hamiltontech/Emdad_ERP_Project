from emdad import models, fields, api

class EmdadSalesOrder(models.Model):
    _name = "emdad.sales"

    name = fields.Char(string="Sales ID")
    
from emdad import fields, api, models

class EmdadCustomers(models.Model):
    _name="emdad.customers"

    name = fields.Char(string="Subscription ID")
    server_ip = fields.Char(String="Server IP")
    port_number = fields.Char(string="Port Number")
    company = fields.Char(string="Company")
    payment = fields.Selection([('paid','Paid'), ('not','Not Paid')])
    server_status = fields.Selection([('down','Down'), ('up','Alive')])
from emdad import api, models, fields
from datetime import datetime

class EmdadFleet(models.Model):
    _name = "emdad.fleet"

    name = fields.Char(string="Plate Number")
    model = fields.Many2one("emdad.fleet.model")
    year = fields.Integer(string="Year Made")
    related_location = fields.Many2one("emdad.warehouse.location", string="Related Container")
    engine_hp = fields.Float(string="Engine Horse Power")
    insurance_plan = fields.Many2one("emdad.fleet.insurance", string="Insurance Contract")
    status = fields.Selection([('in_progress', 'In Progress'), ('expired', 'Expired')], string="Contract Status", related="insurance_plan.status")
    container_quantity = fields.Float(string="Current Quantity", related="related_location.quantity")
    container_status = fields.Selection([('in_use','In Use'), ('not_used','Not Used')], string="Container Status", compute="_container_status")

    @api.depends('container_quantity')
    def _container_status(self):
        for record in self:
            if record.container_quantity > 0:
                record.container_status = 'in_use'
            else:
                record.container_status = 'not_used'
class EmdadFleetModel(models.Model):
    _name = "emdad.fleet.model"
    
    name = fields.Char(string="Model")

class EmdadFleetInsurance(models.Model):
    _name = "emdad.fleet.insurance"

    name = fields.Char(string="Insurance Contract ID")
    insurance_company = fields.Many2one("emdad.contacts", string="Insurance Company")
    contract_start_date = fields.Date(string="Contract Start Date")
    contract_next_renewal = fields.Date(string="Next Renewal", store=True)
    contract = fields.Binary(string="Contract")
    status = fields.Selection([('in_progress', 'In Progress'), ('expired', 'Expired')], string="Contract Status", compute="_compute_status", store=True)
    contract_value = fields.Float(string="Contract Value")
    related_truck = fields.Many2one("emdad.fleet", string="Related Truck")

    @api.depends('contract_next_renewal')
    def _compute_status(self):
        for record in self:
            if record.contract_next_renewal:
                current_date = datetime.now().date()
                if record.contract_next_renewal >= current_date:
                    record.status = 'in_progress'
                else:
                    record.status = 'expired'
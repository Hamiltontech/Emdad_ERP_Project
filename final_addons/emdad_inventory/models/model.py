from emdad import fields, api, models
from datetime import datetime, timedelta

class EmdadWarehouse(models.Model):
    _name = 'emdad.warehouse'

    name = fields.Char(string="Warehouse Name")
    short_name = fields.Char(string="Short Name", unique=True)
    warehouse_relation = fields.Many2one("res.company", string="Related Company")
    locations = fields.One2many("emdad.warehouse.location", "related_warehouse", String="Locations")
    locations_count = fields.Integer(string="Number of Locations", compute="_number_locations", store=True)
    total_qty = fields.Float(string="Total Quantity", compute="_total_quantities")
    @api.depends('locations')
    def _total_quantities(self):
        for record in self:
            record.total_qty = sum(product.quantity for product in record.locations)
    @api.depends('locations')
    def _number_locations(self):
        for record in self:
            record.locations_count = len(record.locations)
class EmdadLocations(models.Model):
    _name = 'emdad.warehouse.location'

    name = fields.Char(string="Location Name")
    related_warehouse = fields.Many2one("emdad.warehouse", string="Related Warehouse")
    location_type = fields.Selection([('expiary', 'Expiary Location'), ('scrap', 'Scrap Location'), ('storage','Storage'), ('moveable', 'Moveable')], string="Location Type")
    used_delivery = fields.Boolean(string="Used for Delivery")
    used_reciepts = fields.Boolean(string="Used for Reciepts")
    parent_location = fields.Many2one("emdad.warehouse.location", string="Parent Location")
    location_usage = fields.Many2one("emdad.warehouse.location.usage", string="Location Usage")
    products = fields.One2many("emdad.warehouse.quants.lines", "location", string="Products Quantities")
    quantity = fields.Float(string="Current Quantity", compute="_current_qty")
    @api.depends('products.counted_qty')
    def _current_qty(self):
        for record in self:
            record.quantity = sum(product.counted_qty for product in record.products)



class EmdadLocationUsage(models.Model):
    _name = 'emdad.warehouse.location.usage'

    name = fields.Char(string="Usage Name")
    instructions = fields.Text(string="Instructions")

class EmdadQuants(models.Model):
    _name = 'emdad.warehouse.quants'

    name = fields.Char(string="Adjustement Reference")
    adjustment_date = fields.Date(string="Date of Adjustment")
    purpose = fields.Selection([('correction', 'Correction'), ('normal', 'Normal Adjustement'), ('purchase','Purchase')], string="Adjustment Purpose")
    location = fields.Many2one("emdad.warehouse.location", string="Adjustment Location")
    quants_lines = fields.One2many("emdad.warehouse.quants.lines", "related_adjustement", string="Lines")

class EmdadBatches(models.Model):
    _name= 'emdad.warehouse.batches'

    name = fields.Char(string="Batch Name")
    expiary = fields.Date(string="Expiary Date")
    status = fields.Selection([('expired', 'Expired'), ('almost','Close to Expiration'), ('active', 'Active')])
    product_id = fields.Many2one("product.management", string="Product")
    gtin = fields.Char(string="GTIN")
    counts = fields.One2many("emdad.warehouse.quants.lines", "batch", string="Quantities")
    available = fields.Float(string="Available Quantity", compute="_available_qty")
    origin = fields.Many2one("res.country", related="product_id.product_origin", string="Batch Origin")
    average_cost = fields.Float(string="Average Cost", compute="_batch_average_cost")
    @api.depends('counts')
    def _batch_average_cost(self):
        for record in self:
            total_cost = sum(line.cost for line in record.counts)
            lines_count = len(record.counts)

            if lines_count > 0:
                record.average_cost = total_cost / lines_count
            else:
                record.average_cost = 0.0
    @api.depends('counts')
    def _available_qty(self):
        for record in self:
            record.available = sum(product.counted_qty for product in record.counts)
    @api.onchange('expiary')
    def _onchange_expiary(self):
        current_date = datetime.now().date()
        if self.expiary:
            expiary_date = fields.Date.from_string(self.expiary)
            days_difference = (expiary_date - current_date).days
            if days_difference < 0:
                self.status = 'expired'
            elif days_difference <= 7:
                self.status = 'almost'
            else:
                self.status = 'active'

class EmdadQuantsLines(models.Model):
    _name = 'emdad.warehouse.quants.lines'

    name = fields.Char(string="Line Relation")
    product_id = fields.Many2one("product.management", string="Product")
    barcode = fields.Char(string="Barcode", related="product_id.barcode")
    expiary = fields.Date(string="Expiary Date")
    location = fields.Many2one("emdad.warehouse.location", string="Location")
    counted_qty = fields.Float(string="Counted")
    metric = fields.Many2one("product.units", string="Unit")
    packaging = fields.Many2one("emdad.product.packaging", string="Packaging")
    batch = fields.Many2one("emdad.warehouse.batches")
    batch_status = fields.Selection([('expired', 'Expired'), ('almost','Close to Expiration'), ('active', 'Active')], related="batch.status", string="Batch Health")
    cost = fields.Float(string="Purchase Cost")
    unit_cost = fields.Float(string="Unit Cost", compute="_calculate_unit_cost")
    related_adjustement = fields.Many2one("emdad.warehouse.quants", string="Related Adjustement")
    scrap_action = fields.Many2one("emdad.warehouse.scrap", string="Related Scrap")

    @api.depends('cost', 'counted_qty')
    def _calculate_unit_cost(self):
        for record in self:
            if record.cost and record.counted_qty > 0:
                record.unit_cost = record.cost / record.counted_qty
            else:
                record.unit_cost = 0

class EmdadScrap(models.Model):
    _name="emdad.warehouse.scrap"

    name = fields.Char(string="Scrap ID")
    date = fields.Date(string="Schedule Date")
    status = fields.Selection([('draft','Draft Action'), ('approved','Approved'), ('done','Done'), ('cancel','Cancelled')], string="Scrap Status", default="draft")
    reason = fields.Selection([('expired_products','Expired Products'), ('damaged','Damaged Products')], string="Scrap Reason")
    explain = fields.Text(string="Explaination")
    location = fields.Many2one("emdad.warehouse.location", string="Scrap Location")
    scrap = fields.One2many("emdad.warehouse.quants.lines", "scrap_action", string="Scrap Actions")
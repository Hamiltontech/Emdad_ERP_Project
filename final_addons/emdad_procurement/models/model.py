from emdad import api, fields, models
from datetime import datetime, date
from emdad.exceptions import ValidationError

class EmdadProcurement(models.Model):
    _name = "emdad.procurement"

    name = fields.Char(string="Procurement ID")
    effective_date = fields.Date(string="Effective Date")
    operation_type = fields.Selection([('resupply', 'Resupply'), ('replinish', 'Replinishement')], string="Procurement Type")
    vendor = fields.Many2one("emdad.contacts", string="Vendor")
    vendor_phone = fields.Char(string="Phone Number", related="vendor.phone")
    procurement_lines = fields.One2many("emdad.line.procurement", "related_procurement", string="Lines")
    process_type = fields.Selection([('market', 'Emdad Market'), ('direct', 'Direct')], string="Process Type")
    payment_type = fields.Selection([('cash', 'Cash'), ('credit', 'Credit')], string="Payment Type")
    distribution_type = fields.Selection([('single', 'One Location'), ('multiple', 'Multiple Locations')], string="Distribution Type")
    total_before_discount = fields.Float(string="Total Before Discount")
    total_discount = fields.Float(string="Total Discount")
    total_amount = fields.Float(string="Total Amount")
    status = fields.Selection([('pending', 'Pending'),('active','Active'), ('closed','Closed'), ('expired','Expired'), ('recieve', 'Receiving'), ('recieved','Recieved')], string="Quote Status", default="pending")
    published = fields.Boolean(string="Published")
    exp_quote = fields.Date(String="Expiration")
    single_location = fields.Many2one("emdad.warehouse.location", string="Single Location")
    is_multiple = fields.Boolean(string="Multiple Location", compute="_type_location")
    all_info = fields.Boolean(string="All Information", compute="_check_all_info")
    in_recieve = fields.Boolean(string="In Recieving")
    recieved = fields.Boolean(string="Recieved")

    @api.depends('in_receive', 'procurement_lines', 'name')
    def create_inventory_input(self):
        quants = self.env['emdad.warehouse.quants']
        for record in self:
            data_to_copy = {
                'adjustment_date': record.effective_date,
                'name': record.name,
                'purpose': 'purchase',
                'quants_lines': [(0, 0, {
                    'product_id': line.product_id.id, 
                    'location': line.location.id,
                    'counted_qty' : line.recieved_qty,
                    'cost' : line.final_total,
                    'metric' : line.metric.id,
                    'batch' : line.batch.id
                }) for line in record.procurement_lines]
            }
            quants_record = quants.create(data_to_copy)
            record.status = ''
    def recieved_process(self):
        for record in self:
            record.status = 'recieve'
            record.in_recieve = True
            record.procurement_lines.in_recieve = True

    @api.depends('effective_date', 'operation_type', 'process_type', 'payment_type', 'distribution_type')
    def _check_all_info(self):
        for record in self:
            if record.effective_date and record.operation_type and record.process_type and record.payment_type and record.distribution_type:
                record.all_info = True
            else:
                record.all_info = False

    @api.onchange('is_multiple')
    def onchange_is_multiple(self):
        if self.procurement_lines:
            self.procurement_lines.write({'is_multiple': self.is_multiple})

    @api.depends('distribution_type')
    def _type_location(self):
        for record in self:
            if record.distribution_type == 'multiple':
                record.is_multiple = True
            else:
                record.is_multiple = False

    @api.onchange('procurement_lines')
    def _onchange_procurement_lines(self):
        total_before_discount = sum(self.procurement_lines.mapped('total'))
        total_discount = sum(self.procurement_lines.mapped('final_total'))
        total_amount = total_before_discount - total_discount

        self.total_before_discount = total_before_discount
        self.total_discount = total_discount
        self.total_amount = total_amount
    
    def close_quote(self):
        for record in self:
            record.status = 'closed'
            record.published = False

    def approve_quote(self):
        for record in self:
            record.status = 'active'

    def publish_quote(self):
        for record in self:
            record.published = True

    @api.onchange('exp_quote')
    def _set_expiary(self):
        for record in self:
            if record.exp_quote and record.exp_quote <= date.today():
                record.status = 'expired'

class EmdadProcurementLines(models.Model):
    _name = "emdad.line.procurement"

    name = fields.Char(string="Procuement Reference ID")
    related_procurement = fields.Many2one("emdad.procurement", string="Related Order", ondelete="cascade", index=True)
    barcode = fields.Char(string="Barcode", related="product_id.barcode")
    product_id = fields.Many2one("product.management", string="Product", ondelete="cascade")
    attach = fields.Binary(string="Specifications")
    request_qty = fields.Float(string="Quantity")
    product_cost = fields.Float(string="Cost")
    total = fields.Float(string="Total", compute="_total_cost")
    final_total = fields.Float(string="Final Total", compute="_calculate_discount")
    discount = fields.Float(string="Discount %")
    vendor = fields.Many2one("emdad.contacts", string="Vendor")
    metric = fields.Many2one("product.units", string="Metric")
    packaging = fields.Many2one("emdad.product.packaging", string="Packaging")
    location = fields.Many2one("emdad.warehouse.location", string="Location")
    is_multiple = fields.Boolean(string="Multiple Location", related="related_procurement.is_multiple")
    in_recieve = fields.Boolean(string="In Recieving")
    recieved_qty = fields.Float(string="Recieved")
    difference = fields.Float(string="Difference", compute="_compute_difference")
    recieve_status = fields.Selection([('full', 'Recieved All'), ('partial', 'Partial'), ('not', 'Not Received')], string="Status", compute="_get_status")
    batch = fields.Many2one("emdad.warehouse.batches", string="Related Batch")

    @api.depends('recieved_qty', 'request_qty')
    def _get_status(self):
        for record in self:
            if record.recieved_qty and record.request_qty:
                diff = -1 * record.difference
                if diff == record.request_qty:
                    record.recieve_status = 'not'
                elif diff > 0:
                    record.recieve_status = 'partial'
                elif record.difference == 0:
                    record.recieve_status = 'full'
                elif record.recieved_qty > record.request_qty:
                    raise ValidationError("You can not receive more than what you requested")
            else: 
                record.recieve_status = ''

    @api.depends('recieved_qty', 'request_qty', 'in_recieve')
    def _compute_difference(self):
        for record in self:
            if record.in_recieve and record.recieved_qty is not None and record.request_qty is not None:
                record.difference = record.recieved_qty - record.request_qty
            else:
                record.difference = 0  # Or handle it based on your business logic

    @api.onchange('is_multiple')
    def _apply_location(self):
        for record in self:
            if record.is_multiple == False:
                record.location = record.related_procurement.single_location

    @api.onchange('packaging')
    def _apply_quantity(self):
        for record in self:
            if record.packaging:
                record.request_qty = record.packaging.quantity_holding * record.packaging.total_value
                record.metric = record.packaging.reference_unit

    @api.depends('request_qty', 'product_cost', 'product_id')
    def _total_cost(self):
        for record in self:
            if record.product_id and record.request_qty and record.product_cost:
                record.total = record.request_qty * record.product_cost
            else:
                record.total = 0

    @api.depends('discount', 'total')
    def _calculate_discount(self):
        for record in self:
            if record.discount and record.total:
                discount = ((record.discount / 100) * record.total)
                new_price = record.total - discount
                record.final_total = new_price
            else:
                record.discount = 0
                record.final_total = record.total

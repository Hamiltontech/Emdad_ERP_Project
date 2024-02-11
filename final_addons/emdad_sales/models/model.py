from emdad import api, fields, models
from emdad.exceptions import ValidationError

class EmdadSales(models.Model):
    _name="emdad.sales"
    #customer information added by laith
    name = fields.Char(string="Sales ID", compute="_get_name")
    date = fields.Date(string="Date Assigned",required=True)
    effective_date = fields.Date(string="Assigned Date",required=True)
    customer = fields.Many2one("emdad.contacts")
    phone = fields.Char(string="Phone", related="customer.phone")
    email = fields.Char(string="Email", related="customer.email")
    cr_number = fields.Char(string="CR Number", related="customer.cr_number")
    #sales information by laith
    delivery_type = fields.Selection([('multiple', 'Multiple Locations'), ('single','Single Location')], string="Delivery Type")
    location = fields.Many2one("emdad.warehouse.location", string="Assigned Location")
    total = fields.Float(string="Total", compute="_get_total_lines")
    #sales Lines
    order_lines = fields.One2many("emdad.sales.line","related_sales", string="Order Lines")
    so_status = fields.Selection([('new','New'), ('approved','Approved'), ('cancelled','Cancelled'), ('in_delivery','In Delivery'),('delivered','Delivered')], string="Status", default="new")
    in_delivery = fields.Boolean(string="In Delivery")
    stages = fields.Char(compute="_get_stage", default="RFP")
    def create_delivery(self):
        quants = self.env['emdad.warehouse.quants']
        for record in self:
            record.in_delivery = True
            record.so_status = 'in_delivery'
            data_to_copy = {
                'adjustment_date' : record.effective_date,
                'name' : record.name,
                'purpose' : 'delivery',
                'quants_lines': [(0,0, {
                    'product_id' : line.product.id,
                    'location' : line.location.id,
                    'metric' : line.metric_unit.id,
                    'counted_qty' : -1 * line.qty,
                }) for line in record.order_lines]
            }
            quants_record = quants.create(data_to_copy)
    @api.onchange('delivery_type', 'location')
    def assign_the_location(self):
        for record in self:
            if record.delivery_type == 'single' and record.location:
                for line in record.order_lines:
                    line.location = record.location
            else:
                pass
    @api.depends('order_lines.final_total')
    def _get_total_lines(self):
        for record in self:
            record.total = sum(line.final_total for line in record.order_lines)
    
    def approve_sales(self):
        for record in self:
            record.so_status = 'approved'
    def cancel_sales(self):
        for record in self:
            record.so_status = 'cancelled'

    @api.depends('date','so_status')
    def _get_name(self):
        for record in self:
            if record.customer and record.date and record.so_status:
                so_status =str(record.so_status)
                year = str(record.date.year)
                month = str(record.date.month).zfill(2)
                sequence = str(record.id).zfill(5)
                record.name = "SALES" + '/' + so_status.upper() + '/' + year + '/' + month + '/' + sequence
            else:
                record.name="Draft Entry"
    
    @api.onchange('so_status')
    def _get_stage(self):
        for record in self:
            if record.so_status == "new" or record.so_status == "cancelled":
                record.stages = "RFP"

            elif record.so_status == "approved":
                record.stages = "sales order"

            else:
                record.stages = "sales order"
                
class EmdadSalesLines(models.Model):
    _name="emdad.sales.line"

    name = fields.Char(string="ID Line")
    delivery_type = fields.Selection([('multiple', 'Multiple Locations'), ('single','Single Location')], related="related_sales.delivery_type" ,string="Delivery Type")
    related_sales = fields.Many2one("emdad.sales", string="Related SO")
    delivery_type = fields.Selection([('multiple', 'Multiple Locations'), ('single','Single Location')], related="related_sales.delivery_type", string="Delivery Type")
    product = fields.Many2one("product.management", string="Product")
    barcode = fields.Char(string="Barcode", related="product.barcode")
    batch = fields.Many2one("emdad.warehouse.batches", string="Batch")
    tax = fields.Many2one("emdad.tax", string="Tax")
    location = fields.Many2one("emdad.warehouse.location", string="Location")
    price = fields.Float(string="Price")
    metric_unit = fields.Many2one("product.units", string="Metric Unit")
    metric = fields.Many2one("product.metrics", related="product.category.products_metrics")
    qty = fields.Float(string="Quantity")
    recieved_qty = fields.Float(string="Sent Quantity")
    sent_status = fields.Selection([('partial','Partial Delivery'), ('full','Full Delivery'), ('not','Not Delivered')], string="Delivery Status", compute="_get_status")
    discount = fields.Float(string="Discount %")
    total = fields.Float(string="Total", compute="_calc_total")
    final_total = fields.Float(string="Total", compute="_get_discount")
    tax_amount = fields.Float(string="Tax Amount", readonly=True)
    after_tax = fields.Float(string="Total Inc.", compute="_calculate_tax")
    in_delivery = fields.Boolean(string="In Delivery", related="related_sales.in_delivery")
    @api.depends('recieved_qty')
    def _get_status(self):
        for record in self:
            if record.recieved_qty < record.qty:
                record.sent_status = 'partial'
            elif record.recieved_qty == 0:
                record.sent_status = 'not'
            elif record.recieved_qty > record.qty:
                 raise ValidationError("You can not receive more than what you requested")
            else:
                record.sent_status = 'full'
    
    @api.depends('final_total', 'tax')
    def _calculate_tax(self):
        for record in self:
            if record.product:
                record.tax_amount = record.final_total * (record.tax.percentage /100)
                after_tax = record.final_total + record.tax_amount
                record.after_tax = after_tax
            else:
                record.after_tax = record.final_total
    @api.onchange('product_id')
    def default_tax(self):
        for record in self:
            if not record.tax:
                record.tax = record.product.sales_tax
            else:
                pass
    @api.depends('price', 'qty', 'final_total')
    def _calc_total(self):
        for record in self:
            if record.qty and record.price:
                record.total = record.price * record.qty
                record.final_total = record.total
            else:
                record.total = 0
                record.final_total = 0
    
    @api.depends('discount')
    def _get_discount(self):
        for record in self:
            if record.discount:
                discount_amount = record.total * (record.discount / 100)
                record.final_total = record.total - discount_amount
            else:
                record.final_total = record.total
    @api.onchange('delivery_type')
    def assign_location(self):
        for record in self:
            if record.delivery_type == 'single':
                record.location = record.related_sales.location
            else:
                pass
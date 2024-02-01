from emdad import api, fields, models

class EmdadSales(models.Model):
    _name="emdad.sales"
    #customer information added by laith
    name = fields.Char(string="Sales ID", compute="_get_name")
    date = fields.Date(string="Date Assigned")
    effective_date = fields.Date(string="Assigned Date")
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

    @api.depends('customer','date','so_status')
    def _get_name(self):
        for record in self:
            if record.customer and record.date and record.so_status:
                customer = str(record.customer.name)
                so_status =str(record.so_status)
                year = str(record.date.year)
                month = str(record.date.month).zfill(2)
                sequence = str(record.id).zfill(5)
                record.name = customer + '/' + so_status.upper() + '/' + year + '/' + month + '/' + sequence
            else:
                record.name="Draft Entry"
                
class EmdadSalesLines(models.Model):
    _name="emdad.sales.line"

    name = fields.Char(string="ID Line")
    related_sales = fields.Many2one("emdad.sales", string="Related SO")
    delivery_type = fields.Selection([('multiple', 'Multiple Locations'), ('single','Single Location')], related="related_sales.delivery_type", string="Delivery Type")
    product = fields.Many2one("product.management", string="Product")
    barcode = fields.Char(string="Barcode", related="product.barcode")
    location = fields.Many2one("emdad.warehouse.location", string="Location")
    price = fields.Float(string="Price")
    metric = fields.Many2one("product.metrics", related="product.category.products_metrics")
    qty = fields.Float(string="Quantity")
    discount = fields.Float(string="Discount %")
    total = fields.Float(string="Total", compute="_calc_total")
    final_total = fields.Float(string="Total", compute="_get_discount")

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
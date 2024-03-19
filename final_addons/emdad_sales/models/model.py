from emdad import api, fields, models
from emdad.exceptions import ValidationError
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import json
import requests


class EmdadSales(models.Model):
    _name="emdad.sales"
    #customer information added by laith
    name = fields.Char(string="Sales ID", compute="_get_name")
    barcode = fields.Char(string='Barcode', copy=False)
    date = fields.Date(string="Date Assigned",required=True)
    effective_date = fields.Date(string="Assigned Date",required=True)
    customer = fields.Many2one("emdad.contacts")
    phone = fields.Char(string="Phone", related="customer.phone")
    email = fields.Char(string="Email", related="customer.email")
    cr_number = fields.Char(string="CR Number", related="customer.cr_number")
    #sales information by laith
    delivery_type = fields.Selection([('multiple', 'Multiple Deliveries / Schedulled'), ('single','Single Time Delivery / Full')], string="Delivery Type")
    schedulle = fields.Datetime(string="Schedulled Delivery")
    delivery_source = fields.Selection([('single','From One Location'),('multiple','From Multiple Locations')])
    location = fields.Many2one("emdad.warehouse.location", string="Assigned Location")
    total = fields.Float(string="Total", compute="_get_total_lines")
    #sales Lines
    order_lines = fields.One2many("emdad.sales.line","related_sales", string="Order Lines")
    so_status = fields.Selection([('new','New'), ('approved','Approved'), ('cancelled','Cancelled'), ('in_delivery','In Delivery'),('delivered','Delivered')], string="Status", default="new")
    in_delivery = fields.Boolean(string="In Delivery")
    stages = fields.Char(compute="_get_stage", default="RFP")
    related_delivery = fields.Many2one("emdad.warehouse.quants", string="Related Delivery")
    related_remote_po = fields.Integer(string="Customer PO ID")
    
    def respond_to_direct_offer(self):
        for record in self:
            # record.is_sent = True

            response = {}
            url = "http://localhost:8022/api/v1/procurement/update"
            data = record.order_lines.read(['price','related_remote_po_line'])
            response['data'] = data
            response['related_remote_po'] = record.read(['related_remote_po'])
            payload = json.dumps(response,default=str)

            
            print(payload)

            headers = {
            'Content-Type': 'application/json',
            }

            response = requests.request("PUT", url, headers=headers, data=payload)

            # print(response.text)
        
            
    
    def generate_barcode(self):
        barcode_value = "YourBarcodeValue"  # Replace with your actual barcode value
        ean = barcode.get('code128', barcode_value, writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
       
        self.write({'barcode': barcode_value})

    def print_report(self):
        return self.env.ref('emdad_sales.action_report_delivery_note').report_action(self)
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
            record.related_delivery = quants_record.id
            record.generate_barcode()
            
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
            if record.customer and record.date:
                year = str(record.date.year)
                month = str(record.date.month).zfill(2)
                sequence = str(record.id).zfill(5)
                record.name = "SALES" + '/' + year + '/' + month + '/' + sequence
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
    # delivery_type = fields.Selection([('multiple', 'Multiple Locations'), ('single','Single Location')], related="related_sales.delivery_type" ,string="Delivery Type")
    delivery_source = fields.Selection([('single','From One Location'),('multiple','From Multiple Locations')], related="related_sales.delivery_source", string="Delivery Source")
    related_sales = fields.Many2one("emdad.sales", string="Related SO")
    delivery_type = fields.Selection([('multiple', 'Schedulled'), ('single','Single Time Deliveryx ')], string="Delivery Type", related="related_sales.delivery_type")
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
    product_image = fields.Binary(string="Product Image", related="product_id.product_image")
    product_id = fields.Many2one("product.management", string="Product", ondelete="cascade")
    description = fields.Text(string="Description")
    barcode = fields.Char(string="Barcode", related="product_id.barcode")
    attach = fields.Binary(string="Specifications")
    request_qty = fields.Float(string="Quantity")
    price_list = fields.Many2one("emdad.products.pricing", string="Price List")
    schedulle = fields.Datetime(string="Schedule")
    related_remote_po_line = fields.Integer(string="Customer PO Line ID")
    @api.onchange('price_list')
    def select_pricing(self):
        for record in self: 
            if record.price_list:
                record.price = record.price_list.price
            else:
                record.price = 0.0

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
                record.schedulle = record.related_sales.schedulle
            elif record.delivery_type == 'multiple':
                record.location = ''
                record.schedulle = record.related_sales.schedulle
            else:
                pass

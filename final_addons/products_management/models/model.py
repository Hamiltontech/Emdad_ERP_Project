from emdad import api, models, fields
from emdad.exceptions import ValidationError
from datetime import datetime, date

class ProductManagement(models.Model):
    _name = 'product.management'
    name = fields.Char(string="Product Name",required=True)
    barcode = fields.Char(string="Barcode", unique=True ,required=True)
    emdad_reference = fields.Char("Emdad ID", unque=True)
    description = fields.Text("Description")
    category = fields.Many2one("product.emdad.category", string="Product Category")
    is_expiary = fields.Boolean(string="Has Expiary")
    product_image = fields.Binary(string="Product Image")
    related_company = fields.Many2many("res.company")
    selling_price = fields.Float(string="Average Price", store=True)
    purchase_price = fields.Float(string="Last Purchase Price")
    products_pricing = fields.One2many("emdad.products.pricing", "related_product", string="Product Pricing")
    active_product = fields.Boolean(string="Active Product")
    fav_product = fields.Boolean(string="Fav. Product")
    product_origin = fields.Many2one("res.country", string="Origin")
    name_ar = fields.Char(string="Product Name العربية")
    is_kit = fields.Boolean(string="Is a kit")
    purchase_metric = fields.Many2one("product.units", string="Purchase Metric")
    selling_metric = fields.Many2one("product.units", string="Selling Metric")
    related_metric = fields.Many2one("product.metrics", related="category.products_metrics", string="Assigned Metric")
    # contains = fields.Many2many("product.management", string="Components")
    quants = fields.Float(compute='get_total_counted_qty')

    @api.onchange('products_pricing')
    def _calculate_average(self):
        for record in self:
            lines = len(record.products_pricing )
            total_price = sum(line.price for line in record.products_pricing)

            if lines > 0:
                record.selling_price = total_price / lines
            else:
                record.selling_price = 0.0

    def get_total_counted_qty(self):
        for record in self:
            print("*****************",record.id)
            quants_lines = self.env['emdad.warehouse.quants.lines']
            subquery = quants_lines.search([
                ('product_id', '=', record.id)
            ])
            subquery = subquery.read(['counted_qty'])
            print(subquery)
            
            total_count = sum(line['counted_qty'] for line in subquery)
            print("---------",total_count)
            print(record.id)
            record.quants = total_count

class ProductsCategories(models.Model):
    _name="product.emdad.category"

    name = fields.Char(string="Category Name")
    code_base = fields.Char(string="Category Code")
    parent_key = fields.Char(string="Parent Key")
    parent = fields.Many2one("product.emdad.category", string="Parent Category")
    category_type = fields.Selection([('internal', 'Internal Use'), ('selling', 'Selling Products'), ('consumed', 'Consumed Products')], string="Category Type")
    products_metrics = fields.Many2one("product.metrics", string="Product Metrics")
    categ_fullname = fields.Char(string="Full Name", compute="_generate_categ_name")

    @api.depends('name', 'parent')
    def _generate_categ_name(self):
        for record in self:
            if record.parent:
                record.categ_fullname = record.parent.categ_fullname + " > " + record.name
            else:
                record.categ_fullname = record.name


class UnitsMetrics(models.Model):
    _name="product.metrics"

    name = fields.Char(string="Metric Name")
    main_reference = fields.Many2one("product.units", string="Main Reference")
    

class UnitsMeasure(models.Model):
    _name="product.units"

    name = fields.Char(string="Unit of Measure")
    reference = fields.Float(string="Value")
    metric = fields.Many2one("product.metrics", string="Metric")
    ref_main = fields.Many2one("product.units", related="metric.main_reference", string="Main Reference")

class ProductsPricing(models.Model):
    _name="emdad.products.pricing"

    name = fields.Char(string="Pricing Name")
    related_product = fields.Many2one("product.management", string="Product")
    min_qty = fields.Float(string="Minimum Quantity")
    max_qty = fields.Float(string="Max Quantity")
    price = fields.Float(string="Pricing")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    active = fields.Boolean(string="Active")
    related_unit = fields.Many2one("product.units", string="Unit Metric")
    status = fields.Selection([('not','Expired'), ('active','Active')], string="Status")

    @api.onchange('min_qty', 'max_qty')
    def _compare_qty(self):
        for record in self:
            if record.min_qty and record.max_qty:
                if record.max_qty < record.min_qty :
                    raise ValidationError("You can not have maximum quantity lower than the minimum quantity")
                else:
                    record.active = True
            else:
                record.active = True
    
    @api.onchange('start_date', 'end_date')
    def _active_status(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date == date.today():
                    record.active = False
                elif record.end_date < record.start_date:
                    raise ValidationError("End date can't be earlier than the start date")
                elif record.end_date < date.today():
                    record.active = False
                    record.status = 'not'
                else:
                    record.active = True
                    record.status = 'active'


class ProductPackaging(models.Model):
    _name="emdad.product.packaging"

    name = fields.Char(string="Package Name")
    reference_unit = fields.Many2one("product.units", string="Unit")
    quantity_holding = fields.Float(string="Capacity")
    total_value = fields.Float(string="Original Value", related="reference_unit.reference")


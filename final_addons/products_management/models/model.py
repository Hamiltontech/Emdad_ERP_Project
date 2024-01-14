from emdad import api, models, fields

class ProductManagement(models.Model):
    _name = 'product.management'

    name = fields.Char(string="Product Name")
    barcode = fields.Char(string="Barcode", unique=True)
    emdad_reference = fields.Char("Emdad ID", unque=True)
    description = fields.Text("Description")
    category = fields.Many2one("product.emdad.category", string="Product Category")
    is_expiary = fields.Boolean(string="Has Expiary")
    product_image = fields.Binary(string="Product Image")
    related_company = fields.Many2many("res.company")
    selling_price = fields.Float(string="Average Price")
    purchase_price = fields.Float(string="Last Purchase Price")
    products_pricing = fields.One2many("emdad.products.pricing", "related_product", string="Product Pricing")
    active_product = fields.Boolean(string="Active Product")
    fav_product = fields.Boolean(string="Fav. Product")

class ProductsCategories(models.Model):
    _name="product.emdad.category"

    name = fields.Char(string="Category Name")
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
    reference = fields.Float(string="Reference Value")
    metric = fields.Many2one("product.metrics", string="Metric")
    ref_main = fields.Many2one("product.units", related="metric.main_reference", string="Main Reference")

class ProductsPricing(models.Model):
    _name="emdad.products.pricing"

    name = fields.Char(string="Pricing Name")
    related_product = fields.Many2one("product.management", string="Product")
    min_qty = fields.Float(string="Minimum Quantity")
    max_qty = fields.Float(string="Max Quantity")
    price = fields.Float(string="Pricing")
    related_unit = fields.Many2one("product.units", string="Unit Metric")




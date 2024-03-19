from emdad import api, fields, models
from datetime import datetime, date
from emdad import exceptions
import xmlrpc.client
import requests
import json
import copy

class EmdadProcurement(models.Model):
    _name = "emdad.procurement"

    name = fields.Char(string="Procurement ID",compute="_get_name")
    effective_date = fields.Date(string="Effective Date")
    parent_rfq = fields.Many2one("emdad.procurement", string="Parent Offer")
    operation_type = fields.Selection([('resupply', 'Resupply'), ('replinish', 'Replinishement')], string="Procurement Type")
    vendor = fields.Many2one("emdad.contacts", string="Vendor")
    vendor_phone = fields.Char(string="Phone Number", related="vendor.phone")
    procurement_lines = fields.One2many("emdad.line.procurement", "related_procurement", string="Lines")
    process_type = fields.Selection([('market', 'Emdad Market'), ('direct', 'Direct'), ('multiple', 'Multiple Vendor')], string="Process Type")
    direct_type = fields.Selection([('single','Single Vendor'), ('multi','Multiple Vendors')], string="Direct Type")
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
    related_bill = fields.Many2one("emdad.journal.entry", string="Related Bill")
    bill_status = fields.Selection([('created','Bill Created'), ('not','Bill Not Created')], default="not")
    amount_pay = fields.Float(string="Amount To Pay")
    payment_date = fields.Date(string="Payment Date")
    payment_journal = fields.Many2one("emdad.accounts.journal", string="Pay From")
    payment_status = fields.Selection([('not','Not Paid'),('paid','Paid')], string="Payment Status", default="not")
    credit_facility = fields.Many2one("emdad.credit.facility", string="Credit Facility")
    credit_value = fields.Float(string="Credit Value", related="credit_facility.amount")
    credit_balance = fields.Float(string="Credit Balance", related="credit_facility.balance")
    stages = fields.Char(compute="_get_stage", default="RFQ")
    procurement_backorder = fields.Boolean(compute="_get_backorder")
    emdad_category = fields.Many2one("product.emdad.category", string="Category")
    related_tender = fields.Many2one("emdad.tender", string="Related Tender")
    related_offers = fields.One2many("emdad.procurement", "parent_rfq", string="Related Offers")
    is_sent = fields.Boolean(string="Is Sent")
    

    # def send_direct_offer(self):
    #     for record in self:
    #         record.is_sent = True
    #         remote_url = 'https://admin.emdad.com'
    #         remote_db = 'emdad'
    #         remote_username = 'emdad'
    #         remote_password = '210@Carringtonrd'
 
    #         target_model = 'emdad.send'
    #         target_url = f'{remote_url}/xmlrpc/2/object'
 
    #         common_proxy = xmlrpc.client.ServerProxy(f'{remote_url}/xmlrpc/2/common')
    #         uid = common_proxy.authenticate(remote_db, remote_username, remote_password, {})
    #         new_record_id = models_proxy.execute_kw(remote_db, uid, remote_password, target_model, 'create', [{'name': remote_name}])
    #         return new_record_id

    def send_direct_offer(self):

        po_company_cr = self.env['res.company'].sudo().search_read([],['cr_number'])

        for record in self:
            record.is_sent = True

            url = "http://localhost:8024/api/v1/sales/direct/create/"
            data = record.read()
            data[0]['parent_rfq'] = self.read_all(record.parent_rfq) if record.parent_rfq else []
            data[0]['vendor'] = self.read_all(record.vendor) if record.vendor else []
            data[0]['procurement_lines'] = self.read_all(record.procurement_lines) if record.procurement_lines else []
            data[0]['emdad_category'] = self.read_all(record.emdad_category) if record.emdad_category else []
            data[0]['single_location'] = self.read_all(record.single_location) if record.single_location else []
            data[0]['related_tender'] = self.read_all(record.related_tender) if record.related_tender else []
            data[0]['related_offers'] = self.read_all(record.related_offers) if record.related_offers else []
            data[0]['procurement_lines'] = self.read_all_procurement_lines(record.procurement_lines) if record.procurement_lines else []
            data[0]['po_company_cr'] = po_company_cr[0] if po_company_cr else []

            payload = json.dumps(data,default=str)
            headers = {
            'Content-Type': 'application/json',
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            raise exceptions.UserError(response.text)
        
    def read_all_procurement_lines(self,record):
        procurement_lines = []
        for line_procurement in record:
            product_id = line_procurement.product_id
            procurement = line_procurement.read()[0]
            procurement['product_id'] = product_id.read(['barcode'])
            procurement_lines.append(procurement)
        return procurement_lines


    def read_all(self, record):
        sub_record = []
        for sub in record:
            sub_dict = sub.read()
            sub_record.append(*sub_dict)
        return sub_record
    
    def create_counter_offer(self):
        for record in self:
            record.parent_rfq = record.id
            procurement_lines = []
            for line in record.procurement_lines:
                line_data = [
                    (0, 0, {
                        'product_id': line.product_id.id,
                        'request_qty': line.request_qty,
                        'is_packge': line.is_packge,
                    }),          
                ]
                procurement_lines.extend(line_data)

            counter_offer = self.env['emdad.procurement'].create({
                'emdad_category' : record.emdad_category.id,
                'effective_date' : record.effective_date,
                'exp_quote' : record.exp_quote,
                'operation_type' : record.operation_type,
                'process_type' : record.process_type,
                'direct_type' : record.direct_type,
                'parent_rfq' : record.parent_rfq.id,
                'payment_type' : record.payment_type,
                'distribution_type' : record.distribution_type,
                'single_location' : record.single_location.id,
                'procurement_lines' : procurement_lines
            })

            record.ensure_one()
            record.write({'parent_rfq': counter_offer.id})
    def print_vendor_bill(self):
        datas = self.env[self._name].browse(self.ids).read()[0]
        report_action = self.env.ref('emdad_procurement.emdad_procurement_report_action')
        if report_action:
            return report_action.report_action(self.ids, data=datas)
        else:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'Error', 'message': 'Report action not found'}}


    @api.model
    def get_tiles_data(self):
        procurements = self.search([])
        procurements_by_process_type = procurements.mapped('process_type')

        direct_count = procurements_by_process_type.count('direct')
        market_count = procurements_by_process_type.count('market')
        multiple_count = procurements_by_process_type.count('multiple')

        return {
            'direct_count': direct_count,
            'market_count': market_count,
            'multiple_count': multiple_count,
        }
    
    @api.onchange('emdad_category')
    def change_category(self):
        for record in self: 
            if record.emdad_category:
                for line in record.procurement_lines:
                    line.product_category = record.emdad_category
            else:
                pass
    def create_payment(self):
        payment = self.env['emdad.journal.entry']
        for record in self:
            data_to_copy = {
                'date' : record.payment_date,
                'journal' : record.payment_journal.id,
                'type' : 'out_payment',
                'journal_lines' : [
                    (0, 0, {
                        'account' : record.payment_journal.bank.id,
                        'debit' : record.amount_pay,
                        'partner' : record.vendor.id,
                    }),
                    (0, 0, {
                        'account' : record.payment_journal.expense.id,
                        'credit' : record.amount_pay,
                        'partner' : record.vendor.id,
                    })
                ]
            }
            payment_created = payment.create(data_to_copy)
            record.payment_status = 'paid'
    def create_bill_je(self):
        for record in self:
            journal_lines = []

            for line in record.procurement_lines:
                line_data = [
                    (0, 0, {
                        'account': line.expense_account.id,
                        'credit': line.after_tax,
                        'partner': line.vendor.id
                    }),
                    (0, 0, {
                        'account': line.tax_amount.tax_account.id,
                        'name': 'Tax for' + ' ' + line.related_procurement.name,
                        'debit': line.taxes,
                        'partner': line.vendor.id
                    }),
                    (0, 0, {
                        'account': line.location.related_warehouse.inventory_account.id,
                        'name': 'Buying '+ line.product_id.name + ' ' + line.related_procurement.name,
                        'debit': line.after_tax - line.taxes,
                        'partner': line.vendor.id
                    })              
                ]
                journal_lines.extend(line_data)

            journal_entry = self.env['emdad.journal.entry'].create({
                'date': record.effective_date,
                'related_entry': record.name,
                'type': 'bill',
                'journal_lines': journal_lines,
            })

            record.ensure_one()
            record.write({'related_bill': journal_entry.id})
            record.bill_status = 'created'


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
        total_amount = sum(self.procurement_lines.mapped('after_tax'))

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

    @api.depends('effective_date','status')
    def _get_name(self):
        for record in self:
            if record.effective_date:
                year = str(record.effective_date.year)
                month = str(record.effective_date.month).zfill(2)
                sequence = str(record.id).zfill(5)
                record.name = "PO" + '/' + year + '/' + month + '/' + sequence
            else:
                record.name="Draft Entry"

    @api.onchange('status','bill_status')
    def _get_stage(self):
        for record in self:
            if record.status == "pending":
                record.stages = "RFQ"

            elif record.status == "active" and record.bill_status == "not":
                record.stages = "PO"

            elif record.bill_status == "created" and record.status == "active":
                record.stages = "Billed"
            
            elif record.bill_status == "created" and record.status == "recieved":
                record.stages = "receipt"
            else:
                record.stages = "PO"

    @api.onchange('status','procurement_lines')
    def _get_backorder(self):  
        for record in self:
            procurement_lines =  self.env['emdad.line.procurement']

            subquery = procurement_lines.search([
                ('difference', '<',0 ),('related_procurement','=',record.id)
            ])
            subquery =len(subquery.read()) 
            print("********",subquery)
            if subquery > 0 :
                record.procurement_backorder = True
            else:
                record.procurement_backorder = False


    def create_back_order (self):
        for record in self:
            procurement_lines =  self.env['emdad.line.procurement']
            procurement_order = procurement_lines.search([
                    ('difference', '<',0 ),('related_procurement','=',record.id)
                ])
            procurement_order = procurement_order.read()
            for procurement in procurement_order:
                procurement_id = procurement['related_procurement'][0]
                procurement_query = self.env['emdad.procurement'].search([('id','=',procurement_id)])
                procurement_records = procurement_query.read()
                for record in procurement_records:

                    procurement_vals = {
                        'effective_date': record['effective_date'],
                        'operation_type' : record['operation_type'],
                        'vendors' : record['vendors'],
                        'vendor_phone' : record['vendor_phone'],
                        'procurement_lines' : [],
                        'process_type' : record['process_type'],
                        'payment_type' : record['payment_type'],
                        'distribution_type' : record['distribution_type'],
                        'total_before_discount' : record['total_before_discount'],
                        'total_discount' : record['total_discount'],
                        'total_amount' : record['total_amount'],
                        'status' : record['status'],
                        'published' : record['published'],
                        'exp_quote' : record['exp_quote'],
                        'single_location' : record['single_location'][0],
                        'is_multiple' : record['is_multiple'],
                        'all_info' : record['all_info'],
                        'in_recieve' : record['in_recieve'],
                        'recieved' : record['recieved'],
                        'related_bill' : record['related_bill'],
                        'bill_status' : record['bill_status'],
                        'amount_pay' : record['amount_pay'],
                        'payment_date' : record['payment_date'],
                        'payment_journal' : record['payment_journal'],
                        'payment_status' : record['payment_status'],
                        'credit_facility' : record['credit_facility'],
                        'credit_value' : record['credit_value'],
                        'credit_balance' : record['credit_balance'],
                        'stages' : record['stages'],
                        'procurement_backorder' : record['procurement_backorder'],
                        'display_name' : record['display_name'],
                        'create_uid' : record['create_uid'],
                        'create_date' : record['create_date']
                    }
                    new_procurement_record = self.env['emdad.procurement'].create(procurement_vals)
                    new_procurement_record_data = new_procurement_record.read()
                    new_procurement_record_id = new_procurement_record_data[0]['id']
                    print(new_procurement_record_id)

                    target_procurement_line_id = record['procurement_lines']
                    record_procurement_lines = self.env['emdad.line.procurement'].search([('id','=',target_procurement_line_id)])
                    record_procurement_lines_data = record_procurement_lines.read()
                    for line in record_procurement_lines_data:
                        qty = line['difference']
                        line['request_qty'] = qty
                        line['difference'] = 0
                        line['related_procurement'] = new_procurement_record_id
                        line['location'] = line['location'][0]
                        line['metric'] = line['metric'][0]
                        line['product_id'] = line['product_id'][0]
                        line['recieved_qty'] = 0
                        line['product_category'] = line['product_category'][0]
                        new_procurement_line = self.env['emdad.line.procurement'].create(line)
                        print(new_procurement_line)


class EmdadProcurementLines(models.Model):
    _name = "emdad.line.procurement"

    name = fields.Char(string="Procuement Reference ID")
    related_procurement = fields.Many2one("emdad.procurement", string="Related Order", ondelete="cascade", index=True)
    related_partner = fields.Many2one("emdad.contacts", related="related_procurement.vendor")
    barcode = fields.Char(string="Barcode", related="product_id.barcode")
    product_id = fields.Many2one("product.management", string="Product", ondelete="cascade")
    product_category = fields.Char(related="product_id.category.categ_fullname", string="Category")
    product_image = fields.Binary(string="Product Image", related="product_id.product_image")
    description = fields.Text(string="Description")
    expense_account = fields.Many2one("emdad.accounts", related="product_id.category.expense_account", string="Expense Account")
    attach = fields.Binary(string="Specifications")
    request_qty = fields.Float(string="Quantity")
    is_packge = fields.Boolean(string="Is Package")
    total_quantity = fields.Float(string="Total Quantity", compute="_cacl_qty")
    package_qty = fields.Float(string="Package Quantity")
    product_cost = fields.Float(string="Cost")
    tax_amount = fields.Many2one("emdad.tax", string="Tax")
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
    taxes = fields.Float(string="Taxes Amount")
    after_tax = fields.Float(string="Total Inc.")
    related_metric = fields.Many2one("product.metrics", related="product_id.related_metric", string="Related Metric")
    proc_status = fields.Selection([('pending', 'Pending'),('active','Active'), ('closed','Closed'), ('expired','Expired'), ('recieve', 'Receiving'), ('recieved','Recieved')], string="Quote Status", default="pending", related="related_procurement.status")
    product_category = fields.Many2one("product.emdad.category", string="Product Category")
    related_tender = fields.Many2one("emdad.tender", string="Related Tender")
    @api.depends('package_qty', 'request_qty')
    def _cacl_qty(self):
        for record in self:
            if record.is_packge == True:
                record.total_quantity = record.package_qty * record.request_qty
                if record.package_qty == 0:
                    record.package_qty = 1
                else:
                    pass
            else:
                record.total_quantity = 0
    @api.onchange('packaging')
    def _is_package(self):
        for record in self:
            if record.packaging:
                record.is_packge = True
    @api.onchange('product_id')
    def get_default_metric(self):
        for record in self:
            if not record.metric:
                record.metric = record.product_id.purchase_metric
            else:
                pass
    @api.onchange('product_id')
    def get_the_tax(self):
        for record in self:
            if record.product_id:
                record.tax_amount = record.product_id.purchase_tax
            else:
                pass
    @api.onchange('product_cost', 'final_total', 'tax_amount', 'after_tax', 'taxes')
    def calculate_tax(self):
        for record in self: 
            if record.tax_amount:
                tax_percentage = record.tax_amount.percentage
                taxes = record.final_total * (tax_percentage / 100)
                record.taxes = taxes
                record.after_tax = record.final_total + taxes
            else:
                record.after_tax = record.final_total
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

class EmdadTender(models.Model):
    _name="emdad.tender"

    name = fields.Char(string="Tender ID")
    exp_date = fields.Date(string="Expiary Date")
    status = fields.Selection([('draft','Darft RFP'), ('rfp','RFP'), ('po','Purchase Order'), ('bill','Billing'), ('recieve','Receiving')], string="Status")
    terms = fields.Html(string="Terms")
    procurements = fields.One2many("emdad.procurement", "related_tender", string="Procurements")
    products = fields.One2many("emdad.line.procurement", "related_tender",string="Products")
    vendors_list = fields.One2many("emdad.tender.vendor", "related_tender", string="Vendors List")

    def approve_tender(self):
        for record in self:
            record.status = 'rfp'
    
class EmdadTenderVendors(models.Model):
    _name="emdad.tender.vendor"

    name = fields.Char(string="Related Tender")
    related_tender = fields.Many2one("emdad.tender", string="Related Tender")
    vendor = fields.Many2one("emdad.contacts", string="Vendor")
    history_purchase = fields.Integer(string="History Purchase", related="vendor.procurement_transactions")
    vendor_category = fields.Many2one("product.emdad.category", string="Vendor Category")
    application_id = fields.Char(string="Application ID", compute="_create_application_id")
    offer = fields.Binary(string="Offer PDF")
    comments = fields.Text(string="Comments")
    apply_date = fields.Date(string="Apply Date")

    @api.onchange('related_tender')
    def _create_application_id(self):
        for record in self:
            if record.related_tender:
                tender = str(record.related_tender.name)
                app_id = str(record.id)
                record.application_id = 'TNDR' + tender + app_id
            else:
                record.application_id = 'Not Defiend'
    @api.onchange('vendor')
    def assign_vendor_category(self):
        for record in self:
            if record.vendor:
                record.vendor_category = record.vendor.category.id
            else:
                pass
    
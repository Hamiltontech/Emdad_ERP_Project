from emdad import models, fields, api
from emdad.exceptions import ValidationError

class EmdadCOA(models.Model):
    _name="emdad.accounts"

    name = fields.Char(string="Account Name", compute="_get_name")
    account = fields.Char(string="Account")
    code_type = fields.Selection([('assets','Assets'), ('libailities','Libailities'),('equity','Equity'),('income','Income'),('expenses','Expenses'),('other','Other')], related="account_type.code_type")
    code = fields.Char(string="Code", unique=True, required=True)
    parent_account = fields.Many2one("emdad.accounts", string="Parent Account")
    account_type = fields.Many2one("emdad.accounts.type", string="Account Type")
    je_lines = fields.One2many("emdad.journal.line", "account", string="JE Lines")
    description = fields.Text(string="Account Description")
    total_debit = fields.Float(string="Total Debit", compute="_get_total_debit")
    total_credit = fields.Float(string="Total Credit", compute="_get_total_credit")
    balance = fields.Float(string="Balance", compute="_get_balance")
    @api.constrains("code", "account_type", "code_type")
    def _check_unique_code(self):
        for record in self:
            if record.code and record.account_type and record.code_type:
                domain = [
                    ("code", "=", record.code),
                    ("account_type", "=", record.account_type.id),
                    ("code_type", "=", record.code_type),
                ]
                count = self.search_count(domain)
                if count > 1:
                    raise ValidationError("The code must be unique within the same account type and code type.")

    @api.onchange('parent_account')
    def _onchange_parent_account(self):
        """
        Replicate the unique code to child accounts.
        """
        if self.parent_account and self.parent_account.code:
            self.code = self.parent_account.code

    @api.onchange('code_type')
    def _onchange_account_type(self):
        """
        Generate suggested code based on the selected account type.
        """
        if self.code_type:
            if self.code_type == "assets":
                self.code = "10000"
            elif self.code_type == "libailities":
                self.code = "60000"
            elif self.code_type == "income":
                self.code = "40000"
    @api.depends('je_lines.debit')
    def _get_total_debit(self):
        for record in self:
            if record.je_lines:
                record.total_debit = sum(line.debit for line in record.je_lines)
            else:
                record.total_debit = 0
    @api.depends('je_lines.credit')
    def _get_total_credit(self):
        for record in self:
            if record.je_lines:
                record.total_credit = sum(line.credit for line in record.je_lines)
            else:
                record.total_credit = 0
    @api.depends('total_credit', 'total_debit')
    def _get_balance(self):
        for record in self:
            record.balance = record.total_debit - record.total_credit

    @api.depends('account', 'code')
    def _get_name(self):
        for record in self:
            if record.account and record.code:
                record.name = str(record.code) + ' ' + str(record.account)
            else:
                record.name = "Name Not Defined"
class EmdadCOAType(models.Model):
    _name="emdad.accounts.type"

    name = fields.Char(string="Account Type", compute="_generate_name")
    code_name = fields.Char(string="Group Name")
    code_type = fields.Selection([('assets','Assets'), ('libailities','Libailities'),('equity','Equity'),('income','Income'),('expenses','Expenses'),('other','Other')])
    description = fields.Text(string="Description")
    accounts = fields.One2many("emdad.accounts", "account_type", string="Related Accounts")

    @api.depends('code_name', 'code_type')
    def _generate_name(self):
        for record in self:
            if record.code_name and record.code_type:
                record.name = str(record.code_type.upper()) + '/' + str(record.code_name)
            else:
                record.name = 'Assign Type & Name'

class EmdadJournals(models.Model):
    _name="emdad.accounts.journal"

    name = fields.Char(string="Journal Name")
    journal_type = fields.Selection([('sales','Sales & Income'),('billing','Purchases'),('cash','Cash'),('bank','Bank'),('hr','Human Resources'),('other','Other')], string="Journal Type")
    income = fields.Many2one("emdad.accounts", string="Income Account")
    expense = fields.Many2one("emdad.accounts", string="Expense Account")
    short_code = fields.Char(string="Short Code")
    cash = fields.Many2one("emdad.accounts", string="Cash Account")
    bank = fields.Many2one("emdad.accounts", string="Bank Account")
    je = fields.One2many("emdad.journal.entry", "journal", string="Journal Entries")
    journal_icon = fields.Binary(string="Image")
    balance_bank = fields.Float(string="Bank Balance", related="bank.balance")
    balance_cash = fields.Float(string="Cash Balance", related="cash.balance")
    # balance = fields.Float(string="Balance", compute="_get_total_amount")

    # @api.depends('je.total_debit', 'je.total_credit')
    # def _get_total_amount(self):
    #     for record in self:
    #         if record.je:
    #             total_debit_je = sum(line.total_debit for line in record.je)
    #             total_credit_je = sum(line.total_credit for line in record.je)
    #             record.balance = total_debit_je - total_credit_je
    #         else:
    #             record.balance = 0
class EmdadJE(models.Model):
    _name="emdad.journal.entry"

    name = fields.Char(string="Journal Entry ID", compute="_get_name")
    je_status = fields.Selection([('draft','Draft'), ('approved','Approved'),('cancelled','Cancelled')], string="Status", default="draft")
    reference = fields.Char(String="Reference")
    date = fields.Date(string="Date")
    journal = fields.Many2one("emdad.accounts.journal", string="Journal")
    type = fields.Selection([('invoice','Invoice'), ('bill','Bill'),('refund','Refund'), ('credit','Credit'),('out_payment','Vendor Payment'),('in_payment','Customer Payment')], string="Transaction Type")
    journal_lines = fields.One2many("emdad.journal.line", "related_je", string="Journal Lines")
    total_debit = fields.Float(string="Total Debit", compute="_get_debit")
    total_credit = fields.Float(string="Total Credit", compute="_get_credit")
 

    @api.depends('journal','type','date','je_status')
    def _get_name(self):
        for record in self:
            if record.journal and record.type and record.date:
                shortname = str(record.journal.short_code)
                type =str(record.type)
                year = str(record.date.year)
                month = str(record.date.month).zfill(2)
                sequence = str(record.id).zfill(5)
                record.name = shortname.upper() + '/' + type.upper() + '/' + year + '/' + month + '/' + sequence
            else:
                record.name="Draft Entry"

    @api.model
    def create(self,vals):
        # print("***********",vals)
        total_debit = 0
        total_credit = 0
        # print("//////////////////",vals.get("journal_lines", []))
        for line in vals.get("journal_lines", []):
            # print(line)
            total_debit += line[2].get("debit", 0)
            total_credit += line[2].get("credit", 0)
        if total_debit != total_credit:
            # print("--------------",total_debit,total_credit)
            raise ValidationError('Debit & Credit not balanced')

        return super(EmdadJE, self).create(vals)
    @api.depends('journal_lines.debit')
    def _get_debit(self):
        for record in self:
            record.total_debit = sum(line.debit for line in record.journal_lines)
    
    @api.depends('journal_lines.credit')
    def _get_credit(self):
        for record in self:
            record.total_credit = sum(line.credit for line in record.journal_lines)

class EmdadJELine(models.Model):
    _name="emdad.journal.line"

    name = fields.Char(string="Description")
    related_je = fields.Many2one("emdad.journal.entry", string="Related JE")
    journal = fields.Many2one("emdad.accounts.journal", related="related_je.journal", string="Related Journal")
    account = fields.Many2one("emdad.accounts", string="Account")
    credit = fields.Float(string="Credit")
    debit = fields.Float(string="Debit")
    date = fields.Date(string="Date")
    partner = fields.Many2one("emdad.contacts", string="Partner")

class EmdadInvoice(models.Model):
    _name="emdad.invoice"

    name = fields.Char(string="Invoice ID")
    date = fields.Date(string="Issue Date")
    accounting_date = fields.Date(string="Accounting Date")
    invoice_lines = fields.One2many("emdad.invoice.lines", "related_invoice", string="Invoice Lines")

class EmdadInvoiceLines(models.Model):
    _name="emdad.invoice.lines"

    name = fields.Char(string="Line ID")
    related_invoice = fields.Many2one("emdad.invoice", string="Related Invoice")
    product_id = fields.Many2one("product.management", string="Product")
    income_account = fields.Many2one("emdad.accounts")
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    discount = fields.Float(string="Discount %")
    total = fields.Float(string="Total", readonly=True)
    final_total = fields.Float(string="Total", compute="_get_final_total")

    @api.depends('quantity', 'unit_price', 'discount')
    def _get_final_total(self):
        for record in self:
            if record.discount and record.quantity and record.unit_price:
                total_amount = record.quantity * record.unit_price
                discount_amount = (record.discount / 100) * total
                record.final_total = total_amount - discount_amount
            elif record.discount and record.quantity and record.unit_price:  # Add the missing colon here
                record.total = record.quantity * record.unit_price
                record.final_total = record.total
            else:
                record.total = 0
                record.final_total = 0

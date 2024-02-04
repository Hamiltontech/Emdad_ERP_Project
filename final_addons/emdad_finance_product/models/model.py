from emdad import models, api, fields


class ProductFinance(models.Model):
    _inherit="product.emdad.category"

    income_account = fields.Many2one("emdad.accounts")
    expense_account = fields.Many2one("emdad.accounts")
    invoice_journal = fields.Many2one("emdad.accounts.journal", string="Invoice Journal")
    expense_journal = fields.Many2one("emdad.accounts.journal", string="Expense Journal")

class ProductTax(models.Model):
    _inherit="product.management"

    sales_tax = fields.Many2one("emdad.tax", string="Sales Tax")
    purchase_tax = fields.Many2one("emdad.tax", string="Purchase Tax")

class InventoryFinance(models.Model):
    _inherit="emdad.warehouse"

    inventory_journal = fields.Many2one("emdad.accounts.journal", string="Inventory Journal")
    inventory_account = fields.Many2one("emdad.accounts", string="Inventory Account")
    total_value = fields.Float(string="Inventory Value", related="inventory_account.balance")


# class EmdadInvoice(models.Model):
#     _name="emdad.invoice"

#     name = fields.Char(string="Invoice ID")
#     date = fields.Date(string="Issue Date")
#     accounting_date = fields.Date(string="Accounting Date")
#     invoice_lines = fields.One2many("emdad.invoice.lines", "related_invoice", string="Invoice Lines")


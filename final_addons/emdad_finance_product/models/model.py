from emdad import models, api, fields


class ProductFinance(models.Model):
    _inherit="product.emdad.category"

    income_account = fields.Many2one("emdad.accounts")
    expense_account = fields.Many2one("emdad.accounts")
# Part of emdad. See LICENSE file for full copyright and licensing details.

from emdad import models, fields


# We add a field on this model
class Unit(models.Model):
    _inherit = 'test.unit'

    second_name = fields.Char()

from emdad import fields, models, api

class Hello(models.Model):
    _name="res.hello"

    name = fields.Char(string="Hello")
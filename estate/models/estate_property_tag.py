from odoo import models, fields


class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tags"
    _order = "name"

    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name must be unique"),
    ]

    # -------------------------- Fields Declaration -----------------------------------
    name = fields.Char(required=True)
    color = fields.Integer("Color Index")

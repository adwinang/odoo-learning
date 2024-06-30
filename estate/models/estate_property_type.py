from odoo import models, fields


class PropertyTypeModel(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Types"
    _order = "name"

    # -------------------------- Fields Declaration -----------------------------------
    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Sequence", default=10, help="Used to order types. Lower is better")

    # ------------------------- Relations ----------------------------------------------
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")

    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer")
    offer_ids = fields.Many2many("estate.property.offer", string="Offers", compute="_compute_offer")

    # ----------------------- Internal Methods ----------------------------------------
    def _compute_offer(self):
        data = self.env["estate.property.offer"].read_group(
            [("property_id.state", "!=", "canceled"), ("property_type_id", "!=", False)],
            ["ids:array_agg(id)", "property_type_id"],
            ["property_type_id"],
        )
        mapped_count = {d["property_type_id"][0]: d["property_type_id_count"] for d in data}
        mapped_ids = {d["property_type_id"][0]: d["ids"] for d in data}
        for prop_type in self:
            prop_type.offer_count = mapped_count.get(prop_type.id, 0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])

    # ---------------------------------------- Action Methods -------------------------------------

    def action_view_offers(self):
        res = self.env.ref("estate.estate_property_offer_action").read()[0]
        res["domain"] = [("id", "in", self.offer_ids.ids)]
        return res

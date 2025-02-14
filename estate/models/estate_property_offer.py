from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offers'
    _order = "price DESC"

    _sql_constraints = [
        ("positive_price", "CHECK(price>=0)", "Offer price has to be positive")
    ]

    # --------------------------- Fields Declaration -----------------------------
    price = fields.Float(string="Price")
    validity = fields.Integer("Validity (days)", default=7)
    date_deadline = fields.Date("Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    # ------------------------------- Relations -----------------------------------
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    property_type_id = fields.Many2one('estate.property.type', string="Property Type",
                                       related="property_id.property_type_id", store=True)

    # ------------------------Special ---------------------------------------------
    state = fields.Selection(string="Status", copy=False, selection=[('accepted', 'Accepted'), ('refused', 'Refused')])

    # -------------------------- Compute and Inverse -------------------------------
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - date).days

    # ---------------------- Action ------------------------------------------
    def action_accept(self):
        if "accepted" in self.mapped("property_id.offer_ids.state"):
            raise UserError("An offer has already been accepted")
        self.write({"state": "accepted"})
        return self.mapped("property_id").write({
            "state": "offer_accepted",
            "selling_price": self.price,
            "buyer_id": self.partner_id.id,
        })

    def action_refuse(self):
        return self.write({"state": "refused"})

    # ------------------- Constraints -------------------------------------------------

    # ------------------------ CRUD Methods -------------------------------------

    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            # We check if the offer is higher than the existing offers
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"
        return super().create(vals)

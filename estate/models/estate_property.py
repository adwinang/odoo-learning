from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_compare, float_is_zero


class PropertyModel(models.Model):
    _name = "estate.property"
    _description = "Estate Properties"
    _order = "id DESC"

    # ----------------------- SQL Constraints ---------------------------------------
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price>=0)", "Expected price has to be positive"),
        ("check_selling_price", "CHECK(selling_price>=0)", "Selling price has to be positive"),
    ]

    # -------------------------- Default Methods --------------------------------------

    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)

    # -------------------------- Fields Declaration -----------------------------------

    # id, create_date, create_uid, write_date, write_uid
    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Char("Available From", copy=False,
                                    default=lambda self: self._default_date_availability())
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ('N', 'North'),
            ('S', 'South'),
            ('E', 'East'),
            ('W', 'West')],
    )
    total_area = fields.Integer("Total Area (sqm)", compute="_compute_total_area")
    best_price = fields.Float("Best Offer", compute="_compute_best_price")

    # Special
    active = fields.Boolean("Active", default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="new",
    )

    # Relations
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    salesperson_id = fields.Many2one('res.users', string='Salesperson', index=True, default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer', index=True, copy=False)
    tag_ids = fields.Many2many('estate.property.tag', string="Property Tag", index=True)
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    user_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)

    # --------------------------- Computed Methods --------------------

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for prop in self:
            prop.best_price = max(prop.offer_ids.mapped("price")) if prop.offer_ids else 0.0

    # ----------------------------------- Constrains and Onchange --------------------------------

    # Never use onchange to add business logic to your model.
    # They are not automatically triggered when creating a record programmatically
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "N"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains('expected_price', 'selling_price')
    def _check_price(self):
        for prop in self:
            if (
                    not float_is_zero(prop.selling_price, precision_rounding=0.01)
                    and float_compare(prop.selling_price, prop.expected_price * 90.0 / 100.0,
                                      precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )

    # --------------------------------- CRUD Methods -----------------------------------------
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise UserError("Only new and canceled properties can be deleted.")

    # ----------------------------------- Action Methods ------------------------------------------
    def action_sold(self):
        if "canceled" in self.mapped("state"):
            raise UserError("Canceled properties cannot be sold.")
        return self.write({"state": "sold"})

    def action_cancel(self):
        if "sold" in self.mapped("state"):
            raise UserError("Sold properties cannot be canceled.")
        return self.write({"state": "canceled"})

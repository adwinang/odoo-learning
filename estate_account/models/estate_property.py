from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        res = super().action_sold()
        journal = self.env["account.move"].with_context(default_move_type="out_invoice")._search_default_journal()
        for prop in self:
            self.env["account.move"].create({
                "partner_id": prop.buyer_id.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create({
                        "name": prop.name,
                        "quantity": 1.0,
                        "price_unit": prop.selling_price * 6.0 / 100.0,
                    }),
                    Command.create({
                        "name": "Administrative fees",
                        "quantity": 1.0,
                        "price_unit": 100.0,
                    }),

                ]
            })

        return res

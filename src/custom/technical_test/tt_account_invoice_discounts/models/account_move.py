# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    discount_policy_applied = fields.Boolean(
        string="Política de descuento aplicada",
        copy=False,
        default=False,
    )

    def action_post(self):
        for move in self:
            if move.move_type not in ("out_invoice", "out_refund"):
                continue

            if move.discount_policy_applied:
                continue

            partner = move.partner_id
            if not partner or not partner.customer_type:
                continue

            rule = self.env["account.discount.rule"].search(
                [
                    ("customer_type", "=", partner.customer_type),
                    ("company_id", "=", move.company_id.id),
                ],
                limit=1,
            )

            if not rule:
                continue

            for line in move.invoice_line_ids:
                if line.display_type != 'product':
                    continue
                if line.discount:
                    continue  # respetando el descuento manual
                line.discount = rule.discount_percent

            move.discount_policy_applied = True

        return super().action_post()
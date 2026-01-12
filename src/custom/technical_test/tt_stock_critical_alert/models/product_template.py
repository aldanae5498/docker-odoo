# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_min_qty = fields.Float(
        string="Stock mínimo",
        help="Cantidad mínima permitida antes de generar alerta",
    )

    critical_alert_active = fields.Boolean(
        string="Alerta crítica activa",
        default=False,
        copy=False,
    )

    def action_check_stock_critical(self):
        """
        Detecta productos con stock por debajo del mínimo
        y crea una alerta.
        """
        for product in self:
            if product.stock_min_qty <= 0:
                continue

            if product.qty_available < product.stock_min_qty:
                if not product.critical_alert_active:
                    product.message_post(
                        body=(
                            f"Stock crítico: {product.qty_available} "
                            f"(mínimo: {product.stock_min_qty})"
                        )
                    )
                    product.critical_alert_active = True
            else:
                # El stock se recuperó
                product.critical_alert_active = False
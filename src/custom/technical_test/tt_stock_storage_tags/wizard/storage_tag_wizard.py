# -*- coding: utf-8 -*-

from odoo import fields, models

class StockStorageTagWizard(models.TransientModel):
    _name = "stock.storage.tag.wizard"
    _description = "Asignar etiquetas de almacenamiento"

    product_tmpl_ids = fields.Many2many("product.template", string="Productos", required=True)
    tag_ids = fields.Many2many("stock.storage.tag", string="Etiquetas")

    def action_apply(self):
        self.ensure_one()
        # Reemplaza etiquetas en todos los productos seleccionados
        for p in self.product_tmpl_ids:
            p.storage_tag_ids = [(6, 0, self.tag_ids.ids)]
        return {"type": "ir.actions.act_window_close"}

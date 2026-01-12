# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    storage_tag_ids = fields.Many2many(
        "stock.storage.tag",
        "product_template_stock_storage_tag_rel",
        "product_tmpl_id",
        "tag_id",
        string="Etiquetas de almacenamiento",
    )

    def action_open_storage_tag_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Asignar etiquetas",
            "res_model": "stock.storage.tag.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                'default_product_tmpl_ids': [(6, 0, [self.id])],
                'default_tag_ids': [(6, 0, self.storage_tag_ids.ids)]
            },
        }    
# -*- coding: utf-8 -*-

from odoo.tests.common import SavepointCase

class TestStorageTags(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tag = cls.env["stock.storage.tag"]
        cls.ProductT = cls.env["product.template"]

    def test_create_and_assign_tag(self):
        tag = self.Tag.create({"name": "Frágil", "color": 2, "description": "Manipular con cuidado"})
        product = self.ProductT.create({"name": "Producto X", "type": "product"})

        product.storage_tag_ids = [(4, tag.id)]
        self.assertIn(tag, product.storage_tag_ids)

    def test_kanban_action_group_by(self):
        action = self.env.ref("tt_stock_storage_tags.action_products_by_storage_tags").read()[0]
        ctx = action.get("context", {})
        # context puede venir como str o dict según Odoo; normalizamos:
        if isinstance(ctx, str):
            self.assertIn("group_by", ctx)
            self.assertIn("storage_tag_ids", ctx)
        else:
            self.assertEqual(ctx.get("group_by"), "storage_tag_ids")
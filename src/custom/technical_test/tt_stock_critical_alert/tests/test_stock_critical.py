# -*- coding: utf-8 -*-

from odoo.tests.common import SavepointCase

class TestStockCritical(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.template"].create({
            "name": "Producto prueba",
            "type": "product",
            "stock_min_qty": 10,
        })

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def test_stock_critical_alert(self):
        # Forzar stock bajo
        self.env["stock.quant"]._update_available_quantity(
            self.product.product_variant_id,
            self.stock_location,
            5,
        )

        self.product.action_check_stock_critical()

        self.assertTrue(self.product.critical_alert_active)
        self.assertEqual(len(self.product.message_ids), 1)

        # Ejecutar otra vez: NO debe duplicar
        self.product.action_check_stock_critical()
        self.assertEqual(len(self.product.message_ids), 1)

        # Recuperar stock
        self.env["stock.quant"]._update_available_quantity(
            self.product.product_variant_id,
            self.stock_location,
            10,
        )

        self.product.action_check_stock_critical()
        self.assertFalse(self.product.critical_alert_active)
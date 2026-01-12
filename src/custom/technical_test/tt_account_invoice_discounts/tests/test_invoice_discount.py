# -*- coding: utf-8 -*-

from odoo.tests.common import SavepointCase

class TestInvoiceDiscount(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({
            "name": "Cliente VIP",
            "customer_type": "vip",
        })

        cls.product = cls.env["product.product"].create({
            "name": "Producto prueba",
            "list_price": 100,
        })

        cls.rule = cls.env["account.discount.rule"].create({
            "name": "Descuento VIP",
            "customer_type": "vip",
            "discount_percent": 10,
        })

        cls.invoice = cls.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": cls.partner.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": cls.product.id,
                "quantity": 1,
                "price_unit": 100,
            })],
        })

    def test_discount_applied(self):
        self.invoice.action_post()
        line = self.invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 10)

    def test_no_duplicate_discount(self):
        self.invoice.action_post()
        self.invoice.action_post()
        line = self.invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 10)

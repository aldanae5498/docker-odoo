from odoo.tests.common import SavepointCase
from odoo import fields

class TestFinancialKpi(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.journal = cls.env["account.journal"].create({
            "name": "Test Journal",
            "code": "TST",
            "type": "general",
            "company_id": cls.company.id,
        })

        cls.acc_bank = cls.env["account.account"].create({
            "name": "Banco Test",
            "code": "1010",
            "account_type": "asset_current",
            "company_id": cls.company.id,
            "reconcile": False,
        })

        cls.acc_income = cls.env["account.account"].create({
            "name": "Ventas Test",
            "code": "4000",
            "account_type": "income",
            "company_id": cls.company.id,
            "reconcile": False,
        })

        cls.acc_cogs = cls.env["account.account"].create({
            "name": "Costo de Ventas Test",
            "code": "5000",
            "account_type": "expense",
            "company_id": cls.company.id,
            "reconcile": False,
        })

        cls.kpi = cls.env["account.financial.kpi"].create({
            "name": "Margen Bruto (%)",
            "company_id": cls.company.id,
            "formula": "(acc('4000') - acc('5000')) / acc('4000') * 100",
            "threshold_warning": 40,   # verde si >= 40
            "threshold_critical": 20,  # amarillo si >= 20, rojo si < 20
        })

    def _post_move(self, lines):
        move = self.env["account.move"].create({
            "move_type": "entry",
            "journal_id": self.journal.id,
            "date": fields.Date.today(),
            "line_ids": [(0, 0, l) for l in lines],
        })
        move.action_post()
        return move

    def test_kpi_calculation_and_state(self):
        # Ingreso 1000: Dr Banco 1000 / Cr Ventas 1000
        self._post_move([
            {"account_id": self.acc_bank.id, "debit": 1000.0, "credit": 0.0, "name": "Banco"},
            {"account_id": self.acc_income.id, "debit": 0.0, "credit": 1000.0, "name": "Ventas"},
        ])

        # Costo 700: Dr COGS 700 / Cr Banco 700  => margen 30% (amarillo)
        self._post_move([
            {"account_id": self.acc_cogs.id, "debit": 700.0, "credit": 0.0, "name": "COGS"},
            {"account_id": self.acc_bank.id, "debit": 0.0, "credit": 700.0, "name": "Banco"},
        ])

        self.kpi.invalidate_cache()
        self.assertAlmostEqual(self.kpi.value, 30.0, places=2)
        self.assertEqual(self.kpi.state, "yellow")

        # Costo adicional 200 => costo total 900 => margen 10% (rojo)
        self._post_move([
            {"account_id": self.acc_cogs.id, "debit": 200.0, "credit": 0.0, "name": "COGS"},
            {"account_id": self.acc_bank.id, "debit": 0.0, "credit": 200.0, "name": "Banco"},
        ])

        self.kpi.invalidate_cache()
        self.assertAlmostEqual(self.kpi.value, 10.0, places=2)
        self.assertEqual(self.kpi.state, "red")

        # Ingreso adicional 1000 => ingresos 2000, costos 900 => margen 55% (verde)
        self._post_move([
            {"account_id": self.acc_bank.id, "debit": 1000.0, "credit": 0.0, "name": "Banco"},
            {"account_id": self.acc_income.id, "debit": 0.0, "credit": 1000.0, "name": "Ventas"},
        ])

        self.kpi.invalidate_cache()
        self.assertAlmostEqual(self.kpi.value, 55.0, places=2)
        self.assertEqual(self.kpi.state, "green")

    def test_dashboard_action_has_kanban(self):
        action = self.env.ref("tt_account_financial_kpi.action_account_financial_kpi_dashboard").read()[0]
        self.assertIn("kanban", action.get("view_mode", ""))

# -*- coding: utf-8 -*-

from odoo.tests.common import SavepointCase
from odoo import fields

class TestPayrollAutoBenefits(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.employee = cls.env["hr.employee"].create({
            "name": "Empleado Prueba",
            "company_id": cls.company.id,
        })

        cls.contract_type = cls.env["hr.contract.type"].create({
            "name": "Tiempo completo",
        })

        cls.contract = cls.env["hr.contract"].create({
            "name": "Contrato Prueba",
            "employee_id": cls.employee.id,
            "company_id": cls.company.id,
            "wage": 1000.0,
            "contract_type_id": cls.contract_type.id,
            "state": "open",
            "date_start": fields.Date.today(),
        })

        stype = cls.env["hr.payroll.structure.type"].search([], limit=1) or \
                cls.env["hr.payroll.structure.type"].create({"name": "Tipo Test"})
        cls.structure = cls.env["hr.payroll.structure"].search([("type_id", "=", stype.id)], limit=1) or \
                        cls.env["hr.payroll.structure"].create({"name": "Estructura Test", "code": "TST", "type_id": stype.id})

        cls.Rule = cls.env["tt.hr.benefit.rule"]

    def _create_payslip(self, contract):
        return self.env["hr.payslip"].create({
            "name": "Nómina Test",
            "employee_id": contract.employee_id.id,
            "contract_id": contract.id,
            "struct_id": self.structure.id,
            "company_id": self.company.id,
            "date_from": fields.Date.today().replace(day=1),
            "date_to": fields.Date.today(),
        })

    def test_payslip_with_benefits(self):
        self.Rule.create({
            "name": "Bono fijo",
            "company_id": self.company.id,
            "contract_type_id": self.contract_type.id,
            "benefit_code": "bonus",
            "amount_type": "fixed",
            "amount": 150.0,
        })
        self.Rule.create({
            "name": "Prestaciones 10%",
            "company_id": self.company.id,
            "contract_type_id": self.contract_type.id,
            "benefit_code": "severance",
            "amount_type": "percent",
            "amount": 10.0,
        })

        slip = self._create_payslip(self.contract)
        self.assertTrue(slip.benefits_applied)
        self.assertEqual(len(slip.benefit_line_ids), 2)

        amounts = sorted(slip.benefit_line_ids.mapped("amount"))
        self.assertEqual(amounts, sorted([150.0, 100.0]))

    def test_edge_case_contract_without_type(self):
        contract2 = self.env["hr.contract"].create({
            "name": "Contrato sin tipo",
            "employee_id": self.employee.id,
            "company_id": self.company.id,
            "wage": 900.0,
            "state": "open",
            "date_start": fields.Date.today(),
        })

        self.Rule.create({
            "name": "Bono tiempo completo",
            "company_id": self.company.id,
            "contract_type_id": self.contract_type.id,
            "benefit_code": "bonus",
            "amount_type": "fixed",
            "amount": 50.0,
        })

        slip = self._create_payslip(contract2)
        self.assertFalse(slip.benefits_applied)
        self.assertEqual(len(slip.benefit_line_ids), 0)
# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    benefit_line_ids = fields.One2many(
        "tt.hr.payslip.benefit.line",
        "slip_id",
        string="Beneficios aplicados",
        copy=False,
    )
    benefits_applied = fields.Boolean(string='Beneficio aplicado', copy=False, default=False)

    def _get_benefit_rules(self, contract):
        Rule = self.env["tt.hr.benefit.rule"]
        if not contract or not contract.contract_type_id:
            return Rule.browse()

        return Rule.search(
            [
                ("active", "=", True),
                ("company_id", "=", self.company_id.id),
                ("contract_type_id", "=", contract.contract_type_id.id),
            ],
            order="id asc",
        )

    def _compute_benefit_amount(self, rule, contract):
        wage = contract.wage or 0.0
        if rule.amount_type == "percent":
            return wage * (rule.amount / 100.0)
        return rule.amount

    def _apply_benefits_from_contract(self):
        for slip in self:
            slip.benefit_line_ids.unlink()
            slip.benefits_applied = False

            contract = slip.contract_id
            rules = slip._get_benefit_rules(contract)
            if not contract or not contract.contract_type_id or not rules:
                continue

            vals_list = []
            for rule in rules:
                vals_list.append({
                    "slip_id": slip.id,
                    "rule_id": rule.id,
                    "name": rule.name,
                    "benefit_code": rule.benefit_code,
                    "amount": slip._compute_benefit_amount(rule, contract),
                })

            if vals_list:
                self.env["tt.hr.payslip.benefit.line"].create(vals_list)
                slip.benefits_applied = True

    @api.model_create_multi
    def create(self, vals_list):
        slips = super().create(vals_list)
        slips._apply_benefits_from_contract()
        return slips

    def write(self, vals):
        res = super().write(vals)
        if any(k in vals for k in ("employee_id", "contract_id", "date_from", "date_to", "company_id")):
            self._apply_benefits_from_contract()
        return res

    def compute_sheet(self):
        res = super().compute_sheet()
        self._apply_benefits_from_contract()
        return res


class HrPayslipBenefitLine(models.Model):
    _name = "tt.hr.payslip.benefit.line"
    _description = "Línea de beneficio en nómina"
    _order = "id"

    slip_id = fields.Many2one("hr.payslip", required=True, ondelete="cascade")
    rule_id = fields.Many2one("tt.hr.benefit.rule", required=True)
    name = fields.Char(string='Nombre', required=True)
    benefit_code = fields.Selection(
        [
            ("vacation", "Vacaciones"),
            ("severance", "Prestaciones"),
            ("bonus", "Bono"),
            ("other", "Otro"),
        ],
        string='Beneficio',
        required=True,
    )
    amount = fields.Float(string='Monto', required=True)

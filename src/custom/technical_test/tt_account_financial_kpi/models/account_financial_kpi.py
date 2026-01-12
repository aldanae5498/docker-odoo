# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression

class AccountFinancialKpi(models.Model):
    _name = "account.financial.kpi"
    _description = "Indicador de Salud Financiera"
    _order = "name"

    name = fields.Char(string='Nombre', required=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
        string='Compañía'
    )

    formula = fields.Text(
        required=True,
        help=(
            "Expresión Python (modo eval). Funciones disponibles:\n"
            "- acc('4000')  -> saldo agregado de cuenta/código (ingresos positivos)\n"
            "- acc('4*')    -> prefijo (todas las cuentas que comienzan con 4)\n"
            "Además se puede usar: abs(), min(), max(), round().\n"
            "Ejemplo: (acc('4000') - acc('5000')) / acc('4000') * 100"
        ),
    )

    threshold_warning = fields.Float(string="Umbral advertencia")
    threshold_critical = fields.Float(string="Umbral crítico")

    value = fields.Float(string="Valor", compute="_compute_value")
    state = fields.Selection(
        [("green", "Verde"), ("yellow", "Amarillo"), ("red", "Rojo")],
        string="Estado",
        compute="_compute_state",
    )

    last_error = fields.Text(string="Último error", readonly=True, copy=False)

    # ---------------------------------------------------------
    # Cálculo principal
    # ---------------------------------------------------------
    @api.depends("formula", "company_id")
    def _compute_value(self):
        for rec in self:
            rec.last_error = False
            try:
                rec.value = rec._eval_formula()
            except Exception as e:
                # No reventar el tablero si una fórmula está mala.
                rec.value = 0.0
                rec.last_error = str(e)

    @api.depends("value", "threshold_warning", "threshold_critical")
    def _compute_state(self):
        for rec in self:
            w = rec.threshold_warning
            c = rec.threshold_critical

            # Si no se configuran umbrales, se considera OK.
            if not w and not c:
                rec.state = "green"
                continue

            # Regla flexible:
            # - si warning >= critical -> "más alto es mejor"
            # - si warning < critical  -> "más bajo es mejor"
            higher_is_better = (w >= c)

            if higher_is_better:
                if rec.value >= w:
                    rec.state = "green"
                elif rec.value >= c:
                    rec.state = "yellow"
                else:
                    rec.state = "red"
            else:
                if rec.value <= w:
                    rec.state = "green"
                elif rec.value <= c:
                    rec.state = "yellow"
                else:
                    rec.state = "red"

    # Helpers de fórmula
    def _eval_formula(self):
        self.ensure_one()

        # Contexto permitido para safe_eval (modo eval)
        safe_ctx = {
            "acc": self._acc,
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
        }
        # mode="eval" limita a expresiones
        return float(safe_eval(self.formula.strip(), safe_ctx, mode="eval"))

    def _acc(self, code):
        """
        Devuelve el monto agregado de cuentas por código o prefijo.

        - Soporta '5111001' y '5111*'
        - Usa debit / credit
        - Solo movimientos posteados
        """
        self.ensure_one()
        company = self.company_id

        Account = self.env["account.account"]
        MoveLine = self.env["account.move.line"]

        code = (code or "").strip()
        if not code:
            return 0.0

        # Dominio por código
        if code.endswith("*"):
            prefix = code[:-1]
            code_domain = [("code", "=like", prefix + "%")]
        else:
            code_domain = [("code", "=", code)]

        # Dominio por compañía
        # company_domain = expression.OR([
        #     [("company_id", "=", company.id)],
        #     [("company_ids", "in", [company.id])],
        # ])

        # accounts = Account.search(expression.AND([code_domain, company_domain]))
        accounts = Account.search(expression.AND([code_domain]))
        if not accounts:
            return 0.0

        # -----------------------------
        # Suma de movimientos
        # -----------------------------
        data = MoveLine.read_group(
            domain=[
                ("company_id", "=", company.id),
                ("parent_state", "=", "posted"),
                ("account_id", "in", accounts.ids),
            ],
            fields=["debit:sum", "credit:sum"],
            groupby=[],
        )

        debit = data[0].get("debit_sum", 0.0) if data else 0.0
        credit = data[0].get("credit_sum", 0.0) if data else 0.0

        # -----------------------------
        # Lógica contable real
        # -----------------------------
        # Si hay crédito y no débito → ingresos
        if credit and not debit:
            return credit

        # Si hay débito y no crédito → gastos / activos
        if debit and not credit:
            return debit

        # Mixto -> neto
        return debit - credit
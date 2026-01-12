{
    "name": "Nómina – Cálculo Automático de Beneficios",
    "version": "18.0.1.0.0",
    "category": "Payroll",
    "summary": "Beneficios automáticos en nómina según tipo de contrato",
    "depends": ["hr_payroll"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_benefit_rule_views.xml",
        "views/hr_payslip_views.xml",
    ],
    "installable": True,
    "application": False,
}

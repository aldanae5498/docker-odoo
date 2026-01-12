{
    "name": "Contabilidad – Indicadores de Salud Financiera (KPIs)",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Tablero de KPIs financieros con fórmulas y semáforos",
    "depends": ["account"],
    "data": [
        # Security:
        "security/ir.model.access.csv",
        # Views:
        "views/account_financial_kpi_views.xml",
    ],
    "installable": True,
    "application": False,
}
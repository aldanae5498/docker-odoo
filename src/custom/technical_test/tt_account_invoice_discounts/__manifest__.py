{
    "name": "Contabilidad – Políticas de Descuento en Facturas",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Descuentos automáticos en facturas según tipo de cliente",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/discount_rule_views.xml",
    ],
    "installable": True,
    "application": False,
}

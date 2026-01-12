{
    "name": "Stock crítico – Alertas automáticas",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "summary": "Alertas cuando el stock baja del mínimo",
    "depends": [
        "stock",
        "mail",
    ],
    "data": [
        # Views:
        "views/product_template_views.xml",
        # Data:
        "data/ir_cron.xml",
    ],
    "installable": True,
    "application": False,
}
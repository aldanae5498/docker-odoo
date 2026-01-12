{
    "name": "Inventario – Etiquetas Inteligentes de Almacenamiento",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "summary": "Etiquetas de almacenamiento para productos + kanban agrupado",
    "depends": ["stock"],
    "data": [
        # Security:
        "security/ir.model.access.csv",
        # Views:
        "views/stock_storage_tag_views.xml",
        "views/product_template_views.xml",
        # Wizard:
        "wizard/wizard_views.xml",
    ],
    "installable": True,
    "application": False,
}

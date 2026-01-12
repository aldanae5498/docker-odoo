# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError

HEX_RE = re.compile(r"^#([0-9a-fA-F]{6})$")

class StockStorageTag(models.Model):
    _name = "stock.storage.tag"
    _description = "Etiqueta de almacenamiento"
    _order = "name"

    name = fields.Char(string="Nombre", required=True)
    color = fields.Char(string="Color", default="#400040")
    description = fields.Text(string="Descripción")
    active = fields.Boolean(default=True)

    @api.constrains("color")
    def _check_color(self):
        for rec in self:
            if rec.color and not HEX_RE.match(rec.color):
                raise ValidationError("Color inválido. Use formato #RRGGBB (ej: #400040).")
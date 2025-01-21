from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    filter_group_id = fields.Many2one('ir.model.access',related="company_id.filter_group_id", readonly=False)

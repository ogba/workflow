from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    filter_group_id = fields.Many2one('ir.model.access', string='Filter')
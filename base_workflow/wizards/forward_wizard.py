from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.tools import float_repr, float_compare
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.tests.common import Form


class ForwardWizard(models.TransientModel):
    _name = "forward.wizard"
    _description = "Forward Wizard"

    user_ids = fields.Many2many('res.users',string="Forward Users")

    def action_confirm(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        records = self.env['workflow.approval.line'].browse(active_ids)
        records.with_context(user_ids=self.user_ids).action_request_forward()


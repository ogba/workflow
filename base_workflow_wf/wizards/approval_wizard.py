from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.tools import float_repr, float_compare
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.tests.common import Form


class ApprovalWizard(models.TransientModel):
    _name = "approval.wizard"
    _description = "Approval Wizard"

    reference = fields.Char('Request Reference', readonly=True)
    reason = fields.Text(required=True)
    model_name = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    status = fields.Selection([('approved', 'Approved'),
                               ('rejected', 'Rejected'), ('rmi', 'Request More Information'),
                               ('rfc', 'Return For Correction'), ('forward', 'Forward')],
                              "Approval Status")
    required_approval = fields.Boolean(help="Required select approval line")
    approval_line_id = fields.Many2one('workflow.approval.line')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    user_ids = fields.Many2many('res.users')

    def action_confirm(self):
        self.ensure_one()
        model_id = self.env['ir.model'].sudo().search([('model', '=', self.model_name)])
        workflow_id = self.env['res.workflow'].sudo().search([('model_id', '=', model_id.id)])
        request = self.env[self.model_name].browse(self.res_id)

        # Construct the comment body
        if self.user_ids:
            mentioned_users = ' '.join(['@%s' % user.name for user in self.user_ids])
            body = _(
                "The Request has been %s for this reason : %s\n"
                "%s"
            ) % (
                       dict(self._fields['status'].selection).get(self.status),
                       self.reason,
                       mentioned_users
                   )
        else:
            body = _('The Request has been %s for this reason :\n\n %s' % (
                dict(self._fields['status'].selection).get(self.status), self.reason))

        # Attachments should be posted in the message (not as a separate record)
        attachment_ids = self.attachment_ids.ids if self.attachment_ids else []

        # Post the comment with the attachment in the chatter
        request.message_post(
            body=body,
            subtype_xmlid='mail.mt_comment',
            partner_ids=self.user_ids.ids,
            attachment_ids=attachment_ids  # Attach the files directly to the comment
        )

        # If there are any attachments, update them to link them to the model and record
        if self.attachment_ids:
            self.attachment_ids.write({'res_model': self.model_name, 'res_id': self.res_id})

        # Handle the status changes and the workflow logic
        if self.status == 'approved':
            request.with_context(reason=self.reason,
                                 upload_attachment=True if self.attachment_ids else False).action_approval_next_approve()
        if self.status == 'rejected':
            request.call_function(request, request, workflow_id.reject_method_name.name)
            request.with_context(reason=self.reason).action_approval_next_reject()
        elif self.status == 'rfc':
            if self.required_approval:
                request.with_context(reason=self.reason, approval_line=self.approval_line_id).action_approval_next_rfc()
            else:
                request.action_remove_lines()
        elif self.status == 'rmi':
            partner_ids = self.user_ids.mapped('partner_id').ids
            request.message_subscribe(partner_ids=partner_ids)
            request.with_context(reason=self.reason, user_ids=self.user_ids.ids).action_approval_next_rmi()
        elif self.status == 'forward':
            request.with_context(reason=self.reason, user_ids=self.user_ids).action_approval_next_forward()


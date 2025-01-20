from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


# class AccountMooove(models.Model):
#     _name = 'account.move'
#     _inherit = ['account.move','workflow.approval']
#
#     def action_post(self):
#         res = super(AccountMooove, self).action_post()
#         self.action_submit()
#         return res

class WorkflowRequest(models.Model):
    _name = 'workflow.request'
    _inherit = ['mail.thread']
    _description = 'Workflow Request'
    _order = 'id desc'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(string='Reference', required=True, copy=False, default='New', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,tracking=True, default=_default_employee)
    user_id = fields.Many2one('res.users', string='User',related='employee_id.user_id',store=True)
    date = fields.Date(default=lambda self: fields.Date.context_today(self))
    description = fields.Html()
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    status = fields.Selection(
        [('draft', 'Draft'), ('pending', 'In progress'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')],
        "Approval Status",
        default='draft',
        readonly=True,
        Tracking=True,
        copy=False
    )

    def approve(self):
        self.status ='approved'

    def reject(self):
        self.status ='rejected'
    # Create a new view that inherits from the base view

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('workflow.request')
        return super().create(vals_list)


    def get_approval_current_user_data(self, user_field='user_id'):
        """
        :param user_field: string representing a `Many2one` field pointing at
        `res.users` model to be used to get all the user specific approvals.
        If the owner partner of the request has no user or is a non-it employee,
        we compute the user representing a user in the same division and is
        stored in field `responsible_division_member_user_id` to be sent off to meth
        `get_approval_current_user_data`.
        NOTE: This field is only populated if it needs to be to prevent
        performance degradation.
        :return: call super method
        """
        self.ensure_one()
        if not user_field:
            user_field = 'create_uid'
        return super(WorkflowRequest, self) \
            .get_approval_current_user_data(user_field)


    def action_approval_send_mail(self, action, line):
        """Override to add request details."""
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(request_name=self._description)
        ctx.update(request_number=self.name)
        ctx.update(request_date=self.create_date)
        ctx.update(request_state=self.approval_status)
        ctx.update(requester_name=self.employee_id.name)
        ctx.update(employee_pin=self.employee_id.pin)
        ctx.update(employee_mobile=self.employee_id.mobile_phone)
        portal_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        portal_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        ctx.update(access_link=portal_url)
        ctx.update(mail_signature="Human Resource Department")
        return super(WorkflowRequest, self.with_context(**ctx)) \
            .action_approval_send_mail(action, line)


    def action_notify_send_mail(self, line):
        """Override to add request details."""
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(request_name=self._description)
        ctx.update(request_number=self.name)
        ctx.update(request_date=self.create_date)
        ctx.update(request_state=dict(self._fields['approval_status'].selection).get(self.approval_status))
        ctx.update(requester_name=self.employee_id.name)
        ctx.update(employee_pin=self.employee_id.pin)
        ctx.update(employee_mobile=self.employee_id.mobile_phone)
        ctx.update(mail_signature="Human Resource Department")
        return super(WorkflowRequest, self.with_context(**ctx)) \
            .action_notify_send_mail(line)


    def action_create_notify_send_mail(self, template_id):
        """Override to add request details."""
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(request_name=self._description)
        ctx.update(request_number=self.name)
        ctx.update(request_date=self.create_date)
        ctx.update(request_state=dict(self._fields['approval_status'].selection).get(self.approval_status))
        ctx.update(requester_name=self.employee_id.name)
        ctx.update(employee_pin=self.employee_id.pin)
        ctx.update(employee_mobile=self.employee_id.mobile_phone)
        ctx.update(mail_signature="Human Resource Department")
        return super(WorkflowRequest, self.with_context(**ctx)) \
            .action_create_notify_send_mail(template_id)




# -*- coding: utf-8 -*-
"""Approval Models"""

import logging
from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, AccessError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import ast


LOGGER = logging.getLogger(__name__)


class WorkflowApproval(models.AbstractModel):
    """Approval Model.

    This is used to define a specific record approval workflow."""
    _inherit = 'mail.thread'

    approval_template_id = fields.Many2one('workflow.condition',
                                           "Workflow Condition",
                                           help="The Approval Condition",
                                           copy=False)
    workflow_template_id = fields.Many2one('res.workflow',
                                           "Workflow Template",
                                           related='approval_template_id.workflow_id',
                                           help="The Approval Workflow Template",
                                           store=True, copy=False)
    approval_template_line_ids = fields.One2many(
        related='approval_template_id.condition_step_ids'
    )
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
    approval_status = fields.Selection(
        [('draft', 'Draft'), ('pending', 'In progress'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')],
        "Approval Status",
        default='draft',
        readonly=True,
        Tracking=True,
        copy=False
    )
    approvals_todo = fields.Integer("Remaining Approvals",
                                    compute='_compute_approvals_number')
    approvals_done = fields.Integer("Completed Approvals",
                                    compute='_compute_approvals_number')
    approvals_count = fields.Integer("Total Approvals",
                                     compute='_compute_approvals_number')
    approval_line_ids = fields.One2many('workflow.approval.line',
                                        compute='_compute_approval_line_ids')
    approval_next_line_ids = fields.One2many('workflow.approval.line',
                                             compute='_compute_approval_line_ids',ondelete='cascade')

    def redraft_workflow_record(self):
        # remove wf approval line step and start from beginning
        for rec in self:
            self.env['workflow.approval.line'].sudo().search([('id','in',self.approval_line_ids.ids)]).unlink()
            rec.approval_status = 'draft'
        return True

    def call_function(self, model, record, function_name, parms=False):
        record_id = record.id
        # Retrieve the record
        record = model.browse(record_id)

        # Check if the function exists
        if hasattr(record, function_name):
            # Get the function object
            function = getattr(record, function_name)

            # Call the function
            if parms:
                parms_obj = ast.literal_eval(parms)
                result = function(parms_obj)
            else:
                result = function()

        else:
            raise Warning(_('The function' + '   ' + str(function_name) + '   ' + 'does not exist in the model'))

    def _compute_approvals_number(self):
        """Compute total, remaining, and completed approvals."""
        for record in self:
            approvals = self.env['workflow.approval.line'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
            ], order='sequence ASC')
            seqs = set(approvals.mapped('sequence'))
            _todo = set(
                approvals.filtered(lambda r: r.status == 'pending')
                .mapped('sequence')
            )
            _done = set(
                approvals.filtered(lambda r: r.status != 'pending')
                .mapped('sequence')
            )
            todo = len(_todo - _done)
            done = len(_done)
            total = len(seqs)
            record.approvals_todo = todo
            record.approvals_done = done
            record.approvals_count = total

    def _compute_approval_line_ids(self):
        """Compute authorization approval lines."""
        for record in self:
            approvals = self.env['workflow.approval.line'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
            ], order='sequence ASC')
            record.approval_line_ids = approvals
            record.approval_next_line_ids = approvals \
                .filtered(lambda r: r.can_approve)

    def get_allowed_users(self, check_stage_approval=False):
        """Compute allowed approval users to see this request.

        Used by inherited models to adjust access rights."""
        for rec in self:
            lines = self.env['workflow.approval.line'].search([
                ('res_model', '=', rec._name),
                ('res_id', '=', rec.id),
                ('status', '=', 'pending'),
            ])
            users = self.env['res.users']
            for line in lines:
                if check_stage_approval:
                    if line.with_context(no_check_user=True) \
                            .check_stage_approval(line):
                        users |= line.get_eligible_users()
                else:
                    users |= line.get_eligible_users()
            return users

    def get_approval_current_user_data(self, user_field='create_uid'):
        """Get current user from the record.

        Overridable by child models to use different fields."""
        self.ensure_one()
        if not user_field:
            user_field = 'create_uid'
        user = self[user_field]
        return user

    def action_submit(self):
        for record in self:
            template = self.env['res.workflow'].sudo().search(
                [('company_id', '=', record.company_id.id), ('model_id', '=', record._name)], limit=1)
            if template:
                if template.workflow_type == 'approval' and template.condition_ids:
                    # check domain of each stage
                    for line in template.condition_ids:
                        if line.model_domain and line.model_domain != '[]':
                            res = record.search(safe_eval(line.model_domain))

                            if record not in res:
                                continue
                        self.action_approval_create(line)
                        #check if any method on submission
                        for line in template.action_on_submit_name:
                            record.call_function(record,record,line.name)

                        self.write({'approval_status': 'pending'})
                else:
                    # self.action_create_notify_send_mail(template)
                    self.action_approval_approve()
            else:
                self.action_approval_approve()

    def action_approval_create(self, template=None):
        """Create approval lines from template.

        This should be called by children models to kick-off the approval
        mandate process."""
        for record in self:
            # check if there's lines already created
            # NOTE: That won't fix race condition issue (if any)
            lines = self.env['workflow.approval.line'].search([
                ('res_model', '=', self._name),
                ('res_id', '=', record.id),
            ])
            if lines:
                continue

            app_lines = []
            if not template:
                template = self.env['workflow.condition'] \
                    .search([
                    ('model_name', '=', record._name), ('company_id', '=', record.company_id.id)
                ], limit=1)
            if template:
                record.approval_template_id = template.id
                for line in template.condition_step_ids:
                    
                    app_line = self.env['workflow.approval.line'] \
                        .create({
                        'res_model': record._name,
                        'res_id': record.id,
                        'step_line_id': line.id,
                    })
                    app_line.get_eligible_users()
                    app_lines.append(app_line)
                # send the first notification after creation
                if app_lines:
                    
                    app_lines[0].action_send_mail()
            return app_lines



    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        access_recs = self.env['workflow.approval.line'].sudo().search(
            [('res_model', '=', self._name),('status','=','pending')],limit=1).filtered(lambda r: r.can_approve)
        if access_recs:
            for field in access_recs.step_line_id.required_field_ids:
                if view_type == 'form':
                    for node in arch.xpath("//field[@name='%s']" % field.name):
                        node.attrib['required'] = 'True'

        return arch, view

    def action_open_approvals(self):
        
        """Open approval lines of the current record."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Approvals"),
            'res_model': 'workflow.approval.line',
            'views':  [(self.env.ref('base_workflow_wf.workflow_approval_line_view_tree_grouped').id,'tree')],
            'domain': [('res_model', '=', self._name),
                       ('res_id', '=', self.id)],

        }

    def action_approval_next_approve(self):
        """Approve the next lines by the current user"""
        for record in self:
            record.approval_next_line_ids.action_approve()

    def action_approval_next_reject(self):
        """Reject the next lines by the current user"""
        for record in self:
            record.approval_next_line_ids.action_reject()

    def action_approval_next_rfc(self):
        """Request For Correction the next lines by the current user"""
        for record in self:
            record.approval_next_line_ids.action_request_correction()

    def action_remove_lines(self):
        """Request For Correction and no approved lines"""
        for record in self:
            approvals = self.env['workflow.approval.line'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id)])
            approvals.unlink()
        self.write({'approval_status': 'draft', 'approval_template_id': False})

    def action_approval_next_rmi(self):
        """Request More Information the next lines by the current user"""
        for record in self:
            record.approval_next_line_ids.action_request_rmi()

    def action_approval_next_forward(self):
        """Forward the next lines by the current user"""
        for record in self:
            record.approval_next_line_ids.action_request_forward()

    def action_approval_line_approve(self, line):
        """Signal line approval for children models use.

        To be implemented by inherited models."""
        for fun in line.step_line_id.method_action_ids.filtered(lambda x: x.type == 'approve'):
            cxt = {
                'object': self._name,
                'env': self.env,
                'record': self,
            }

            if fun.parameter:
                self.call_function(self, fun.name, fun.parameter)
            else:
                self.call_function(self,self,fun.name)


    def action_approval_line_reject(self, line):
        """Signal line rejection for children models use.

        To be implemented by inherited models."""
        for fun in line.step_line_id.method_action_ids.filtered(lambda x: x.type == 'reject'):
            cxt = {
                'object': self._name,
                'env': self.env,
                'record': self,
            }

            if fun.parameter:
                self.call_function(self, fun.name, fun.parameter)
            else:
                self.call_function(self, self, fun.name)
    def action_approval_line_request_correction(self, line):
        """Signal line Request For Correction for children models use.

        To be implemented by inherited models."""
        for method in line.step_line_id.method_action_ids.filtered(lambda x: x.type == 'rfc'):
            safe_eval(method.name)

    def action_approval_line_rmi(self, line):
        """Signal line forward for children models use.

        To be implemented by inherited models."""
        for method in line.step_line_id.method_action_ids.filtered(lambda x: x.type == 'rmi'):
            safe_eval(method.name)

    def action_approval_line_forward(self, line):
        """Signal line forward for children models use.

        To be implemented by inherited models."""
        for method in line.step_line_id.method_action_ids.filtered(lambda x: x.type == 'forward'):
            safe_eval(method.name)

    def action_approval_line_request_information(self, line):
        """Signal line Request More Information for children models use.

        To be implemented by inherited models."""
        pass

    def action_approval_approve(self):
        """Store overall approval status as approved."""
        self.write({'approval_status': 'approved'})

    def action_approval_reject(self):
        """Store overall approval status as rejected."""
        self.write({'approval_status': 'rejected'})

    def action_approval_wizard(self):
        """Store overall approval status as rejected."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_workflow_wf.approval_wizard_action")
        action['context'] = dict(self.env.context)
        action['context']['default_reference'] = self.name
        action['context']['default_model_name'] = self._name
        action['context']['default_res_id'] = self.id
        action['context']['default_status'] = 'approved'
        action['target'] = 'new'
        return action

    def action_reject_wizard(self):
        """Store overall approval status as rejected."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_workflow_wf.approval_wizard_action")
        action['context'] = dict(self.env.context)
        action['context']['default_reference'] = self.name
        action['context']['default_model_name'] = self._name
        action['context']['default_res_id'] = self.id
        action['context']['default_status'] = 'rejected'
        action['target'] = 'new'
        #execute the reject action in the workflow template
        return action

    def action_rfc_wizard(self):
        """Store overall approval status as Request For Correction."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_workflow_wf.approval_wizard_action")
        approvals = self.env['workflow.approval.line'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id), ('status', '=', 'approved')])
        action['context'] = dict(self.env.context)
        action['context']['default_reference'] = self.name
        action['context']['default_model_name'] = self._name
        action['context']['default_res_id'] = self.id
        action['context']['default_status'] = 'rfc'
        if approvals:
            action['context']['default_required_approval'] = True
        action['target'] = 'new'
        return action

    def action_rmi_wizard(self):
        """Store overall approval status as Request More Information."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_workflow_wf.approval_wizard_action")
        action['context'] = dict(self.env.context)
        action['context']['default_reference'] = self.name
        action['context']['default_model_name'] = self._name
        action['context']['default_res_id'] = self.id
        action['context']['default_status'] = 'rmi'
        action['target'] = 'new'
        return action

    def action_forward_wizard(self):
        """Store overall approval status as Forward."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_workflow_wf.approval_wizard_action")
        action['context'] = dict(self.env.context)
        action['context']['default_reference'] = self.name
        action['context']['default_model_name'] = self._name
        action['context']['default_res_id'] = self.id
        action['context']['default_status'] = 'forward'
        action['target'] = 'new'
        return action

    def action_approval_send_mail(self, action, line):
        """Send email to designated parties to notify them.

        This method provides a way to customize the email for inherited
        models using the following context keys:
        - mail_subject: change the mail subject to a different title.
        - mail_partner_to: add a single partner ID (or multiple separated by
                           commas) to the default partners recipients.
        - mail_cc: add a single email address (or multiple separated by
                   commas) to the default CC recipients.
        - mail_details: add a block of details (HTML) to the email.
        - mail_signature: modify the signature of the email footer.
        - mail_reminder: add "Reminder" string to the subject when set to
                         True."""
        self.ensure_one()
        ctx = dict(self.env.context)
        # pass record and line information using context to the email template
        ctx.update(record=self)
        ctx.update(line=line)
        ctx.update(mail_subject=("%s , %s has been %s") %
                                (self._description, self.name, line.status))
        ctx.update(mail_signature="IT Department")
        ctx.update(mail_cc='')
        eligible_users = line.get_eligible_users()
        if eligible_users:
            try:
                # Filter out False or None values before joining
                email_list = eligible_users.mapped('email')
                mail_to = ','.join([email for email in email_list if email]) if email_list else False

                if not mail_to:
                    raise ValueError("Please ensure that all eligible users have their email addresses set.")
            except ValueError as e:
                raise UserError(_("Error: %s") % str(e))
        else:
            raise UserError("Please ensure the workflow has been configured correctly in conditoin.")
        # Don't send notifications to no-users!!!
        if not mail_to:
            return False
        ctx.update(mail_to=mail_to)
        template = line.step_line_id.done_template_id or self.env.ref('base_workflow_wf.mail_workflow_approval_line_done')
        if action == 'waiting':
            ctx.update(mail_subject=("%s , %s is waiting for your "
                                     "approval") % (self._description, self.name))
            template = line.step_line_id.waiting_template_id or self.env.ref(
                'base_workflow_wf'
                '.mail_template_workflow_approval_line_waiting'
            )
            # record last notification date for reminders
            line.approval_start_time = fields.Datetime.now()
            sla_id = line.step_line_id.sla_id
            if sla_id:
                sla_time = relativedelta(days=sla_id.sla_value) if sla_id.period_type == 'day' else relativedelta(
                    hours=sla_id.sla_value)
                reminder_time = relativedelta(
                    days=sla_id.reminder_value) if sla_id.period_type == 'day' else relativedelta(
                    hours=sla_id.reminder_value)
                line.sla_due_datetime = fields.Datetime.now() + sla_time
                line.sla_reminder_datetime = fields.Datetime.now() + reminder_time
        # obtain link for the current record
        if not ctx.get('access_link') \
                and hasattr(self, '_notify_get_action_link'):
            ctx.update(access_link=self._notify_get_action_link('view'))
        return template.sudo().with_context(**ctx) \
            .send_mail(line.id, force_send=False)

    def action_notify_send_mail(self, line):
        """Send email to designated notify parties to notify them.

        This method provides a way to customize the email for inherited
        models using the following context keys:
        - mail_subject: change the mail subject to a different title.
        - mail_partner_to: add a single partner ID (or multiple separated by
                           commas) to the default partners recipients.
        - mail_cc: add a single email address (or multiple separated by
                   commas) to the default CC recipients.
        - mail_details: add a block of details (HTML) to the email.
        - mail_signature: modify the signature of the email footer.
        - mail_reminder: add "Reminder" string to the subject when set to
                         True."""
        self.ensure_one()
        ctx = dict(self.env.context)
        # pass record and line information using context to the email template
        ctx.update(record=self)
        ctx.update(line=line)
        ctx.update(mail_subject=("%s , %s has been %s") %
                                (self._description, self.name, line.status))
        ctx.update(mail_signature="IT Department")
        ctx.update(mail_cc='')
        notify_users = line.get_notify_users()
        mail_to = ','.join(notify_users.mapped('email')) if notify_users else False
        # Don't send notifications to no-users!!!
        if not mail_to:
            return False
        ctx.update(mail_to=mail_to)
        template = line.step_line_id.notify_template_id or self.env.ref(
            'base_workflow_wf.mail_workflow_approval_line_notify_users')
        # obtain link for the current record
        if not ctx.get('access_link') \
                and hasattr(self, '_notify_get_action_link'):
            ctx.update(access_link=self._notify_get_action_link('view'))
        return template.sudo().with_context(**ctx) \
            .send_mail(line.id, force_send=False)

    def get_user_hierarchy(self, hierarchy_level, user):
        employee_id = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        parents = self.env['hr.employee']
        parent_id = employee_id.parent_id
        level = 1
        while parent_id and level <= hierarchy_level:
            parents += parent_id
            parent_id = parent_id.parent_id
            level += 1
        return parents.mapped('user_id')

    def get_workflow_notification_users(self, workflow):
        """Get workflow user to Notification them."""
        self.ensure_one()
        result = []

        if workflow.workflow_type == 'notify':
            if workflow.workflow_notify_type == 'user':
                if not workflow.notify_user_ids:
                    raise UserError(_("No users selected for notification."))
                result = workflow.notify_user_ids

            elif workflow.workflow_notify_type == 'group':
                if not workflow.notify_group_ids:
                    raise UserError(_("No groups selected for notification."))
                result = workflow.notify_group_ids.mapped('users')

            elif workflow.workflow_notify_type == 'hierarchy':
                record = self.env[self._name].browse(self.id)
                user_data = record.get_approval_current_user_data()
                if not user_data:
                    raise UserError(_("No user data found for hierarchy notification."))
                result = record.get_user_hierarchy(workflow.notify_hierarchy_level, user_data)

            elif workflow.workflow_notify_type == 'department':
                record = self.env[self._name].browse(self.id)
                user_data = record.get_approval_current_user_data()
                if not user_data:
                    raise UserError(_("No user data found for department notification."))
                if not user_data.department_id:
                    raise UserError(_("No department assigned to the user."))
                if not user_data.department_id.manager_id or not user_data.department_id.manager_id.user_id:
                    raise UserError(_("No manager assigned to the department."))
                result.append(user_data.department_id.manager_id.user_id)

            elif workflow.workflow_notify_type == 'filter':
                if not workflow.notify_filter_group_id:
                    raise UserError(_("No filter group selected for notification."))
                result = workflow.notify_filter_group_id.get_filter_result()

        return result

    def action_create_notify_send_mail(self, template_id):
        """Send email to designated notify parties to create request them.

        This method provides a way to customize the email for inherited
        models using the following context keys:
        - mail_subject: change the mail subject to a different title.
        - mail_partner_to: add a single partner ID (or multiple separated by
                           commas) to the default partners recipients.
        - mail_cc: add a single email address (or multiple separated by
                   commas) to the default CC recipients.
        - mail_details: add a block of details (HTML) to the email.
        - mail_signature: modify the signature of the email footer.
        - mail_reminder: add "Reminder" string to the subject when set to
                         True."""
        self.ensure_one()
        ctx = dict(self.env.context)
        # pass record and line information using context to the email template
        ctx.update(record=self)
        mail_subject = _("%s , %s has been created") % (self._description, self.name)
        ctx.update(mail_signature="IT Department")
        ctx.update(mail_cc='')
        notify_users = self.get_workflow_notification_users(template_id)
        mail_to = ','.join(notify_users.mapped('email')) if notify_users else False
        # Don't send notifications to no-users!!!
        if not mail_to:
            return False
        ctx.update(mail_to=mail_to)
        template = template_id.notify_template_id or self.env.ref(
            'base_workflow_wf.mail_workflow_notification_create')
        vals = {
            'subject': mail_subject,
            'body_html': template.body_html,
            'email_from': self.env.user.email,
            'email_to': mail_to,
            'auto_delete': False,
            'model': self._name,
            'res_id': self.id,
        }
        return self.sudo().with_context(**ctx).env['mail.mail'].create(vals).send()

    def action_sla_escalation_send_mail(self, line, notify_users):
        """Send email to escalate parties to notify them.

        This method provides a way to customize the email for inherited
        models using the following context keys:
        - mail_subject: change the mail subject to a different title.
        - mail_partner_to: add a single partner ID (or multiple separated by
                           commas) to the default partners recipients.
        - mail_cc: add a single email address (or multiple separated by
                   commas) to the default CC recipients.
        - mail_details: add a block of details (HTML) to the email.
        - mail_signature: modify the signature of the email footer.
        - mail_reminder: add "Reminder" string to the subject when set to
                         True."""
        self.ensure_one()
        ctx = dict(self.env.context)
        # pass record and line information using context to the email template
        ctx.update(record=self)
        ctx.update(line=line)
        ctx.update(mail_subject=("%s , %s has been %s") %
                                (self._description, self.name, line.status))
        ctx.update(mail_signature="IT Department")
        ctx.update(mail_cc='')
        mail_to = ','.join(notify_users.mapped('email')) if notify_users else False
        # Don't send notifications to no-users!!!
        if not mail_to:
            return False
        ctx.update(mail_to=mail_to)
        template = line.step_line_id.notify_template_id or self.env.ref(
            'base_workflow_wf.mail_template_workflow_approval_sla_escalation')
        # obtain link for the current record
        if not ctx.get('access_link') \
                and hasattr(self, '_notify_get_action_link'):
            ctx.update(access_link=self._notify_get_action_link('view'))
        return template.sudo().with_context(**ctx) \
            .send_mail(line.id, force_send=False)


    def action_sla_reminder_send_mail(self, line):
        """Send reminder email to designated parties to notify them.

        This method provides a way to customize the email for inherited
        models using the following context keys:
        - mail_subject: change the mail subject to a different title.
        - mail_partner_to: add a single partner ID (or multiple separated by
                           commas) to the default partners recipients.
        - mail_cc: add a single email address (or multiple separated by
                   commas) to the default CC recipients.
        - mail_details: add a block of details (HTML) to the email.
        - mail_signature: modify the signature of the email footer.
        - mail_reminder: add "Reminder" string to the subject when set to
                         True."""
        self.ensure_one()
        ctx = dict(self.env.context)
        # pass record and line information using context to the email template
        ctx.update(record=self)
        ctx.update(line=line)
        ctx.update(mail_subject=("%s , %s has been %s") %
                                (self._description, self.name, line.status))
        ctx.update(mail_signature="IT Department")
        ctx.update(mail_cc='')
        eligible_users = line.get_eligible_users()
        mail_to = ','.join(eligible_users.mapped('email')) if eligible_users else False
        # Don't send notifications to no-users!!!
        if not mail_to:
            return False
        ctx.update(mail_to=mail_to)
        template = line.step_line_id.notify_template_id or self.env.ref(
            'base_workflow_wf.mail_template_workflow_approval_line_sla_reminder')
        # obtain link for the current record
        if not ctx.get('access_link') \
                and hasattr(self, '_notify_get_action_link'):
            ctx.update(access_link=self._notify_get_action_link('view'))
        return template.sudo().with_context(**ctx) \
            .send_mail(line.id, force_send=False)




class WorkflowApprovalLine(models.Model):
    """Approval Line Model.

    This is used to define a specific approval on a specific record."""
    _name = 'workflow.approval.line'
    _description = "Workflow Approval"
    _order = 'sequence'

    res_model = fields.Char("Model Name", required=True)
    res_model_id = fields.Many2one('ir.model', "Model",
                                   compute='_compute_model_id', store=True ,ondelete='cascade')
    res_id = fields.Integer("Resource ID", required=True)
    res_id_record_name = fields.Char("Record Name", compute='_compute_record_name',store=True)

    step_line_id = fields.Many2one(
        'workflow.condition.step',
        "Approval Step",
        required=True,
        index=True
    )
    condition_id = fields.Many2one(
        related='step_line_id.condition_id', readonly=True, store=True,
        index=True
    )
    workflow_id = fields.Many2one('res.workflow',
                                  "Workflow Template",
                                  related='step_line_id.workflow_id',
                                  help="The Approval Workflow Template",
                                  store=True, copy=False)
    category_id = fields.Many2one('workflow.category', string='Category',related='step_line_id.workflow_id.category_id',store=True)
    required = fields.Boolean(related='step_line_id.required',
                              store=True, index=True, readonly=True,
                              help="If not, only one approval per sequence is "
                                   "required.")
    required_attachment = fields.Boolean(related='step_line_id.required_attachment',
                                          readonly=True,
                                         help="If yes, not approved without upload attachment")

    required_attachment_message = fields.Text(related='step_line_id.required_attachment_message',
                                          readonly=True,
                                         )
    name = fields.Char(string='Step name',related='step_line_id.name', store=True,
                       readonly=True)
    sequence = fields.Integer(related='step_line_id.sequence',
                              store=True, index=True, readonly=True)
    user_id = fields.Many2one('res.users', "Approved By", index=True)
    approval_start_time = fields.Datetime(string='Start Time')
    approval_end_time = fields.Datetime("Approval Time", index=True)
    sla_due_datetime = fields.Datetime("SLA Due Date")
    sla_reminder_datetime = fields.Datetime("SLA Reminder Date")
    status = fields.Selection([('pending', 'Pending'),
                               ('approved', 'Approved'),
                               ('rejected', 'Rejected'), ('na', 'N/A')],
                              "Approval Status",
                              default='pending')
    can_approve = fields.Boolean("Can Approve?",
                                 compute='_compute_can_approve',
                                 default=False)
    eligible_user_ids = fields.Many2many('res.users', string="Eligible Users",
                                         compute='_compute_eligible_user_ids')
    notify_user_ids = fields.Many2many('res.users', 'approval_notify_users_rel', string="Notify Users",
                                       compute='_compute_notify_user_ids')
    forward_user_ids = fields.Many2many('res.users', 'approval_forward_users_rel', string="Forward Users")
    rmi_user_ids = fields.Many2many('res.users', 'approval_rmi_users_rel', string='Request More Information Users')
    delegated_user_ids = fields.Many2many('res.users', 'rel_workflow_delegated_user', string='Delegated Users',
                                          compute='_compute_delegated_user_ids',store=True)
    comment = fields.Char(string='Comments')



    @api.model
    def unlink(self):
        # Custom logic to delete related records
        self.search([]).unlink()
        return super(WorkflowApprovalLine, self).unlink()

    def open_request(self):
        self.ensure_one()
        record = self.env[self.res_model].browse(self.res_id)
        return {'type': 'ir.actions.act_window',
                'name':record._description,
                'res_model': self.res_model,
                'target': 'current',
                'view_mode': 'form',
                'domain': [],
                'res_id': self.res_id,
                }

    def _compute_delegated_user_ids(self):
        """Compute Delegated users for this line."""
        for record in self:
            record.delegated_user_ids = record.get_delegated_users()

    def get_delegated_users(self):
        """Get delegated users to approve/reject the current stage."""
        self.ensure_one()
        result = []
        record = self.env[self.res_model].browse(self.res_id)

        users = self.get_step_users()
        
        if not users:
            raise UserError(_("No users found for this step. Please check the workflow configuration."))

        if isinstance(users, list):  # Ensure users is a recordset
            users = self.env['res.users'].browse(users)

        delegates = self.env['workflow.delegate'].sudo().search(
            [('user_id', 'in', users.ids), ('date_from', '<=', fields.Date.today()),
            ('date_to', '>=', fields.Date.today()), ('company_id', '=', record.company_id.id)]
        )

        if not delegates:
            raise UserError(_("No delegated users found for this step."))

        result = delegates.mapped('replace_user_id')
        return result

    @api.depends('name','status')
    def _compute_record_name(self):
        """Compute the name of record in model"""

        for rec in self:

            model_id = rec.res_model_id
            res_id = rec.res_id
            record = rec.env[model_id.model].browse(res_id)
            try:
                rec.res_id_record_name = record.display_name
            except:
                rec_name_field = model_id._rec_name
                rec.res_id_record_name = record[rec_name_field]

    @api.depends('res_model')
    def _compute_model_id(self):
        """Compute model object from res_model field."""
        for record in self:
            record.res_model_id = self.env['ir.model'].search([
                ('model', '=', record.res_model)
            ], limit=1)


    def _compute_eligible_user_ids(self):
        """Compute eligible users for this line."""
        for record in self:
            record.eligible_user_ids = record.get_eligible_users()

    def _compute_notify_user_ids(self):
        """Compute notify users for this line."""
        for record in self:
            record.notify_user_ids = record.get_notify_users()

    def get_manager_user(self, employee_id):
        """Get manager of the employee."""
        self.ensure_one()
        if employee_id.parent_id:
            return employee_id.parent_id.user_id
        return False

    def get_eligible_users(self):
        """Get eligible users to approve/reject the current stage."""
        self.ensure_one()
        result = self.get_step_users()
        if self.forward_user_ids:
            result += self.forward_user_ids
        if self.delegated_user_ids:
            result += self.get_delegated_users()
        return result

    def get_step_users(self):
        """Get step users current stage."""
        self.ensure_one()
        temp_line = self.step_line_id
        result = []

        if temp_line.type == 'user':
            if temp_line.type_user_ids:
                result = temp_line.type_user_ids
               
            else:
                raise UserError(_("No users are assigned in the 'User' step. Please check the configuration."))

        elif temp_line.type == 'group':
            if temp_line.type_group_ids:
                result = temp_line.type_group_ids.mapped('users')
                
            if not result:
                raise UserError(_("No users found in the 'Group' step. Ensure the selected groups contain users."))

        elif temp_line.type == 'hierarchy':
            record = self.env[self.res_model].browse(self.res_id)
            user_data = record.get_approval_current_user_data()
            for level in range(temp_line.type_hierarchy_level):
                user_data = self.get_manager_user(user_data.employee_id)
                if not user_data:
                    raise UserError(_("No managers found in the 'Hierarchy' step. Please verify the employee hierarchy."))
                if user_data:
                    result.append(user_data)
            

        elif temp_line.type == 'department':
            record = self.env[self.res_model].browse(self.res_id)
            user_data = record.get_approval_current_user_data()
            if user_data.department_id.manager_id.user_id:
                result = user_data.department_id.manager_id.user_id
            if not result:
                raise UserError(_("No department manager found in the 'Department' step. Please check department assignments."))

        elif temp_line.type == 'filter':
            result = temp_line.filter_group_id.get_filter_result()
            if not result:
                raise UserError(_("No users match the criteria in the 'Filter' step. Adjust the filter settings."))
        
        return result

    def get_notify_users(self):
        """Get notify users to the current stage."""
        self.ensure_one()
        temp_line = self.step_line_id
        result = []
        if temp_line.notify_type == 'user' and temp_line.notify_user_ids:
            result = temp_line.notify_user_ids
        elif temp_line.notify_type == 'group' and temp_line.notify_group_ids:
            result = temp_line.notify_group_ids.mapped('users')
        elif temp_line.notify_type == 'hierarchy':
            record = self.env[self.res_model].browse(self.res_id)
            user_data = record.get_approval_current_user_data()
            for level in range(temp_line.notify_hierarchy_level):
                user_data = self.get_manager_user(user_data.employee_id)
                if user_data:
                    result.append(user_data)
        elif temp_line.notify_type == 'department':
            record = self.env[self.res_model].browse(self.res_id)
            user_data = record.get_approval_current_user_data()
            if user_data.department_id.manager_id.user_id:
                result.append(user_data.department_id.manager_id.user_id)
        elif temp_line.notify_type == 'filter':
            result = temp_line.notify_filter_group_id.get_filter_result()
        return result

    @api.model
    def check_stage_approval(self, line):
        """Check the ability to approve provided stage by current user."""
        # if this line has been already approved/rejected, don't repeat it
        if line.status != 'pending':
            return False

        # if the overall record has been recorded as approved/rejected
        # (this line is optional, and has been passed)
        record = self.env[line.res_model].browse(line.res_id)
        if record.approval_status not in ('draft', 'pending'):
            return False

        # if this line is not the current stage, or any previous stage
        # has already decided not in favor of the record
        lines = self.search([('res_id', '=', line.res_id),
                             ('res_model', '=', line.res_model)],
                            order='sequence ASC')
        seq = 1
        seq_approval = False
        for _line in lines:
            # any required stage before the current one will deem the
            # current one not ready
            if line.sequence > _line.sequence \
                    and _line.required \
                    and _line.status != 'approved':
                return False

            # any stage contains all optional lines but no single line
            # has been decided will deem the current stage not ready
            if seq < _line.sequence \
                    and seq < line.sequence \
                    and not seq_approval:
                return False

            # also, current sequence with a single line that has decided
            # will deem current stage irrelevant
            if seq < _line.sequence \
                    and not line.required \
                    and seq == line.sequence \
                    and seq_approval:
                return False

            seq = _line.sequence
            seq_approval = _line.status in ('approved', 'na')

        # check current user is one of eligible approval users
        if not self.env.context.get('no_check_user', False) \
                and self.env.user not in \
                line.get_eligible_users():
            return False

        return True

    @api.model
    def check_last_stage(self, line):
        """Check if the provided line is the last approval in the record."""
        lines = self.search([('res_id', '=', line.res_id),
                             ('res_model', '=', line.res_model),
                             ('sequence', '>=', line.sequence),
                             ('id', '!=', line.id)],
                            order='sequence ASC')
        for _line in lines:
            # if there's a stage in the same sequence but still required and
            # pending, the current one is not the last stage
            if line.sequence == _line.sequence \
                    and _line.required \
                    and _line.status == 'pending':
                return False

            # if there's another sequence after the current one, this isn't
            # the last stage
            if line.sequence < _line.sequence:
                return False

        return True

    def _compute_can_approve(self):
        """Compute the current stage ability to be approved/rejected."""
        for line in self:
            line.can_approve = self.check_stage_approval(line)

    def action_approve(self):
        """Switch this stage to approved status."""
        for line in self:
            if not line.can_approve and not (self.env.user.has_group('base_workflow_wf.group_workflow_user')):
                raise UserError(_("You can't approve the request at this "
                                  "stage."))

            if self.required_attachment and not self.env.context.get('upload_attachment', False):
                raise UserError(_(self.required_attachment_message))


            line.status = 'approved'
            line.comment = self.env.context.get('reason', False)
            line.user_id = self.env.user
            line.approval_end_time = fields.Datetime.now()
            line.action_na()
            record = self.env[line.res_model].browse(line.res_id)
            record.action_approval_line_approve(line)
            # only approval at the last stage will deem the overall approval
            # for the request as approved
            if self.check_last_stage(line):
                #last step
                #cal approve function
                record.call_function(record, record, self.workflow_id.approve_method_name.name)
                record.action_approval_approve()

            line.action_send_mail()

    def action_approve_multi(self):
        # self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        approvals = self.env['workflow.approval.line'].browse(active_ids)
        for approval in approvals.filtered(lambda x: x.status == 'pending'):
            approval.action_approve()

    def action_reject(self):
        """Switch this stage to rejected status."""
        for line in self:
            if not line.can_approve and not (self.env.user.has_group('base_workflow_wf.group_workflow_user')):
                raise UserError(_("You can't reject the request at this "
                                  "stage."))
            line.status = 'rejected'
            line.comment = self.env.context.get('reason', False)
            line.user_id = self.env.user
            line.approval_end_time = fields.Datetime.now()
            line.action_na()
            # any rejection at any stage will deem the request rejected
            record = self.env[line.res_model].browse(line.res_id)
            record.action_approval_line_reject(line)
            record.action_approval_reject()
            line.action_send_mail()

    def action_reject_multi(self):
        # self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        approvals = self.env['workflow.approval.line'].browse(active_ids)
        for approval in approvals.filtered(lambda x: x.status == 'pending'):
            approval.action_reject()

    def action_request_correction(self):
        """Switch this stage to Request For Correction status."""
        for line in self:
            if not line.can_approve:
                raise UserError(_("You can't Request For Correction the request at this "
                                  "stage."))
            line.comment = self.env.context.get('reason', False)
            correction_line = self.env.context.get('approval_line', False)
            line.user_id = self.env.user
            line.approval_end_time = fields.Datetime.now()
            record = self.env[line.res_model].browse(line.res_id)
            record.action_approval_line_request_correction(line)
            domain = [
                ('res_model', '=', line.res_model),
                ('res_id', '=', line.res_id),
                ('status', '=', 'approved'),
                ('sequence', '>=', correction_line.sequence)
            ]
            lines = self.search(domain)
            lines.write({'status': 'pending', 'user_id': False, 'approval_end_time': False})
            record._compute_approvals_number()

    def action_request_rmi(self):
        """Request More Information to line."""
        for line in self:
            if not line.can_approve:
                raise UserError(_("You can't Request More Information the request at this "
                                  "stage."))
            line.rmi_user_ids = self.env.context.get('user_ids', False)
            line.comment = self.env.context.get('reason', False)
            record = self.env[line.res_model].browse(line.res_id)
            record.action_approval_line_rmi(line)

    def action_request_forward(self):
        """Add Forward to line."""
        for line in self:
            if not line.can_approve and not (self.env.user.has_group('base_workflow_wf.group_workflow_user')):
                raise UserError(_("You can't Forward the request at this "
                                  "stage."))
            line.forward_user_ids = self.env.context.get('user_ids', False)
            line.comment = self.env.context.get('reason', False)
            line._compute_eligible_user_ids()
            record = self.env[line.res_model].browse(line.res_id)
            record.action_approval_line_forward(line)


    def action_forward_multi(self):
        return {
            'name': _('Forward'),
            'res_model': 'forward.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'workflow.approval.line',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_na(self):
        """Mark not-needed approvals as N/A.

        This method called by the approved/rejected line."""
        for line in self:
            domain = [
                ('res_model', '=', line.res_model),
                ('res_id', '=', line.res_id),
                ('status', '=', 'pending'),
            ]
            if line.status == 'approved':
                domain.append(('required', '=', False))
                domain.append(('sequence', '>=', line.sequence))
            elif line.status == 'rejected':
                domain.append(('sequence', '>=', line.sequence))
            lines = self.search(domain)
            lines.write({'status': 'na'})

    def action_send_mail(self):
        """Send email for the current and next stages."""
        self.ensure_one()

        record = self.env[self.res_model].browse(self.res_id)

        if self.status != 'pending':

            record.action_approval_send_mail('done', self)

        # search for lines (including the current line) that are eligible for
        # approval right now
        lines = self.search([('res_id', '=', self.res_id),
                             ('res_model', '=', self.res_model),
                             ('status', '=', 'pending'),
                             ('sequence', '>=', self.sequence)],
                            order='sequence ASC')
        for line in lines:
            if self.with_context(no_check_user=True) \
                    .check_stage_approval(line):

                record.action_approval_send_mail('waiting', line)
                record.action_notify_send_mail(line)

    def write(self, vals):
        """Override to prevent overriding sequences from list drag'n'drop."""
        if 'sequence' in vals and len(vals) == 1:
            raise AccessError(_("You can't change sequence of approvals."))
        return super(WorkflowApprovalLine, self).write(vals)

    @api.model
    def _cron_workflow_escalate(self):
        """ This method is called by the cron to fetch
                    pending approval with SLA.
                """
        approvals = self.search([('status', '=', 'pending'), '|', ('sla_due_datetime', '<=', datetime.utcnow()),
                                 ('sla_reminder_datetime', '<=', datetime.utcnow())])
        for approval in approvals:
            sla = approval.step_line_id.sla_id
            record = self.env[approval.res_model].browse(approval.res_id)
            if record and sla:
                if approval.sla_due_datetime <= datetime.utcnow():
                    property_ids = self.env['workflow.sla.property'].sudo().search([('sla_id', '=', sla.id)], order='sequence ASC')
                    for sl in property_ids:
                        if sl.action_type == 'escalate_hrc' and sl.hierarchy_level > 0:
                            user_data = record.get_approval_current_user_data()
                            users = record.get_user_hierarchy(sl.hierarchy_level, user_data)
                            record.action_sla_escalation_send_mail(approval, users)
                        elif sl.action_type == 'escalate_filter' and sl.filter_group_id:
                            users = sl.filter_group_id.get_filter_result()
                            record.action_sla_escalation_send_mail(approval, users)
                        elif sl.action_type == 'escalate_group' and sl.group_id.users:
                            users = sl.group_id.users.ids
                            record.action_sla_escalation_send_mail(approval, users)
                        elif sl.action_type == 'skip':
                            approval.action_approve()
                        else:
                            pass
                    continue
                if approval.sla_reminder_datetime <= datetime.utcnow():
                    record.action_sla_reminder_send_mail(approval)



    # dashboad code #

    @api.model
    def get_workflow_approval_line_table(self):
        user = self.env.user
        top_workflow_to_approve = []
        # TO_DO : Must make query
        data = self.env['workflow.approval.line'].search([]).filtered(
                lambda r: r.can_approve)
        if data:
            top_workflow_to_approve = [
                [rec.workflow_id.name, rec.res_id_record_name, rec.approval_start_time, rec.create_uid.name, rec.id,
                 rec.res_model_id.model, rec.res_model_id.name]
                for rec in data]
            return {'top_workflow_to_approve': top_workflow_to_approve}
        else:
            return {'top_workflow_to_approve': top_workflow_to_approve}

    @api.model
    def get_wf_category(self):

        # TO_DO : Must make query
        data = self.env['workflow.category'].search([])
        card_wf_category = [
            [rec.name, rec.pending_count, rec.id, rec.icon_type, rec.font_aws_icon, rec.card_icon]
            for rec in data]
        return {'card_wf_category': card_wf_category}

    @api.model
    def get_wf_approval(self, wf_category=False):

        if wf_category:
            data = self.env['workflow.approval.line'].search([]).filtered(
                lambda r: r.can_approve and r.category_id.id == wf_category.id)
        else:
            data = self.env['workflow.approval.line'].search([]).filtered(
                lambda r: r.can_approve)

        return len(data)

    @api.model
    def open_approval_lines_view(self, category_id):
        data = self.env['workflow.approval.line'].search([]).filtered(
            lambda r: r.can_approve and r.category_id.id == category_id)
        # Define the domain with the provided category_id
        domain = [('id', 'in', data.ids),('status','=','pending')]

        # Return an action that opens the tree view of workflow.approval.line
        # filtered by the specified domain
        return domain

    @api.model
    def open_all_approval_lines_view(self):
        data = self.env['workflow.approval.line'].search([]).filtered(
            lambda r: r.can_approve)
        # Define the domain with the provided category_id
        domain = [('id', 'in', data.ids)]

        # Return an action that opens the tree view of workflow.approval.line
        # filtered by the specified domain
        return domain

    @api.model
    def get_count_all_wf_request(self):
        data = self.env['workflow.approval.line'].search([]).filtered(lambda r: r.can_approve and r.status == 'pending')
        return {'count_all_wf_request': len(data)}

    @api.model
    def get_approval_count(self, state=False):
        """Unassigned Leads Count Card"""

        get_approval_count = self.env['crm.lead'].search_count(
            [('user_id', '=', False), ('type', '=', 'lead')])
        if state:

            if state['ev'] == 'this_week':
                return {'get_approval_count': 55}
            if state['ev'] == 'for_your_action':
                return {'get_approval_count': 6666}
            else:
                return {'get_approval_count': 22}

        else:
            return {'get_approval_count': 0}

    def _compute_workflow_dashboard_count(self):
        records = self.env['res.workflow'].search([])
        pending_count = 0
        late_count = 0
        approved_count = 0

        for workflow in records:
            pending_count += workflow.pending_count
            late_count += workflow.late_count
            approved_count += workflow.approved_count

        return [approved_count, pending_count, late_count]

    @api.model
    def get_workflow_approval_pie_chart(self):
        count = self._compute_workflow_dashboard_count()
        number_in_pie = [count, ['Done', 'Pending', 'Late'], ["#47B39C", "#FFC154", "#EC6B56"]]
        return number_in_pie
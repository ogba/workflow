# -*- coding: utf8 -*-
from odoo import models, tools, fields, api, _
from odoo import SUPERUSER_ID
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime, date, time, timedelta
from lxml import etree
import random
import string
import logging

_logger = logging.getLogger(__name__)



class Workflow(models.Model):
    _name = 'res.workflow'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Workflow"
    _order = 'name, model_id'
    _rec_names_search = ['name', 'model_id']




    name = fields.Char('Name', required=True, translate=True, tracking=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade', tracking=True)
    res_model = fields.Char("Model Name", compute='_compute_res_model',
                            store=True)
    category_id = fields.Many2one('workflow.category', string='Category', required=True, ondelete='cascade', tracking=True)
    workflow_state = fields.Selection(
        [('not_active', 'Not Active'), ('active', 'Active')],
        default='not_active', string="State", tracking=True)
    workflow_type = fields.Selection(
        [('approval', 'Approval'), ('notify', 'Notification')],
        default='approval', string="Workflow Type", required=True, tracking=True)
    notify_template_id = fields.Many2one("mail.template", string='Notification Template', tracking=True,
                                         )
    workflow_notify_type = fields.Selection([('group', 'Role'), ('user', 'User'), ('hierarchy', 'Hierarchy'),
                                             ('department', 'Department Manager'), ('filter', 'Domain Filter')],
                                            string="Notify Approval By", tracking=True)
    action_ids = fields.One2many('workflow.action', 'workflow_id', string='Actions',compute='')
    action_on_submit_ids = fields.Many2many('workflow.action', string='Action to be run on Submit',
                                            help='the method that be called when start workflow , Example : send to approve ')
    approve_method_name = fields.Many2one('workflow.action',string='Approve method', help="The approval method to be applied in the workflow approved")
    reject_method_name = fields.Many2one('workflow.action', string='Reject method',help="The method that will be called when the workflow is rejected by user")
    redraft_method_name = fields.Many2one('workflow.action', string='Redraft method',help='the method that will be called when need to return the document to draft , it will start the workflow from beginning')
    status_bar_to_view = fields.Selection([('model', 'Status Bar of Original Model'), ('wf_status_bar', 'Workflow Status Bar (Recomended)')],
                                            help='write the status bar field technical name to be replaced in view',
                                            default='model',string="Status Bar to View", tracking=True)
    model_status_bar_name = fields.Char(string='Name of status bar field')
    notify_user_ids = fields.Many2many('res.users', 'workflow_notify_users_rel', string='Notify Users', tracking=True)
    notify_group_ids = fields.Many2many('res.groups', 'workflow_notify_group_rel', string='Notify Roles', tracking=True)
    notify_hierarchy_level = fields.Integer(default=1, tracking=True)
    notify_filter_group_id = fields.Many2one('ir.model.filter', string='Notify Filter', tracking=True)
    condition_ids = fields.One2many('workflow.condition', 'workflow_id', tracking=True)
    step_ids = fields.One2many('workflow.condition.step', 'workflow_id', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    description = fields.Html(string='Description')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
    show_on_dashboard = fields.Boolean(string='Show workflow on dashboard',
                                       help="Whether this workflow should be displayed on the dashboard or not",
                                       default=True)
    color = fields.Integer("Color Index", default=0)
    view_to_inherit_id = fields.Many2one('ir.ui.view',domain="[('model','=',res_model),('type','=','form')]",
                                         string='View to add Inherit',)
    inherited_view_id = fields.Many2one('ir.ui.view', string='Inherited view',store=True)
    approval_count = fields.Integer()
    pending_count = fields.Integer(compute='_compute_dashboard_count')
    late_count = fields.Integer(compute='_compute_dashboard_count')
    approved_count = fields.Integer(compute='_compute_dashboard_count')
    rejected_count = fields.Integer(compute='_compute_dashboard_count')


    _sql_constraints = [
        ('uniq_name', 'unique(company_id, name)', _("Workflow name must be unique."))]




    def create(self, vals):
        record = super(Workflow, self).create(vals)
        record.create_inherited_view()
        return record



    def _compute_dashboard_count(self):
        user = self.env.user
        for rec in self:
            approvals = self.env['workflow.approval.line'].search(
                [('workflow_id', '=', rec.id)])
            rec.pending_count = len(approvals.filtered(lambda r: r.can_approve and r.status == 'pending'))
            rec.late_count = self.env['workflow.approval.line'].search_count(
            [("eligible_user_ids", "in", user.id), ('status', '=', 'pending'),('sla_due_datetime', '<=', datetime.utcnow())])
            rec.approved_count = len(approvals.filtered(lambda r: r.user_id.id == user.id and r.status == 'approved'))
            rec.rejected_count = len(approvals.filtered(lambda r: r.user_id.id == user.id and r.status == 'rejected'))


    @api.onchange('model_id','view_to_inherit_id')
    def _onchange_ir_model(self):
        # insert workflow.state in state_ids
        if self.model_id:

            cmd = [(5,)]
            for el in self.model_id.view_ids.filtered(lambda r: r.type == 'form' and r.mode == 'primary' and r.id != self.inherited_view_id.id):
                arch = etree.XML(el.arch_db)
                buttons = arch.xpath("//form/header/button")
                for element in buttons:
                    record = (0, 0,
                              {
                                  'name': element.get('name'),
                                  'type': element.get('type'),
                                  'description': element.get('string')
                              })
                    if record not in cmd:
                        cmd.append(record)
            for view in self.model_id.view_ids.filtered(lambda r: r.type == 'form' and r.mode == 'extension' and r.id != self.inherited_view_id.id):
                arch = etree.XML(view.arch_db)
                buttons = arch.xpath("//button")
                for element in buttons:
                    if element.get('name') and element.get('type'):
                        record = (0, 0,
                                  {
                                      'name': element.get('name'),
                                      'description': element.get('string')
                                  })
                        if record not in cmd:
                            cmd.append(record)
            self.update({'action_ids': cmd})


    def xpath_button_hide(self,button_names):
        view = self.env.ref(self.view_to_inherit_id.xml_id).with_context(active_test=False)
        tree = etree.fromstring(view.arch)

        button_hide_xpath = ''
        for button_name in button_names:
            button_count = len(tree.xpath("//button[@name='%s']" % button_name))
            button_hide_xpath += ''.join([
                '<xpath expr="//button[@name=\'%s\'][%d]" position="attributes">'
                '<attribute name="invisible">1</attribute></xpath>' % (button_name, index + 1)
                for index in range(button_count)
            ])

        return button_hide_xpath
    def create_inherited_view(self):
        # remove the view
        self.env['ir.ui.view'].sudo().search([('id','=',self.inherited_view_id.id)]).unlink()

        view = self.env['ir.ui.view']
        base_view = self.env.ref(self.view_to_inherit_id.xml_id)
        button_to_hide = [button for button in [self.approve_method_name.name,self.reject_method_name.name]if button]

        button_hide_xpath = self.xpath_button_hide(button_to_hide)

        self.inherited_view_id = view.create({
            'name': 'Inherited View',
            'type': 'form',
            'model': base_view.model,
            'inherit_id': base_view.id,
            'arch':
                '''
                <data>
                        <xpath expr="//header" position="inside">
                        <field name="approval_status" invisible="1"/>
                            <button name="action_submit" type="object" string="Submit" class="oe_highlight"
                                invisible="approval_status != 'draft'"/>
                            <field name="approval_next_line_ids" invisible="1"/>
                            <button name="action_approval_wizard" string="Approve"
                                class="btn btn-success"
                                invisible="not approval_next_line_ids"
                                type="object"/>
                            <button name="action_reject_wizard" string="Reject"
                                invisible="not approval_next_line_ids"
                                class="btn btn-danger" type="object"/>
                            <button name="action_rfc_wizard" string="Return For Correction"
                                invisible="not approval_next_line_ids"
                                class="oe_highlight oe_inline" type="object"/>
                            <button name="action_rmi_wizard" string="Request More Information"
                                invisible="not approval_next_line_ids"
                                class="oe_highlight oe_inline" type="object"/>
                            <button name="action_forward_wizard" string="Forward"
                                invisible="not approval_next_line_ids"
                                class="oe_highlight oe_inline" type="object"/>
                            
        
                            <div class="oe_button_box" name="button_box">
                                <field name="approval_template_id" invisible="1"/>
                                <button name="action_open_approvals" type="object"
                                    class="oe_stat_button" icon="fa-lock"
                                    invisible="not approval_template_id"
                                    help="Approval Status: click to open list of approvals.">
                                    <div class="o_form_field o_stat_info">
                                        <span class="o_stat_text">
                                            <field name="approvals_done"/>
                                            <span>/</span>
                                            <field name="approvals_count"/>
                                        </span>
                                    </div>
                                </button>
                               
                            </div>
                        </xpath>
                         %s
                    </data>
                    ''' % button_hide_xpath,

                }).id
        if self.inherited_view_id:
            self.workflow_state = 'active'





    def open_action(self):
        self.ensure_one()
        return {
            'name': _('Workflow Approval'),
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'view_mode': 'tree,form',
            'domain': [('workflow_template_id', 'in', self.ids)],
        }

    def show_pending_approvals(self):
        self.ensure_one()
        approvals = self.env['workflow.approval.line'].search(
            [('workflow_id', 'in', self.ids), ('status', '=', 'pending'),]).filtered(lambda r: r.can_approve)
        return {
            'name': _('Pending Approval'),
            'type': 'ir.actions.act_window',
            'res_model': "workflow.approval.line",
            'view_mode': 'tree,form',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', approvals.ids)],
        }

    def show_late_approvals(self):
        self.ensure_one()
        approvals = self.env['workflow.approval.line'].search(
            [('workflow_id', 'in', self.ids), ('status', '=', 'pending'),('sla_due_datetime', '<=', datetime.utcnow())]).filtered(lambda r: r.can_approve)
        return {
            'name': _('Late Approval'),
            'type': 'ir.actions.act_window',
            'res_model': "workflow.approval.line",
            'view_mode': 'tree,form',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', approvals.ids)],
        }

    def action_create_new(self):
        return {
            'name': _('Create Record'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self.res_model,
        }

    @api.depends('model_id', 'model_id.name')
    def _compute_res_model(self):
        """Compute model name from model_id field."""
        for record in self:
            record.res_model = record.model_id and \
                               record.model_id.model or None

    @api.onchange('workflow_type')
    def onchange_workflow_type(self):
        """Reset notify fields"""
        if self.workflow_type:
            self.workflow_notify_type = False
            self.notify_user_ids = False
            self.notify_group_ids = False
            self.notify_filter_group_id = False

    def write(self, vals):
        """Override to prevent overriding workflow_type."""
        if self.workflow_state == 'active' and any(field in vals for field in vals):
            vals['workflow_state'] = 'not_active'
        if 'workflow_type' in vals:
            approvals = self.env["workflow.approval.line"].sudo().search_count([("workflow_id", "in", self.ids)])
            if vals['workflow_type'] == 'notify' and approvals > 0:
                raise UserError(_("You can't change workflow type of approvals."))
        return super(Workflow, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.approval_count > 0.0:
                raise UserError(_("You can't delete workflow that has approvals!"))
        return super(Workflow, self).unlink()


class WorkflowCondition(models.Model):
    _name = 'workflow.condition'
    _description = "Workflow Condition"
    _order = 'sequence, name'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=1)
    workflow_id = fields.Many2one('res.workflow', string='Workflow', ondelete='cascade')
    model_name = fields.Char(related='workflow_id.model_id.model')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
    condition_step_ids = fields.One2many('workflow.condition.step', 'condition_id')
    model_domain = fields.Text(
        help="pyhton expression that returns True or False to determine whether the condition is valid or not.")

    @api.constrains('condition_step_ids')
    def _check_condition_step_ids(self):
        for record in self:
            if not record.condition_step_ids:
                raise ValidationError(_("You must add at least one line in step  '  %s  ' in Conditions", record.name))

class WorkflowStep(models.Model):
    _name = 'workflow.condition.step'
    _description = "Workflow Condition Step"
    _order = 'sequence, name,condition_id'

    sequence = fields.Integer(string='Sequence', default=1)
    name = fields.Char(string='Name', required=True, translate=True)
    type = fields.Selection(
        [('group', 'Role'), ('user', 'User'), ('hierarchy', 'Hierarchy'),
         ('department', 'Department Manager'), ('filter', 'Domain Filter')],
        default='group', string="Approval By", required=True)
    type_user_ids = fields.Many2many('res.users', 'condition_users_rel', string='Users')
    type_group_ids = fields.Many2many('res.groups', 'condition_type_group_rel', string='Roles')
    type_hierarchy_level = fields.Integer(default=1)
    filter_group_id = fields.Many2one('ir.model.filter', string='Filter')
    waiting_template_id = fields.Many2one("mail.template", string='Waiting Approval Template',
                                         default= lambda self: self.env.ref('base_workflow_wf.mail_template_workflow_approval_line_waiting').id,  domain="[('model', '=', 'workflow.approval.line')]")
    notify_type = fields.Selection([('group', 'Role'), ('user', 'User'), ('hierarchy', 'Hierarchy'),
                                    ('department', 'Department Manager'), ('filter', 'Domain Filter')],
                                   string="Notify Approval By")
    notify_user_ids = fields.Many2many('res.users', 'notify_users_rel', string='Notify Users')
    notify_group_ids = fields.Many2many('res.groups', 'condition_notify_group_rel', string='Notify Roles')
    notify_hierarchy_level = fields.Integer(default=1)
    notify_filter_group_id = fields.Many2one('ir.model.filter', string='Notify Filter')
    notify_template_id = fields.Many2one("mail.template", string='Notify Template',
                                         domain="[('model', '=', 'workflow.approval.line')]")
    done_template_id = fields.Many2one("mail.template", string='Done Approval template',
                                       default= lambda self: self.env.ref('base_workflow_wf.mail_workflow_approval_line_done').id,domain="[('model', '=', 'workflow.approval.line')]")
    method_action_ids = fields.One2many('workflow.step.action', 'step_id', string='Actions')
    required_field_ids = fields.Many2many('ir.model.fields', 'condition_required_field_rel', string='Required Fields',
                                          domain="[('model_id', '=', 'workflow.approval')]")
    required_field_message = fields.Text(string='Required Field Message',help="The message will apear when user do action without fill the required field")

    required_attachment = fields.Boolean(string='Required Attachment')
    required_attachment_message = fields.Text(string='Required Attachment Message',help="The message will apear when user do action without upload attachment")
    condition_id = fields.Many2one('workflow.condition', string='Condition', ondelete='cascade')
    model_name = fields.Char(related='workflow_id.model_id.model')
    workflow_id = fields.Many2one('res.workflow', string='Workflow', related='condition_id.workflow_id', store=True)
    required = fields.Boolean("Required Stage", default=True)
    sla_id = fields.Many2one('workflow.sla', string='SLA')


    @api.constrains('type_hierarchy_level')
    def _check_hierarchy_level(self):
        for rec in self:
            if rec.type == 'hierarchy' and rec.type_hierarchy_level < 1:
                raise ValidationError(_("Hierarchy level can't be lower then 1"))


class WorkflowActions(models.Model):
    _name = 'workflow.step.action'
    _description = "Step Actions"
    _order = 'name, type'
    _rec_names_search = ['name', 'description']

    name = fields.Char('Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    parameter = fields.Char('Partmeter in ()')
    type = fields.Selection(
        [('approve', 'Approve'), ('reject', 'Reject'), ('rmi', 'Request More Information'),
         ('rfc', 'Return For Correction'), ('forward', 'Forward')], string='Action', required=True)
    description = fields.Char('Description')
    required_comment = fields.Boolean(string='Required Comment', default=False)
    step_id = fields.Many2one('workflow.condition.step', string='Step', ondelete='cascade')





class WorkflowMethodActions(models.Model):
    _name = 'workflow.action'
    _rec_name = 'name_description'

    name = fields.Char('Name')
    type = fields.Char('Type')
    description = fields.Char('Description')
    workflow_id = fields.Many2one('res.workflow', string='Workflow', ondelete='cascade')
    action_type = fields.Selection(
        [('approve', 'Approve'), ('reject', 'Reject'),('redraft', 'Re Draft')],

        string="Action Type",)
    @api.depends('name', 'description')
    def _compute_name_description(self):
        for record in self:
            record.name_description = f"{record.name} / {record.description}"

    name_description = fields.Char(string='Name / Description', compute='_compute_name_description', store=True)

# -*- coding: utf-8 -*-
"""SLA Models"""

import logging

from datetime import date, timedelta, datetime
from pytz import timezone, utc
from werkzeug.urls import url_encode
from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError, AccessError

LOGGER = logging.getLogger(__name__)


class WorkflowSLA(models.Model):
    _name = 'workflow.sla'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Workflow SLA"
    _order = 'name'
    _rec_names_search = ['name']

    name = fields.Char(string='SLA Name', translate=True, required=True)
    code = fields.Char(string='Code')
    period_type = fields.Selection([('hour', 'Hours'), ('day', 'Days')], default='day', required=True)
    sla_value = fields.Float(string='Escalation After', digits=0)
    reminder_value = fields.Float(string='Reminder After', digits=0)
    sla_template_id = fields.Many2one("mail.template", string='Escalation Template',domain="[('model', '=', 'workflow.approval.line')]")
    reminder_template_id = fields.Many2one("mail.template", string='Reminder Template',domain="[('model', '=', 'workflow.approval.line')]")
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
    sla_property_ids = fields.One2many('workflow.sla.property', 'sla_id', string='Lines')

    @api.constrains('reminder_value', 'sla_value')
    def _check_sla_reminder_value(self):
        for rec in self:
            if rec.sla_value <= 0.0:
                raise ValidationError(_("Please set SLA Value by positive value"))
            if rec.reminder_value <= 0.0:
                raise ValidationError(_("Please set Reminder Value by positive value"))
            if rec.sla_value <= rec.reminder_value:
                raise ValidationError(_("Please set SLA Value above Reminder Value"))


class SLAProperty(models.Model):
    _name = 'workflow.sla.property'
    _description = "SLA Property"
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence')
    action_type = fields.Selection([('skip', 'Skip to the next state'),
                                    ('escalate_hrc', 'Escalate Hierarchically'),
                                    ('escalate_group', 'Escalate to Group'),
                                    ('escalate_filter', 'Escalate to User Filter')], default='skip', required=True)
    sla_id = fields.Many2one('workflow.sla', string='SLA')
    filter_group_id = fields.Many2one('ir.model.filter', string='Domain Filter')
    group_id = fields.Many2one('res.groups', string='group to take action')
    hierarchy_level = fields.Integer(default=1)

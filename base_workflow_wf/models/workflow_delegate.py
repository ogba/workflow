from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WorkflowDelegate(models.Model):
    _name = 'workflow.delegate'
    _inherit = ['mail.thread']
    _description = 'Workflow Delegate'
    _order = 'id desc'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _get_employee_replace_domain(self):
        filter_group_id = self.env.user.company_id.filter_group_id
        if filter_group_id:
            return filter_group_id.domain
        return "[('id', '!=',employee_id)]"

    name = fields.Char(string='Reference', required=True, copy=False, default='New', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,tracking=True, default=_default_employee)
    user_id = fields.Many2one('res.users', string='User',related='employee_id.user_id',store=True)
    employee_replace_id = fields.Many2one('hr.employee', string='Alternative Employee', required=True,tracking=True, domain=_get_employee_replace_domain)
    replace_user_id = fields.Many2one('res.users', string='User', related='employee_replace_id.user_id', store=True)
    date_from = fields.Date(string='Start Date', required=True,tracking=True)
    date_to = fields.Date(string='End Date', required=True,tracking=True)
    active = fields.Boolean(string='Active', default=True,tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('workflow.delegate')

        return super().create(vals_list)


    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Check date constraints."""
        for record in self:
            if record.date_from and record.date_to:
                if str(record.date_from) > str(record.date_to):
                    raise ValidationError(_("Start date must be less than the end date"))
                if str(record.date_from) < str(fields.Date.today()):
                    raise ValidationError(_("Start date must be greater than the today date"))
                for rec in self.sudo().search(
                        [('employee_id', '=', record.employee_id.id),
                         ('employee_replace_id', '=', record.employee_replace_id.id),
                         ('date_from', '!=', False), ('date_to', '!=', False), ('id', '!=', record.id)]):
                    if rec.date_from <= record.date_from <= rec.date_to \
                            or rec.date_from <= record.date_to <= rec.date_to \
                            or record.date_from <= rec.date_from <= record.date_to \
                            or record.date_from <= rec.date_to <= record.date_to:
                        raise ValidationError(_("There is date overlap with a delegation"))

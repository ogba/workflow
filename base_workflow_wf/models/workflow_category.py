from odoo import models, fields, api, _

class WorkflowCategory(models.Model):
    _name = 'workflow.category'
    _description = 'Workflow Category'

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one('workflow.category', index=True, ondelete='cascade')
    child_ids = fields.One2many('workflow.category', 'parent_id')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    show_on_dashboard = fields.Boolean(string='Show workflow on dashboard',
                                       help="Whether this workflow should be displayed on the dashboard or not",
                                       default=True)
    color = fields.Integer("Color Index", default=0)
    pending_count = fields.Integer(compute='_compute_dashboard_count')
    icon_type = fields.Selection(
        [('default', 'Default'), ('upload', 'Upload Image'), ('font_aws', 'Font Awsome Icon')],
        string='Icon Display', default="default")
    card_icon = fields.Binary(string="Card Icon", attachment=True)
    default_icon = fields.Char(string="Icon", default="fa-users")
    font_aws_icon = fields.Char(string="Font awsome icon", help="Icon name from font awsome EX : fa-id-card ")
    color = fields.Integer(string='Color',
                           help="The color selected here will be used in every screen with the time off type.")

    _sql_constraints = [
        ('uniq_name', 'unique(company_id, name)', _("category name must be unique."))]

    @api.depends('child_ids')
    def _compute_dashboard_count(self):
        for category in self:
            # Search for approval lines in the current category and its children
            approvals = self.env['workflow.approval.line'].search([
                ('category_id', 'child_of', category.id),
                ('status', '=', 'pending')
            ])
            # Filter approvals where the current user can approve
            category.pending_count = len(approvals.filtered(lambda r: r.can_approve))

    def show_pending_approvals(self):
        self.ensure_one()
        approvals = self.env['workflow.approval.line'].search([
            ('category_id', 'child_of', self.id),
            ('status', '=', 'pending')
        ]).filtered(lambda r: r.can_approve)
        return {
            'name': _('Pending Approval'),
            'type': 'ir.actions.act_window',
            'res_model': "workflow.approval.line",
            'view_mode': 'tree,form',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', approvals.ids)],
        }

    def open_action(self):
        self.ensure_one()
        if self.child_ids:
            return {
                'name': _('Category'),
                'type': 'ir.actions.act_window',
                'res_model': 'workflow.category',
                'view_mode': 'kanban,form',
                'domain': [('parent_id', '=', self.id)],
            }

        return {
            'name': _('Workflows'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.workflow',
            'view_mode': 'kanban,form',
            'domain': [('category_id', 'in', self.ids)],
        }
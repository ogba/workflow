from odoo import api, fields, models


class ResWorkflowInherit(models.Model):
    _inherit = 'workflow.category'

    icon_type = fields.Selection(
        [('default', 'Default'), ('upload', 'Upload Image'),('font_aws', 'Font Awsome Icon')],
        string='Icon Display',default="default")
    card_icon = fields.Binary(string="Card Icon", attachment=True)
    default_icon = fields.Char(string="Icon", default="fa-users")
    font_aws_icon = fields.Char(string="Font awsome icon",help="Icon name from font awsome EX : fa-id-card ")
    color = fields.Integer(string='Color',
                           help="The color selected here will be used in every screen with the time off type.")
class CRMLead(models.Model):
    _inherit = 'workflow.approval.line'

    @api.model
    def get_workflow_approval_line_table(self, kwargs):
        user = self.env.user
        top_workflow_to_approve = []
        # TO_DO : Must make query
        data = self.env['workflow.approval.line'].sudo().search([('approval_start_time','!=',False),('status','=','pending')], limit=8, order='approval_start_time desc').filtered(
            lambda step: user.id in step.eligible_user_ids.ids)
        if data:
            top_workflow_to_approve = [
                [rec.workflow_id.name, rec.res_id_record_name, rec.approval_start_time, rec.create_uid.name,rec.res_id,rec.res_model_id.model,rec.res_model_id.name]
                for rec in data]
            return {'top_workflow_to_approve': top_workflow_to_approve}
        else:
            return {'top_workflow_to_approve': top_workflow_to_approve}



    @api.model
    def get_wf_category(self, kwargs):

        # TO_DO : Must make query
        data = self.env['workflow.category'].search([])
        card_wf_category = [
            [rec.name,rec.pending_count,rec.id,rec.icon_type,rec.font_aws_icon,rec.card_icon]
            for rec in data]
        return {'card_wf_category': card_wf_category}

    @api.model
    def get_wf_approval(self ,wf_category=False):

        if wf_category:
            data = self.env['workflow.approval.line'].search([]).filtered(
                lambda r: r.can_approve and r.category_id.id == wf_category.id)
        else:
            data = self.env['workflow.approval.line'].search([]).filtered(
                lambda r: r.can_approve)

        return len(data)

   

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
    def get_approval_count(self,state= False):
        """Unassigned Leads Count Card"""

        get_approval_count = self.env['crm.lead'].search_count(
            [('user_id', '=', False), ('type', '=', 'lead')])
        if state:

            if state['ev'] == 'this_week':
                return {'get_approval_count':55}
            if state['ev'] == 'for_your_action':
                return {'get_approval_count':6666}
            else:
                return {'get_approval_count': 22}

        else:
            return {'get_approval_count':0}

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
    def get_workflow_approval_pie_chart(self, kwargs):
        count = self._compute_workflow_dashboard_count()
        number_in_pie = [count, ['Done', 'Pending', 'Late'], ["#47B39C", "#FFC154", "#EC6B56"]]
        return number_in_pie
{
    'name': "Approval Workflow Engine | Multi-Step Workflow & Approval Automation",
    'version': '17.0.1.0.0',
    'sequence': 1,
    'category': 'Productivity/Workflow',
    'summary': """
        Approval Workflow Engine for Odoo | Multi-Step Workflow | SLA Tracking |
        Delegation | Bulk Approval | Dynamic Workflow Builder | No Code Required |
        Works on Any Odoo Model | Purchase Approval | Invoice Approval | HR Workflow
    """,
    'description': """
Approval Workflow Engine - Dynamic Multi-Step Workflow & Approval Automation
===========================================================

MAIN FEATURES:
--------------
* Dynamic Workflow Engine - Create workflows for any Odoo model
* Multi-Level Approval Process - Configure complex approval hierarchies
* User Delegation - Delegate approvals when unavailable
* SLA Management - Set time limits and escalation rules
* Email Notifications - Automatic alerts for pending approvals
* Custom Conditions - Define approval rules without coding
* Approval Dashboard - Track all pending and completed approvals
* Attachment Validation - Require documents before approval
* Bulk Approval - Approve multiple requests at once
* Forward & Return - Route requests for corrections

KEYWORDS:
---------
workflow, approval, approval workflow, multi-level approval, approval process,
workflow engine, approval management, document approval, purchase approval,
expense approval, leave approval, hr approval, sales approval, invoice approval,
manager approval, approval chain, approval hierarchy, approval routing,
SLA, delegation, process automation, workflow automation, business process,
notification, email notification, approval notification, dynamic workflow,
sequential approval, parallel approval, conditional approval, approval rules,
workflow mixin, approval mixin, statusbar, state management, process flow,
workflow state, approval state, reject, return, forward, escalation,
approval dashboard, workflow dashboard, approval widget, workflow widget,
no code workflow, configurable workflow, flexible workflow, custom workflow

USE CASES:
----------
* Purchase Order Approvals
* Sales Order Approvals
* Invoice Approvals
* Expense Approvals
* Leave Request Approvals
* Employee Document Approvals
* Contract Approvals
* Project Approvals
* Custom Document Approvals
* Any Odoo Model Approvals

COMPATIBLE WITH:
----------------
* Odoo Community Edition
* Odoo Enterprise Edition
* Odoo.sh

    """,
    'author': 'Aztek Computers',
    'company': 'Aztek Computers',
    'maintainer': 'Aztek Computers',
    'website': "https://www.aztekcomputers.com",
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'data/ir_cron.xml',
        'data/workflow_data.xml',
        'wizards/approval_wizard_views.xml',
        'wizards/forward_wizard_views.xml',
        'views/workflow_views.xml',
        'views/res_config_settings_views.xml',
        'views/workflow_dashboard_views.xml',
        'views/workflow_category_view.xml',
        'views/workflow_dashboard_view.xml',
        'views/workflow_delegate_view.xml',
        'views/workflow_sla_view.xml',
        'views/workflow_approval.xml',
        'views/workflow_request_view.xml',
    ],

    'assets': {
            'web.assets_backend': [
                'base_workflow_wf/static/src/css/dashboard.css',
                'base_workflow_wf/static/src/css/style.scss',
                'base_workflow_wf/static/src/css/material-gauge.css',
                'base_workflow_wf/static/src/js/workflow_dashboard.js',
                'base_workflow_wf/static/src/js/lib/highcharts.js',
                'base_workflow_wf/static/src/js/lib/Chart.bundle.js',
                'base_workflow_wf/static/src/js/lib/funnel.js',
                'base_workflow_wf/static/src/js/lib/d3.min.js',
                'base_workflow_wf/static/src/js/lib/material-gauge.js',
                'base_workflow_wf/static/src/js/lib/columnHeatmap.min.js',
                'base_workflow_wf/static/src/js/lib/columnHeatmap.js',
                'base_workflow_wf/static/src/xml/dashboard_templates.xml',
            ],
        },

    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
	'currency': 'EUR',
	'price': '50',
    'installable': True,
    'auto_install': False,
    'application': True,
}

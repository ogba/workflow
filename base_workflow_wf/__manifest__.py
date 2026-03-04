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
============================================================================

The most powerful no-code approval workflow engine for Odoo.
Build any approval workflow chain — multi-step, conditional, parallel, or sequential —
for any Odoo model without writing a single line of code.

MAIN FEATURES:
--------------
* Approval Workflow Engine - Build multi-step approval workflows for any Odoo model
* Multi-Level Approval Process - Configure complex approval hierarchies
* Dynamic Approver Assignment - Route by user, group, manager, or any field on the form
* Hierarchy-Based Routing - Route to direct manager, department head, or any management level
* Amount-Based Conditions - Trigger different approval chains based on invoice amount or any numeric field
* Any-Field Conditions - Use Odoo domain filters to conditionally skip or enforce stages
* Sequential & Parallel Approvals - Any-one or all-must-approve per stage
* SLA Management - Set time limits and auto-escalate overdue approvals
* Smart Delegation - Delegate approvals during absence with auto-activation by date
* Bulk Approval - Approve multiple requests simultaneously in one click
* Email Notifications - Automatic alerts at every workflow stage transition
* Approval Dashboard - Unified view of all pending approvals across all models
* Audit Trail - Complete timestamped log of every decision in Odoo chatter
* Field Locking - Lock document fields during active workflow to prevent edits
* Forward & Return - Route requests for corrections back to submitter

USE CASES:
----------
* Purchase Order Approval Workflow
* Invoice Approval Workflow
* Sales Order Approval Workflow
* Quotation Approval Workflow
* Expense Report Approval Workflow
* Leave Request Approval Workflow
* HR Document Approval Workflow
* Contract Approval Workflow
* Project Approval Workflow
* Budget Approval Workflow
* Employee Onboarding Workflow
* Custom Document Approval Workflow
* Any Odoo Model Approval Workflow

KEYWORDS:
---------
approval workflow, odoo workflow, workflow engine, approval workflow engine,
multi-step approval, multi level approval, dynamic workflow, workflow automation,
approval automation, workflow management, approval management, workflow builder,
no-code workflow, no code approval, workflow odoo, odoo approval workflow,
purchase order approval, purchase approval, invoice approval, bill approval,
hr workflow, hr approval, leave approval, leave request approval,
expense approval, expense report approval, sales order approval, quotation approval,
contract approval, document approval, sequential approval, parallel approval,
conditional approval, sla workflow, deadline approval, escalation workflow,
delegation workflow, approval delegation, bulk approval, mass approval,
manager approval, department approval, line manager approval, hierarchy approval,
approval audit trail, workflow log, configurable workflow, flexible workflow,
custom workflow, workflow stages, approval stages, approval process,
business process workflow, workflow notification, approval notification,
workflow dashboard, approval dashboard, workflow any model, approval management system,
workflow management system, dynamic approval, approval chain, approval hierarchy,
workflow routing, approval routing, amount based approval, value based workflow

COMPATIBLE WITH:
----------------
* Odoo Community Edition
* Odoo Enterprise Edition
* Odoo.sh
* On-Premise installations
* All Odoo versions

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

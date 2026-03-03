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

Transform your Odoo operations with our powerful no-code workflow engine.
Automate complex business processes, approvals, and notifications without writing a single line of code.

Key Features
------------
★ **Dynamic Workflow Builder** - Create custom workflows with drag-and-drop simplicity
★ **Multi-Level Approvals** - Sequential and parallel approval chains
★ **SLA Management** - Track deadlines and escalate automatically
★ **Delegation System** - Delegate approvals during absences
★ **Email Notifications** - Automated alerts at every workflow stage
★ **Advanced Dashboard** - Real-time workflow analytics and KPIs
★ **Flexible Conditions** - Rule-based routing and decision logic
★ **Process Tracking** - Complete audit trail and status monitoring

Use Cases
---------
• Purchase Request Approvals
• Leave & Expense Management
• Document Review Processes
• Sales Order Validation
• HR Onboarding Workflows
• Custom Business Processes

Benefits
--------
✓ No Coding Required - 100% Configuration Based
✓ Reduce Approval Delays
✓ Ensure Compliance & Accountability
✓ Improve Process Visibility
✓ Scale Business Operations

Technical Highlights
--------------------
• Compatible with any Odoo model
• RESTful API ready
• Multi-company support
• Full audit logging
• Compatible with all Odoo versions

Support & Documentation
-----------------------
📧 Contact: ogba.awed@gmail.com
📖 Full documentation included
🔄 Regular updates & improvements
    """,

    'author': 'Aztek Computers',
    'company': 'Aztek Computers',
    'maintainer': 'Aztek Computers',
    'website': "https://www.aztekcomputers.com",
    'support': 'ogba.awed@gmail.com',
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

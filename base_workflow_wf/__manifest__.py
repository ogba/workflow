{
    'name': "Approval Workflow Engine | Multi-Step Workflow & Approval Automation",
    'version': '17.0.1.0.0',
    'sequence': 1,
    'category': 'Productivity/Workflow',
    'summary': """
        Approval Workflow | Workflow Engine | Multi-Step Approval | Dynamic Workflow |
        Purchase Approval | Invoice Approval | HR Workflow | Leave Approval |
        Expense Approval | Sales Approval | SLA | Delegation | Bulk Approval |
        No Code Workflow Builder | Works on Any Odoo Model | Approval Automation
    """,
    'description': """
Approval Workflow Engine - Dynamic Multi-Step Workflow & Approval Automation
============================================================================

The most powerful no-code approval workflow engine for Odoo.
Build any approval workflow, multi-step approval chain, conditional workflow,
parallel approval, or sequential approval for any Odoo model — zero code required.

WHAT IS IT:
-----------
A fully configurable approval workflow engine and automation platform built natively
for Odoo. Design approval workflow stages, assign approvers dynamically by role,
group, department manager, or hierarchy, trigger automatic actions, lock fields,
send real-time notifications, and maintain a complete audit trail — all from a
simple point-and-click interface. No developer needed.

MAIN FEATURES:
--------------
* Approval Workflow Engine - Build multi-step approval workflows for any Odoo model
* Multi-Level Approval - Configure unlimited approval levels and hierarchies
* Dynamic Approver Assignment - Route by user, security group, manager, or any field
* Organisational Hierarchy Routing - Direct manager, department head, CEO, any level
* Amount-Based Approval Routing - Different chains based on invoice/PO amount or any value
* Any-Field Condition Logic - Domain filter rules to skip or enforce stages automatically
* Sequential Approvals - Staged one-after-another approval chains
* Parallel Approvals - Multiple approvers working simultaneously in one stage
* Any-One or All-Must-Approve - Flexible quorum rules per stage
* SLA & Deadline Management - Time-limit stages, auto-remind, auto-escalate overdue
* Smart Delegation - Date-based auto-delegation for absences, auto-reverts on return
* Bulk Approval Processing - Approve or reject hundreds of records in one click
* Automated Email Notifications - Instant alerts on submission, transition, approval, rejection
* Personal Approval Dashboard - Every pending task in one unified view per user
* Admin Control Centre - Cross-department real-time visibility for managers
* Complete Audit Trail - Timestamped decision log in Odoo native chatter
* Document Field Locking - Auto-lock fields on submission, unlock on completion
* Forward & Return Routing - Return to submitter or escalate to higher authority
* Approve / Reject / Return / Escalate Actions - Full decision toolkit per stage
* Category-Based Dashboards - Organise workflows by department or business unit

USE CASES:
----------
* Purchase Order Approval Workflow
* Purchase Request Approval
* Vendor Approval Workflow
* Supplier Approval Process
* RFQ Approval Odoo
* Invoice Approval Workflow
* Bill Approval Odoo
* Payment Approval Workflow
* Credit Note Approval
* Sales Order Approval Workflow
* Quotation Approval Odoo
* Discount Approval Workflow
* Price Approval Odoo
* Expense Report Approval Workflow
* Leave Request Approval Workflow
* Time Off Approval Odoo
* Overtime Approval Workflow
* HR Document Approval
* Recruitment Approval Workflow
* Contract Approval Workflow
* Budget Approval Workflow
* Project Approval Workflow
* Asset Approval Odoo
* Manufacturing Approval Workflow
* Quality Approval Workflow
* Inventory Approval Odoo
* CRM Opportunity Approval
* Custom Document Approval Workflow
* Any Odoo Model Approval Workflow

KEYWORDS:
---------
approval workflow, workflow approval, odoo workflow, odoo approval,
workflow engine, approval workflow engine, dynamic workflow engine,
multi-step approval, multi level approval, multi-level approval workflow,
multi step approval odoo, approval levels, approval tiers, approval stages,
sequential approval, sequential workflow, parallel approval, parallel workflow,
conditional approval, conditional workflow, approval chain, workflow chain,
approval hierarchy, workflow hierarchy, approval routing, workflow routing,
dynamic workflow, dynamic approval, automated approval, automated workflow,
workflow automation, approval automation, process automation, business process automation,
workflow management, approval management, approval management system,
workflow management system, workflow builder, approval builder,
no-code workflow, no code workflow, no code approval, zero code workflow,
low code workflow, no developer needed, workflow without coding,
odoo approval workflow, odoo workflow module, odoo workflow engine,
odoo multi step approval, odoo approval automation, odoo process automation,
purchase order approval, purchase approval, purchase request approval, po approval,
rfq approval, vendor approval, supplier approval,
invoice approval, bill approval, invoice approval odoo, payment approval,
credit note approval, payment workflow, financial approval,
sales order approval, quotation approval, discount approval, price approval,
sales approval odoo, crm approval, opportunity approval,
expense approval, expense report approval, expense workflow, expense claim approval,
leave approval, leave request approval, time off approval, overtime approval,
hr workflow, hr approval, hr approval workflow, employee approval,
recruitment approval, contract approval, onboarding workflow,
hr document approval, payroll approval, attendance approval,
project approval, task approval, budget approval, asset approval,
manufacturing approval, quality approval, mrp approval,
inventory approval, stock approval, warehouse approval,
sla workflow, sla approval, deadline approval, approval deadline,
escalation workflow, approval escalation, auto escalation,
delegation workflow, approval delegation, auto delegation,
bulk approval, mass approval, batch approval, bulk workflow,
manager approval, department approval, line manager approval,
department manager approval, hierarchy approval, organisational hierarchy approval,
ceo approval, director approval, management approval,
amount based approval, value based workflow, threshold approval,
invoice amount approval, po amount approval, budget threshold workflow,
approval audit trail, approval log, workflow log, audit trail odoo,
approval history, approval record, approval tracking, approval status,
field locking, document locking, workflow field lock,
email notification workflow, approval notification, automated email approval,
approval dashboard, workflow dashboard, approval status widget,
workflow status bar, approval progress, workflow progress,
configurable workflow, flexible workflow, custom workflow, universal workflow,
generic workflow, multi model workflow, workflow any model,
workflow community, workflow enterprise, workflow odoo sh,
workflow mixin, approval mixin, workflow plugin, approval plugin,
workflow addon, approval addon, workflow module, approval module

COMPATIBLE WITH:
----------------
* Odoo Community Edition
* Odoo Enterprise Edition
* Odoo.sh
* On-Premise Installations
* All Odoo Versions

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
	'price': '20',
    'installable': True,
    'auto_install': False,
    'application': True,
}

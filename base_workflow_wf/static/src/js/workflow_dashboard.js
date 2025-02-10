/** @odoo-module */
import { registry} from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted} = owl
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";
export class WFDashboard extends Component {

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        onWillStart(this.onWillStart);
        onMounted(this.onMounted);
    }

    async onWillStart() {
        var self = this;
        this.login_employee = {};


        var def_workflow_table = jsonrpc('/web/dataset/call_kw/workflow.approval.line/get_workflow_approval_line_table', {
                model: "workflow.approval.line",
                method: "get_workflow_approval_line_table",
                
                kwargs: {},
            })
            .then(function(res) {
                self.top_workflow_to_approve = res['top_workflow_to_approve'];
            });



        var def_top_category = jsonrpc('/web/dataset/call_kw/workflow.approval.line/get_wf_category', {
                model: "workflow.approval.line",
                method: "get_wf_category",
                args: [{}],
                kwargs: {},
            })
            .then(function(res) {
                self.card_wf_category = res['card_wf_category'];
            });



        var def_count_wf_request = jsonrpc('/web/dataset/call_kw/workflow.approval.line/get_count_all_wf_request', {
                model: "workflow.approval.line",
                method: "get_count_all_wf_request",
                args: [{}],
                kwargs: {},
            })
            .then(function(res) {
                self.get_count_all_wf_request = res['count_all_wf_request'];
            });



        return $.when(def_workflow_table,def_top_category,def_count_wf_request);
    }


    function_get_approval_count(ev) {
        var self = this;
        jsonrpc('/web/dataset/call_kw/workflow.approval.line/get_approval_count', {
                model: 'workflow.approval.line',
                method: 'get_approval_count',
                args: [{ev}],
                kwargs: {},
            })
            .then(function(result) {
                $('#request_count').hide();
                $('#leads_for_your_action').empty();
                $('#leads_for_your_action').append('<span>' +result['get_approval_count'] + '</span>');
            })
    }


    opportunity(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Opportunity"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form,calendar',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [
                ['user_id', '=', session.uid],
                ['type', '=', 'opportunity']
            ],
            target: 'current',
        })
    }
    /**
     * Initiates an action to display leads assigned to the current user.
     * @param {Event} e - The event object.
     */
    my_approval_list(e) {

        var self = this;
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };

        var domain = [["id", "=",e[4]]]
        this.action.doAction({
            name: _t(e[6]),
            type: 'ir.actions.act_window',
            res_model: e[5],
            view_mode: 'form',
            views: [
                [false, 'form']
            ],
            res_id: e[4],
            domain: domain,
            target: 'current',
        }, options)
    }

//    ------------------------------------------------------------
    my_lead(ev) {
        var self = this;
        jsonrpc('/web/dataset/call_kw/workflow.approval.line/open_approval_lines_view', {
                model: 'workflow.approval.line',
                method: 'open_approval_lines_view',
                args: [{ev}],
                kwargs: {},
            })
            .then(function(result) {
               var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                };

          self.action.doAction({
            name: _t(""),
            type: 'ir.actions.act_window',
            res_model: 'workflow.approval.line',
            view_mode: 'tree,form,calendar',
            context:{'group_by': ['workflow_id', 'res_id_record_name']},
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: result,
            target: 'current',
        }, options);
            })
    }
    all_pending_request(ev) {
        var self = this;
        jsonrpc('/web/dataset/call_kw/workflow.approval.line/open_all_approval_lines_view', {
                model: 'workflow.approval.line',
                method: 'open_all_approval_lines_view',
                args: [],
                kwargs: {},
            })
            .then(function(result) {
               var options = {
            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                };

          self.action.doAction({
            name: _t(""),
            type: 'ir.actions.act_window',
            res_model: 'workflow.approval.line',
            view_mode: 'tree,form,calendar',
            context:{'group_by': ['workflow_id', 'res_id_record_name']},
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: result,
        target: 'current',
        }, options);
            })
    }
//    ------------------------------------------------------------
    /**
     * Handles the reverse breadcrumb action.
     * Updates the breadcrumb, fetches updated data, and reloads the dashboard.
     */
    on_reverse_breadcrumb() {
        var self = this;
        WebClient.do_push_state({});
        this.update_cp();
        this.fetch_data().then(function() {
            self.$('.o_hr_dashboard').reload();
            self.render_dashboards();
        });
    }
    /**
     * Lifecycle hook triggered when the component is mounted.
     * Renders various charts and graphs upon mounting.
     */
    async onMounted() {
//        this.renderElement();
        this.workflow_pie_chart();
    }



    workflow_pie_chart() {
        var self = this
        var ctx = $(".workflow_pie_chart");
        jsonrpc('/web/dataset/call_kw/workflow.approval.line/get_lead_month_pie', {
            model: "workflow.approval.line",
            method: "get_workflow_approval_pie_chart",
            args: [{}],
            kwargs: {},
        }).then(function(arrays) {
            var data = {
                labels: arrays[1],
                datasets: [{
                    label: "",
                    data: arrays[0],
                    backgroundColor:arrays[2],
                    borderColor: arrays[2],
                    borderWidth: 1
                }, ]
            };
            //options
            var options = {
                responsive: true,
                title: false,
                legend: {
                    display: true,
                    position: "right",
                    labels: {
                        fontColor: "#333",
                        fontSize: 16
                    }
                },
                scales: {
                    yAxes: [{
                        gridLines: {
                            color: "rgba(0, 0, 0, 0)",
                            display: false,
                        },
                        ticks: {
                            min: 0,
                            display: false,
                        }
                    }]
                },
//                onClick: function(evt) {
//                    console.log("onClick",evt)
//                    self.action.doAction({
//                    name: _t(""),
//                    type: 'ir.actions.act_window',
//                    res_model: 'workflow.approval.line',
//                    view_mode: 'tree,form,calendar',
//                    context:{'group_by': ['workflow_id', 'res_id_record_name']},
//                    views: [
//                        [false, 'list'],
//                        [false, 'form']
//                    ],
//                    target: 'current',
//                }, options);
//                    }

            };
            //create Chart class object
            var chart = new Chart(ctx, {
                type: "doughnut",
                data: data,
                options: options
            });
        });
    }

}
WFDashboard.template = "WFDashboard"
registry.category("actions").add("workflow_dashboard", WFDashboard)

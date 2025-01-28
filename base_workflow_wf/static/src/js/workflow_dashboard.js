odoo.define('workflow_dashboard.WFDashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var DashBoard = AbstractAction.extend({
        contentTemplate: 'WFDashboard',
        events: {
            'click .my_lead': 'my_lead',
            'click .all_pending_request': 'all_pending_request',
            'click .unassigned_leads': 'unassigned_leads',
            'click .my_approval_list': 'my_approval_list',
            'click .revenue_card': 'revenue_card',
            'change #income_expense_values': function(e) {
                e.stopPropagation();
                var $target = $(e.target);
                var value = $target.val();
                if (value=="this_year"){
                    this.onclick_this_year($target.val());
                }else if (value=="this_quarter"){
                    this.onclick_this_quarter($target.val());
                }else if (value=="this_month"){
                    this.onclick_this_month($target.val());
                }else if (value=="this_week"){
                    this.onclick_this_week($target.val());
                }
            },
          

        },

        init: function(parent, context) {
            this._super(parent, context);
            this.upcoming_events = [];
            this.current_lang=[];
            this.dashboards_templates = ['LoginUser','Managercrm','Admincrm'];
            this.login_employee = [];
        },

        willStart: function(){
            var self = this;
            this.login_employee = {};
            return this._super()
            .then(function() {

                var def_workflow_table =  self._rpc({
                    model: 'workflow.approval.line',
                    method: 'get_workflow_approval_line_table'
                }).then(function(res) {
                    self.top_workflow_to_approve = res['top_workflow_to_approve'];
                });

                var def_top_category = self._rpc({
                    model: "workflow.approval.line",
                    method: "get_wf_category",
                })
                .then(function (res) {
                    self.card_wf_category = res['card_wf_category'];
                });

                var def_count_wf_request = self._rpc({
                    model: "workflow.approval.line",
                    method: "get_count_all_wf_request",
                })
                .then(function (res) {
                    self.get_count_all_wf_request = res['count_all_wf_request'];
                });



                return $.when(def_workflow_table,def_top_category,def_count_wf_request);
            });
        },





        my_lead: function(e) {
            var self = this;
            var cardId = $(e.currentTarget).data('id');
           
            rpc.query({
                model: "workflow.approval.line",
                method: "open_approval_lines_view",
                args: [cardId]
              
            }).then(function(result) {
                var options = {
                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                };
        
                // Do Action with the result domain
                self.do_action({
                    name: _t("My Approvals"),
                    type: 'ir.actions.act_window',
                    res_model: 'workflow.approval.line',
                    view_mode: 'tree,form,calendar',
                    context: {'group_by': ['workflow_id', 'res_id_record_name']},
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    domain: result, // Result from the RPC
                    target: 'current',
                }, options);
            }).catch(function(err) {
                console.error("Error in RPC call:", err);
            });
        },


        my_approval_list: function(e) {
            var self = this;
            var line_id = $(e.currentTarget).data('id');
            
            var domain = [["id", "=",line_id]]
                var options = {
                on_reverse_breadcrumb: self.on_reverse_breadcrumb,
            };

            // Do Action with the result domain
            self.do_action({
                name: _t("My Approvals"),
                type: 'ir.actions.act_window',
                res_model: 'workflow.approval.line',
                view_mode: 'tree,form,calendar',
                context: {'group_by': ['workflow_id', 'res_id_record_name']},
                views: [
                    [false, 'list'],
                    [false, 'form']
                ],
                res_id: line_id,
                domain: domain, // Result from the RPC
                target: 'current',
            }, options);
            
        },

        all_pending_request: function(e) {
            var self = this;
           
           
            rpc.query({
                model: "workflow.approval.line",
                method: "open_all_approval_lines_view",
                
              
            }).then(function(result) {
                var options = {
                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                };
        
                // Do Action with the result domain
                self.do_action({
                    name: _t("My Approvals"),
                    type: 'ir.actions.act_window',
                    res_model: 'workflow.approval.line',
                    view_mode: 'tree,form,calendar',
                    context: {'group_by': ['workflow_id', 'res_id_record_name']},
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    domain: result, // Result from the RPC
                    target: 'current',
                }, options);
            }).catch(function(err) {
                console.error("Error in RPC call:", err);
            });
        },

        







        start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.update_cp();
                self.render_dashboards();
                self.render_graphs();
                self.$el.parent().addClass('oe_background_grey');
            });
        },

        render_graphs: function(){
            var self = this;
           
           
            self.workflow_pie_chart();
        },




        workflow_pie_chart:function(){
            var self = this
            var ctx = self.$(".workflow_pie_chart");
            rpc.query({
                model: "workflow.approval.line",
                method: "get_workflow_approval_pie_chart",
            }).then(function (arrays) {
                var data = {
                    labels : arrays[1],
                    datasets: [{
                        label: "",
                        data: arrays[0],
                        backgroundColor:arrays[2],
                        borderColor: arrays[2],
                        borderWidth: 1
                    },]
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
                    }
                };

                //create Chart class object
                var chart = new Chart(ctx, {
                    type: "doughnut",
                    data: data,
                    options: options
                });
            });
        },





        render_dashboards: function() {
            var self = this;
            if (this.login_employee){
                var templates = []
                if( self.is_manager == true){
                    templates = ['LoginUser', 'Managercrm', 'Admincrm'];
                }
                else{
                    templates = ['LoginUser','Managercrm'];
                }
                _.each(templates, function(template) {
                    self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}));
                });
            }
            else{
                self.$('.o_hr_dashboard').append(QWeb.render('EmployeeWarning', {widget: self}));
            }
        },

        on_reverse_breadcrumb: function() {
            var self = this;
            web_client.do_push_state({});
            this.update_cp();

        },

         update_cp: function() {
            var self = this;
         },
    });

    core.action_registry.add('workflow_dashboard', DashBoard);
    return DashBoard;
});
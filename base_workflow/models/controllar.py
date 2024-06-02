# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import main
from odoo.addons.web.controllers import dataset

from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

import inspect


class CustomDataSet(dataset.DataSet):

    @http.route('/web/dataset/call_button', type='json', auth="user")
    def call_button(self, model, method, args,kwargs):
        print('======================= call controller ========================')
        # check if the current model inherit from workflow.model
        parents = request.env[model]._inherit
        parents = [parents] if isinstance(parents, str) else (parents or [])
        # a tmp solution that needs to be fixed
        # workflow.model doesn't appear in _inherit list for standard Odoo models
        workflow_id = request.env['res.workflow'].search([('model_id', '=', model)])
        if 'mail.thread' in parents or workflow_id:

            if method == workflow_id.redraft_method_name.name:
                #redraft method
                redraft_mothod = request.env[model].search([('id','in',args[0])]).redraft_workflow_record()
                if redraft_mothod:
                    action = self._call_kw(model, method, args, kwargs)

            else:
                 action = self._call_kw(model, method, args, kwargs)
        else:
            action = self._call_kw(model, method, args, kwargs)

        if isinstance(action, dict) and action.get('type') != '':
            return main.clean_action(action, env=request.env)
        return False
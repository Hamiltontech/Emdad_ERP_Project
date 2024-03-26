# -*- coding: utf-8 -*-
from emdad import http
from emdad.http import request
import logging
import json
import werkzeug.wrappers
import functools
from emdad.exceptions import AccessDenied, AccessError
# from emdad.addons.emdad_sales.models.model import EmdadSalesLines

_logger = logging.getLogger(__name__)


class contacts(http.Controller):

    @http.route("/api/v1/slave/baseurl/", methods=["GET"], type="http", auth="none", csrf=False)
    def get_sales(self, **post):
        
        cr_number = http.request.params.get('company_cr')
        print(cr_number)
        records = request.env["emdad.customer"].sudo().search([('cr_number','=',cr_number)])
        records = records.read(['domain_name'])
        print(records)

        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Headers","*")],
            response=json.dumps(records, default=str)
        )
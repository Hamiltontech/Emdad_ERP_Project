# -*- coding: utf-8 -*-
from emdad import http
from emdad.http import request
import logging
import json
import werkzeug.wrappers
import functools
from emdad.exceptions import AccessDenied, AccessError

_logger = logging.getLogger(__name__)

class Procurement(http.Controller):
    
    @http.route("/api/v1/procurement", methods=["GET"], type="http", auth="none", csrf=False)
    def get_procurements(self, **post):

        records = request.env["emdad.procurement"].sudo().search([])
        records = records.read()

        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Headers","*")],
            response=json.dumps(records, default=str)
        )

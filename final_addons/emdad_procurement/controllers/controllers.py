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

        procurements = request.env["emdad.procurement"].sudo().search([])
        procurements = procurements.read()

        for po in procurements:
            lines_id = po['procurement_lines']
            procurements_lines = request.env["emdad.line.procurement"].sudo().search_read([('id', 'in', lines_id)], [])
            po['procurement_lines'] = procurements_lines
            for line in po['procurement_lines']:
                line['product_image'] = line['product_image'].decode('utf-8')

 
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Headers","*")],
            response=json.dumps(procurements, default=str)
        )
    
    @http.route("/api/v1/procurement/update", methods=["PUT"], type="http", auth="none", csrf=False)
    def update_procurements(self, **post):
                
        payload = request.httprequest.data.decode()

        if not payload:
            print("-----------")
            return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Headers","*")],
            response=json.dumps("", default=str)
            )
        

        data = json.loads(payload)
        print(55555555555,data)
        for po_line in data['data']:
            print(po_line)
            po_line_id = po_line['related_remote_po_line']
            records_to_update = request.env['emdad.line.procurement'].sudo().search([('id', '=', po_line_id)])
            print(records_to_update)
            for record in records_to_update:
                record.write({'product_cost': po_line['price'],})
                print(record.read())

        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Headers","*")],
            response=json.dumps(data, default=str)
        )
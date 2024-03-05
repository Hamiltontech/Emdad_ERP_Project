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

class Procurement(http.Controller):
    
    @http.route("/api/v1/sales", methods=["GET"], type="http", auth="none", csrf=False)
    def get_sales(self, **post):
        
        records = request.env["emdad.sales"].sudo().search([])
        records = records.read()

        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Headers","*")],
            response=json.dumps(records, default=str)
        )
    
    @http.route("/api/v1/sales/create", methods=["POST"], type="http", auth="none", csrf=False)
    def create_sales(self, **post):
        
        payload = request.httprequest.data.decode()

        if not payload:
            print("-----------")
            return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Headers","*")],
            response=json.dumps("", default=str)
            )
        
        print(11111111111111,payload)
        data = json.loads(payload)
        print(444444444,data["effective_date"])
        
        sales_vals = {
            "date":data["create_date"],
            "effective_date":data["effective_date"],
            # "customer":data["customer"],
            # "delivery_type":data["delivery_type"]
        }

        sales_record = request.env["emdad.sales"].sudo().create(sales_vals)

        sales_lines = []
        for line in data['procurement_lines']:
            print(line)
            sales_lines_vals = {
                "related_sales":sales_record.id,
                "product_id":line['product_id'][0],
                "barcode":line['barcode'],
                "batch":line['batch'],
                "tax":line['taxes'],
                "location":line['location'][0],
                "metric":line['metric'],
                "qty":line['request_qty'],
                "description":line['description'],
                "request_qty":line['request_qty'],
                "metric_unit":line['metric'][0] if line['metric'] else None,
                "product":line['product_id'][0]
            }

            sales_lines_record = request.env["emdad.sales.line"].sudo().create(sales_lines_vals)
            sales_lines.append(sales_lines_record.id)
            print(sales_lines_record.id)

        print(sales_lines)
        sales_record.update({"order_lines":sales_lines})


        
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache"),("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Headers","*")],
            response=json.dumps(data, default=str)
        )



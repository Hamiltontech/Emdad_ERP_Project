/** @emdad-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from  "@emdad/owl";

class ProcurementDashboard extends Component {
    static template = "emdad_procurement.ProcurementDashboard";
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.action = useService('action');
        this._fetch_data();
    }

    _fetch_data() {
        var self = this;
        this.orm.call("emdad.procurement", "get_tiles_data", [], {}).then(function(result) {
            $('#direct').append('<span>' + result.direct_count + '</span>');
            $('#market').append('<span>' + result.market_count + '</span>');
            $('#multiple').append('<span>' + result.multiple_count + '</span>');
        });
    }

    openDirect() {
        if (this.action) {
            this.action.doAction({
                type: 'ir.actions.act_window',
                name: 'Create Journal Entry',
                target: 'new',
                res_model: 'emdad.procurement',
                views: [[false, 'form']],
                context: {
                    // Set default values for specific fields
                    default_process_type: 'direct',
                    // Add more fields as needed
                },
            });
        } else {
            console.error('this.action is not defined. Make sure it is properly initialized.');
        }
    }
    openMarket() {
        if (this.action) {
            this.action.doAction({
                type: 'ir.actions.act_window',
                name: 'Create Journal Entry',
                target: 'new',
                res_model: 'emdad.procurement',
                views: [[false, 'form']],
                context: {
                    // Set default values for specific fields
                    default_process_type: 'market',
                    // Add more fields as needed
                },
            });
        } else {
            console.error('this.action is not defined. Make sure it is properly initialized.');
        }
    }
    openTender() {
        if (this.action) {
            this.action.doAction({
                type: 'ir.actions.act_window',
                name: 'Create Journal Entry',
                target: 'new',
                res_model: 'emdad.tender',
                views: [[false, 'form']],
            });
        } else {
            console.error('this.action is not defined. Make sure it is properly initialized.');
        }
    }
}

registry.category("actions").add("emdad_procurement.dashboard", ProcurementDashboard);

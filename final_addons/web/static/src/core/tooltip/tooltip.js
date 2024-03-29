/** @emdad-module **/

import { Component } from "@emdad/owl";

export class Tooltip extends Component {}
Tooltip.template = "web.Tooltip";
Tooltip.props = {
    close: Function,
    tooltip: { type: String, optional: true },
    template: { type: String, optional: true },
    info: { optional: true },
};

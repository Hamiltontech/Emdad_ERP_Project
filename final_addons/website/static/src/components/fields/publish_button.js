/** @emdad-module **/

import { registry } from "@web/core/registry";
import { Component } from "@emdad/owl";

class PublishField extends Component {}
PublishField.template = "website.PublishField";

registry.category("fields").add("website_publish_button", {
    component: PublishField,
});

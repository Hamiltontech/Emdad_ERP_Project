/** @emdad-module **/

import { Component } from "@emdad/owl";
import { registry } from "@web/core/registry";


class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    
}
const myService = {
    dependencies: ["notification"],
    start(env, { notification }) {
       let counter = 1;
       setInterval(() => {
          notification.add(`Tick Tock ${counter++}`);
       }, 5000);
    },
    };
    
registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
registry.category("services").add("myService", myService);


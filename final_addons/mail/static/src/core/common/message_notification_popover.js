/* @emdad-module */

import { Component } from "@emdad/owl";

export class MessageNotificationPopover extends Component {
    static template = "mail.MessageNotificationPopover";
    static props = ["message", "close?"];
}

/** @emdad-module */

import { coreTypes, CorePlugin } from "@emdad/o-spreadsheet";

/** Plugin that link charts with emdad menus. It can contain either the Id of the emdad menu, or its xml id. */
export class ChartemdadMenuPlugin extends CorePlugin {
    constructor(config) {
        super(config);
        this.emdadMenuReference = {};
    }

    /**
     * Handle a spreadsheet command
     * @param {Object} cmd Command
     */
    handle(cmd) {
        switch (cmd.type) {
            case "LINK_emdad_MENU_TO_CHART":
                this.history.update("emdadMenuReference", cmd.chartId, cmd.emdadMenuId);
                break;
            case "DELETE_FIGURE":
                this.history.update("emdadMenuReference", cmd.id, undefined);
                break;
        }
    }

    /**
     * Get emdad menu linked to the chart
     *
     * @param {string} chartId
     * @returns {object | undefined}
     */
    getChartemdadMenu(chartId) {
        const menuId = this.emdadMenuReference[chartId];
        return menuId ? this.getters.getIrMenu(menuId) : undefined;
    }

    import(data) {
        if (data.chartemdadMenusReferences) {
            this.emdadMenuReference = data.chartemdadMenusReferences;
        }
    }

    export(data) {
        data.chartemdadMenusReferences = this.emdadMenuReference;
    }
}
ChartemdadMenuPlugin.getters = ["getChartemdadMenu"];

coreTypes.add("LINK_emdad_MENU_TO_CHART");

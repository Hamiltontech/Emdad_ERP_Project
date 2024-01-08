/** @emdad-module */

import * as spreadsheet from "@emdad/o-spreadsheet";

const { chartComponentRegistry } = spreadsheet.registries;
const { ChartJsComponent } = spreadsheet.components;

chartComponentRegistry.add("emdad_bar", ChartJsComponent);
chartComponentRegistry.add("emdad_line", ChartJsComponent);
chartComponentRegistry.add("emdad_pie", ChartJsComponent);

import { emdadChartCorePlugin } from "./plugins/emdad_chart_core_plugin";
import { ChartemdadMenuPlugin } from "./plugins/chart_emdad_menu_plugin";
import { emdadChartUIPlugin } from "./plugins/emdad_chart_ui_plugin";

export { emdadChartCorePlugin, ChartemdadMenuPlugin, emdadChartUIPlugin };

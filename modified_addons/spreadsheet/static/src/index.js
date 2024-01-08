/** @emdad-module */

/**
 * This file is meant to load the different subparts of the module
 * to guarantee their plugins are loaded in the right order
 *
 * dependency:
 *             other plugins
 *                   |
 *                  ...
 *                   |
 *                filters
 *                /\    \
 *               /  \    \
 *           pivot  list  emdad chart
 */

/** TODO: Introduce a position parameter to the plugin registry in order to load them in a specific order */
import * as spreadsheet from "@emdad/o-spreadsheet";
const { corePluginRegistry, coreViewsPluginRegistry } = spreadsheet.registries;

import { GlobalFiltersCorePlugin, GlobalFiltersUIPlugin } from "@spreadsheet/global_filters/index";
import { PivotCorePlugin, PivotUIPlugin } from "@spreadsheet/pivot/index"; // list depends on filter for its getters
import { ListCorePlugin, ListUIPlugin } from "@spreadsheet/list/index"; // pivot depends on filter for its getters
import {
    ChartemdadMenuPlugin,
    emdadChartCorePlugin,
    emdadChartUIPlugin,
} from "@spreadsheet/chart/index"; // emdadchart depends on filter for its getters

corePluginRegistry.add("emdadGlobalFiltersCorePlugin", GlobalFiltersCorePlugin);
corePluginRegistry.add("emdadPivotCorePlugin", PivotCorePlugin);
corePluginRegistry.add("emdadListCorePlugin", ListCorePlugin);
corePluginRegistry.add("emdadChartCorePlugin", emdadChartCorePlugin);
corePluginRegistry.add("chartemdadMenuPlugin", ChartemdadMenuPlugin);

coreViewsPluginRegistry.add("emdadGlobalFiltersUIPlugin", GlobalFiltersUIPlugin);
coreViewsPluginRegistry.add("emdadPivotUIPlugin", PivotUIPlugin);
coreViewsPluginRegistry.add("emdadListUIPlugin", ListUIPlugin);
coreViewsPluginRegistry.add("emdadChartUIPlugin", emdadChartUIPlugin);

/** @emdad-module */

import * as spreadsheet from "@emdad/o-spreadsheet";
import { _t } from "@web/core/l10n/translation";
import { emdadChart } from "./emdad_chart";

const { chartRegistry } = spreadsheet.registries;

const { getDefaultChartJsRuntime, chartFontColor, ChartColors } = spreadsheet.helpers;

export class emdadBarChart extends emdadChart {
    constructor(definition, sheetId, getters) {
        super(definition, sheetId, getters);
        this.verticalAxisPosition = definition.verticalAxisPosition;
        this.stacked = definition.stacked;
    }

    getDefinition() {
        return {
            ...super.getDefinition(),
            verticalAxisPosition: this.verticalAxisPosition,
            stacked: this.stacked,
        };
    }
}

chartRegistry.add("emdad_bar", {
    match: (type) => type === "emdad_bar",
    createChart: (definition, sheetId, getters) => new emdadBarChart(definition, sheetId, getters),
    getChartRuntime: createemdadChartRuntime,
    validateChartDefinition: (validator, definition) =>
        emdadBarChart.validateChartDefinition(validator, definition),
    transformDefinition: (definition) => emdadBarChart.transformDefinition(definition),
    getChartDefinitionFromContextCreation: () => emdadBarChart.getDefinitionFromContextCreation(),
    name: _t("Bar"),
});

function createemdadChartRuntime(chart, getters) {
    const background = chart.background || "#FFFFFF";
    const { datasets, labels } = chart.dataSource.getData();
    const locale = getters.getLocale();
    const chartJsConfig = getBarConfiguration(chart, labels, locale);
    const colors = new ChartColors();
    for (const { label, data } of datasets) {
        const color = colors.next();
        const dataset = {
            label,
            data,
            borderColor: color,
            backgroundColor: color,
        };
        chartJsConfig.data.datasets.push(dataset);
    }

    return { background, chartJsConfig };
}

function getBarConfiguration(chart, labels, locale) {
    const fontColor = chartFontColor(chart.background);
    const config = getDefaultChartJsRuntime(chart, labels, fontColor, { locale });
    config.type = chart.type.replace("emdad_", "");
    const legend = {
        ...config.options.legend,
        display: chart.legendPosition !== "none",
        labels: { fontColor },
    };
    legend.position = chart.legendPosition;
    config.options.plugins = config.options.plugins || {};
    config.options.plugins.legend = legend;
    config.options.layout = {
        padding: { left: 20, right: 20, top: chart.title ? 10 : 25, bottom: 10 },
    };
    config.options.scales = {
        x: {
            ticks: {
                // x axis configuration
                maxRotation: 60,
                minRotation: 15,
                padding: 5,
                labelOffset: 2,
                color: fontColor,
            },
        },
        y: {
            position: chart.verticalAxisPosition,
            ticks: {
                color: fontColor,
                // y axis configuration
            },
            beginAtZero: true, // the origin of the y axis is always zero
        },
    };
    if (chart.stacked) {
        config.options.scales.x.stacked = true;
        config.options.scales.y.stacked = true;
    }
    return config;
}

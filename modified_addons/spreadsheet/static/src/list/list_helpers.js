/** @emdad-module */

import { getemdadFunctions } from "../helpers/emdad_functions_helpers";

/** @typedef {import("@spreadsheet/helpers/emdad_functions_helpers").Token} Token */

/**
 * Parse a spreadsheet formula and detect the number of LIST functions that are
 * present in the given formula.
 *
 * @param {Token[]} tokens
 *
 * @returns {number}
 */
export function getNumberOfListFormulas(tokens) {
    return getemdadFunctions(tokens, ["emdad.LIST", "emdad.LIST.HEADER"]).length;
}

/**
 * Get the first List function description of the given formula.
 *
 * @param {Token[]} tokens
 *
 * @returns {import("../helpers/emdad_functions_helpers").emdadFunctionDescription|undefined}
 */
export function getFirstListFunction(tokens) {
    return getemdadFunctions(tokens, ["emdad.LIST", "emdad.LIST.HEADER"])[0];
}

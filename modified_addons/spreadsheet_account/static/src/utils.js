/** @emdad-module **/
import { getemdadFunctions } from "@spreadsheet/helpers/emdad_functions_helpers";

/**
 * @typedef {import("@spreadsheet/helpers/emdad_functions_helpers").Token} Token
 * @typedef  {import("@spreadsheet/helpers/emdad_functions_helpers").emdadFunctionDescription} emdadFunctionDescription
 */

/**
 * @param {Token[]} tokens
 * @returns {number}
 */
export function getNumberOfAccountFormulas(tokens) {
    return getemdadFunctions(tokens, ["emdad.BALANCE", "emdad.CREDIT", "emdad.DEBIT"]).length;
}

/**
 * Get the first Account function description of the given formula.
 *
 * @param {Token[]} tokens
 * @returns {emdadFunctionDescription | undefined}
 */
export function getFirstAccountFunction(tokens) {
    return getemdadFunctions(tokens, ["emdad.BALANCE", "emdad.CREDIT", "emdad.DEBIT"])[0];
}

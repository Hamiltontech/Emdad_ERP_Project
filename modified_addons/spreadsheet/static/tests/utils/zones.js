/** @emdad-module */

import { helpers } from "@emdad/o-spreadsheet";

const { toUnboundedZone } = helpers;

export function toRangeData(sheetId, xc) {
    return { _zone: toUnboundedZone(xc), _sheetId: sheetId };
}

# -*- coding: utf-8 -*-
# Part of emdad. See LICENSE file for full copyright and licensing details.

from emdad import models


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(Http, self).session_info()
        if self.env.user._is_internal():
            res['emdadbot_initialized'] = self.env.user.emdadbot_state not in [False, 'not_initialized']
        return res

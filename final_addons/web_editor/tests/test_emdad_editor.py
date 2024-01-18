# -*- coding: utf-8 -*-
# Part of emdad. See LICENSE file for full copyright and licensing details.

import emdad.tests

@emdad.tests.tagged("post_install", "-at_install")
class TestemdadEditor(emdad.tests.HttpCase):

    def test_emdad_editor_suite(self):
        self.browser_js('/web_editor/tests', "", "", login='admin', timeout=1800)

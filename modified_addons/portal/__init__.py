# -*- coding: utf-8 -*-
# Part of emdad. See LICENSE file for full copyright and licensing details.

# Updating mako environement in order to be able to use slug
try:
    from emdad.tools.rendering_tools import template_env_globals
    from emdad.addons.http_routing.models.ir_http import slug

    template_env_globals.update({
        'slug': slug
    })
except ImportError:
    pass

from . import controllers
from . import models
from . import wizard

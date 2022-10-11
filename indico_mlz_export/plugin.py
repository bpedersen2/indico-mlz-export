#  -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2018 Björn Pedersen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# Created on Mar 9, 2018
#
# @author: pedersen

from __future__ import unicode_literals
from indico.core import signals
from flask import session

from indico.core.plugins import IndicoPlugin, url_for_plugin
from indico.web.http_api import HTTPAPIHook
from indico_mlz_export.blueprint import blueprint
from indico_mlz_export.api import MLZExportRegistrationsHook, MLZExportRegistrationHook, MLZExportRegistrationsFZJHook
from indico.web.menu import SideMenuItem
from indico.modules.events.features.util import is_feature_enabled

from indico_mlz_export import _
from indico_mlz_export.forms  import EventSettingsForm

class MLZExporterPlugin(IndicoPlugin):
    """MLZ registration export API plugin

    Allow for registration data export to external systems

    It offers both old-style HTTP-API (http API token authentication and new-style REST API (OAuth2 authentication)
    endpoints for exporting single registrations or list of all registrations.

    HTTP API:
        /export/mlzevent/<eventid>.{json|xml}
        /export/mlzevent/<eventid>/registrant/<registrant_id>.{json|xml}

    REST API:
        /mlz/export/<eventid>/registrants
        /mlz/export/<eventid>/registrants/<registrantid>
    """

    acl_settings = {'managers'}
    configurable = True
    event_settings_form = EventSettingsForm

    def init(self):
        super().init()
        self.connect(signals.menu.items, self.extend_event_management_menu, sender='event-management-sidemenu')
        HTTPAPIHook.register(MLZExportRegistrationsHook)
        HTTPAPIHook.register(MLZExportRegistrationsFZJHook)
        HTTPAPIHook.register(MLZExportRegistrationHook)

    def get_blueprints(self):
        yield blueprint

    def extend_event_management_menu(self, sender, event, **kwargs):
        if event.can_manage(session.user) and is_feature_enabled(event, 'fzjexport'):
            yield  SideMenuItem(
                'FZJExport',
                _('FZJ export'),
                url_for_plugin('mlz_export.api_registrants_fzj', event),
                section='services')
            yield  SideMenuItem(
                'FZJExportsettings',
                _('FZJ export settings'),
                url_for_plugin('mlz_export.configure', event),
                section='services')
            


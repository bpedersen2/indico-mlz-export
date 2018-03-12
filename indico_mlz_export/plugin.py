'''
Created on Mar 9, 2018

@author: pedersen
'''
from __future__ import unicode_literals

from indico.core.plugins import IndicoPlugin
from indico.web.http_api import HTTPAPIHook
from indico_mlz_export.blueprint import blueprint
from indico_mlz_export.api import MLZExportRegistrationsHook, MLZExportRegistrationHook


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

    def init(self):
        super(MLZExporterPlugin, self).init()
        HTTPAPIHook.register(MLZExportRegistrationsHook)
        HTTPAPIHook.register(MLZExportRegistrationHook)

    def get_blueprints(self):
        yield blueprint

'''
Created on Mar 9, 2018

@author: pedersen
'''
from __future__ import unicode_literals

from indico.core.plugins import IndicoPluginBlueprint
from indico_mlz_export.controller import RHExportRegistrations, RHExportRegistration

blueprint = IndicoPluginBlueprint('mlzexport', __name__, url_prefix='/mlz/export')
# API
blueprint.add_url_rule(
    '/<int:event_id>/registrants/<int:registrant_id>', 'api_registrant', RHExportRegistration, methods=('GET', ))
blueprint.add_url_rule('/<int:event_id>/registrants', 'api_registrants', RHExportRegistrations)

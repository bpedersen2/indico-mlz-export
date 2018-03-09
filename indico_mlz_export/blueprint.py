'''
Created on Mar 9, 2018

@author: pedersen
'''
from __future__ import unicode_literals

from indico.core.plugins import IndicoPluginBlueprint
from indico_mlz_export.controller import RHExportRegistrations

blueprint = IndicoPluginBlueprint(
    'mlzexport', __name__, url_prefix='/mlz/export')
blueprint.add_url_rule('/', 'registrations', RHExportRegistrations)

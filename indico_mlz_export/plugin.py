'''
Created on Mar 9, 2018

@author: pedersen
'''
from __future__ import unicode_literals

from indico.core.plugins import IndicoPlugin
from indico_mlz_export.blueprint import blueprint


class MLZExporterPlugin(IndicoPlugin):
    """
MLZ API pluign  for ergsitratoin data export to external systems
    """

    acl_settings = {'managers'}

    def init(self):
        super(MLZExporterPlugin, self).init()

    def get_blueprints(self):
        yield blueprint

'''
Created on Mar 9, 2018

@author: pedersen
'''
from __future__ import unicode_literals

from flask import jsonify, request
from werkzeug.exceptions import Forbidden

from indico.modules.events.models.events import Event
from indico.modules.oauth import oauth
from indico.web.rh import RH
from indico_mlz_export.api import all_registrations


class RHExportRegistrations(RH):
    """RESTful registrant API"""

    CSRF_ENABLED = False

    @oauth.require_oauth('registrants')
    def _check_access(self):
        if not Event(self.eventId).can_manage(
                request.oauth.user, permission='registration'):
            raise Forbidden()

    def _process_args(self):
        self.eventId = request.view_args['event_id']

    def _process_GET(self):
        return jsonify(all_registrations(self.eventId))

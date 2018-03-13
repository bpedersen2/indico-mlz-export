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
from indico_mlz_export.api import all_registrations, one_registration


class RHMLZExportBase(RH):
    """RESTful registrant API base class"""

    CSRF_ENABLED = False

    @oauth.require_oauth('registrants')
    def _check_access(self):
        try:
            ok = self.event.can_manage(request.oauth.user, permission='registration')
        except TypeError:
            ok = self.event.can_manage(request.oauth.user)

        if not ok:
            raise Forbidden()


class RHExportRegistrations(RHMLZExportBase):
    """ Export a list of registrations for an event"""

    def _process_args(self):
        self.event_id = request.view_args['event_id']
        self.event = Event.get(self.event_id, is_deleted=False)

    def _process_GET(self):
        return jsonify(all_registrations(self.event, False))


class RHExportRegistration(RHMLZExportBase):
    """ Export a single registration for an event"""

    def _process_args(self):
        self.event_id = request.view_args['event_id']
        self.registrant_id = request.view_args['registrant_id']
        self.event = Event.get(self.event_id, is_deleted=False)

    def _process_GET(self):
        return jsonify(one_registration(self.event, self.registrant_id, False))

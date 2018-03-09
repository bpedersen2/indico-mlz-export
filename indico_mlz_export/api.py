'''
Created on Mar 9, 2018

@author: pedersen
'''

from __future__ import unicode_literals

from collections import defaultdict

from sqlalchemy.orm import joinedload

from indico.modules.events.models.events import Event
from indico.modules.events.registration.util import build_registration_api_data
from indico.web.http_api import HTTPAPIHook
from indico.web.http_api.util import get_query_parameter


@HTTPAPIHook.register
class MLZExportRegistrationsHook(HTTPAPIHook):
    RE = r'(?P<event>[\w\s]+)'
    METHOD_NAME = 'export_registration_info'
    TYPES = ('mlzevent', )
    DEFAULT_DETAIL = 'default'
    MAX_RECORDS = {'default': 100}
    GUEST_ALLOWED = False
    VALID_FORMATS = ('json', 'jsonp', 'xml', 'ics')

    def _getParams(self):
        super(MLZExportRegistrationsHook, self)._getParams()
        self._eventId = self._pathParams['event']
        self.event = Event.get(self._eventId, is_deleted=False)
        self.flat = get_query_parameter(self._queryParams, ['flat'], False)

    def _has_access(self, user):
        return self.event.can_manage(user, permission='registration')

    def export_registration_info(self, user):
        return all_registrations(self.event, self.flat)


def all_registrations(event, flat):
    _registrations = (event.registrations.filter_by(is_deleted=False)
                      .options(joinedload('data').joinedload('field_data'))
                      .all())
    result = []
    for r in _registrations:
        one_res = build_registration_api_data(r)
        one_res['data'] = all_fields(r, flat)
        one_res['price'] = r.price
        result.append(one_res)
    return result


def all_fields(registration, flat=False):
    reg_data = registration.data_by_field
    if flat:
        data = dict()
        titles = dict()
    else:
        data = defaultdict(dict)
    for section in registration.sections_with_answered_fields:
        for field in section.active_fields:
            if field.id not in reg_data:
                continue
            if flat:
                data[field.id] = reg_data[field.id].friendly_data
                titles[field.id] = '{}:{}'.format(section.title, field.title)
            else:
                data[section.title][field.title] = reg_data[field.id].friendly_data
    if flat:
        return [data, titles]
    return dict(data)

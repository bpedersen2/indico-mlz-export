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


class MLZExportBase(HTTPAPIHook):
    """Base class for Mlz export http api"""

    METHOD_NAME = 'export_registration_info'
    TYPES = ('mlzevent', )
    DEFAULT_DETAIL = 'default'
    MAX_RECORDS = {'default': 100}
    GUEST_ALLOWED = False
    VALID_FORMATS = ('json', 'jsonp', 'xml')

    def _getParams(self):
        super(MLZExportBase, self)._getParams()
        self.event_id = self._pathParams['event']
        self.event = Event.get(self.event_id, is_deleted=False)
        self.flat = get_query_parameter(self._queryParams, ['flat'], False)

    def _has_access(self, user):
        return self.event.can_manage(user, permission='registration')


class MLZExportRegistrationsHook(MLZExportBase):
    """Export a lis tof registrations (with full infos)"""

    RE = r'(?P<event>[\w\s]+)'

    def export_registration_info(self, user):
        return all_registrations(self.event, self.flat)


class MLZExportRegistrationHook(MLZExportBase):
    """Export a single registration"""

    RE = r'(?P<event>[\w\s]+)/registrant/(?P<registrant>[\w\s]+)'

    def _getParams(self):
        super(MLZExportRegistrationHook, self)._getParams()
        self.registrant_id = self._pathParams['registrant']

    def export_registration_info(self, user):
        return one_registration(self.event, self.registrant_id, self.flat)


def all_registrations(event, flat):
    """Helper to generate data for all registrations in an event"""
    _registrations = (event.registrations.filter_by(is_deleted=False).options(
        joinedload('data').joinedload('field_data')).all())
    result = []
    for _registration in _registrations:
        result.append(process_field_data(_registration, flat))
    return result


def one_registration(event, registrant_id, flat):
    """Helper to generate data for one registration in an event"""
    _registration = (event.registrations.filter_by(id=registrant_id, is_deleted=False).options(
        joinedload('data').joinedload('field_data')).first_or_404())
    if _registration:
        return process_field_data(_registration, flat)
    return None


def process_field_data(_registration, flat):
    """Helper to generate field data for one registration"""
    one_res = build_registration_api_data(_registration)
    one_res['data'] = all_fields(_registration, flat)
    one_res['price'] = _registration.price
    return one_res


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

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

import re
from collections import defaultdict
from io import StringIO, BytesIO
from csv import DictWriter, QUOTE_ALL

from sqlalchemy.orm import joinedload

from indico.modules.events.models.events import Event
from indico.modules.events.registration.util import build_registration_api_data
from indico.web.http_api import HTTPAPIHook
from indico.web.http_api.util import get_query_parameter
from indico_mlz_export import mlzexport_event_settings
from indico.web.flask.util import send_file


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
        try:
            # v2.1+
            return self.event.can_manage(user, permission='registration')
        except TypeError:
            # v2.0
            return self.event.can_manage(user)


class MLZExportRegistrationsHook(MLZExportBase):
    """Export a lis tof registrations (with full infos)"""

    RE = r'(?P<event>[\w\s]+)'

    def export_registration_info(self, user):
        return all_registrations(self.event, self.flat)


class MLZExportRegistrationsFZJHook(MLZExportBase):
    """Export a list of registrations (as FZJ compliant CSV)"""

    RE = r'(?P<event>[\w\s]+)'

    def export_registration_info(self, user):
        return all_registrations_csv(self.event)


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
    _registrations = (event.registrations.filter_by(is_deleted=False, is_active=True).options(
        joinedload('data').joinedload('field_data')).all())
    result = []
    for _registration in _registrations:
        result.append(process_field_data(_registration, flat))
    return result


def all_registrations_csv(event):
    an = {'male': 'Mr.', 'female': 'Mrs.', 'divers': ''}
    result = []
    _registrations = (event.registrations.filter_by(is_deleted=False, is_active=True, is_paid=False).options(
        joinedload('data').joinedload('field_data')).all())
    for _registration in _registrations:
        registration = build_registration_api_data(_registration)
        pd = registration['personal_data']
        reg_data = _registration.data_by_field
        rdata = {}
        field_title_map = {}
        for section in _registration.sections_with_answered_fields:
            for field in section.active_fields:
                if field.id not in reg_data:
                    continue
                ft = ft_to_logickey(field.title)
                if ft == 'country':
                    rdata[ft] = reg_data[field.id].data
                else:
                    rdata[ft] = reg_data[field.id].friendly_data
        street = rdata['street']
        plz = rdata['plz']
        city = rdata['city']
        vat = ''
        invoice_x = ''
        other_address = rdata.get('invoiceaddress')
        if other_address:
            address = other_address.split('\n')
            al = len(address)
            if al == 3:
                invoice_x = address[0]
                street = address[1]
                plz, city = address[2].split(' ')[:2]
        vat = rdata.get('vat', '')
        data = {}
        data['status'] = ''
        data['veranstaltungsschluessel'] = mlzexport_event_settings.get(event, 'veranstaltungsid', '<unset>')

        data['bsecname1'] = rdata.get('bsecname1')
        data['bsecname2'] = rdata.get('bsecname2')
        data['bsecname3'] = rdata.get('bsecname3')
        data['bsecname4'] = ''
        data['postfach'] = ''
        data['strasse'] = street
        data['plz'] = plz
        data['ort'] = city
        data['land'] = rdata.get('country')
        gender = pd.get('Gender', 'divers')
        data['anrede'] = rdata.get('formofaddress', an[gender])
        data['titel'] = rdata.get('title', '')
        data['vorname'] = pd.get('firstName')
        data['nachname'] = pd.get('surname')
        data['mail'] = pd.get('email')
        data['teilnehmer_intern'] = '1' if 'fz-juelich.de' in pd.get('email') else '0'
        data['sprache'] = 'EN'
        data['ust_id_nr'] = vat
        data['betrag'] = registration.get('ticket_price', 0)
        data['zahlweise'] = 'U'
        data['rechnungsnummer'] = ''
        result.append(data)
    return to_csv(result)


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
    ## local migration code
    if 'datatitle' in one_res:
        del one_res['datatitle']
    one_res['data'] = all_fields(_registration, flat)
    one_res['price'] = _registration.price
    if _registration.state is not None:
        one_res['state'] = _registration.state.title
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


def to_csv(data):
    res = StringIO()
    csv = DictWriter(res, data[0].keys(), dialect='excel', delimiter=';', quoting=QUOTE_ALL)
    csv.writeheader()
    csv.writerows(data)
    r2 = BytesIO(res.getvalue().encode('utf-8'))
    res.close()
    rv = send_file('fzj.csv', r2, 'text/csv')
    return rv


FZJ_MAPPING = {
    'bsecname1': re.compile(r'acronym|(affiliation.*badge)'),
    'bsecname2': re.compile(r'(institution$)|(affiliation(?!.*badge))'),
    'bsecname3': re.compile(r'department'),
    'plz': re.compile(r'zip|plz|postleitzahl'),
    'city': re.compile(r'city'),
    'street': re.compile(r'street|strasse'),
    'titel': re.compile(r'title|titel'),
    'country': re.compile(r'country|land'),
    'vat': re.compile(r'vat\s*id'),
    'invoiceaddress': re.compile(r'invoiceaddress'),
    'formofaddress': re.compile(r'form\s*of\s*address|anrede'),
}


def ft_to_logickey(ft):
    for key, r_e in FZJ_MAPPING.items():
        if r_e.search(ft.lower()):
            return key
    return re.sub(r'\s+', '', ft.lower())

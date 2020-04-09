#!/usr/bin/env python
import argparse
import sys
from StringIO import StringIO

import requests
import simplejson as json
from lxml import html
from requests_oauthlib import OAuth2Session

#

# Credentials you get from registering a new application
client_id = '<>'
client_secret = '<>'

scopes = ['registrants', 'read:legacy_api', 'read:user']
redirect_uri = 'https://localhost/'

target_base = 'https://<indico host>/'
target_verify = True
# OAuth endpoints given in the GitHub API documentation
authorization_base_url = target_base + 'oauth/authorize'
token_url = target_base + 'oauth/token'


def getsession(username, password):
    indico = OAuth2Session(client_id, scope=scopes, redirect_uri=redirect_uri)
    indico.verify = target_verify

    authorization_url, state = indico.authorization_url(authorization_base_url)

    s = requests.Session()
    s.verify = target_verify
    res = s.get(
        authorization_url,
        headers={
            'X-CSRF-Token': '00000000-0000-0000-0000-000000000000'
        })

    res = s.post(
        res.url,
        data={
            '_provider': '<>', #whatever you use as auth providers
            'username': username,
            'password': password,
            'csrf_token': '00000000-0000-0000-0000-000000000000'
        })

    tree = html.parse(StringIO(res.text))
    csrf = tree.xpath('//*[@id="csrf_token"]')[0].value

    def handle_url(res, **kwds):
        if res.headers['Location'].startswith(redirect_uri):
            res.url = res.headers['Location']
            del res.headers['Location']
        return res

    res = s.post(
        res.url,
        data={
            '_provider': '<>', # what you use as auth provider
            'username': username,
            'password': password,
            'csrf_token': csrf
        },
        hooks=dict(response=handle_url))

    # Fetch the access token
    indico.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=res.url,
        verify=target_verify)
    return indico


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('username')
    ap.add_argument('password')
    ap.add_argument('--flat', type=bool, default=False)
    ap.add_argument('--confid', type=int, default=56)
    args = ap.parse_args()

    indico = getsession(args.username, args.password)
    if not args.flat:
        # Fetch all registrants
        registrants_base = 'mlz/export/{.confid}/registrants'.format(args)
        #registrants_base = 'api/events/{.confid}/registrants'.format(args)
        r = indico.get(target_base + registrants_base)
        registrants = json.loads(r.content)

        for r in registrants:
            registrant_base = registrants_base + '/{registrant_id}'.format(**r)
            res = indico.get(target_base + registrant_base)
            print res.content

    if args.flat:
        # Fetch all registrants (flattend format with ids
        registrants_base = 'mlz/export/{.confid}/registrants_flat'.format(args)

        #registrants_base = 'api/events/{.confid}/registrants'.format(args)
        r = indico.get(target_base + registrants_base)
        registrants = json.loads(r.content)


        for r in registrants:
            registrant_base = registrants_base + '/{registrant_id}'.format(**r)
            res = indico.get(target_base + registrant_base)
            print res.content
 

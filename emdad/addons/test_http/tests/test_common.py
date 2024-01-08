# Part of emdad. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

import emdad
from emdad.http import Session
from emdad.addons.base.tests.common import HttpCaseWithUserDemo
from emdad.tools.func import lazy_property
from emdad.addons.test_http.utils import MemoryGeoipResolver, MemorySessionStore


class TestHttpBase(HttpCaseWithUserDemo):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        geoip_resolver = MemoryGeoipResolver()
        session_store = MemorySessionStore(session_class=Session)

        lazy_property.reset_all(emdad.http.root)
        cls.addClassCleanup(lazy_property.reset_all, emdad.http.root)
        cls.classPatch(emdad.conf, 'server_wide_modules', ['base', 'web', 'test_http'])
        cls.classPatch(emdad.http.Application, 'session_store', session_store)
        cls.classPatch(emdad.http.Application, 'geoip_city_db', geoip_resolver)
        cls.classPatch(emdad.http.Application, 'geoip_country_db', geoip_resolver)

    def setUp(self):
        super().setUp()
        emdad.http.root.session_store.store.clear()

    def db_url_open(self, url, *args, allow_redirects=False, **kwargs):
        return self.url_open(url, *args, allow_redirects=allow_redirects, **kwargs)

    def nodb_url_open(self, url, *args, allow_redirects=False, **kwargs):
        with patch('emdad.http.db_list') as db_list, \
             patch('emdad.http.db_filter') as db_filter:
            db_list.return_value = []
            db_filter.return_value = []
            return self.url_open(url, *args, allow_redirects=allow_redirects, **kwargs)

    def multidb_url_open(self, url, *args, allow_redirects=False, dblist=(), **kwargs):
        dblist = dblist or self.db_list
        assert len(dblist) >= 2, "There should be at least 2 databases"
        with patch('emdad.http.db_list') as db_list, \
             patch('emdad.http.db_filter') as db_filter, \
             patch('emdad.http.Registry') as Registry:
            db_list.return_value = dblist
            db_filter.side_effect = lambda dbs, host=None: [db for db in dbs if db in dblist]
            Registry.return_value = self.registry
            return self.url_open(url, *args, allow_redirects=allow_redirects, **kwargs)

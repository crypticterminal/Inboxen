##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django import test
from django.conf import settings as dj_settings
from django.core import urlresolvers
from django.core.cache import cache

from inboxen import models

class LoginTestCase(test.TestCase):
    """Test various login things"""
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        super(LoginTestCase, self).setUp()
        cache.clear()

    def test_last_login(self):
        login = self.client.login(username="isdabizda", password="123456")
        self.assertEqual(login, True)

        user = models.User.objects.get(username="isdabizda")
        self.assertEqual(user.last_login, user.date_joined)

    def test_normal_login(self):
        response = self.client.get(urlresolvers.reverse("user-home"))
        self.assertEqual(response.status_code, 302)

        params = {"username": "isdabizda", "password": "123456"}
        response = self.client.post(dj_settings.LOGIN_URL, params)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(urlresolvers.reverse("user-home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["request"].user.is_authenticated(), True)

    def test_ratelimit(self):
        params = {"username": "isdabizda", "password": "bad password"}
        response = self.client.post(dj_settings.LOGIN_URL, params)
        self.assertEqual(response.status_code, 200)
        for i in range(100):
            resp = self.client.post(dj_settings.LOGIN_URL, params=params)

        params["password"] = "123456"
        response = self.client.post(dj_settings.LOGIN_URL, params=params)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(urlresolvers.reverse("user-home"))
        self.assertEqual(response.status_code, 302)

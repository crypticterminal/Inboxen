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
from django.contrib.auth import get_user_model
from django.core import urlresolvers

from blog import models

BODY = """
Hey there!
==========

This is a test post:

* A list item
* And another

Bye!
"""

class BlogTestCase(test.TestCase):
    fixtures = ['inboxen_testdata.json']

    def test_blog_index(self):
        url = urlresolvers.reverse("blog")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_blog_post(self):
        user = get_user_model().objects.get(username="isdabizda")
        user.is_staff = True
        user.save()

        login = self.client.login(username=user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

        params = {"title": "A Test Post", "body": BODY}
        response = self.client.post(urlresolvers.reverse("blog-post-add"), params)

        self.assertRedirects(response, urlresolvers.reverse("blog"))

        post = models.BlogPost.objects.latest("date")
        self.assertEqual(post.subject, "A Test Post")
        self.assertEqual(post.body, BODY)
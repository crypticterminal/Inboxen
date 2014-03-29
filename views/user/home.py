##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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


from django.utils.translation import ugettext as _
from django.views import generic
from django.db.models import F

from inboxen import models
from website.views import base

class UserHomeView(base.CommonContextMixin, base.LoginRequiredMixin, generic.ListView):
    """ The user's home which lists the inboxes """
    allow_empty = True
    paginate_by = 100
    template_name = "user/home.html"
    title = _("Home")

    def get_queryset(self):
        queryset = self.request.user.inbox_set.filter(flags=~models.Inbox.flags.deleted)
        queryset = queryset.select_related("domain")
        return queryset.order_by("-created")

    def process_messages(self, inboxes):
        """Get tags"""
        if len(inboxes) == 0:
            return

        tag_set = {}
        tag_list = models.Tag.objects.filter(inbox__in=inboxes).values_list("inbox_id", "tag")
        for id, tag in tag_list:
            tags = tag_set.get(id, [])
            tags.append(tag)
            tag_set[id] = tags

        for inbox in inboxes:
            inbox.tags = ", ".join(tag_set.get(inbox.id, []))

    def get_context_data(self, *args, **kwargs):
        context = super(UserHomeView, self).get_context_data(*args, **kwargs)
        self.process_messages(context["object_list"])
        return context

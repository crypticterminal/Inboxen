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

from datetime import datetime
import difflib

from pytz import utc


def diff_creator(sender, instance, **kwargs):
    if instance.last_modified is None:
        modified = datetime.now(utc)
    else:
        modified = instance.last_modified

    try:
        last = sender.objects.exclude(id=instance.id, last_modified__gte=modified)
        last = last.filter(published=True).only("text", "last_modified").latest()
    except sender.DoesNotExist:
        class last_object(object):
            text = ""
            last_modified = None
        last = last_object()

    # make sure we have a new line at the end - always
    if len(last.text) > 0 and last.text[-1] != "\n":
        last.text = last.text + "\n"
    if len(instance.text) == 0 or instance.text[-1] != "\n":
        instance.text = instance.text + "\n"

    differ = difflib.unified_diff(
        last.text.split("\n"),
        instance.text.split("\n"),
        fromfile=str(last.last_modified),
        tofile=str(instance.last_modified)
    )
    instance.diff = "".join(differ)
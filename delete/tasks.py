import logging
import types
from datetime import datetime

from celery import chain, chord, group, task
from pytz import utc

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from inboxen.models import Email, Inbox, Tag, User

log = logging.getLogger(__name__)

@task(rate_limit="10/m", default_retry_delay=5 * 60) # 5 minutes
@transaction.atomic()
def delete_inbox(email, username=None):
    inbox = Inbox.objects

    if username is not None:
        inbox = Inbox.objects.filter(user__username=username)

    try:
        inbox = inobx.from_string(email=email)
    except Inbox.DoesNotExist:
        return False

    # delete emails in another task(s)
    emails = inbox.email_set.only('id')

    # sending an ID over the wire and refetching the Django model on the side
    # is cheaper than serialising the Django model - this appears to be the
    # cause of our previous memory issues! - M
    emails = group([delete_email.s(email.id) for email in emails])
    try:
        emails.apply_async()
    except IndexError:
        # no emails in this inbox
        pass

    # okay now mark the inbox as deleted
    inbox.created = datetime.fromtimestamp(0, utc)
    inbox.deleted = True
    inbox.save()

    return True

@task(rate_limit=200)
@transaction.atomic()
def delete_email(email_id):
    email = Email.objects.only('id').get(id=email_id)
    email.delete()

@task(rate_limit=200)
@transaction.atomic()
def delete_inboxen_item(model, item_id):
    _model = ContentType.objects.get(app_label="inboxen", model=model).model_class()

    item = _model.objects.only('id').get(id=item_id)
    item.delete()

@task()
@transaction.atomic()
def disown_inbox(result, inbox_id):
    # delete tags
    tags = Tag.objects.filter(inbox__id=inbox_id).only('id')
    tags.delete()

    inbox.user = None
    inbox.save()

@task()
@transaction.atomic()
def delete_user(result, username):
    inbox = Inbox.objects.filter(user__username=username).only('id').exists()
    if inbox:
        raise Exception("User {0}  still has inboxes!".format(username))
    else:
        log.debug("Deleting user %s" % username)
        user.delete()
    return True

@task()
@transaction.atomic()
def delete_account(user):
    # first we need to make sure the user can't login
    user.set_unusable_password()
    user.is_active = False
    user.save()

    # get ready to delete all inboxes
    inboxes = user.inbox_set.only('id')
    if len(inboxes): # pull in all the data
        delete = chord([chain(delete_inbox.s(inbox.id), disown_inbox.s(inbox.id)) for inbox in inboxes], delete_user.s(username))
        delete.apply_async()

    log.debug("Deletion tasks for %s sent off", user.username)

@task(rate_limit="1/m")
@transaction.atomic()
def major_cleanup_items(model, filter_args=None, filter_kwargs=None, batch_number=1000, count=0):
    """If something goes wrong and you've got a lot of orphaned entries in the
    database, then this is the task you want.

    * model is a string
    * filter_args and filter_kwargs should be obvious
    * batch_number is the number of delete tasks that get sent off in one go
    """
    _model = ContentType.objects.get(app_label="inboxen", model=model).model_class()

    if filter_args and filter_kwargs:
        items = _model.objects.only('id').filter(*filter_args, **filter_kwargs)
    elif filter_args:
        items = _model.objects.only('id').filter(*filter_args)
    elif filter_kwargs:
        items = _model.objects.only('id').filter(**filter_kwargs)
    else:
        raise Exception("You need to specify some filter options!")

    tasks = [delete_inboxen_item.s(model, item.id) for item in items[:batch_number]]

    if len(tasks):
        tasks = chord(tasks, major_cleanup_items.si(model, filter_args, filter_kwargs, batch_number, count+1))
        tasks.apply_async()
        log.warning("%s deletes sent (overestimate), %s completed", batch_number, count*batch_number)
    else:
        log.warning("Batch deletes finished")

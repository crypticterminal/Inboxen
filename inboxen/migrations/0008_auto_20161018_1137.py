# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-18 11:37
from __future__ import unicode_literals

import annoying.fields
from django.conf import settings
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inboxen', '0007_auto_20161002_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='inboxenprofile', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]

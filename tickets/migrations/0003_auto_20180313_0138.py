# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-13 01:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_auto_20171231_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]

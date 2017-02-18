# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-18 21:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_helpindex_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apppage',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='helpindex',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='helppage',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='peoplepage',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]

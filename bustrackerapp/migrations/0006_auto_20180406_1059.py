# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-06 10:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bustrackerapp', '0005_busstop_reverse'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='busstop',
            name='reverse',
        ),
        migrations.AddField(
            model_name='bus',
            name='reverse',
            field=models.BooleanField(default=False),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-07 07:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bustrackerapp', '0006_auto_20180406_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='currSeq',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

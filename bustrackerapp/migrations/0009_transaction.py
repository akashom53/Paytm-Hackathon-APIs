# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-07 13:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bustrackerapp', '0008_auto_20180407_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userId', models.IntegerField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.FloatField(default=0.0)),
                ('startStation', models.IntegerField()),
                ('stopsStation', models.IntegerField()),
            ],
        ),
    ]

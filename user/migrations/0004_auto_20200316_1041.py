# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2020-03-16 10:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20200316_0621'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='logintoken',
            name='expiry_time',
        ),
        migrations.RemoveField(
            model_name='logintoken',
            name='is_valid',
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-12-05 15:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0032_auto_20171205_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='lng',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

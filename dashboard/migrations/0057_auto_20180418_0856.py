# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-04-18 08:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0056_auto_20180412_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entityproxy',
            name='externalId',
            field=models.CharField(default='0', max_length=50),
        ),
    ]

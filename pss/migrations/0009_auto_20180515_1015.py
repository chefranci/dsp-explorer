# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-05-15 10:15
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import pss.models


class Migration(migrations.Migration):

    dependencies = [
        ('pss', '0008_auto_20180409_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='zip_location',
            field=models.FileField(max_length=500, storage=django.core.files.storage.FileSystemStorage(location=b'pss/application'), upload_to=pss.models.upload_to_and_rename, verbose_name='Zip Location'),
        ),
    ]

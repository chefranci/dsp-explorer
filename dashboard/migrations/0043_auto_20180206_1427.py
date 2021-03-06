# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-02-06 14:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0042_auto_20180206_1000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='video_link',
        ),
        migrations.AddField(
            model_name='challenge',
            name='notify_admin',
            field=models.BooleanField(default=True, verbose_name='Notifiy Coordinator when user add/remove interest'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='notify_user',
            field=models.BooleanField(default=True, verbose_name='Notifiy User when removes interest'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='challenges', to='dashboard.Company'),
        ),
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(upload_to='images/company', verbose_name='Logo'),
        ),
    ]

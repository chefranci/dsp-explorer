# Generated by Django 2.0.5 on 2018-07-17 10:28

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dashboard', '0063_auto_20180717_1028'),
    ]

    operations = [
        migrations.CreateModel(
            name='Twitter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.CharField(max_length=200)),
                ('app_secret', models.CharField(max_length=200)),
                ('redirect_url', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='TwitterProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=200)),
                ('secret_access_token', models.CharField(max_length=200)),
                ('token_type', models.CharField(default='Bearer', max_length=30)),
                ('expires_in', models.CharField(max_length=30)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Profile')),
            ],
        ),
    ]

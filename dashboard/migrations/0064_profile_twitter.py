# Generated by Django 2.0.5 on 2018-07-17 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0063_auto_20180717_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='twitter',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 2.0.5 on 2018-07-17 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0062_auto_20180525_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='message_text',
            field=models.TextField(max_length=500),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]

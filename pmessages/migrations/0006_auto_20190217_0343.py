# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-17 02:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pmessages', '0005_proxymessage_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proxymessage',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pmessages.ProxyUser'),
        ),
    ]

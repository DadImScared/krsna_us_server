# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-10 05:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harikatha', '0013_playlistitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlistitem',
            name='item_order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]

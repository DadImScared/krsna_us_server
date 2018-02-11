# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-09 02:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('harikatha', '0012_auto_20180208_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaylistItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('collection_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harikatha.HarikathaCollection')),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='harikatha.Playlists')),
            ],
        ),
    ]

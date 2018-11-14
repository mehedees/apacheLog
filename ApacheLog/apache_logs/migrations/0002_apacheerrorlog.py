# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-14 12:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('log_formats', '0001_initial'),
        ('apache_logs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApacheErrorLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_line', models.TextField()),
                ('time', models.TextField()),
                ('log_module', models.TextField(null=True)),
                ('log_level', models.TextField()),
                ('pid', models.IntegerField(null=True)),
                ('tid', models.IntegerField(null=True)),
                ('src_fileName', models.TextField(null=True)),
                ('status', models.TextField(null=True)),
                ('remote_host', models.GenericIPAddressField(null=True)),
                ('error_msg', models.TextField(null=True)),
                ('referer', models.TextField(null=True)),
                ('log_format', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='log_formats.LogFormats')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
            ],
        ),
    ]

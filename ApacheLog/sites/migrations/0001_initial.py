# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-28 12:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=100)),
                ('site_url', models.CharField(max_length=400)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='site',
            unique_together=set([('site_name', 'site_url')]),
        ),
    ]

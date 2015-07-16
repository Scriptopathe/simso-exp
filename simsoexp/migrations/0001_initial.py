# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigurationFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('conf', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('metrics', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SchedulingPolicy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.TextField()),
                ('sha1', models.TextField()),
                ('md5', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TestSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('files', models.ManyToManyField(to='simsoexp.ConfigurationFile')),
            ],
        ),
        migrations.AddField(
            model_name='results',
            name='scheduling_policy',
            field=models.ForeignKey(to='simsoexp.SchedulingPolicy'),
        ),
        migrations.AddField(
            model_name='results',
            name='test_set',
            field=models.ForeignKey(to='simsoexp.TestSet'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0014_auto_20150724_0958'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('count', models.IntegerField()),
                ('avg', models.FloatField()),
                ('std', models.FloatField()),
                ('median', models.FloatField()),
            ],
        ),
        migrations.RemoveField(
            model_name='results',
            name='aborted_jobs',
        ),
        migrations.RemoveField(
            model_name='results',
            name='jobs',
        ),
        migrations.RemoveField(
            model_name='results',
            name='migrations',
        ),
        migrations.RemoveField(
            model_name='results',
            name='norm_laxity',
        ),
        migrations.RemoveField(
            model_name='results',
            name='on_schedule',
        ),
        migrations.RemoveField(
            model_name='results',
            name='preemptions',
        ),
        migrations.RemoveField(
            model_name='results',
            name='sys_preempt',
        ),
        migrations.RemoveField(
            model_name='results',
            name='task_migrations',
        ),
        migrations.RemoveField(
            model_name='results',
            name='timers',
        ),
        migrations.AddField(
            model_name='results',
            name='metrics',
            field=models.ManyToManyField(to='simsoexp.Metric'),
        ),
    ]

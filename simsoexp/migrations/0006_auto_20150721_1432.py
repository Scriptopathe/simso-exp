# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0005_schedulingpolicy_class_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='results',
            name='metrics',
        ),
        migrations.AddField(
            model_name='results',
            name='aborted_jobs',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='jobs',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='migrations',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='norm_laxity',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='on_schedule',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='preemptions',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='sys_preempt',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='task_migrations',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='timers',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

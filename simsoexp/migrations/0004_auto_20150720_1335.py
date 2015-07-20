# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0003_auto_20150717_1118'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testcategory',
            name='description',
        ),
        migrations.AddField(
            model_name='configurationfile',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='results',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedulingpolicy',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='testcategory',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='testset',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]

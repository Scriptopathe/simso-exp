# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0004_auto_20150720_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulingpolicy',
            name='class_name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0017_auto_20150727_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='metric',
            name='maximum',
            field=models.FloatField(default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='metric',
            name='minimum',
            field=models.FloatField(default=-1),
            preserve_default=False,
        ),
    ]

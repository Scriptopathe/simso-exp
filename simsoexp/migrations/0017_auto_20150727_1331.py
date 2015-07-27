# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0016_auto_20150724_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metric',
            name='count',
            field=models.FloatField(),
        ),
    ]

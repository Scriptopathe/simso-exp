# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0015_auto_20150724_1054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configurationfile',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='testcategory',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='testset',
            name='approved',
        ),
    ]

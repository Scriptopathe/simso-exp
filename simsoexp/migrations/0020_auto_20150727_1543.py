# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0019_auto_20150727_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcategory',
            name='description',
            field=models.TextField(default='default description'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testset',
            name='description',
            field=models.TextField(default='default description'),
            preserve_default=False,
        ),
    ]

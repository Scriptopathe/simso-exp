# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0002_auto_20150717_1035'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testset',
            old_name='catetories',
            new_name='categories',
        ),
    ]

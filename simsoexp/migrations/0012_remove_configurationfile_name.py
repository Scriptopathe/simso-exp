# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0011_notification_ntype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configurationfile',
            name='name',
        ),
    ]

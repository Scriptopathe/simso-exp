# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0022_auto_20150806_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='unread_only',
            field=models.BooleanField(default=False),
        ),
    ]

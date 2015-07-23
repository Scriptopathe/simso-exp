# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0010_notification_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='ntype',
            field=models.CharField(default='danger', max_length=255),
            preserve_default=False,
        ),
    ]

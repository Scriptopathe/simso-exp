# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('simsoexp', '0018_auto_20150727_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='testset',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='testset',
            name='contributor',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]

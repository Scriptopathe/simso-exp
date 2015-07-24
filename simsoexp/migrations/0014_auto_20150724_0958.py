# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simsoexp', '0013_results_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='results',
            old_name='user',
            new_name='contributor',
        ),
    ]

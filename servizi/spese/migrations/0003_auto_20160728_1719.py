# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-28 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spese', '0002_auto_20160728_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='amount'),
        ),
    ]
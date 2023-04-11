# Generated by Django 4.1.7 on 2023-04-11 07:02

import SiteServe.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SiteServe', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staticpage',
            options={'ordering': ('nav_ordering', 'slug')},
        ),
        migrations.AddField(
            model_name='staticpage',
            name='nav_ordering',
            field=models.PositiveSmallIntegerField(default=SiteServe.models.NAV_ORDERING_CALCULATOR),
        ),
    ]

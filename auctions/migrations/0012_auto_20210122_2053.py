# Generated by Django 3.1.4 on 2021-01-22 20:53

import auctions.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_auto_20210120_2248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='bg_colour',
            field=models.CharField(choices=[('#B0C4DE', 'Light Steel Blue'), ('#87CEFA', 'Light Sky Blue'), ('#87CEEB', 'Sky Blue'), ('#ADD8E6', 'Light Blue'), ('#B0E0E6', 'Powder Blue'), ('#E0FFFF', 'Light Cyan'), ('#AFEEEE', 'Pale Turquoise'), ('#66CDAA', 'Aquamarine'), ('#20B2AA', 'Light Sea Green')], default=auctions.utils.get_random_colour, max_length=16),
        ),
    ]

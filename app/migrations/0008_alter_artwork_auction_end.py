# Generated by Django 4.2.13 on 2024-06-22 16:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_artwork_seller_alter_artwork_auction_end'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='auction_end',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 29, 16, 33, 37, 931720, tzinfo=datetime.timezone.utc)),
        ),
    ]

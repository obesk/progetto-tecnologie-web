# Generated by Django 4.2.13 on 2024-06-08 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_category_options_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-08 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_artwork_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artwork',
            name='price',
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Bids', to='app.artwork')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Bids', to='app.customer')),
            ],
            options={
                'verbose_name_plural': 'Bids',
            },
        ),
    ]

# Generated by Django 2.1.5 on 2019-05-03 17:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Franchise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('franchise_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Glace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parfum_text', models.CharField(max_length=50)),
                ('parfum_id', models.IntegerField(default=0)),
                ('poids', models.FloatField(default=0)),
                ('date_prod', models.DateField(verbose_name='date de production')),
                ('date_dlc', models.DateField(default=django.utils.timezone.now, verbose_name='date limite de consommation')),
                ('no_lot', models.CharField(max_length=50)),
                ('status', models.CharField(default='Disponible', max_length=20)),
                ('franchise_name', models.CharField(default='None', max_length=100)),
                ('commande_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Parfum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parfum_text', models.CharField(max_length=50)),
                ('sorbet', models.BooleanField(default=False)),
            ],
        ),
    ]

# Generated by Django 3.1 on 2020-09-06 13:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IsUpdateMng',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_update', models.CharField(max_length=1)),
                ('insert_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
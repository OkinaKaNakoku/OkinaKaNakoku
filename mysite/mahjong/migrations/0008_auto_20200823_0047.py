# Generated by Django 3.1 on 2020-08-22 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong', '0007_hansosum_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hansosum',
            name='rank',
            field=models.CharField(max_length=1),
        ),
    ]

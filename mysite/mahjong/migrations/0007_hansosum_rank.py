# Generated by Django 3.1 on 2020-08-22 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong', '0006_hansosum_score_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='hansosum',
            name='rank',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
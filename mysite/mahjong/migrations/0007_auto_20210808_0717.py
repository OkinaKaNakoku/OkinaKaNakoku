# Generated by Django 3.1 on 2021-08-07 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong', '0006_gamestatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameresult',
            name='huro_div',
            field=models.IntegerField(default=9),
        ),
        migrations.AddField(
            model_name='gameresult',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]

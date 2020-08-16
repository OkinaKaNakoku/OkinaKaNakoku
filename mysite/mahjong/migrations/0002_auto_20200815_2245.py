# Generated by Django 3.1 on 2020-08-15 13:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='hansosum',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.DO_NOTHING, to='mahjong.userinfo'),
        ),
        migrations.DeleteModel(
            name='MahjongScore',
        ),
    ]

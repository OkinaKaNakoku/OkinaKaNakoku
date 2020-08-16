# Generated by Django 3.1 on 2020-08-15 13:35

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HansoSum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hanso_id', models.IntegerField()),
                ('user_id', models.CharField(max_length=4)),
                ('insert_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=4)),
                ('last_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('eng_last_name', models.CharField(max_length=100, null=True)),
                ('eng_first_name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MahjongScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('insert_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.DO_NOTHING, to='mahjong.userinfo')),
            ],
        ),
        migrations.AddConstraint(
            model_name='hansosum',
            constraint=models.UniqueConstraint(fields=('hanso_id', 'user_id'), name='unique_booking'),
        ),
    ]

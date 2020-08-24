# Generated by Django 3.1 on 2020-08-24 12:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=4)),
                ('last_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('eng_last_name', models.CharField(max_length=100, null=True)),
                ('eng_first_name', models.CharField(max_length=100, null=True)),
                ('score_sum', models.DecimalField(decimal_places=1, default=0.0, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='HansoSum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hanso_id', models.IntegerField()),
                ('rank', models.CharField(max_length=1)),
                ('score', models.IntegerField(default=0)),
                ('score_result', models.DecimalField(decimal_places=1, default=0.0, max_digits=6)),
                ('insert_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.DO_NOTHING, to='mahjong.userinfo')),
            ],
        ),
        migrations.AddConstraint(
            model_name='hansosum',
            constraint=models.UniqueConstraint(fields=('hanso_id', 'user_id'), name='unique_booking'),
        ),
    ]

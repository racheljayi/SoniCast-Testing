# Generated by Django 5.0 on 2023-12-24 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SontiCastApp', '0002_rename_users_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='access_token_information',
        ),
        migrations.RemoveField(
            model_name='user',
            name='location_information',
        ),
        migrations.AddField(
            model_name='user',
            name='access_token',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='ip_address',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='refresh_token',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='region',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='playlist_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_spotify_id',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
# Generated by Django 5.1.1 on 2024-09-07 08:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roche_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('co2_saved', models.FloatField(default=0.0)),
                ('challenges_completed', models.IntegerField(default=0)),
                ('challenges_created', models.IntegerField(default=0)),
                ('challenges_joined', models.IntegerField(default=0)),
                ('wallet_points', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='challenge',
            name='impact',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='challenge_id',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='participants',
        ),
        migrations.AlterField(
            model_name='challenge',
            name='reward',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='tracking_method',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='why',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='challenge',
            name='participants',
            field=models.ManyToManyField(related_name='challenges', to=settings.AUTH_USER_MODEL),
        ),
    ]

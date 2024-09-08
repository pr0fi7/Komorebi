# Generated by Django 5.1.1 on 2024-09-07 17:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roche_app', '0006_rename_ideas_created_userprofile_idea_created_idea'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='challenge_id',
        ),
        migrations.AlterField(
            model_name='challenge',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]

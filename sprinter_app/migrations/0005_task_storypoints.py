# Generated by Django 3.2 on 2025-02-23 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sprinter_app', '0004_sprint_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='storyPoints',
            field=models.IntegerField(default=1),
        ),
    ]

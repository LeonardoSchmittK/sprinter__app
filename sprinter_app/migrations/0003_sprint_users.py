# Generated by Django 3.2 on 2025-02-22 03:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sprinter_app', '0002_alter_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprint',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='participating_sprints', to=settings.AUTH_USER_MODEL),
        ),
    ]

# Generated by Django 3.2 on 2025-02-17 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sprinter_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('todo', 'TODO'), ('in_progress', 'In Progress'), ('done', 'Done')], default='TODO', max_length=20),
        ),
    ]

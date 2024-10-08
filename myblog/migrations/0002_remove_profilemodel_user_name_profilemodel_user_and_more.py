# Generated by Django 5.0.7 on 2024-07-17 20:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myblog', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilemodel',
            name='user_name',
        ),
        migrations.AddField(
            model_name='profilemodel',
            name='user',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profilemodel',
            name='bio',
            field=models.TextField(),
        ),
    ]

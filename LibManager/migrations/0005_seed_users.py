# Migration to seed initial users

import os
from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_users(apps, schema_editor):
    """Create initial user with ID 3151415"""
    User = apps.get_model('LibManager', 'User')
    
    # Optionally create default user when explicitly enabled via env var.
    # To avoid committing real credentials, seeding is disabled by default.
    seed_flag = os.environ.get('SEED_DEFAULT_USER', 'false').lower() == 'true'
    default_password = os.environ.get('DEFAULT_USER_PASSWORD', '')
    if seed_flag and default_password:
        if not User.objects.filter(user_id='3151415').exists():
            User.objects.create(
                user_id='3151415',
                password_hash=make_password(default_password),
                name='Default User'
            )


def reverse_users(apps, schema_editor):
    """Remove created users"""
    User = apps.get_model('LibManager', 'User')
    User.objects.filter(user_id='3151415').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('LibManager', '0004_user'),
    ]

    operations = [
        migrations.RunPython(create_users, reverse_users),
    ]

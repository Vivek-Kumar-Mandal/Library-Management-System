# Generated migration for User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LibManager', '0003_seed_books'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True)),
                ('password_hash', models.CharField(max_length=255)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

# Generated by Django 4.1.7 on 2023-03-10 22:36

import app.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SallaUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('salla_id', models.CharField(db_index=True, max_length=64, unique=True)),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
                ('email', models.EmailField(blank=True, max_length=256, null=True)),
                ('mobile', models.CharField(blank=True, max_length=32, null=True)),
                ('role', models.CharField(default='user', max_length=16)),
                ('is_active', models.BooleanField(default=True)),
                ('is_merchant', models.BooleanField(default=False)),
                ('merchant', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_token', models.CharField(db_index=True, default=app.utils.generate_token, editable=False, max_length=256, unique=True)),
                ('access_token', models.CharField(max_length=256)),
                ('refresh_token', models.CharField(max_length=256)),
                ('expires_in', models.PositiveSmallIntegerField(default=app.utils.next_two_weeks)),
                ('scope', models.CharField(max_length=1024)),
                ('token_type', models.CharField(max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='token', to='app.sallauser')),
            ],
        ),
    ]

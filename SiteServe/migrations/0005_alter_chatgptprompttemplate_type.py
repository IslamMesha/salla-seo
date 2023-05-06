# Generated by Django 4.1.7 on 2023-05-05 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SiteServe', '0004_alter_chatgptprompttemplate_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgptprompttemplate',
            name='type',
            field=models.CharField(choices=[('title', 'title'), ('description', 'description'), ('seo_title', 'seo_title'), ('seo_description', 'seo_description')], max_length=32),
        ),
    ]

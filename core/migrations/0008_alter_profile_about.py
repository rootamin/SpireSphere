# Generated by Django 4.2.2 on 2023-07-06 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_profile_about'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='about',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]

# Generated by Django 4.2.2 on 2023-07-06 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_room_host_profilepic_profile_about'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='about',
            field=models.TextField(blank=True, default=''),
        ),
    ]

# Generated by Django 5.1.2 on 2024-10-22 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_alter_event_capacity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='capacity',
            field=models.IntegerField(null=True),
        ),
    ]

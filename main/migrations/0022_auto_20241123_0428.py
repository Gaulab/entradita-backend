# Generated by Django 3.2 on 2024-11-23 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20241122_1910'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickettag',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tickettag',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]

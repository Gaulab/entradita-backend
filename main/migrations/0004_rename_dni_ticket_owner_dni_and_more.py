# Generated by Django 5.1.2 on 2024-10-18 04:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_event_capacity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='dni',
            new_name='owner_dni',
        ),
        migrations.RenameField(
            model_name='ticket',
            old_name='name',
            new_name='owner_lastname',
        ),
        migrations.RenameField(
            model_name='ticket',
            old_name='seller',
            new_name='owner_name',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='surname',
        ),
        migrations.AddField(
            model_name='ticket',
            name='seller_id',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_seller', models.BooleanField()),
                ('uuid', models.CharField(max_length=36, unique=True)),
                ('assigned_name', models.CharField(max_length=100)),
                ('status', models.BooleanField(default=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.event')),
            ],
        ),
        migrations.DeleteModel(
            name='UrlAccess',
        ),
    ]

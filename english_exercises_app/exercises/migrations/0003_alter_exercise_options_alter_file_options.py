# Generated by Django 4.2 on 2023-06-22 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0002_exercise'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exercise',
            options={'verbose_name': 'Exercise', 'verbose_name_plural': 'Exercises'},
        ),
        migrations.AlterModelOptions(
            name='file',
            options={'verbose_name': 'File', 'verbose_name_plural': 'Files'},
        ),
    ]

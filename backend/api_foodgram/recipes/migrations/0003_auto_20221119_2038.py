# Generated by Django 3.2.16 on 2022-11-19 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredients',
            name='unique_name',
        ),
        migrations.AddConstraint(
            model_name='ingredients',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_name'),
        ),
    ]
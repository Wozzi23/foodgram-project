# Generated by Django 3.2.16 on 2022-11-02 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes',
            name='tags',
            field=models.ManyToManyField(to='recipes.Tags', verbose_name='Тег'),
        ),
    ]

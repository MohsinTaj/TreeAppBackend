# Generated by Django 5.1.1 on 2024-09-05 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_community_trees_community'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]

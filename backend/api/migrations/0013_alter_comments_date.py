# Generated by Django 5.1 on 2024-09-29 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_merge_20240920_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]

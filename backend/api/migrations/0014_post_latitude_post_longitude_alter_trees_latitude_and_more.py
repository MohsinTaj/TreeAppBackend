# Generated by Django 5.1.1 on 2025-07-09 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_comments_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trees',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trees',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

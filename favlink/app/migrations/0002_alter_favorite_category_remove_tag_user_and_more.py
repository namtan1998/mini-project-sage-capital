# Generated by Django 5.0.7 on 2024-07-12 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='category',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.RemoveField(
            model_name='tag',
            name='user',
        ),
        migrations.RemoveField(
            model_name='favorite',
            name='tags',
        ),
        migrations.AddField(
            model_name='favorite',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='url',
            field=models.URLField(max_length=255),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
        migrations.AddField(
            model_name='favorite',
            name='tags',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

# Generated by Django 2.0 on 2019-01-13 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infilect_app', '0004_auto_20190113_0803'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='location',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='mime_type',
        ),
        migrations.AddField(
            model_name='photo',
            name='height_field',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='photo',
            name='image',
            field=models.ImageField(blank=True, height_field='height_field', null=True, upload_to='', width_field='width_field'),
        ),
        migrations.AddField(
            model_name='photo',
            name='width_field',
            field=models.IntegerField(default=0),
        ),
    ]
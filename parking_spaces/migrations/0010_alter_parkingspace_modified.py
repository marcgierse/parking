# Generated by Django 3.2.9 on 2021-12-11 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking_spaces', '0009_auto_20211210_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingspace',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

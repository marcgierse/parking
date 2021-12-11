# Generated by Django 3.2.9 on 2021-12-10 17:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('parking_spaces', '0008_auto_20211113_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingspace',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='parkingspace',
            name='name',
            field=models.CharField(max_length=40, verbose_name='Parkplatzname'),
        ),
        migrations.AlterField(
            model_name='parkingspace',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Besitzer'),
        ),
        migrations.AlterField(
            model_name='parkingspace',
            name='valid_from',
            field=models.DateField(help_text='Ab wann steht der Mietvertrag grundsätzlich zur Verfügung? (TT.MM.JJJJ)', verbose_name='Start Mietvertrag'),
        ),
        migrations.AlterField(
            model_name='parkingspace',
            name='valid_to',
            field=models.DateField(help_text='Bis wann steht der Parkplatz grundsätzlich zur Verfügung? (TT.MM.JJJJ)', verbose_name='Ende Mietvertrag'),
        ),
        migrations.AlterField(
            model_name='parkingspaceevent',
            name='status',
            field=models.CharField(choices=[('USED_OWNER', 'USED_BY_OWNER'), ('FREE', 'FREE'), ('USED_USER', 'BOOKED_BY_USER')], max_length=10),
        ),
        migrations.AlterField(
            model_name='parkingspaceevent',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

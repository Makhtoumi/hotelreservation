# Generated by Django 4.2.4 on 2023-08-16 20:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Menugenerale', '0008_rename_name_pax_roomavailability_name_assi'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('occupants', models.CharField(max_length=200)),
                ('date_arriv', models.DateField()),
                ('date_sortie', models.DateField()),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Menugenerale.chambre')),
            ],
        ),
    ]

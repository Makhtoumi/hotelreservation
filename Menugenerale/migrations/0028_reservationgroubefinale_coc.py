# Generated by Django 4.2.4 on 2024-01-11 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Menugenerale", "0027_pax_nationalite_pax_num_telephone_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservationgroubefinale",
            name="coc",
            field=models.CharField(default="", max_length=30),
        ),
    ]

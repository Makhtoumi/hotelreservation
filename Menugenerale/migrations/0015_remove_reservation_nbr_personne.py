# Generated by Django 4.2.4 on 2023-08-17 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Menugenerale', '0014_remove_reservation_codeagence'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='nbr_personne',
        ),
    ]
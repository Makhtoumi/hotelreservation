# Generated by Django 4.2.4 on 2023-08-16 20:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Menugenerale', '0007_roomavailability_name_pax_alter_client_typeclient'),
    ]

    operations = [
        migrations.RenameField(
            model_name='roomavailability',
            old_name='name_pax',
            new_name='name_assi',
        ),
    ]

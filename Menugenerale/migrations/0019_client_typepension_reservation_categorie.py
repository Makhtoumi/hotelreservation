# Generated by Django 4.2.4 on 2023-08-17 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Menugenerale', '0018_reservation_nbr_personne'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='typepension',
            field=models.CharField(choices=[('pension complte', 'pension complte'), ('demi pension', 'demi pension'), ('LOG', 'log'), ('LPD', 'LPD')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='categorie',
            field=models.CharField(choices=[('indiv', 'indiv'), ('double', 'double'), ('triple', 'triple')], max_length=30, null=True),
        ),
    ]

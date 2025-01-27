# Generated by Django 4.2.4 on 2023-08-20 14:09

from django.db import migrations, models
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ("Menugenerale", "0020_remove_facture_chambre_vue_facture_paxes_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="association",
            name="adress",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Adress"
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="code",
            field=models.CharField(
                max_length=30, primary_key=True, serialize=False, verbose_name="Code"
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="nom",
            field=models.CharField(max_length=100, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="association",
            name="type",
            field=models.CharField(
                choices=[
                    ("agence de voyage", "Agence de voyage"),
                    ("association", "Association"),
                    ("e/se privee", "E/se privee"),
                ],
                max_length=20,
                verbose_name="Type",
            ),
        ),
        migrations.AlterField(
            model_name="associationcriteria",
            name="debut_contart",
            field=models.DateField(verbose_name="Début de contrat"),
        ),
        migrations.AlterField(
            model_name="associationcriteria",
            name="fin_contrat",
            field=models.DateField(verbose_name="Fin de contrat"),
        ),
        migrations.AlterField(
            model_name="associationcriteria",
            name="monnaie",
            field=models.CharField(
                choices=[
                    ("TND", "Dinar Tunisien"),
                    ("USD", "US Dollar"),
                    ("EUR", "Euro"),
                ],
                default="",
                max_length=100,
                verbose_name="Monnaie",
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="codeclient",
            field=models.CharField(
                max_length=30, primary_key=True, serialize=False, verbose_name="Code"
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="nomclient",
            field=models.CharField(max_length=30, null=True, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="client",
            name="typepension",
            field=models.CharField(
                choices=[
                    ("pension complte", "pension complte"),
                    ("demi pension", "demi pension"),
                    ("LOG", "log"),
                    ("LPD", "LPD"),
                ],
                max_length=20,
                null=True,
                verbose_name="Pension",
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="vchambre_vue",
            field=models.CharField(
                choices=[("Vue picine", "Vue picine"), ("normal", "nomal")],
                max_length=30,
                null=True,
                verbose_name="Vue",
            ),
        ),
        migrations.AlterField(
            model_name="occupant",
            name="age",
            field=models.IntegerField(blank=True, null=True, verbose_name="Age"),
        ),
        migrations.AlterField(
            model_name="occupant",
            name="nationalite",
            field=django_countries.fields.CountryField(
                blank=True, max_length=2, null=True, verbose_name="Nationalité"
            ),
        ),
        migrations.AlterField(
            model_name="occupant",
            name="nom",
            field=models.CharField(max_length=100, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="occupant",
            name="num_telephone",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="Numéro de téléphone"
            ),
        ),
        migrations.AlterField(
            model_name="occupant",
            name="prenom",
            field=models.CharField(max_length=100, verbose_name="Prénom"),
        ),
        migrations.AlterField(
            model_name="pax",
            name="age",
            field=models.IntegerField(verbose_name="Age"),
        ),
        migrations.AlterField(
            model_name="pax",
            name="first_name",
            field=models.CharField(max_length=50, verbose_name="Prénom"),
        ),
        migrations.AlterField(
            model_name="pax",
            name="last_name",
            field=models.CharField(max_length=50, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="reservation",
            name="date_arriv",
            field=models.DateField(blank=True, verbose_name="Date d'Arrivée"),
        ),
        migrations.AlterField(
            model_name="reservation",
            name="date_sortie",
            field=models.DateField(blank=True, verbose_name="Date de Départ"),
        ),
        migrations.AlterField(
            model_name="reservationgroube",
            name="categorie",
            field=models.CharField(
                choices=[
                    ("indiv", "Single"),
                    ("double", "Double"),
                    ("triple", "Triple"),
                ],
                max_length=30,
                null=True,
                verbose_name="Catégorie",
            ),
        ),
        migrations.AlterField(
            model_name="reservationgroube",
            name="date_arrivee",
            field=models.DateField(verbose_name="Date d'Arrivée"),
        ),
        migrations.AlterField(
            model_name="reservationgroube",
            name="date_depart",
            field=models.DateField(verbose_name="Date de Départ"),
        ),
        migrations.AlterField(
            model_name="reservationgroube",
            name="date_reservation",
            field=models.DateField(
                default=django.utils.timezone.now, verbose_name="Date de reservation"
            ),
        ),
        migrations.AlterField(
            model_name="reservationgroube",
            name="pension",
            field=models.CharField(
                choices=[
                    ("pension complte", "pension complte"),
                    ("demi pension", "demi pension"),
                    ("LOG", "log"),
                    ("LPD", "LPD"),
                ],
                max_length=20,
                null=True,
                verbose_name="Pension",
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="duration_discount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="Duration Réduction",
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="duration_threshold",
            field=models.PositiveIntegerField(default=0, verbose_name="Si nbr days >"),
        ),
        migrations.AlterField(
            model_name="season",
            name="earlybooking_discount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="Early booking Réduction",
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="earlybooking_threshold",
            field=models.PositiveIntegerField(default=0, verbose_name="Si"),
        ),
        migrations.AlterField(
            model_name="season",
            name="end_date",
            field=models.DateField(verbose_name="Date de début"),
        ),
        migrations.AlterField(
            model_name="season",
            name="mineur2_discount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="Réduction mineur",
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="mineur2_threshold",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Mineur Si age < "
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="mineur_discount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="Réduction mineur",
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="mineur_threshold",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Mineur Si age < "
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="name_season",
            field=models.CharField(max_length=100, verbose_name="Nom de la Saison"),
        ),
        migrations.AlterField(
            model_name="season",
            name="paxnum3_discount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="Réduction pour 3 personnes",
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="paxnum3_threshold",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Seuil pour 3 personnes"
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="start_date",
            field=models.DateField(verbose_name="Date de début"),
        ),
        migrations.AlterField(
            model_name="seasoncategorie",
            name="cat",
            field=models.CharField(
                choices=[
                    ("indiv", "indiv"),
                    ("double", "double"),
                    ("triple", "triple"),
                    ("quaderiple", "quaderiple"),
                ],
                max_length=20,
                null=True,
                verbose_name="Catégorie",
            ),
        ),
        migrations.AlterField(
            model_name="seasoncategorie",
            name="demipension_price",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="Prix DemiPension",
            ),
        ),
        migrations.AlterField(
            model_name="seasoncategorie",
            name="pensioncomplte_price",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                verbose_name="Prix PensionComplet",
            ),
        ),
    ]

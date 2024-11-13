# Generated by Django 4.2.4 on 2023-08-24 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Menugenerale", "0023_alter_season_duration_discount_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="InforamtionHotel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "FIX",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="Numéro de Fix",
                    ),
                ),
                (
                    "FAX",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="Numéro de Fax",
                    ),
                ),
                (
                    "email",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="Email"
                    ),
                ),
                (
                    "Nom",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="Nom"
                    ),
                ),
                (
                    "Adress",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="Adress"
                    ),
                ),
                (
                    "codeTva",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="code tva"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Taxes",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "FDCST",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=5,
                        verbose_name="FDCST %",
                    ),
                ),
                (
                    "TVA",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=5, verbose_name="TVA %"
                    ),
                ),
                (
                    "taxe_sejour",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                (
                    "frais_de_timbre",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RenameField(
            model_name="facture",
            old_name="date_arriv",
            new_name="date_arrivee",
        ),
        migrations.RenameField(
            model_name="facture",
            old_name="date_sortie",
            new_name="date_depart",
        ),
        migrations.RemoveField(
            model_name="facture",
            name="chambre_id",
        ),
        migrations.RemoveField(
            model_name="facture",
            name="chambre_type",
        ),
        migrations.RemoveField(
            model_name="facture",
            name="codeclient",
        ),
        migrations.RemoveField(
            model_name="facture",
            name="nomclient",
        ),
        migrations.RemoveField(
            model_name="facture",
            name="paxes",
        ),
        migrations.RemoveField(
            model_name="facture",
            name="price",
        ),
        migrations.RemoveField(
            model_name="facture",
            name="reservation",
        ),
        migrations.AddField(
            model_name="facture",
            name="categorie",
            field=models.CharField(default="", max_length=30),
        ),
        migrations.AddField(
            model_name="facture",
            name="code_assi",
            field=models.CharField(default="", max_length=30),
        ),
        migrations.AddField(
            model_name="facture",
            name="date_reservation",
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name="facture",
            name="discountfard",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facture",
            name="discounts",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facture",
            name="discounts_detail",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facture",
            name="final_price_with_discount",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facture",
            name="nbr_personne",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facture",
            name="nom_assi",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facture",
            name="pension",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="facture",
            name="price_without_discount",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facture",
            name="reservation_code",
            field=models.CharField(default="", max_length=30),
        ),
        migrations.AddField(
            model_name="facture",
            name="tarif",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facturefinale",
            name="discountfard",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="facturefinale",
            name="reservation_code",
            field=models.CharField(default="", max_length=30),
        ),
        migrations.AddField(
            model_name="facturefinale",
            name="tarif",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="reservationgroubefinale",
            name="occupnumb3",
            field=models.ManyToManyField(
                blank=True,
                related_name="reservations_with_occupnumb3",
                to="Menugenerale.occupant",
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="vchambre_type",
            field=models.CharField(
                choices=[
                    ("indiv", "single"),
                    ("double", "double"),
                    ("triple", "triple"),
                ],
                max_length=30,
                null=True,
                verbose_name="Categorie",
            ),
        ),
        migrations.AlterField(
            model_name="facturefinale",
            name="date_reservation",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="reservation",
            name="categorie",
            field=models.CharField(
                choices=[
                    ("indiv", "single"),
                    ("double", "double"),
                    ("triple", "triple"),
                ],
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="season",
            name="earlybooking_threshold",
            field=models.DateField(blank=True, null=True, verbose_name="Si"),
        ),
        migrations.AlterField(
            model_name="season",
            name="end_date",
            field=models.DateField(verbose_name="Date de fin"),
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
            model_name="seasoncategorie",
            name="cat",
            field=models.CharField(
                choices=[
                    ("indiv", "single"),
                    ("double", "double"),
                    ("triple", "triple"),
                    ("quaderiple", "quaderiple"),
                ],
                max_length=20,
                null=True,
                verbose_name="Catégorie",
            ),
        ),
    ]
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
import random





class Client(models.Model):
    x = [
        ('indiv', 'indiv'),
        ('privé', 'privé'),
        ('groupe','groupe'),
    ]
    y = [ ('indiv','single'),
          ('double','double'),
          ('triple','triple')]
    z = [ ('Vue picine','Vue picine'),
          ('normal','nomal')]
    j = [
        ('pension complte', 'pension complte'),
        ('demi pension', 'demi pension'),
        ('LOG', 'log'),
        ('LPD', 'LPD'),
    ]
    codeclient = models.CharField(verbose_name="Code" ,primary_key=True, max_length=30, null=False, blank=False)
    nomclient = models.CharField(verbose_name="Nom" ,max_length=30, null=True, blank=False)
    typeclient = models.CharField(max_length=20, choices=x, null=True, blank=False)
    vchambre_type = models.CharField(verbose_name="Categorie" ,max_length=30,choices=y, null=True, blank=False)
    typepension = models.CharField(verbose_name="Pension",max_length=20, choices=j, null=True, blank=False)
    vchambre_vue = models.CharField(verbose_name="Vue" ,max_length=30,choices=z, null=False, blank=False, default='')
    def __str__(self):
        return self.nomclient

class Chambre(models.Model):
    x = [ ('indiv','indiv'),
          ('double','double'),
          ('triple','triple'),
          ('quadruple','quadruple')]
    y = [ ('Vue picine','Vue picine'),
          ('normal','nomal'),
          ('Vue sur mer','Vue sur mer')]
    chambre_id = models.CharField(primary_key=True, max_length=30, blank=False)
    chambre_type = models.CharField(max_length=30,choices=x, null=True, blank=False)
    chambre_Vue = models.CharField(max_length=30,choices=y, null=True, blank=False)
    capacity = models.IntegerField(default=1)


    def __str__(self):
        return self.chambre_id
    def save(self, *args, **kwargs):
        if self.chambre_type == 'indiv':
            self.capacity = 1
        elif self.chambre_type == 'double':
            self.capacity = 2
        elif self.chambre_type == 'triple':
            self.capacity = 3
        elif self.chambre_type == 'quadruple':
            self.capacity = 4

        super(Chambre, self).save(*args, **kwargs)


class Pax(models.Model):

    first_name = models.CharField(verbose_name="Prénom" ,max_length=50)
    last_name = models.CharField(verbose_name="Nom" ,max_length=50)
    age = models.IntegerField(verbose_name="Age" )
    nationalite = CountryField(verbose_name="Nationalité" ,null=True, blank=True)
    num_telephone = models.CharField(verbose_name="Numéro de téléphone" ,max_length=20, null=True, blank=True)



    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Reservation(models.Model):
    y = [
        ('pension complte', 'pension complte'),
        ('demi pension', 'demi pension'),
        ('LOG', 'logement'),
        ('LPD', 'logement et petit dejeuner'),
    ]
    x = [
        ('indiv', 'indiv'),
        ('agence de voyage', 'agence de voyage'),
        ('privé', 'privé')
    ]
    j = [ ('indiv','single'),
          ('double','double'),
          ('triple','triple')]
    nbr_personne = models.IntegerField(verbose_name="Number of People", default=0)  # Add this field
    clients = models.ForeignKey(Client, to_field='codeclient', on_delete=models.CASCADE, related_name='reservations')
    typeclient = models.CharField(max_length=20, choices=x, null=True, blank=True)
    date_arriv = models.DateField(verbose_name="Date d'Arrivée",blank=True)
    date_sortie = models.DateField(verbose_name="Date de Départ",blank=True)
    chambre = models.ManyToManyField(Chambre, blank=True)
    categorie  = models.CharField(max_length=30,choices=j,null=True,blank=False)
    type_pension = models.CharField(max_length=20, choices=y, null=True, blank=False)
    paxes = models.ManyToManyField(Pax,blank=True)
    prix_force = models.DecimalField(max_digits=5, decimal_places=2, default=0,verbose_name='Prix Forcer')



    def save(self, *args, **kwargs):
        created = not self.pk

        # If the clients field is provided and not already saved, populate date_arriv and date_sortie
        if self.clients and created:
            client = self.clients
            self.typeclient = client.typeclient
        if not self.id:
            # Calculate a unique ID based on date_arriv
            year_last_two_digits = str(self.date_arriv.year)[-1:]
            base_id = self.date_arriv.strftime('%m%d')
            while True:
                # Generate a random 4-digit number
                random_suffix = random.randint(1000, 9999)

                # Construct the new ID
                new_id = f"{base_id}{random_suffix}{year_last_two_digits}"

                # Check if the ID already exists
                if not Reservation.objects.filter(id=new_id).exists():
                    self.id = new_id
                    break


        super(Reservation, self).save(*args, **kwargs)







class Facture(models.Model):
    reservation_code = models.CharField(max_length=30, null=False, blank=False , default='')
    code_assi = models.CharField(max_length=30, null=False, blank=False ,default='')
    nom_assi = models.CharField(max_length=100, null=False, blank=False ,default='')
    date_reservation = models.DateField(null=True, blank=False)
    date_arrivee = models.DateField()
    date_depart = models.DateField()
    pension = models.CharField(max_length=20 ,default='')
    categorie = models.CharField(max_length=30 ,default='')
    nbr_personne = models.CharField(max_length=100, null=False, blank=False ,default='')
    discounts = models.CharField(max_length=100, null=False, blank=False, default='')
    discounts_detail = models.CharField(max_length=100, null=False, blank=False,default='')
    discountfard = models.CharField(max_length=100, null=False, blank=False,default='')
    tarif = models.CharField(max_length=100, null=False, blank=False,default='')
    price_without_discount = models.CharField(max_length=100, null=False, blank=False,default='' )
    final_price_with_discount = models.CharField(max_length=100, null=False, blank=False ,default='')


class AssociationType(models.Model):
    assoctiontype = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.assoctiontype}"

class Association(models.Model):
    AGENCE_DE_VOYAGE = 'agence de voyage'
    ASSOCIATION = 'association'
    PRIVEE = 'e/se privee'
    ASSOCIATION_TYPES = [
        (AGENCE_DE_VOYAGE, 'Agence de voyage'),
        (ASSOCIATION, 'Association'),
        (PRIVEE, 'E/se privee'),
    ]

    code = models.CharField(verbose_name="Code" ,primary_key=True, max_length=30, null=False, blank=False)
    nom = models.CharField(verbose_name="Nom" ,max_length=100, null=False, blank=False)
    type = models.ForeignKey(AssociationType, on_delete=models.CASCADE)
    adress = models.CharField(verbose_name="Adress" ,max_length=200, null=True, blank=True)
    matfacial = models.CharField(verbose_name='Matricule Fiscal',max_length=50,null=True, blank=True)


    def __str__(self):
        return f"{self.nom} ({self.type})"



class Reservationgroube(models.Model):
    PENSION_TYPES = (
        ('pension complte', 'pension complte'),
        ('demi pension', 'demi pension'),
        ('LOG', 'Logement'),
        ('LPD', 'Logement et petit dejeuner'),
    )
    y = (('indiv','Single'),
         ('double','Double'),
         ('triple','Triple'),)
    date_reservation = models.DateField(verbose_name="Date de reservation" ,default=timezone.now)
    date_arrivee = models.DateField(verbose_name="Date d'Arrivée")
    date_depart = models.DateField(verbose_name="Date de Départ")
    pension = models.CharField(verbose_name="Pension" ,max_length=20, choices=PENSION_TYPES, null=True, blank=False)
    categorie = models.CharField(verbose_name="Catégorie" ,max_length=30,choices=y ,null=True, blank=False)

    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='reservations')

    def __str__(self):
        return f"Reservation for {self.association.nom} ({self.association.type})"


class ReservationOccupant(models.Model):
    reservation = models.ForeignKey(Reservationgroube, on_delete=models.CASCADE)
    occupant = models.ForeignKey('Occupant', on_delete=models.CASCADE)
    chambre = models.ForeignKey('Chambre', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.occupant.nom} {self.occupant.prenom} - Reservation: {self.reservation.date_reservation}"


class Occupant(models.Model):
    reservation = models.ForeignKey(Reservationgroube, on_delete=models.CASCADE, related_name='occupants')
    nom = models.CharField(verbose_name="Nom" ,max_length=100, null=False, blank=False)
    prenom = models.CharField(verbose_name="Prénom" ,max_length=100, null=False, blank=False)
    num_telephone = models.CharField(verbose_name="Numéro de téléphone" ,max_length=20, null=True, blank=True)
    nationalite = CountryField(verbose_name="Nationalité" ,null=True, blank=True)
    age = models.IntegerField(verbose_name="Age" ,null=True, blank=True)
    chambre = models.ForeignKey(Chambre, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"



class AssociationCriteria(models.Model):
    CURRENCY_CHOICES = [
        ('TND', 'Dinar Tunisien'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        # Add more currency choices as needed
    ]
    association = models.OneToOneField(Association, on_delete=models.CASCADE)
    debut_contart = models.DateField(verbose_name="Début de contrat" )
    fin_contrat = models.DateField(verbose_name="Fin de contrat" )
    monnaie = models.CharField(verbose_name="Monnaie" ,max_length=100, choices=CURRENCY_CHOICES, null=False, blank=False, default='')
    def __str__(self):
        return f"{self.association.nom}"

class Season(models.Model):

    association_criteria = models.ForeignKey(AssociationCriteria, on_delete=models.CASCADE)
    name_season = models.CharField(max_length=100, null=False, blank=False,verbose_name="Nom de la Saison")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    duration_discount = models.DecimalField(max_digits=8, decimal_places=2,default=0,verbose_name='Long Stay Réduction')  # Discount based on the number of days
    duration_threshold = models.PositiveIntegerField(default=0,verbose_name='Sejour >')  # Number of days to reach the discount threshold
    earlybooking_discount = models.DecimalField(max_digits=8, decimal_places=2,default=0,verbose_name="Early booking Réduction")
    earlybooking_threshold = models.DateField(verbose_name="Si", blank=True, null=True)
    mineur_discount = models.DecimalField(max_digits=8, decimal_places=2,default=0,verbose_name="Réduction mineur")
    mineur_threshold = models.PositiveIntegerField(default=0,verbose_name="Mineur Si age < ")
    mineur2_discount = models.DecimalField(max_digits=8, decimal_places=2,default=0,verbose_name="Réduction mineur")
    mineur2_threshold = models.PositiveIntegerField(default=0,verbose_name="Mineur Si age < ")
    paxnum3_discount = models.DecimalField(max_digits=8, decimal_places=2,default=0 ,verbose_name="Réduction pour 3 personnes")
    paxnum3_threshold = models.PositiveIntegerField(default=0,verbose_name="Seuil pour 3 personnes")


class SeasonCategorie(models.Model):
    PENSION_TYPES = (
        ('indiv', 'single'),
        ('double', 'double'),
        ('triple', 'triple'),
        ('quaderiple', 'quaderiple'),
    )
    season = models.ForeignKey(Season, on_delete=models.CASCADE,related_name='categories')
    cat = models.CharField(max_length=20, choices=PENSION_TYPES, null=True, blank=False,verbose_name='Catégorie')
    demipension_price = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='Prix DemiPension')
    pensioncomplte_price = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='Prix PensionComplet')
    log_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    lpd_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

class ReservationGroubeFinale(models.Model):
    code_assi = models.CharField(max_length=30, null=False, blank=False)
    nom_assi = models.CharField(max_length=100, null=False, blank=False)
    date_reservation = models.DateField()
    date_arrivee = models.DateField()
    date_depart = models.DateField()
    pension = models.CharField(max_length=20, choices=Reservationgroube.PENSION_TYPES, null=True, blank=False)
    categorie = models.CharField(max_length=30, choices=Reservationgroube.y, null=True, blank=False)
    nbr_personne = models.IntegerField(default=0)
    occupantslist = models.TextField(null=True, blank=True)
    occupant = models.ManyToManyField(Occupant,blank=True)
    chambre_taked = models.TextField(null=True, blank=True)
    chambre = models.ManyToManyField(Chambre, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    occupnumb3 = models.ManyToManyField(Occupant, related_name='reservations_with_occupnumb3', blank=True)
    coc = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return f"{self.code_assi} - {self.nom_assi} - Price: {self.price}"

    def save(self, *args, **kwargs):
        if not self.id:
            # Extract the last two digits of the year from date_arriv
            year_last_two_digits = str(self.date_reservation.year)[-1:]

            # Calculate a unique ID based on date_arriv
            base_id = f"{self.date_reservation.strftime('%m%d')}"

            while True:
                # Generate a random 4-digit number
                random_suffix = random.randint(1000, 9999)

                # Construct the new ID
                new_id = f"{base_id}{random_suffix}{year_last_two_digits}"

                # Check if the ID already exists
                if not ReservationGroubeFinale.objects.filter(id=new_id).exists():
                    self.id = new_id
                    break

        super(ReservationGroubeFinale, self).save(*args, **kwargs)





class RoomAvailability(models.Model):
    chambre = models.ForeignKey(Chambre, to_field='chambre_id', on_delete=models.CASCADE)
    reservation = models.CharField(max_length=200,default='')
    name_assi =  models.CharField(max_length=30,null=True, blank=False,default='')
    champre_type = models.CharField(max_length=30, choices=Chambre.x, null=True, blank=False)
    champre_Vue = models.CharField(max_length=30, choices=Chambre.y, null=True, blank=False)
    date_arriv = models.DateField()
    date_sortie = models.DateField()
    dispo = models.BooleanField(default=False)

    class Meta:
        unique_together = ('chambre', 'date_arriv', 'date_sortie')

    def __str__(self):
        return f"Room {self.chambre.chambre_id}: {self.champre_type}, {self.champre_Vue}"

    def save(self, *args, **kwargs):
        # Delete existing objects with the same reservation ID
        RoomAvailability.objects.filter(reservation=self.reservation).delete()
        super(RoomAvailability, self).save(*args, **kwargs)
    @classmethod
    def get_available_rooms(cls, date_arriv, date_sortie):
        available_rooms = cls.objects.filter(
            date_arriv__gte=date_arriv,
            date_sortie__lte=date_sortie,
        )
        return available_rooms


class OccupantRoom(models.Model):
    occupant = models.ForeignKey(Occupant, on_delete=models.CASCADE)
    room = models.ForeignKey(Chambre, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.occupant} - Room {self.room.chambre.chambre_id}"


class FactureFinale(models.Model):
    reservation_code = models.CharField(max_length=30, null=False, blank=False , default='')
    code_assi = models.CharField(max_length=30, null=False, blank=False)
    nom_assi = models.CharField(max_length=100, null=False, blank=False)
    date_reservation = models.DateField(null=True, blank=False)
    date_arrivee = models.DateField()
    date_depart = models.DateField()
    pension = models.CharField(max_length=20)
    categorie = models.CharField(max_length=30)
    nbr_personne = models.CharField(max_length=100, null=False, blank=False)
    discounts = models.CharField(max_length=100, null=False, blank=False)
    discounts_detail = models.CharField(max_length=100, null=False, blank=False,default='')
    discountfard = models.CharField(max_length=100, null=False, blank=False,default='')
    tarif = models.CharField(max_length=100, null=False, blank=False,default='')
    price_without_discount = models.CharField(max_length=100, null=False, blank=False)
    final_price_with_discount = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return f"Facture for {self.reservation_code}"



class RoomAssignment(models.Model):
    room = models.ForeignKey(Chambre, on_delete=models.CASCADE)
    occupants = models.CharField(max_length=200)  # Store occupants' names
    reservation = models.CharField(max_length=200,default='')
    date_arriv = models.DateField()
    date_sortie = models.DateField()
    code_assi =  models.CharField(max_length=30, null=False, blank=False,default='')
    nom_assi  =  models.CharField(max_length=30, null=False, blank=False,default='')

    def __str__(self):
        return f"Room {self.room.chambre_id} - {self.occupants}"
    def save(self, *args, **kwargs):
        # Delete existing objects with the same reservation ID
        RoomAssignment.objects.filter(reservation=self.reservation).delete()
        super(RoomAssignment, self).save(*args, **kwargs)



class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class Taxes(SingletonModel):
    FDCST = models.DecimalField(max_digits=5, decimal_places=2, default=0,verbose_name='FDCST %')
    TVA = models.DecimalField(max_digits=5, decimal_places=2, default=0,verbose_name='TVA %')
    taxe_sejour = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    frais_de_timbre = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return "Taxes Instance"

class InforamtionHotel(SingletonModel):
    Nom = models.CharField(verbose_name="Nom" ,max_length=50, null=True, blank=True)
    marticule = models.CharField(verbose_name="Matricule Fiscial",max_length=50,null=True, blank=True)
    FIX = models.CharField(verbose_name="Numéro de Fix" ,max_length=50, null=True, blank=True)
    FAX = models.CharField(verbose_name="Numéro de Fax" ,max_length=50, null=True, blank=True)
    email = models.CharField(verbose_name="Email" ,max_length=50, null=True, blank=True)
    Adress = models.CharField(verbose_name="Adress" ,max_length=50, null=True, blank=True)
    codeTva = models.CharField(verbose_name="code tva" ,max_length=50, null=True, blank=True)
    def __str__(self):
        return "Taxes Instance"


class CombinedReservation(models.Model):
    reservation = models.ManyToManyField(Reservation, blank=True)
    reservation_group = models.ManyToManyField(ReservationGroubeFinale, blank=True)
    chosen_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return f'{self.chosen_date}'




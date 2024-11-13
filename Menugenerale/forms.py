from django import forms
from .models import *
from django_select2.forms import Select2Widget
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField


class CreateUserForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'groups']

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        exclude = ('clients','chambre','paxes','nbr_personne','typeclient')
        widgets = {
            'date_arriv': forms.DateInput(attrs={'type': 'date'}),
            'date_sortie': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        date_arrivee = cleaned_data.get('date_arriv')
        date_depart = cleaned_data.get('date_sortie')

        if date_arrivee and date_depart and date_depart < date_arrivee:
            raise ValidationError("Oups ! La date de fin ne peut précéder le début de la Reservation. Veuillez vérifier vos dates")

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('vchambre_vue',)

def validate_no_special_characters_2(value):
    prohibited_characters = ['-', '@', '#', '$', '%' ,'1' ,'2' ,'3' , '4' , '5' , '6' , '8' , '9' , '0']  # Add more characters as needed
    for char in prohibited_characters:
        if char in value:
            raise ValidationError(f"'{value}' Nom et Prenom ne peut pas contenir le caractère '{char}'.")

def validator(value):
    if value > 115:
        raise ValidationError("c'est impossible de le réserver pour un humain mort")
    elif value < 0:
        raise ValidationError("l'âge ne peut pas être négatif")

def validate_not_israel(value):
    if value == "IL":
        raise ValidationError("La nationalité ne peut pas être Israélienne.")

class PaxForm(forms.ModelForm):
    first_name = forms.CharField(validators=[validate_no_special_characters_2] , label="Prénom")
    last_name = forms.CharField(validators=[validate_no_special_characters_2] , label="Nom")
    age = forms.IntegerField(validators=[validator] , label="Age")
    nationalite = CountryField(
        verbose_name="Nationalité",
        null=True,
        blank=True,
    )
    class Meta:
        model = Pax
        fields = ['first_name', 'last_name', 'age' , 'nationalite' , 'num_telephone']
        widgets = {
            'nationalite': Select2Widget,
        }
    def clean_nationalite(self):
        nationalite = self.cleaned_data.get('nationalite')
        if nationalite == 'IL':  # Replace 'IL' with the correct country code for Israel
            raise ValidationError("Tu veux dire Palestine ? ")
        return nationalite


class UpdateClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

class AssociationForm(forms.ModelForm):
    class Meta:
        model = Association
        fields = ['code', 'nom', 'type', 'adress']

class ReservationgroubeForm(forms.ModelForm):
    class Meta:
        model = Reservationgroube
        fields = ('date_reservation', 'date_arrivee', 'date_depart', 'pension', 'categorie')
        widgets = {
            'date_reservation': forms.DateInput(attrs={'type': 'date'}),
            'date_arrivee': forms.DateInput(attrs={'type': 'date'}),
            'date_depart': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        date_arrivee = cleaned_data.get('date_arrivee')
        date_depart = cleaned_data.get('date_depart')
        date_reservation = cleaned_data.get('date_reservation')
        if date_arrivee and date_depart and date_depart < date_arrivee  :
            raise ValidationError("Oups ! La date de départ ne peut précéder le arrive de la Reservation. Veuillez vérifier vos dates")

        if date_reservation > date_arrivee:
            raise ValidationError("Oups ! La date de arrivée ne peut précéder  date de la Reservation. Veuillez vérifier vos dates")

def validate_no_special_characters(value):
    prohibited_characters = ['-', '@', '#', '$', '%' ,'1' ,'2' ,'3' , '4' , '5' , '6' , '8' , '9' , '0']  # Add more characters as needed
    for char in prohibited_characters:
        if char in value:
            raise ValidationError(f" '{value}' Nom et Prenom ne peut pas contenir le caractère '{char}'.")

class OccupantForm(forms.ModelForm):
    nom = forms.CharField(validators=[validate_no_special_characters])
    prenom = forms.CharField(validators=[validate_no_special_characters])
    age = forms.IntegerField(validators=[validator] , label="Age")

    class Meta:
        model = Occupant
        fields = ['nom', 'prenom', 'num_telephone', 'nationalite', 'age']
        widgets = {
            'nationalite': Select2Widget,
        }
    def clean_nationalite(self):
        nationalite = self.cleaned_data.get('nationalite')
        if nationalite == 'IL':  # Replace 'IL' with the correct country code for Israel
            raise ValidationError("Tu veux dire Palestine ? ")
        return nationalite


class AssociationCriteriaForm(forms.ModelForm):
    class Meta:
        model = AssociationCriteria
        fields = ['debut_contart', 'fin_contrat', 'monnaie']
        widgets = {
            'debut_contart': forms.DateInput(attrs={'type': 'date'}),
            'fin_contrat': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        debut_contart = cleaned_data.get('debut_contart')
        fin_contrat = cleaned_data.get('fin_contrat')

        if debut_contart > fin_contrat:
            raise ValidationError('Oups ! La date de fin ne peut précéder le début de la contrat. Veuillez vérifier vos dates.')


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name_season', 'start_date', 'end_date', 'duration_discount', 'duration_threshold', 'earlybooking_discount', 'earlybooking_threshold' , 'mineur_discount', 'mineur_threshold','mineur2_discount','mineur2_threshold','paxnum3_discount',]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'earlybooking_threshold': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        association_criteria = cleaned_data.get('association_criteria')

        if start_date and end_date and association_criteria:
            overlapping_seasons = Season.objects.filter(
                association_criteria=association_criteria,
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exclude(id=self.instance.id)  # Exclude the current instance if updating

            if overlapping_seasons.exists():
                raise ValidationError('Oups ! Une saison avec des dates qui se chevauchent existe déjà.')
        if start_date > end_date:
            raise ValidationError('Oups ! La date de fin ne peut précéder le début de la saison. Veuillez vérifier vos dates.')

        return cleaned_data

class SeasonCategorieForm(forms.ModelForm):
    class Meta:
        model = SeasonCategorie
        fields = ['cat', 'demipension_price', 'pensioncomplte_price', 'log_price', 'lpd_price']

class ChambreForm(forms.ModelForm):
    class Meta:
        model = Chambre
        fields = ['chambre_id', 'chambre_type', 'chambre_Vue']

class ReservationUpdateForm(forms.ModelForm):
    class Meta:
        model = Reservationgroube
        fields = ['date_reservation', 'date_arrivee', 'date_depart', 'pension', 'categorie']
        widgets = {
            'date_reservation': forms.DateInput(attrs={'type': 'date'}),
            'date_arrivee': forms.DateInput(attrs={'type': 'date'}),
            'date_depart': forms.DateInput(attrs={'type': 'date'}),
        }

class TaxesForm(forms.ModelForm):
    class Meta:
        model = Taxes
        fields = '__all__'

class InforamtionHotelForm(forms.ModelForm):
    class Meta:
        model = InforamtionHotel
        fields = '__all__'

class AssociationTypeForm(forms.ModelForm):
    class Meta:
        model = AssociationType
        fields = '__all__'
    def clean_assoctiontype(self):
        assoctiontype = self.cleaned_data['assoctiontype']
        if AssociationType.objects.filter(assoctiontype=assoctiontype).exists():
            raise forms.ValidationError("This type already exists.")
        return assoctiontype
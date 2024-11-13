from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, HttpResponseRedirect
from .forms import  *
from .models import *
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph , Spacer, Image , Table , TableStyle
import io
import os
from django.conf import settings
from django.urls import reverse
from reportlab.lib import colors
from .utils import is_coo_or_developer
from decimal import Decimal
from io import BytesIO
from collections import defaultdict
from datetime import date ,timedelta , datetime
from num2words import num2words
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django_countries.data import COUNTRIES
import random


@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            groups = form.cleaned_data.get('groups')
            user.groups.set(groups)
            return redirect('dashboard')  # Redirect to the appropriate page after user creation
    else:
        form = CreateUserForm()
    return render(request, 'create_user.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def edit_taxes(request):
    taxes_instance = Taxes.load()

    if request.method == 'POST':
        form = TaxesForm(request.POST, instance=taxes_instance)
        if form.is_valid():
            form.save()
            return redirect('edit_taxes')
    else:
        form = TaxesForm(instance=taxes_instance)

    context = {'form': form}
    return render(request, 'edit_taxes.html', context)


@user_passes_test(lambda u: u.is_superuser)
def edit_info(request):
    taxes_instance = InforamtionHotel.load()

    if request.method == 'POST':
        form = InforamtionHotelForm(request.POST, instance=taxes_instance)
        if form.is_valid():
            form.save()
            return redirect('edit_info')
    else:
        form = InforamtionHotelForm(instance=taxes_instance)

    context = {'form': form}
    return render(request, 'edit_info.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def parameter(request):
    return render(request,'parametre.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def assoctiontype(request):
    existing_types = AssociationType.objects.all()
    if request.method == 'POST':
        form = AssociationTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assoctiontype')
    else:
        form = AssociationTypeForm()
    return render(request,'assoctiontype.html',{'form': form ,'existing_types':existing_types})

def delete_association_type(request, type_id):
    association_type = get_object_or_404(AssociationType, pk=type_id)
    association_type.delete()
    return redirect('assoctiontype')

def permission_denied_view(request):
    return render(request, 'permission_denied.html')


def generate_pdf(request, facture_id,reservation_id):
    facture = get_object_or_404(FactureFinale, id=facture_id)
    reservation = get_object_or_404(Reservation, id=reservation_id)
    association_criteria = get_object_or_404(AssociationCriteria, association_id='111111')
    nbrnu = (reservation.date_sortie-reservation.date_arriv).days

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles['Normal'].fontSize = 8
    styles['Title'].fontSize = 12
    normal_style = styles['Normal']
    normal_style.fontName = 'Times-Bold'  # Set the font family
    normal_style.fontSize = 8

    elements = []
    informations = InforamtionHotel.load()
    # Add STE HOTEL MONSTIR header
    header = Paragraph(f"{informations.Nom}", styles['Title'])
    elements.append(header)

    # Add a spacer
    elements.append(Spacer(1, 10))

    # Add address information
    address = f"Adress :{informations.Adress} | Email: {informations.email}"
    elements.append(Paragraph(address, styles['Normal']))

    elements.append(Spacer(1, 5))

    fixfax = Paragraph(f"TEL:{informations.FIX} |  FAX: {informations.FAX}", styles['Normal'])
    elements.append(fixfax)
    elements.append(Spacer(1, 5))
    invoice_details = f"FACTURE N : {facture.id}\n  du : {date.today()} _____POUR     {facture.nom_assi}.{facture.code_assi}"
    elements.append(Paragraph(invoice_details, styles['Normal']))
    elements.append(Spacer(1, 5))


    tva = f"CODE TVA : {informations.codeTva}"
    elements.append(Paragraph(tva, styles['Normal']))


    # Add a spacer
    elements.append(Spacer(1, 24))
    discounts_detail = facture.discounts_detail
    discounts_detail_list = discounts_detail.split('-')
    formatted_discounts_detail = []
    for detail in discounts_detail_list:
        if detail.strip():
            formatted_discounts_detail.append(f"{detail.strip()}")
    formatted_discounts_detail_text = '\n'.join(formatted_discounts_detail)

    y=0
    nbrper = 0
    # Create table for occupants
    table_data = [["Nom", "Prénom","age" ,"Pension", "Catégorie", "Période","nbr nuite" ,"Réduction","Base", "Montant"]]
    for occupant in reservation.paxes.all():
        nbrper += 1
        reduction_percentage = ""
        x = 0
        for line in formatted_discounts_detail:
            if (occupant.first_name in line) and (occupant.last_name in line):
                reduction_percentage = line.split("%")[0]
                reduction_percentage_2 =  (float(line.split("%")[0]) / 100 )
                x = float(facture.tarif) * float(reduction_percentage_2)
                break
        if reduction_percentage:
            redred= f'-{reduction_percentage}%'
        else:
            redred = ''
        ch = ''
        if reservation.type_pension == 'pension complte':
            ch = 'PC'
        elif reservation.type_pension == 'demi pension':
            ch = 'DP'
        elif reservation.type_pension == 'LOG':
            ch = 'LOG'
        elif reservation.type_pension == 'LPD':
            ch = 'LPD'

        ch2 = ''
        if reservation.categorie == 'indiv':
            ch2 = 'SGL'
        if reservation.categorie == 'double':
            ch2 = 'DBL'
        if reservation.categorie == 'triple':
            ch2 = 'TPL'
        table_data.append([occupant.first_name, occupant.last_name, occupant.age,ch, ch2,
                           f"du {reservation.date_arriv} au {reservation.date_sortie}",nbrnu,redred ,float(facture.tarif) - float(x), float(nbrnu)*(float(facture.tarif)-float(x))])

        y += float(nbrnu)*(float(facture.tarif)-float(x))

    discounts_detail_paragraph = Paragraph(f'<font size="5.8">{facture.discounts_detail}</font>', normal_style)
    table_data.append(["", "", "", "", "","","","", ""])

    table_data.append(["", "", "", "", "","","",f'-{facture.discounts}%', "Total", y])
    table_data.append(["", "", "", "", "","","","", "TotalTTC", facture.final_price_with_discount])


    cell_style = [
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8.3)
    ]
    table = Table(table_data, colWidths=[60, 60, 20,60, 55, 130,60 ,60,60, 60])
    table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    *cell_style

    ]))
    elements.append(table)

    numeric_part = ''.join(filter(lambda x: x.isdigit() or x == '.', facture.final_price_with_discount))
    amount_float = Decimal(numeric_part)



    netapayer = Paragraph(f'<font size="10">     Net a payer</font>', normal_style)

    elements.append(Spacer(1, 24))
    taxes_instance = Taxes.load()
    fdcst_value = taxes_instance.FDCST
    tva_value = taxes_instance.TVA
    fdcst_valuepersentage = fdcst_value / 100
    tva_valuepersentage  = tva_value/ 100
    tauxx = (1+tva_valuepersentage) * (1+fdcst_valuepersentage)
    taxe_sejour_value = taxes_instance.taxe_sejour
    frais_de_timbre_value = taxes_instance.frais_de_timbre
    total_hors_taxe=round(amount_float/tauxx,3)
    fdcstfinal = total_hors_taxe * fdcst_valuepersentage
    totalhortva = total_hors_taxe + fdcstfinal
    tvaa = totalhortva * tva_valuepersentage
    toto = tvaa + totalhortva
    if nbrnu <= 14 :
        coaf_sejour = nbrnu
    else:
        coaf_sejour = 14

    taxsejour = (taxe_sejour_value * coaf_sejour) * nbrper
    apayer = amount_float + taxsejour  + frais_de_timbre_value

    table_data_2 = [["Libelle", "Base", "Taux", "Montatnt"]]
    table_data_2.append(["Total","","",f'{facture.final_price_with_discount}'])
    table_data_2.append(["Total hors taxe","","",total_hors_taxe])
    table_data_2.append(["F.D.C.S.T",total_hors_taxe,fdcst_value,round(fdcstfinal,3)])
    table_data_2.append(["Total hors T.V.A","","",round(totalhortva,3)])
    table_data_2.append(["T.V.A 7%",round(totalhortva,3),tva_value,round(tvaa,3)])
    table_data_2.append(["Total T.T.C","","",round(toto,3)])
    table_data_2.append(["Taxe / Sejour","","",f'{taxsejour}'])
    table_data_2.append(["Frais de timbrage","","",f'{frais_de_timbre_value}'])
    table_data_2.append([netapayer,"","",round(apayer,3)])





    cell_style = [
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 6.5)
    ]
    table2 = Table(table_data_2, colWidths=[200, 80, 80, 100])
    table2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    *cell_style

    ]))
    elements.append(table2)


    amount_float = Decimal(round(apayer,3))
    number_in_words = num2words(amount_float, lang='fr')
    diget = f"{number_in_words} {association_criteria.monnaie}"
    elements.append(Paragraph(diget, styles['Normal']))

    # Build the PDF document
    doc.build(elements)
    # Save the PDF file
    dt = date.today().strftime("%d-%m-%Y")
    file_path = os.path.join(settings.MEDIA_ROOT, 'pdf_files', f'facture_{facture.code_assi}_{facture.id}_{dt}.pdf')

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as pdf_file:
        pdf_file.write(buffer.getvalue())

    # Return the PDF as a response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.code_assi}_{facture.id}_{dt}.pdf"'
    response.write(pdf)

    return redirect(settings.MEDIA_URL + f'pdf_files/facture_{facture.code_assi}_{facture.id}_{dt}.pdf')

def generate_pdff(request, facture_id, reservation_id):
    facture = get_object_or_404(FactureFinale, id=facture_id)
    reservation = get_object_or_404(ReservationGroubeFinale, id=reservation_id)
    association_criteria = get_object_or_404(AssociationCriteria, association_id=reservation.code_assi)
    nbrnu = (reservation.date_depart-reservation.date_arrivee).days

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles['Normal'].fontSize = 8
    styles['Title'].fontSize = 12
    normal_style = styles['Normal']
    normal_style.fontName = 'Times-Bold'  # Set the font family
    normal_style.fontSize = 8

    elements = []

    # Add STE HOTEL MONSTIR header
    informations = InforamtionHotel.load()
    # Add STE HOTEL MONSTIR header
    header = Paragraph(f"{informations.Nom}", styles['Title'])
    elements.append(header)



    # Add a spacer
    elements.append(Spacer(1, 10))

    # Add address information
    address = f"Adress :{informations.Adress} |Email: {informations.email} &nbsp; &nbsp; &nbsp;  "
    elements.append(Paragraph(address, styles['Normal']))

    elements.append(Spacer(1, 5))

    fixfax = Paragraph(f"TEL:{informations.FIX} |  FAX: {informations.FAX}", styles['Normal'])
    elements.append(fixfax)
    elements.append(Spacer(1, 5))
    invoice_details = f"FACTURE N : {facture.id}\n  du : {date.today()}  &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp; &nbsp;&nbsp; &nbsp;  Code Client:   {facture.code_assi}&nbsp; &nbsp; &nbsp; Nom Client : {facture.nom_assi}"
    elements.append(Paragraph(invoice_details, styles['Normal']))
    elements.append(Spacer(1, 5))


    tva = f"CODE TVA : {informations.codeTva}"
    elements.append(Paragraph(tva, styles['Normal']))

    # Add a spacer
    elements.append(Spacer(1, 24))
    discounts_detail = facture.discounts_detail
    discounts_detail_list = discounts_detail.split('-')
    formatted_discounts_detail = []
    for detail in discounts_detail_list:
        if detail.strip():
            formatted_discounts_detail.append(f"{detail.strip()}")
    formatted_discounts_detail_text = '\n'.join(formatted_discounts_detail)
    nbrper = 0
    y=0
    # Create table for occupants
    table_data = [["Nom", "Prénom","age" ,"Pension", "Catégorie", "Période","nbr nuite" ,"Réduction","Base", "Montant"]]
    for occupant in reservation.occupant.all():
        nbrper += 1
        reduction_percentage = ""
        x = 0
        for line in formatted_discounts_detail:
            if (occupant.nom in line) and (occupant.prenom in line):
                reduction_percentage = line.split("%")[0]
                reduction_percentage_2 =  (float(line.split("%")[0]) / 100 )
                x = float(facture.tarif) * float(reduction_percentage_2)
                break
        if reduction_percentage:
            redred= f'-{reduction_percentage}%'
        else:
            redred = ''

        ch = ''
        if reservation.pension == 'pension complte':
            ch = 'PC'
        elif reservation.pension == 'demi pension':
            ch = 'DP'
        elif reservation.pension == 'LOG':
            ch = 'LOG'
        elif reservation.pension == 'LPD':
            ch = 'LPD'
        ch2 = ''
        if reservation.categorie == 'indiv':
            ch2 = 'SGL'
        if reservation.categorie == 'double':
            ch2 = 'DBL'
        if reservation.categorie == 'triple':
            ch2 = 'TPL'

        table_data.append([occupant.nom, occupant.prenom, occupant.age,ch, ch2 ,
                           f"du {reservation.date_arrivee} au {reservation.date_depart}",(reservation.date_depart-reservation.date_arrivee).days,redred ,float(facture.tarif) - float(x), float(nbrnu)*(float(facture.tarif)-float(x))])

        y += float(nbrnu)*(float(facture.tarif)-float(x))

    discounts_detail_paragraph = Paragraph(f'<font size="5.8">{facture.discounts_detail}</font>', normal_style)
    table_data.append(["", "", "", "", "","","","", ""])

    table_data.append(["", "", "", "", "","","",f'-{facture.discounts}%', "Total", y])
    table_data.append(["", "", "", "", "","","", "","TotalTTC", facture.final_price_with_discount])


    cell_style = [
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8.3)
    ]
    table = Table(table_data, colWidths=[60, 60, 20,60, 55, 130,60 ,60,60, 60])
    table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    *cell_style

    ]))
    elements.append(table)

    numeric_part = ''.join(filter(lambda x: x.isdigit() or x == '.', facture.final_price_with_discount))
    amount_float = Decimal(numeric_part)



    netapayer = Paragraph(f'<font size="10">     Net a payer</font>', normal_style)

    elements.append(Spacer(1, 24))
    taxes_instance = Taxes.load()
    fdcst_value = taxes_instance.FDCST
    tva_value = taxes_instance.TVA
    fdcst_valuepersentage = fdcst_value / 100
    tva_valuepersentage  = tva_value/ 100
    tauxx = (1+tva_valuepersentage) * (1+fdcst_valuepersentage)
    taxe_sejour_value = taxes_instance.taxe_sejour
    frais_de_timbre_value = taxes_instance.frais_de_timbre
    total_hors_taxe=round(amount_float/tauxx,3)
    fdcstfinal = total_hors_taxe * fdcst_valuepersentage
    totalhortva = total_hors_taxe + fdcstfinal
    tvaa = totalhortva * tva_valuepersentage
    toto = tvaa + totalhortva
    if nbrnu <= 14 :
        coaf_sejour = nbrnu
    else:
        coaf_sejour = 14


    taxsejour = (taxe_sejour_value * nbrper) * coaf_sejour
    apayer = amount_float + taxsejour   + frais_de_timbre_value

    table_data_2 = [["Libelle", "Base", "Taux", "Montatnt"]]
    table_data_2.append(["Total","","",f'{facture.final_price_with_discount}'])
    table_data_2.append(["Total hors taxe","","",total_hors_taxe])
    table_data_2.append(["F.D.C.S.T",total_hors_taxe,fdcst_value,round(fdcstfinal,3)])
    table_data_2.append(["Total hors T.V.A","","",round(totalhortva,3)])
    table_data_2.append(["T.V.A 7%",round(totalhortva,3),tva_value,round(tvaa,3)])
    table_data_2.append(["Total T.T.C","","",f'{facture.final_price_with_discount}'])
    table_data_2.append(["Taxe / Sejour","","",f' {taxsejour}'])
    table_data_2.append(["Frais de timbrage","","",f' {frais_de_timbre_value}'])
    table_data_2.append([netapayer,"","",round(apayer,3)])





    cell_style = [
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 6.5)
    ]
    table2 = Table(table_data_2, colWidths=[200, 80, 80, 100])
    table2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    *cell_style

    ]))
    elements.append(table2)


    amount_float = Decimal(round(apayer,3))
    number_in_words = num2words(amount_float, lang='fr')
    diget = f"{number_in_words} {association_criteria.monnaie}"
    elements.append(Paragraph(diget, styles['Normal']))

#    datedereervation = Paragraph(f"date de reservation {facture.date_reservation}", styles['Normal'])
#    elements.append(datedereervation)
    # Build the PDF document
    doc.build(elements)
    # Save the PDF file
    dt = date.today().strftime("%d-%m-%Y")
    file_path = os.path.join(settings.MEDIA_ROOT, 'pdf_files', f'facture_{facture.code_assi}_{facture.id}_{dt}.pdf')

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as pdf_file:
        pdf_file.write(buffer.getvalue())

    # Return the PDF as a response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.code_assi}_{facture.id}_{dt}.pdf"'
    response.write(pdf)

    return redirect(settings.MEDIA_URL + f'pdf_files/facture_{facture.code_assi}_{facture.id}_{dt}.pdf')

def generate_pdfff(request, association_id):
    # Get AssociationCriteria and related data
    association_criteria = get_object_or_404(AssociationCriteria, association_id=association_id)
    seasons = Season.objects.filter(association_criteria=association_criteria)
    season_categories = SeasonCategorie.objects.filter(season__in=seasons)

    # Create a BytesIO object to store the PDF
    buffer = BytesIO()
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='TitleStyle', fontSize=16, alignment=1)
    heading_style = ParagraphStyle(name='HeadingStyle', fontSize=14, alignment=1)
    styles.add(title_style)
    styles.add(heading_style)

    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Build content for the PDF
    content = []

    # Title
    content.append(Paragraph("Contrat Detail", styles['Title']))

    # AssociationCriteria Information
    association_table_data = [
        ["Association", str(association_criteria.association)],
        ["Debut Contrat", str(association_criteria.debut_contart)],
        ["Fin Contrat", str(association_criteria.fin_contrat)],
        ["Monnaie", str(association_criteria.monnaie)],
    ]
    association_table = Table(association_table_data, colWidths=[100, 200])
    association_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    content.append(association_table)

    # Seasons and Categories
    for season in seasons:
        season_header = Paragraph(f"Season: {season.name_season}", styles['Heading3'])
        content.append(season_header)

        # Season Table
        season_table_data = [
            ["Start Date", "End Date"],
            [str(season.start_date), str(season.end_date)],
        ]
        season_table = Table(season_table_data, colWidths=[100, 200])
        season_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(season_table)

        # Categories Table
        category_table_data = [
            ["Category", "Demipension Price", "Pensioncomplte Price", "Log Price", "LPD Price"],
        ]
        for category in season.categories.all():
            category_table_data.append([
                category.get_cat_display(),
                str(category.demipension_price),
                str(category.pensioncomplte_price),
                str(category.log_price),
                str(category.lpd_price),
            ])
        category_table = Table(category_table_data, colWidths=[100, 100, 100, 100, 100])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
        ]))
        content.append(category_table)
    for season in seasons:
        season_header = Paragraph(f"Season: {season.name_season}", styles['Heading3'])
        content.append(season_header)

            # ... existing code ...

            # Add new information table for each season
        season_info_table_data = [
                ["Discount", "Threshold"],
                [f"Duration: {season.duration_discount}%", f"more then: {season.duration_threshold} days"],
                [f"Early Booking: {season.earlybooking_discount}%", f"before : {season.earlybooking_threshold} days"],
                [f"Mineur: {season.mineur_discount}%", f"if age : {season.mineur_threshold} "],
                [f"Mineur: {season.mineur2_discount}%", f"if age: {season.mineur2_threshold} "],
                [f"Pax Number 3: {season.paxnum3_discount}%", ],
            ]
        season_info_table = Table(season_info_table_data, colWidths=[200, 200])
        season_info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
        content.append(season_info_table)

    doc.build(content)
    file_path = os.path.join(settings.MEDIA_ROOT, 'contrat', f'Contrat_Client_N{association_criteria.association.code}.pdf')

    # Set response headers to serve the PDF
    response = HttpResponse(content_type='application/pdf')

    # Write the PDF data to the response
    response.write(buffer.getvalue())
    with open(file_path, 'wb') as file:
        file.write(response.content)
    buffer.close()

    return response



@login_required
def pdf_list(request):
    custom_directory = 'pdf_files'
    custom_directory2 = 'contrat'
    pdf_files = []
    contract = []
    pdf_files_dir = os.path.join(settings.MEDIA_ROOT, custom_directory)
    if os.path.exists(pdf_files_dir) and os.path.isdir(pdf_files_dir):
        pdf_files = [f for f in os.listdir(pdf_files_dir) if f.endswith('.pdf')]

    pdf_files_dir_2 = os.path.join(settings.MEDIA_ROOT, custom_directory2)
    if os.path.exists(pdf_files_dir_2) and os.path.isdir(pdf_files_dir_2):
        contract = [f for f in os.listdir(pdf_files_dir_2) if f.endswith('.pdf')]

    search_query = request.GET.get('q', '')

    # Apply search query filter
    if search_query:
        pdf_files = [pdf_file for pdf_file in pdf_files if search_query.lower() in pdf_file.lower()]
        contract = [cont for cont in contract if search_query.lower() in cont.lower()]

    # Pagination logic
    page_num = request.GET.get('page')
    paginator = Paginator(pdf_files, 20)  # Show 20 files per page
    page = paginator.get_page(page_num)
    # Pagination logic for contracts
    contract_page_num = request.GET.get('contract_page')
    contract_paginator = Paginator(contract, 20)  # Show 20 contracts per page
    contract_page = contract_paginator.get_page(contract_page_num)


    # Pass variables to the template
    context = {
        'pdf_files': page,
        'search_query': search_query,
        'contract': contract_page,  # Use the contract_page instead of contract
        'contract_page_num': int(contract_page_num) if contract_page_num else 1,
        'total_contract_pages': contract_paginator.num_pages,
        'page_num': int(page_num) if page_num else 1,
        'total_pages': paginator.num_pages,
    }

    return render(request, 'pdf_list.html', context)



@login_required
def view_pdf(request, pdf_file_name):
    pdf_paths = [
        os.path.join(settings.MEDIA_ROOT, 'pdf_files', pdf_file_name),
        os.path.join(settings.MEDIA_ROOT, 'contrat', pdf_file_name),
    ]

    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{pdf_file_name}"'
                return response

    # If none of the paths existed
    return HttpResponse("PDF not found.", status=404)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Username OR password is incorrect')
    return render(request,'login.html')
@login_required
def clientview(request):
    return render(request,'client.html')
@login_required
def reservationview(request):
    return render(request,'reservation.html')

@login_required
def update_client(request):
    clients = Client.objects.all()
    search_query = request.GET.get('search_query')

    if search_query:
        clients = clients.filter(
            Q(codeclient__icontains=search_query) | Q(nomclient__icontains=search_query)
        )

    return render(request, 'update_client.html', {'clients': clients})

@login_required
def edit_client(request, client_code):
    client = get_object_or_404(Client, codeclient=client_code)

    if request.method == 'POST':
        form = UpdateClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('update_client')
    else:
        form = UpdateClientForm(instance=client)

    return render(request, 'edit_client.html', {'form': form})

@login_required
def search_client(request):
    search_field = request.GET.get('search_field')
    search_value = request.GET.get('search_value')

    clients = []

    if search_field == 'id':
        try:
            client = Client.objects.get(id=int(search_value))
            clients.append(client)
        except (Client.DoesNotExist, ValueError):
            pass
    elif search_field == 'name':
        clients = Client.objects.filter(nomclient__icontains=search_value)

    context = {
        'clients': clients,
        'search_field': search_field,
        'search_value': search_value,
    }
    return render(request, 'search_client.html', context)

@login_required
def availblee_room(request):
    date_arriv = request.GET.get('date_arriv')
    date_sortie = request.GET.get('date_sortie')
    chambre_type = request.GET.get('chambre_type')
    chambre_vue = request.GET.get('chambre_vue')

    available_rooms = Chambre.objects.all()

    if date_arriv and date_sortie:
        # Query reserved room IDs for the given date range
        reserved_chambre_ids = RoomAvailability.objects.filter(
            date_arriv__lt=date_sortie,
            date_sortie__gt=date_arriv
        ).values_list('chambre_id', flat=True)

        available_rooms = available_rooms.exclude(chambre_id__in=reserved_chambre_ids)

    if chambre_type and chambre_type != 'Any':
        available_rooms = available_rooms.filter(chambre_type=chambre_type)

    if chambre_vue and chambre_vue != 'Any':
        available_rooms = available_rooms.filter(chambre_Vue=chambre_vue)
    x = [('indiv', 'indiv'), ('double', 'double'), ('triple', 'triple')]
    y = [('Vue picine', 'Vue picine'), ('normal', 'nomal'),('Vue sur mer','Vue sur mer')]


    return render(request, 'availblee_room.html', {
        'available_rooms': available_rooms,
        'date_arriv': date_arriv,
        'date_sortie': date_sortie,
        'chambre_type': chambre_type,
        'chambre_vue': chambre_vue,
        'x': x,
        'y': y,
    })





@login_required
def selectclienttoreserv(request):
    clients = Client.objects.all()
    search_query = request.GET.get('search_query')

    if search_query:
        clients = clients.filter(
            Q(codeclient__icontains=search_query) | Q(nomclient__icontains=search_query)
        )

    return render(request, 'selectclient.html', {'clients': clients})


@login_required
def create_reservation(request):
    client = get_object_or_404(Client, codeclient=111111)

    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST)

        if reservation_form.is_valid():
            reservation = reservation_form.save(commit=False)
            reservation.clients = client
            reservation.save()

            return redirect('enter_paxes', reservation_id=reservation.id)  # Redirect to paxes entry page
    else:
        reservation_form = ReservationForm()

    # Rest of the code

    return render(request, 'reservation_form.html', {
        'reservation_form': reservation_form,
        'client': client,
    })

@login_required
def reservation_list_2(request):
    reservations = Reservation.objects.all()
    id_search = request.GET.get('id')
    date_arrivee_search = request.GET.get('date_arrivee')
    date_depart_search = request.GET.get('date_depart')
    if id_search:
        reservations = reservations.filter(id__icontains=id_search)
    if date_arrivee_search and date_depart_search:
        date_arrivee = parse_date(date_arrivee_search)
        date_depart = parse_date(date_depart_search)
        reservations = reservations.filter(date_arriv__lte=date_depart, date_sortie__gte=date_arrivee)
    return render(request, 'reservation_list_2.html', {'reservations': reservations})
@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('assign_rooms', reservation_id=reservation.id)  # Redirect to detail page
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'edit_reservation.html', {'form': form, 'reservation': reservation})
@login_required
def update_pax(request, pax_id):
    pax = get_object_or_404(Pax, pk=pax_id)

    if request.method == 'POST':
        form = PaxForm(request.POST, instance=pax)
        if form.is_valid():
            form.save()
            return redirect('reservation_list_2')  # Redirect to the reservation list after updating pax
    else:
        form = PaxForm(instance=pax)

    return render(request, 'update_paxes.html', {'form': form, 'pax': pax})

@login_required
def delete_pax(request, type_id , reservation_id):
    occupant = get_object_or_404(Pax, pk=type_id)
    occupant.delete()
    return redirect('enter_paxes' , reservation_id=reservation_id)


@login_required
def enter_paxes(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    pax_objects = reservation.paxes.all()

    if request.method == 'POST':
        pax_form = PaxForm(request.POST)

        if pax_form.is_valid():
            pax = pax_form.save()
            reservation.paxes.add(pax)  # Add the pax to the reservation's paxes field
            if 'save_and_add_another' in request.POST:
                pax_form = PaxForm()  # Clear the form for adding another pax
            else:
                return redirect('assign_rooms', reservation_id=reservation.id)  # Redirect to assign_rooms view

    else:
        pax_form = PaxForm()

    return render(request, 'enter_paxes.html', {
        'pax_form': pax_form,
        'reservation': reservation,
        'pax_objects' : pax_objects ,
    })

def save_rooms_to_availability_for_reservation(reservation):
    assigned_rooms = reservation.chambre.all()
    room_availability_list = []
    for room in assigned_rooms:
        room_availability = RoomAvailability(
            chambre=room,
            champre_type=room.chambre_type,
            champre_Vue=room.chambre_Vue,
            date_arriv=reservation.date_arriv,
            date_sortie=reservation.date_sortie,
            name_assi=reservation.clients.nomclient,  # You might need to adjust this based on your models
            reservation = f'{reservation.id} Reservation',
            dispo=False,
        )
        room_availability_list.append(room_availability)
    RoomAvailability.objects.bulk_create(room_availability_list)


@login_required
def assign_rooms(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    paxes = reservation.paxes.all()
    date_arriv= reservation.date_arriv
    date_sortie = reservation.date_sortie
    available_rooms = Chambre.objects.all()
    if date_arriv and date_sortie:
        # Query reserved room IDs for the given date range
        reserved_chambre_ids = RoomAvailability.objects.filter(
            date_arriv__lt=date_sortie,
            date_sortie__gt=date_arriv
        ).values_list('chambre_id', flat=True)

        available_rooms = available_rooms.exclude(chambre_id__in=reserved_chambre_ids)




    if request.method == 'POST':
        assigned_rooms = {}

        for pax in paxes:
            room_id = request.POST.get(f'pax_{pax.id}_room')
            if room_id:
                room = get_object_or_404(Chambre, chambre_id=room_id)
                assigned_rooms[pax] = room
                room_availability_list = []
                room_assignment = RoomAssignment(
                room=room,
                occupants=f'{pax.first_name}.{pax.last_name}',
                date_arriv=reservation.date_arriv,
                date_sortie=reservation.date_sortie,
                code_assi=reservation.clients.codeclient,  # Use client's codeclient
                nom_assi=f'{reservation.clients.nomclient} Client individuel ',  # Use client's nomclient
                reservation = f'{reservation.id} Reservation'
                )
                room_availability_list.append(room_assignment)
        RoomAssignment.objects.bulk_create(room_availability_list)

        reservation.chambre.clear()
        for pax, room in assigned_rooms.items():
            reservation.chambre.add(room)
        reservation.nbr_personne = len(paxes)
        reservation.save()
        save_rooms_to_availability_for_reservation(reservation)

        return redirect('reservation_info', reservation_id=reservation_id)  # Redirect back to reservation detail

    return render(request, 'assign_rooms.html', {
        'paxes': paxes,
        'available_rooms': available_rooms,
        'reservation': reservation,
    })

@login_required
def reservation_info(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    associationcriteria = AssociationCriteria.objects.get(association='111111')
    seasons = []
    if associationcriteria:
        associated_seasons = Season.objects.filter(association_criteria=associationcriteria)
        selected_seasons = []

        for season in associated_seasons:
            if (season.start_date <= reservation.date_arriv <= season.end_date) or \
                (season.start_date <= reservation.date_sortie <= season.end_date) or \
                (reservation.date_arriv <= season.start_date <= reservation.date_sortie) or \
                (reservation.date_arriv <= season.end_date <= reservation.date_sortie):
                selected_seasons.append(season)
        if selected_seasons:
            for season in selected_seasons:
                part_start_date = max(season.start_date, reservation.date_arriv)
                part_end_date = min(season.end_date, reservation.date_sortie)
                part_duration = (part_end_date - part_start_date).days
                if part_duration == 0:
                    part_duration = 1
                typedecategorie = reservation.categorie
                nbr_personne = reservation.nbr_personne

                season_categorie = season.categories.get(cat=typedecategorie)
                demipension_price = season_categorie.demipension_price
                pensioncomplte_price = season_categorie.pensioncomplte_price
                log_price = season_categorie.log_price
                lpd_price = season_categorie.lpd_price
                typedepension = reservation.type_pension
                pu = 0
                if typedepension == 'pension complte':
                    if reservation.prix_force or reservation.prix_force != 0:
                        pu = reservation.prix_force
                    else:
                        pu = pensioncomplte_price
                elif typedepension == 'demi pension':
                    if reservation.prix_force or reservation.prix_force != 0:
                        pu = reservation.prix_force
                    else:
                        pu = demipension_price
                elif typedepension == 'LOG':
                    if reservation.prix_force or reservation.prix_force != 0:
                        pu = reservation.prix_force
                    else:
                        pu = log_price
                elif typedepension == 'LPD':
                    if reservation.prix_force or reservation.prix_force != 0:
                        pu = reservation.prix_force
                    else:
                        pu = lpd_price
                else:
                    pu = 0
                toto = 0
                dis_detail=''
                prixsans = 0
                for occupant in reservation.paxes.all():
                    age = occupant.age
                    if age is None:
                        age = 10000
                    if age <  season.mineur_threshold:
                        dis = (float(season.mineur_discount)/100) * float(pu)
                        prixsans += float(pu)
                        toto += float(pu) - dis
                        dis_detail += f'-{season.mineur_discount}% '
                    elif age < season.mineur2_threshold:
                        dis2 = (float(season.mineur2_discount)/100) * float(pu)
                        prixsans += float(pu)
                        toto += float(pu) - dis2
                        dis_detail += f'-{season.mineur2_discount}% '
                    else:
                        prixsans += float(pu)
                        toto += float(pu)
                prixsansfinale = float(prixsans * part_duration)
                prix = float(toto * part_duration)
                discount = 0
                if part_duration >= season.duration_threshold:
                    discount += season.duration_discount
                    if season.duration_discount != 0:
                        dis_detail += f'-{season.duration_discount}% '


                discount_f = (float(discount) / 100) * prix
                prix_finale = Decimal(prix) - Decimal(discount_f)
                seasons.append({
                    'season': season,
                    'part_start_date': part_start_date,
                    'part_end_date': part_end_date,
                    'total_price':prixsansfinale,
                    'price': prix_finale,
                })

            total_price_without_discount = sum(part['total_price'] for part in seasons)
            total_price_all_parts = sum(part['price'] for part in seasons)

            finale = f'{total_price_without_discount} {associationcriteria.monnaie}'
            finalewithdiscount = f'{total_price_all_parts} {associationcriteria.monnaie}'

            facture = FactureFinale(
            reservation_code = reservation.id,
            code_assi=reservation.clients.codeclient,
            nom_assi = reservation.clients.nomclient,
            date_arrivee=reservation.date_arriv,
            date_depart=reservation.date_sortie,
            pension=reservation.type_pension,
            categorie=reservation.categorie,
            discounts=discount,
            discounts_detail=dis_detail,
            tarif = pu ,
            price_without_discount=finale,
            final_price_with_discount=finalewithdiscount,
        )
            facture.save()
    return render(request, 'reservation_info.html', {
        'reservation': reservation,
        'finale':finale,
        'finalewithdiscount':finalewithdiscount,
        'facture':facture,

    })

@login_required
def create_client(request):
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        if 'submit_client' in request.POST and client_form.is_valid():
            client_form.save()
            return redirect('dashboard')  # Redirect to the same page after creating the client
        elif 'create_reservation' in request.POST and client_form.is_valid():
            client = client_form.save()  # Save the client instance to get the client object
            return redirect('create_reservation')
    else:
        client_form = ClientForm()

    context = {
        'client_form': client_form,
    }
    return render(request, 'client_form.html', context)

@login_required
def dashboard(request):
    total_final_price = FactureFinale.objects.aggregate(Sum('final_price_with_discount'))

    # Sum of final_price_with_discount for each category
    category_sums = ReservationGroubeFinale.objects.values('categorie').annotate(category_sum=Count('price'))
    category_sums = [{'categorie': entry['categorie'], 'category_sum': round(entry['category_sum'], 3) if entry['category_sum'] is not None else 0} for entry in category_sums]

    # Sum of final_price_with_discount for each pension
    pension_sums = ReservationGroubeFinale.objects.values('pension').annotate(pension_sum=Count('price'))
    pension_sums = [{'pension': entry['pension'], 'pension_sum': round(entry['pension_sum'], 3) if entry['pension_sum'] is not None else 0} for entry in pension_sums]

    # Sum of final_price_with_discount for every 3 months of the year
    quarterly_sums = []
    current_year = datetime.now().year
    monthly_sums = []


    for month in range(1, 13):
        start_date = f'{current_year}-{month:02d}-01'
        next_month = month + 1 if month < 12 else 1
        next_year = current_year + 1 if month == 12 else current_year
        end_date = (datetime.strptime(f'{next_year}-{next_month:02d}-01', '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        monthly_sum = ReservationGroubeFinale.objects.filter(date_arrivee__range=[start_date, end_date]).aggregate(Sum('price'))
        monthly_sum_value = monthly_sum['price__sum']
        quarterly_sums.append({'start_date': start_date, 'end_date': end_date, 'quarterly_sum': round(monthly_sum_value, 3) if monthly_sum_value is not None else 0})

    most_common = ReservationGroubeFinale.objects.values('code_assi', 'pension').annotate(
         pension_sum=Sum('price'))
    europension = defaultdict()
    dollarpension = defaultdict()
    dinarpension = defaultdict()
    unique_pensions = set(entry['pension'] for entry in most_common)

    for pension in unique_pensions:
        dinarpension[pension] = 0
        europension[pension] = 0
        dollarpension[pension] = 0

    for entery in most_common:
        code_assii = entery['code_assi']
        pension = entery ['pension']
        pension_sum = entery['pension_sum']

        try:
            association_criteria = AssociationCriteria.objects.get(association=code_assii)
            monnaie = association_criteria.monnaie

        except AssociationCriteria.DoesNotExist:
            monnaie = 'TND'
        if monnaie == 'EUR':
            europension[pension] += pension_sum
        elif monnaie == 'USD':
            dollarpension[pension] += pension_sum
        elif monnaie == 'TND':
            dinarpension[pension] += pension_sum
    # Query to find the most common code_assi
    most_common_code_assi_info = ReservationGroubeFinale.objects.values('code_assi', 'nom_assi').annotate(
        count=Count('code_assi'), total_price=Sum('price')).order_by('-count')
    dollar = 0
    euro = 0
    dinar = 0
    most_common_entries = []
    for entry in most_common_code_assi_info:
        code_assi = entry['code_assi']
        nom_assi = entry['nom_assi']
        reservation_count = entry['count']
        total_price = entry['total_price']
        if total_price is not None:
            total_price = round(total_price,3)
        else:
            total_price = 0

        try:
            association_criteria = AssociationCriteria.objects.get(association=code_assi)
            monnaie = association_criteria.monnaie
            if monnaie == 'EUR':
                euro +=  total_price
            elif monnaie == 'USD':
                dollar += total_price
            elif monnaie == 'TND':
                dinar += total_price

        except AssociationCriteria.DoesNotExist:
            monnaie = 'TND'
            dinar += total_price
        most_common_entries.append({'code_assi': code_assi, 'nom_assi': nom_assi, 'reservation_count': reservation_count, 'monnaie': monnaie ,'total_price':total_price,})

    nationaliti = Occupant.objects.values('nationalite').annotate(
        count=Count('nationalite')).order_by('-count')

    natio = []
    for enteryy in nationaliti:
        nationalite = enteryy['nationalite']
        count = enteryy['count']


        if nationalite is not None:
            country_name = COUNTRIES[nationalite]

            natio.append({'count':count , 'nationalite' :nationalite , 'country_name' : country_name})


    return render(request, 'dashboard.html', {
        'total_final_price': round(total_final_price['final_price_with_discount__sum'], 3) if total_final_price['final_price_with_discount__sum'] is not None else None,
        'category_sums': category_sums,
        'pension_sums': pension_sums,
        'quarterly_sums': quarterly_sums,
        'most_common_entries': most_common_entries,
        'euro':euro,
        'dollar':dollar,
        'dinar': dinar,
        'europension':europension,
        'dollarpension':dollarpension,
        'dinarpension': dinarpension,
        'natio':natio,

    })


@login_required
def create_association(request):
    if request.method == 'POST':
        form = AssociationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('association_list')
    else:
        form = AssociationForm()

    return render(request, 'create_association.html', {'form': form})

@login_required
def association_list(request):
    associations = Association.objects.all()
    search_query = request.GET.get('search_query')

    if search_query:
        associations = associations.filter(
            Q(code__icontains=search_query) | Q(nom__icontains=search_query)
        )
    return render(request, 'association_list.html', {'associations': associations})


@login_required
def association_listtoreserve(request):
    associations = Association.objects.all()
    search_query = request.GET.get('search_query')

    if search_query:
        associations = associations.filter(
            Q(code__icontains=search_query) | Q(nom__icontains=search_query)
        )
    return render(request, 'selectclientasso.html', {'associations': associations})


@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def update_association(request, association_code):
    association = get_object_or_404(Association, code=association_code)
    if request.method == 'POST':
        form = AssociationForm(request.POST, instance=association)
        if form.is_valid():
            form.save()
            return redirect('association_list')
    else:
        form = AssociationForm(instance=association)

    return render(request, 'update_association.html', {'form': form, 'association': association})

@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def delete_association(request, association_code):
    association = get_object_or_404(Association, code=association_code)
    if request.method == 'POST':
        association.delete()
        return redirect('association_list')
    return render(request, 'delete_association.html', {'association': association})

@login_required
def cons_association(request,association_code):
    association = get_object_or_404(Association, code=association_code)

    return render(request,'cons_association.html',{'association':association})


@login_required
def create_reservation_for_association(request, association_code):
    association = get_object_or_404(Association, code=association_code)

    try:
        association_criteria = AssociationCriteria.objects.get(association=association.code)
    except AssociationCriteria.DoesNotExist:
        association_criteria = None
    adver = ''
    if association_criteria:
        if request.method == 'POST':
            form = ReservationgroubeForm(request.POST)
            if form.is_valid():
                reservation = form.save(commit=False)
                reservation.association = association
                if (reservation.date_arrivee > association_criteria.fin_contrat) or (reservation.date_depart > association_criteria.fin_contrat):
                    form.add_error('date_arrivee', 'Oups ! Out of limite le contrat est expiré')
                else:
                    reservation.save()

                    return redirect('add_occupant', reservation_id=reservation.pk)  # Redirect to add occupants page
        else:
            form = ReservationgroubeForm()
    else:
        return redirect('create_association_criteria' , association_code = association.code)

    return render(request, 'create_reservation_for_association.html', {'form': form, 'association': association ,'adver':adver})

@login_required
def add_occupant(request, reservation_id):
    reservation = get_object_or_404(Reservationgroube, pk=reservation_id)

    try:
        occupants = Occupant.objects.filter(reservation=reservation_id)
    except (Occupant.DoesNotExist):
        pass

    if request.method == 'POST':
        form = OccupantForm(request.POST)
        if form.is_valid():
            occupant = form.save(commit=False)
            occupant.reservation = reservation
            occupant.save()

            if 'save_and_add_another' in request.POST:
                form = OccupantForm()  # Create a new empty form
            else:
                return redirect('assign_rooms_to_occupants', reservation_id=reservation.pk)  # Redirect to the index page after adding the last occupant
    else:
        form = OccupantForm()

    return render(request, 'add_occupant.html', {'form': form, 'reservation': reservation , 'occupants': occupants})

@login_required
def delete_occupant(request, type_id):
    occupant = get_object_or_404(Occupant, pk=type_id)
    occupant.delete()
    return redirect('add_occupant' , reservation_id=occupant.reservation.id)

def save_rooms_to_availability(reservation_groube_finale):
    room_availability_list = []
    for room in reservation_groube_finale.chambre.all():
        room_availability = RoomAvailability(
            chambre=room,
            champre_type=room.chambre_type,
            champre_Vue=room.chambre_Vue,
            date_arriv=reservation_groube_finale.date_arrivee,
            date_sortie=reservation_groube_finale.date_depart,
            name_assi=reservation_groube_finale.nom_assi,  # Concatenate occupant names
            reservation = f'{reservation_groube_finale.id} Reservationgroube',

            dispo=False,
        )
        room_availability_list.append(room_availability)
    RoomAvailability.objects.bulk_create(room_availability_list)

@login_required
def assign_rooms_to_occupants(request, reservation_id):
    reservation = get_object_or_404(Reservationgroube, id=reservation_id)
    occupants = reservation.occupants.all()

    available_rooms = Chambre.objects.all()
    date_arriv = reservation.date_arrivee
    date_sortie = reservation.date_depart
    categorie = reservation.categorie

    if date_arriv and date_sortie:
        # Query reserved room IDs for the given date range
        reserved_chambre_ids = RoomAvailability.objects.filter(
            date_arriv__lt=date_sortie,
            date_sortie__gt=date_arriv
        ).values_list('chambre_id', flat=True)

        available_rooms = available_rooms.exclude(chambre_id__in=reserved_chambre_ids)
    available_rooms = available_rooms.filter(chambre_type=categorie)
    if request.method == 'POST':
        assigned_rooms = []
        assigned_roomss = defaultdict(list)
        diction = {}
        for occupant in occupants:
            room_id = request.POST.get(f'occupant_{occupant.id}_room')
            diction[occupant]= room_id
            if room_id:
                room = get_object_or_404(Chambre, chambre_id=room_id)
                occupant.chambre = room
                occupant.save()
                assigned_rooms.append(str(room.chambre_id))
                assigned_roomss[room].append(occupant.nom)  # Group occupants by room
        occupnumb3 = set()  # Initialize a set to store third occupants
        for x in diction:
            ss = 0

            for j in diction:
                if diction[j] == diction[x]:
                    ss = ss + 1
                    if ss == 3 :
                        occupnumb3.add(j)
                        break

        room_availability_list = []
        for room, occupants_list in assigned_roomss.items():
            # Create a single RoomAssignment instance for the room and its occupants
            room_assignment = RoomAssignment(
                room=room,
                occupants=', '.join(occupants_list),  # Combine occupants' names
                date_arriv=reservation.date_arrivee,
                date_sortie=reservation.date_depart,
                code_assi=reservation.association.code,
                nom_assi=reservation.association.nom,
                reservation = f'{reservation.id} Reservation Groupe'
            )
            room_availability_list.append(room_assignment)
        RoomAssignment.objects.bulk_create(room_availability_list)


        old_reservation_groube_finale = ReservationGroubeFinale.objects.filter(coc=reservation.id).first()

        if old_reservation_groube_finale:
            # Delete the old object
            old_reservation_groube_finale.delete()
        reservation_groube_finale = ReservationGroubeFinale(
            code_assi=reservation.association.code,
            nom_assi=reservation.association.nom,
            date_reservation=reservation.date_reservation,
            date_arrivee=reservation.date_arrivee,
            date_depart=reservation.date_depart,
            pension=reservation.pension,
            categorie=reservation.categorie,
            nbr_personne=reservation.occupants.count(),
            occupantslist=', '.join(str(occupant) for occupant in reservation.occupants.all()),
            chambre_taked=','.join(assigned_rooms),
            coc = reservation.id
        )
        # Calculate the final price

        # Assign the calculated price to the price field
        reservation_groube_finale.save()
        reservation_groube_finale.occupant.set(occupants)

        reservation_groube_finale.chambre.set(assigned_rooms)
        reservation_groube_finale.occupnumb3.set(occupnumb3)
        reservation_groube_finale.save()
        save_rooms_to_availability(reservation_groube_finale)



        return HttpResponseRedirect(reverse('reservation_detail', args=[reservation_groube_finale.pk]))

    return render(request, 'assign_rooms_to_occupants.html', {'reservation': reservation, 'occupants': occupants, 'available_rooms': available_rooms})

@login_required
def reservation_list(request):
    reservations = ReservationGroubeFinale.objects.all()
    id_search = request.GET.get('id')
    code_assi_search = request.GET.get('code_assi')
    nom_assi_search = request.GET.get('nom_assi')
    date_reservation_search = request.GET.get('date_reservation')
    date_arrivee_search = request.GET.get('date_arrivee')
    date_depart_search = request.GET.get('date_depart')

    if id_search:
        reservations = reservations.filter(id__icontains=id_search)
    if code_assi_search:
        reservations = reservations.filter(code_assi__icontains=code_assi_search)
    if nom_assi_search:
        reservations = reservations.filter(nom_assi__icontains=nom_assi_search)
    if date_reservation_search:
        date_reservation = parse_date(date_reservation_search)
        reservations = reservations.filter(date_reservation=date_reservation)
    if date_arrivee_search and date_depart_search:
        date_arrivee = parse_date(date_arrivee_search)
        date_depart = parse_date(date_depart_search)
        reservations = reservations.filter(date_arrivee__lte=date_depart, date_depart__gte=date_arrivee)
    return render(request, 'reservation_list.html', {'reservations': reservations})

@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def reservation_management(request):
    reservations = ReservationGroubeFinale.objects.all()
    id_search = request.GET.get('id')
    code_assi_search = request.GET.get('code_assi')
    nom_assi_search = request.GET.get('nom_assi')
    date_reservation_search = request.GET.get('date_reservation')
    date_arrivee_search = request.GET.get('date_arrivee')
    date_depart_search = request.GET.get('date_depart')

    if id_search:
        reservations = reservations.filter(id__icontains=id_search)
    if code_assi_search:
        reservations = reservations.filter(code_assi__icontains=code_assi_search)
    if nom_assi_search:
        reservations = reservations.filter(nom_assi__icontains=nom_assi_search)
    if date_reservation_search:
        date_reservation = parse_date(date_reservation_search)
        reservations = reservations.filter(date_reservation=date_reservation)
    if date_arrivee_search and date_depart_search:
        date_arrivee = parse_date(date_arrivee_search)
        date_depart = parse_date(date_depart_search)
        reservations = reservations.filter(date_arrivee__lte=date_depart, date_depart__gte=date_arrivee)
    return render(request, 'reservation_management.html', {'reservations': reservations})

@login_required
def occupant_detail(request, occupant_id):
    occupant = get_object_or_404(Occupant, id=occupant_id)
    return render(request, 'occupant_detail.html', {'occupant': occupant})

@login_required
def update_reservation(request, reservation_id):
    reservation = get_object_or_404(ReservationGroubeFinale, id=reservation_id)
    reservation2 = get_object_or_404(Reservationgroube, id=reservation.coc)
    if request.method == 'POST':
        form = ReservationUpdateForm(request.POST, instance=reservation2)
        if form.is_valid():
            form.save()
            return redirect('assign_rooms_to_occupants', reservation_id=reservation.coc)  # Redirect to the reservation_detail view
    else:
        form = ReservationUpdateForm(instance=reservation)

    return render(request, 'update_reservation.html', {'form': form, 'reservation': reservation})
@login_required
def update_occupant(request, occupant_id):
    occupant = get_object_or_404(Occupant, id=occupant_id)

    if request.method == 'POST':
        form = OccupantForm(request.POST, instance=occupant)
        if form.is_valid():
            form.save()
            return redirect('reservation_management')  # Redirect to the reservation management page or another suitable page
    else:
        form = OccupantForm(instance=occupant)

    return render(request, 'update_occupant.html', {'form': form, 'occupant': occupant})

@login_required
def roomAssignment(request):
    search_query = request.GET.get('search_query')
    search_date = request.GET.get('search_date')


    room_assignments = RoomAssignment.objects.all()

    if search_query:
        room_assignments = room_assignments.filter(
            Q(room__chambre_id__icontains=search_query) |
            Q(nom_assi__icontains=search_query) |
            Q(code_assi__icontains=search_query) |
            Q(occupants__icontains=search_query) |
            Q(date_arriv__icontains=search_query) |
            Q(date_sortie__icontains=search_query)
        )
    if search_date:
        room_assignments = room_assignments.filter(date_arriv__lte=search_date, date_sortie__gte=search_date)

    return render(request, 'roomAssignment.html', {'roomAssignment': room_assignments})




@login_required
def reservation_detail(request, reservation_id):
    reservation_groube_finale = get_object_or_404(ReservationGroubeFinale, pk=reservation_id)
    try:
        associationcriteria = AssociationCriteria.objects.get(association=reservation_groube_finale.code_assi)
    except AssociationCriteria.DoesNotExist:
        associationcriteria = None

    seasons = []
    total_price_all_parts = None
    facture = None
    if associationcriteria:
        associated_seasons = Season.objects.filter(association_criteria=associationcriteria)
        selected_seasons = []

        for season in associated_seasons:
            if (season.start_date <= reservation_groube_finale.date_arrivee <= season.end_date) or \
                (season.start_date <= reservation_groube_finale.date_depart <= season.end_date) or \
                (reservation_groube_finale.date_arrivee <= season.start_date <= reservation_groube_finale.date_depart) or \
                (reservation_groube_finale.date_arrivee <= season.end_date <= reservation_groube_finale.date_depart):
                selected_seasons.append(season)

        if selected_seasons:
            for season in selected_seasons:
                part_start_date = max(season.start_date, reservation_groube_finale.date_arrivee)
                part_end_date = min(season.end_date, reservation_groube_finale.date_depart)
                part_duration = (part_end_date - part_start_date).days
                if part_duration == 0:
                    part_duration = 1
                typedecategorie = reservation_groube_finale.categorie
                nbr_personne = reservation_groube_finale.nbr_personne

                try:
                    season_categorie = season.categories.get(cat=typedecategorie)
                    demipension_price = season_categorie.demipension_price
                    pensioncomplte_price = season_categorie.pensioncomplte_price
                    log_price = season_categorie.log_price
                    lpd_price = season_categorie.lpd_price
                    typedepension = reservation_groube_finale.pension
                except SeasonCategorie.DoesNotExist:

                    season_categorie = None
                    demipension_price = None
                    pensioncomplte_price = None
                    log_price = None
                    lpd_price = None
                    typedepension = None


                pu = 0
                if typedepension == 'pension complte':
                    pu = pensioncomplte_price
                elif typedepension == 'demi pension':
                    pu = demipension_price
                elif typedepension == 'LOG':
                    pu = log_price
                elif typedepension == 'LPD':
                    pu = lpd_price
                else:
                    pu=0
                toto = 0
                dis_detail=''
                prixsans = 0
                for occupant in reservation_groube_finale.occupant.all():
                    age = occupant.age
                    if age is None:
                        age = 10000
                    if season.mineur2_threshold < age <  season.mineur_threshold:
                        dis = (float(season.mineur_discount)/100) * float(pu)
                        prixsans += float(pu)
                        toto += float(pu) - dis
                        dis_detail += f'-{season.mineur_discount}% pour {occupant.nom}.{occupant.prenom} '
                    elif age < season.mineur2_threshold:
                        dis2 = (float(season.mineur2_discount)/100) * float(pu)
                        prixsans += float(pu)
                        toto += float(pu) - dis2
                        dis_detail += f'-{season.mineur2_discount}% pour {occupant.nom}.{occupant.prenom} '

                    if occupant in reservation_groube_finale.occupnumb3.all():  # Check if occupant is in occupnumb3 list
                        if season.paxnum3_discount != 0 :
                            di3 = (float(season.paxnum3_discount)/100) * float(pu)
                            prixsans += float(pu)

                            toto += float(pu) - di3
                            dis_detail += f'-{season.paxnum3_discount}% pour {occupant.nom}.{occupant.prenom} '
                    else:
                        prixsans += float(pu)
                        toto += float(pu)
                prixsansfinale = float(prixsans * part_duration)
                prix = float(toto * part_duration)
                discount = 0
                if part_duration >= season.duration_threshold:
                    discount += season.duration_discount
                    if season.duration_discount != 0:
                        dis_detail += f'-{season.duration_discount}% LongStay '
                if season.earlybooking_threshold is not None :
                    if reservation_groube_finale.date_reservation <= season.earlybooking_threshold:
                        discount += season.earlybooking_discount
                        if season.earlybooking_discount != 0:
                            dis_detail += f'-{season.earlybooking_discount}% EarlyBooking '


                discount_f = (float(discount) / 100) * prix
                prix_finale = Decimal(prix) - Decimal(discount_f)
                seasons.append({
                    'season': season,
                    'part_start_date': part_start_date,
                    'part_end_date': part_end_date,
                    'total_price':prixsansfinale,
                    'price': prix_finale,
                })

            total_price_without_discount = round(sum(part['total_price'] for part in seasons), 3)
            total_price_all_parts = round(sum(part['price'] for part in seasons), 3)

            finale = f'{total_price_without_discount} {associationcriteria.monnaie}'
            finalewithdiscount = f'{total_price_all_parts} {associationcriteria.monnaie}'

            reservation_groube_finale.price = Decimal(total_price_all_parts)
            reservation_groube_finale.save()


            if total_price_all_parts != 0:
                facture = FactureFinale(
                reservation_code = reservation_groube_finale.id ,
                code_assi=reservation_groube_finale.code_assi,
                nom_assi = reservation_groube_finale.nom_assi,
                date_reservation=reservation_groube_finale.date_reservation,
                date_arrivee=reservation_groube_finale.date_arrivee,
                date_depart=reservation_groube_finale.date_depart,
                pension=reservation_groube_finale.pension,
                categorie=reservation_groube_finale.categorie,
                nbr_personne=reservation_groube_finale.nbr_personne,
                discounts=discount,
                discounts_detail=dis_detail,
                tarif = pu ,
                price_without_discount=finale,
                final_price_with_discount=finalewithdiscount,
            )
                facture.save()

    today = date.today()
    is_contract_expired = associationcriteria.fin_contrat < today if associationcriteria else False

    advertisement = None
    if is_contract_expired:
        advertisement = "Ceci est un message d'advertisement pour un contrat expiré."

    return render(request, 'reservation_details.html', {
        'reservation_groube_finale': reservation_groube_finale,
        'associationcriteria': associationcriteria,
        'seasons': seasons,
        'total_price_all_parts': total_price_all_parts,
        'facture': facture,
        'advertisement': advertisement,
    })



@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def create_association_criteria(request, association_code):
    association = get_object_or_404(Association, code=association_code)

    if request.method == 'POST':
        form = AssociationCriteriaForm(request.POST)
        if form.is_valid():
            association_criteria = form.save(commit=False)
            association_criteria.association = association
            association_criteria.save()
            return redirect('create_seasons_for_association_criteria', association_criteria_id=association_criteria.pk)
    else:
        form = AssociationCriteriaForm()

    return render(request, 'create_association_criteria.html', {'form': form , 'association':association})




@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def create_seasons_for_association_criteria(request, association_criteria_id):
    association_criteria = get_object_or_404(AssociationCriteria, id=association_criteria_id)
    error_message = None

    if request.method == 'POST':
        form = SeasonForm(request.POST)
        if form.is_valid():
            season = form.save(commit=False)
            season.association_criteria = association_criteria

            # Check if end_date is after fin_contrat
            if season.end_date > association_criteria.fin_contrat:
                form.add_error('end_date', 'Out of limite le contrat est expiré')
            else:
                # Check for overlapping seasons
                overlapping_seasons = Season.objects.filter(
                    association_criteria=association_criteria,
                    start_date__lte=season.end_date,
                    end_date__gte=season.start_date
                )
                if overlapping_seasons.exists():
                    form.add_error('start_date', 'A season with the same duration already exists.')
                    form.add_error('end_date', 'A season with the same duration already exists.')
                else:
                    season.save()
                    return redirect('create_season_categorie', season_id=season.id)  # Redirect to fill SeasonCategorie form
    else:
        form = SeasonForm()

    return render(request, 'create_seasons_for_association_criteria.html', {'form': form, 'error_message': error_message})




@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def create_season_categorie(request, season_id):
    season = get_object_or_404(Season, id=season_id)

    try:
        categorie = SeasonCategorie.objects.filter(season=season_id)
        print(categorie)
    except (SeasonCategorie.DoesNotExist):
        pass

    if request.method == 'POST':
        form = SeasonCategorieForm(request.POST)
        if form.is_valid():
            cat = form.cleaned_data['cat']
            existing_categories = SeasonCategorie.objects.filter(season=season, cat=cat)

            if existing_categories.exists():
                form.add_error('cat', f'Cette Season avec la catégorie {cat} existe déjà pour cette saison.')

            else:
                season_categorie = form.save(commit=False)
                season_categorie.season = season
                season_categorie.save()

                if 'save_season_categorie' in request.POST:
                    return redirect('create_seasons_for_association_criteria', association_criteria_id=season.association_criteria.id)
                elif 'save_and_add_another' in request.POST:
                    return redirect('create_season_categorie', season_id=season.id)
                else:
                    return redirect('association_criteria_detail' , association_id=season.association_criteria.association.code)
    else:
        form = SeasonCategorieForm()

    return render(request, 'create_season_categorie.html', {'form': form , 'categorie':categorie})



@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def association_criteria_list(request):
    search_query = request.GET.get('search')
    associations_with_criteria = Association.objects.filter(associationcriteria__isnull=False).distinct()
    associations_without_criteria = Association.objects.exclude(associationcriteria__isnull=False).distinct()
    if search_query:
        associations_with_criteria = associations_with_criteria.filter(
            Q(code__icontains=search_query) | Q(nom__icontains=search_query)
        )

    if search_query:
        associations_without_criteria = associations_without_criteria.filter(
            Q(code__icontains=search_query) | Q(nom__icontains=search_query)
        )

    associations_info = []
    for association in associations_with_criteria:
        criteria = AssociationCriteria.objects.get(association=association)
        seasons = Season.objects.filter(association_criteria=criteria)

        associations_info.append({
            'association': association,
            'criteria': criteria,
            'seasons': seasons,
        })
    today = timezone.now().date()

    return render(request, 'association_criteria_list.html', {
        'associations_with_criteria': associations_with_criteria,
        'associations_without_criteria': associations_without_criteria,
        'associations_info': associations_info,
        'today': today,
    })
@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def copy_ass_criteria(request, association_criteria_id, target_association_code):
    source_criteria = get_object_or_404(AssociationCriteria, id=association_criteria_id)
    source_seasons = Season.objects.filter(association_criteria=source_criteria)

    target_association = get_object_or_404(Association, code=target_association_code)

    # Create new association criteria for the target association
    new_criteria = AssociationCriteria.objects.create(
        association=target_association,
        debut_contart=source_criteria.debut_contart,
        fin_contrat=source_criteria.fin_contrat,
        monnaie=source_criteria.monnaie,
    )

    new=[]
    for original_season in source_seasons:
        new_season=Season.objects.create(
                association_criteria=new_criteria,
                name_season=original_season.name_season,
                start_date=original_season.start_date,
                end_date=original_season.end_date,
                duration_discount=original_season.duration_discount,
                duration_threshold=original_season.duration_threshold,
                earlybooking_discount=original_season.earlybooking_discount,
                earlybooking_threshold=original_season.earlybooking_threshold,
                mineur_discount=original_season.mineur_discount,
                mineur_threshold=original_season.mineur_threshold,
                mineur2_discount=original_season.mineur2_discount,
                mineur2_threshold=original_season.mineur2_threshold,
                paxnum3_discount=original_season.paxnum3_discount,
                paxnum3_threshold=original_season.paxnum3_threshold,
            )

        for original_categorie in original_season.categories.all():
            SeasonCategorie.objects.create(
                season=new_season,
                cat=original_categorie.cat,
                demipension_price=original_categorie.demipension_price,
                pensioncomplte_price=original_categorie.pensioncomplte_price,
                log_price=original_categorie.log_price,
                lpd_price=original_categorie.lpd_price,
            )



    # Redirect to a success page or view

    return redirect('association_criteria_detail', association_id = target_association.code)
@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def copy_criteria_interface(request):
    source_association_criteria = AssociationCriteria.objects.all()
    associations_without_criteria = Association.objects.filter(associationcriteria__isnull=True)

    if request.method == 'POST':
        source_association_code = request.POST.get('source_criteria')
        target_association_code = request.POST.get('target_association')

        if source_association_code and target_association_code:
            return redirect('copy_ass_criteria', source_association_code, target_association_code)

    return render(request, 'copy_criteria_interface.html', {
        'source_association_criteria': source_association_criteria,
        'associations_without_criteria': associations_without_criteria,
    })
@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def association_criteria_detail(request, association_id):
    association_criteria = get_object_or_404(AssociationCriteria, association_id=association_id)
    seasons = Season.objects.filter(association_criteria=association_criteria)
    season_categories = SeasonCategorie.objects.filter(season__in=seasons)

    return render(request, 'association_criteria_detail.html', {
        'criteria': association_criteria,
        'seasons': seasons,
        'season_categories':season_categories,
    })
@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def edit_association_criteria(request, association_id):
    association_criteria = get_object_or_404(AssociationCriteria, association_id=association_id)

    if request.method == 'POST':
        form = AssociationCriteriaForm(request.POST, instance=association_criteria)
        if form.is_valid():
            form.save()
            return redirect('association_criteria_detail', association_id=association_id)
    else:
        form = AssociationCriteriaForm(instance=association_criteria)

    return render(request, 'edit_association_criteria.html', {'criteria': association_criteria, 'form': form})
@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def edit_season(request, season_id):
    season = get_object_or_404(Season, id=season_id)

    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            form.save()
            return redirect('association_criteria_detail', association_id=season.association_criteria.association.code)
    else:
        form = SeasonForm(instance=season)

    return render(request, 'edit_season.html', {'season': season, 'form': form})

@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def delete_association_criteria(request, association_criteria_id):
    association_criteria = get_object_or_404(AssociationCriteria, association_id=association_criteria_id)
    if not association_criteria.association.code=='111111':
        if request.method == 'POST':
            seasons = Season.objects.filter(association_criteria=association_criteria)
            for season in seasons:
                season.delete()
            association_criteria.delete()

            return redirect('association_criteria_list')
    else:
        return redirect('association_criteria_list')

    return render(request, 'delete_association_criteria.html', {'criteria': association_criteria})
@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def delete_season_categorie(request, season_categorie_id):
    category = get_object_or_404(SeasonCategorie, id=season_categorie_id)


    if request.method == 'POST':
        category.delete()
        return redirect('association_criteria_detail', association_id=category.season.association_criteria.association_id)

    return render(request, 'delete_season_categorie.html', {'category': category})
@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def delete_season(request, season_id):
    season = get_object_or_404(Season, id=season_id)


    if request.method == 'POST':
        season.delete()
        return redirect('association_criteria_detail', association_id=season.association_criteria.association_id)

    return render(request, 'delete_season.html', {'season': season})

@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def update_season_categorie(request, season_categorie_id):
    season_categorie = get_object_or_404(SeasonCategorie, id=season_categorie_id)

    if request.method == 'POST':
        form = SeasonCategorieForm(request.POST, instance=season_categorie)
        if form.is_valid():
            form.save()
            return redirect('association_criteria_detail' , association_id = season_categorie.season.association_criteria.association.code)  # Redirect to a suitable page after updating
    else:
        form = SeasonCategorieForm(instance=season_categorie)

    return render(request, 'update_season_categorie.html', {'form': form, 'season_categorie': season_categorie})


@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def create_or_edit_room(request, chambre_id=None):
    chambre = None

    if chambre_id:
        chambre = get_object_or_404(Chambre, pk=chambre_id)

    if request.method == 'POST':
        form = ChambreForm(request.POST, instance=chambre)
        if form.is_valid():
            form.save()
            return redirect('room_list')
    else:
        form = ChambreForm(instance=chambre)

    return render(request, 'create_edit_room.html', {'form': form})

@login_required
def room_list(request):
    room_id = request.GET.get('room_id')
    if room_id:
        # If a room_id is provided, filter the rooms by that ID
        rooms = Chambre.objects.filter(chambre_id__icontains=room_id)
    else:
        # If no room_id is provided, show all rooms
        rooms = Chambre.objects.all()

    return render(request, 'room_list.html', {'rooms': rooms})

@login_required
def facture(request):
    reservations = ReservationGroubeFinale.objects.all()
    reservation = Reservation.objects.all()

    id_search = request.GET.get('id')
    code_assi_search = request.GET.get('code_assi')
    nom_assi_search = request.GET.get('nom_assi')
    date_reservation_search = request.GET.get('date_reservation')
    date_arrivee_search = request.GET.get('date_arrivee')
    date_depart_search = request.GET.get('date_depart')

    if id_search:
        reservations = reservations.filter(id__icontains=id_search)
        reservation = reservation.filter(id__icontains=id_search)
    if code_assi_search:
        reservations = reservations.filter(code_assi__icontains=code_assi_search)
        reservation = reservation.filter(clients__codeclient__icontains=code_assi_search)

    if nom_assi_search:
        reservations = reservations.filter(nom_assi__icontains=nom_assi_search)
        reservation = reservation.filter(clients__nomclient__icontains=nom_assi_search)

    if date_reservation_search:
        date_reservation = parse_date(date_reservation_search)
        reservations = reservations.filter(date_reservation=date_reservation)
    if date_arrivee_search and date_depart_search:
        date_arrivee = parse_date(date_arrivee_search)
        date_depart = parse_date(date_depart_search)
        reservations = reservations.filter(date_arrivee__lte=date_depart, date_depart__gte=date_arrivee)
        reservation = reservation.filter(date_arriv__lte=date_depart, date_sortie__gte=date_arrivee)

    return render(request,'facturation.html',{'reservations':reservations,'reservation':reservation})

@login_required
def effectif(request):
    return render(request,'effectif.html')

@login_required
def reservations_for_day(request):
    if request.method == 'POST':
        chosen_date = request.POST.get('chosen_date')  # Assuming you have a form field with the chosen date
        reservations = ReservationGroubeFinale.objects.filter(date_arrivee__lte=chosen_date, date_depart__gte=chosen_date)
        reservationsindiv = Reservation.objects.filter(date_arriv__lte=chosen_date, date_sortie__gte=chosen_date)

        CombinedReservation.objects.filter(chosen_date=chosen_date).delete()
        combined_reservation = CombinedReservation(chosen_date=chosen_date)
        combined_reservation.save()
        combined_reservation.reservation.add(*reservationsindiv)
        combined_reservation.reservation_group.add(*reservations)

        return redirect('combined_reservation_detail', pk=combined_reservation.pk)

    return render(request, 'choose_date.html')

@login_required
def combined_reservation_detail(request, pk):
    combined_reservation = get_object_or_404(CombinedReservation, pk=pk)
    reservationn = []
    pension = []
    categorie = []
    paxarrive = 0
    chamrearrive = 0
    for reservation_group in combined_reservation.reservation_group.all():
        code_assi = reservation_group.code_assi


        # Check if a row with the same code_assi already exists in reservationn
        existing_row = next((item for item in reservationn if item['code'] == code_assi), None)

        if existing_row:
            # Update the existing row
            existing_row['pax'] += reservation_group.occupant.count()
            existing_row['chb'] += reservation_group.chambre.count()
            existing_row['nbrreseration'] += 1
            existing_row['prveilpax'] += reservation_group.occupant.count()
            existing_row['prejour'] += reservation_group.occupant.count()
            existing_row['prveilchamp'] += reservation_group.chambre.count()
            existing_row['prejourcham'] += reservation_group.chambre.count()

            if reservation_group.date_arrivee == combined_reservation.chosen_date:
                existing_row['paxarrive'] += reservation_group.occupant.count()
                existing_row['chamrearrive'] += reservation_group.chambre.count()
                existing_row['prveilpax'] -= reservation_group.occupant.count()
                existing_row['prveilchamp'] -= reservation_group.chambre.count()

            if reservation_group.date_depart == combined_reservation.chosen_date:
                existing_row['paxdepart'] += reservation_group.occupant.count()
                existing_row['chamredepart'] += reservation_group.chambre.count()
                existing_row['prejour'] -= reservation_group.occupant.count()
                existing_row['prejourcham'] -= reservation_group.chambre.count()

        else:
            # Add a new row
            paxarrive = reservation_group.occupant.count() if reservation_group.date_arrivee == combined_reservation.chosen_date else 0
            chamrearrive = reservation_group.chambre.count() if reservation_group.date_arrivee == combined_reservation.chosen_date else 0
            paxdepart = reservation_group.occupant.count() if reservation_group.date_depart == combined_reservation.chosen_date else 0
            chamredepart = reservation_group.chambre.count() if reservation_group.date_depart == combined_reservation.chosen_date else 0

            reservationn.append({
                'code': code_assi,
                'nom': reservation_group.nom_assi,
                'nbrreseration' : 1 ,
                'chosen_date' : combined_reservation.chosen_date ,
                'prveilpax' : reservation_group.occupant.count() - paxarrive  ,
                'prveilchamp' : reservation_group.chambre.count() - chamrearrive ,
                'pax': reservation_group.occupant.count(),
                'chb': reservation_group.chambre.count(),
                'prejour' : reservation_group.occupant.count() - paxdepart ,
                'prejourcham' : reservation_group.chambre.count() - chamredepart ,
                'paxarrive': paxarrive,
                'chamrearrive': chamrearrive,
                'paxdepart': paxdepart,
                'chamredepart': chamredepart,
            })



    for reservation in combined_reservation.reservation.all():
        existing_row = next((item for item in reservationn if item['code'] == 1111), None)
        if existing_row :
            existing_row['pax'] += reservation.paxes.count()
            existing_row['chb'] += reservation.chambre.count()
            existing_row['nbrreseration'] += 1
            existing_row['prveilpax'] += reservation.paxes.count()
            existing_row['prejour'] += reservation.paxes.count()
            existing_row['prveilchamp'] += reservation.chambre.count()
            existing_row['prejourcham'] += reservation.chambre.count()

            if reservation.date_arriv == combined_reservation.chosen_date:
                existing_row['paxarrive'] += reservation.paxes.count()
                existing_row['chamrearrive'] += reservation.chambre.count()
                existing_row['prveilpax'] -= reservation.paxes.count()
                existing_row['prveilchamp'] -= reservation.chambre.count()

            if reservation.date_sortie == combined_reservation.chosen_date:
                existing_row['paxdepart'] += reservation.paxes.count()
                existing_row['chamredepart'] += reservation.chambre.count()
                existing_row['prejour'] -= reservation.paxes.count()
                existing_row['prejourcham'] -= reservation.chambre.count()
        else:
            if reservation.date_arriv == combined_reservation.chosen_date :
                paxarrive = reservation.paxes.count()
                chamrearrive = reservation.chambre.count()
            else:
                paxarrive = 0
                chamrearrive = 0

            if reservation.date_sortie == combined_reservation.chosen_date :

                paxdepart = reservation.paxes.count()
                chamredepart = reservation.chambre.count()
            else:
                paxdepart = 0
                chamredepart = 0
            reservationn.append({'code':1111 ,
                             'nom': 'Clients individuels',
                             'nbrreseration' : 1 ,
                             'chosen_date' : combined_reservation.chosen_date ,
                             'prveilpax' : reservation.paxes.count() - paxarrive  ,
                             'prveilchamp' : reservation.chambre.count() - chamrearrive ,
                             'pax' : reservation.paxes.count() ,
                             'chb' : reservation.chambre.count() ,
                             'prejour' : reservation.paxes.count() - paxdepart ,
                             'prejourcham' : reservation.chambre.count() - chamredepart ,
                             'paxarrive' : paxarrive ,
                             'chamrearrive' : chamrearrive ,
                             'paxdepart' : paxdepart ,
                             'chamredepart' : chamredepart ,

                             })


    context = {'combined_reservation': combined_reservation , 'reservationn':reservationn}
    return render(request, 'combined_reservation_detail.html', context)

@login_required
def rooms(request):
    return render(request,'rooms.html')

@login_required
@user_passes_test(is_coo_or_developer, login_url='permission_denied')
def cont(request):
    return render(request,'cont.html')

@login_required
def index(request):
    return render(request,'index.html')

def custom_404(request, exception):
    return render(request, '404.html', status=404)
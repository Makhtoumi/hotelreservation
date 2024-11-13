from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from Menugenerale import views
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    path('create-user/', views.create_user, name='create_user'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('',views.login_view,name='login'),
    path('menu', login_required(views.index), name='index'),
    path('reservation/create/', login_required(views.create_reservation), name='create_reservation'),
    path('client/createc', login_required(views.create_client), name='create_client'),
    path('client/', login_required(views.clientview), name='clientview'),
    path('reservation/', login_required(views.reservationview), name='reservationview'),
    path('client/search', login_required(views.search_client), name='search_client'),
    path('client/update', login_required(views.update_client), name='update_client'),
    path('client/edit/<str:client_code>/', login_required(views.edit_client), name='edit_client'),
    path('reservation/room', login_required(views.availblee_room), name='availble_room'),
    path('dashboard',login_required(views.dashboard),name='dashboard'),
    path('reservation/select',login_required(views.selectclienttoreserv),name='selectclienttoreserv'),
    path('generate_pdf/<int:facture_id>/<int:reservation_id>/', views.generate_pdf, name='generate_pdf'),
    path('create/', views.create_association, name='create_association'),
    path('list/', views.association_list, name='association_list'),
    path('listclient/', views.association_listtoreserve, name='association_listtoreserve'),
    path('association/<str:association_code>/delete/', views.delete_association, name='delete_association'),
    path('association/<str:association_code>/update/', views.update_association, name='update_association'),
    path('association/<str:association_code>/create_reservation/', views.create_reservation_for_association, name='create_reservation_for_association'),
    path('reservation/<int:reservation_id>/add_occupant/', views.add_occupant, name='add_occupant'),
    path('reservation/<int:reservation_id>/assign_rooms/', views.assign_rooms_to_occupants, name='assign_rooms_to_occupants'),
    path('reservation/<int:reservation_id>/detail/', views.reservation_detail, name='reservation_detail'),
    path('create_association_criteria/<str:association_code>/', views.create_association_criteria, name='create_association_criteria'),
    path('create_room/', views.create_or_edit_room, name='create_room'),
    path('edit_room/<str:chambre_id>/', views.create_or_edit_room, name='edit_room'),
    path('room_list/', views.room_list, name='room_list'),
    path('rooms',views.rooms,name='rooms'),
    path('permission_denied/', views.permission_denied_view, name='permission_denied'),
    path('association/<str:association_code>/conulter/', views.cons_association, name='cons_association'),
    path('create_seasons_for_association_criteria/<int:association_criteria_id>/', views.create_seasons_for_association_criteria, name='create_seasons_for_association_criteria'),
    path('association_criteria_list/', views.association_criteria_list, name='association_criteria_list'),
    path('generate_pdff/<int:facture_id>/<int:reservation_id>/', views.generate_pdff, name='generate_pdff'),
    path('pdf-list/', views.pdf_list, name='pdf_list'),
    path('pdf_view/<str:pdf_file_name>/', views.view_pdf, name='view_pdf'),
    path('copy_ass_criteria/<int:association_criteria_id>/<str:target_association_code>/', views.copy_ass_criteria, name='copy_ass_criteria'),
    path('copy_criteria_interface/', views.copy_criteria_interface, name='copy_criteria_interface'),
    path('cont/', views.cont, name='cont'),
    path('association/<int:association_id>/', views.association_criteria_detail, name='association_criteria_detail'),
    path('association/<int:association_id>/edit_criteria/', views.edit_association_criteria, name='edit_association_criteria'),
    path('season/<int:season_id>/edit/', views.edit_season, name='edit_season'),
    path('association_criteria/<int:association_criteria_id>/delete/', views.delete_association_criteria, name='delete_association_criteria'),
    path('create_season_categorie/<int:season_id>/', views.create_season_categorie, name='create_season_categorie'),
    path('update_season_categorie/<int:season_categorie_id>/', views.update_season_categorie, name='update_season_categorie'),
    path('reservation-list/', views.reservation_list, name='reservation_list'),
    path('occupant/<int:occupant_id>/', views.occupant_detail, name='occupant_detail'),
    path('reservation_management/', views.reservation_management, name='reservation_management'),
    path('update_reservation/<int:reservation_id>/', views.update_reservation, name='update_reservation'),
    path('update_occupant/<int:occupant_id>/', views.update_occupant, name='update_occupant'),
    path('generate_pdfff/<int:association_id>/', views.generate_pdfff, name='generate_pdfff'),
    path('room/roomAssignment',views.roomAssignment,name='roomAssignment'),
    path('enter_paxes/<int:reservation_id>/', views.enter_paxes, name='enter_paxes'),
    path('reservation/<int:reservation_id>/assign-rooms/', views.assign_rooms, name='assign_rooms'),
    path('reservation/info/<int:reservation_id>/', views.reservation_info, name='reservation_info'),
    path('delete_season/<int:season_id>/', views.delete_season, name='delete_season'),
    path('delete_season_categorie/<int:season_categorie_id>/', views.delete_season_categorie, name='delete_season_categorie'),
    path('edit_reservation/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('reservation_list_2/', views.reservation_list_2, name='reservation_list_2'),
    path('update_pax/<int:pax_id>/', views.update_pax, name='update_pax'),
    path('taxes/',views.edit_taxes,name='edit_taxes'),
    path('facture/',views.facture,name='facture'),
    path('Information/',views.edit_info,name='edit_info'),
    path('parameter',views.parameter,name='parameter'),
    path('clienttype',views.assoctiontype,name='assoctiontype'),
    path('delete_client_type/<int:type_id>/', views.delete_association_type, name='delete_association_type'),
    path('delete_occupant/<int:type_id>/', views.delete_occupant, name='delete_occupant'),
    path('delete_pax/<int:type_id>/<int:reservation_id>', views.delete_pax, name='delete_pax'),
    path('effectif/',views.effectif,name='effectif'),
    path('reservations_for_day/',views.reservations_for_day,name='reservations_for_day'),
    path('combined_reservation/<int:pk>/', views.combined_reservation_detail, name='combined_reservation_detail'),











] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



handler404 = 'Menugenerale.views.custom_404'


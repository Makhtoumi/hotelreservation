from django.core.management.base import BaseCommand
from random import choices
from Menugenerale.models import Chambre

class Command(BaseCommand):
    help = 'Create 100 rooms'

    def handle(self, *args, **kwargs):
        chambre_types = ['indiv', 'double', 'triple', 'quadruple']
        chambre_views = ['Vue picine', 'normal']

        for i in range(100, 350):
            chambre_type = choices(chambre_types, weights=[60, 20, 20, 0])[0]
            chambre_view = choices(chambre_views, weights=[20, 80])[0]
            chambre_id = f'{i:03d}'

            Chambre.objects.create(chambre_id=chambre_id, chambre_type=chambre_type, chambre_Vue=chambre_view)

            self.stdout.write(self.style.SUCCESS(f'Successfully created room with ID {chambre_id}'))

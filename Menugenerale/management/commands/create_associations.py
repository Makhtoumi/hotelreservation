from django.core.management.base import BaseCommand
from random import choice, randint
from faker import Faker  
from Menugenerale.models import Association

class Command(BaseCommand):
    help = 'Create random associations'

    def handle(self, *args, **kwargs):
        fake = Faker()

        association_types = [Association.AGENCE_DE_VOYAGE, Association.ASSOCIATION, Association.PRIVEE]

        for i in range(100):
            code = str(randint(100000, 999999))
            name = fake.company()
            assoc_type = choice(association_types)
            address = fake.address()

            Association.objects.create(code=code, nom=name, type=assoc_type, adress=address)

            self.stdout.write(self.style.SUCCESS(f'Successfully created association: {name}'))


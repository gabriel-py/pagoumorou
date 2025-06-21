from django.core.management.base import BaseCommand
from decimal import Decimal
from pagoumorou.models import Destination, Property, Address, Room, RoomPrice, RoomPhoto, Feature, RoomFeature
from pagoumorou.constants import PeriodChoices
import random


class Command(BaseCommand):
    help = 'Popula o banco com quartos próximos à USP Leste que aceitam homens e possuem preço para 15 dias'

    def handle(self, *args, **options):
        # 1. Cria destination
        destination, _ = Destination.objects.get_or_create(
            name='USP Leste',
            country_id='BR',
            destination_type='NB',
            latitude=-23.4854987,
            longitude=-46.5005576
        )

        # 2. Cria endereço base
        base_address, _ = Address.objects.get_or_create(
            street='Rua Apaura',
            number='90',
            neighborhood='Vila Silvia',
            city='São Paulo',
            state='SP',
            zip_code='08010-000',
        )

        # 3. Cria propriedade
        property_obj, _ = Property.objects.get_or_create(
            name='Pensão USP Leste',
            type='BoardingHouse',
            rules='Proibido fumar; visitas até 22h.',
            address=base_address,
            destination=destination
        )

        # 4. Cria Features base
        feature_names = ['WiFi', 'Ar Condicionado', 'Geladeira', 'Escrivaninha', 'Banheiro Privativo']
        features = []
        for name in feature_names:
            feature, _ = Feature.objects.get_or_create(name=name)
            features.append(feature)

        # 5. Cria 10 quartos
        for i in range(1, 11):
            room = Room.objects.create(
                room_number=f"{100 + i}",
                capacity=random.choice([1, 2]),
                shared=random.choice([True, False]),
                property=property_obj,
                accept_men=True,
                accept_women=False
            )

            # 6. Preço para 15 dias (biweek)
            RoomPrice.objects.create(
                room=room,
                period=PeriodChoices.BIWEEK,
                price=Decimal(random.randint(400, 800))
            )

            # 7. Foto de exemplo
            RoomPhoto.objects.create(
                room=room,
                url='https://photos.webquarto.com.br/property_ads/thumb/2021-05/47830_SxLBh4OQR9ruB8RV.jpg'
            )

            # 8. Associa de 2 a 4 features aleatórias
            room_features = random.sample(features, k=random.randint(2, 4))
            for feature in room_features:
                RoomFeature.objects.create(room=room, feature=feature)

        self.stdout.write(self.style.SUCCESS("✅ Quartos com features populados com sucesso!"))

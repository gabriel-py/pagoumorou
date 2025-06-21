from typing import List
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

from pagoumorou.constants import PERIOD_VERBOSE, PeriodChoices
from pagoumorou.models import Room, RoomPrice, RoomPhoto, RoomFeature
import json


def haversine(lat1: float, lon1: float, lat2: float, lon2: float):
    """Calcula a distância em km entre dois pontos (lat/lon)"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 6371 * 2 * asin(sqrt(a))


class SearchAPI(APIView):
    def post(self, request):
        data = json.loads(request.body)

        lat = data.get('lat')
        lon = data.get('lon')
        location = data.get('location')
        gender = data.get('gender')
        move_date = data.get('moveDate')
        stay_duration = int(data.get('stayDuration'))

        # 1. Mapeia duração para período
        period_map = {
            7: PeriodChoices.WEEK,
            15: PeriodChoices.BIWEEK,
            30: PeriodChoices.MONTH,
            180: PeriodChoices.SEMESTER,
            365: PeriodChoices.YEAR,
        }
        period = period_map.get(stay_duration)
        if not period:
            return Response({"error": "Invalid stayDuration"}, status=400)

        # 2. Busca quartos com precificação para o período
        rooms = Room.objects.filter(
            roomprice__period=period
        ).select_related('property__address', 'property__destination')

        # 3. Filtro de gênero
        if gender == "male":
            rooms = rooms.filter(accept_men=True)
        elif gender == "female":
            rooms = rooms.filter(accept_women=True)

        # 4. Filtro de disponibilidade (sem aluguel na data)
        if move_date:
            move_date_obj = datetime.strptime(move_date, "%Y-%m-%d").date()
            rooms = rooms.exclude(
                rental__start_date__lte=move_date_obj,
                rental__end_date__gte=move_date_obj
            )

        # 5. Filtro por distância (raio de 10km)
        RADIUS_KM = 10
        matching_rooms = []
        for room in rooms:
            addr = room.property.address
            destination = room.property.destination
            if not destination or not destination.latitude or not destination.longitude:
                continue

            distance = haversine(lat, lon, float(destination.latitude), float(destination.longitude))
            if distance > RADIUS_KM:
                continue

            # Preço
            room_price = RoomPrice.objects.filter(room=room, period=period).first()
            price = float(room_price.price) if room_price else 0.0

            # Fotos
            photos = list(RoomPhoto.objects.filter(room=room).values_list('url', flat=True))

            # Features
            features = list(
                RoomFeature.objects.filter(room=room)
                .select_related('feature')
                .values_list('feature__name', flat=True)
            )

            matching_rooms.append({
                "room_id": room.id,
                "room_number": room.room_number,
                "property": room.property.name,
                "address": {
                    "street": addr.street if addr else None,
                    "number": addr.number if addr else None,
                    "neighborhood": addr.neighborhood if addr else None,
                    "city": addr.city if addr else None,
                    "state": addr.state if addr else None,
                },
                "destination": {
                    "name": destination.name,
                    "lat": destination.latitude,
                    "lon": destination.longitude
                },
                "price": price,
                "period": PERIOD_VERBOSE.get(period, period),
                "accept_men": room.accept_men,
                "accept_women": room.accept_women,
                "shared": room.shared,
                "photos": photos,
                "features": features,
            })

        return Response({"results": matching_rooms, "success": True})

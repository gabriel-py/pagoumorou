from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt

from pagoumorou.constants import PERIOD_VERBOSE, PeriodChoices, StatusChoices
from pagoumorou.models import Proposal, Room, RoomPrice, RoomPhoto, RoomFeature
import json

from user.models import Profile


class SearchAPI(APIView):
    def post(self, request):
        data = json.loads(request.body)

        destinationId = int(data.get('destinationId'))
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
            roomprice__period=period,
            property__destination_id=destinationId
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

        matching_rooms = []
        for room in rooms:
            addr = room.property.address
            destination = room.property.destination

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


class RoomAPI(APIView):
    def get(self, request, room_id):
        try:
            room = Room.objects.select_related('property__address', 'property__destination').get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        # Endereço e destino
        addr = room.property.address
        destination = room.property.destination

        # Preços disponíveis
        prices = RoomPrice.objects.filter(room=room)
        price_list = [
            {
                "period": PERIOD_VERBOSE.get(price.period, price.period),
                "raw_period": price.period,
                "price": float(price.price)
            }
            for price in prices
        ]

        # Fotos
        photos = list(RoomPhoto.objects.filter(room=room).values_list('url', flat=True))

        # Features
        features = list(
            RoomFeature.objects.filter(room=room)
            .select_related('feature')
            .values_list('feature__name', flat=True)
        )

        return Response({
            "success": True,
            "data": {
                "room_id": room.id,
                "room_number": room.room_number,
                "property": room.property.name,
                "property_description": room.property.description,
                "property_rules": room.property.rules,
                "description": room.description,
                "rules": room.rules,
                "available_now": room.available_now,
                "available_from": room.available_from,
                "address": {
                    "street": addr.street if addr else None,
                    "number": addr.number if addr else None,
                    "neighborhood": addr.neighborhood if addr else None,
                    "city": addr.city if addr else None,
                    "state": addr.state if addr else None,
                },
                "destination": {
                    "name": destination.name if destination else None,
                    "lat": destination.latitude if destination else None,
                    "lon": destination.longitude if destination else None,
                },
                "prices": price_list,
                "accept_men": room.accept_men,
                "accept_women": room.accept_women,
                "shared": room.shared,
                "photos": photos,
                "features": features,
            }
        })


class ProposalAPI(APIView):
    def get(self, request, proposal_id=None):
        if not proposal_id:
            return Response({"error": "Proposal ID is required"}, status=400)

        try:
            proposal = Proposal.objects.select_related('profile', 'room__property__address').get(id=proposal_id)
        except Proposal.DoesNotExist:
            return Response({"error": "Proposal not found"}, status=404)

        data = {
            "proposal_id": proposal.id,
            "full_name": proposal.profile.name,
            "email": proposal.profile.user.email,
            "cpf": proposal.profile.cpf,
            "birth_date": proposal.profile.birth_date,
            "gender": proposal.profile.gender,
            "room_id": proposal.room.id,
            "room_number": proposal.room.room_number,
            "property": proposal.room.property.name,
            "proposed_price": float(proposal.proposed_price),
            "period": proposal.period,
            "move_in_date": proposal.move_in_date,
            "move_out_date": proposal.move_out_date,
            "message": proposal.message,
            "status": proposal.status,
            "created_at": proposal.created_at,
        }

        return Response({"success": True, "data": data}, status=200)

    def post(self, request):
        data = json.loads(request.body)
        room_id = data.get("roomId")

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        period_int = int(data.get("stayInPeriod"))
        period_map = {
            7: PeriodChoices.WEEK,
            15: PeriodChoices.BIWEEK,
            30: PeriodChoices.MONTH,
            180: PeriodChoices.SEMESTER,
            365: PeriodChoices.YEAR,
        }
        period = period_map.get(period_int)
        if not period:
            return Response({"error": "Invalid stayInPeriod"}, status=400)

        try:
            email = data.get("email")
            full_name = data.get("fullName")
            cpf = data.get("cpf")
            birth_date = data.get("birthDate")
            gender = data.get("gender")

            user, _ = User.objects.get_or_create(
                username=email,
                defaults={"email": email, "first_name": full_name}
            )

            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "name": full_name,
                    "cpf": cpf,
                    "birth_date": birth_date,
                    "gender": gender,
                }
            )

            move_in_date = datetime.strptime(data.get("moveDate"), "%Y-%m-%d").date()
            move_out_date = move_in_date + timedelta(days=period_int)

            proposal = Proposal.objects.create(
                profile=profile,
                room=room,
                proposed_price=data.get("suggestedPrice"),
                period=period,
                move_in_date=move_in_date,
                move_out_date=move_out_date,
                message=data.get("message"),
                status=StatusChoices.PENDING,
            )

            return Response({
                "success": True,
                "proposal_id": proposal.id
            }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

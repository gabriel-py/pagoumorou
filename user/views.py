from datetime import date
from typing import Any
from django.db import transaction
from django.db.models import TextChoices
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from rest_framework.views import APIView
import json

from .models import Address, Profile


def validate_choice(value: str | None, choices_class: type[TextChoices], field_name: str) -> None:
    if value is not None and value not in choices_class.values:
        raise ValueError(f"Valor inválido para '{field_name}': {value}. Opções válidas: {', '.join(choices_class.values)}")


def create_address(data: Any) -> None | Address:
    if not data:
        return None

    return Address.objects.create(
        street=data["street"],
        number=data["number"],
        complement=data.get("complement"),
        neighborhood=data["neighborhood"],
        city=data["city"],
        state=data["state"],
        zip_code=data["zip_code"]
    )


def update_address(address: Address, data: Any) -> Address:
    address.street = data["street"]
    address.number = data["number"]
    address.complement = data.get("complement")
    address.neighborhood = data["neighborhood"]
    address.city = data["city"]
    address.state = data["state"]
    address.zip_code = data["zip_code"]
    address.save()

    return address


def validate_unique_user_fields(username: str, email: str, user_id: int | None) -> None:
    if User.objects.exclude(id=user_id).filter(username=username).exists():
        raise ValueError("Este nome de usuário já está em uso.")
    if User.objects.exclude(id=user_id).filter(email=email).exists():
        raise ValueError("Este e-mail já está em uso.")


class CreateUserView(APIView):
    @transaction.atomic
    def post(self, request):
        data = json.loads(request.body)

        validate_unique_user_fields(username=data["user"]["username"], email=data["user"]["email"], user_id=None)

        user: User = User.objects.create_user(
            username=data["user"]["username"],
            email=data["user"]["email"],
            password=data["user"]["password"]
        )

        user.set_password(data["user"]["password"])

        try:
            validate_choice(data.get("gender"), Profile.Gender, "gender")
            validate_choice(data["role"], Profile.Role, "role")
        except ValueError as ex:
            return JsonResponse({"success": False, "error": str(ex)}, status=400)

        birth_date: date | None = parse_date(data["birth_date"])
        if not birth_date:
            return JsonResponse({"success": False, "error": "Falha ao processar data de nascimento"}, status=400)

        profile: Profile = Profile.objects.create(
            user=user,
            name=data["name"],
            birth_date=birth_date,
            gender=data.get("gender"),
            role=data["role"]
        )

        address: None | Address = create_address(data.get("address"))
        if address:
            profile.address = address
            profile.save()

        return JsonResponse({"success": True, "data": profile.to_dict()}, status=201)


class UpdateUserView(APIView):
    @transaction.atomic
    def put(self, request, user_id):
        data = json.loads(request.body)

        user: User = get_object_or_404(User, id=user_id)

        try:
            profile: Profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return JsonResponse({"success": False, "error": f"Usuário não possui perfil associado"}, status=400)

        validate_unique_user_fields(
            username=data["user"]["username"],
            email=data["user"]["email"],
            user_id=user.id
        )

        user.username = data["user"]["username"]
        user.email = data["user"]["email"]

        if data["user"].get("password"):
            user.set_password(data["user"]["password"])

        user.save()

        address_data = data.get("address")
        if address_data:
            if profile.address:
                update_address(profile.address, address_data)
            else:
                profile.address = create_address(address_data)

        profile.name = data["name"]

        birth_date: date | None = parse_date(data["birth_date"])
        if not birth_date:
            return JsonResponse({"success": False, "error": "Falha ao processar data de nascimento"}, status=400)

        profile.birth_date = birth_date

        try:
            validate_choice(data.get("gender"), Profile.Gender, "gender")
            validate_choice(data["role"], Profile.Role, "role")
        except ValueError as ex:
            return JsonResponse({"success": False, "error": str(ex)}, status=400)

        profile.gender = data.get("gender")
        profile.role = data["role"]

        profile.save()

        return JsonResponse({"success": True, "data": profile.to_dict()}, status=200)

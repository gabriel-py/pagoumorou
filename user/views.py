from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from rest_framework.views import APIView
import json

from .models import Address, Profile


def create_address(data):
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


def update_address(address, data):
    address.street = data["street"]
    address.number = data["number"]
    address.complement = data.get("complement")
    address.neighborhood = data["neighborhood"]
    address.city = data["city"]
    address.state = data["state"]
    address.zip_code = data["zip_code"]
    address.save()
    return address


def validate_unique_user_fields(username, email, exclude_id=None):
    if User.objects.exclude(id=exclude_id).filter(username=username).exists():
        raise ValueError("Este nome de usuário já está em uso.")
    if User.objects.exclude(id=exclude_id).filter(email=email).exists():
        raise ValueError("Este e-mail já está em uso.")


class CreateUserView(APIView):
    @transaction.atomic
    def post(self, request):
        data = json.loads(request.body)

        try:
            validate_unique_user_fields(data["user"]["username"], data["user"]["email"])

            user = User.objects.create_user(
                username=data["user"]["username"],
                email=data["user"]["email"],
                password=data["user"]["password"]
            )

            address: None | Address = create_address(data.get("address"))

            profile: Profile = Profile.objects.create(
                user=user,
                name=data["name"],
                birth_date=parse_date(data["birth_date"]),
                gender=data.get("gender"),
                role=data["role"],
                address=address
            )

            return JsonResponse({"success": True, "user": profile.to_dict()}, status=201)

        except KeyError as e:
            return JsonResponse({"success": False, "error": f"Campo obrigatório faltando: {e}"}, status=400)
        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
        except IntegrityError as e:
            return JsonResponse({"success": False, "error": f"Erro de integridade no banco de dados: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class UpdateUserView(APIView):
    @transaction.atomic
    def put(self, request, user_id):
        data = json.loads(request.body)

        try:
            profile = get_object_or_404(Profile, id=user_id)
            user = profile.user

            validate_unique_user_fields(
                username=data["user"]["username"],
                email=data["user"]["email"],
                exclude_id=user.id
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
            profile.birth_date = parse_date(data["birth_date"])
            profile.gender = data.get("gender")
            profile.role = data["role"]
            profile.save()

            return JsonResponse({"success": True, "user": profile.to_dict()}, status=200)

        except KeyError as e:
            return JsonResponse({"success": False, "error": f"Campo obrigatório faltando: {e}"}, status=400)
        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
        except IntegrityError as e:
            return JsonResponse({"success": False, "error": f"Erro de integridade no banco de dados: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

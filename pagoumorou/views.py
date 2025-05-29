from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from rest_framework.views import APIView
import json

from .models import Address, CustomUser

class CreateUserView(APIView):
    @transaction.atomic
    def post(self, request):
        data = json.loads(request.body)

        try:
            user = User.objects.create_user(
                username=data["user"]["username"],
                email=data["user"]["email"],
                password=data["user"]["password"]
            )

            address_data = data.get("address")
            address = None
            if address_data:
                address = Address.objects.create(
                    street=address_data["street"],
                    number=address_data["number"],
                    complement=address_data.get("complement"),
                    neighborhood=address_data["neighborhood"],
                    city=address_data["city"],
                    state=address_data["state"],
                    zip_code=address_data["zip_code"]
                )

            custom_user = CustomUser.objects.create(
                user=user,
                name=data["name"],
                birth_date=parse_date(data["birth_date"]),
                gender=data.get("gender"),
                role=data["role"],
                address=address
            )

            return JsonResponse({"success": True, "user": custom_user.to_dict()}, status=201)

        except KeyError as e:
            return JsonResponse({"success": False, "error": f"Campo obrigatório faltando: {str(e)}"}, status=400)

        except IntegrityError as e:
            error_msg = str(e)

            if "auth_user_username_key" in error_msg:
                return JsonResponse({"success": False, "error": "Este nome de usuário já está em uso."}, status=400)
            if "auth_user_email_key" in error_msg:
                return JsonResponse({"success": False, "error": "Este e-mail já está em uso."}, status=400)

            return JsonResponse({"success": False, "error": f"Erro de integridade no banco de dados: {error_msg}"}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class UpdateUserView(APIView):
    @transaction.atomic
    def put(self, request, user_id):
        data = json.loads(request.body)

        try:
            custom_user = get_object_or_404(CustomUser, id=user_id)
            user = custom_user.user

            username = data["user"]["username"]
            email = data["user"]["email"]
            password = data["user"].get("password")

            if User.objects.exclude(id=user.id).filter(username=username).exists():
                return JsonResponse({"success": False, "error": "Este nome de usuário já está em uso."}, status=400)
            if User.objects.exclude(id=user.id).filter(email=email).exists():
                return JsonResponse({"success": False, "error": "Este e-mail já está em uso."}, status=400)

            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.save()

            address_data = data.get("address")
            if address_data:
                if custom_user.address:
                    address = custom_user.address
                    address.street = address_data["street"]
                    address.number = address_data["number"]
                    address.complement = address_data.get("complement")
                    address.neighborhood = address_data["neighborhood"]
                    address.city = address_data["city"]
                    address.state = address_data["state"]
                    address.zip_code = address_data["zip_code"]
                    address.save()
                else:
                    address = Address.objects.create(
                        street=address_data["street"],
                        number=address_data["number"],
                        complement=address_data.get("complement"),
                        neighborhood=address_data["neighborhood"],
                        city=address_data["city"],
                        state=address_data["state"],
                        zip_code=address_data["zip_code"]
                    )
                    custom_user.address = address

            custom_user.name = data["name"]
            custom_user.birth_date = parse_date(data["birth_date"])
            custom_user.gender = data.get("gender")
            custom_user.role = data["role"]
            custom_user.save()

            return JsonResponse({"success": True, "user": custom_user.to_dict()}, status=200)

        except KeyError as e:
            return JsonResponse({"success": False, "error": f"Campo obrigatório faltando: {str(e)}"}, status=400)

        except IntegrityError as e:
            return JsonResponse({"success": False, "error": f"Erro de integridade no banco de dados: {str(e)}"}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

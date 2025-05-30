from typing import Any
from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    complement = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city}/{self.state}"

    class Meta:
        db_table = "address"


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'MALE'
        FEMALE = 'FEMALE'

    class Role(models.TextChoices):
        CLIENT = 'CLIENT'
        MANAGER = 'MANAGER'

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, blank=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "birth_date": str(self.birth_date),
            "gender": self.gender,
            "role": self.role,
            "user": {
                "id": self.user.id if self.user else None,
                "username": self.user.username if self.user else None,
                "email": self.user.email if self.user else None,
            },
            "address": {
                "id": self.address.id,
                "street": self.address.street,
                "number": self.address.number,
                "complement": self.address.complement,
                "neighborhood": self.address.neighborhood,
                "city": self.address.city,
                "state": self.address.state,
                "zip_code": self.address.zip_code
            } if self.address else None
        }

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "profile"


import uuid
from django.db import models

class User(models.Model):
    class Gender(models.TextChoices):
        MALE = 'Male'
        FEMALE = 'Female'
        OTHER = 'Other'

    class Role(models.TextChoices):
        CLIENT = 'Client'
        MANAGER = 'Manager'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, choices=Role.choices)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Destination(models.Model):
    class DestinationType(models.TextChoices):
        COUNTRY = 'CT'
        STATE = 'ST'
        CITY = 'CI'
        NEIGHBORHOOD = 'NB'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    destination_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    country_id = models.CharField(max_length=2)
    destination_type = models.CharField(max_length=2, choices=DestinationType.choices)
    parent_destination_id = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_destination_type_display()})"

class Property(models.Model):
    class PropertyType(models.TextChoices):
        REPUBLIC = 'Republic'
        BOARDING_HOUSE = 'BoardingHouse'
        HOTEL = 'Hotel'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=PropertyType.choices)
    rules = models.TextField()
    address = models.TextField()
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class PropertyManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name} - {self.property.name}"

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_number = models.CharField(max_length=50)
    capacity = models.IntegerField()
    shared = models.BooleanField(default=False)
    weekly_price = models.DecimalField(max_digits=10, decimal_places=2)
    biweekly_price = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    def __str__(self):
        return f"Room {self.room_number} - {self.property.name}"

class Feature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class RoomFeature(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.room} - {self.feature.name}"

class RoomPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo of {self.room.room_number}"

class Proposal(models.Model):
    class PeriodChoices(models.TextChoices):
        WEEK = 'Week'
        BIWEEK = 'Biweek'
        MONTH = 'Month'

    class StatusChoices(models.TextChoices):
        PENDING = 'Pending'
        ACCEPTED = 'Accepted'
        REJECTED = 'Rejected'
        EXPIRED = 'Expired'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=10, choices=PeriodChoices.choices)
    move_in_date = models.DateField()
    move_out_date = models.DateField()
    message = models.TextField()
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_proposals')

    def __str__(self):
        return f"Proposal by {self.user.name} for {self.room.room_number}"

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} stays in {self.room.room_number}"

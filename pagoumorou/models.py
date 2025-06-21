
from django.db import models
from pagoumorou.constants import PeriodChoices, StatusChoices
from user.models import Address, Profile

class Destination(models.Model):
    class DestinationType(models.TextChoices):
        COUNTRY = 'CT'
        STATE = 'ST'
        CITY = 'CI'
        NEIGHBORHOOD = 'NB'

    name = models.CharField(max_length=255)
    country_id = models.CharField(max_length=2)
    destination_type = models.CharField(max_length=2, choices=DestinationType.choices)
    parent_destination_id = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_destination_type_display()})" # type: ignore[attr-defined]

    class Meta:
        db_table = "destination"

class Property(models.Model):
    class PropertyType(models.TextChoices):
        REPUBLIC = 'Republic'
        BOARDING_HOUSE = 'BoardingHouse'
        HOTEL = 'Hotel'

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=PropertyType.choices)
    rules = models.TextField()
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})" # type: ignore[attr-defined]

    class Meta:
        db_table = "property"

class PropertyManager(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profile.name} - {self.property.name}"

    class Meta:
        db_table = "property_manager"

class Room(models.Model):
    room_number = models.CharField(max_length=50)
    capacity = models.IntegerField()
    shared = models.BooleanField(default=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    accept_men = models.BooleanField(default=True)
    accept_women = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} - {self.property.name}"

    class Meta:
        db_table = "room"


class RoomPrice(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    period = models.CharField(max_length=10, choices=PeriodChoices.choices, default=PeriodChoices.SEMESTER)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Feature(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "feature"

class RoomFeature(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.room} - {self.feature.name}"

    class Meta:
        db_table = "room_feature"

class RoomPhoto(models.Model):
    url = models.URLField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo of {self.room.room_number}"

    class Meta:
        db_table = "room_photo"

class Proposal(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='proposals')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=10, choices=PeriodChoices.choices, default=PeriodChoices.SEMESTER)
    move_in_date = models.DateField()
    move_out_date = models.DateField()
    message = models.TextField()
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_proposals')

    def __str__(self):
        return f"Proposal by {self.profile.name} for {self.room.room_number}"

    class Meta:
        db_table = "proposal"

class Rental(models.Model):
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    period = models.CharField(max_length=10, choices=PeriodChoices.choices, default=PeriodChoices.SEMESTER)
    expected_start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.name} stays in {self.room.room_number}"

    class Meta:
        db_table = "rental"

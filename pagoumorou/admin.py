from django.contrib import admin
from .models import (
    CustomUser,
    Destination,
    Property,
    PropertyManager,
    Room,
    Feature,
    RoomFeature,
    RoomPhoto,
    Proposal,
    Rental
)

admin.site.register(CustomUser)
admin.site.register(Destination)
admin.site.register(Property)
admin.site.register(PropertyManager)
admin.site.register(Room)
admin.site.register(Feature)
admin.site.register(RoomFeature)
admin.site.register(RoomPhoto)
admin.site.register(Proposal)
admin.site.register(Rental)

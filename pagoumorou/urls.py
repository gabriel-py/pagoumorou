from django.urls import path

from pagoumorou.views import RoomAPI, SearchAPI

urlpatterns = [
    path("search", SearchAPI.as_view(), name="search"),
    path("room/<int:room_id>/", RoomAPI.as_view(), name="room"),
]

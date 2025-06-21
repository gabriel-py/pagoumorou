from django.urls import path

from pagoumorou.views import ProposalAPI, RoomAPI, SearchAPI

urlpatterns = [
    path("search", SearchAPI.as_view(), name="search"),
    path("room/<int:room_id>/", RoomAPI.as_view(), name="room"),
    path("proposal", ProposalAPI.as_view(), name="proposal"),
    path("proposal/<int:proposal_id>/", ProposalAPI.as_view(), name="proposal"),
]

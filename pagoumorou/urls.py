from django.urls import path

from pagoumorou.views import SearchAPI

urlpatterns = [
    path("search", SearchAPI.as_view(), name="search"),
]

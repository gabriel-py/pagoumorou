from django.urls import path

from user.views import CreateUserView, UpdateUserView

urlpatterns = [
    path("users/", CreateUserView.as_view(), name="create-user"),
    path("users/<int:user_id>/", UpdateUserView.as_view(), name="update-user"),
]

from django.urls import path

from user.views import CreateUserView, UpdateUserView

urlpatterns = [
    path("profile/", CreateUserView.as_view(), name="create-user"),
    path("profile/<int:user_id>/", UpdateUserView.as_view(), name="update-user"),
]

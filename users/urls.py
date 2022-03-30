from django.urls import path
from users.views import UserAuthorization

urlpatterns = [
    path('register/', UserAuthorization.as_view(), name='register'),
]
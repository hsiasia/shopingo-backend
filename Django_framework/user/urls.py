from django.urls import path
from user.views import GetUserByID

urlpatterns = [
    path('api/user/', GetUserByID.as_view())
]
from django.urls import path
from user.views import GetUserByID,CreateUserAccount

urlpatterns = [
    path('api/user/', GetUserByID.as_view()),
    path('api/user/', CreateUserAccount.as_view())
]
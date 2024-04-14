from django.urls import path
from user.views import GetUserByID,CreateUserAccount

urlpatterns = [
    path('api/user/googleAuth', CreateUserAccount.as_view()),
    path('api/user/', GetUserByID.as_view())   
]
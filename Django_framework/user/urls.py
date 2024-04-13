from django.urls import path
from user import views

urlpatterns = [
    path('api/user/', views.get_user_info, name='get_user_info')
]
from django.urls import path
from user.views import GetUserByID,CreateUserAccount,UpdateUserScore,GetUserScoreData


urlpatterns = [
    path('api/user/scoreHistory', GetUserScoreData.as_view()),
    path('api/user/score', UpdateUserScore.as_view()),    
    path('api/user/login', CreateUserAccount.as_view()),
    path('api/user/', GetUserByID.as_view())   
] 
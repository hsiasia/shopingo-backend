from django.urls import path
from googleAPIs.views import GenerateSignedUrlsAPIView
urlpatterns = [
    path('api/google/image',  GenerateSignedUrlsAPIView.as_view(), name='GenerateSignedUrls'),
]
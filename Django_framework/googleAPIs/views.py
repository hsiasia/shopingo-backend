from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from googleAPIs.tool.tools import generate_download_signed_urls

class GenerateSignedUrlsAPIView(generics.ListAPIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        blob_names = request.data.get('blob_names')

        try:
            urls = generate_download_signed_urls(blob_names)
            resp = {
                'data': urls,
                'error' : None,
                'status': status.HTTP_200_OK
            }
            return Response(resp,status=status.HTTP_200_OK)
        except Exception as e:
            resp = {
                'data':None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(resp, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from googleAPIs.tool.tools import generate_download_signed_urls

class GenerateSignedUrlsAPIView(generics.CreateAPIView):
    parser_classes = [JSONParser]

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'blob_names': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='List of blob names for which signed URLs are to be generated')
        },
        required=['blob_names']  # Specify required fields
    )

    # Define the successful response schema
    response_schema_dict = {
        status.HTTP_201_CREATED: openapi.Response(
            description="Signed URLs generated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(
                        type=openapi.TYPE_ARRAY, 
                        items=openapi.Items(type=openapi.TYPE_ARRAY, items=openapi.Items(
                            type=openapi.TYPE_STRING)),
                        description='Each inner array contains two strings: the generated signed URL and the GCS static image URL.'
                    ),
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error status (null if no error)'),
                    'status': openapi.Schema(type=openapi.TYPE_INTEGER, description='HTTP status code')
                }
            )
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
            description="Internal Server Error",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(type=openapi.TYPE_STRING, description='Data field (null on error)'),
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message if the operation fails'),
                    'status': openapi.Schema(type=openapi.TYPE_INTEGER, description='HTTP status code')
                }
            )
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'data': openapi.Schema(type=openapi.TYPE_STRING, description='No data to return'),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message indicating missing blob_names'),
                        'status': openapi.Schema(type=openapi.TYPE_INTEGER, description='HTTP status code')
                    }
                )
        )
    }

    @swagger_auto_schema(
        request_body=request_body,
        responses=response_schema_dict,
        operation_description="Generate signed URLs for specified blob names",
        operation_summary="Generate URLs file path, add it directly into frontend image attribute"
    )
    def post(self, request, *args, **kwargs):
        blob_names = request.data.get('blob_names')

        if not blob_names:
            resp = {
                'data': None,
                'error': 'Missing required parameter: blob_names',
                'status': status.HTTP_400_BAD_REQUEST
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            urls = generate_download_signed_urls(blob_names)
                
            resp = {
                'data': urls,
                'error': None,
                'status': status.HTTP_201_CREATED
            }
            return Response(resp, status=status.HTTP_201_CREATED)

        except Exception as e:
            resp = {
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(resp, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

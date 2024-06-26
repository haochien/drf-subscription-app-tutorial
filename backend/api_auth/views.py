from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import TestModel
from .serializers import TestModelSerializer, RegisterSerializer
import logging

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)
User = get_user_model()

# Create your views here.
class TestModelViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer

    def list(self, request, *args, **kwargs):
        logger.info('TestModelViewSet list view called')
        logger.warning('Warning log in list view')
        return super().list(request, *args, **kwargs)


class TestModelProtectedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer
    

class CustomRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

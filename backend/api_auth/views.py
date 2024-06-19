from django.shortcuts import render
from rest_framework import viewsets
from .models import TestModel
from .serializers import TestModelSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class TestModelViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer

    def list(self, request, *args, **kwargs):
        logger.info('TestModelViewSet list view called')
        logger.warning('Warning log in list view')
        return super().list(request, *args, **kwargs)
    
    

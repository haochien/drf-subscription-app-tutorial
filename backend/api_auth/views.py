from django.shortcuts import render
from rest_framework import viewsets
from .models import TestModel
from .serializers import TestModelSerializer

# Create your views here.
class TestModelViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer

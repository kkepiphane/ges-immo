from rest_framework import serializers
from .models import *

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model=Building
        fields = ['id', 'name', 'address', 'description', 'building_type']

class AppartmentSerializer(serializers.ModelSerializer):
    building = BuildingSerializer()
    class Meta:
        model=Appartment
        fields = '__all__'

class AppPicSerializer(serializers.ModelSerializer):
    class Meta:
        model=AppPic
        fields = ['id', 'image_fil']

class DemandCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Demand
        fields = '__all__'

class DemandSerializer(serializers.ModelSerializer):
    appartment = AppartmentSerializer()
    class Meta:
        model=Demand
        fields = '__all__'
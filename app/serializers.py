from rest_framework import serializers

from app import models


class SallaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SallaUser
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated': {'read_only': True},
            'password': {'read_only': True},
        }


class SallaStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SallaStore
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated': {'read_only': True},
        }


class ProductEndpointParamsSerializer(serializers.Serializer):
    STATUS_CHOICES = ('hidden', 'sale', 'out')

    category = serializers.CharField(required=False, max_length=100)
    keyword = serializers.CharField(required=False, max_length=100)
    page = serializers.IntegerField(required=False, default=1)
    per_page = serializers.IntegerField(required=False, default=100)
    status = serializers.ChoiceField(required=False, choices=STATUS_CHOICES)


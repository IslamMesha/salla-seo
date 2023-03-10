from rest_framework import serializers

class ProductEndpointParamsSerializer(serializers.Serializer):
    STATUS_CHOICES = ('hidden', 'sale', 'out')

    category = serializers.CharField(required=False, max_length=100)
    keyword = serializers.CharField(required=False, max_length=100)
    page = serializers.IntegerField(required=False, default=1)
    per_page = serializers.IntegerField(required=False, default=100)
    status = serializers.ChoiceField(required=False, choices=STATUS_CHOICES)


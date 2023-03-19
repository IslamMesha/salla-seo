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
    per_page = serializers.IntegerField(required=False, default=10)
    status = serializers.ChoiceField(required=False, choices=STATUS_CHOICES)


class ChatGPTResponseSerializer(serializers.Serializer):
    id = serializers.CharField(write_only=True, required=False)
    object = serializers.CharField(write_only=True, required=False)
    created = serializers.CharField(write_only=True, required=False)
    model = serializers.CharField(write_only=True, required=False)
    usage = serializers.DictField(write_only=True)
    choices = serializers.ListField(write_only=True, child=serializers.DictField())

    prompt = serializers.CharField()

    total_tokens = serializers.IntegerField(source='usage.total_tokens', read_only=True)
    answer = serializers.SerializerMethodField(read_only=True)
    full_response = serializers.DictField(source='*', read_only=True)

    def get_answer(self, obj):
        return obj['choices'][0]['text'].strip()

    def save(self, **kwargs):
        return models.ChatGPTLog.objects.create(**self.data)


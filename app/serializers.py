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


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
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


class ChatGPTLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChatGPTLog
        fields = '__all__'


class UserPromptSerializer(serializers.ModelSerializer):
    chat_gpt_log = ChatGPTLogSerializer(read_only=True)
    class Meta:
        model = models.UserPrompt
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
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


class ProductGetDescriptionPOSTBodySerializer(serializers.Serializer):
    id = serializers.CharField(required=True, write_only=True)
    name = serializers.CharField(required=True, write_only=True)
    keywords_list = serializers.ListField(child=serializers.CharField(), default=[])

    # Those will be used as values in the chatgpt templates
    product_id = serializers.CharField(source='id', read_only=True)
    product_name = serializers.CharField(source='name', read_only=True)
    keywords = serializers.SerializerMethodField(read_only=True)
    
    def get_keywords(self, obj):
        return ', '.join(obj['keywords'])


class ProductListHistoryPOSTBodySerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True)
    prompt_type = serializers.ChoiceField(required=True, choices=['title', 'description','seo_title','seo_description'])


class ProductUpdatePOSTBodySerializer(serializers.Serializer):
    description = serializers.CharField(required=True)


class LoginPOSTBodySerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class SallaWebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SallaWebhookLog
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }



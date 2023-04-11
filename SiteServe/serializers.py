from rest_framework import serializers

from SiteServe import models


class StaticPageNavPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StaticPage
        fields = ('nav_name', 'slug', 'url')
    

import os

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from SiteServe import models


class LoadStaticPageView(APIView):
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, slug):
        page = get_object_or_404(models.StaticPage, slug=slug)
        context = {
            'page': page,
            'nav_pages': models.StaticPage.get_nav_pages()
        }

        return Response(context, template_name='static_page.html')




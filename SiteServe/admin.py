from django.contrib import admin

from SiteServe import models


admin.site.register(models.StaticPage)
admin.site.register(models.ChatGPTPromptTemplate)


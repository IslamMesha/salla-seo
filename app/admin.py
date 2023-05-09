from django.contrib import admin

from app import models

admin.site.register(models.SallaUser)
admin.site.register(models.SallaStore)
admin.site.register(models.Account)
admin.site.register(models.ChatGPTResponse)
admin.site.register(models.UserPrompt)
admin.site.register(models.SallaWebhookLog)


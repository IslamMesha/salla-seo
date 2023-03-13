from django.db.models.signals import post_save
from django.dispatch import receiver

from app import models
from app import utils
from app.controllers import SallaMerchantReader
from app.serializers import SallaStoreSerializer

@receiver(post_save, sender=models.Account)
def pull_store(sender, instance, created, **kwargs):
    if not created:
        return

    store_data = SallaMerchantReader(instance).get_store()
    store_data['salla_id'] = store_data.pop('id')

    return utils.create_by_serializer(SallaStoreSerializer, store_data)

    
    


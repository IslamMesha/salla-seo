from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from app import models
from app import utils
from app.controllers import SallaMerchantReader, SallaAppSettingsReader
from app.serializers import SallaUserSerializer, SallaStoreSerializer, SallaUserSubscriptionPayloadSerializer


@receiver(pre_save, sender=models.Account)
def pull_user(sender, instance, **kwargs):
    created = instance.pk is None
    user_not_exists = instance.user is None

    if created and user_not_exists:
        user_data = SallaMerchantReader(instance).get_user()
        user_data['salla_id'] = user_data.pop('id')

        user = utils.create_by_serializer(SallaUserSerializer, user_data)
        instance.user = user


@receiver(post_save, sender=models.Account)
def pull_store(sender, instance, created, **kwargs):
    if created:
        store_data = SallaMerchantReader(instance).get_store()
        store_data['salla_id'] = store_data.pop('id')
        store_data['user'] = instance.user.pk

        utils.create_by_serializer(SallaStoreSerializer, store_data)


@receiver(post_save, sender=models.SallaUser)
def pull_subscription_plan(sender, instance, created, **kwargs):
    if created:
        account = instance.account
        try:
            payload = SallaAppSettingsReader(account).get_subscription()
        except Exception as e:
            payload = {
                'plan_type': 'recurring',
                'plan_name': 'Free',
                'plan_period': None,
            }

        payload_data = SallaUserSubscriptionPayloadSerializer(data=payload)
        payload_data.is_valid(raise_exception=True)

        subscription = models.SallaUserSubscription(
            user=instance, payload=payload, **payload_data.data,
        )
        subscription.save()

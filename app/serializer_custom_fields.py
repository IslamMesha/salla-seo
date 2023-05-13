from datetime import timedelta
from rest_framework import serializers


class SallaSubscriptionPlanDurationField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, timedelta):
            return data.days / 30
        else:
            return data

    def to_representation(self, value):
        try:
            duration_in_months = int(value)
            return timedelta(days=duration_in_months*30)
        except ValueError:
            raise serializers.ValidationError("Invalid duration")



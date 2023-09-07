from rest_framework import permissions
from datetime import timedelta

class SallaPlanLimits(permissions.BasePermission):
    message = 'You have reached your plan limits'

    def has_permission(self, request, view):
        from app.models import UserPrompt

        if request.user.is_authenticated:
            subscription = request.user.subscriptions.filter(is_active=True).last()
            if subscription and subscription.is_alive:
                start_date = subscription.created_at
                end_date = subscription.created_at + (subscription.plan_period or timedelta(days=1000)) 
                # get prompts count during the subscription month
                prompts_count = UserPrompt.count_for_user(request.user, start_date, end_date, gpt=True)
                # request.user.prompts.filter(
                #     created_at__gte=start_date, created_at__lte=end_date
                # ).count()
                return prompts_count < subscription.gpt_prompts_limit
        return False

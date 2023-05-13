from rest_framework import permissions


class SallaPlanLimits(permissions.BasePermission):
    message = 'You have reached your plan limits'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            subscription = request.user.subscriptions.filter(is_active=True).last()
            if subscription and subscription.is_alive:
                start_date = subscription.created_at
                end_date = subscription.created_at + subscription.plan_period
                # get prompts count during the subscription month
                prompts_count = request.user.prompts.filter(
                    created_at__gte=start_date, created_at__lte=end_date
                ).count()
                return prompts_count < subscription.gpt_prompts_limit
        return False

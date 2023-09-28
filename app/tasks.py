
from celery import shared_task


@shared_task
def refresh_tokens():
    from time import time
    from app.models import Account
    
    print('REFRESH')
    
    end_in_3_days = time() + 60*60*24*3
    accounts = Account.objects.filter(expires_in__lte=end_in_3_days)
    for account in accounts:
        account.refresh_access_token()
        
    print('REFRESH DONE')
    
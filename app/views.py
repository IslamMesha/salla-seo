import os

from django.shortcuts import render, redirect
from django.contrib import messages

from app.controllers import SallaOAuth


def index(request):
    app_id = os.environ.get('SALLA_APP_ID')
    context = {
        'installation_url': f'https://s.salla.sa/apps/install/{app_id}',
    }
    return render(request, 'index.html', context=context)

def oauth_callback(request):
    code = request.GET.get('code')
    if code:
        messages.success(request, 'Login Success.')
        access_token = SallaOAuth().get_access_token(code)
        print(access_token)
    else:
        messages.error(request, 'Login Failed.')

    return redirect('app:index')




import jwt
import datetime
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os

@csrf_exempt
def sign_in(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            # Define JWT payload
            payload = {
                'id': user.id,
                'username': user.username,
                'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),  # Token expires in 1 hour
            }
            # Encode JWT token
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return JsonResponse({'token': token}, status=200)
        else:
            return JsonResponse({'error': 'Invalid Credentials'}, status=400)
    return JsonResponse({'error': 'POST request required.'}, status=400)

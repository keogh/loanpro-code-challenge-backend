import jwt
import datetime
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.core.cache import cache


class AuthViews:
    @classmethod
    @csrf_exempt
    def sign_in(cls, request):
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                payload = {
                    'id': user.id,
                    'username': user.username,
                    'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=36),  # Token expires in 1 hour
                }
                # Encode JWT token
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

                return JsonResponse({'token': token}, status=200)
            else:
                return JsonResponse({'error': 'Invalid Credentials'}, status=400)
        return JsonResponse({'error': 'POST request required.'}, status=400)

    @classmethod
    @csrf_exempt
    def sign_out(cls, request):
        if request.method == 'POST':
            token = request.headers.get('Authorization')
            if token:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'],
                                           options={"verify_exp": False})
                exp_time = decoded_token['exp']
                cache.set(token, 'blocklisted', timeout=exp_time - datetime.datetime.now(datetime.UTC).timestamp())

                return JsonResponse({'message': 'Signed out successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Authorization token not provided'}, status=400)
        return JsonResponse({'error': 'POST request required.'}, status=400)

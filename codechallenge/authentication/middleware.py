import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse


def jwt_authentication_middleware(get_response):
    def middleware(request):
        token = request.headers.get('Authorization')
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user = get_user_model().objects.get(id=payload['id'])
                request.user = user
            except (jwt.ExpiredSignatureError, jwt.DecodeError, get_user_model().DoesNotExist):
                return JsonResponse({'error': 'Invalid or expired token'}, status=403)

        response = get_response(request)
        return response

    return middleware

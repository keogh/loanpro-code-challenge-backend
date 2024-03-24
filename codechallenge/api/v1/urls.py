from django.urls import path, include
from codechallenge.views import sign_in

urlpatterns = [
    path('sign-in', sign_in, name='sign-in'),
]

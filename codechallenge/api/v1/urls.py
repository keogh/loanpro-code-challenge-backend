from django.urls import path, include
from codechallenge.views.auth import AuthViews
from codechallenge.views.record import RecordViews

urlpatterns = [
    path('sign-in', AuthViews.sign_in, name='sign-in'),

    path('records', RecordViews.plural_endpoint, name='Record plural actions'),
    # path('records/<record_id>'),
]

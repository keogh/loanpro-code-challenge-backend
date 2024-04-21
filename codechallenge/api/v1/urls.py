from django.urls import path, include
from codechallenge.views.auth import AuthViews
from codechallenge.views.operation import OperationViews
from calculator.views import RecordViews

urlpatterns = [
    path('sign-in', AuthViews.sign_in, name='sign-in'),
    path('sign-out', AuthViews.sign_out, name='sign-out'),

    path('operations', OperationViews.plural_endpoint, name='Operation plural actions'),

    path('records', RecordViews.plural_endpoint, name='Record plural actions'),
    path('records/<record_id>', RecordViews.singular_endpoint, name='Record singular actions'),
]

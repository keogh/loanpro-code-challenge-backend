from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from calculator.models import Operation


class OperationViews:
    @classmethod
    @method_decorator(csrf_exempt)
    def plural_endpoint(cls, request):
        if request.method == 'GET':
            return cls.list(request)
        if request.method == 'POST':
            return cls.create(request)
        else:
            return JsonResponse({
                'success': False,
                'errors': ['Method not Allowed']
            }, status=405)

    @classmethod
    def list(cls, request):
        operations_list = Operation.objects.all()

        operations_data = [{
            'id': operation.id,
            'type': operation.type,
            'cost': operation.cost,
        } for operation in operations_list]

        return JsonResponse({
            'success': True,
            'operations': operations_data
        })
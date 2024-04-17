from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from calculator.models import Operation


class OperationViews:
    @classmethod
    @method_decorator(csrf_exempt)
    def plural_endpoint(cls, request):
        if request.method == 'GET':
            return cls.list(request)
        else:
            return JsonResponse({
                'success': False,
                'errors': ['Method not Allowed']
            }, status=405)

    @classmethod
    def list(cls, request):
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort_by', 'id').strip()
        direction = request.GET.get('direction', 'desc').strip()
        valid_sort_columns = ['id', 'type', 'cost', 'name']
        sort_prefix = '' if direction.lower() == 'asc' else '-'

        if sort_by not in valid_sort_columns:
            sort_by = 'id'

        order_by = f'{sort_prefix}{sort_by}'

        operations_list = Operation.objects.filter(
            type__icontains=search_query
        ).order_by(order_by)

        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        paginator = Paginator(operations_list, int(per_page))

        try:
            operations = paginator.page(page)
        except PageNotAnInteger:
            operations = paginator.page(1)
        except EmptyPage:
            operations = paginator.page(paginator.num_pages)

        operations_data = [{
            'id': operation.id,
            'name': operation.name,
            'type': operation.type,
            'cost': operation.cost,
        } for operation in operations]

        return JsonResponse({
            'success': True,
            'operations': operations_data,
            'pagination': {
                'page': operations.number,
                'per_page': paginator.per_page,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
            }
        })
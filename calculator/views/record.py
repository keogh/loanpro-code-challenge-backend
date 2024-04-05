from django.http import JsonResponse
from calculator.models import Record, Operation
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)


class RecordViews:
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
        records_list = Record.objects.filter(user=request.user)
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        paginator = Paginator(records_list, per_page)  # Show 10 records per page

        try:
            records = paginator.page(page)
        except PageNotAnInteger:
            records = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            records = paginator.page(paginator.num_pages)

        records_data = [{
            'id': record.id,
            'operation_id': record.operation.id,
            'operation_type': record.operation.type,
            'user_id': record.user.id,
            'amount': record.amount,
            'user_balance': record.user_balance,
            'operation_response': record.operation_response,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        } for record in records]

        return JsonResponse({
            'success': True,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
            },
            'records': records_data
        })

    @classmethod
    def create(cls, request):
        try:
            data = json.loads(request.body)
            operation_id = data.get('operation_id')

            if not operation_id:
                return JsonResponse({'success': False, 'error': 'Missing operation_id'}, status=400)

            try:
                operation = Operation.objects.get(id=operation_id)
            except ObjectDoesNotExist:
                return JsonResponse({'success': False, 'error': 'Operation not found'}, status=404)

            try:
                operator1 = int(data.get('operator1'))
                operator2 = int(data.get('operator2'))
            except ValueError:
                return JsonResponse({'error': 'both operators must integer numbers'}, status=400)

            OPERATIONS_WITH_TWO_OPERATORS = [
                'addition', 'subtraction', 'multiplication', 'division'
            ]
            if not operator1:
                return JsonResponse({'success': False, 'error': 'Missing operator1'}, status=400)
            if operation.type in OPERATIONS_WITH_TWO_OPERATORS and not operator2:
                return JsonResponse({'success': False, 'error': 'Missing operator2'}, status=400)

            if operation.type == 'addition':
                operation_response = operator1 + operator2
            elif operation.type == 'subtraction':
                operation_response = operator1 - operator2
            elif operation.type == 'multiplication':
                operation_response = operator1 * operator2
            elif operation.type == 'division':
                operation_response = operator1 / operator2
            elif operation.type == 'square_root':
                operation_response = operator1 ** 0.5
            elif operation.type == 'random_string':
                # TODO: Connect to service for random string
                operation_response = 'hola'
            else:
                return JsonResponse({'success': False, 'error': 'Invalid Operation'}, status=400)

            record = Record.objects.create(
                user=request.user,
                operation=operation,
                amount=operation.cost,
                user_balance=0,
                operation_response=operation_response,
            )

            return JsonResponse({'success': True, 'record_id': record.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
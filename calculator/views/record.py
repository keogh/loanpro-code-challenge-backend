from django.contrib.auth.models import User
from django.http import JsonResponse
from calculator.models import Record, Operation
from calculator.utils import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator
import logging
from django.db import transaction

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
    @method_decorator(csrf_exempt)
    def singular_endpoint(cls, request, record_id):
        if request.method == 'DELETE':
            return cls.delete(request, record_id)
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
        valid_sort_columns = ['id', 'amount', 'user_balance', 'created_at']
        sort_prefix = '' if direction.lower() == 'asc' else '-'

        if sort_by not in valid_sort_columns:
            sort_by = 'id'

        order_by = f'{sort_prefix}{sort_by}'

        records_list = Record.objects.filter(
            deleted_at__isnull=True,
            user=request.user,
            operation__type__icontains=search_query
        ).order_by(order_by)

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
            'operation_type': record.operation.name,
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
        # TODO: Make this method thinner by moving code sections into its own methods:
        #       - Validate input
        #       - calculate balance
        #       - Perform operation
        #       - Save in database
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

            profile = request.user.userprofile
            try:
                new_user_balance = profile.balance - operation.cost
            except AttributeError:
                new_user_balance = -1  # Default balance if UserProfile does not exist
            except User.userprofile.RelatedObjectDoesNotExist:
                new_user_balance = -1  # Handle the case where the userprofile is not created

            if new_user_balance < 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Request denied. Insufficient balance for this operation'
                }, status=403)

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
                operation_response = get_random_string(operator1, 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
                if operation_response is None:
                    return JsonResponse({
                        'success': False,
                        'error': 'Oops. Something went wrong in the Random.org external service.'
                    }, status=503)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid Operation'}, status=400)

            try:
                with transaction.atomic():
                    profile.balance = new_user_balance
                    profile.save()

                    record = Record.objects.create(
                        user=request.user,
                        operation=operation,
                        amount=operation.cost,
                        user_balance=new_user_balance,
                        operation_response=operation_response,
                    )

            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Something went wrong while saving. {e}'
                }, status=500)

            return JsonResponse({
                'success': True,
                'record_id': record.id,
                'user_balance': new_user_balance
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    @classmethod
    def delete(cls, request, record_id):
        with transaction.atomic():
            try:
                record = Record.objects.select_for_update().get(
                    pk=record_id,
                    user=request.user,
                    deleted_at__isnull=True
                )
                record.deleted_at = timezone.now()
                record.save()

                # Fetch all subsequent records for the same user created after the soft-deleted record
                subsequent_records = Record.objects.filter(
                    user=request.user,
                    created_at__gt=record.created_at,
                    deleted_at__isnull=True
                ).select_for_update()  # Lock these records

                # Update user_balance for subsequent records
                amount_to_read = record.amount
                for subsequent_record in subsequent_records:
                    subsequent_record.user_balance += amount_to_read
                    subsequent_record.save()

                # Update user's UserProfile balance
                user_profile = request.user.userprofile
                user_profile.balance += amount_to_read
                user_profile.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Record deleted successfully, user balances records updated'
                })

            except Record.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

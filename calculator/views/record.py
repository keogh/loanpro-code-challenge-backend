from django.http import JsonResponse
from calculator.models import Record
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class RecordViews:
    @classmethod
    def plural_endpoint(cls, request):
        if request.method == 'GET':
            return cls.list(request)
        # if request.method == 'POST':
        #     # TODO: Create a record
        else:
            return JsonResponse({
                'success': False,
                'errors': ['Method not Allowed']
            }, status=405)

    @classmethod
    def list(cls, request):
        records_list = Record.objects.filter(user=request.user.id)
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
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'records': records_data
        })
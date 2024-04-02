from django.http import JsonResponse
from calculator.models import Record


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
        user_records = Record.objects.filter(user=request.user.id)

        # Serialize the records into a list of dictionaries
        records_data = [{
            'id': record.id,
            'operation_id': record.operation.id,
            'operation_type': record.operation.type,  # Assuming you want to show the type of operation
            'user_id': record.user.id,
            'amount': record.amount,
            'user_balance': record.user_balance,
            'operation_response': record.operation_response,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format datetime as string
        } for record in user_records]

        # Return the serialized data as a JsonResponse
        return JsonResponse({
            'success': True,
            'records': records_data
        })

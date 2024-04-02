from django.http import JsonResponse


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
        return JsonResponse({
            'success': True,
            'records': [{'hola': 'que ase'}]
        })

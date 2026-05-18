"""Filter endpoint for the doctor dashboard session list."""

from django.http import JsonResponse

from api.models import Test


def filter_tests_view(request):
    """GET /portal/filter-sessions/

    Optional query params (all ignored when absent):
        test_id, age_min, age_max, language, date_from, date_to, status
    """
    qs = Test.objects.all()

    test_id = request.GET.get('test_id')
    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    language = request.GET.get('language')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    test_status = request.GET.get('status')

    if test_id:
        qs = qs.filter(test_id=test_id)
    if age_min:
        qs = qs.filter(age__gte=int(age_min))
    if age_max:
        qs = qs.filter(age__lte=int(age_max))
    if language:
        qs = qs.filter(language__iexact=language)
    if date_from:
        qs = qs.filter(date_created__date__gte=date_from)
    if date_to:
        qs = qs.filter(date_created__date__lte=date_to)
    if test_status:
        qs = qs.filter(status=test_status)

    data = list(qs.values(
        'test_id', 'doctor_id', 'age', 'language',
        'status', 'date_created', 'date_completed',
    ))
    return JsonResponse(data, safe=False)

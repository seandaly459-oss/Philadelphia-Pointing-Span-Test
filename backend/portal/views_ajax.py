from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from api.models import Test
from django.db.models import CharField, Max
from django.db.models.functions import Cast
import datetime
from .session_utils import annotate_session_queryset, build_recent_sessions

def filter_sessions_ajax(request):
    """
    AJAX endpoint for filtering sessions. Returns rendered HTML fragment.
    Accepts POST with filter fields: anon_id, age_min, age_max, language, date_from, date_to
    """

    try:
        doctor = request.user.doctor
    except Exception:
        return HttpResponse('Unauthorized', status=401)

    qs = annotate_session_queryset(Test.objects.filter(doctor=doctor))

    raw_anon_id = request.POST.get('anon_id', '').strip()
    anon_id = raw_anon_id.replace('ANON-', '') if raw_anon_id.upper().startswith('ANON-') else raw_anon_id
    age_min = request.POST.get('age_min')
    age_max = request.POST.get('age_max')
    language = request.POST.get('language')
    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')

    print("[DEBUG] Filter values:", dict(request.POST))

    if anon_id:
        qs = qs.annotate(test_id_str=Cast('test_id', CharField()))
        if raw_anon_id.upper().startswith('ANON-') and anon_id.isdigit():
            qs = qs.filter(test_id=int(anon_id))
        else:
            qs = qs.filter(test_id_str__icontains=anon_id)
    if age_min:
        qs = qs.filter(age__gte=int(age_min))
    if age_max:
        qs = qs.filter(age__lte=int(age_max))
    if language:
        qs = qs.filter(language__iexact=language)
    if date_from:
        qs = qs.filter(activity_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(activity_at__date__lte=date_to)

    qs = qs.order_by('-activity_at', '-test_id')
    print(f"[DEBUG] Filtered queryset count: {qs.count()}")

    recent_sessions = build_recent_sessions(qs)

    if not recent_sessions:
        html = '<div class="session"><div class="sess-info"><div class="sess-row1"><span class="sess-id">No sessions found matching your filters.</span></div></div></div>'
    else:
        html = render_to_string('portal/_sessions_list.html', {'recent_sessions': recent_sessions})
    return HttpResponse(html)
from django.db.models import Exists, Max, OuterRef
from django.db.models.functions import Coalesce

from api.models import Response as PatientResponse
from api.models import Stimulus, Test_Data


STATUS_METADATA = {
    'completed': {
        'label': 'Complete',
        'css_class': 'tag-status-complete',
    },
    'in_progress': {
        'label': 'In Progress',
        'css_class': 'tag-status-progress',
    },
    'incomplete': {
        'label': 'Incomplete',
        'css_class': 'tag-status-incomplete',
    },
}


def annotate_session_queryset(queryset):
    return queryset.annotate(
        max_span=Max('stimuli__span'),
        has_mixed=Exists(
            Stimulus.objects.filter(test=OuterRef('pk'), stimulus_type__icontains='mixed')
        ),
        has_test_data=Exists(Test_Data.objects.filter(test=OuterRef('pk'))),
        has_responses=Exists(PatientResponse.objects.filter(stimulus__test=OuterRef('pk'))),
        activity_at=Coalesce('date_completed', 'date_created'),
    )


def build_recent_sessions(queryset):
    recent_sessions = []
    for test in queryset:
        status_key = derive_session_status(test)
        status_meta = STATUS_METADATA[status_key]
        display_date = test.date_completed if status_key == 'completed' and test.date_completed else test.date_created

        recent_sessions.append({
            'test_id': test.test_id,
            'anon_id': f'ANON-{test.test_id}',
            'date': display_date.strftime('%Y-%m-%d') if display_date else '-',
            'span': test.max_span or 0,
            'test_type': 'Digit-Letter' if test.has_mixed else 'Digit Span',
            'status_label': status_meta['label'],
            'status_class': status_meta['css_class'],
        })

    return recent_sessions


def derive_session_status(test):
    if test.date_completed or getattr(test, 'has_test_data', False):
        return 'completed'

    if test.status == 'in_progress' or getattr(test, 'has_responses', False):
        return 'in_progress'

    return 'incomplete'
"""Views for the portal app."""

import json
import random
import uuid
from django.db.models import Avg, Max
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from api.models import Response as PatientResponse, Test, Doctor, Stimulus
from api.email_utils import validate_patient_email, send_test_link_email
from .session_utils import annotate_session_queryset, build_recent_sessions

# Age buckets used for the Performance Trends chart
_AGE_BUCKETS = [
    ('20-24', 20, 24), ('25-29', 25, 29), ('30-34', 30, 34),
    ('35-39', 35, 39), ('40-44', 40, 44), ('45-49', 45, 49),
    ('50-54', 50, 54), ('55-59', 55, 59), ('60-64', 60, 64),
    ('65-69', 65, 69), ('70-74', 70, 74), ('75+', 75, 200),
]

digits = ['1','2','3','4','5','6','7','8','9']
letters = ['A','E','I','O','Q','R','S','U','Y']


def _resolve_doctor_for_user(user):
    """Return a Doctor profile for an authenticated Django user, creating/linking one if needed."""
    if not user.is_authenticated:
        return None

    username = user.username.strip()
    fallback_email = f'{username}@ppst.local'

    doctor = Doctor.objects.filter(user=user).first()

    if not doctor:
        doctor = Doctor.objects.filter(username=username).first()
        if doctor and doctor.user_id is None:
            doctor.user = user

    if not doctor:
        doctor = Doctor(
            user=user,
            username=username,
            email=user.email.strip() if user.email else fallback_email,
            password_hash='!',
        )
        doctor.save()
        return doctor

    update_fields = []
    if doctor.user_id != user.id:
        doctor.user = user
        update_fields.append('user')
    if user.email and doctor.email != user.email:
        doctor.email = user.email
        update_fields.append('email')
    elif not doctor.email:
        doctor.email = fallback_email
        update_fields.append('email')
    if not doctor.password_hash:
        doctor.password_hash = '!'
        update_fields.append('password_hash')

    if update_fields:
        doctor.save(update_fields=update_fields)

    return doctor


def dashboard_stats(request):
    """GET /portal/stats/ — returns live summary statistics as JSON."""
    total_tests = Test.objects.count()
    completed_tests = Test.objects.filter(status='completed').count()
    avg_age = Test.objects.aggregate(avg=Avg('age'))['avg'] or 0
    mean_latency_ms = PatientResponse.objects.aggregate(avg=Avg('latency_ms'))['avg'] or 0

    chart_labels = []
    chart_data = []
    for label, lo, hi in _AGE_BUCKETS:
        avg_lat = PatientResponse.objects.filter(
            stimulus__test__age__gte=lo,
            stimulus__test__age__lte=hi,
        ).aggregate(avg=Avg('latency_ms'))['avg']
        if avg_lat is not None:
            chart_labels.append(label)
            chart_data.append(round(avg_lat / 1000, 3))

    return JsonResponse({
        'total_tests': total_tests,
        'completed_tests': completed_tests,
        'avg_age': round(avg_age, 1),
        'mean_latency_s': round(mean_latency_ms / 1000, 2),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    })


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    doctor = _resolve_doctor_for_user(request.user)
    if not doctor:
        return redirect('/accounts/login/')
    
    total_tests = Test.objects.filter(doctor=doctor).count()
    completed_tests = Test.objects.filter(doctor=doctor, status='completed').count()
    avg_age = Test.objects.filter(doctor=doctor).aggregate(avg=Avg('age'))['avg'] or 0
    mean_latency_ms = PatientResponse.objects.filter(stimulus__test__doctor=doctor).aggregate(avg=Avg('latency_ms'))['avg'] or 0

    recent_tests = annotate_session_queryset(
        Test.objects.filter(doctor=doctor)
    ).order_by('-activity_at', '-test_id')
    recent_sessions = build_recent_sessions(recent_tests)

    age_groups = [
        '20-24','25-29','30-34','35-39','40-44','45-49','50-54',
        '55-59','60-64','65-69','70-74','75-79','80-84','85-89',
        '90-94','95-99','100+'
    ]

    from collections import defaultdict
    latency_by_age = defaultdict(list)

    completed = Test.objects.filter(
        doctor=doctor, status='completed'
    ).select_related('test_data')

    for t in completed:
        try:
            latency = t.test_data.avg_overall_latency
            bucket = get_age_bucket(t.age)
            if bucket and latency:
                latency_by_age[bucket].append(latency)
        except Exception:
            continue

    chart_data = {
        'labels': age_groups,
        'values': [
            round(sum(latency_by_age[g]) / len(latency_by_age[g]) / 1000, 2)
            if latency_by_age[g] else None
            for g in age_groups
        ]
    }

    context = {
        'total_tests': total_tests,
        'completed_tests': completed_tests,
        'avg_age': round(avg_age, 1),
        'mean_latency_s': round(mean_latency_ms / 1000, 2),
        'recent_sessions': recent_sessions,
        'chart_data': json.dumps(chart_data),
        'doctor_profile_cookie_key': request.user.username if request.user.is_authenticated else 'anonymous',
        'doctor_welcome_last_name': request.user.last_name.strip() if request.user.is_authenticated else '',
    }
    return render(request, 'portal/dashboard.html', context)

def get_age_bucket(age):
    if age >= 100:
        return '100+'
    lower = (age // 5) * 5
    if lower < 20:
        return None
    return f'{lower}-{lower + 4}'

@require_POST
def create_test(request):
    try:
        age = int(request.POST.get('age'))
        language = request.POST.get('language', 'en')
        patient_email = request.POST.get('email', '').strip()

        if request.user.is_authenticated:
            username = request.user.username.strip()
            doctor = _resolve_doctor_for_user(request.user)
            doctor_display_name = f"Dr. {request.user.last_name.strip()}" if request.user.last_name.strip() else f"Dr. {username}"
        else:
            doctor = Doctor.objects.first()
            doctor_display_name = doctor.username if doctor else 'Doctor'

        if not doctor:
            return JsonResponse({'success': False, 'error': 'Doctor account not found.'}, status=400)

        if not patient_email:
            return JsonResponse({'success': False, 'error': 'Patient email is required.'}, status=400)

        is_valid, error_message = validate_patient_email(patient_email)
        if not is_valid:
            return JsonResponse({'success': False, 'error': error_message}, status=400)

        link = uuid.uuid4().hex
        test = Test.objects.create(
            doctor=doctor,
            link=link,
            age=age,
            language=language,
            voice_settings='default',
            patient_email=patient_email,
            email_sent=False,
            status='pending',
        )

        # Define the test phases with their respective parameters
        test_phases = [
            {'type': 'test_digits', 'span': 4, 'trials': 3},
            {'type': 'test_digits', 'span': 5, 'trials': 3},
            {'type': 'test_mixed', 'span': 4, 'trials': 3},
            {'type': 'test_mixed', 'span': 5, 'trials': 3},
        ]
        counter = 0
        for phase in test_phases:
            for i in range(phase.get('trials')):
                stimulus = generate_sequence(phase.get('span'), phase.get('type'))
                Stimulus.objects.create(
                    test=test,
                    sequence=stimulus,
                    stimulus_type=phase.get('type'),
                    span=phase.get('span'),
                    order_index=counter
                )
                counter += 1
                
        test_url = request.build_absolute_uri(f'/testapp/{link}/intro/')
        success, message = send_test_link_email(patient_email, test_url, doctor_display_name)

        if not success:
            test.delete()
            return JsonResponse({'success': False, 'error': message}, status=500)



        return JsonResponse({
            'success': True,
            'link': test_url,
            'test_id': test.test_id,
            'message': f'Test created and link sent to {patient_email}.',
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def generate_sequence(span, stimulus_type):
    pool = digits + letters if 'mixed' in stimulus_type else digits
    return ' '.join(random.sample(pool, span))
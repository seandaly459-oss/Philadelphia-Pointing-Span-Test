import csv

from django.http import HttpResponse
from django.utils import timezone
from django.db import models
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response as DRFResponse

from .models import Response as PatientResponse, Test, Test_Data
from .serializers import TestSerializer, TestDataSerializer


def _build_trial_response_log(stimuli):
    trial_response_log = []

    for stimulus in stimuli.order_by('order_index'):
        responses = list(stimulus.responses.order_by('click_order'))
        correct_sequence = stimulus.sequence.split(' ')
        clicked_sequence = [response.clicked_symbol for response in responses]
        click_comparisons = []

        for index, correct_char in enumerate(correct_sequence):
            response = responses[index] if index < len(responses) else None
            click_comparisons.append({
                'click_order': index + 1,
                'correct_char': correct_char,
                'clicked_char': response.clicked_symbol if response else None,
                'is_correct': response.is_correct if response else False,
                'latency_since_previous_click_ms': response.latency_ms if response else None,
            })

        trial_response_log.append({
            'is_practice': stimulus.stimulus_type.startswith('practice_'),
            'kind': 'mixed' if 'mixed' in stimulus.stimulus_type else 'numeric',
            'stimulus_type': stimulus.stimulus_type,
            'stimulus_sequence': correct_sequence,
            'clicked_sequence': clicked_sequence,
            'click_comparisons': click_comparisons,
            'is_correct': all(item['is_correct'] for item in click_comparisons) and len(clicked_sequence) == len(correct_sequence),
            'latency_ms': sum(response.latency_ms for response in responses),
        })

    return trial_response_log


# ── 1. Complete a test ────────────────────────────────────────────────────────

@api_view(['POST'])
def complete_test_view(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except Test.DoesNotExist:
        return DRFResponse({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

    stimuli = test.stimuli.all()
    all_responses = PatientResponse.objects.filter(stimulus__in=stimuli)

    total_correct = all_responses.filter(is_correct=True).count()
    total_latency = sum(r.latency_ms for r in all_responses)

    digit_stimuli = stimuli.filter(stimulus_type__in=['digit', 'test_digits'])
    digit_responses = PatientResponse.objects.filter(stimulus__in=digit_stimuli)
    digit_correct = digit_responses.filter(is_correct=True).count()
    digit_total_latency = sum(r.latency_ms for r in digit_responses)

    mixed_stimuli = stimuli.filter(stimulus_type__in=['mixed', 'test_mixed'])
    mixed_responses = PatientResponse.objects.filter(stimulus__in=mixed_stimuli)
    mixed_correct = mixed_responses.filter(is_correct=True).count()
    mixed_total_latency = sum(r.latency_ms for r in mixed_responses)
    numeric_total_stimuli = digit_stimuli.count()
    mixed_total_stimuli = mixed_stimuli.count()
    overall_total_stimuli = numeric_total_stimuli + mixed_total_stimuli
    avg_num_latency = (digit_total_latency / numeric_total_stimuli) if numeric_total_stimuli else 0
    avg_mix_latency = (mixed_total_latency / mixed_total_stimuli) if mixed_total_stimuli else 0
    avg_overall_latency = ((digit_total_latency + mixed_total_latency) / overall_total_stimuli) if overall_total_stimuli else 0
    trial_response_log = _build_trial_response_log(stimuli)

    completed_at = timezone.now()
    Test_Data.objects.update_or_create(
        test=test,
        defaults={
            'date_completed': completed_at,
            'num_total_latency': digit_total_latency,
            'mix_total_latency': mixed_total_latency,
            'avg_num_latency': avg_num_latency,
            'avg_mix_latency': avg_mix_latency,
            'avg_overall_latency': avg_overall_latency,
            'numeric_correct': digit_correct,
            'mixed_correct': mixed_correct,
            'numeric_total_stimuli': numeric_total_stimuli,
            'mixed_total_stimuli': mixed_total_stimuli,
            'trial_response_log': trial_response_log,
        },
    )

    test.status = 'completed'
    test.date_completed = completed_at
    test.save(update_fields=['status', 'date_completed'])

    return DRFResponse({
        'message': 'Test marked as completed',
        'test_id': test.test_id,
        'date_completed': test.date_completed,
        'stats': {
            'total_correct': total_correct,
            'total_latency_ms': total_latency,
            'digit_span_correct': digit_correct,
            'digit_letter_correct': mixed_correct,
        },
    })


# ── 2. CSV export for a single completed test ─────────────────────────────────

@api_view(['GET'])
def export_csv_view(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except Test.DoesNotExist:
        return DRFResponse({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

    http_response = HttpResponse(content_type='text/csv')
    http_response['Content-Disposition'] = f'attachment; filename="test_{pk}.csv"'

    writer = csv.writer(http_response)

    # Metadata header (2 rows)
    writer.writerow(['test_id', 'doctor_id', 'age', 'language', 'voice_settings',
                     'status', 'date_created', 'date_completed'])
    writer.writerow([
        test.test_id, test.doctor_id, test.age, test.language,
        test.voice_settings, test.status, test.date_created, test.date_completed,
    ])
    writer.writerow([])  # blank separator

    # Per-response data
    writer.writerow([
        'stimulus_id', 'stimulus_type', 'span', 'sequence', 'order_index',
        'response_id', 'clicked_symbol', 'click_order', 'latency_ms',
        'is_correct',
    ])
    for stimulus in test.stimuli.order_by('order_index'):
        for resp in stimulus.responses.order_by('click_order'):
            writer.writerow([
                stimulus.stimulus_id, stimulus.stimulus_type, stimulus.span,
                stimulus.sequence, stimulus.order_index,
                resp.response_id, resp.clicked_symbol, resp.click_order,
                resp.latency_ms, resp.is_correct
            ])

    return http_response


# ── 3. Excel export for a single completed test ─────────────────────────────────

@api_view(['GET'])
def export_excel_view(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except Test.DoesNotExist:
        return DRFResponse({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

    if test.status != 'completed':
        return DRFResponse({'error': 'Cannot create spreadsheet, test is incomplete.'}, status=status.HTTP_400_BAD_REQUEST)

    from openpyxl import Workbook
    from openpyxl.styles import NamedStyle, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = f'Test {pk} Data'

    date_style = NamedStyle(name='datetime', number_format='YYYY-MM-DD HH:MM:SS')

    def autofit(worksheet):
        for col in worksheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                except:
                    pass
            worksheet.column_dimensions[col_letter].width = min(max_len + 4, 40)

    # ── Test Information ──
    ws.append(['Test Information'])
    ws.append(['test_id', 'doctor_id', 'age', 'language', 'voice_settings', 'status', 'date_created', 'date_completed'])
    ws.append([
        test.test_id,
        test.doctor_id,
        test.age,
        test.language,
        test.voice_settings,
        test.status,
        test.date_created.replace(tzinfo=None) if test.date_created else None,
        test.date_completed.replace(tzinfo=None) if test.date_completed else None,
    ])
    ws['G3'].style = date_style
    ws['H3'].style = date_style

    # ── Test Data Summary ──
    ws.append([])
    ws.append(['Test Data Summary'])
    try:
        test_data = test.test_data
    except Test_Data.DoesNotExist:
        test_data = None
    if test_data:
        ws.append([
            'test_data_id', 'date_completed', 'num_total_latency', 'mix_total_latency',
            'avg_num_latency', 'avg_mix_latency', 'avg_overall_latency',
            'numeric_correct', 'mixed_correct', 'numeric_total_stimuli', 'mixed_total_stimuli'
        ])
        ws.append([
            test_data.test_data_id,
            test_data.date_completed.replace(tzinfo=None) if test_data.date_completed else None,
            test_data.num_total_latency,
            test_data.mix_total_latency,
            test_data.avg_num_latency,
            test_data.avg_mix_latency,
            test_data.avg_overall_latency,
            test_data.numeric_correct,
            test_data.mixed_correct,
            test_data.numeric_total_stimuli,
            test_data.mixed_total_stimuli,
        ])
        ws[f'B{ws.max_row}'].style = date_style

    # ── Stimulus Data ──
    ws.append([])
    ws.append(['Stimulus Data'])
    ws.append(['stimulus_id', 'sequence', 'stimulus_type', 'span', 'order_index', 'over_pressed'])
    for stimulus in test.stimuli.order_by('order_index'):
        ws.append([
            stimulus.stimulus_id,
            stimulus.sequence,
            stimulus.stimulus_type,
            stimulus.span,
            stimulus.order_index,
            stimulus.over_pressed,
        ])

    # ── Response Data ──
    ws.append([])
    ws.append(['Response Data'])
    ws.append([
        'response_id', 'stimulus_id', 'correct_symbol', 'clicked_symbol',
        'click_order', 'latency_ms', 'is_correct'
    ])
    for stimulus in test.stimuli.order_by('order_index'):
        correct_sequence = stimulus.sequence.split(' ')
        for response in stimulus.responses.order_by('click_order'):
            correct_char = correct_sequence[response.click_order - 1] if response.click_order - 1 < len(correct_sequence) else None
            ws.append([
                response.response_id,
                response.stimulus_id,
                correct_char,
                response.clicked_symbol,
                response.click_order,
                response.latency_ms,
                response.is_correct,
            ])

    autofit(ws)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="test_{pk}_data.xlsx"'
    wb.save(response)
    return response


# ── 4. List all completed tests available for CSV export ──────────────────────

@api_view(['GET'])
def available_csvs_view(request):
    tests = (
        Test.objects.filter(status='completed')
        .order_by('-date_completed')
        .values('test_id', 'doctor_id', 'age', 'language', 'date_created', 'date_completed')
    )
    data = [
        {**t, 'export_url': f'/api/tests/{t["test_id"]}/export-csv/'}
        for t in tests
    ]
    return DRFResponse(data)


# ─── 4. ViewSets for API endpoints ──────────────────────────────────

class TestViewSet(viewsets.ModelViewSet):
    """ViewSet for Test model providing CRUD operations."""
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    @action(detail=True, methods=['post'])
    def start_test(self, request, pk=None):
        """Custom action to start a test session."""
        test = self.get_object()
        if test.status != 'pending':
            return DRFResponse({'error': 'Test cannot be started. Current status: {}'
                             .format(test.status)}, status=400)
        
        test.status = 'in_progress'
        test.save()
        return DRFResponse({'status': 'started'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Custom action to complete a test session."""
        test = self.get_object()
        if test.status != 'in_progress':
            return DRFResponse({'error': 'Test cannot be completed. Current status: {}'
                             .format(test.status)}, status=400)
        
        data = request.data
        num_total_latency = data.get('num_total_latency')
        mix_total_latency = data.get('mix_total_latency')
        num_correct = data.get('num_correct')
        mix_correct = data.get('mix_correct')
        numeric_total_stimuli = data.get('numeric_total_stimuli', num_correct)
        mixed_total_stimuli = data.get('mixed_total_stimuli', mix_correct)
        trial_response_log = data.get('trial_response_log', [])
        
        if any(x is None for x in [num_total_latency, mix_total_latency, num_correct, mix_correct]):
            return DRFResponse({'error': 'Missing required test data fields'}, status=400)

        overall_total_stimuli = int(numeric_total_stimuli) + int(mixed_total_stimuli)
        avg_num_latency = (float(num_total_latency) / int(numeric_total_stimuli)) if int(numeric_total_stimuli) else 0
        avg_mix_latency = (float(mix_total_latency) / int(mixed_total_stimuli)) if int(mixed_total_stimuli) else 0
        avg_overall_latency = ((float(num_total_latency) + float(mix_total_latency)) / overall_total_stimuli) if overall_total_stimuli else 0

        completed_at = timezone.now()
        Test_Data.objects.update_or_create(
            test=test,
            defaults={
                'date_completed': completed_at,
                'num_total_latency': num_total_latency,
                'mix_total_latency': mix_total_latency,
                'avg_num_latency': avg_num_latency,
                'avg_mix_latency': avg_mix_latency,
                'avg_overall_latency': avg_overall_latency,
                'numeric_correct': num_correct,
                'mixed_correct': mix_correct,
                'numeric_total_stimuli': numeric_total_stimuli,
                'mixed_total_stimuli': mixed_total_stimuli,
                'trial_response_log': trial_response_log,
            },
        )

        test.status = 'completed'
        test.date_completed = completed_at
        test.save(update_fields=['status', 'date_completed'])
        return DRFResponse({'status': 'completed'})


class TestDataViewSet(viewsets.ModelViewSet):
    """ViewSet for Test_Data model providing CRUD operations."""
    queryset = Test_Data.objects.all()
    serializer_class = TestDataSerializer


@api_view(['GET'])
def test_data_summary(request):
    """API view to get summary statistics for all test data."""
    total_tests = Test_Data.objects.count()
    avg_numeric_correct = Test_Data.objects.aggregate(models.Avg('numeric_correct'))['numeric_correct__avg'] or 0
    avg_mixed_correct = Test_Data.objects.aggregate(models.Avg('mixed_correct'))['mixed_correct__avg'] or 0
    avg_total_latency = Test_Data.objects.aggregate(
        total_latency=models.Avg(models.F('mix_total_latency') + models.F('num_total_latency'))
    )['total_latency'] or 0

    data = {
        'total_tests': total_tests,
        'avg_numeric_correct': round(avg_numeric_correct, 2),
        'avg_mixed_correct': round(avg_mixed_correct, 2),
        'avg_total_latency': round(avg_total_latency, 2),
    }
    return DRFResponse(data)

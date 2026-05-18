"""Views for the testapp app."""

# Create your views here.
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from api.models import Stimulus, Test, Test_Data, Response
 
def _resolve_lang(request, test):
    param = request.GET.get('lang', '').strip().lower()
    return param if param in ('en', 'es') else test.language.lower()

def test_intro(request, link):
    test = get_object_or_404(Test, link=link)
    lang = _resolve_lang(request, test)
    context = {'lang': lang, 'link': test.link}
    return render(request, 'testapp/intro.html', context)

def tutorial(request, link):
    test = get_object_or_404(Test, link=link)
    lang = _resolve_lang(request, test)
    context = {'lang': lang, 'link': test.link}
    return render(request, 'testapp/tutorial.html', context)

def test_instructions(request, link):
    test = get_object_or_404(Test, link=link)
    lang = _resolve_lang(request, test)
    context = {'lang': lang, 'link': test.link}
    return render(request, 'testapp/instructions.html', context)

def test_keypad(request, link):
    test = get_object_or_404(Test, link=link)
    lang = _resolve_lang(request, test)
    sequences = Stimulus.objects.filter(test=test).order_by('order_index')
    stimuli_list = [
        {
            'sequence': s.sequence.split(' '),
            'stimulus_type': s.stimulus_type,
            'span': s.span,
            'order_index': s.order_index,
        }
        for s in sequences
    ]

    context = {'lang': lang, 'link': test.link, 'stimuli_json': json.dumps(stimuli_list)}
    return render (request, 'testapp/test_keypad.html', context)

def test_submit(request, link):
    test = get_object_or_404(Test, link=link)

    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')

            trial_details = payload.get('trial_details') or []
            if trial_details and not isinstance(trial_details, list):
                raise ValueError('trial_details must be a list.')

            def as_int(name):
                value = payload.get(name)
                if value is None:
                    raise ValueError(f'Missing field: {name}')
                return int(value)

            if trial_details:
                scored_trials = [t for t in trial_details if not t.get('is_practice', False)]
                numeric_trials = [t for t in scored_trials if t.get('kind') == 'numeric']
                mixed_trials = [t for t in scored_trials if t.get('kind') == 'mixed']

                def latency_for(trial):
                    return int(trial.get('latency_ms', 0) or 0)

                num_total_latency = sum(latency_for(t) for t in numeric_trials)
                mix_total_latency = sum(latency_for(t) for t in mixed_trials)
                num_correct = sum(1 for t in numeric_trials if bool(t.get('is_correct')))
                mix_correct = sum(1 for t in mixed_trials if bool(t.get('is_correct')))
                numeric_total_stimuli = len(numeric_trials)
                mixed_total_stimuli = len(mixed_trials)
            else:
                num_total_latency = as_int('num_total_latency')
                mix_total_latency = as_int('mix_total_latency')
                num_correct = as_int('num_correct')
                mix_correct = as_int('mix_correct')
                numeric_total_stimuli = int(payload.get('numeric_total_stimuli', num_correct))
                mixed_total_stimuli = int(payload.get('mixed_total_stimuli', mix_correct))

            overall_total_stimuli = numeric_total_stimuli + mixed_total_stimuli
            avg_num_latency = (num_total_latency / numeric_total_stimuli) if numeric_total_stimuli else 0
            avg_mix_latency = (mix_total_latency / mixed_total_stimuli) if mixed_total_stimuli else 0
            avg_overall_latency = ((num_total_latency + mix_total_latency) / overall_total_stimuli) if overall_total_stimuli else 0

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
                    'trial_response_log': trial_details,
                },
            )

            # Create Response instances and update over_pressed on Stimulus
            stimuli = list(Stimulus.objects.filter(test=test).order_by('order_index'))
            real_trial_index = 0

            for trial in trial_details:
                if trial.get('is_practice'):
                    continue
                
                if real_trial_index >= len(stimuli):
                    break
                
                stimulus = stimuli[real_trial_index]
                clicked_sequence = trial.get('clicked_sequence', [])
                
                # Set over_pressed
                stimulus.over_pressed = len(clicked_sequence) > stimulus.span
                stimulus.save(update_fields=['over_pressed'])
                
                # Create Response instances
                for click in trial.get('click_comparisons', []):
                    clicked_char = click.get('clicked_char')
                    if clicked_char is None:
                        continue
                    Response.objects.create(
                        stimulus=stimulus,
                        clicked_symbol=clicked_char,
                        click_order=click.get('click_order'),
                        latency_ms=click.get('latency_since_previous_click_ms') or 0,
                        is_correct=click.get('is_correct', False),
                        timestamp=completed_at,
                    )
                
                real_trial_index += 1

            test.status = 'completed'
            test.date_completed = completed_at
            test.save(update_fields=['status', 'date_completed'])

            return JsonResponse({'success': True, 'message': 'Test data saved.'})
        except (ValueError, TypeError) as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON payload.'}, status=400)

    lang = _resolve_lang(request, test)
    context = {'lang': lang, 'link': test.link}
    return render(request, 'testapp/test_keypad.html', context)

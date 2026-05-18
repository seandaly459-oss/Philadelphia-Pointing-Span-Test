import random
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Doctor, Test, Test_Data, Stimulus, Response

DIGITS = '0123456789'
LETTERS = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
LANGUAGES = ['en', 'es']
VOICE_OPTIONS = ['default', 'female', 'male']

# A full test always produces exactly 12 stimuli:
#   - 3× digit  span-4  (order 0–2)
#   - 3× digit  span-5  (order 3–5)
#   - 3× mixed  span-4  (order 6–8)
#   - 3× mixed  span-5  (order 9–11)
FULL_TEST_PLAN = [
    ('test_digits', 4),
    ('test_digits', 4),
    ('test_digits', 4),
    ('test_digits', 5),
    ('test_digits', 5),
    ('test_digits', 5),
    ('test_mixed',  4),
    ('test_mixed',  4),
    ('test_mixed',  4),
    ('test_mixed',  5),
    ('test_mixed',  5),
    ('test_mixed',  5),
]


def generate_sequence(stimulus_type, span):
    if stimulus_type == 'test_mixed':
        half = span // 2
        symbols = random.sample(DIGITS, half) + random.sample(LETTERS, span - half)
        random.shuffle(symbols)
        return ' '.join(symbols)
    return ' '.join(random.choices(DIGITS, k=span))


class Command(BaseCommand):
    help = 'Seed realistic fake completed Test, Test_Data, and Stimulus rows for the dashboard.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of fake completed tests to create.',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing Test/Test_Data/Stimulus rows before seeding.',
        )
        parser.add_argument(
            '--doctor-id',
            type=int,
            default=None,
            help='Primary key of the Doctor to assign tests to. Defaults to the first doctor found.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Test_Data.objects.all().delete()
            Stimulus.objects.all().delete()
            Response.objects.all().delete()
            Test.objects.all().delete()
            self.stdout.write(self.style.WARNING('Deleted existing Test, Test_Data, and Stimulus rows.'))

        doctor_id = options['doctor_id']
        if doctor_id is not None:
            try:
                doctor = Doctor.objects.get(pk=doctor_id)
                self.stdout.write(self.style.SUCCESS(f'Using Doctor {doctor.username} (pk={doctor.pk}).'))
            except Doctor.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'No Doctor found with pk={doctor_id}. Aborting.'))
                return
        else:
            doctor = Doctor.objects.first()
            if not doctor:
                doctor = Doctor.objects.create(
                    email='demo_doctor@example.com',
                    username='demo_doctor',
                    password='DemoPassword123!'
                )
                self.stdout.write(self.style.SUCCESS(f'Created demo Doctor {doctor.username}.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Using first Doctor found: {doctor.username} (pk={doctor.pk}).'))

        created = 0
        now = timezone.now()

        for index in range(options['count']):
            date_created = now - timezone.timedelta(
                days=random.randint(1, 45),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            date_completed = date_created + timezone.timedelta(minutes=random.randint(20, 75))

            test = Test.objects.create(
                doctor=doctor,
                link=str(uuid.uuid4()),
                age=random.randint(12, 80),
                language=random.choice(LANGUAGES),
                voice_settings=random.choice(VOICE_OPTIONS),
                patient_email=f'patient{index + 1}@example.com',
                email_sent=True,
                date_created=date_created,
                date_completed=date_completed,
                status='completed',
            )

            # Create all 12 stimuli that make up a full test
            for order_index, (stimulus_type, span) in enumerate(FULL_TEST_PLAN):
                Stimulus.objects.create(
                    test=test,
                    sequence=generate_sequence(stimulus_type, span),
                    stimulus_type=stimulus_type,
                    span=span,
                    order_index=order_index,
                )

            # Create responses — one per symbol in each stimulus sequence,
            # simulating the patient attempting to recall every item.
            for stimulus in test.stimuli.all():
                sequence_symbols = stimulus.sequence.split()  # e.g. ['9', '1', '6', '4']
                elapsed_ms = 0
                for click_order, expected_symbol in enumerate(sequence_symbols, start=1):
                    latency_ms = random.randint(200, 2000)
                    elapsed_ms += latency_ms
                    # Occasionally the patient clicks the wrong symbol
                    clicked = expected_symbol if random.random() > 0.25 else random.choice(sequence_symbols)
                    Response.objects.create(
                        stimulus=stimulus,
                        clicked_symbol=clicked,
                        click_order=click_order,
                        latency_ms=latency_ms,
                        is_correct=(clicked == expected_symbol),
                        timestamp=date_completed - timezone.timedelta(
                            seconds=random.randint(10, 300)
                        ),
                    )

            # 6 digit stimuli, 6 mixed stimuli
            numeric_correct = random.randint(0, 6)
            mixed_correct = random.randint(0, 6)

            num_total_latency = random.randint(1200, 3600)
            mix_total_latency = random.randint(1600, 4200)
            overall_total = num_total_latency + mix_total_latency
            total_stimuli = 12  # always 12 for a full test

            Test_Data.objects.create(
                test=test,
                date_completed=date_completed,
                num_total_latency=num_total_latency,
                mix_total_latency=mix_total_latency,
                avg_num_latency=(num_total_latency / 6),
                avg_mix_latency=(mix_total_latency / 6),
                avg_overall_latency=overall_total / total_stimuli,
                numeric_correct=numeric_correct,
                mixed_correct=mixed_correct,
                numeric_total_stimuli=6,
                mixed_total_stimuli=6,
                trial_response_log=[
                    {
                        'stimulus_type': stype,
                        'span': span,
                        'correct': random.choice([True, False]),
                        'latency_ms': random.randint(200, 1200),
                    }
                    for stype, span in FULL_TEST_PLAN
                ],
            )

            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created Test {test.test_id}: patient{index + 1}@example.com'))

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created} fake completed tests.'))
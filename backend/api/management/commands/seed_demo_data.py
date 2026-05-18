import random
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Doctor, Test, Test_Data, Stimulus, Response

LANGUAGES = ["en", "es"]
VOICE_OPTIONS = ["default", "female", "male", "neutral"]
STATUS_CHOICES = ["pending", "completed"]
STIMULUS_PLAN = ["digit", "mixed", "practice_digit", "practice_mixed"]
DIGIT_CHARS = "0123456789"
LETTER_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def generate_sequence(stimulus_type, span):
    if stimulus_type in ("digit", "practice_digit"):
        return "".join(random.choices(DIGIT_CHARS, k=span))

    symbol_set = random.choices(DIGIT_CHARS, k=span // 2) + random.choices(LETTER_CHARS, k=span - span // 2)
    random.shuffle(symbol_set)
    return "".join(symbol_set)


def generate_latency_ms(age, stimulus_type, is_correct, click_order):
    """Generate realistic response latency with age trend and trial-level noise."""
    age = age or 30
    age_delta = max(age - 18, 0)

    # Baseline grows with age so charted averages show an upward trend.
    baseline = 450 + (age_delta * 18)

    if stimulus_type in ("mixed", "practice_mixed"):
        baseline += 120
    if click_order > 2:
        baseline += 20
    if not is_correct:
        baseline += 90

    noisy = int(random.gauss(baseline, 110))
    return max(220, min(noisy, 3200))


class Command(BaseCommand):
    help = "Seed demo records for Doctor, Test, Test_Data, Stimulus, and Response."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing Doctor/Test/Test_Data/Stimulus/Response records before seeding.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of tests to generate (recommended 500-1000 for dashboard stress testing).",
        )
        parser.add_argument(
            "--pending-ratio",
            type=float,
            default=0.4,
            help="Fraction of tests marked pending (0.0 to 1.0).",
        )

    def handle(self, *args, **options):
        count = options["count"]
        pending_ratio = options["pending_ratio"]

        if count < 1:
            self.stdout.write(self.style.ERROR("--count must be at least 1."))
            return
        if pending_ratio < 0 or pending_ratio > 1:
            self.stdout.write(self.style.ERROR("--pending-ratio must be between 0.0 and 1.0."))
            return

        if options["clear"]:
            Response.objects.all().delete()
            Stimulus.objects.all().delete()
            Test_Data.objects.all().delete()
            Test.objects.all().delete()
            Doctor.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing demo data."))

        doctors = []
        doctor_count = min(max(count // 10, 5), 100)
        for i in range(doctor_count):
            doctor = Doctor.objects.create(
                email=f"demo{i+1}@ppst-demo.com",
                username=f"demo_doctor_{i+1}",
                password_hash="!"  # placeholder hash, not valid for login
            )
            doctors.append(doctor)

        completed_count = 0
        pending_count = 0

        for i in range(count):
            doctor = random.choice(doctors)
            status = "pending" if random.random() < pending_ratio else "completed"
            date_created = timezone.now() - timezone.timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
            date_completed = date_created + timezone.timedelta(minutes=random.randint(15, 60)) if status == "completed" else None

            test = Test.objects.create(
                doctor=doctor,
                link=str(uuid.uuid4()),
                age=random.randint(18, 80),
                language=random.choice(LANGUAGES),
                voice_settings=random.choice(VOICE_OPTIONS),
                date_created=date_created,
                date_completed=date_completed,
                status=status,
            )

            if status == "completed":
                completed_count += 1
                Test_Data.objects.create(
                    test=test,
                    date_completed=date_completed,
                    num_total_latency=random.randint(1200, 4200),
                    mix_total_latency=random.randint(1400, 4800),
                    numeric_correct=random.randint(5, 10),
                    mixed_correct=random.randint(5, 10),
                )
            else:
                pending_count += 1
                Test_Data.objects.create(
                    test=test,
                    date_completed=timezone.now(),
                    num_total_latency=random.randint(1200, 4200),
                    mix_total_latency=random.randint(1400, 4800),
                    numeric_correct=random.randint(0, 10),
                    mixed_correct=random.randint(0, 10),
                )

            stim_count = random.randint(6, 12)
            for order_index in range(stim_count):
                stimulus_type = random.choice(STIMULUS_PLAN)
                span = random.choice([4, 5])
                sequence = generate_sequence(stimulus_type, span)

                stimulus = Stimulus.objects.create(
                    test=test,
                    sequence=sequence,
                    stimulus_type=stimulus_type,
                    span=span,
                    order_index=order_index,
                )

                for click_order, symbol in enumerate(sequence):
                    is_correct = random.random() < 0.8
                    clicked_symbol = symbol if is_correct else random.choice((DIGIT_CHARS + LETTER_CHARS).replace(symbol, ""))
                    Response.objects.create(
                        stimulus=stimulus,
                        clicked_symbol=clicked_symbol,
                        click_order=click_order,
                        latency_ms=generate_latency_ms(test.age, stimulus_type, is_correct, click_order),
                        is_correct=is_correct,
                        timestamp=date_created + timezone.timedelta(seconds=random.randint(5, 300)),
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {doctor_count} doctors, {count} tests ({completed_count} completed / {pending_count} pending), "
            f"{Stimulus.objects.count()} total stimuli, and {Response.objects.count()} total responses."
        ))

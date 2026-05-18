"""
Management command to seed fake Stimulus and Response data for development/testing.

Usage:
    python manage.py seed_stimuli_responses
    python manage.py seed_stimuli_responses --clear
"""

import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Doctor, Test, Stimulus, Response

DIGIT_CHARS = "0123456789"
LETTER_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def generate_sequence(stimulus_type, span):
    if stimulus_type in ("digit", "practice_digit"):
        return "".join(random.choices(DIGIT_CHARS, k=span))
    else:
        digits = random.choices(DIGIT_CHARS, k=span // 2)
        letters = random.choices(LETTER_CHARS, k=span - span // 2)
        combo = digits + letters
        random.shuffle(combo)
        return "".join(combo)


class Command(BaseCommand):
    help = "Seed fake Stimulus and Response data linked to existing Test records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing Stimulus and Response records before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Response.objects.all().delete()
            Stimulus.objects.all().delete()
            Test.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing data."))

        # Create a fake doctor if none exists
        doctor, _ = Doctor.objects.get_or_create(
            username="demo_doctor",
            defaults={"email": "demo@ppst.com", "password_hash": "!"},
        )

        # Create 3 fake tests
        for i in range(3):
            test = Test.objects.create(
                doctor=doctor,
                link=f"demo-link-{i}-{random.randint(1000,9999)}",
                age=random.randint(18, 80),
                language="EN",
                voice_settings="default",
                status="completed",
                date_completed=timezone.now(),
            )

            stimulus_plan = [
                ("practice_digit", 4),
                ("practice_digit", 4),
                ("practice_mixed", 4),
                ("practice_mixed", 4),
                ("digit", 4),
                ("digit", 5),
                ("digit", 5),
                ("mixed", 4),
                ("mixed", 5),
                ("mixed", 5),
            ]

            random.shuffle(stimulus_plan)

            for order_index, (stimulus_type, span) in enumerate(stimulus_plan):
                sequence = generate_sequence(stimulus_type, span)

                stimulus = Stimulus.objects.create(
                    test=test,
                    sequence=sequence,
                    stimulus_type=stimulus_type,
                    span=span,
                    order_index=order_index,
                )

                for click_order, symbol in enumerate(sequence):
                    is_correct = random.random() < 0.80
                    clicked = symbol if is_correct else random.choice(
                        list((DIGIT_CHARS + LETTER_CHARS).replace(symbol, ""))
                    )

                    Response.objects.create(
                        stimulus=stimulus,
                        clicked_symbol=clicked,
                        click_order=click_order,
                        latency_ms=random.randint(300, 2000),
                        is_correct=is_correct,
                        timestamp=timezone.now(),
                    )

        self.stdout.write(self.style.SUCCESS("Seeded 3 tests with stimuli and responses successfully."))

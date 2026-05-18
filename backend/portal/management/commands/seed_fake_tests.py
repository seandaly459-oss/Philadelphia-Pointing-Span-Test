import random
import uuid

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Doctor, Test


LANGUAGES = ['en', 'es']
STATUSES = ['pending', 'completed', 'in_progress']
VOICE_SETTINGS = ['default', 'male', 'female']


class Command(BaseCommand):
    help = 'Seed the database with fake Test objects spread across repeated doctors and mixed statuses.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of Test objects to create. Defaults to 30.',
        )
        parser.add_argument(
            '--doctor-count',
            type=int,
            default=4,
            help='Number of doctors to spread the tests across. Defaults to 4.',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing Test rows before seeding.',
        )
        parser.add_argument(
            '--seed',
            type=int,
            default=None,
            help='Optional random seed for reproducible test data.',
        )

    def handle(self, *args, **options):
        count = max(options['count'], 1)
        doctor_count = max(options['doctor_count'], 1)
        random_seed = options['seed']
        now = timezone.now()

        if random_seed is not None:
            random.seed(random_seed)

        if options['clear']:
            deleted_count, _ = Test.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing Test rows.'))

        doctors = self._get_or_create_doctors(doctor_count)
        doctor_pool = self._build_doctor_pool(doctors, count)
        status_pool = self._build_status_pool(count)

        created_tests = []
        for index in range(count):
            doctor = doctor_pool[index]
            status = status_pool[index]
            date_created = now - timezone.timedelta(
                days=random.randint(0, 60),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            date_completed = None
            if status == 'completed':
                date_completed = date_created + timezone.timedelta(
                    days=random.randint(0, 7),
                    minutes=random.randint(20, 180),
                )

            patient_email = f'patient{index + 1}@example.com' if index % 5 != 0 else None
            email_sent = bool(patient_email and status != 'pending')

            test = Test.objects.create(
                doctor=doctor,
                link=f'seed-test-{uuid.uuid4()}',
                age=random.randint(18, 80),
                language=random.choice(LANGUAGES),
                voice_settings=random.choice(VOICE_SETTINGS),
                patient_email=patient_email,
                email_sent=email_sent,
                status=status,
            )
            Test.objects.filter(pk=test.pk).update(
                date_created=date_created,
                date_completed=date_completed,
            )

            created_tests.append(test)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created Test {test.test_id} for doctor {doctor.username} ({status})'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {len(created_tests)} Test objects across {len(doctors)} doctors.'
            )
        )

    def _get_or_create_doctors(self, doctor_count):
        doctors = []
        for index in range(doctor_count):
            doctor, created = Doctor.objects.get_or_create(
                username=f'seed_doctor_{index + 1}',
                defaults={
                    'email': f'seed_doctor_{index + 1}@ppst.local',
                    'password_hash': '!',
                },
            )
            doctors.append(doctor)

            if created:
                self.stdout.write(self.style.WARNING(f'Created doctor {doctor.username}.'))

        return doctors

    def _build_doctor_pool(self, doctors, count):
        weighted_doctors = []
        remaining = count
        for index, doctor in enumerate(doctors):
            slots_left = len(doctors) - index
            share = max(1, remaining // slots_left)
            if index == 0:
                share = max(share, count // 3)
            elif index == 1 and count > 3:
                share = max(share, count // 4)

            share = min(share, remaining)
            weighted_doctors.extend([doctor] * share)
            remaining -= share

        while len(weighted_doctors) < count:
            weighted_doctors.append(random.choice(doctors))

        random.shuffle(weighted_doctors)
        return weighted_doctors[:count]

    def _build_status_pool(self, count):
        completed_count = max(1, count // 3)
        in_progress_count = max(1, count // 4)
        pending_count = max(count - completed_count - in_progress_count, 0)

        status_pool = (
            ['completed'] * completed_count
            + ['in_progress'] * in_progress_count
            + ['pending'] * pending_count
        )

        while len(status_pool) < count:
            status_pool.append(random.choice(STATUSES))

        random.shuffle(status_pool)
        return status_pool[:count]

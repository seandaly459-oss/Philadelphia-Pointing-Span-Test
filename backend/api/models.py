import uuid
from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Doctor(models.Model):
    """A doctor account used to manage PPST sessions and view results."""

    doctor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True, default=None)
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password: str) -> None:
        """Hash and store a password for this doctor."""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Validate the given password against the stored hash."""
        return check_password(raw_password, self.password_hash)

    @classmethod
    def create(cls, *, email: str, username: str, password: str) -> "Doctor":
        """Convenience helper to create a doctor with a hashed password."""
        doctor = cls(email=email, username=username)
        doctor.set_password(password)
        doctor.save()
        return doctor

    @classmethod
    def authenticate(cls, *, email_or_username: str, password: str) -> "Doctor | None":
        """Authenticate a doctor by email or username."""
        try:
            doctor = cls.objects.get(models.Q(email__iexact=email_or_username) | models.Q(username__iexact=email_or_username))
        except cls.DoesNotExist:
            return None

        return doctor if doctor.check_password(password) else None


class Test(models.Model):
    """A single anonymous PPST session created by a doctor."""

    test_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    link = models.CharField(max_length=255, unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=10)
    voice_settings = models.CharField(max_length=100)
    patient_email = models.EmailField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Test {self.test_id} (Doctor: {self.doctor_id})"


class Test_Data(models.Model):
    """A model to store summary test data for PPST sessions."""

    test_data_id = models.AutoField(primary_key=True)
    test = models.OneToOneField(Test, on_delete=models.CASCADE)
    date_completed = models.DateTimeField()
    num_total_latency = models.IntegerField()
    mix_total_latency = models.IntegerField()
    avg_num_latency = models.FloatField(default=0)
    avg_mix_latency = models.FloatField(default=0)
    avg_overall_latency = models.FloatField(default=0)
    numeric_correct = models.IntegerField()
    mixed_correct = models.IntegerField()
    numeric_total_stimuli = models.IntegerField(default=0)
    mixed_total_stimuli = models.IntegerField(default=0)
    trial_response_log = models.JSONField(default=list, blank=True)

    @property
    def total_correct(self):
        """Total number of correct answers (numeric + mixed)."""
        return self.numeric_correct + self.mixed_correct

    def __str__(self):
        return f"Test Data {self.test_data_id} for Test {self.test_id}"

    @classmethod
    def create_test_data(cls, test, mix_latency, num_latency, date_completed, numeric_correct, mixed_correct):
        """Convenience method to create a Test_Data instance."""
        numeric_total_stimuli = numeric_correct
        mixed_total_stimuli = mixed_correct
        overall_stimuli = numeric_total_stimuli + mixed_total_stimuli
        avg_num_latency = (num_latency / numeric_total_stimuli) if numeric_total_stimuli else 0
        avg_mix_latency = (mix_latency / mixed_total_stimuli) if mixed_total_stimuli else 0
        avg_overall_latency = ((num_latency + mix_latency) / overall_stimuli) if overall_stimuli else 0

        return cls.objects.create(
            test=test,
            date_completed=date_completed,
            num_total_latency=num_latency,
            mix_total_latency=mix_latency,
            avg_num_latency=avg_num_latency,
            avg_mix_latency=avg_mix_latency,
            avg_overall_latency=avg_overall_latency,
            numeric_correct=numeric_correct,
            mixed_correct=mixed_correct,
            numeric_total_stimuli=numeric_total_stimuli,
            mixed_total_stimuli=mixed_total_stimuli,
        )


class Stimulus(models.Model):
    """A single stimulus presented to a patient during a test."""

    STIMULUS_TYPES = [
        ("digit", "Digit"),
        ("mixed", "Mixed"),
        ("practice_digit", "Practice Digit"),
        ("practice_mixed", "Practice Mixed"),
    ]

    stimulus_id = models.AutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="stimuli")
    sequence = models.CharField(max_length=255)
    stimulus_type = models.CharField(max_length=50, choices=STIMULUS_TYPES)
    span = models.PositiveIntegerField()
    order_index = models.PositiveIntegerField()
    over_pressed = models.BooleanField(default=False)

    def __str__(self):
        return f"Stimulus {self.stimulus_id} [{self.stimulus_type}] span={self.span}"


class Response(models.Model):
    """A single click/response made by a patient for a given stimulus."""

    response_id = models.AutoField(primary_key=True)
    stimulus = models.ForeignKey(Stimulus, on_delete=models.CASCADE, related_name="responses")
    clicked_symbol = models.CharField(max_length=5)
    click_order = models.PositiveIntegerField()
    latency_ms = models.IntegerField()
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Response {self.response_id} (Stimulus {self.stimulus_id}) correct={self.is_correct}"


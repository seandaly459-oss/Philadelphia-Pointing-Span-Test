# PSEUDOCODE
# -------------------------------------------------
# Goal: reflect the ERD structure, NOT perfect syntax.
# Focus: fields, relationships, and why they exist.

class Doctor(models.Model):
    # Primary key for each doctor (Django adds id by default, but we name it for clarity)
    doctor_id = models.AutoField(primary_key=True)
    # Used for login + contact; not related to patients (privacy preserved)
    email = models.EmailField(unique=True)
    # Separate username in case email ever changes
    username = models.CharField(max_length=150, unique=True)
    # Hashed password, never stored in plain text
    password_hash = models.CharField(max_length=255)
    # When this doctor account was created (for auditing / admin)
    date_created = models.DateTimeField(auto_now_add=True)

    # - Only doctor identity is stored, never patient identity.
    # - Supports secure login and future account management.


class Test(models.Model):
    # Unique identifier for a test session
    test_id = models.AutoField(primary_key=True)
    # The doctor who created this test (1 Doctor : M Tests)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    # Anonymous test link token sent to the patient
    link = models.CharField(max_length=255, unique=True)
    # Patient age only – satisfies requirement: "Only the patient's age is provided"
    age = models.PositiveIntegerField()
    # Language of the interface (e.g., 'EN', 'ES')
    language = models.CharField(max_length=10)
    # Voice configuration chosen for auditory stimuli
    voice_settings = models.CharField(max_length=100)
    # When the test was created (for dashboard stats)
    date_created = models.DateTimeField(auto_now_add=True)
    # High-level state of the test: pending, in_progress, completed
    status = models.CharField(max_length=20)

    # - Represents a single anonymous PPST session.
    # - Stores only age, language, voice, and timing—no identifying patient data.
    # - Link is the bridge between doctor and anonymous patient.


class TestData(models.Model):
    # One-to-one summary for a completed test
    test_data_id = models.AutoField(primary_key=True)
    # Each Test has at most one TestData record (1 : 1)
    test = models.OneToOneField(Test, on_delete=models.CASCADE)
    # When the test was completed (used for trends over time)
    date_completed = models.DateTimeField()
    # Total latency for numeric-only stimuli
    num_total_latency = models.IntegerField()
    # Total latency for mixed stimuli
    mix_total_latency = models.IntegerField()
    # Number of correct numeric stimuli
    numeric_correct = models.IntegerField()
    # Number of correct mixed stimuli
    mixed_correct = models.IntegerField()

    # - Separates raw click data from summary metrics.
    # - Directly supports spreadsheet export and dashboard statistics.
    # - Keeps the Test table lean while enabling rich analytics.


class Stimulus(models.Model):
    # Unique identifier for each stimulus instance
    stimulus_id = models.AutoField(primary_key=True)
    # The test this stimulus belongs to (1 Test : M Stimuli)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    # The sequence of symbols (digits and/or letters) shown to the patient
    sequence = models.CharField(max_length=255)
    # Type of stimulus: 'digit', 'mixed', 'practice_digit', 'practice_mixed'
    stimulus_type = models.CharField(max_length=50)
    # Span length (4 or 5), matching PPST design
    span = models.PositiveIntegerField()
    # Order of presentation within the test (supports varying order per patient)
    order_index = models.PositiveIntegerField()

    # - Stimuli are tied to a specific test because order may vary per patient.
    # - Span and type encode PPST structure (digit vs mixed, 4 vs 5 span).
    # - Order_index allows reconstruction of the exact test flow.


class Response(models.Model):
    # Unique identifier for each click/response
    response_id = models.AutoField(primary_key=True)
    # The stimulus this response belongs to (1 Stimulus : M Responses)
    stimulus = models.ForeignKey(Stimulus, on_delete=models.CASCADE)
    # Which symbol the patient clicked (digit or letter)
    clicked_symbol = models.CharField(max_length=5)
    # The order of this click within the stimulus (1st, 2nd, 3rd, etc.)
    click_order = models.PositiveIntegerField()
    # Latency in milliseconds from stimulus onset or previous click
    latency_ms = models.IntegerField()
    # Whether this click was correct according to PPST rules
    is_correct = models.BooleanField()
    # Timestamp of when the click occurred (for fine-grained timing analysis)
    timestamp = models.DateTimeField()

    # - Captures raw behavioral data: timing + correctness per click.
    # - Enables computation of latencies and accuracy required by the spec.
    # - Keeps the model flexible for future analyses (e.g., sequence patterns).
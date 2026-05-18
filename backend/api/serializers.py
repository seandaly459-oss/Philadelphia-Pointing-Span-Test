from rest_framework import serializers
from .models import Doctor, Test, Test_Data, Stimulus, Response


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = '__all__'


class StimulusSerializer(serializers.ModelSerializer):
    responses = ResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Stimulus
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    stimuli = StimulusSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        exclude = ['password_hash']


class TestDataSerializer(serializers.ModelSerializer):
    total_correct = serializers.ReadOnlyField()
    total_latency = serializers.ReadOnlyField()

    class Meta:
        model = Test_Data
        fields = '__all__'

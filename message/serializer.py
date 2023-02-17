from rest_framework import serializers
from .models import MeterCheck

class MeterCheckSerializer(serializers.ModelSerializer):
	class Meta:
		model = MeterCheck
		fields = '__all__'
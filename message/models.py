from django.db import models

# Create your models here.
class MeterCheck(models.Model):
	meter_id = models.CharField(max_length=20, blank=True)
	gas_level = models.CharField(max_length=10, blank=True)
	message_status = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '{} {}'.format(self.meter_id, self.message_status)

	class Meta:
		ordering = ['-date_created']
from django.urls import path
from . import views

urlpatterns = [
	path('meter-reading/<str:meter_id>', views.meter_view, name='meter-view'),
	path('gaslevel-notification/<str:meter_id>', views.gas_usage_alert, name='alert'),
	path('checkmeter-status/<str:pk>', views.MessageStatusDetail.as_view(), name='check-meter-status')
	#path('checkmeter-status/<str:meter_id>', views.check_meter_status, name='check-meter'),
]
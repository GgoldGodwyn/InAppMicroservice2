from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MeterCheck
from .serializer import MeterCheckSerializer
from django.core import serializers
from django.http import HttpResponse
from rest_framework.parsers import JSONParser
import requests
import json
import datetime

# Get current time
current_time = datetime.datetime.now()

# Create your views here.
@api_view(['GET'])
def meter_view(request, meter_id):
	"""
		GET THE LAST READING FOR A PARTICULAR METER
	"""
	#req = requests.get(f'https://fornewhft.herokuapp.com/api/allmeterreadings/{meter_id}')
	req = requests.get(f'https://fornewhft.herokuapp.com/api/getreading/{meter_id}')
	data = json.loads(req.content)
	if request.method == 'GET':
		try:
			#last_data = data[0] # use this if the right reading is allmeterreadings 
			last_data = data
			get_meter = last_data['meter']
			gas_supplied = last_data['quantity_supplied']
			gas_level = last_data['quantity_remaining']

			#print(f'requested meter==>{last_data}')
			print(f"For meter {get_meter}, quantity_supplied:quantity_remaining ==> {gas_supplied}:{gas_level}")
			
			# Store meter details	
			request.session['gas_level'] = gas_level
			request.session['get_meter'] = get_meter

			return Response (last_data)
		except IndexError:
			return Response('Oops! Your request is outta range. Please request for a different meter :)')
	else:
		return ('ONLY A GET REQUEST IS ALLOWED!!!')

@api_view(['GET'])
def gas_usage_alert(request, meter_id):
	"""
	Check for gas level, compare with gas scale and return a custom message & message status. 
	"""
	#req = requests.get(f'https://fornewhft.herokuapp.com/api/allmeterreadings/{meter_id}')
	req = requests.get(f'https://fornewhft.herokuapp.com/api/getreading/{meter_id}')
	data = json.loads(req.content)

	if request.method == 'GET':
		# try:
		#last_data = data[0] # use this if the right reading is allmeterreadings 
		last_data = data
		get_meter = last_data['meter']
		gas_supplied = last_data['quantity_supplied']
		gas_level = last_data['quantity_remaining']
		sdata = {'meter_id':get_meter, "gas_level":gas_level}
		print(f"For meter {get_meter}, quantity_supplied:quantity_remaining ==> {gas_supplied}:{gas_level}")
		print('Incoming type gl', type(gas_level))

		# Save meter data needed!
		saved_meter_readings = MeterCheck.objects.all()
		# if get_meter not in saved_meter_readings:
		gl = float(gas_level)
		meter = MeterCheck.objects.create(meter_id=get_meter, gas_level=gl)
		meter.save()
		
		print('meter saved!', meter)
		meter_x = MeterCheck.objects.get(pk=meter.id)
		print('mmmmeter_x:', meter_x.id)

		#meter_data = JSONParser().parse(request)
		#meter_data = serializers.serialize('json', MeterCheck.objects.get(meter_id))
		meter_serializer = MeterCheckSerializer(data=sdata)
		
		if meter_serializer.is_valid():
			print('first meter_serializer:', meter_serializer.data)
			meter_serializer.save()
			print('meter serializer saved!',meter_serializer.data)
		else:
			print('meter serializer not saved!')
		

		# Get meter data and compare with scale	
		last_meter = MeterCheck.objects.filter(meter_id=meter_id).last()

		gas_level = last_meter.gas_level
		#
		print('comparing meter, id, & type:', last_meter, last_meter.id, type(gas_level))
		gas_level = float(gas_level)
		
		# Gas usage scale
		scale = {
	            'track 1':f'Dear customer, you have {gas_level}kg of gas left. Relax, you are good!', #12kg - 10kg
	            'track 2':f'Dear customer, you have {gas_level}kg of gas left. Keep the fire burning!', #9.99kg - 8kg
	            'track 3':f'Dear customer, you have {gas_level}kg of gas left. We’ve got your back: do the cooking!', #7.99 – 6kg
	            'track 4':f'Dear customer, you have {gas_level}kg of gas left. We are actively monitoring your gas level. Relax!', #5.99 – 4kg
	            'track 5':f'Dear customer, you have {gas_level}kg of gas left. We will contact you for a bottle swap when you get to 2kg!', #3.99kg – 2.1kg
	            'track 6':f'Dear customer, you have {gas_level}kg of gas left. Your gas level is low. You will be contacted for a bottle swap. You are covered!', #<=1.9kg
	            'track 7':f'Dear customer, you have {gas_level}kg of gas left. 12kg of gas has been delivered to you. Go explore your culinary skills!' #12kg
	        }

		 	# Check gas level and return a message
		try:
			if gas_level <= 2:
				res = scale['track 6']
				return Response ({
					'id': meter_x.id,
					'meter':get_meter,
					'last_gas_quantity_used':gas_level,
					'alert message': res,
					'status':last_meter.message_status,
					'time_fetched':current_time
	            })
			elif gas_level > 2 and gas_level <= 3.9:
				res = scale['track 5']
				return Response ({
					'id': meter_x.id,
					'meter':get_meter,
					'last_gas_quantity_used':gas_level,
					'alert message': res,
					'status':last_meter.message_status,
					'time_fetched':current_time
	            })
			elif gas_level >= 4 and gas_level < 6:
				res = scale['track 4']
				return Response ({
					'id': meter_x.id,
					'meter':get_meter,
					'last_gas_quantity_used':gas_level,
					'alert message': res,
					'status':last_meter.message_status,
					'time_fetched':current_time
	            })
			elif gas_level >= 6 and gas_level <= 7.9:
				res = scale['track 3']
				return Response ({
					'id': meter_x.id,
					'meter':get_meter,
					'last_gas_quantity_used':gas_level,
					'alert message': res,
					'status':last_meter.message_status,
					'time_fetched':current_time
	            })
			elif gas_level >= 8 and gas_level <= 9.9:
				res = scale['track 2']
				return Response ({
					'id': meter_x.id,
					'meter':get_meter,
					'last_gas_quantity_used':gas_level,
					'alert message': res,
					'status':last_meter.message_status,
					'time_fetched':current_time
	            })
			elif gas_level >= 10 and gas_level <= 11.9:
				res = scale['track 1']
				return Response ({
					'id': meter_x.id,
					'meter':get_meter,
					'last_gas_quantity_used':gas_level,
					'alert message': res,
					'status':last_meter.message_status,
					'time_fetched':current_time
	            })
			elif gas_level == 12:
				res = scale['track 7']
				return Response ({
					'id': meter_x.id,
					'meter':get_meter,
					'last_gas_quantity_used':gas_level,
					'alert message': res,
					'status':last_meter.message_status,
					'time_fetched':current_time
	            })
		except IndexError:
			print(f'The gas level for the meter fetched is {gas_level}')
			x = TypeError()
			print(x)
			return Response('Meter data not fetched because gas level is None!', status=status.HTTP_204_NO_CONTENT)
	else:
		print('Gas level is Null or Meter not found!')
		return ({
				'message':'Oops! This meter id is not found !!!',
				'status':204
			})


class MessageStatusDetail(generics.RetrieveUpdateAPIView):
	"""
	PUT & DELETE API for the App Version
	"""
	queryset = MeterCheck.objects.all()
	serializer_class = MeterCheckSerializer
		

@api_view(['PUT', 'PATCH'])
def check_meter_status(request, meter_id):
	"""
	GETS A METER ID, CHECK FOR MESSAGE STATUS & UPDATE IT.
	"""
	try:
		meter = MeterCheck.objects.get(meter_id=meter_id)
	except MeterCheck.DoesNotExist:
		print('Meter id not found!')
		return Response('Meter id not found!', status=status.HTTP_404_NOT_FOUND)

	if request.method == 'PUT' or request.method == 'PATCH':
		#meter_data = JSONParser().parse(request)
		meter_serializer = MeterCheckSerializer(meter, data=request.data)
		if meter_serializer.is_valid():
			meter_serializer.save()
			return Response(meter_serializer.data)
	return Response(meter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

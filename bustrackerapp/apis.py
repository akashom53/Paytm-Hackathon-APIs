import json as JsonModule
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from models import BUS, User, BusStop, Transaction
import requests
import math
from PrintUtils import color


# Internal Logic---------------------------------------------------------------------------------

def hitApi(url):
	print("Hittin API: "+url)
	req = requests.get(url)
	return req.json()

def fetchDistance(srcLat, srcLon, dstLat, dstLon):
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={cur_lat},{cur_lon}&destinations={next_lat},{next_lon}&key=AIzaSyAYXwOto9wStCVDTRxv0_6Kn9o2VlAf0OM".format(cur_lat=srcLat, cur_lon=srcLon, next_lat=dstLat, next_lon=dstLon)
	json = hitApi(url)
	print("Response: {0}".format(json))
	return json['rows'][0]['elements'][0]['distance']['value']


def distance(lat1, lon1, lat2, lon2): 
		R=6371000                               # radius of Earth in meters
		phi_1=math.radians(lat1)
		phi_2=math.radians(lat2)
		delta_phi=math.radians(lat2-lat1)
		delta_lambda=math.radians(lon2-lon1)
		a= math.sin(delta_phi/2.0)**2+math.cos(phi_1)*math.cos(phi_2)*math.sin(delta_lambda/2.0)**2
		c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
		meters=R*c                             # output distance in meters
		return meters


#------------------------------------------------------------------------------------------------

@csrf_exempt 
def testjson(request):


	response_data = {}
	response_data['result'] = 'Success'
	response_data['message'] = 'Hello '
	
	return JsonResponse(response_data)

# Bus apis----------------------------------------------------------------------------------------

@csrf_exempt 
def saveBus(request):

	route = request.POST.get("route", "")
	loc = request.POST.get("loc", "")

	b = BUS(bus_route = route, bus_location = loc)
	b.save()


	response_data = {}
	response_data['success'] = True
	response_data['message'] = 'Bus ' + route + " saved!"
	
	return JsonResponse(response_data)


@csrf_exempt 
def getBusData(request):

	busId = request.POST.get("busId", "")

	b = BUS.objects.values().filter(id=busId).get()


	response_data = {}
	response_data['success'] = True
	response_data['data'] = b
	
	return JsonResponse(response_data)


@csrf_exempt 
def getRouteStops(request):

	route = request.POST.get("route", "")

	b = BusStop.objects.values().filter(route=route)


	response_data = {}
	response_data['success'] = True
	response_data['data'] = list(b)
	
	return JsonResponse(response_data)


@csrf_exempt
def getBusList(request):

	buses = BUS.objects.values()

	response_data = {}
	response_data['success'] = True
	response_data['message'] = ''
	response_data['data'] = list(buses)
	
	return JsonResponse(response_data)

@csrf_exempt 
def updateBusLocation(request):

	busId = request.POST.get("bus_id", "")
	lat = request.POST.get("lat", 0)
	lon = request.POST.get("lon", 0)

	print("Update Bus Location API ========================================================")
	print("Bus ID: {0}, Lattitude: {1}, Longitude: {2}".format(busId, lat, lon))

	busQuery = BUS.objects.all().filter(id=busId)

	response_data = {}
	if busQuery.exists():
		response_data['success'] = True
		response_data['message'] = 'Data updated!'
		print("Found bus: "+busQuery.get().bus_route)
	else:
		response_data['success'] = False
		response_data['message'] = 'Invalid bus id'
		print('Invalid bus id')
	
	bus = busQuery.get()
	nextStop = BusStop.objects.all().filter(stop_name=bus.next_stop).get()
	print("Next stop: {0}, Lattitude: {1}, Longitude: {2}".format(bus.next_stop, nextStop.location_lat, nextStop.location_lon))
	distance = fetchDistance(lat, lon, nextStop.location_lat, nextStop.location_lon)
	print("Distance: {0}".format(distance))

	if distance <= 50:
		# arrived at nextStop
		print("Arrived at stop: {0}, Distance: {1}".format(bus.next_stop, distance))
		bus.last_stop = bus.next_stop
		bus.currSeq = nextStop.seq
		nextSeq = 0
		if bus.reverse:
			nextSeq = nextStop.seq - 1
		else:
			nextSeq = nextStop.seq + 1
		nextStopQuery = BusStop.objects.all().filter(route=bus.bus_route, seq=nextSeq)
		if nextStopQuery.exists():
			nextStop = BusStop.objects.all().filter(route=bus.bus_route, seq=nextSeq).get()
		else:
			bus.reverse = not bus.reverse
			if bus.reverse:
				nextSeq = nextStop.seq - 1
			else:
				nextSeq = nextStop.seq + 1
			nextStop = BusStop.objects.all().filter(route=bus.bus_route, seq=nextSeq).get()
		print("New next stop: "+nextStop.stop_name)
		bus.next_stop = nextStop.stop_name

	bus.bus_location_lat = lat
	bus.bus_location_lon = lon
	bus.save()
	print(response_data)
	print("================================================================================")
	return JsonResponse(response_data)

@csrf_exempt
def searchBusStops(request):
	print("Search Bus Stops API ===========================================================")
	lat = float(request.POST.get("lat"))
	lon = float(request.POST.get("lon"))
	busStops = BusStop.objects.values()
	nearestBusStops = list()
	radius = 1000
	for busStop in busStops:
		newDistance = distance(lat, lon, float(busStop['location_lat']), float(busStop['location_lon']))
		print(newDistance)
		if newDistance < float(radius):
			print('Appending')
			nearestBusStops.append(busStop)
	print(nearestBusStops)
	response_data = {}
	response_data['success'] = True
	response_data['data'] = nearestBusStops
	print(response_data)
	print("================================================================================")
	return JsonResponse(response_data)



@csrf_exempt 
def searchBuses(request):
	print("Search Buses API ===============================================================")
	response_data = {}

	srcLat = float(request.POST.get("src_lat", ""))
	srcLon = float(request.POST.get("src_lon", ""))
	dstLat = float(request.POST.get("dst_lat", ""))
	dstLon = float(request.POST.get("dst_lon", ""))
	print("From: ({0}, {1}), To: ({2}, {3})".format(srcLat, srcLon, dstLat, dstLon))

	busStops = BusStop.objects.values()
	radius = 2000
	nearestSrcBusStops = []
	nearestDstBusStops = []

	srcRoutes = []
	dstRoutes = []

	for busStop in busStops:
		srcDistance = distance(srcLat, srcLon, float(busStop['location_lat']), float(busStop['location_lon']))
		# print("Souce distance: ", srcDistance)
		if srcDistance < radius:
			print('Appending Source: ', busStop['stop_name'], " Distance: ", srcDistance)
			nearestSrcBusStops.append(busStop)
			if not busStop['route'] in srcRoutes:
				srcRoutes.append(busStop['route'])

		dstDistance = distance(dstLat, dstLon, float(busStop['location_lat']), float(busStop['location_lon']))
		# print("Destination distance: ", dstDistance)
		if dstDistance < radius:
			print('Appending Destination: ', busStop['stop_name'], " Distance: ", dstDistance)
			nearestDstBusStops.append(busStop)
			if not busStop['route'] in dstRoutes:
				dstRoutes.append(busStop['route'])

	filteredNearestSrcStops = []
	filteredNearestDstStops = []

	for r in srcRoutes:
		tempStops = list(filter(lambda d: d['route'] in [r], nearestSrcBusStops))
		# tempStops = nearestSrcBusStops.filter(route=r)
		curDist = radius
		tempStop = None
		for stop in tempStops:
			tempDist = distance(srcLat, srcLon, float(stop['location_lat']), float(stop['location_lon']))
			if curDist > tempDist:
				curDist = tempDist
				tempStop = stop
		filteredNearestSrcStops.append(tempStop)
	nearestSrcBusStops = filteredNearestSrcStops
	print color.RED+"SRC: {0}".format(nearestSrcBusStops)+color.END

	for r in dstRoutes:
		tempStops = list(filter(lambda d: d['route'] in [r], nearestDstBusStops))
		# tempStops = nearestSrcBusStops.filter(route=r)
		curDist = radius
		tempStop = None
		for stop in tempStops:
			tempDist = distance(dstLat, dstLon, float(stop['location_lat']), float(stop['location_lon']))
			if curDist > tempDist:
				curDist = tempDist
				tempStop = stop
		filteredNearestDstStops.append(tempStop)
	nearestDstBusStops = filteredNearestDstStops
	print color.RED+"DST: {0}".format(nearestDstBusStops)+color.END

	if len(nearestSrcBusStops) == 0:
		response_data['success'] = False
		response_data['message'] = 'There are no bus stops within 2 kms of your location'

	elif len(nearestDstBusStops) == 0:
		response_data['success'] = False
		response_data['message'] = 'There are no bus stops within 2 kms of your destination'

	else:
		routes = []
		buses = []
		data = []
		allBusesQuery = BUS.objects.values()
		for srcBusStop in nearestSrcBusStops:
			for dstBusStop in nearestDstBusStops:
				if srcBusStop['route'] == dstBusStop['route'] and not srcBusStop['route'] in routes:
					# found route. Fetch bus and append to array
					print("Found route: ", srcBusStop['route'])
					routes.append(srcBusStop['route'])
					reverse = srcBusStop['seq'] > dstBusStop['seq']
					newBuses = allBusesQuery.filter(bus_route=srcBusStop['route'], reverse=reverse)
					if reverse:
						newBuses = [i for i in newBuses if i['currSeq'] > srcBusStop['seq']]
					else:
						newBuses = [i for i in newBuses if i['currSeq'] < srcBusStop['seq']]
					dataObj = {}
					dataObj['startStation'] = srcBusStop
					dataObj['endStation'] = dstBusStop
					dataObj['buses'] = list(newBuses)
					data.append(dataObj)
					buses = buses + list(newBuses)

		if len(buses) == 0:
			response_data['success'] = False
			response_data['message'] = 'There are no buses on for your chosen destination from your location'
		else:
			response_data['success'] = True
			response_data['message'] = 'Buses found!'
			response_data['data'] = data
	print(response_data)
	print("================================================================================")
	return JsonResponse(response_data)

#--------------------------------------------------------------------------------------------------

# User apis----------------------------------------------------------------------------------------

@csrf_exempt 
def login(request):

	response_data = {}

	userName = request.POST.get("userName", "")
	password = request.POST.get("password", "")
	userQuery = User.objects.all().filter(user_name=userName, password=password)

	if userQuery.exists():
		response_data['success'] = True
		response_data['message'] = 'Login successful'
		response_data['data'] = userQuery.get().getJson()
	else:
		response_data['success'] = False

	return JsonResponse(response_data)

@csrf_exempt
def boardingConfirm(request):
	print("Boarding Confirm API============================================================")
	userId = request.POST.get("userId", "")
	busId = request.POST.get("busId", "")
	stopId = request.POST.get("stopId", "")

	b = BUS.objects.all().filter(id=busId).get()
	b.numTravellers = b.numTravellers + 1
	b.save()

	u = User.objects.all().filter(id=userId).get()
	u.startStation = stopId
	u.save()

	s = BusStop.objects.all().filter(id=stopId).get()

	print("User {0} boarded bus {1} at {2}".format(u.user_name, b.id, s.stop_name))
	response_data = {}
	response_data['success'] = True
	response_data['message'] = 'Boarding successful'

	print(response_data)

	print("================================================================================")
	return JsonResponse(response_data)

@csrf_exempt
def exitConfirm(request):
	print("Boarding Confirm API============================================================")
	userId = request.POST.get("userId", "")
	busId = request.POST.get("busId", "")

	b = BUS.objects.all().filter(id=busId).get()
	b.numTravellers = b.numTravellers - 1
	b.save()


	sExit = BusStop.objects.all().filter(stop_name=b.next_stop).get()


	u = User.objects.all().filter(id=userId).get()
	u.stopStation = sExit.id
	u.save()

	
	sBoarded = BusStop.objects.all().filter(id=u.startStation).get()
	print("User {0} exited bus {1} at {2}".format(u.user_name, b.id, sExit.stop_name))

	numStations = abs(sExit.seq - sBoarded.seq)
	bill = numStations * 4

	t = Transaction(userId=userId, amount=bill, startStation=sBoarded.id, stopsStation=sExit.id)
	t.save()

	response_data = {}
	response_data['success'] = True
	response_data['message'] = 'Exit successful'
	response_data['bill_amount'] = bill

	print(response_data)

	print("================================================================================")
	return JsonResponse(response_data)





























#--------------------------------------------------------------------------------------------------
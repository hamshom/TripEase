""" 
This file should contain all the scheduler functions, classes and methods. 
"""
import googlemaps as maps # The google maps python API package
import json # Module for importing data from JSON
from pprint import pprint # Pretty print, imported for use in debugging. 
import numpy as np
from urllib.request import urlopen
import urllib.request
import json
import datetime
import re
import dateutil.parser as dparser
import copy

api_key = 'AIzaSyAbL4TToOmmWOcSjzdyOXK95HDdsYjMC04' # Our free API key
client = maps.Client(key=api_key) # Creates a client object, which is an argument in all maps functions.

class Location():
	"""Class containing info on a given location."""
	def __init__(self, name, address):
		self.address = address
		self.name = name
		self.place_id = None
		self.hours = None

	def __str__(self):
		return self.name + " - " + self.address

	def __repr__(self):
		return self.name + " - " + self.address

	def __eq__(self, other):
		return (self.address == other.address) and (self.name == other.name) and (self.place_id == other.place_id) and (self.hours == other.hours)


def getLocations(file, userInput):
	"""Returns a list of location objects from a JSON file of bookmarked maps locations"""
	startingPoint = Location(name=userInput['starting name'],address = userInput['starting_address'])
	locations = [startingPoint] # Initializes the list of locations with the starting location.
	with open(file) as bookmarks:
		data = json.load(bookmarks)
		for i in range(len(data['features'])):
			address = data['features'][i]['properties']['Location']['Address'] # JSON data can be accessed with keys, like nested dictionaries.
			name = data['features'][i]['properties']['Location']['Business Name']
			locations.append(Location(name,address)) # Make a location out of each name-address pair, add to a list
	return locations

def locationDetails(place_id):
	"""
	Finds the type and hours of a location using the Google Places API, and adds the info to the location object
	Strips the JSON file and creates keys with the weekdays in a dictionary with tuples for the opening and closing hour, returns None if it is closed on that date.
	"""
	opening_hours = []
	MyUrl = ('https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=AIzaSyAbL4TToOmmWOcSjzdyOXK95HDdsYjMC04') % (place_id)
	response = urlopen(MyUrl)
	data = json.load(response)
	try:
		for hours in data['result']['opening_hours']['weekday_text']:
			opening_hours.append(hours)
	except:
		pprint(data)
	response.close()
	week_hours = {}
	for i in opening_hours:
		weekday = i.split(':')[0]
		try:
			start_date = re.search('[0-9]{1,2}:[0-9]{2}\s(AM|PM)', i).group()
			date = dparser.parse(start_date)
			start_time = date.strftime('%H:%M')
			start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
		except:
			start_time = None
		try:
			end_date = re.search('(?<= – ).*', i).group()
			date = dparser.parse(end_date)
			end_time = date.strftime('%H:%M')
			end_time = datetime.datetime.strptime(end_time, "%H:%M").time()
			if end_time == datetime.time(0, 0):
				end_time = datetime.time(23, 59)
		except:
			end_time = None
		week_hours[weekday] = (start_time, end_time)
	return week_hours

def OpenClose(location, currentTime, currentDay):
	"""Tests if the location is open at the time and day called. Returns True if open or False if closed"""
	print(location.name)
	print(location.hours, '\n')
	hours_operation = location.hours
	current_operation_time = hours_operation[str(currentDay)]
	if current_operation_time[0] == None or current_operation_time[1] == None:
		return False
	elif current_operation_time[0] < current_operation_time[1]:
		return current_operation_time[0] <= currentTime.time() < current_operation_time[1]
	else:
		return current_operation_time[0] <= currentTime.time() or currentTime.time() < current_operation_time[1]

def canGoTo(location, arrivalTime, inputs):
	"""Tests if the user can go to the given location based on transit time - checks to see if location is still open after travel time is accounted. 
	Returns True if location is open after travel time, False if location will be closed after travel time."""
	return OpenClose(location, arrivalTime, inputs['start_day']) and arrivalTime.time() < inputs['end'].time()

def getUserInputs():
	"""
	Gets user inputs of start/end dates, times, and starting address, returning a dictionary.
	The keys are as follows:
	start: date-time object of the user's starting date and time
	end: date-time object of the user's ending date and time
	starting_location: The user's starting location for their itinerary
	travel_mode: The user's preferred mode of transport (driving or transit)
	"""
	inputs = {}
	start_date = input("Enter your trip start date (MM/DD/YYYY): ")
	start_time = input("What time (00:00-23:59) will you be arriving on that day? ")
	end_time = input("What time (00:00-23:59) will you be leaving on that day? ")
	inputs['start_date'] = start_date
	inputs['start_day'] = convertWeekDay(start_date)
	inputs['start'] = convertUserDateTime(start_time)
	inputs['end'] = convertUserDateTime(end_time)
	inputs['starting name'] = "Nopa" # input('Enter starting location name: ')
	inputs['starting_address'] = "560 Divisadero Street, San Francisco, CA" # input("Enter your starting address: ")
	travel_mode_int = int(input("Will you be driving or taking transit? Enter 1 for driving, 2 for transit. ").strip())
	travel_mode = None
	if travel_mode_int == 1:
		travel_mode = "driving"
	elif travel_mode_int == 2:
		travel_mode = "transit"
	else:
		print("Please re-run the program and enter a valid integer.")
		return
	inputs['travel_mode'] = travel_mode
	return inputs

def convertUserDateTime(time):
	"""
	Converts input times into datetime objects.
	"""
	return datetime.datetime.strptime(time, "%H:%M")

def convertWeekDay(start_date):
	"""
	Converts input date into a string containing the day of the week.
	"""
	return datetime.datetime.strptime(start_date, "%m/%d/%Y").strftime("%A")

def getPlaceID(client,location):
	"""
	Returns the google API place ID of a location, which is found by searching the name
	and address of the location in the Google Maps API"
	"""
	details = maps.places.places(client=client,query=location.name + ' ' + location.address)
	place_id = details['results'][0]['place_id']
	return place_id

def getDistanceMatrix(client,addresses,mode='driving'):
	"""
	Given a client code and address list, calls the Maps API to create a distance matrix
	The matrix element [i,j] returns the distance in travel time (seconds) from location
	i to location j
	"""
	N = len(addresses) # N is the number of locations we have
	mapsMatrix = maps.distance_matrix.distance_matrix(client=client,origins=addresses,destinations=addresses,mode=mode) # Get JSON distance matrix from API. mode = 'transit'
	distanceMatrix = np.zeros((N,N)) # Initialize a distance matrix as an N x N matrix of 0s
	for i in range(N):
		for j in range(N):
			if i == j:
				distanceMatrix[i,j] = float('inf') # Distance from a location to itself should never be the minimum
			else:
				distanceMatrix[i,j] = int(round(mapsMatrix['rows'][i]['elements'][j]['duration']['value'] / 60)) #Gets travel time in minutes
	return distanceMatrix

def makeItinerary(distanceMatrix, start_location, start_day, start, end, locations, inputs):
	"""
	Creates a schedule based on shortest travel times between points, and checks for hours of operation
	"""
	places = copy.deepcopy(locations)
	schedule = [(places[0], 0, start, 60)] # (locationClass, transitTime, timeOfArrival, durationOfStay) adds starting location to the schedule
	del places[0]

	while (len(places) > 0):
		currentPlaceOnSchedule = schedule[-1]
		currentLocation = currentPlaceOnSchedule[0]
		newPlaceAndDistance = []
		numberOfPlacesLeft = len(places)
		for nextPlace in places:
			transitTime = int(distanceMatrix[locations.index(currentLocation), locations.index(nextPlace)])
			newPlaceAndDistance.append((nextPlace, transitTime))
			newPlaceAndDistance.sort(key=lambda tuple: tuple[1])
		for index, (newLocation, transitTime) in enumerate(newPlaceAndDistance):
			newTimeOfArrival = currentPlaceOnSchedule[2] + datetime.timedelta(minutes=currentPlaceOnSchedule[3]) + datetime.timedelta(minutes=transitTime)
			if canGoTo(newLocation, newTimeOfArrival, inputs):
				schedule.append((newLocation, transitTime, newTimeOfArrival, 60))
				del newPlaceAndDistance[index]
				del places[places.index(newLocation)]
				break
			else:
				continue

		if len(newPlaceAndDistance) == numberOfPlacesLeft:
			break
	return schedule


def export(schedulelist):
	address_list = []
	duration = []
	current = []
	for index in schedulelist:
		address,travel_duration,current_time,time_spent = index
		address_list.append(address)
		duration.append(travel_duration)
		current.append(current_time)
	return address_list, duration, current

def main(file):
	inputs = getUserInputs()
	locations = getLocations(file, inputs) # Gets as list of location objects from my saved bookmarks

	for location in locations:
		location.place_id = getPlaceID(client,location)
		location.hours = locationDetails(location.place_id)

	addresses = [location.address for location in locations]
	distanceMatrix = getDistanceMatrix(client,addresses,inputs['travel_mode'])
	itinerary_list = makeItinerary(distanceMatrix, inputs['starting_address'], inputs['start_day'], inputs['start'], inputs['end'], locations, inputs)

	adrs,drtn,crnt = export(itinerary_list)

	itinerary = open("itinerary.txt", "w+")

	itinerary.write("Trip Details\n")
	itinerary.write("Date: " + inputs['start_date'] + "\n")
	itinerary.write("Starting Address: " + inputs['starting_address'] + "\n")
	itinerary.write("Start Time: " + inputs['start'].strftime('%H:%M') + "\n")
	itinerary.write("End Time: " + inputs['end'].strftime('%H:%M') + "\n")
	itinerary.write("Travel Mode: " + inputs['travel_mode'] + "\n")
	itinerary.write("\n")
	itinerary.write("--- Itinerary ----\n")
	itinerary.write("\n")
	for i in range(len(itinerary_list)):
		current = crnt[i].strftime('%H:%M')
		address = adrs[i]
		itinerary.write(str(current) + "\n" + str(address) + "\n")
		if i < len(adrs) - 1:
			itinerary.write("--- " + str(drtn[i + 1]) + " mins traveling time ----\n")
		else:
			itinerary.write("--- End ----\n")



main('saved_places.json')
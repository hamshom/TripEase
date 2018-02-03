### Problem statement
We’re looking to solve issues revolving around trip planning and creating a smart itinerary based on a researched list of places you’d like to go. When on vacation, it’s often difficult to find out the ideal route or plan to visit all the places you have in mind because you need to conceptualize where each place is on the map and how close together each spot is so you don’t have to needlessly travel from one side of a city to another. We hope to mitigate that problem by allowing users to create a list of all the places they would like to go. Our program will then create an optimal schedule for the user's time based on proximity and time required in each location. 

### Use cases
We believe our program will be most useful for tourists visiting a town from out of town (for example, a parent that is trying to plan their visit to Berkeley). We assume the user will have looked at Google Maps and bookmarked a list of places they want to go. The user will export their bookmarks from Google Maps into a JSON file and then run our script on the file, which will prompt them for their preferred mode of transit, and the arrival/departure times and dates. After the script runs, it will generate an output of the optimal schedule for visiting each given location during the given time window. 

### Assumptions and constraints
Our program assumes the user has already bookmarked the locations that they are interested in visiting, and that they have exported their file into JSON. The user must also define their preferred mode of transit (walking/public transit or driving) which will be used in calculating distances and travel times. Finally, the user must set their arrival time and date as well as their departure time and date, which we will use as the constraints on the time our schedule will be made. 

Making the schedule will involve several assumptions: Time spent at a given place will be pulled from the Google Maps API if possible, although if Google does not have those data we will make a heuristic for each type of location (i.e. 1-2 hours for bars or restaurants). Our program will call the Google API to create a distance matrix, calculating the distances and estimated travel times between each location. To control the number of API calls we need to make, the travel times will be calculated assuming the same start time in the day. We are also assuming that the locations list will be constrained to a single metropolitan area, and assuming a reasonable amount of time in each location. As such, the program will return an error if any locations are too far apart (i.e. 2 hours or more) and also if the user tries to visit too many places in a given day (i.e. a hard cap of ~7 per day). 

As a team, our primary constraints will be time and experience with the Google API. We will focus on making a basic implementation of this program in the time given, and can add features if we finish ahead of schedule. We believe that the given time will be sufficient to learn the basic Google API functions we need and to find out how to make an optimal schedule.

### Architecture
What are the major features in your program and what are their interfaces? How do components or features interact? You may represent your architecture through drawings/sketches and/or pseudocode. (This section is the most important! Please dedicate ample time to writing and documenting your architectural plan.)

The user will export their Google Maps bookmarks through Google Takeout, which we will use to get a JSON file of each location's name, longitude and latitude. In our basic implementation, the user will then enter their travel dates and their preferred method of transit. 

Our program will first use the JSON of the user's locations to create a matrix, with locations as rows and columns. We will populate this matrix by making calls on the Google Maps API for each element. Elements [i,j] of the matrix will be a tuple of: 
(driving distance, walking/public transit distance) between locations i & j. We will also create a separate list of location objects, each of which will have the attributes name, hours of operation and business type. Finally, the schedule will be created as a schedule object that will contain the available times. 

We will model this as a constrained optimization problem, where the constraints are time available in the schedule and hours of operation for each location. Using backtracking search, we will assign each location to a given time in the schedule. The basic pseudocode of this process is:

```python
def make_schedule(schedule,locations):	
	if locations.isEmpty(): # Goal state: All locations have been assigned to a schedule without error
		return schedule
	for i in len(locations): # Iterate through all the locations in our list
	   l = locations.pop() # Choose one from the list
	   if no available timeslots in schedule or timeslot out of location's hours: 
	   	backtrack # When the problem hits a 'dead end', backtrack and try a different assignment until it works 
	   else: 
	   schedule.add(l) 
	   make_schedule(schedule,locations) # Recursively continue to assign locations to the schedule
	return failure # There is no solution if we iterate through all assignments without hitting the goal state
```

### Implementation plan
The user will input a JSON file of Google Maps bookmarks. From this file, we will extract the name of each location as well as the type and operating hours. These data will be used to create a location class, which will have attributes for name, type of business and hours of operation. We will also initiate a Schedule class object, which will track the available times and the location items that are assigned to each timeslot. The available times will be set from the user’s input travel dates and times. 

We will make a DistanceMatrix class that will be modeled as a numpy array of a size (n x n) where n = number of locations. During the initialization of our DistanceMatrix object we will call the Google API on each of the locations we extracted. For each element [i,j] of the matrix, we will find the distance between them in terms of travel time (either driving or walking/using public transit).

As included in the Architecture section, we will solve the problem with a very basic backtracking search algorithm. The features we’ll be writing is an algorithm that calculates the distance between different points using Google’s API and then assigns each place into a different time slot in the itinerary based on an exported saved places JSON file and user inputs. We’ll be using Google Maps API in order to fetch data such as distances, hours of operation and place type as well as GeoJSON to get the data.

## Feature List
What algorithms and/or data structures will each feature need?

Which features will be written by your team? Which features will rely on existing libraries or code that you will be drawing upon? Be sure to cite any such libraries and code that you will be using. How long will each feature take you? When will each feature be completed? Give anticipated dates and specify who will be working on each feature.


| Function  | Time Estimated | Person in Charge |
| ------------- | ------------- | -------------  |
| Reading the JSON file  | 1-2 days | Tim |
| Creating user input prompts for trip parameters  | 1 day | Jing |
| Converting user inputs into appropriate formats | 1 day | Jing & Daphne|
| Calling the API to get distance, hours of operation, place type, time takes to travel from point a to point b  | 3 days | Mahmoud |
| Distance Matrix  | 3 days | Tim |
| Slotting information into different time slots according to information gathered from the API | 3 days | Daphne |
| Backtracking  | 3 days | Mahmoud |
| Error Checking | 1-2 days | Daphne |
| Generating an itinerary | 1-2 days | Daphne & Jing |

### Test plan
How will you convince yourself (and users) that your program works? What test cases will you use? Propose examples of test cases.

We’ll be exporting a sample JSON file with around 10 locations and 2 days in Berkeley as we already know the optimum route and are familiar with the area.

After that, we’ll also test on a larger number of places in a different country to make sure it still works properly. 

We’ll also test for edge cases (100 places in 2 days, large distances between locations, etc) to see if our program is handling those correctly.

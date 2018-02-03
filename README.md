# Info 206 - Project Assignment #1 #

Group D - Tim Burke, Jing Xiong, Daphne Jong, Mahmoud Hamsho

# Project Overview #

# Project Summary #

A program that allows users to import a list of saved places in Google Maps to create a day trip itinerary based on distance, hours of operation, and time spent on each location. This script will then return a viable itinerary with the shortest distances between locations of interest and whether they are open at the right times.

# Problem Statement #

Many people do research prior to traveling to a new place and create a list of points of interest they'd like to visit, but it's often difficult to decide on the best route to take, especially while trying to take into account each point's hours of operation and minimizing travel time. As a result, travelers can end up traveling inefficiently back and forth between one side of town to another. We hope to help travelers maximize their time in a new city by optimizing their route based on the distances between the locations of interest while taking into account the operating hours of each location. 

# Features #

* Users can import their saved places on Google Maps (JSON file format)
* A customized itinerary will be generated based on locations selected, hours of operation, and average time needed in each location
* Output includes trip details with travel times in a text file format

# How to Run #

usage: scheduler.py

Note: Make sure the JSON file of saved places is in the same directory as the script. It should be saved as "saved_places.json" (Google should automatically save it as such when you export it.)

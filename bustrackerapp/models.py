# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.db import models
from django.utils import timezone

# Create your models here.
class BUS(models.Model):
	bus_route = models.CharField(max_length=200)
	bus_location_lat = models.DecimalField(max_digits=8, decimal_places=6)
	bus_location_lon = models.DecimalField(max_digits=8, decimal_places=6)
	last_stop = models.CharField(max_length=200)
	next_stop = models.CharField(max_length=200)
	reverse = models.BooleanField(default=False)
	currSeq = models.IntegerField()
	numTravellers = models.IntegerField()

	def __str__(self):
		return self.bus_route

class User(models.Model):
	user_name = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	startStation = models.IntegerField()
	stopStation = models.IntegerField()

	def __str__(self):
		return self.user_name

	def getJson(self):
		response_data = {}
		response_data['user_name'] = self.user_name
		response_data['user_id'] = self.id
		return response_data


class BusStop(models.Model):
	route = models.CharField(max_length=200)
	location_lat = models.DecimalField(max_digits=8, decimal_places=6)
	location_lon = models.DecimalField(max_digits=8, decimal_places=6)
	stop_name = models.CharField(max_length=200)
	seq = models.IntegerField()

	def __str__(self):
		return self.stop_name


class Transaction(models.Model):
	userId = models.IntegerField()
	date = models.DateTimeField(default=timezone.now)
	amount = models.FloatField(default=0.0)
	startStation = models.IntegerField()
	stopsStation = models.IntegerField()

	def __str__(self):
		return self.amount
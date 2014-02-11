# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


class Objective(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=200)
	pub_date = models.DateField('publication date', auto_now_add=True)
	end_date = models.DateField('end date')

	def __unicode__(self): 
		return self.name


class KeyResult(models.Model):
	POSITIVE = '0'
	NEGATIVE = '1'
	BINARY = '2'
	TYPE_DATA_CHOICES = (
		('0', 'Positive'),
		('1', 'Negative'),
		('2', 'Binary')
	)

	objective = models.ForeignKey(Objective)
	name = models.CharField(max_length=200)
	type_data = models.CharField('Type', 
								 max_length=1, 
								 choices=TYPE_DATA_CHOICES, 
								 default=POSITIVE)
	obtained = models.FloatField()
	expected = models.FloatField()
	pub_date = models.DateField('publication date', auto_now_add=True)

	def __unicode__(self): 
		return self.name

	def percentage(self):
		# Round without decimals
		if self.type_data == self.POSITIVE:
			return int(100 * float(self.obtained) / float(self.expected))
		elif self.type_data == self.NEGATIVE:
			return int(100 * (1 - float(self.obtained) / float(self.expected)))
		elif self.type_data == self.BINARY:
			if self.obtained == 0: 
				return 0
			else:
				return 100

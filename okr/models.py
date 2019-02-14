# -*- coding: utf-8 -*-
from django.db.models import Sum
from django.db import models
from django.contrib.auth.models import User


class Objective(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=200)
	pub_date = models.DateField('publication date', auto_now_add=True)
	end_date = models.DateField('end date')

	def __unicode__(self):
		return self.name

	def percentage_total(self):
		num_kr = self.keyresult_set.count()
		if num_kr > 0:
			sum_percentages = self.keyresult_set.aggregate(percentage_total=Sum("percentage"))
			return sum_percentages['percentage_total'] / num_kr
		else:
			return 0.0


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
	obtained = models.FloatField(default=0)
	expected = models.FloatField()
	percentage = models.FloatField()
	pub_date = models.DateField('publication date', auto_now_add=True)

	def __unicode__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.percentage = calculate_percentage(self.type_data, self.obtained, self.expected)
		super(KeyResult, self).save(*args, **kwargs)


def calculate_percentage(type_data, obtained, expected):
	# Round without decimals
	if type_data == KeyResult.POSITIVE:
		return 100 * obtained / expected
	elif type_data == KeyResult.NEGATIVE:
		return 100 * (1 - obtained / expected)
	elif type_data == KeyResult.BINARY:
		if obtained == 0:
			return 0
		else:
			return 100
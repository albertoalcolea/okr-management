# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.utils import timezone

from okr.models import Objective, KeyResult


def list_okrs(objectives_list):
	okr_list = []
	for o in objectives_list:
		key_results_list = KeyResult.objects.filter(objective=o)

		keyresults = []
		percentage_total = 0

		if len(key_results_list) > 0:
			for k in key_results_list:

				if k.type_data == KeyResult.POSITIVE:
					details = 'Obtained %d of %d' % (k.obtained, k.expected)
				elif k.type_data == KeyResult.NEGATIVE:
					details = 'Failed %d of %d' % (k.obtained, k.expected)
				elif k.type_data == KeyResult.BINARY:
					if k.obtained == 0:
						details = 'No achieved'
					else:
						details = 'Achieved'

				keyresults.append({
					'name': k.name,
					'percentage': k.percentage(),
					'details': details
				})
				percentage_total += k.percentage()
				
			percentage_total = percentage_total / len(key_results_list)
			
		okr_list.append({
			'objective': o, 
			'percentage': percentage_total,
			'keyresults': keyresults
		})

	return {'okr_list': okr_list} #context


def index(request):
	objectives_list = Objective.objects.filter(
		end_date__gte=timezone.now()).order_by('end_date')
	return render(request, 'okr/index.html', list_okrs(objectives_list))


def archived(request):
	objectives_list = Objective.objects.filter(
		end_date__lt=timezone.now()).order_by('end_date')
	return render(request, 'okr/archived.html', list_okrs(objectives_list))
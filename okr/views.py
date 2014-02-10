# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.utils import timezone
from django.utils import simplejson

from okr.models import Objective, KeyResult
from okr.forms import KeyResultForm


def get_details(type_data, obtained, expected):
	if type_data == KeyResult.POSITIVE:
		details = 'Obtained %d of %d' % (obtained, expected)
	elif type_data == KeyResult.NEGATIVE:
		details = 'Failed %d of %d' % (obtained, expected)
	elif type_data == KeyResult.BINARY:
		if obtained == 0:
			details = 'No achieved'
		else:
			details = 'Achieved'
	return details


def list_okrs(objectives_list, forms=False):
	okr_list = []
	for o in objectives_list:
		key_results_list = KeyResult.objects.filter(objective=o)

		keyresults = []
		percentage_total = 0

		if len(key_results_list) > 0:
			for k in key_results_list:
				kform = None
				if forms:
					kform = KeyResultForm(instance=k)

				keyresults.append({
					'id': k.id,
					'name': k.name,
					'percentage': k.percentage(),
					'details': get_details(k.type_data, k.obtained, k.expected),
					'form': kform,
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
	return render(request, 'okr/index.html', list_okrs(objectives_list, True))


def archived(request):
	objectives_list = Objective.objects.filter(
		end_date__lt=timezone.now()).order_by('end_date')
	return render(request, 'okr/archived.html', list_okrs(objectives_list))


def ajax_test(request):
	if request.method == 'POST' and request.is_ajax:
		form = KeyResultForm(request.POST)
		if form.is_valid():
			kr = KeyResult.objects.get(id=request.POST['id'])
			kr.name 		= request.POST['name']
			kr.type_data 	= request.POST['type_data']
			kr.expected 	= float(request.POST['expected'])
			kr.obtained 	= float(request.POST['obtained'])
			kr.save()

			response = {
				'name': kr.name,
				'percentage': kr.percentage(),
				'details': get_details(kr.type_data, kr.obtained, kr.expected),
			}   
			return HttpResponse(simplejson.dumps(response), 
				mimetype='application/javascript')
	else:	
		response = {'status': 'error'}                                                             
		return HttpResponse(simplejson.dumps(response), 
			mimetype='application/javascript')

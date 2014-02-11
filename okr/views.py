# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.utils import timezone
import json

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
		key_results_list = KeyResult.objects.filter(objective=o).order_by('-pub_date')

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
			'keyresults': keyresults,
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


def edit_kr(request):
	if not request.is_ajax():
		raise Http404

	if request.method == 'POST' and request.POST.has_key('id'):
		try:
			kr = KeyResult.objects.get(id=request.POST['id'])
			form = KeyResultForm(request.POST, instance=kr)
			if form.is_valid():
				form.save()
				response = {
					'status': 'ok',
					'data': {
						'name': kr.name,
						'percentage': kr.percentage(),
						'details': get_details(kr.type_data, kr.obtained, kr.expected),
					}
				}   
				return HttpResponse(json.dumps(response), mimetype='application/json')
			else:
				response = {
					'status': 'error',
					'data': form.errors
				}
				return HttpResponse(json.dumps(response), mimetype='application/json')
		except (KeyError, KeyResult.DoesNotExist):
			response = {'status': 'method-error'}                                                             
			return HttpResponseBadRequest(json.dumps(response), mimetype='application/json')
	else:	
		response = {'status': 'method-error'}                                                             
		return HttpResponseBadRequest(json.dumps(response), mimetype='application/json')


def show_kr(request, id):
	if not request.is_ajax():
	 	raise Http404

	try:
		kr = KeyResult.objects.get(id=id)
		response = {
			'name': kr.name,
			'type_data': kr.type_data,
			'expected': kr.expected,
			'obtained': kr.obtained
		}
		return HttpResponse(json.dumps(response), mimetype='application/json')
	except (KeyError, KeyResult.DoesNotExist):
		response = {'status': 'method-error'}
		return HttpResponseBadRequest(json.dumps(response), mimetype='application/json')

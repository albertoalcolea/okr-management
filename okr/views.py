# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
import json

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from okr.models import Objective, KeyResult
from okr.forms import ObjectiveForm, KeyResultForm, AuthForm


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


def list_okrs(objectives_list, show_forms=False):
	okr_list = []
	for o in objectives_list:
		key_results_list = KeyResult.objects.filter(objective=o).order_by('-pub_date')

		keyresults = []
		if key_results_list:
			for k in key_results_list:
				keyresults.append({
					'id': k.id,
					'name': k.name,
					'percentage': int(k.percentage),
					'details': get_details(k.type_data, k.obtained, k.expected),
				})
				if show_forms:
					keyresults[-1]['form'] = KeyResultForm(instance=k)
			
		okr_list.append({
			'objective': o, 
			'percentage': int(o.percentage_total()),
			'keyresults': keyresults,
		})

	return okr_list


def index(request):
	objectives_list = Objective.objects.filter(
		end_date__gte=timezone.now()).order_by('end_date')
	context = {'okr_list': list_okrs(objectives_list, True)}
	return render(request, 'okr/visible.html', context)


def archived(request):
	return archived_paged(request, 1)


def archived_paged(request, page):
	objectives_list = Objective.objects.filter(
		end_date__lt=timezone.now()).order_by('end_date')
	
	okr_list = list_okrs(objectives_list)
	paginator = Paginator(okr_list, 7)

	try:
		okrs = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		okrs = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		okrs = paginator.page(paginator.num_pages)

	return render(request, 'okr/archived.html', {'okr_list': okrs})


def edit_kr(request):
	if not request.is_ajax():
		raise Http404

	if request.method == 'POST' and request.POST.has_key('id'):
		kr = get_object_or_404(KeyResult, id=request.POST['id'])
		form = KeyResultForm(request.POST, instance=kr)
		if form.is_valid():
			form.save()
			response = {
				'status': 'ok',
				'data': {
					'name': kr.name,
					'percentage': int(kr.percentage),
					'details': get_details(kr.type_data, kr.obtained, kr.expected),
					'percentage_total': int(kr.objective.percentage_total()),
				}
			}   
			return HttpResponse(json.dumps(response), mimetype='application/json')
		else:
			response = {
				'status': 'error',
				'data': form.errors
			}
			return HttpResponse(json.dumps(response), mimetype='application/json')
	else:	
		response = {'status': 'method-error'}                                                             
		return HttpResponseBadRequest(json.dumps(response), mimetype='application/json')


def show_kr(request, id):
	if not request.is_ajax():
		raise Http404

	kr = get_object_or_404(KeyResult, id=id)
	response = {
		'name': kr.name,
		'type_data': kr.type_data,
		'expected': kr.expected,
		'obtained': kr.obtained
	}
	return HttpResponse(json.dumps(response), mimetype='application/json')


def add_kr(request, o):
	obj = get_object_or_404(Objective, id=o)
	if request.method == "POST":
		form = KeyResultForm(request.POST)
		if form.is_valid():
			kr = form.save(commit=False)
			kr.objective = obj
			kr.save()
			return HttpResponseRedirect(reverse('okr:index'))
	else:
		form = KeyResultForm()
	context = {
		'form': form,
		'objective': obj
	}
	return render(request, "okr/add_kr.html", context)


def delete_kr(request, id):
	get_object_or_404(KeyResult, pk=id).delete()
	return HttpResponseRedirect(reverse('okr:index'))



def add_obj(request):
	if request.method == "POST":
		form = ObjectiveForm(request.POST)
		if form.is_valid():
			user = User.objects.get(username='admin')
			o = form.save(commit=False)
			o.user = user
			o.save()
			return HttpResponseRedirect(reverse('okr:index'))
	else:
		form = ObjectiveForm()
	context = {'form': form}
	return render(request, "okr/add_obj.html", context)


def edit_obj(request, id):
	obj = get_object_or_404(Objective, id=id)
	if request.method == "POST":
		form = ObjectiveForm(request.POST, instance=obj)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('okr:index'))
	else:
		form = ObjectiveForm(instance=obj)
	context = {
		'form': form,
		'objective': obj
	}
	return render(request, "okr/edit_obj.html", context)


def delete_obj(request, id):
	get_object_or_404(Objective, pk=id).delete()
	return HttpResponseRedirect(reverse('okr:index'))


def login(request):
	if request.method == "POST":
		form = AuthForm(request.POST)
		if form.is_valid:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					# Username and password are correct and user is marked as "active"
					login(request, user)
					return HttpResponseRedirect(reverse('okr:index'))
				else:
					# TODO: ir a pagina de error: usuario desactivado
					pass
			else:
				# TODO: ir a pagina de error: usuario invalido
				pass
	else:
		form = AuthForm()
	context = {'form': form}
	return render(request, 'okr/login.html', context)


def logout(request):
	#logout(request)
	return HttpResponseRedirect(reverse('okr:login'))
# -*- coding: utf-8 -*-
from django.contrib import admin
from okr.models import Objective, KeyResult


class ObjectiveAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'pub_date', 'end_date')
	list_filter = ['pub_date']
	search_fields = ['name', 'user']
	date_hierarchy = 'pub_date'


class KeyResultAdmin(admin.ModelAdmin):
	fieldsets = [
		('Objective',	{'fields': ['objective']}),
		('Key Result',	{'fields': ['name', 'type_data', 'expected', 'obtained']}),
	]
	list_display = ('name', 'objective', 'type_data', 'expected', 'obtained', 'pub_date')
	list_filter = ['pub_date']
	search_fields = ['name', 'objective']
	date_hierarchy = 'pub_date'


admin.site.register(Objective, ObjectiveAdmin)
admin.site.register(KeyResult, KeyResultAdmin)

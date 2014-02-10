from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
import datetime

from django.contrib.auth.models import User
from okr.models import Objective, KeyResult
from okr.forms import KeyResultForm


# Auxiliar functions
def create_okr(o_name, num_kr, date):
	u = User.objects.create_user(username='admin', password='password',
		first_name='admin', last_name='admin', email='admin@admin.com')

	o = Objective.objects.create(user=u, name=o_name, end_date=date)

	for i in range(num_kr):
		KeyResult.objects.create(objective=o, name='key result test-' + str(i), 
			type_data=KeyResult.POSITIVE, obtained=2, expected=6)


def create_kr_form(name, type_data, expected, obtained):
	return KeyResultForm(data={'name': name,
							   'type_data': type_data,
							   'expected': expected,
							   'obtained': obtained
			})



###########################################################################
# MODELS
###########################################################################

class KeyResultModelTest(TestCase):
	def test_positive_percentage(self):
		r = KeyResult(obtained=2, expected=8)
		self.assertEqual(r.percentage(), 25)
		r = KeyResult(obtained=2, expected=6)
		self.assertEqual(r.percentage(), 33)
	
	def test_negative_percentage(self):
		r = KeyResult(type_data=KeyResult.NEGATIVE, obtained=2, expected=3)
		self.assertEqual(r.percentage(), 33)
		r = KeyResult(type_data=KeyResult.NEGATIVE, obtained=1, expected=3)
		self.assertEqual(r.percentage(), 66)

	def test_binary_percentage(self):
		r = KeyResult(type_data=KeyResult.BINARY, obtained=0, expected=1)
		self.assertEqual(r.percentage(), 0)
		r = KeyResult(type_data=KeyResult.BINARY, obtained=1, expected=1)
		self.assertEqual(r.percentage(), 100)



###########################################################################
# VIEWS
###########################################################################

class OkrViewTest(TestCase):
	def test_index_with_no_okrs(self):
		response = self.client.get(reverse('okr:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No objectives are available.")
		self.assertQuerysetEqual(response.context['okr_list'], [])

	def test_index_with_one_archived_okr(self):
		o_name = 'archived test'
		n = 1
		create_okr(o_name, n, timezone.now() - datetime.timedelta(days=30))
		response = self.client.get(reverse('okr:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No objectives are available.")
		self.assertQuerysetEqual(response.context['okr_list'], [])

	def test_index_with_one_okr(self):
		o_name = 'objective test'
		n = 3
		create_okr(o_name, n, timezone.now() + datetime.timedelta(days=30))
		response = self.client.get(reverse('okr:index'))
		self.assertEqual(response.status_code, 200)

		percentage_expected=round(100*2.0/6.0) # *n/n
		okr_list = response.context['okr_list']
		okr = okr_list[0]
		self.assertEqual(len(okr_list), 1)
		self.assertEqual(okr['objective'].name, o_name)
		self.assertEqual(len(okr['keyresults']), n)
		self.assertEqual(okr['percentage'], percentage_expected)

	def test_archived_with_no_okrs(self):
		response = self.client.get(reverse('okr:archived'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No objectives are available.")
		self.assertQuerysetEqual(response.context['okr_list'], [])

	def test_archived_with_one_no_archived_okr(self):
		o_name = 'no archived test'
		n = 1
		create_okr(o_name, n, timezone.now() + datetime.timedelta(days=30))
		response = self.client.get(reverse('okr:archived'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No objectives are available.")
		self.assertQuerysetEqual(response.context['okr_list'], [])

	def test_archived_with_one_okr(self):
		o_name = 'archived test'
		n = 3
		create_okr(o_name, n, timezone.now() - datetime.timedelta(days=30))
		response = self.client.get(reverse('okr:archived'))
		self.assertEqual(response.status_code, 200)

		percentage_expected=round(100*2.0/6.0) # *n/n
		okr_list = response.context['okr_list']
		okr = okr_list[0]
		self.assertEqual(len(okr_list), 1)
		self.assertEqual(okr['objective'].name, o_name)
		self.assertEqual(len(okr['keyresults']), n)
		self.assertEqual(okr['percentage'], percentage_expected)



###########################################################################
# FORMS
###########################################################################

class OkrFormTest(TestCase):
	def test_form_valid(self):
		form = create_kr_form('test kr', KeyResult.POSITIVE, 2.0, 2.0)
		self.assertTrue(form.is_valid())  
		self.assertEqual(form.cleaned_data['name'], 'test kr')
		self.assertEqual(form.cleaned_data['type_data'], KeyResult.POSITIVE)
		self.assertEqual(form.cleaned_data['expected'], 2.0)
		self.assertEqual(form.cleaned_data['obtained'], 2.0)

	def test_invalid_fields(self):
		# name
		form = create_kr_form('', KeyResult.POSITIVE, 2.0, 2.0)
		self.assertFalse(form.is_valid())

		# type_data
		form = create_kr_form('test kr', '9', 2.0, 2.0)
		self.assertFalse(form.is_valid())
		form = create_kr_form('test kr', '-1', 2.0, 2.0)
		self.assertFalse(form.is_valid())
		form = create_kr_form('test kr', 'a', 2.0, 2.0)
		self.assertFalse(form.is_valid())

		# expected
		form = create_kr_form('test kr', KeyResult.POSITIVE, '2.0', 2.0)
		self.assertTrue(form.is_valid())
		form = create_kr_form('test kr', KeyResult.POSITIVE, 2, 2.0)
		self.assertTrue(form.is_valid())
		form = create_kr_form('test kr', KeyResult.POSITIVE, 'a', 2.0)
		self.assertFalse(form.is_valid())

		# obtained
		form = create_kr_form('test kr', KeyResult.POSITIVE, 2.0, '2.0')
		self.assertTrue(form.is_valid())
		form = create_kr_form('test kr', KeyResult.POSITIVE, 2.0, 2)
		self.assertTrue(form.is_valid())
		form = create_kr_form('test kr', KeyResult.POSITIVE, 2.0, 'a')
		self.assertFalse(form.is_valid())

	def test_obtained_gt_expected(self):
		form = create_kr_form('test kr', KeyResult.POSITIVE, 2, 3)
		self.assertFalse(form.is_valid())

	def test_binary(self):
		form = create_kr_form('test kr', KeyResult.BINARY, 1, 0)
		self.assertTrue(form.is_valid())
		form = create_kr_form('test kr', KeyResult.BINARY, 0, 0)
		self.assertFalse(form.is_valid())
		form = create_kr_form('test kr', KeyResult.BINARY, 3, 0)
		self.assertFalse(form.is_valid())
		form = create_kr_form('test kr', KeyResult.BINARY, 1, 0)
		self.assertTrue(form.is_valid())
		form = create_kr_form('test kr', KeyResult.BINARY, 1, 1)
		self.assertTrue(form.is_valid())
		form = create_kr_form('test kr', KeyResult.BINARY, 1, 3)
		self.assertFalse(form.is_valid())


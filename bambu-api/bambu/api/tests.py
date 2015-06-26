from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf.urls import patterns, url, include
from django.contrib.auth.models import User
from bambu.api import autodiscover, site
import json

class APIEndpointTest(TestCase):
	def setUp(self):
		if not any(site._registry):
			autodiscover()
		
		self.endpoints = []
		for model, model_api in site._registry.iteritems():
			self.endpoints.append(model_api)
		
		self.user = User.objects.create_user(
			username = 'test',
			password = 'test'
		)
		
		self.assertTrue(
			self.client.login(username = 'test', password = 'test')
		)
	
	def tearDown(self):
		self.client.logout()
		self.user.delete()
	
	def test_endpoints(self, parent = None, *args):
		endpoints = parent and parent.inline_instances or self.endpoints
		for api in endpoints:
			opts = api.model._meta
			data = api.example_object()
			if not any(data):
				continue
			
			for format in ('json',):
				if 'GET' in api.allowed_methods:
					# Get a list of objects
					url = reverse(
						'api:%s_%s_list' % (opts.app_label, opts.module_name),
						args = list(args) + [format]
					)
					
					response = self.client.get(url)
					self.assertEqual(response.status_code, 200)
					objects = json.loads(response.content)
					self.assertIsInstance(objects, (list, tuple))
				
				obj = None
				pk = None
				
				if 'POST' in api.allowed_methods:
					# Create a new object
					url = reverse(
						'api:%s_%s_list' % (opts.app_label, opts.module_name),
						args = list(args) + [format]
					)
					
					response = self.client.post(url, data)
					self.assertEqual(response.status_code, 200)
					obj = json.loads(response.content)
					self.assertIsInstance(obj, dict)
					self.assertIsInstance(obj['id'], int)
					self.assertIn('id', obj)
					
					if 'GET' in api.allowed_methods and obj:
						# Return the specific created object
						url = reverse(
							'api:%s_%s_single' % (opts.app_label, opts.module_name),
							args = list(args) + [obj['id'], format]
						)
						
						response = self.client.get(url)
						obj = json.loads(response.content)
						self.assertIsInstance(obj, dict)
						self.assertIn('id', obj)
						pk = obj['id']
						self.assertIsInstance(pk, int)
				else:
					o = api.model.objects.create(**data)
					if 'GET' in api.allowed_methods:
						# Return the specific created object
						url = reverse(
							'api:%s_%s_single' % (opts.app_label, opts.module_name),
							args = list(args) + [o.pk, format]
						)
						
						response = self.client.get(url)
						obj = json.loads(response.content)
						self.assertIsInstance(obj, dict)
						self.assertIn('id', obj)
						pk = obj['id']
						self.assertIsInstance(pk, int)
				
				if 'PUT' in api.allowed_methods and obj:
					# Create a new object
					url = reverse(
						'api:%s_%s_single' % (opts.app_label, opts.module_name),
						args = list(args) + [obj['id'], format]
					)
					
					response = self.client.put(url, obj)
					self.assertEqual(response.status_code, 200)
					obj = json.loads(response.content)
					self.assertIsInstance(obj, dict)
					self.assertIn('id', obj)
					self.assertIsInstance(obj['id'], int)
				
				if any(api.inlines) and obj:
					subargs = list(args) + [obj['id']]
					self.test_endpoints(api, *subargs)
				
				if 'DELETE' in api.allowed_methods and obj:
					url = reverse(
						'api:%s_%s_single' % (opts.app_label, opts.module_name),
						args = list(args) + [obj['id'], format]
					)
					
					response = self.client.delete(url)
					self.assertEqual(response.status_code, 200)
					obj = json.loads(response.content)
					self.assertIsInstance(obj, (list, tuple))
					self.assertIn('OK', obj)
				elif pk:
					api.model.objects.get(pk = pk).delete()
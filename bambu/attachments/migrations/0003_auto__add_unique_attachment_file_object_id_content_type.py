# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

	def forwards(self, orm):
		# Adding index on 'Attachment', fields ['mimetype']
		db.create_index(u'attachments_attachment', ['mimetype'])

		# Adding index on 'Attachment', fields ['featured']
		db.create_index(u'attachments_attachment', ['featured'])
		
		# Adding unique constraint on 'Attachment', fields ['file', 'object_id', 'content_type']
		db.create_unique(u'attachments_attachment', ['file', 'object_id', 'content_type_id'])


	def backwards(self, orm):
		# Removing unique constraint on 'Attachment', fields ['file', 'object_id', 'content_type']
		db.delete_unique(u'attachments_attachment', ['file', 'object_id', 'content_type_id'])

		# Removing index on 'Attachment', fields ['featured']
		db.delete_index(u'attachments_attachment', ['featured'])

		# Removing index on 'Attachment', fields ['mimetype']
		db.delete_index(u'attachments_attachment', ['mimetype'])


	models = {
		u'attachments.attachment': {
			'Meta': {'unique_together': "(('content_type', 'object_id', 'file'),)", 'object_name': 'Attachment'},
			'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
			'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
			'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
			'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
			'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
			'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
			'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
		},
		u'contenttypes.contenttype': {
			'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
			'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
		}
	}

	complete_apps = ['attachments']
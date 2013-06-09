# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Resource', fields ['url']
        db.create_index('oembed_resource', ['url'])


    def backwards(self, orm):
        # Removing index on 'Resource', fields ['url']
        db.delete_index('oembed_resource', ['url'])


    models = {
        'oembed.resource': {
            'Meta': {'unique_together': "(('url', 'width'),)", 'object_name': 'Resource'},
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'db_index': 'True'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['oembed']
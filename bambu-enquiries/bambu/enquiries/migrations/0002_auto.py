# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Enquiry', fields ['email']
        db.create_index('enquiries_enquiry', ['email'])

        # Adding index on 'Enquiry', fields ['sent']
        db.create_index('enquiries_enquiry', ['sent'])


    def backwards(self, orm):
        # Removing index on 'Enquiry', fields ['sent']
        db.delete_index('enquiries_enquiry', ['sent'])

        # Removing index on 'Enquiry', fields ['email']
        db.delete_index('enquiries_enquiry', ['email'])


    models = {
        'enquiries.enquiry': {
            'Meta': {'ordering': "('-sent',)", 'object_name': 'Enquiry'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['enquiries']
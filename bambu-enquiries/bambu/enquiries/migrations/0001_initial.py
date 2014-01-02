# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Enquiry'
        db.create_table('enquiries_enquiry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=200)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('enquiries', ['Enquiry'])


    def backwards(self, orm):
        
        # Deleting model 'Enquiry'
        db.delete_table('enquiries_enquiry')


    models = {
        'enquiries.enquiry': {
            'Meta': {'ordering': "('-sent',)", 'object_name': 'Enquiry'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['enquiries']

# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Resource'
        db.create_table('oembed_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('oembed', ['Resource'])

        # Adding unique constraint on 'Resource', fields ['url', 'width']
        db.create_unique('oembed_resource', ['url', 'width'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Resource', fields ['url', 'width']
        db.delete_unique('oembed_resource', ['url', 'width'])

        # Deleting model 'Resource'
        db.delete_table('oembed_resource')


    models = {
        'oembed.resource': {
            'Meta': {'unique_together': "(('url', 'width'),)", 'object_name': 'Resource'},
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['oembed']

# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Job'
        db.create_table('cron_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('next_run', self.gf('django.db.models.fields.DateTimeField')()),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('running', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('cron', ['Job'])


    def backwards(self, orm):
        
        # Deleting model 'Job'
        db.delete_table('cron_job')


    models = {
        'cron.job': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Job'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'next_run': ('django.db.models.fields.DateTimeField', [], {}),
            'running': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['cron']

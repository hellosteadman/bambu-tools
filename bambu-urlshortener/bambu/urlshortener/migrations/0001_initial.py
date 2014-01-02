# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShortURL'
        db.create_table('urlshortener_shorturl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=7)),
            ('visits', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('last_visited', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('urlshortener', ['ShortURL'])


    def backwards(self, orm):
        # Deleting model 'ShortURL'
        db.delete_table('urlshortener_shorturl')


    models = {
        'urlshortener.shorturl': {
            'Meta': {'object_name': 'ShortURL'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_visited': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '7'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'visits': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['urlshortener']
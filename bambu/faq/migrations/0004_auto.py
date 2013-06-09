# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Category', fields ['order']
        db.create_index('faq_category', ['order'])


    def backwards(self, orm):
        # Removing index on 'Category', fields ['order']
        db.delete_index('faq_category', ['order'])


    models = {
        'faq.category': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Category'},
            'icon': ('django.db.models.fields.CharField', [], {'default': "u'question-sign'", 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'faq.topic': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Topic'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topics'", 'to': "orm['faq.Category']"}),
            'icon': ('django.db.models.fields.CharField', [], {'default': "u'question-sign'", 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['faq']
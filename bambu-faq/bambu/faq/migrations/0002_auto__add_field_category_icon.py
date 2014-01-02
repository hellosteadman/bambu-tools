# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Category.icon'
        db.add_column('faq_category', 'icon',
                      self.gf('django.db.models.fields.CharField')(default=u'question-sign', max_length=30),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Category.icon'
        db.delete_column('faq_category', 'icon')


    models = {
        'faq.category': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Category'},
            'icon': ('django.db.models.fields.CharField', [], {'default': "u'question-sign'", 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'faq.topic': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Topic'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topics'", 'to': "orm['faq.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['faq']
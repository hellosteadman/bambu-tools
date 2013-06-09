# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Comment', fields ['spam']
        db.create_index('comments_comment', ['spam'])

        # Adding index on 'Comment', fields ['object_id']
        db.create_index('comments_comment', ['object_id'])

        # Adding index on 'Comment', fields ['email']
        db.create_index('comments_comment', ['email'])

        # Adding index on 'Comment', fields ['approved']
        db.create_index('comments_comment', ['approved'])

        # Adding index on 'Comment', fields ['sent']
        db.create_index('comments_comment', ['sent'])


    def backwards(self, orm):
        # Removing index on 'Comment', fields ['sent']
        db.delete_index('comments_comment', ['sent'])

        # Removing index on 'Comment', fields ['approved']
        db.delete_index('comments_comment', ['approved'])

        # Removing index on 'Comment', fields ['email']
        db.delete_index('comments_comment', ['email'])

        # Removing index on 'Comment', fields ['object_id']
        db.delete_index('comments_comment', ['object_id'])

        # Removing index on 'Comment', fields ['spam']
        db.delete_index('comments_comment', ['spam'])


    models = {
        'comments.comment': {
            'Meta': {'ordering': "('-sent',)", 'object_name': 'Comment'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'spam': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['comments']
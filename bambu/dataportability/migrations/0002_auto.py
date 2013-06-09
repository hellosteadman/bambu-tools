# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'ImportStatus', fields ['updated']
        db.create_index('dataportability_import_status', ['updated'])

        # Adding index on 'ImportStatus', fields ['kind']
        db.create_index('dataportability_import_status', ['kind'])

        # Adding index on 'ExportJob', fields ['updated']
        db.create_index('dataportability_export', ['updated'])

        # Adding index on 'ExportJob', fields ['started']
        db.create_index('dataportability_export', ['started'])

        # Adding index on 'ExportJob', fields ['object_id']
        db.create_index('dataportability_export', ['object_id'])

        # Adding index on 'ExportStatus', fields ['updated']
        db.create_index('dataportability_export_status', ['updated'])

        # Adding index on 'ExportStatus', fields ['kind']
        db.create_index('dataportability_export_status', ['kind'])

        # Adding index on 'ImportJob', fields ['updated']
        db.create_index('dataportability_import', ['updated'])

        # Adding index on 'ImportJob', fields ['started']
        db.create_index('dataportability_import', ['started'])

        # Adding index on 'ImportJob', fields ['object_id']
        db.create_index('dataportability_import', ['object_id'])


    def backwards(self, orm):
        # Removing index on 'ImportJob', fields ['object_id']
        db.delete_index('dataportability_import', ['object_id'])

        # Removing index on 'ImportJob', fields ['started']
        db.delete_index('dataportability_import', ['started'])

        # Removing index on 'ImportJob', fields ['updated']
        db.delete_index('dataportability_import', ['updated'])

        # Removing index on 'ExportStatus', fields ['kind']
        db.delete_index('dataportability_export_status', ['kind'])

        # Removing index on 'ExportStatus', fields ['updated']
        db.delete_index('dataportability_export_status', ['updated'])

        # Removing index on 'ExportJob', fields ['object_id']
        db.delete_index('dataportability_export', ['object_id'])

        # Removing index on 'ExportJob', fields ['started']
        db.delete_index('dataportability_export', ['started'])

        # Removing index on 'ExportJob', fields ['updated']
        db.delete_index('dataportability_export', ['updated'])

        # Removing index on 'ImportStatus', fields ['kind']
        db.delete_index('dataportability_import_status', ['kind'])

        # Removing index on 'ImportStatus', fields ['updated']
        db.delete_index('dataportability_import_status', ['updated'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dataportability.exportjob': {
            'Meta': {'ordering': "('-updated',)", 'object_name': 'ExportJob', 'db_table': "'dataportability_export'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'handler': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'progress': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'exports'", 'to': "orm['auth.User']"}),
            'writer': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'dataportability.exportstatus': {
            'Meta': {'ordering': "('updated', 'id')", 'object_name': 'ExportStatus', 'db_table': "'dataportability_export_status'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'updates'", 'to': "orm['dataportability.ExportJob']"}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'dataportability.importjob': {
            'Meta': {'ordering': "('-updated',)", 'object_name': 'ImportJob', 'db_table': "'dataportability_import'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'handler': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parser': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imports'", 'to': "orm['auth.User']"})
        },
        'dataportability.importstatus': {
            'Meta': {'ordering': "('updated', 'id')", 'object_name': 'ImportStatus', 'db_table': "'dataportability_import_status'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'updates'", 'to': "orm['dataportability.ImportJob']"}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dataportability']
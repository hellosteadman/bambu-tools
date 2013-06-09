# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Notification'
        db.create_table('notifications_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('happened', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('notifications', ['Notification'])

        # Adding M2M table for field relevant_to on 'Notification'
        db.create_table('notifications_notification_relevant_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notification', models.ForeignKey(orm['notifications.notification'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('notifications_notification_relevant_to', ['notification_id', 'user_id'])

        # Adding model 'ContextVariable'
        db.create_table('notifications_contextvariable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notification', self.gf('django.db.models.fields.related.ForeignKey')(related_name='context', to=orm['notifications.Notification'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notification_contexts', to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('notifications', ['ContextVariable'])

        # Adding unique constraint on 'ContextVariable', fields ['notification', 'name']
        db.create_unique('notifications_contextvariable', ['notification_id', 'name'])

        # Adding model 'DeliveryPreference'
        db.create_table('notifications_deliverypreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notification_preferences', to=orm['auth.User'])),
            ('module', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('methods', self.gf('django.db.models.fields.TextField')(default='["email"]')),
        ))
        db.send_create_signal('notifications', ['DeliveryPreference'])

        # Adding unique constraint on 'DeliveryPreference', fields ['user', 'module', 'kind']
        db.create_unique('notifications_deliverypreference', ['user_id', 'module', 'kind'])


    def backwards(self, orm):
        # Removing unique constraint on 'DeliveryPreference', fields ['user', 'module', 'kind']
        db.delete_unique('notifications_deliverypreference', ['user_id', 'module', 'kind'])

        # Removing unique constraint on 'ContextVariable', fields ['notification', 'name']
        db.delete_unique('notifications_contextvariable', ['notification_id', 'name'])

        # Deleting model 'Notification'
        db.delete_table('notifications_notification')

        # Removing M2M table for field relevant_to on 'Notification'
        db.delete_table('notifications_notification_relevant_to')

        # Deleting model 'ContextVariable'
        db.delete_table('notifications_contextvariable')

        # Deleting model 'DeliveryPreference'
        db.delete_table('notifications_deliverypreference')


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
        'notifications.contextvariable': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('notification', 'name'),)", 'object_name': 'ContextVariable'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notification_contexts'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'context'", 'to': "orm['notifications.Notification']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'notifications.deliverypreference': {
            'Meta': {'unique_together': "(('user', 'module', 'kind'),)", 'object_name': 'DeliveryPreference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'methods': ('django.db.models.fields.TextField', [], {'default': '\'["email"]\''}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notification_preferences'", 'to': "orm['auth.User']"})
        },
        'notifications.notification': {
            'Meta': {'ordering': "('-happened',)", 'object_name': 'Notification'},
            'happened': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'relevant_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifications'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['notifications']
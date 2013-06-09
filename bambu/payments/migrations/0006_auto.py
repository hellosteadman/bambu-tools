# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Status', fields ['changed']
        db.create_index('payments_status', ['changed'])

        # Adding index on 'Status', fields ['state']
        db.create_index('payments_status', ['state'])

        # Adding index on 'TaxRate', fields ['chargeable_percent']
        db.create_index('payments_taxrate', ['chargeable_percent'])

        # Adding index on 'TaxRate', fields ['payable_percent']
        db.create_index('payments_taxrate', ['payable_percent'])

        # Adding index on 'TaxRate', fields ['shorthand']
        db.create_index('payments_taxrate', ['shorthand'])

        # Adding index on 'TaxRate', fields ['name']
        db.create_index('payments_taxrate', ['name'])

        # Adding index on 'RemoteClient', fields ['remote_id']
        db.create_index('payments_remoteclient', ['remote_id'])

        # Adding index on 'RemoteOffer', fields ['remote_id']
        db.create_index('payments_remoteoffer', ['remote_id'])

        # Adding index on 'RemoteOffer', fields ['currency']
        db.create_index('payments_remoteoffer', ['currency'])

        # Adding index on 'Payment', fields ['created']
        db.create_index('payments_payment', ['created'])

        # Adding index on 'Payment', fields ['remote_id']
        db.create_index('payments_payment', ['remote_id'])

        # Adding index on 'Payment', fields ['object_id']
        db.create_index('payments_payment', ['object_id'])

        # Adding index on 'RemoteSubscription', fields ['remote_id']
        db.create_index('payments_remotesubscription', ['remote_id'])

        # Adding index on 'RemoteSubscription', fields ['live']
        db.create_index('payments_remotesubscription', ['live'])


    def backwards(self, orm):
        # Removing index on 'RemoteSubscription', fields ['live']
        db.delete_index('payments_remotesubscription', ['live'])

        # Removing index on 'RemoteSubscription', fields ['remote_id']
        db.delete_index('payments_remotesubscription', ['remote_id'])

        # Removing index on 'Payment', fields ['object_id']
        db.delete_index('payments_payment', ['object_id'])

        # Removing index on 'Payment', fields ['remote_id']
        db.delete_index('payments_payment', ['remote_id'])

        # Removing index on 'Payment', fields ['created']
        db.delete_index('payments_payment', ['created'])

        # Removing index on 'RemoteOffer', fields ['currency']
        db.delete_index('payments_remoteoffer', ['currency'])

        # Removing index on 'RemoteOffer', fields ['remote_id']
        db.delete_index('payments_remoteoffer', ['remote_id'])

        # Removing index on 'RemoteClient', fields ['remote_id']
        db.delete_index('payments_remoteclient', ['remote_id'])

        # Removing index on 'TaxRate', fields ['name']
        db.delete_index('payments_taxrate', ['name'])

        # Removing index on 'TaxRate', fields ['shorthand']
        db.delete_index('payments_taxrate', ['shorthand'])

        # Removing index on 'TaxRate', fields ['payable_percent']
        db.delete_index('payments_taxrate', ['payable_percent'])

        # Removing index on 'TaxRate', fields ['chargeable_percent']
        db.delete_index('payments_taxrate', ['chargeable_percent'])

        # Removing index on 'Status', fields ['state']
        db.delete_index('payments_status', ['state'])

        # Removing index on 'Status', fields ['changed']
        db.delete_index('payments_status', ['changed'])


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
        'international.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'payments.payment': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Payment'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'default': '272', 'related_name': "'payments'", 'to': "orm['international.Country']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': "orm['auth.User']"}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_amount': ('django.db.models.fields.FloatField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'offer_description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'offer_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'offer_net_amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'offer_tax_amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'postage': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'recurring': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tax_amount': ('django.db.models.fields.FloatField', [], {}),
            'tax_rate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': "orm['payments.TaxRate']"}),
            'trial_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'payments.remoteclient': {
            'Meta': {'unique_together': "(('gateway', 'remote_id'),)", 'object_name': 'RemoteClient'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'remote_records'", 'to': "orm['auth.User']"}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'payments.remoteoffer': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('gateway', 'remote_id'),)", 'object_name': 'RemoteOffer'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'trial': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'payments.remotesubscription': {
            'Meta': {'unique_together': "(('gateway', 'remote_id'),)", 'object_name': 'RemoteSubscription'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': "orm['payments.RemoteClient']"}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'live': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': "orm['payments.RemoteOffer']"}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': "orm['payments.Payment']"}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'payments.status': {
            'Meta': {'ordering': "('-changed',)", 'object_name': 'Status'},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statuses'", 'to': "orm['payments.Payment']"}),
            'state': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'payments.taxrate': {
            'Meta': {'ordering': "('chargeable_percent',)", 'object_name': 'TaxRate'},
            'chargeable_percent': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'payable_percent': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'shorthand': ('django.db.models.fields.CharField', [], {'default': "'Tax'", 'max_length': '10', 'db_index': 'True'})
        }
    }

    complete_apps = ['payments']
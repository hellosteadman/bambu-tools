# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Payment.offer_net_amount'
        db.add_column('payments_payment', 'offer_net_amount', self.gf('django.db.models.fields.FloatField')(default=0), keep_default=False)

        # Adding field 'Payment.offer_tax_amount'
        db.add_column('payments_payment', 'offer_tax_amount', self.gf('django.db.models.fields.FloatField')(default=0), keep_default=False)

        # Adding field 'Payment.offer_months'
        db.add_column('payments_payment', 'offer_months', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)

        # Adding field 'Payment.offer_description'
        db.add_column('payments_payment', 'offer_description', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Payment.offer_net_amount'
        db.delete_column('payments_payment', 'offer_net_amount')

        # Deleting field 'Payment.offer_tax_amount'
        db.delete_column('payments_payment', 'offer_tax_amount')

        # Deleting field 'Payment.offer_months'
        db.delete_column('payments_payment', 'offer_months')

        # Deleting field 'Payment.offer_description'
        db.delete_column('payments_payment', 'offer_description')


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
        'payments.payment': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Payment'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': "orm['auth.User']"}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_amount': ('django.db.models.fields.FloatField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'offer_description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'offer_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'offer_net_amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'offer_tax_amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'postage': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'recurring': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tax_amount': ('django.db.models.fields.FloatField', [], {}),
            'tax_rate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': "orm['payments.TaxRate']"}),
            'trial_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'payments.status': {
            'Meta': {'ordering': "('-changed',)", 'object_name': 'Status'},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statuses'", 'to': "orm['payments.Payment']"}),
            'state': ('django.db.models.fields.IntegerField', [], {})
        },
        'payments.taxrate': {
            'Meta': {'ordering': "('chargeable_percent',)", 'object_name': 'TaxRate'},
            'chargeable_percent': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payable_percent': ('django.db.models.fields.FloatField', [], {}),
            'shorthand': ('django.db.models.fields.CharField', [], {'default': "'Tax'", 'max_length': '10'})
        }
    }

    complete_apps = ['payments']

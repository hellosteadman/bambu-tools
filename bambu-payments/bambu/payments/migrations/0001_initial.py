# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TaxRate'
        db.create_table('payments_taxrate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('shorthand', self.gf('django.db.models.fields.CharField')(default='Tax', max_length=10)),
            ('chargeable_percent', self.gf('django.db.models.fields.FloatField')()),
            ('payable_percent', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('payments', ['TaxRate'])

        # Adding model 'Payment'
        db.create_table('payments_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('recurring', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('trial_months', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('gateway', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('net_amount', self.gf('django.db.models.fields.FloatField')()),
            ('tax_amount', self.gf('django.db.models.fields.FloatField')()),
            ('tax_rate', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['payments.TaxRate'])),
            ('postage', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('remote_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('payments', ['Payment'])

        # Adding model 'Status'
        db.create_table('payments_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='statuses', to=orm['payments.Payment'])),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('payments', ['Status'])


    def backwards(self, orm):
        
        # Deleting model 'TaxRate'
        db.delete_table('payments_taxrate')

        # Deleting model 'Payment'
        db.delete_table('payments_payment')

        # Deleting model 'Status'
        db.delete_table('payments_status')


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
            'postage': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'recurring': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tax_amount': ('django.db.models.fields.FloatField', [], {}),
            'tax_rate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': "orm['payments.TaxRate']"}),
            'trial_months': ('django.db.models.fields.PositiveIntegerField', [], {})
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

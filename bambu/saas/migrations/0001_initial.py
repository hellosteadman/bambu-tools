# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Plan'
        db.create_table('saas_plan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('best_value', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('saas', ['Plan'])

        # Adding model 'Price'
        db.create_table('saas_price', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='prices', to=orm['saas.Plan'])),
            ('monthly', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('yearly', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.CharField')(default='GBP', max_length=3)),
        ))
        db.send_create_signal('saas', ['Price'])

        # Adding unique constraint on 'Price', fields ['plan', 'currency']
        db.create_unique('saas_price', ['plan_id', 'currency'])

        # Adding model 'Feature'
        db.create_table('saas_feature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('is_boolean', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('test_function', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('upgrade_cta', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('saas', ['Feature'])

        # Adding model 'PlanFeature'
        db.create_table('saas_planfeature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='features', to=orm['saas.Plan'])),
            ('feature', self.gf('django.db.models.fields.related.ForeignKey')(related_name='plans', to=orm['saas.Feature'])),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('saas', ['PlanFeature'])

        # Adding unique constraint on 'PlanFeature', fields ['plan', 'feature']
        db.create_unique('saas_planfeature', ['plan_id', 'feature_id'])

        # Adding model 'UserPlan'
        db.create_table('saas_userplan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='users', to=orm['saas.Plan'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='plans', unique=True, to=orm['auth.User'])),
            ('started', self.gf('django.db.models.fields.DateField')()),
            ('expiry', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('renewed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('period', self.gf('django.db.models.fields.PositiveIntegerField')(default=12)),
        ))
        db.send_create_signal('saas', ['UserPlan'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'PlanFeature', fields ['plan', 'feature']
        db.delete_unique('saas_planfeature', ['plan_id', 'feature_id'])

        # Removing unique constraint on 'Price', fields ['plan', 'currency']
        db.delete_unique('saas_price', ['plan_id', 'currency'])

        # Deleting model 'Plan'
        db.delete_table('saas_plan')

        # Deleting model 'Price'
        db.delete_table('saas_price')

        # Deleting model 'Feature'
        db.delete_table('saas_feature')

        # Deleting model 'PlanFeature'
        db.delete_table('saas_planfeature')

        # Deleting model 'UserPlan'
        db.delete_table('saas_userplan')


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
        'saas.feature': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Feature'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_boolean': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'test_function': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'upgrade_cta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'saas.plan': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Plan'},
            'best_value': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        'saas.planfeature': {
            'Meta': {'unique_together': "(('plan', 'feature'),)", 'object_name': 'PlanFeature'},
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plans'", 'to': "orm['saas.Feature']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'features'", 'to': "orm['saas.Plan']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'saas.price': {
            'Meta': {'ordering': "('monthly',)", 'unique_together': "(('plan', 'currency'),)", 'object_name': 'Price'},
            'currency': ('django.db.models.fields.CharField', [], {'default': "'GBP'", 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monthly': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': "orm['saas.Plan']"}),
            'yearly': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        'saas.userplan': {
            'Meta': {'ordering': "('-renewed', '-started')", 'object_name': 'UserPlan'},
            'expiry': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.PositiveIntegerField', [], {'default': '12'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users'", 'to': "orm['saas.Plan']"}),
            'renewed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'started': ('django.db.models.fields.DateField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plans'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['saas']

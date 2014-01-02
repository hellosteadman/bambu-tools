# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserPlanChange'
        db.create_table('saas_userplan_changes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='plan_changes', to=orm['auth.User'])),
            ('old_plan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='changed_from', to=orm['saas.Plan'])),
            ('new_plan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='changed_to', to=orm['saas.Plan'])),
            ('period', self.gf('django.db.models.fields.PositiveIntegerField')(default=12)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('discount', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='user_plan_changes', null=True, to=orm['saas.Discount'])),
        ))
        db.send_create_signal('saas', ['UserPlanChange'])


    def backwards(self, orm):
        # Deleting model 'UserPlanChange'
        db.delete_table('saas_userplan_changes')


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
        'saas.discount': {
            'Meta': {'ordering': "('-percent',)", 'object_name': 'Discount'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'valid_yearly': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'saas.emailvalidation': {
            'Meta': {'ordering': "('-sent',)", 'object_name': 'EmailValidation'},
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_validations'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'saas.feature': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Feature'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_boolean': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'test_function': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'upgrade_cta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'saas.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations'", 'to': "orm['saas.UserPlan']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_sent'", 'to': "orm['auth.User']"})
        },
        'saas.passwordreset': {
            'Meta': {'ordering': "('-sent',)", 'object_name': 'PasswordReset'},
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'password_resets'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'saas.plan': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Plan'},
            'best_value': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'groups'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'subuser_groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subuser_groups'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'trial_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
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
            'discount': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_plans'", 'null': 'True', 'to': "orm['saas.Discount']"}),
            'expiry': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_start': ('django.db.models.fields.DateField', [], {}),
            'period': ('django.db.models.fields.PositiveIntegerField', [], {'default': '12'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users'", 'to': "orm['saas.Plan']"}),
            'renewed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'started': ('django.db.models.fields.DateField', [], {}),
            'subusers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'parent_plans'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plans'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'saas.userplanchange': {
            'Meta': {'ordering': "('-changed',)", 'object_name': 'UserPlanChange', 'db_table': "'saas_userplan_changes'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_plan_changes'", 'null': 'True', 'to': "orm['saas.Discount']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changed_to'", 'to': "orm['saas.Plan']"}),
            'old_plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changed_from'", 'to': "orm['saas.Plan']"}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period': ('django.db.models.fields.PositiveIntegerField', [], {'default': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plan_changes'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['saas']
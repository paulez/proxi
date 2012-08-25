# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProxyMessage'
        db.create_table('pmessages_proxymessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('pmessages', ['ProxyMessage'])


    def backwards(self, orm):
        # Deleting model 'ProxyMessage'
        db.delete_table('pmessages_proxymessage')


    models = {
        'pmessages.proxymessage': {
            'Meta': {'object_name': 'ProxyMessage'},
            'address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['pmessages']
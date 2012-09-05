# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProxyIndex'
        db.create_table('pmessages_proxyindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('update', self.gf('django.db.models.fields.DateTimeField')()),
            ('radius', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('pmessages', ['ProxyIndex'])


    def backwards(self, orm):
        # Deleting model 'ProxyIndex'
        db.delete_table('pmessages_proxyindex')


    models = {
        'pmessages.proxyindex': {
            'Meta': {'object_name': 'ProxyIndex'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'radius': ('django.db.models.fields.IntegerField', [], {}),
            'update': ('django.db.models.fields.DateTimeField', [], {})
        },
        'pmessages.proxymessage': {
            'Meta': {'object_name': 'ProxyMessage'},
            'address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'ref': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmessages.ProxyMessage']", 'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['pmessages']
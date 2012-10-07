# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProxyUser'
        db.create_table('pmessages_proxyuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('last_use', self.gf('django.db.models.fields.DateTimeField')()),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('pmessages', ['ProxyUser'])


    def backwards(self, orm):
        # Deleting model 'ProxyUser'
        db.delete_table('pmessages_proxyuser')


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
        },
        'pmessages.proxyuser': {
            'Meta': {'object_name': 'ProxyUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_use': ('django.db.models.fields.DateTimeField', [], {}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['pmessages']
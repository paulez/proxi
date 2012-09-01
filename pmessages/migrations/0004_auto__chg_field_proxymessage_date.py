# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ProxyMessage.date'
        db.alter_column('pmessages_proxymessage', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

    def backwards(self, orm):

        # Changing field 'ProxyMessage.date'
        db.alter_column('pmessages_proxymessage', 'date', self.gf('django.db.models.fields.DateField')(auto_now_add=True))

    models = {
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
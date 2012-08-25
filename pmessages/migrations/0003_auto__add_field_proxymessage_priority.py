# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ProxyMessage.priority'
        db.add_column('pmessages_proxymessage', 'priority',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ProxyMessage.priority'
        db.delete_column('pmessages_proxymessage', 'priority')


    models = {
        'pmessages.proxymessage': {
            'Meta': {'object_name': 'ProxyMessage'},
            'address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'ref': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmessages.ProxyMessage']", 'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['pmessages']
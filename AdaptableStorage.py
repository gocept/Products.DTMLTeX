# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 2002-2004 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""Serializers for AdaptableStorage.

$Id: AdaptableStorage.py,v 1.3 2004/03/08 16:31:06 thomas Exp $"""

__version__= '0.01'

from apelib.core.interfaces import ISerializer
from apelib.core.schemas import RowSequenceSchema, FieldSchema

from DTMLTeX import DTMLTeX

class AttributeSerializer:
    __implements__ = ISerializer

    schema = RowSequenceSchema()
    schema.addField('id', 'string', 1)
    schema.addField('type', 'string')
    schema.addField('data', 'string')

    attributes = {}
    ignore_attributes = []
    update = None
    serializes = None 

    def getSchema(self):
        return self.schema

    def canSerialize(self, object):
        return isinstance(object, self.serializes)

    def serialize(self, object, event):
        assert isinstance(object, self.serializes), \
            '%r does not serialize %r' % (self, object)
        res = []
        for attribute, factory in self.attributes.items():
            if not hasattr(object, attribute):
                continue
            value = getattr(object, attribute)
            t = factory.__name__
            if factory in (str, unicode) and value is not None:
                assert isinstance(value, (str, unicode))
                # `quote' <None>
                value = value.replace("<None>", "<None><None>")
            if value is None:
                value = '<None>'
            else:
                if factory in (list, tuple):
                    value = ','.join(value)
                elif factory == unicode:
                    value = value.encode('UTF-8')
            value = str(value)
            event.ignoreAttribute(attribute)
            res.append((attribute, t, value))
        event.ignoreAttributes(self.ignore_attributes) 
        return res 
        
    def deserialize(self, object, event, state):
        assert isinstance(object, self.serializes), \
            '%r does not deserialize %r but %r' % (self, object, 
                self.serializes)
        for attribute, t, value in state:
            if value == '<None>':
                value = None
            else:
                value = value.replace("<None><None>", "<None>")
                factory = self.attributes.get(attribute)
                if factory is None:
                    continue
                if factory in (list, tuple):
                    value = factory(value.split(','))
                elif factory == unicode:
                    if t != 'str':
                        value = unicode(value, 'UTF-8')
                else:
                    value = factory(value)
            setattr(object, attribute, value)
        if self.update:    
            update_method = getattr(object, self.update)
            if callable(update_method):
                update_method()


class DTMLTeXPropertySerializer(AttributeSerializer):
    serializes = DTMLTeX 
    attributes = {
        'temppath': str, 
        'defaultfilter': str,
        'filters': unicode,
        '__version__': str
    }

class DTMLTeXDataSerializer:
    __implements__ = ISerializer

    schema = FieldSchema('data', 'string')

    def getSchema(self):
        return self.schema

    def canSerialize(self, object):
        return isinstance(object, DTMLTeX)

    def serialize(self, object, event):
        assert isinstance(object, DTMLTeX)
        data = object.read_raw()
        assert isinstance(data, StringType)
        return data

    def deserialze(self, object, event, state):
        assert isinstance(object, DTMLTeX)
        assert isinstance(state, StringType)
        object.manage_edit(state)

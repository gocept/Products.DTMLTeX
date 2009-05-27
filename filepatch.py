# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 1999 Marian Kelc, 2002-2005 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""A patch to Zope's File content type for temporarily writing files
from the ZODB to disk where TeX can find them.

$Id$"""

#Python imports

from time import sleep
from mimetypes import guess_extension
from tempfile import mkstemp
from thread import start_new_thread
from os import write, close, unlink

# Zope imports

import OFS.Image

default_interval = 60

# Helper method running in its own thread to delete the temporary file
# after a time
def delete_tempfile_thread(path, t=default_interval):
    sleep(t)
    unlink(path)
    return

def create_temp(self, t=default_interval):

    suffix = guess_extension(self.content_type) or ""
    if suffix == '.jpe':
        suffix = '.jpg'

    handle, path = mkstemp(suffix)

    data = self.data
    if type(data) is not type(''):
        while data:
            write(handle, data.data)
            data = data.next
    else:
        write(handle, data)
    close(handle)

    # this removes the temporary file in t seconds
    start_new_thread(delete_tempfile_thread, (path, t))

    return path

OFS.Image.File.create_temp = create_temp

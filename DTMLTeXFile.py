#    DTMLTeX - A Zope Product for PS/PDF generation with TeX
#    Copyright (C) 1999 Marian Kelc, 2002 gocept gmbh & co. kg
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: DTMLTeXFile.py,v 1.1.2.2 2003/09/15 16:27:42 ctheune Exp $
"""DTML TeX objects.

$Id: DTMLTeXFile.py,v 1.1.2.2 2003/09/15 16:27:42 ctheune Exp $"""

#from DocumentTemplate.DT_String import File
from App.special_dtml import ClassicHTMLFile
from DTMLTeX import DTMLTeX

class DTMLTeXFile(ClassicHTMLFile, DTMLTeX):
    """docstring"""

    def __init__(self, *nv, **kw):
        DTMLTeX.__init__(self, *nv, **kw)
        ClassicHTMLFile.__init__(self, *nv, **kw)

    def __call__(self, *nv, **kw):
        return DTMLTeX.__call__(self, *nv, **kw)

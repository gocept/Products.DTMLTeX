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
# $Id: __init__.py,v 1.1 2002/05/30 13:37:18 ctheune Exp $
__doc__    = """DTMLTeX initialization"""
__version__= '0.01'

import DTMLTeX
from tex_quote import tex_quote, __init__
from zLOG import LOG

def initialize(context):
    context.registerClass(
        DTMLTeX.DTMLTeX,
        permission='Add DTML TeX Objects',
        constructors=(DTMLTeX.addForm, DTMLTeX.add),
        icon='www/dtmltex.gif',
        legacy=(
            ('manage_addDTMLTeX_form', DTMLTeX.addForm),
            ('manage_addDTMLTeX', DTMLTeX.add),
        )
    )


# The DTML monkeypatch ...
LOG('DTMLTeX',0, 'Applying tex_quote DTML monkeypatch.')
from DocumentTemplate import DT_Var
DT_Var.modifiers.append( (tex_quote.__name__,tex_quote) )
oldinit = DT_Var.Var.__init__
DT_Var.Var.__init__ = __init__
DT_Var.Var.__init__.im_func.func_globals.update(oldinit.im_func.func_globals)


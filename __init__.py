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
# $Id: __init__.py,v 1.1.1.1.8.3 2002/07/24 22:49:11 ctheune Exp $
__doc__    = """DTMLTeX initialization"""
__version__= '0.01'

import DTMLTeX
from tex_quote import tex_quote, __init__25, __init__24
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

# We need two different patches for 2.4.X and 2.5.X
from App import version_txt

if hasattr(version_txt, "getZopeVersion"):
    # Older Zope Versions ( <2.5 don't have this function )
    version = version_txt.getZopeVersion()
    _version = str(version[0]) + "." + str(version[1])
else:
    version = [2,4]

if version[0] != 2:
    LOG("DTMLTeX", 500, "Incompatible Zope Version. (not a Zope 2 Server). No Patch is beeing applied. Maybe you can live without the tex_quote.")
    raise "CompatibilityError"
elif version[1] <= 4:
    LOG("DTMLTeX", 100, "Unsupported Zope Version. ( <= 2.4 ). Trying to apply patch for Zope 2.4 maybe this works. (IF this is a 2.4, this will work, but i can't determine earlier versions.)")
elif version[1] == 5:
    new = __init__25
elif version[1] > 5:
    LOG("DTMLTeX", 100, "Unsupported Zope Version. ( > 2.5 ). Trying to apply patch for Zope 2.5 maybe this works.")
    new = __init__25
    
from DocumentTemplate import DT_Var
DT_Var.modifiers.append( (tex_quote.__name__,tex_quote) )
oldinit = DT_Var.Var.__init__
DT_Var.Var.__init__ = new
DT_Var.Var.__init__.im_func.func_globals.update(oldinit.im_func.func_globals)

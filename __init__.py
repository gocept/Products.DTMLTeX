# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 1999 Marian Kelc, 2002-2004 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""DTMLTeX initialization.

$Id: __init__.py,v 1.3 2004/03/08 18:21:51 thomas Exp $"""

import DTMLTeX
from tex_quote import tex_quote, __init__25, __init__24
from zLOG import *

def initialize(context):
    context.registerClass(
        DTMLTeX.DTMLTeX,
        permission='Add DTMLTeX Objects',
        constructors=(DTMLTeX.addForm, DTMLTeX.add),
        icon='www/dtmltex.gif',
        legacy=(('manage_addDTMLTeX_form', DTMLTeX.addForm),
                ('manage_addDTMLTeX', DTMLTeX.add))
        )


# The DTML monkeypatch ...
LOG('DTMLTeX', 0, 'Applying tex_quote DTML monkeypatch.')

# We need two different patches for 2.4.X and 2.5.X
from App import version_txt

if hasattr(version_txt, "getZopeVersion"):
    # Older Zope Versions ( <2.5 don't have this function )
    version = version_txt.getZopeVersion()
    _version = str(version[0]) + "." + str(version[1])
else:
    version = [2,4]

if version[0] != 2:
    LOG("DTMLTeX", PANIC, "Incompatible Zope Version. (not a Zope 2 Server). No Patch is beeing applied. Maybe you can live without the tex_quote.")
    raise "CompatibilityError"
elif version[1] <= 4:
    LOG("DTMLTeX", WARNING, "Unsupported Zope Version. ( <= 2.4 ). Trying to apply patch for Zope 2.4 maybe this works. (IF this is a 2.4, this will work, but i can't determine earlier versions.)")
    new = __init__24
elif version[1] in [5,6,7]:
    new = __init__25
elif version[1] > 7:
    LOG("DTMLTeX", WARNING, "Unsupported Zope Version. ( > 2.5 ). Trying to apply patch for Zope 2.5 maybe this works.\nReported version is: %s" % version)
    new = __init__25
    
from DocumentTemplate import DT_Var

DT_Var.modifiers.append((tex_quote.__name__, tex_quote))
oldinit = DT_Var.Var.__init__
DT_Var.Var.__init__ = new
DT_Var.Var.__init__.im_func.func_globals.update(oldinit.im_func.func_globals)

try:
    import Products.StructuredDocument
    try:
        import stxdocpatch
    except ImportError:
        LOG('DTMLTeX', WARNING, "ImportError when applying STX patch.")
        import traceback
        traceback.print_exc()
except ImportError:
    LOG('DTMLTeX', INFO, "Product `Structured Document` not found. Not applying STX patch.")
    
import dtvarpatch

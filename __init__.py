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

$Id: __init__.py,v 1.6 2005/01/04 15:33:41 ctheune Exp $"""

import DTMLTeX
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

try:
    import Products.StructuredDocument
    try:
        import stxdocpatch
    except ImportError:
        LOG("DTMLTeX", WARNING,
            "ImportError when applying STX patch.")
        import traceback
        traceback.print_exc()
except ImportError:
    LOG("DTMLTeX", INFO,
        "Product `Structured Document` not found. " \
        "Not applying STX patch.")
    
import dtvarpatch

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

$Id: __init__.py,v 1.2 2004/03/08 16:31:06 thomas Exp $"""

__version__= '0.01'

import DTMLTeX
from tex_quote import tex_quote, __init__
from zLOG import LOG

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

from DocumentTemplate import DT_Var

DT_Var.modifiers.append((tex_quote.__name__, tex_quote))
oldinit = DT_Var.Var.__init__
DT_Var.Var.__init__ = __init__
DT_Var.Var.__init__.im_func.func_globals.update(
    oldinit.im_func.func_globals)


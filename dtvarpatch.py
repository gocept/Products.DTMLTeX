# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 2002 Andreas Kostyrka, 2004 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""Convert structured text into LaTeX.

$Id: dtvarpatch.py,v 1.3 2004/03/08 22:11:19 thomas Exp $"""

from zLOG import *

import LaTeXClass
import StructuredText.StructuredText as st

LaTeX = LaTeXClass.LaTeXClass()

def structured_tex(data, name='(Unknown name)', md={}):
    """Convert structured text into LaTeX."""

    LOG("DTMLTex", DEBUG, "structured_tex(%r,%r,%r)" % (data,name,md))
    s = data[:]

    return LaTeX(st.Document(st.Basic(s)), header=0)
    

LOG("DTMLTex", INFO, "Applying structured_tex DTML monkeypatch.")

from DocumentTemplate import DT_Var

DT_Var.special_formats["structured-tex"] = structured_tex


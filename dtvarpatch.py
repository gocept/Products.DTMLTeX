##############################################################################
#
# (c) 2002 Andreas Kostyrka
#
# Published under the
# GNU LESSER GENERAL PUBLIC LICENSE Version 2.1, February 1999
# or later versions of this LICENSE as published by the
# Free Software Foundation, Inc.
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from zLOG import *

import LaTeXClass
import StructuredText.StructuredText as st

LaTeX=LaTeXClass.LaTeXClass()

def structured_tex(data, name='(Unknown name)', md={}):
    """convert structured text into latex"""

    LOG("DTMLTex",DEBUG,"structured_tex(%r,%r,%r)" % (data,name,md))
    s = data[:]

    return LaTeX(st.Document(st.Basic(s)),header=0)
    

LOG("DTMLTex",0,"Applying structured-tex DTML monkeypatch.")

from DocumentTemplate import DT_Var

DT_Var.special_formats["structured-tex"]=structured_tex


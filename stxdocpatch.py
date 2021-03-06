# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 2002 Andreas Kostyrka, 2004 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""Render the document into PDF using LaTeX.

$Id$"""

from zLOG import *

LOG("DTMLTeX", INFO, "Applying STX patch.")

import Products.StructuredDocument.StructuredDocument as std
from OFS.DTMLMethod import decapitate
import StructuredText
import LaTeXClass
from DTMLTeX import latex

colors = ["#FFFFFF","#FF9944"]

LaTeX=LaTeXClass.LaTeXClass()

_marker = []

def pdf_method(self, REQUEST={}, RESPONSE=None, **kw):
    """Render the document given a client object, REQUEST mapping,
    Response, and key word arguments. This produces a LaTeX/PDF Version
    with standard_latex_header and standard_latex_footer."""

    # original code from OFS/DTMLDocument.py

    if not self._cache_namespace_keys:
        data = self.ZCacheable_get(default=_marker)
        if data is not _marker:
            # Return cached results.
            return data

    # Here we go on our own...

    st = StructuredText.StructuredText.Basic(self.raw)
    doc = StructuredText.StructuredText.Document(st)
    r = LaTeX(doc, header=0)

    LOG("DTMLTex",DEBUG,"REQUEST:%r" % REQUEST)
    LOG("DTMLTex",DEBUG,"RESPONSE:%r" % RESPONSE)
    LOG("DTMLTex",DEBUG,"hasattr(standard_latex_header):%d" \
        % hasattr(self,"standard_latex_header"))
    LOG("DTMLTex",DEBUG,"hasattr(standard_latex_footer):%d" \
        % hasattr(self,"standard_latex_footer"))
    if hasattr(self,'standard_latex_header') and \
           hasattr(self,'standard_latex_footer'):
        r = (
            self.standard_latex_header(self, REQUEST, RESPONSE)
            + r                         
            + self.standard_latex_footer(self, REQUEST, RESPONSE)
            )

        try:
            LOG("DTMLTex",DEBUG,"before latex run:%r" % r)
            r = "content-type: application/pdf\n\n" + latex( r )
            if type(r) is not type(''):
                return r

            if RESPONSE:
                RESPONSE.setHeader('Content-Type','application/pdf')
        except 'LatexError', (logdata, texfile):
            tf = texfile.split('\n')
            errorlines = []
            errlogtable = "<table>"
            for line in logdata:
                errline = None
                htmlline = ""
                if len(line) > 0 and line[0] == "!" or \
                       line[0:2] == "l.":
                    htmlline += "<tr bgcolor=\"#FF9944\">"
                    try:
                        errline = int(line.split(" ")[0][2:])
                        errorlines.append(errline)
                    except:
                        pass
                else:
                    htmlline += "<tr>"
                if errline is not None:
                    line = "<a href=\"#line%s\">%s</a>" \
                           % (errline, line)
                htmlline += "<td><code>"+line+"</code></td></tr>\n"

                errlogtable += htmlline
            errlogtable += "</table>" 

            texlist = []
            for item in zip(range(1, len(tf)+1), tf):
                texlist.append("<tr bgcolor=\"%s\"> <td align=\"right\"><a name=\"line%s\"><code>%s</code></a></td>" \
                               "<td><code>%s</code></td></tr>\n" % \
                                (colors[item[0] in errorlines], item[0], item[0], item[1]))

            texlogtable = "<table>" + "\n".join(texlist) + "</table>"

            # create output document with error infos
            errmsg = "<html><title>LaTeX compilation had errors.</title>" + \
                      "<body><h1>Latex output</h1>You receive this output, because latex wasn't able to compile your .tex file correctly. <hr>" + \
                     errlogtable +"<hr> <h2> Used latex content </h2>" + texlogtable + "<hr><font size=\"2\">generated by DTMLLatex / pdftex</font></body></html>"

            # append the uses text document
            RESPONSE.setHeader('Content-Type','text/html')
            return errmsg

    # original code from OFS/DTMLDocument.py again

    result = decapitate(r, RESPONSE)
    if not self._cache_namespace_keys:
        self.ZCacheable_set(result)
    return result


std.StructuredDocument.pdf = pdf_method

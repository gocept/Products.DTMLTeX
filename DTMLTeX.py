# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 1999 Marian Kelc, 2002-2004 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""DTMLTeX objects.

DTMLTeX objects are DTML-Methods that produce Postscript or PDF using
LaTeX.

$Id: DTMLTeX.py,v 1.9.2.2 2004/12/07 11:10:14 thomas Exp $"""

from Globals import HTML, HTMLFile, MessageDialog, InitializeClass
from OFS.content_types import guess_content_type
from OFS.DTMLMethod import DTMLMethod, decapitate
from OFS.PropertyManager import PropertyManager
from AccessControl import ClassSecurityInfo
from ZODB.PersistentMapping import PersistentMapping
import os.path
import re
from urllib import quote
from Products.PythonScripts.standard import html_quote

def join_dicts(a, b):
    a.update(b)
    return a

# Color for the error beautifier
errorcolor = "#fc6"

addForm = HTMLFile('dtml/texAdd', globals())

def add(self, id, title='', file='', REQUEST=None, submit=None):
    """Add a DTML TeX object with the contents of file. If
    'file' is empty, default document text is used."""
    
    if type(file) is not type(''): file=file.read()
    ob = DTMLTeX(file, __name__=id)
    ob.title = title
    id = self._setObject(id, ob)
    if REQUEST is not None:
        try: u = self.DestinationURL()
        except: u = REQUEST['URL1']
        if submit == " Add and Edit ": u = "%s/%s" % (u, quote(id))
        REQUEST.RESPONSE.redirect(u + '/manage_main')
    return ''

class DTMLTeX(DTMLMethod, PropertyManager):
    """DTMLTeX objects are DTML-Methods that produce Postscript or PDF
    using LaTeX."""

    meta_type = 'DTMLTeX'

    security = ClassSecurityInfo()
    
    index_html = None # Prevent accidental acquisition

    manage_options = DTMLMethod.manage_options + \
                     PropertyManager.manage_options

    defaultfilter = "pdf"

    filters = {'pdf': {'ct':'application/pdf',
                       'path':'/usr/bin/pdflatex', 'ext':'pdf'},
               'ps': {'ct':'application/ps',
                      'path': os.path.join(os.path.split(__file__)[0],
                                           'genlatex'),
                      'ext':'ps'}}

    default_dm_html = \
r"""\documentclass{minimal}
\begin{document}
\end{document}
"""

    security.declareProtected('View management screens',
                              'manage_editForm', 'manage',
                              'manage_main', 'manage_uploadForm',
                              'document_src', 'PrincipiaSearchSource')
    security.declareProtected('Change DTML Methods', 'manage_edit',
                              'manage_upload', 'PUT')
    security.declareProtected('Change proxy roles',
                              'manage_proxyForm', 'manage_proxy')
    security.declareProtected('View', '__call__','')
    security.declareProtected('FTP access', 'manage_FTPstat',
                              'manage_FTPget', 'manage_FTPlist')

    def __init__(self, *nv, **kw):
        DTMLMethod.__init__(self, *nv, **kw)

    security.declareProtected('View management screens', 'filterIds')
    
    def filterIds(self):
        """Lists the Ids of all available filters."""
        return self.filters.keys()
        
    def __call__(self, client=None,
                 REQUEST=None, RESPONSE=None, **kw):
        """Render the document given a client object, REQUEST mapping,
        Response, and key word arguments."""

        #XXX Here we throw away the response passed. Maybe this is
        #asking for trouble - we'll see.
        RESPONSE = self.REQUEST.RESPONSE

        #this list takes the temporary-file objects
        tmp = [] 
        
        kw['document_id'] = self.id
        kw['document_title'] = self.title
        kw['__temporary_files__'] = tmp

        # resolve dtml
        result = HTML.__call__(self, client, REQUEST, **kw)
        
        if client is None or REQUEST.has_key("tex_raw"):
            # We were either not called directly, or somebody
            # explicitly wants to see the tex code, no converted
            # postscript or pdf.
            RESPONSE.setHeader("Content-type", "application/x-tex")
            return result
        
        # Determine which latex filter to use
        used_filter = REQUEST.get('tex_filter', self.defaultfilter)
        if not used_filter in self.filterIds():
            used_filter = self.defaultfilter
        used_filter = self.filters[used_filter]

        # construct the content-type
        RESPONSE.setHeader("Content-type", used_filter['ct'])
        
        #make the distilled output from TeX
        try:
            return latex(used_filter['path'], used_filter['ext'],
                         result)
        except 'LatexError', (logdata, texfile):
            # The next lines are the Code-o-Beautifier *G

            # Pick error lines from latex log, mark up log
            errorlines = []
            contline = 0
            errlog = ""
            for line in logdata:
                line = html_quote(line);
                
                if contline:
                    errlog += "%s</a>\n</strong>" % re.sub(
                        r"^( *)", r'\1<a href="#line%s">' % errline,
                        line)
                    contline = 0
                    continue

                if line[:2] == "! ":
                    errlog += "<strong>%s\n</strong>" % line
                    continue

                if line[:2] == "l.":
                    errline = None
                    try:
                        errline = int(line.split(" ")[0][2:])
                    except:
                        pass
                    if errline is not None:
                        errorlines.append(errline)
                        contline = 1
                        errlog += \
                               "<strong><a href=\"#line%s\">%s</a>\n" \
                               % (errline, line)
                        continue
                errlog += "%s\n" % line

            # mark up LaTeX source
            tf = texfile.strip("\n").split("\n")
            numberwidth = len("%s" % len(tf))
            texlog = ""
            for (lineno, line) in zip(range(1,len(tf)+1),tf):
                line = html_quote("%*d %s" \
                                  % (numberwidth, lineno, line))
                if lineno in errorlines:
                    texlog += "<strong><a name=\"line%s\">%s</a>\n" \
                              "</strong>" % (lineno, line)
                else:
                    texlog += "%s\n" % line

            # create output document with error infos
            errmsg = \
r"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
                       "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <meta http-equiv="content-type"
          content="text/html; charset=ISO-8859-1">
    <title>LaTeX compilation had errors.</title>
    <style type="text/css">
    <!--
        strong {
            display:block;
            color:black;
            background-color:%s;
            }
    </style>
</head>
<body>
    <h1>There were LaTeX errors.</h1>

    <p>
      You receive this output because (pdf)latex wasn't able to
      compile the .tex file generated by this DTMLTeX object
      correctly. You can find the
      <a href="#latexfile">generated LaTeX file</a> at the bottom of
      this page.
    </p>

    <h2>Latex output (log file)</h2>

<pre>
%s</pre>

    <h2><a name="latexfile">Generated LaTeX content</a></h2>

<pre>
%s</pre>

</body>
</html>
""" % (errorcolor, errlog, texlog)

            RESPONSE.setHeader('Content-Type', 'text/html')
            return errmsg

    security.declareProtected('View management screens', 'getFilters')

    def getFilters(self, REQUEST=None):
        """Returns a list of all filters."""
        list = [join_dicts(value, {'mapid':id})
                for (id, value) in self.filters.items()]
        return list

InitializeClass(DTMLTeX)

#### This is for running the latex-command
from os import chdir, spawnv, waitpid, unlink, P_WAIT
from thread import start_new_thread
from time import sleep
from tempfile import mktemp
from glob import glob
import tempfile


def tmpcmd (path, args):
    chdir(tempfile.gettempdir())
    if spawnv(P_WAIT, path, args):
        raise 'CommandError'
        pass
    return

def latex(binary, ext, data):
    try:
        base = mktemp()
        tex = base + ".tex"
        output = base + ".%s" % ext
        log = base + ".log" 
        
        # create temporary tex file
        f = open(tex, "w")
        f.write(data)
        f.close()

        stdout = []   # list of output lines of the command
        rerun = 1     # flag for running the command again
        runs = 0      # count of runs already done.

        while rerun and runs <= 10:
            rerun = 0

            try:
                tmpcmd(binary,
                       (binary, '-interaction=batchmode', tex)) 
                runs += 1
            except 'CommandError':
                stdout = open(log, "r").read().split("\n")
                raise 'LatexError', (stdout, data)
                
            stdout = open(log, "r").read().split("\n")

            # if the output contains hints about rerunning the
            # generation (content etc) we do so ...
            # but at maximum 10 times ...
            for line in stdout:
                if line.lower().find("no file") != -1:
                    rerun = 1
                if line == "! Emergency stop." or \
                       line == "No pages of output.":
                    raise 'LatexError', (stdout, data)
        
        f  = open(output, "rb")
        out = f.read()
        f.close()
    finally:
        for i in glob(base + ".*"):
            unlink(i)
    return out

### Extension to File class follows
import OFS.Image
import mimetypes

def delete_tempfile_thread(tmp, t):
    sleep(t)
    unlink(tmp)
    return

def create_temp(self, t=60):

    suffix = mimetypes.guess_extension(self.content_type) or ""
    if suffix == '.jpe':
        suffix = '.jpg'

    base = mktemp()
    os.mkdir(base)
    tmp = base + "/file" + suffix
    f = open(tmp, "w")
    data = self.data
    if type(data) is not type(''):
        while data:
            f.write(data.data)
            data = data.next
    else:
        f.write(data)
    f.close()
    # this removes the temporary file in t seconds
    #    start_new_thread(delete_tempfile_thread, (tmp, t))
    return tmp

OFS.Image.File.create_temp = create_temp

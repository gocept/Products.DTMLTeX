# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 1999 Marian Kelc, 2002-2007 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""DTMLTeX objects.

DTMLTeX objects are DTML-Methods that produce Postscript or PDF using
LaTeX.

$Id$"""

# Python imports
import os.path
from urllib import quote
from tempfile import mkstemp, gettempdir
from os import write, close, \
    chdir, listdir, getcwd, unlink, rmdir, \
    spawnv, waitpid, P_WAIT

# Zope imports
from Globals import HTML, HTMLFile, InitializeClass
from OFS.DTMLMethod import DTMLMethod
from OFS.PropertyManager import PropertyManager
from AccessControl import ClassSecurityInfo
from DocumentTemplate.DT_Util import TemplateDict
from Products.PythonScripts.standard import html_quote

# Sibling imports
from Products.DTMLTeX import texvar

# Some helper functions
def join_dicts(a, b):
    a.update(b)
    return a

def TrueOrFalse(x):
    return x not in (False, 0, 'False', 'false', '0',
                     'No', 'no', 'Off', 'off')

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

    # Add texvar
    commands = {}
    commands.update(DTMLMethod.commands)
    commands['texvar'] = texvar.TEXVar

    index_html = None # Prevent accidental acquisition

    manage_options = DTMLMethod.manage_options + \
                     PropertyManager.manage_options

    filters = {'pdf': {'ct':'application/pdf',
                       'path':'/usr/bin/pdflatex',
                       'ext':'pdf'},
               'ps': {'ct':'application/ps',
                      'path': os.path.join(os.path.split(__file__)[0],
                                           'genlatex'),
                      'ext':'ps'}}

    encoding = "ascii" # Dumb but makes no assumptions about usage of
                       # LaTeX's inputenc package.

    tex_raw = False
    tex_filter = "pdf"

    deliver = True
    download = False
    filename = '' # Object ID will be used as a fall-back.

    _properties = (
        {'id':'title', 'type':'string'},
        {'id':'encoding', 'type':'string'},
        {'id':'filename', 'type':'string'},
        {'id':'download', 'type':'boolean'}
        )

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

    def __call__(self, client=None, REQUEST=None, RESPONSE=None,
                 **kw):
        """Render the document given a client object, REQUEST mapping,
        and key word arguments."""

        # Implement the option overriding cascade.
        def get_option(name):
            temp = getattr(self, name)
            if REQUEST is not None:
                temp = REQUEST.get(name, temp)
            return kw.get(name, temp)

        kw['document_id'] = self.id
        kw['document_title'] = self.title

        # Resolve DTML.
        tex_code = HTML.__call__(self, client, REQUEST, **kw)

        # If, for some reason, nothing came back, we're done.
        if tex_code == '':
            return ''

        # A comment in DocumentTemplate.DT_String.__call__ indicates
        # that being passed a TemplateDict as the REQUEST is
        # characteristic for a sub-template (nested call). In that
        # case, we're done.
        if isinstance(REQUEST, TemplateDict):
            return tex_code

        # We're still here, so we're the top template.

        # At some point we need to care about character encoding.
        # What we write out to the TeX file must be a byte string.
        # Since we don't want to fool people, we do this before
        # returning anything, even raw TeX code.

        # By going through Unicode we deal with whatever encoding our
        # input came in. XXX Which is? Hopefully the system enc...
        if not isinstance(tex_code, unicode):
            tex_code = tex_code.decode()

        # Find the encoding to use.
        encoding = get_option('encoding')

        # Encoding errors are handled by silently replacing the
        # offending characters with place holders. XXX Is this OK?
        # There can still be trouble later if working with UTF-8:
        # Since Python can't know about the subset of UTF-8 known to
        # LaTeX's utf8.def/utf8enc.dfu, it is possible that characters
        # get thrown at LaTeX that make it kick and scream.
        # XXX Fixing this means patching LaTeX's inputenc mechanism so
        # it doesn't fuck up but either uses place holders or silently
        # weeps into the log file. We could use this for warning the
        # user about missing characters.
        tex_code = tex_code.encode(encoding, 'replace')

        # Some simplification can be done to make the LaTeX source
        # more readable.
        tex_code = tex_code.strip("\n")

        # This is the first time we might have something of interest.

        # Find out what to do with the whole mess.
        tex_raw = TrueOrFalse(get_option('tex_raw'))
        if not tex_raw:
            tex_filter = get_option('tex_filter')
            if not tex_filter in self.filterIds():
                tex_filter = DTMLTeX.tex_filter

            tex_filter = self.filters[tex_filter]

        deliver = TrueOrFalse(get_option('deliver'))
        if deliver:
            # In order to deliver anything, we need a
            # RESPONSE. Changing the RESPONSE doesn't hurt since we
            # won't pass it to nested calls anyway.
            if RESPONSE is None and REQUEST is not None:
                RESPONSE = REQUEST.RESPONSE

            # If there's still no RESPONSE, we can't deliver.
            if RESPONSE is None:
                deliver = False
            else:
                download = TrueOrFalse(get_option('download'))

                filename = get_option('filename')
                if filename is None or '' == filename:
                    filename = self.getId()

        # Do it.
        if tex_raw:
            # Somebody explicitly wants to see the tex code, not a
            # typeset postscript or pdf document.
            if deliver:
                RESPONSE.setHeader(
                    "Content-type",
                    "application/x-tex; name=%s.tex" % filename)
                if download:
                    RESPONSE.setHeader(
                        "Content-Disposition",
                        "attachment; filename=%s.tex" % filename)
            return tex_code

        # OK, we're still here. This means we have to throw the stuff
        # at the typesetter.
        try:
            result = latex(tex_filter['path'], tex_filter['ext'],
                           tex_code)
        except 'LatexError', logdata:
            errmsg = compose_errmsg(logdata, tex_code)

            if deliver:
                RESPONSE.setHeader("Content-type", "text/html")

            return errmsg

        # Still here? Fine. Now we have a typeset document to return.
        if deliver:
            RESPONSE.setHeader(
                "Content-type",
                "%s; name=%s.%s" % (tex_filter['ct'],
                                    filename,
                                    tex_filter['ext']))
            if download:
                RESPONSE.setHeader(
                    "Content-Disposition",
                    "attachment; filename=%s.%s" % (
                        filename, tex_filter['ext']))
        return result

    security.declareProtected('View management screens', 'filterIds')
    def filterIds(self):
        """Lists the Ids of all available filters."""
        return self.filters.keys()

    security.declareProtected('View management screens', 'getFilters')
    def getFilters(self, REQUEST=None):
        """Returns a list of all filters."""
        list = [join_dicts(value, {'mapid':id})
                for (id, value) in self.filters.items()]
        return list

InitializeClass(DTMLTeX)

# This is for running the latex-command
def latex(binary, ext, tex_code):
    tempdir = gettempdir()

    handle, texpath = mkstemp('.tex')

    tex = os.path.basename(texpath)
    texbasedot = tex[:-3]
    output = texbasedot + ext
    log = texbasedot + 'log'

    # create temporary tex file
    write(handle, tex_code)
    close(handle)

    rerun = True  # flag for running the command again
    runs = 0      # count of runs already done.

    cwd = getcwd()
    try:
        chdir(tempdir)
        while rerun and runs <= 10:
            rerun = False

            try:
                if spawnv(P_WAIT, binary,
                          (binary, '-interaction=batchmode', tex)):
                    raise 'CommandError'
                runs += 1
            except ('CommandError', OSError), e:
                # OSError occurs on Win when a file (e.g. image) is not found
                try:
                    logdata = file(log).readlines()
                except IOError:
                    if e is None:
                        e = 'spawnv returned a value <> 0'
                    logdata = [e]
                raise 'LatexError', logdata

            logdata = file(log).readlines()

            # if the output contains hints about rerunning the
            # generation (content etc) we do so ...
            # but at maximum 10 times ...
            for line in logdata:
                if ((line.startswith("LaTeX Warning:") or
                     line.startswith("Package longtable Warning:")) and
                    line.lower().find("rerun") != -1):
                    rerun = True
                if line == "! Emergency stop." or \
                       line == "No pages of output.":
                    raise 'LatexError', logdata

        out = file(output, "rb").read()
    finally:
        chdir(cwd)

        for i in listdir(tempdir):
            # XXX Is this safe? If a filename created by mkstemp is
            # allowed to contain a dot, this filter is not enough.
            if i.startswith(texbasedot):
                unlink(os.path.join(tempdir, i))

    return out

# The next lines are the Code-o-Beautifier *G
def compose_errmsg(logdata, tex_code):
    # Pick error lines from latex log, mark up log
    errorlines = []
    contline = 0
    errlog = ""
    for line in logdata:
        line = html_quote(line);

        if contline:
            stripped_line = line.lstrip()
            whitespace = line[:len(line)-len(stripped_line)]
            errlog += '%s<a href="#line%s">%s</a>\n</strong>' % \
                (whitespace, errline, stripped_line)
            contline = 0
            continue

        if line[:2] == "! ":
            errlog += "<strong>%s</strong>" % line
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
                    "<strong><a href=\"#line%s\">%s</a>" \
                    % (errline, line.rstrip())
                continue

        errlog += "%s" % line

    # mark up LaTeX source
    tf = tex_code.split("\n")
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
r'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
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
      You receive this output because (pdf)latex was not able to
      compile the .tex file generated by this DTMLTeX object
      correctly. You can find the
      <a href="#latexfile">generated LaTeX file</a> at the bottom of
      this page.
    </p>

    <h2>LaTeX output (log file)</h2>

<pre>
%s</pre>

    <h2><a name="latexfile">Generated LaTeX content</a></h2>

<pre>
%s</pre>

</body>
</html>
''' % (errorcolor, errlog, texlog)

    return errmsg

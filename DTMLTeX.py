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
# $Id: DTMLTeX.py,v 1.1.1.1.8.13 2003/11/17 21:32:05 ctheune Exp $

"""DTML TeX objects."""

__version__='0.3'

from OFS import PropertyManager
from Globals import HTML, HTMLFile, MessageDialog, InitializeClass
from OFS.content_types import guess_content_type
from OFS.DTMLMethod import DTMLMethod, decapitate
from AccessControl import ClassSecurityInfo
from ZODB.PersistentMapping import PersistentMapping
import os.path
from string import strip

from urllib import quote

def join_dicts(a, b):
    a.update(b)
    return a

# Colors for the error beautifier
colors = ["#FFFFFF","#FF9944"]

addForm=HTMLFile('dtml/texAdd', globals())

def add(self, id, title='', file='', REQUEST=None, submit=None):
    """Add a DTML TeX object with the contents of file. If
    'file' is empty, default document text is used.
    """
    if type(file) is not type(''): file=file.read()
    ob=DTMLTeX(file, __name__=id)
    ob.title=title
    id=self._setObject(id, ob)
    if REQUEST is not None:
        try: u=self.DestinationURL()
        except: u=REQUEST['URL1']
        if submit==" Add and Edit ": u="%s/%s" % (u,quote(id))
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    return ''

class DTMLTeX( DTMLMethod, PropertyManager.PropertyManager):
    """DTML TeX objects are DTML-Methods that produce Postscript from TeX"""
    
    meta_type='DTML TeX'

    security = ClassSecurityInfo()
    
    index_html=None # Prevent accidental acquisition

    manage_options=({'label':'Edit', 'action':'manage_main'},
                    {'label':'View', 'action':''} ) + \
                    PropertyManager.PropertyManager.manage_options + \
                   ( {'label':'Proxy', 'action':'manage_proxyForm'},
                     {'label':'Security', 'action':'manage_access'} )

    _properties = ( { 'id':'defaultfilter', 'type':'selection', 'select_variable': 'filterIds', 
                      'mode':'w'}, )

    _temppath = "/tmp"
    defaultfilter = "pdf"

    filters = { 'pdf' : { 'ct':'application/pdf', 'path':'/usr/bin/pdflatex', 'ext':'pdf'},
                'ps' : {'ct':'application/ps', 'path': os.path.join(os.path.split(__file__)[0],'genlatex'), 'ext':'ps'}}

    security.declareProtected('View management screens', 'manage_editForm', 'manage', 'manage_main', 'manage_uploadForm', 'document_src', 'PrincipiaSearchSource')
    security.declareProtected('Change DTML Methods', 'manage_edit', 'manage_upload', 'PUT')
    security.declareProtected('Change proxy roles', 'manage_proxyForm', 'manage_proxy')
    security.declareProtected('View', '__call__','')
    security.declareProtected('FTP access', 'manage_FTPstat','manage_FTPget','manage_FTPlist')

    def __init__(self, *nv, **kw):
        DTMLTeX.inheritedAttribute('__init__')(self, *nv, **kw)
        self.__version__ = "0.3"

    security.declareProtected('View management screens', 'filterIds')
    def filterIds(self):
        """Lists the Ids of all available filters."""
        return self.filters.keys()
        
    def __call__(self, client=None, REQUEST=None, RESPONSE=None, **kw):
        """Render the document given a client object, REQUEST mapping,
        Response, and key word arguments."""

        if REQUEST is None:
            REQUEST = self.REQUEST
            RESPONSE = REQUEST.RESPONSE

        #this list takes the temporary-file objects
        tmp = [] 
        
        kw['document_id']   =self.id
        kw['document_title']=self.title
        kw['__temporary_files__'] =tmp

        # resolve dtml
        result = apply(HTML.__call__, (self, client, REQUEST), kw)
        
        if client is None or REQUEST.has_key("tex_raw"):
            # We were either not callen directly, or somebody explicitly
            # wants to see the tex code, no converted postscript or pdf.
            return result
        
        # Determine which latex filter to use
        used_filter = REQUEST.get('tex_filter', self.defaultfilter)
        if not used_filter in self.filterIds():
            used_filter = self.defaultfilter
        used_filter = self.filters[used_filter]

        # construct the content-type
        REQUEST.RESPONSE.setHeader("Content-type", used_filter['ct'])
        
        #make the distilled output from TeX
        try:
            return latex(used_filter['path'], used_filter['ext'], self._temppath, result)
        except 'LatexError', (logdata, texfile):
            # The next lines are the Code-o-Beautifier *G
            tf = texfile.split("\n")

            errorlines = []
            # create coloured output with red lines for error infos
            errlogtable = "<table>"
            for line in logdata:
                errline = None
                htmlline = ""
                if len(line)>0 and line[0] == "!" or \
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
                    line = "<a href=\"#line%s\">%s</a>" % (errline, line)
                htmlline += "<td><code>"+line+"</code></td></tr>\n"

                errlogtable += htmlline
            errlogtable += "</table>" 

            texlist = []
            for item in zip(range(1,len(tf)+1),tf):
                texlist.append("<tr bgcolor=\"%s\"> <td align=\"right\">" \
                                "<a name=\"line%s\"><code>%s</code></a></td>" \
                               "<td><code>%s</code></td></tr>\n" % \
                                (colors[item[0] in errorlines], item[0], 
                                 item[0], item[1]))

            texlogtable = "<table>" + "\n".join(texlist) + "</table>"

            # create output document with error infos
            errmsg = "<html><title>LaTeX compilation had errors.</title>" + \
                      "<body><h1>Latex output</h1>You receive this output, "+\
                      "because latex wasn't able to compile your .tex file "+\
                      "correctly. <hr>" + \
                     errlogtable +"<hr> <h2> Used latex content </h2>" + \
                     texlogtable + "<hr><font size=\"2\">generated by "+\
                     "DTMLTeX</font></body></html>"

            REQUEST.RESPONSE.setHeader('Content-Type','text/html')
            return errmsg

    security.declareProtected('View management screens', 'getFilters')
    def getFilters(self, REQUEST=None):
        """Returns a list of all filters."""
        list = [ join_dicts(value, { 'mapid':id }) for (id, value) in 
                                            self.filters.items() ]
        return list

InitializeClass(DTMLTeX)

#### This is for running the latex-command
from os import chdir, spawnv, waitpid, unlink, P_WAIT
from thread import start_new_thread
from time import sleep
from tempfile import mktemp
from glob import glob
import tempfile


def tmpcmd ( path, args ):
    chdir( tempfile.tempdir )
    if spawnv(P_WAIT, path, args ):
        raise 'CommandError'
        pass
    return

def latex(binary, ext, temp, data):
    try:
    
        tempfile.tempdir = temp
        base = mktemp()
        tex  = base + ".tex"
        output  = base + ".%s" % ext
        log  = base + ".log" 
        
        # create temporary tex file
        f= open( tex, "w" )
        f.write( data )
        f.close()

        stdout = []             # list of output lines of the command
        rerun = 1               # flag for running the command again
        runs = 0                # count of runs already done.

        while rerun and runs <= 10:
            rerun = 0

            try:
                tmpcmd(binary, (binary,'-interaction=batchmode',tex)) 
                runs += 1
            except 'CommandError':
                stdout = open(log,"r").read().split("\n")
                raise 'LatexError', (stdout, data)
                
            stdout = open(log,"r").read().split("\n")
            

            # if the output contains hints about rerunning the generation (content etc) we do so ...
            # but at maximum 10 times ...
            for line in stdout:
                if line.lower().find("no file") != -1:
                    rerun = 1
                if line == "! Emergency stop." or line == "No pages of output.":
                    raise 'LatexError', (stdout, data)
        
        f  = open(output, "r")
        out= f.read()
        f.close()
    finally:
        for i in glob(base+".*"):
            unlink( i )
    return out

### Extension to File class follows
import OFS.Image

def delete_tempfile_thread( tmp, t ):
    sleep( t )
    unlink( tmp )
    return

def create_temp( self , t=60, sfx=0 ):
    if hasattr( self, 'suffix' ):
        suffix= self.suffix
    else:
        suffix= ''
    base = mktemp()
    os.mkdir(base)
    tmp  = base + "/data."+suffix
    f= open( tmp, "w" )
    data= self.data
    if type(data) is not type(''):
        while data:
            f.write(data.data)
            data= data.next
    else:
        f.write( data )
    f.close()
    #this removes the temporary file in t seconds
    start_new_thread( delete_tempfile_thread, (tmp,t) )
    if sfx:
        return tmp
    else:
        return base

OFS.Image.File.create_temp= create_temp


# $Log: DTMLTeX.py,v $
# Revision 1.1.1.1.8.13  2003/11/17 21:32:05  ctheune
#  - Security updates
#  - Fix for Bug 1455
#  - Supporting new apeconf
#
# Revision 1.1.1.1.8.12  2003/11/17 19:10:32  ctheune
#  - Fix for Bug 1419
#
# Revision 1.1.1.1.8.11  2003/11/17 18:49:28  ctheune
#  - minor cleanups
#  - fix for bug #1419
#
# Revision 1.1.1.1.8.10  2003/11/14 22:21:57  ctheune
#  - checking spawnv to avoid forking (need windows compatibility)
#
# Revision 1.1.1.1.8.9  2003/09/15 16:27:42  ctheune
#  - added support for DTMLTeXFile
#
# Revision 1.1.1.1.8.8  2003/07/17 10:35:17  ctheune
#  - added new DTMLTeXFile
#  - fixed RESPONSE reference in DTMLTeX.py
#
# Revision 1.1.1.1.8.7  2003/03/12 06:50:42  ctheune
# fixed bug with creating external tempfiles for graphics
#
# Revision 1.1.1.1.8.6  2002/12/29 16:02:51  ctheune
# Added structured text support
#
# Revision 1.1.1.1.8.5  2002/07/31 12:28:04  ctheune
# Look into the changelog ...
#
# Revision 1.1.1.1.8.4  2002/07/24 23:30:44  ctheune
# better error handling of latex log
#
# Revision 1.1.1.1.8.3  2002/07/24 23:23:04  ctheune
# now for the real fix
#
# Revision 1.1.1.1.8.2  2002/07/24 23:21:30  ctheune
# wrong call to latex()
#
# Revision 1.1.1.1.8.1  2002/07/24 22:19:43  ctheune
# provided the first 0.3 changes:
#
# - properties for tmp, tex binary and mime type
# - raw tex output
# - 2.4 support
#
# Revision 1.1.1.1  2002/05/30 13:37:18  ctheune
# Imported sources
#
# Revision 1.4  2002/02/20 10:28:18  zagy
# changed behaviour if file is include in another dtml
#  (just puts out the rendered dtml instead of this fancy link)
#


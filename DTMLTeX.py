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
# $Id: DTMLTeX.py,v 1.1.1.1.8.4 2002/07/24 23:30:44 ctheune Exp $

"""DTML TeX objects."""

__version__='0.3'

from OFS import PropertyManager
from Globals import HTML, HTMLFile, MessageDialog
from OFS.content_types import guess_content_type
from OFS.DTMLMethod import DTMLMethod, decapitate
from urllib import quote

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
    
    index_html=None # Prevent accidental acquisition

    manage_options=({'label':'Edit', 'action':'manage_main'},
                    {'label':'Upload', 'action':'manage_uploadForm'},
                    {'label':'View', 'action':''},
                    {'label':'Proxy', 'action':'manage_proxyForm'},
                    {'label':'Security', 'action':'manage_access'},
                   ) + PropertyManager.PropertyManager.manage_options

    _properties = ( { 'id':'latexbinary', 'type':'string', 'mode':'w'},
                    { 'id':'mimetype', 'type':'string', 'mode':'w'},
                    { 'id':'temppath', 'type':'string', 'mode':'w'} )

    latexbinary = "/usr/bin/pdftex"
    mimetype = "application/pdf"
    temppath = "/tmp"

    __ac_permissions__=(
    ('View management screens',
     ('manage_editForm', 'manage', 'manage_main', 'manage_uploadForm',
      'document_src', 'PrincipiaSearchSource')),
    ('Change DTML Methods',     ('manage_edit', 'manage_upload', 'PUT')),
    ('Change proxy roles', ('manage_proxyForm', 'manage_proxy')),
    ('View', ('__call__', '')),
    ('FTP access', ('manage_FTPstat','manage_FTPget','manage_FTPlist')),
    )

    def __call__(self, client=None, REQUEST={}, RESPONSE=None, **kw):
        """Render the document given a client object, REQUEST mapping,
        Response, and key word arguments."""
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
        
        # construct the content-type
        if REQUEST.has_key("tex_ct"):
            if str(REQUEST["tex_ct"]).find("/") == -1:
                content_type = self.mimetype + "=" + REQUEST["tex_ct"]
            else:
                content_type = REQUEST["tex_ct"]
        else:
            content_type = self.mimetype
            
        REQUEST.RESPONSE.setHeader("content-type", content_type)
        
        #make the distilled output from TeX
        try:
            return latex(self.latexbinary, self.temppath, result)
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
                texlist.append("<tr bgcolor=\"%s\"> <td align=\"right\"><a name=\"line%s\"><code>%s</code></a></td>" \
                               "<td><code>%s</code></td></tr>\n" % \
                                (colors[item[0] in errorlines], item[0], item[0], item[1]))

            texlogtable = "<table>" + "\n".join(texlist) + "</table>"

            # create output document with error infos
            errmsg = "<html><title>LaTeX compilation had errors.</title>" + \
                      "<body><h1>Latex output</h1>You receive this output, because latex wasn't able to compile your .tex file correctly. <hr>" + \
                     errlogtable +"<hr> <h2> Used latex content </h2>" + texlogtable + "<hr><font size=\"2\">generated by DTMLLatex / pdftex</font></body></html>"

            RESPONSE.setHeader('Content-Type','text/html')
            return errmsg



#### This is for running the latex-command
from os import chdir, execv, fork, waitpid, unlink
from thread import start_new_thread
from time import sleep
from tempfile import mktemp
from glob import glob
import tempfile


def tmpcmd ( path, args ):
    pid= fork()
    if pid==0:
        #we are the child
        chdir( tempfile.tempdir )
        execv( path, args )
    elif pid<0:
        #something goes wrong
        raise 'cant fork for command'
    if waitpid(pid,0)[1]:
        raise 'CommandError'
        pass
    return

def latex(binary, temp, data):
    try:
    
        tempfile.tempdir = temp
        base = mktemp()
        tex  = base + ".tex"
        pdf  = base + ".pdf"
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
        
        f  = open( pdf, "r" )
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
    tmp  = base + suffix
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


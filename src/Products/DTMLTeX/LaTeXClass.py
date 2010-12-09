# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 2002 Andreas Kostyrka, 2004 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""LaTeXClass parses structured text into LaTeX.

$Id$"""

class LaTeXClass:
    """LaTeXClass parses structured text into LaTeX."""

    element_types={
        '#text': '_text',
        'StructuredTextDocument': 'document',
        'StructuredTextParagraph': 'paragraph',
        'StructuredTextExample': 'example',
        'StructuredTextBullet': 'bullet',
        'StructuredTextNumbered': 'numbered',
        'StructuredTextDescription': 'description',
        'StructuredTextDescriptionTitle': 'descriptionTitle',
        'StructuredTextDescriptionBody': 'descriptionBody',
        'StructuredTextSection': 'section',
        'StructuredTextSectionTitle': 'sectionTitle',
        'StructuredTextLiteral': 'literal',
        'StructuredTextEmphasis': 'emphasis',
        'StructuredTextStrong': 'strong',
        'StructuredTextLink': 'link',
        'StructuredTextXref': 'xref',
        'StructuredTextInnerLink':'innerLink',
        'StructuredTextNamedLink':'namedLink',
        'StructuredTextUnderline':'underline',
        'StructuredTextTable':'table',
        'StructuredTextSGML':'sgml',
        }


    def dispatch(self, doc, level, output):
        getattr(self, self.element_types[doc.getNodeName()])(
            doc, level, output)
        
    def __call__(self, doc, level=1, header=1):
        r = []
        self.header = header
        self.dispatch(doc, level-1, r.append)
        return string.join(r, '')

    def _text(self, doc, level, output):
        output(tex_quote((doc.getNodeValue())))

    def document(self, doc, level, output):
        children = doc.getChildNodes()

        output("%begin document\n")

#        if (children and
#            children[0].getNodeName() == 'StructuredTextSection'):
#            output('<head>\n<title>%s</title>\n</head>\n' %
#                   children[0].getChildNodes()[0].getNodeValue())
            
        for c in children:
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)

        output("%end document\n")


    def section(self, doc, level, output):
        children = doc.getChildNodes()
        for c in children:
            getattr(self, self.element_types[c.getNodeName()])(
                c, level+1, output)
        
    def sectionTitle(self, doc, level, output):
        sections = ['chapter', 'section', 'subsection',
                    'subsubsection', 'paragraph', 'subparagraph']
        
        output('\\%s{' % sections[level])
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        output('}\n')

    def description(self, doc, level, output):
        p = doc.getPreviousSibling()
        if p is None or p.getNodeName() is not doc.getNodeName():            
            output('\\begin{description}\n')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        n = doc.getNextSibling()
        if n is None or n.getNodeName() is not doc.getNodeName():            
            output('\\end{description}\n')
        
    def descriptionTitle(self, doc, level, output):
        output('\\item[')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        output('] ')
        
    def descriptionBody(self, doc, level, output):
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        output('\n')

    def bullet(self, doc, level, output):
        p = doc.getPreviousSibling()
        if p is None or p.getNodeName() is not doc.getNodeName():
            output('\n\\begin{itemize}\n')
        output('\\item ')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        n = doc.getNextSibling()
        output('\n')
        if n is None or n.getNodeName() is not doc.getNodeName():            
            output('\n\\end{itemize}\n')

    def numbered(self, doc, level, output):
        p = doc.getPreviousSibling()
        if p is None or p.getNodeName() is not doc.getNodeName():            
            output('\n\\begin{enumerate}\n')
        output('\\item ')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        n = doc.getNextSibling()
        output('\n')
        if n is None or n.getNodeName() is not doc.getNodeName():
            output('\\end{enumerate}\n')

    def example(self, doc, level, output):
        i = 0
        for c in doc.getChildNodes():
            if i == 0:
                output('\n\\begin{verbatim}\n')
                output(c.getNodeValue())
                output('\n\\end{verbatim}\n')
            else:
                getattr(self, self.element_types[c.getNodeName()])(
                    c, level, output)

    def paragraph(self, doc, level, output):
        output('\n\n')
        for c in doc.getChildNodes():
            if c.getNodeName() in ['StructuredTextParagraph']:
                getattr(self, self.element_types[c.getNodeName()])(
                    c, level, output)
            else:
                getattr(self, self.element_types[c.getNodeName()])(
                    c, level, output)
        output('\\par\n')

    def link(self, doc, level, output):
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        output('(\\texttt{%s})' % doc.href)

    def emphasis(self, doc, level, output):
        output('{\\emph')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        output('}')

    def literal(self, doc, level, output):
        output('\\begin{verbatim}')
        for c in doc.getChildNodes():
            output(cgi.escape(c.getNodeValue()))
        output('\\end{verbatim}')

    def strong(self, doc, level, output):
        output('\\textbf{')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
        output('}')
     
    def underline(self, doc, level, output):
#        output("<u>")
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
#        output("</u>")
          
    def innerLink(self, doc, level, output):
#        output('<a href="#ref');
#        for c in doc.getChildNodes():
#            getattr(self, self.element_types[c.getNodeName()])(
#                c, level, output)
#        output('">[')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
#        output(']</a>')
    
    def namedLink(self, doc, level, output):
#        output('<a name="ref')
#        for c in doc.getChildNodes():
#            getattr(self, self.element_types[c.getNodeName()])(
#                c, level, output)
#        output('">[')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)
#        output(']</a>')
    
    def sgml(self, doc, level, output):
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(
                c, level, output)

    def xref(self, doc, level, output):
#        val = doc.getNodeValue()
#        output('<a href="#ref%s">[%s]</a>' % (val, val) )
        output(val)
    
    def table(self, doc, level, output):
        """A StructuredTextTable holds StructuredTextRow(s) which
        holds StructuredTextColumn(s). A StructuredTextColumn is a
        type of StructuredTextParagraph and thus holds the actual
        data."""
        
        output("\\textbf{Tables not yet supported in STX"
               "$\\rightarrow$ \\LaTeX conversions.}")
        return None
        output('<table border="1" cellpadding="2">\n')
        for row in doc.getRows()[0]:
            output("<tr>\n")
            for column in row.getColumns()[0]:
                if hasattr(column,"getAlign"):
                    str = '<%s colspan="%s" align="%s" valign="%s">' % (column.getType(),
                                                                  column.getSpan(),
                                                                  column.getAlign(),
                                                                  column.getValign())
                else:
                    str = '<td colspan="%s">' % column.getSpan()
                output(str)
                for c in column.getChildNodes():
                    getattr(self, self.element_types[c.getNodeName()])(c, level, output)
                if hasattr(column,"getType"):
                    output("</"+column.getType()+">\n")
                else:
                    output("</td>\n")
            output("</tr>\n")
        output("</table>\n")

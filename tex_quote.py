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
# $Id: tex_quote.py,v 1.1 2002/05/30 13:37:18 ctheune Exp $

replacement_table =  \
	[	("\\", "\textbackslash"),
	 	("$", "\$"),
		("&", "\&"),
		("%", "\%"),
		("#", "\#"),
		("_", "\_"),
		("{", "\{"),
		("}", "\}"),
		("~", "\textasciitilde"),
		("^", "\textasciicircum"),
		("|", "\textbar"),
		("<", "\textless"),
		(">", "\textgreater") ]

def tex_quote(data, name='(Unknown name)', md={}):
	"""A dtml modifier, that returns quoted text for TeX."""
	s = data[:]
	for replacement in replacement_table:
		s=s.replace(replacement[0],replacement[1])
	return s

def __init__(self, args, fmt='s'):
        if args[:4]=='var ': args=args[4:]
        args = parse_params(args, name='', lower=1, upper=1, expr='',
                            capitalize=1, spacify=1, null='', fmt='s',
                            size=0, etc='...', thousands_commas=1,
                            html_quote=1, url_quote=1, sql_quote=1,
                            url_quote_plus=1, missing='',
                            newline_to_br=1, url=1, tex_quote=1)
        self.args=args

        self.modifiers=tuple(
            map(lambda t: t[1],
                filter(lambda m, args=args, used=args.has_key:
                       used(m[0]) and args[m[0]],
                       modifiers)))

        name, expr = name_param(args,'var',1)

        self.__name__, self.expr = name, expr
        self.fmt = fmt

        if len(args)==1 and fmt=='s':
            if expr is None: expr=name
            else: expr=expr.eval
            self.simple_form=('v', expr)
        elif len(args)==2  and fmt=='s' and args.has_key('html_quote'):
            if expr is None: expr=name
            else: expr=expr.eval
            self.simple_form=('v', expr, 'h')

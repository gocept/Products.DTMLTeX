# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 1999 Marian Kelc, 2002-2004 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""A DTML modifier that returns text quoted for LaTeX.

$Id: tex_quote.py,v 1.4 2004/03/08 18:43:38 thomas Exp $"""

replacement_table = [("\\", r"\textbackslash"),
                     ("$", r"\$"),
                     ("&", r"\&"),
                     ("%", r"\%"),
                     ("#", r"\#"),
                     ("_", r"\_"),
                     ("{", r"\{"),
                     ("}", r"\}"),
                     ("~", r"\textasciitilde"),
                     ("^", r"\textasciicircum"),
                     ("|", r"\textbar"),
                     ("<", r"\textless"),
                     (">", r"\textgreater")]

def tex_quote(data, name='(Unknown name)', md={}):
    """A DTML modifier that returns text quoted for LaTeX."""
    s = data[:]
    for replacement in replacement_table:
        s = s.replace(replacement[0], replacement[1])
    return s

def newline_to_dbs(data, name='(Unknown name)', md={}):
    """A DTML modifier that changes newlines to LaTeX linebreaks."""
    s = data[:].replace("\n", r"\\")
    return s

def __init__25(self, args, fmt='s'):
        if args[:4]=='var ': args=args[4:]
        args = parse_params(args, name='', lower=1, upper=1, expr='',
                            capitalize=1, spacify=1, null='', fmt='s',
                            size=0, etc='...', thousands_commas=1,
                            html_quote=1, url_quote=1, sql_quote=1,
                            url_quote_plus=1, missing='',
                            newline_to_br=1, url=1,
                            tex_quote=1, newline_to_dbs=1)
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

def __init__24(self, args, fmt='s'):
        if args[:4]=='var ': args=args[4:]
        args = parse_params(args, name='', lower=1, upper=1, expr='',
                            capitalize=1, spacify=1, null='', fmt='s',
                            size=0, etc='...', thousands_commas=1,
                            html_quote=1, url_quote=1, sql_quote=1,
                            url_quote_plus=1, missing='',
                            newline_to_br=1, url=1,
                            tex_quote=1, newline_to_dbs=1)
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
            self.simple_form = expr,

# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 1999 Marian Kelc, 2002-2004 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""A DTML tag that allows modification of the value with respect
to tex specifics.

$Id: texvar.py,v 1.2 2005/01/04 18:49:53 thomas Exp $"""

from ZPublisher.TaintedString import TaintedString

from DocumentTemplate.DT_Var import Var
from DocumentTemplate.DT_Util import parse_params, name_param, ustr

def replace_map(value, map):
    """Helper method to make multiple replacements that are
       described in a dictionary
    """
    for old, new in map:
        value = value.replace(old, new)
    return value

class TEXVar:
    name = "texvar"

    def __init__(self, args):
        args = parse_params(args, name='', expr='', null='',
                            tex_quote=1, format_maps='')

        name, expr = name_param(args, 'texvar', 1)
        if expr is None:
            expr = name
        else:
            expr = expr.eval
        self.__name__ = name
        self.expr = expr

        self.args = args
    
    def render(self, md):
        name = self.__name__
        args = self.args

        expr = self.expr
        if type(expr) is type(''):
            val = md[expr]
        else:
            val = expr(md)

        if not val and val != 0 and args.has_key('null'):
            # check for null (false but not zero, including None, [], '')
            val = args['null']

        if not isinstance(val, TaintedString):
            val = ustr(val)
            
        if self.args.has_key('tex_quote'):
            val = replace_map(val, maps['tex_quote'])

        if self.args.has_key('format_maps'):
            selected_maps = self.args['format_maps'].split(',')
            for map in selected_maps:
                val = replace_map(val, maps[map])

        return val

    __call__ = render

maps = {
    'nl_to_dbs': [('\n', r'\\')],
    'tab_to_amp': [('\t', '&')],
    'tex_quote': [
        ("\\", r"\textbackslash{}"),
        ("$", r"\$"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("|", r"\textbar{}"),
        ("<", r"\textless{}"),
        (">", r"\textgreater{}")
    ]
}

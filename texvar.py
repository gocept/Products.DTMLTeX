# -*- coding: utf-8 -*-
######################################################################
#
# DTMLTeX - A Zope Product for PS/PDF generation with TeX
# Copyright (C) 1999 Marian Kelc, 2002-2005 gocept gmbh & co. kg
#
# See also LICENSE.txt
#
######################################################################
"""A DTML tag that allows modification of the value with respect
to tex specifics.

$Id$"""

# Zope imports

from ZPublisher.TaintedString import TaintedString
from DocumentTemplate.DT_Util import parse_params, name_param, ustr

from AccessControl import ModuleSecurityInfo

module_security = ModuleSecurityInfo("Products.DTMLTeX.texvar")


def replace_map(value, map):
    """Helper method to make multiple replacements that are
       described in a dictionary
    """
    for old, new in map:
        value = value.replace(old, new)
    return value

module_security.declarePublic("transform_content")
def transform_content(val, args):
    # Sanitize input, allowing for simpler format_maps which
    # can take some things for granted:

    # Retain a newline at the end.
    newline_at_end = val.endswith('\n') or \
        val.endswith('\r')

    # Make line endings Unix-like, while trimming whitespace
    # on the right (so empty lines are really empty).
    lines = []
    for line in val.splitlines():
        lines.append(line.rstrip())
    val = '\n'.join(lines)

    if newline_at_end:
        val += '\n'

    # Now we can work with somewhat saner input.

    if args.has_key('tex_quote'):
        val = replace_map(val, maps['tex_quote'])

        # For replacing characters beyond ASCII (which
        # math_chars are) we switch to unicode. val will be
        # decoded under the assumption that it's in system
        # encoding. If the system encoding is ASCII and val
        # contains characters beyond that (i.e., in the case
        # math quoting makes sense in the first place), this
        # will break, raising an encoding error.
        # Make sure strings subject to tex_quote are always
        # unicode.
        val = unicode(val)

        for c in math_chars:
            val = val.replace(c, '\\ensuremath{%s}' % c)

    if args.has_key('format_maps'):
        selected_maps = args['format_maps'].replace(' ', '').split(',')
        for map in selected_maps:
            val = replace_map(val, maps[map])

    return val

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
        else:
            if not isinstance(val, TaintedString):
                val = ustr(val)

        return transform_content(val, args)

    __call__ = render

maps = { # Maps need to be lists of pairs as order of application may
         # be important (e.g., \ has to be quoted first of all).
    'nl_to_dbs': [('\n\n', '\n~\n'), ('\n', '\\\\\n')],
    'nl_to_newline': [('\n\n', '\n~\n'), ('\n', '\\newline\n')],
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
        (r"\textbackslash\{\}", r"\textbackslash{}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("|", r"\textbar{}"),
        ("<", r"\textless{}"),
        (">", r"\textgreater{}"),
        ('"', r"\textquotedbl{}")
        ]
}

math_chars = [u'¹', u'²', u'³']

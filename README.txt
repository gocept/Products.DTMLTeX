=========
 DTMLTeX
=========

This is DTMLTeX, a Zope Product similar to the DTML Method, but which
gets sent through pdflatex (you may replace this with the default
latex/dvips procedure) and sends you a pdf file as view.

This release is based on the Zope Product found on zope.org by
Christian Theune <ct@gocept.com>.

Prerequisites
=============

``pdflatex``

  pdflatex should be installed in /usr/bin, otherwise change DTMLTeX.py This
  means that you must have installed a TeX system. The package assumes the
  binaries in /usr/bin/ - you can change this behavior by editing the
  DTMLTeX.py file.

Usage
=====

In the content you can use all DTML-Tags you know. There is a new one,
dtml-texvar, which is similar to dtml-var except that its available
modifiers cater for the needs of the LaTeX language. There is a
modifier called tex_quote which has all LaTeX special characters
quoted, and a format_maps attribute which takes a comma-separated list
of names denoting mappings from text formatting to LaTeX formatting
commands. For instance, nl_to_dbs has all line endings changed to
double backslashes.

For the special case that you want to include a file (e.g. a jpg file)
stored in the Zope Database as a File-Object, a "create_temp" Method
is added to the File class. This creates a temporary copy of the
File's content in the system's tmp directory and inserts the temporary
name of the File at the place where it was called (e. g.  ``<dtml-texvar
"myfile.create_temp()">``).

The temporary copy is erased after a certain amount of time (keyword
parameter t, defaults to 60 seconds) by a Thread started when calling
create_temp and sleeping during this time.

Backwards compatibility
=======================

DTMLTeX 0.7 broke backwards compatibility in that dtml-var is no
longer being patched but LaTeX-related functionality is instead in
dtml-texvar. Documents which use tex_quote on dtml-var will stop
working.

Moreover it's necessary to makes strings subject to tex_quote
unicode. (You might get away without if you can guarantee that the
strings in question never contains characters beyond the system
encoding.)

Examples
========

You can find a example for this tool in example.dtml. It's a letter
typeset using the KOMA-script letter class scrlttr2 and includes an
image as well as variables of several types.

Contact
=======

For suggestions, ideas, or questions, send mail to
Thomas Lotze <tl@gocept.com>

History
=======

This Product was first developed by Marian Kelc in 1999. Due to
changes in Zope and lack of time from Marian, Christian Theune
<ct@gocept.com> took over. The current maintainer is Thomas Lotze
<tl@gocept.com>, starting March 2004.

In 2002, Andreas Kostyrka <andreas@kostyrka.priv.at> added the
following features:

- Conversion of Structured Text to LaTeX.

  + <dtml-texvar stxtxt fmt=structured-tex>
    This adds LaTeX code generated from stxtxt.

- StructuredDocument support.
  If the StructuredDocument product by maik.jablonski@uni-bielefeld.de
  is found, it is patched to support a /pdf method that creates a PDF
  version of the document.
  standard_latex_header and standard_latex_footer are stuck onto the
  LaTeX generated from the Document.

  For an example in production use see http://www.detox.at/ and
  http://www.detox.at/index_html/pdf

Bugs
====

It is not generally possible to find out for sure whether a given
DTMLTeX call is the original one made by whoever requested the LaTeX
or PDF document, or a nested dtml-texvar call, either direct or through
methods other than DTMLTeX. Therefore it may happen that DTMLTeX tries
to throw only part of a document at pdflatex, which results in a LaTeX
error.

Additionally, it is hardly possible to sensibly propagate those errors
from LaTeX calls on nested parts of documents. The clean thing would
be to use exceptions, but if we can't know whether we are in a nested
call, we can't decide whether to propagate the exception or not. (And
we don't want to raise an exception in the top-level call after all,
but rather do a nice error page.)

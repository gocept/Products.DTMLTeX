#######################################################################
#
# Copyright (c) 2003 gocept gmbh & co. kg. All rights reserved.
#
# See also LICENSE.txt
#
#######################################################################
"""Testcases for DTMLTeXFile

$Id: testDTMLTeXFile.py,v 1.2 2004/03/08 18:21:51 thomas Exp $"""

import unittest

import ZODB, OFS.Application
from ZODB.DemoStorage import DemoStorage
from ZODB.DB import DB

import StringIO
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

from Products.DTMLTeX.DTMLTeXFile import DTMLTeXFile

class DTMLTeXFileTests(unittest.TestCase):
    """Tests for the DTMLTeXFile
    """

    def __create(self, file="asdf"):
        x = DTMLTeXFile(file, _prefix='/home/ctheune/Yukon/Products/DTMLTeX/tests/')
        return x

    def testInstanciation(self):
        file = self.__create("test1.tex")
        assert isinstance(file, DTMLTeXFile)
        file.REQUEST = get_fake_request()
        assert file(client=file)


def get_fake_request():
    return HTTPRequest(StringIO.StringIO(), {'SERVER_NAME':'jucon', 'SERVER_PORT':'8080'}, HTTPResponse())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DTMLTeXFileTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

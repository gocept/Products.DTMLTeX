#######################################################################
#
# Copyright (c) 2003 gocept gmbh & co. kg. All rights reserved.
#
# See also LICENSE.txt
#
#######################################################################
"""Testcases for DTMLTeXFile

$Id$"""

import unittest

import ZODB, OFS.Application
from ZODB.DemoStorage import DemoStorage
from ZODB.DB import DB

import StringIO
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

from Products.DTMLTeX.DTMLTeX import DTMLTeX

class DTMLTeXFileTests(unittest.TestCase):
    """Tests for the DTMLTeXFile
    """

    def __create(self, file="asdf"):
        x = DTMLTeX(file, _prefix='/home/ctheune/Yukon/Products/DTMLTeX/tests/')
        return x

    def testInstanciation(self):
        file = self.__create("test1.tex")
        assert isinstance(file, DTMLTeX)
        file.REQUEST = get_fake_request()
        self.assert_(file(client=file))


def get_fake_request():
    return HTTPRequest(StringIO.StringIO(), {'SERVER_NAME':'jucon', 'SERVER_PORT':'8080'}, HTTPResponse())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DTMLTeXFileTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

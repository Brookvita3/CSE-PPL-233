import unittest
from TestUtils import TestChecker
from AST import *

class CheckerSuite(unittest.TestCase):
    def test401(self):
        input = """ 
    a: integer = 3;
"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 401))
    
    def test402(self):
        input = """
    a: integer = 3;
"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 402))
    
    def test403(self):
        input = """
    a: integer = 3;
"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 403))
    
    def test404(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 404))
    
    def test405(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 405))
    
    def test406(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 406))
    
    def test407(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 407))
    
    def test408(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 408))
    
    def test409(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 409))
    
    def test410(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 410))
    
    def test411(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 411))

    def test412(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 412))

    def test413(self):
        input = """a: integer = 3;"""
        expect = "No entry point"
        self.assertTrue(TestChecker.test(input, expect, 413))

    



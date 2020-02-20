"""Unit tests for the durable functions library"""
import os
import sys
import unittest


def suite():
    """

    :return: configuration for the suite of tests
    """
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        os.path.dirname(__file__), pattern='test_*.py')
    return test_suite


if __name__ == '__main__':
    runner = unittest.runner.TextTestRunner()
    result = runner.run(suite())
    sys.exit(not result.wasSuccessful())

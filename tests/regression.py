#! /usr/bin/env python3

import sys, os, inspect, glob
import unittest

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import doxpp


class Regression(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

def create_test(name, root, h_file, md_file, json_file):
    options = {
        'code_formatting': 'no',
        'tab_size': 4
    }
    def t(self):
        data = doxpp.buildtree.buildtree(root, h_file, md_file, '-std=c++11', '', options)
        expected = doxpp.walktree.load_data_from_json_file(json_file)

        self.maxDiff = None
        self.assertEqual(data, expected)

    t.__name__ = 'test_' + name
    return t

def generate_tests():
    for file in glob.glob(os.path.join(currentdir, 'input', '*')):
        name, ext = os.path.splitext(os.path.basename(file))
        json_file = os.path.join(currentdir, 'output', name + '.json')
        if ext == '.md':
            h_file = ''
            md_file = file
        else:
            h_file = file
            md_file = ''
        t = create_test(name, os.path.join(currentdir, 'input'), h_file, md_file, json_file)
        setattr(Regression, t.__name__, t)

os.environ['CLDOC_DEV'] = '1'

generate_tests()

if __name__ == '__main__':
    unittest.main()

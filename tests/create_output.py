#! /usr/bin/env python3

import sys, os, inspect, glob
import json

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import doxpp

doxpp.log.setLevel('info')

options = {
    'code_formatting': 'no',
    'tab_size': 4
}

for file in glob.glob(os.path.join(currentdir, 'input', '*')):
    name, ext = os.path.splitext(os.path.basename(file))
    json_file = os.path.join(currentdir, 'output', name + '.json')
    if ext == '.md':
        h_file = ''
        md_file = file
    else:
        h_file = file
        md_file = ''
    data = doxpp.buildtree.buildtree(os.path.join(currentdir, 'input'), h_file, md_file, '-std=c++11', '', options)
    with open(json_file, 'w') as output_file:
        output_file.write(json.dumps(data, indent=2))

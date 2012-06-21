"""
A minimal utility to help with some standardizations
"""
import os

DEFAULT_FILE = "default"




"""
Ensure that each directory contains a default file
"""
for dirname, dirnames, filenames in os.walk('.'):
    for subdirname in dirnames:
       p_dir = os.path.join(dirname, subdirname)
       f_path = os.path.join(p_dir, DEFAULT_FILE)
       if not os.path.exists(f_path):
           print "WARN: No *{0}* file in {1}".format(DEFAULT_FILE, p_dir[2:])



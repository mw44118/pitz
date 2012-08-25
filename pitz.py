#!/usr/bin/python

import sys
import subprocess

def _help():
    subprocess.call(['pitz-help'])
    sys.exit(1)

if len(sys.argv) < 2:
    _help()

cmd = sys.argv[1]
new_args = sys.argv[2:] or []
try:
    subprocess.call(["pitz-%s" % cmd] + new_args)
except OSError as exc:
    _help()

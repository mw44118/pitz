#!/usr/bin/python

import sys
import subprocess

cmd = sys.argv[1]
new_args = sys.argv[2:] or []
subprocess.call(["pitz-%s" % cmd] + new_args)

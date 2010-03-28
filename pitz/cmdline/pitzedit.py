# vim: set expandtab ts=4 sw=4 filetype=python:

import logging

from pitz.entity import Entity
from pitz.cmdline import PitzScript

log = logging.getLogger('pitz.cmdline.pitzedit')


class PitzEdit(PitzScript):
    """
    Edit an attribute's value
    """

    script_name = 'pitz-edit'

    def handle_p(self, p):
        p.set_usage('%prog frag attribute')

    def handle_options_and_args(self, p, options, args):
        if not args or len(args) != 2:
            p.print_usage()
            raise SystemExit

    def handle_proj(self, p, options, args, proj):

        e = proj[args[0]]

        if not isinstance(e, Entity):
            print("I couldn't find an entity %s" % args[0])
            raise SystemExit

        else:
            print(e.one_line_view)
            e.edit(args[1])
            print("Edited %s on %s." % (args[1], args[0]))

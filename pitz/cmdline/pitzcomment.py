# vim: set expandtab ts=4 sw=4 filetype=python:

import sys

import clepy

from pitz.cmdline import PitzScript


class PitzComment(PitzScript):
    """
    Store a comment on an entity
    """

    script_name = 'pitz-comment'

    def handle_p(self, p):

        p.add_option('-t', '--title', help="Comment title")

        p.add_option('--no-description',
            action='store_true',
            help='Stores this comment with an empty description')

        p.set_usage("%prog frag-to-comment-on")

    def handle_proj(self, p, options, args, proj):

        if not proj.me:
            print("Sorry, I don't know who you are.")
            print("Use pitz-me to add yourself to the project.")
            sys.exit()

        e = proj[args[0]]

        c = e.comment(

            who_said_it=proj.me,

            title=options.title or raw_input("Comment title: ").strip(),

            description='' if options.no_description \
            else clepy.edit_with_editor('# Comment description goes here'))

        print("Added comment %r on entity %r to the project." % (c, e))

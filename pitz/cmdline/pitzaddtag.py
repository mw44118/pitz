# vim: set expandtab ts=4 sw=4 filetype=python:

import logging

import clepy

from pitz.entity import Tag
from pitz.cmdline import PitzScript

log = logging.getLogger('pitz.cmdline.pitzaddtag')

class PitzAddTag(PitzScript):

    """
    Add a tag to the project
    """

    script_name = 'pitz-add-tag'

    def handle_p(self, p):

        p.add_option('-t', '--title', help='tag title')
        p.add_option('--no-description',
            action='store_true',
            help='Stores this tag with an empty description')


    def handle_proj(self, p, options, args, proj):

        t = Tag(

            proj,

            title=options.title or raw_input('Tag title: ').strip(),

            description=(
                '' if options.no_description
                else clepy.edit_with_editor('# Tag description here')),

        )

        proj.append(t)

        print("Added %r to the project." % t)

# vim: set expandtab ts=4 sw=4 filetype=python:

import jinja2

from pitz.entity import Entity

class Task(Entity):

    # This is a dictionary that maps keys in self.data to the type it
    # should hold.
    pointers = dict(
        milestone='milestone',
        creator='person',
        owner='person',
        component='component',
    )

    @property
    def detailed_view(self):
        """
        The detailed view of a task.
        """

        d = dict()
        d.update(self.data)
        d['summarized_view'] = self.summarized_view
        d['line_of_dashes'] = "-" * len(self.summarized_view)
        d['type'] = self.__class__.__name__
        d['data'] = self.data

        t = jinja2.Template("""\
{{summarized_view}}
{{line_of_dashes}}

     description: 
{{description}}

            type: {{type}}
            name: {{name}}
           title: {{title}}
    created date: {{created_time}}
   modified date: {{modified_time}}
         creator: {{getattr(creator, 'summarized_view', creator)}}
last modified by: {{last_modified_by}}
       milestone: {{milestone}}

      All fields:
{% for k in data %}
{{ k }}: {{ data[k] }}
{% endfor %}
""")
        
        return t.render(**d)

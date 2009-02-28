# vim: set expandtab ts=4 sw=4 filetype=python:

class Bag(object):
    """
    Really just a collection of entities and some functions to query
    them.
    """

    def __init__(self, entities=()):
        
        self.entities = {}
        for e in entities:
            self.entities[e['name']] = e

    def matching_pairs(self, pairs):
        """
        For pairs like

            [
                ('type', 'task'),
                ('assigned-to', 'person-matt'),
            ]

        return all entities that match.
        """

        return [e for e in self.entities.values() if e.match(pairs)]

    def append(self, e):

        if e['name'] in self.entities:
            raise ValueError("I already have %(name)s in here!" % e)

        self.entities[e['name']] = e

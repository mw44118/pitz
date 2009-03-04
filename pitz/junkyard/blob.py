# vim: set expandtab ts=4 sw=4 filetype=python:

class Blob(yaml.YAMLObject):

    @property
    def id(self):
        return id(self)

    @property
    def type(self):
        return type(self)

    def __new__(cls, *args, **kwargs):
        """
        I'm doing this so every instance can add itself to the list of
        instances.

        Remember that if I put the instances attribute on the class,
        then all subclasses would get a reference to it.
        """


        if not hasattr(cls, 'instances'):
            cls.instances = []

        self = super(Blob, cls).__new__(cls)
        cls.instances.append(self)
        self.pointers_here = defaultdict(list)

        return self

    def __init__(self, **kwargs):
        """
        Any keyword params are added as traits.
        """

        for k,v  in kwargs.items():

            setattr(self, k, v)

            if isinstance(v, Blob):

                plural_name = self.__class__.plural_name
                v.pointers_here[plural_name].append(self)

    def __repr__(self):

        attributes = ', '.join(['%s=%s' % (k, v) 
            for k, v in self.__dict__.items()
            if k not in ('pointers_here', )])

        return "%s(%s)" % (self.__class__.__name__, attributes)

class Project(Blob):
    plural_name = 'projects'

class Issue(Blob):
    plural_name = 'issues'

class Person(Blob):
    plural_name = 'people'

class Milestone(Blob):
    plural_name = 'milestones'
    
class Component(Blob):
    plural_name = 'components'

def test_blob_1():
    """
    Verify Blob subclasses keep references of instances.
    """

    issues = [Issue(), Issue()]
    people = [Person(), Person()]

    assert Issue.instances == issues
    assert Person.instances == people

def test_pointers_1():

    """
    Verify we can follow pointer traits.
    """

    matt = Person()

    Issue(owner=matt, title="Wash the car")
    Issue(owner=matt, title="Take out the trash")

    x = len(matt.pointers_here['issues'])
    assert x == 2, "Counted %d, expected 2!" % x

sample_data = [

    # tasks.
    ('task-1', 'type', 'task'),
    ('task-1', 'name', 'task-1'),
    ('task-1', 'description', 'Clean out the cat box'),
    ('task-1', 'assigned-to', 'person-matt'),

    ('task-2', 'type', 'task'),
    ('task-2', 'name', 'task-2'),
    ('task-2', 'description', 'Pay the bills'),
    ('task-2', 'assigned-to', 'person-matt'),

    ('task-3', 'type', 'task'),
    ('task-3', 'name', 'task-3'),
    ('task-3', 'description', 'Mow the yard'),
    ('task-3', 'assigned-to', 'person-matt'),

    ('task-4', 'type', 'task'),
    ('task-4', 'name', 'task-4'),
    ('task-4', 'description', 'seal-coat the driveway'),
    ('task-4', 'assigned-to', 'person-matt'),

    # milestones
    ('milestone-1', 'type', 'milestone'),
    ('milestone-1', 'name', 'milestone-1'),
    ('milestone-1', 'description', 'stuff to do this week'),

    ('milestone-2', 'type', 'milestone'),
    ('milestone-2', 'name', 'milestone-2'),
    ('milestone-2', 'description', 'stuff to do next week'),

    # people
    ('person-matt', 'type', 'person'),
    ('person-matt', 'name', 'person-matt'),
    ('person-matt', 'description', 'Matt (me)'),

    # components

    ('component-indoor chores', 'type', 'component'),
    ('component-indoor chores', 'name', 'component-indoor chores'),
    ('component-indoor chores', 'description', 'component'),

    ('component-outdoor chores', 'type', 'component'),
    ('component-outdoor chores', 'name', 'component-outdoor chores'),
    ('component-outdoor chores', 'description', 'component'),

    # comments

    ('comment-1', 'type', 'comment'),
    ('comment-1', 'name', 'I do not want to'),

    ('comment-1', 'description', 
        'I do not want to clean out the cat box.  You do it.'),

    ('comment-1', 'linked-to', 'task-1'),
    ('comment-1', 'created-date', 'Wed Feb 11 09:58:08 EST 2009'),

    ('comment-2', 'type', 'comment'),
    ('comment-2', 'name', 'But...'),
    ('comment-2', 'description', 'You said you would do it!'),
    ('comment-2', 'linked-to', 'task-1'),
    ('comment-2', 'created-date', 'Wed Feb 11 09:58:48 EST 2009'),

]

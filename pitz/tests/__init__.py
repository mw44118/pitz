# vim: set expandtab ts=4 sw=4 filetype=python:


# This is a list of entity-attribute-value tuples.

# we got tasks, milestones, people, and components.
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
]

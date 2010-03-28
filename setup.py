from setuptools import setup, find_packages

from pitz import __version__
version = __version__

setup(

    name='pitz',
    version=version,
    description="Python to-do tracker inspired by ditz (ditz.rubyforge.org)",

    long_description="""\
ditz (http://ditz.rubyforge.org) is the best distributed ticketing
system that I know of.  There's a few things I want to change, so I
started pitz.""",

    classifiers=[],
    keywords='ditz',
    author='Matt Wilson',
    author_email='matt@tplus1.com',
    url='http://pitz.tplus1.com',
    license='BSD',
    packages=find_packages(exclude=['docs', 'pitzdir', 'tests']),
    include_package_data=True,

    package_dir={'pitz': 'pitz'},

    package_data={
        'pitz': [
            'jinja2templates/*.html',
            'jinja2templates/*.txt',
        ],
    },

    zip_safe=False,

    install_requires=[
        'mock==0.4',
        'clepy>=0.3.18',
        'IPython',
        'PyYAML',
        'sphinx',
        'nose',
        'jinja2',
        'Tempita',
    ],


    entry_points="""
    [console_scripts]
    pitz-everything = pitz.cmdline:pitz_everything
    pitz-todo = pitz.cmdline:pitz_todo
    pitz-add = pitz.cmdline:pitz_add
    pitz-shell = pitz.cmdline:pitz_shell
    pitz-setup = pitz.cmdline:pitz_setup
    pitz-show = pitz.cmdline:pitz_show
    pitz-html = pitz.cmdline:pitz_html
    pitz-edit = pitz.cmdline:pitz_edit
    pitz-add-task = pitz.cmdline:pitz_add_task
    pitz-add-milestone = pitz.cmdline:pitz_add_milestone
    pitz-add-person = pitz.cmdline:pitz_add_person
    pitz-add-status = pitz.cmdline:pitz_add_status
    pitz-add-estimate = pitz.cmdline:pitz_add_estimate
    pitz-add-component = pitz.cmdline:pitz_add_component
    pitz-destroy = pitz.cmdline:pitz_destroy
    pitz-my-todo = pitz.cmdline:pitz_my_todo
    pitz-me = pitz.cmdline:pitz_me
    pitz-claim-task = pitz.cmdline:pitz_claim_task
    pitz-assign-task = pitz.cmdline:pitz_assign_task
    pitz-finish-task = pitz.cmdline:pitz_finish_task
    pitz-start-task = pitz.cmdline:pitz_start_task
    pitz-abandon-task = pitz.cmdline:pitz_abandon_task
    pitz-unassign-task = pitz.cmdline:pitz_unassign_task
    pitz-webapp = pitz.cmdline:pitz_webapp
    pitz-estimate-task = pitz.cmdline:pitz_estimate_task
    pitz-attach-file = pitz.cmdline:pitz_attach_file
    pitz-frags = pitz.cmdline:pitz_frags
    pitz-recent-activity = pitz.cmdline:pitz_recent_activity
    pitz-prioritize-above = pitz.cmdline:pitz_prioritize_above
    pitz-prioritize-below = pitz.cmdline:pitz_prioritize_below
    pitz-tasks = pitz.cmdline:pitz_tasks
    pitz-milestones = pitz.cmdline:pitz_milestones
    pitz-estimates = pitz.cmdline:pitz_estimates
    pitz-components = pitz.cmdline:pitz_components
    pitz-people = pitz.cmdline:pitz_people
    pitz-statuses = pitz.cmdline:pitz_statuses
    pitz-help = pitz.cmdline:pitz_help
    pitz-refresh-pickle = pitz.cmdline:pitz_refresh_pickle
    pitz-comment = pitz.cmdline:pitz_comment
    pitz-tags = pitz.cmdline:pitz_tags
    pitz-add-tag = pitz.cmdline:pitz_add_tag
    pitz-pause-task = pitz.cmdline:pitz_pause_task

    """,

    test_suite='nose.collector',


)

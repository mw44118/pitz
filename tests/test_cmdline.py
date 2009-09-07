# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, sys, unittest
from nose import SkipTest
from nose.tools import raises

from mock import Mock, patch, patch_object
from IPython.Shell import IPShellEmbed

from pitz.cmdline import *

@patch('__builtin__.open') # m1
@patch('yaml.load') # m2
@patch('__builtin__.__import__') # m3
@patch('__builtin__.getattr') # m4
@patch('IPython.Shell.IPShellEmbed') # m5
def test_shell_1(m1, m2, m3, m4, m5):

    raise SkipTest

    # I spent two hours trying to get this test working, but failed
    # around the point where I tried to mock out IPython. 

    m2.return_value = {
        'module':Mock(),
        'classname':'bogus'}

    P = Mock()
    P.classes.values.return_value = []

    m4.return_value = P
    m5.return_value = None

    shell('bogus')


def test_list_projects_1():
    """
    Verify we get a list of pitz modules that we can use.
    """

    raise SkipTest
    list_projects()


def test_list_projects_2():
    """
    Verify we can add our own weird modules in as ones we can use.
    """

    raise SkipTest


def test_pitz_setup():
    """
    Verify we make a pitzfiles folder, copy simplepitz.py in there, and
    write a project-abcd.yaml file that loads that simplepitz.py file.
    """

    raise SkipTest


class TestPitzEverything(unittest.TestCase):

    @raises(SystemExit)
    def test_version(self):

        # This just feels wrong.  There's gotta be a better way to set
        # up sys.argv.  Maybe I should mock it.
        sys.argv = ['pitz-everything', '--version']

        pitz_everything()


    @patch('pitz.cmdline.send_through_pager')
    def test_nofilter(self, m1):

        sys.argv = ['pitz-everything']

        pitz_everything()


    @patch('pitz.cmdline.send_through_pager')
    def test_filter(self, m1):

        sys.argv = ['pitz-everything', 'type=task']

        pitz_everything()


    @patch('pitz.cmdline.send_through_pager')
    @patch('pitz.bag.Bag.grep')
    def test_grep(self, m1, m2):

        sys.argv = ['pitz-everything', '--grep', 'foo']

        pitz_everything()


class TestPitzTodo(unittest.TestCase):

    @raises(SystemExit)
    def test_version(self):

        # This just feels wrong.  There's gotta be a better way to set
        # up sys.argv.  Maybe I should mock it.
        sys.argv = ['pitz-todo', '--version']

        pitz_todo()


    @patch('pitz.cmdline.send_through_pager')
    def test_nofilter(self, m1):

        sys.argv = ['pitz-todo']

        pitz_todo()


    @patch('pitz.cmdline.send_through_pager')
    def test_filter(self, m1):

        sys.argv = ['pitz-todo', 'type=task']

        pitz_todo()


    @patch('pitz.cmdline.send_through_pager')
    @patch('pitz.bag.Bag.grep')
    def test_grep(self, m1, m2):

        sys.argv = ['pitz-todo', '--grep', 'foo']

        pitz_todo()


class TestPitzShell(unittest.TestCase):

    @raises(SystemExit)
    def test_version(self):

        sys.argv = ['pitz-shell', '--version']
        pitz_shell()

    @patch('pitz.cmdline.IPShellEmbed')
    @patch('__builtin__.raw_input')
    def test_shell(self, m1, m2):

        sys.argv = ['pitz-shell']
        pitz_shell()


class TestPitzSetup(unittest.TestCase):

    @raises(SystemExit)
    def test_version(self):

        sys.argv = ['pitz-setup', '--version']
        pitz_setup()


class TestPitzAdd(unittest.TestCase):

    @raises(SystemExit)
    def test_version(self):

        sys.argv = ['pitz-add', '--version']
        pitz_add()


class TestPitzShow(unittest.TestCase):

    @raises(SystemExit)
    def test_version(self):

        sys.argv = ['pitz-show', '--version']
        pitz_show()


class TestPitzHtml(unittest.TestCase):

    @raises(SystemExit)
    def test_version(self):

        sys.argv = ['pitz-html', '--version']
        pitz_html()

# vim: set expandtab ts=4 sw=4 filetype=python:

import glob
import sys
import os
import unittest

from nose.tools import raises
from mock import Mock, patch

from pitz import cmdline
from pitz.cmdline.pitzsetup import mk_pitzdir
from pitz.project import Project
from pitz.entity import Entity


class TestPitzCmdLine(unittest.TestCase):

    def setUp(self):
        """
        Create a bogus pitz project for us to work on.
        """

        os.chdir('/tmp')
        os.mkdir('/tmp/pitzdir')
        proj = Project('bogus', pathname='/tmp/pitzdir')
        proj.append(Entity(title="frog"))
        proj.append(Entity(title="toad"))
        proj.save_entities_to_yaml_files()
        proj.to_yaml_file()

    def tearDown(self):

        for f in glob.glob('/tmp/pitzdir/*'):
            os.unlink(f)

        os.rmdir('/tmp/pitzdir')


class TestPitzEverything(TestPitzCmdLine):

    @raises(SystemExit)
    def test_version(self):

        # This just feels wrong.  There's gotta be a better way to set
        # up sys.argv.  Maybe I should mock it.
        sys.argv = ['pitz-everything', '--version']

        cmdline.pitz_everything()

    @patch('clepy.send_through_pager')
    def test_nofilter(self, m1):

        sys.argv = ['pitz-everything']

        cmdline.pitz_everything()

    @patch('clepy.send_through_pager')
    def test_filter(self, m1):

        sys.argv = ['pitz-everything', 'type=task']

        cmdline.pitz_everything()

    @patch('clepy.send_through_pager')
    @patch('pitz.bag.Bag.grep')
    def test_grep(self, m1, m2):

        sys.argv = ['pitz-everything', '--grep', 'foo']

        cmdline.pitz_everything()


class TestPitzTodo(TestPitzCmdLine):

    @raises(SystemExit)
    def test_version(self):

        # This just feels wrong.  There's gotta be a better way to set
        # up sys.argv.  Maybe I should mock it.
        sys.argv = ['pitz-todo', '--version']

        cmdline.pitz_todo()

    @patch('clepy.send_through_pager')
    def test_nofilter(self, m1):

        sys.argv = ['pitz-todo']

        cmdline.pitz_todo()

    @patch('clepy.send_through_pager')
    def test_filter(self, m1):

        sys.argv = ['pitz-todo', 'type=task']

        cmdline.pitz_todo()

    @patch('clepy.send_through_pager')
    @patch('pitz.bag.Bag.grep')
    def test_grep(self, m1, m2):

        sys.argv = ['pitz-todo', '--grep', 'foo']

        cmdline.pitz_todo()


class TestPitzShell(TestPitzCmdLine):

    def test_version(self):

        sys.argv = ['pitz-shell', '--version']
        cmdline.pitz_shell()

    @patch('pitz.cmdline.IPShellEmbed')
    @patch('__builtin__.raw_input')
    def test_shell(self, m1, m2):

        sys.argv = ['pitz-shell']
        cmdline.pitz_shell()


class TestPitzSetup(unittest.TestCase):

    def test_version(self):

        sys.argv = ['pitz-setup', '--version']
        cmdline.pitz_setup()


class TestPitzAdd(TestPitzCmdLine):

    @raises(SystemExit)
    def test_version(self):

        sys.argv = ['pitz-add', '--version']
        cmdline.pitz_add()

    @patch('__builtin__.raw_input')
    @patch('clepy.edit_with_editor')
    def test_created_by(self, m1, m2):

        sys.argv = ['pitz-add', '--pitzdir=/tmp/pitzdir', '--title=foo']

        m1.return_value = None
        m2.return_value = 'bogus description'

        cmdline.pitz_add()

        proj = Project.from_pitzdir('/tmp/pitzdir')

        assert proj(title='foo')


class TestPitzHtml(unittest.TestCase):

    def test_version(self):

        sys.argv = ['pitz-html', '--version']
        cmdline.pitz_html()


class TestMkPitzdir(unittest.TestCase):

    def setUp(self):
        os.chdir('/tmp')

    def tearDown(self):

        if os.path.isdir('/tmp/pitzdir/hooks'):
            for f in glob.glob('/tmp/pitzdir/hooks/*'):
                os.remove(f)
            os.rmdir('/tmp/pitzdir/hooks')

        if os.path.isdir('/tmp/pitzdir'):
            os.rmdir('/tmp/pitzdir')

    @patch('__builtin__.raw_input')
    def test_1(self, m):

        m.return_value = None

        mk_pitzdir()

        assert os.path.isdir('./pitzdir')

    def test_2(self):

        mk_pitzdir()

        assert os.path.isdir('/tmp/pitzdir')


class TestPitzScript(unittest.TestCase):

    def test_apply_filter_and_grep_1(self):
        """
        Make sure nothing blows up.
        """

        bogus_options = Mock()
        bogus_options.grep = False

        script = cmdline.PitzScript(title='bogus pitz script')
        b = script.apply_filter_and_grep(
            None, bogus_options, [], 'bogus')

        assert b == 'bogus', 'b is %s!' % b

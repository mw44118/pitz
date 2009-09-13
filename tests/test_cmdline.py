# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, sys, unittest
from nose import SkipTest
from nose.tools import raises

from mock import Mock, patch, patch_object
from IPython.Shell import IPShellEmbed

from pitz.cmdline import *
from pitz.simplepitz import SimpleProject
from pitz.entity import Entity


class TestPitzCmdLine(unittest.TestCase):

    def setUp(self):
        """
        Create a bogus pitz project for us to work on.
        """

        os.chdir('/tmp')
        os.mkdir('/tmp/pitzdir')
        proj = SimpleProject('bogus', pathname='/tmp/pitzdir')
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


class TestPitzTodo(TestPitzCmdLine):

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


class TestPitzShell(TestPitzCmdLine):

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


class TestPitzAdd(TestPitzCmdLine):

    @raises(SystemExit)
    def test_version(self):

        sys.argv = ['pitz-add', '--version']
        pitz_add()


    @patch('__builtin__.raw_input')
    @patch('pitz.cmdline.edit_with_editor')
    def test_created_by(self, m1, m2):

        sys.argv = ['pitz-add', '--pitzdir=/tmp/pitzdir', '--title=foo']

        m1.return_value = None
        m2.return_value = 'bogus description'

        pitz_add()

        proj = Project.from_pitzdir('/tmp/pitzdir')

        assert proj(title='foo')


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


class TestMkPitzdir(unittest.TestCase):

    def setUp(self):
        os.chdir('/tmp')

    def tearDown(self):

        for d in ('./pitzdir', '/tmp/pitzdir'):
            if os.path.isdir(d):
                os.rmdir(d)


    @patch('__builtin__.raw_input')
    def test_1(self, m):

        m.return_value = None

        mk_pitzdir()

        assert os.path.isdir('./pitzdir')


    @patch('__builtin__.raw_input')
    def test_2(self, m):

        m.return_value = '/tmp'

        mk_pitzdir()

        assert os.path.isdir('/tmp/pitzdir')


    @raises(ValueError)
    @patch('__builtin__.raw_input')
    def test_3(self, m):

        m.return_value = '/nonexistent'

        mk_pitzdir()

        assert os.path.isdir('/tmp/pitzdir')

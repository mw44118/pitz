# vim: set expandtab ts=4 sw=4 filetype=python:


import unittest

from pitz import edit_with_editor, by_pscore_et_al
from pitz.entity import Entity
from pitz.project import Project

from mock import Mock, patch

m, t = Mock(), Mock()

@patch('subprocess.call', m)
@patch('tempfile.NamedTemporaryFile', t)
def test_edit_with_editor_1():

    """
    Verify we can load a blank editor.
    """

    edit_with_editor()
    assert m.called
    assert t.called

@patch('subprocess.call', m)
@patch('tempfile.NamedTemporaryFile', t)
def test_edit_with_editor_2():

    """
    Verify we can load a variable into the editor.
    """

    edit_with_editor('abcdef')
    assert m.called
    assert t.called

class TestByPscoreEtAl(unittest.TestCase):

    def setUp(self):

        self.p = Project(title='test sorting...')
        Entity(self.p, title='a', pscore=2)
        Entity(self.p, title='b', pscore=1)
        Entity(self.p, title='c', pscore=3)

    def test_by_pscore_et_al(self):

        self.p.order(by_pscore_et_al)
        prevscore = 99

        for e in self.p:
            print(e)

            assert e['pscore'] < prevscore, \
            '%s, %s' % (e['pscore'], prevscore)

            prevscore = e['pscore']

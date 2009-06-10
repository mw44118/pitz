# vim: set expandtab ts=4 sw=4 filetype=python:

from pitz import edit_with_editor

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

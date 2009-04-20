# vim: set expandtab ts=4 sw=4 filetype=python:

from nose import SkipTest

from mock import Mock, patch, patch_object
from IPython.Shell import IPShellEmbed

from pitz.cmdline import shell

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

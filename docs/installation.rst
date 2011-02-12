++++++++++++
Install pitz
++++++++++++

Install the most recent release
===============================

You can get it off the python package index like this::

    $ easy_install pitz

Or build the development version from source
============================================

Grab this git repo::

    $ git clone git://github.com/mw44118/pitz.git

Then, install pitz like this::

    $ cd pitz
    $ python setup.py develop

You might need sudo in front of that second line if you're not using a
virtualenv.

Finally, there's an optional bash_completion.bash file that sets up tab
completion. To use that, add these lines to the end of your ~/.bashrc::

    # Pitz stuff to enable tab completion on fragments.
    source $HOME/checkouts/pitz/bash_completion.bash

Of course, you may need to change that line to point to where that file
lives on your box.

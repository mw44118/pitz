+++++
Hooks
+++++

Drop a file named after_add_task into pitzdir/hooks.  When you add a
task, pitz will try to run that task, passing in the location of the
pitzdir as the first command-line argument.

You might want to have your source control system ignore the hooks, so
other people don't get them when they checkout your project.



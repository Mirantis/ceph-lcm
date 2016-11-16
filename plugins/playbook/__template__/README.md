# cookiecutter template

This is playbook plugin template for
[cookiecutter](https://cookiecutter.readthedocs.io). Please refer its
documentation to check how to work with such templater.

To generate new plugin, do following:

```shell
$ cd plugins/playbook
$ cookiecutter __template__
plugin_name [my_plugin]: just_solve_problems
package [decapod_just_solve_problems]:
entry_point [just_solve_problems]:
plugin_class_name [JustSolveProblems]:
description [just_solve_problems plugin for Decapod]: My plugin seriously solves problems (and do not brings new)
plugin_display_name [My plugin seriously solves problems (and do not brings new)]: Magic button 'Make good'
is_public [True]:
required_server_list [False]: True

$ tree just_solve_problems/
├── decapod_just_solve_problems
│   ├── config.yaml
│   ├── __init__.py
│   ├── plugin.py
│   └── plugin.yaml
├── MANIFEST.in
├── setup.cfg
└── setup.py

1 directory, 7 files
```

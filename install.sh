#!/bin/sh

PYTHON_IMPLEMENTATION="$(python -c 'import platform; print(platform.python_implementation())')"

tr '\n' '\0' < uninstall_files_${PYTHON_IMPLEMENTATION}.txt | xargs -0 rm -f --
python setup.py install --force --record uninstall_files_${PYTHON_IMPLEMENTATION}.txt

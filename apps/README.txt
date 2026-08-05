pyxlsb2/apps
============

This directory contains the following python scripts:

1. install-user.py - this script installs the contents of the pyxlsb2 directory to the usersitepackages
   directory. Thus you can ensure that you can use the latest version of pyxlsb2 without going via pip.
   See the script for further details.

2. xls-formula-parser.py - this script enables you to parse a number of xls files (xlsb, xlsx, xlsm) and
   parse out the formulae in the workbooks. By default we will not be showing any values. For xlsb files
   we use pyxlsb2 (of course). For xlsx and xlsm files we use openpyxl - you are responsible for installing
   the openpyxl package - but the script will work without openpyxl except that it can only handle xlsb
   files. The install-user.py script is the recommended method of installing pyxlsb2 while you are
   developing pyxlsb2. Logging is supported by xls-parser.py - see the script for further details of
   command line options.

The .gitignore entry ignores the baseline and output directories. This is for convenience. The way
that I run xls-formula-parser.py is that I create a baseline directory which has the previous results,
and I run xls-formula-parser.py so that it outputs to the output directory. Then I can compare the two
directories to see what has changed.


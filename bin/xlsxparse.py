#-------------------------------------------------------------------------------
#
# Name:     bin/xlsxparse.py
# Purpose:  This module parses input from .xlsx Excel files and preprocesses
#           the data for query to the HGNC database.  This is a submodule of
#           the hquery program and is meant to be accessed from there.
#
# Author:   Steven Lakin (Steven.Lakin@colostate.edu or lakinsm@miamioh.edu)
#
# Created:  July 7th, 2015
# Copyright: National Institutes of Health BTRIS
#
# Documentation: https://github.com/lakinsm/hquery
#
#-------------------------------------------------------------------------------

# Note: this module requires Python 3

try:
    import openpyxl
except ImportError:
    print('Please install the requests package: pip install requests')
    raise


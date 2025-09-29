"""
Author: L. Flygare
Description: demonstrate file handling and data processing using a provided log file
"""

import re

#open and read the log file into list
in_file = open("access.log")
in_data = in_file.read()
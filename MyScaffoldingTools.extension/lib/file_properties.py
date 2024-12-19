# -*- coding: utf-8 -*-

import re
from pyrevit import revit

def get_filename():
    revit_file_path = revit.doc.PathName
    
    if len(revit_file_path) > 4:
        revit_filename = revit_file_path[:-4].split("\\")[-1]
        revit_filename = re.sub(r" \((ID [0-9]+)\)$", "", revit_filename)
    else:
        revit_filename = "ProjectUknown"
    
    return revit_filename, revit_file_path

def contains_only_alphanumerics(filename):
    return False if re.search(r"[^a-zA-Z0-9_]", filename) else True

def starts_with_capital_letter(filename):
    return False if filename[0].islower() else True

def contains_too_many_underscores(filename):
    return False if filename.count("_") > 1 else True
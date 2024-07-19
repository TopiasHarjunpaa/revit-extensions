# -*- coding: utf-8 -*-

import re
from pyrevit import revit

def check_naming_conventions():
    file_name_points = 0
    file_name_checks = 0

    revit_file_path = revit.doc.PathName
    
    if len(revit_file_path) > 4:
        revit_filename = revit_file_path[:-4].split("\\")[-1]
        revit_filename = re.sub(r" \((ID [0-9]+)\)$", "", revit_filename)
        file_name_points += 1
        print("File saved: OK")
    else:
        revit_filename = "ProjectUknown"
        print("File saved: Revit file has no name. Save the file using proper naming conventions.")
    file_name_checks += 1

    if revit_file_path.startswith("M:\Telinekataja"):
        print("File location: OK")
        file_name_points += 1
    else:
        print("File location: Revit file is not stored into M-files.") 
    file_name_checks += 1

    naming_conventions = True

    if re.search(r"[^a-zA-Z0-9_]", revit_filename):
        print("Naming conventions: Filename contains characters other than alphanumerics.")
        naming_conventions = False
    else:
        file_name_points += 1
    file_name_checks += 1

    if revit_filename[0].islower():
        print("Naming conventions: Filename does not start with a capital letter.")
        naming_conventions = False
    else:
        file_name_points += 1
    file_name_checks += 1

    if revit_filename.count("_") > 1:
        print("Naming conventions: Filename does have too many underscores. Use maximum of one underscore before phase name.")
        naming_conventions = False
    else:
        file_name_points += 1
    file_name_checks += 1
    
    if naming_conventions:
        print("Naming conventions: OK")

    return file_name_points, file_name_checks


def check_file_properties():
    file_name_points, file_name_checks = check_naming_conventions()

    return file_name_points, file_name_checks
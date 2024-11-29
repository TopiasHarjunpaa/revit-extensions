# -*- coding: utf-8 -*-

import re
from pyrevit import revit
from file_properties import get_filename, contains_only_alphanumerics, starts_with_capital_letter, contains_too_many_underscores
from score_counter import ScoreCounter

counter = ScoreCounter()

def check_naming_conventions(outputter):
    revit_filename, revit_file_path = get_filename()

    if revit_filename == "ProjectUnknown":
        outputter.print_response("File is saved", "Revit file has no name. Save the file using proper naming conventions.", "red")
    else:
        outputter.print_response("File is saved", "OK")
        counter.increment_points()
    
    if revit_file_path.startswith("M:\Telinekataja"):
        outputter.print_response("File location", "OK")
        counter.increment_points()
    else:
        outputter.print_response("File location", "Revit file is not stored into M-files.", "red") 

    naming_conventions = True

    if contains_only_alphanumerics(revit_filename):
        counter.increment_points()
    else:
        naming_conventions = False
        outputter.print_response("Naming conventions", "Filename contains characters other than alphanumerics.", "red") 

    if starts_with_capital_letter(revit_filename):
        counter.increment_points()
    else:
        outputter.print_response("Naming conventions", "Filename does not start with a capital letter.", "red") 

    if contains_too_many_underscores(revit_filename):
        counter.increment_points()
    else:
        outputter.print_response("Naming conventions", "Filename does have too many underscores. Use maximum of one underscore before phase name.", "red") 

    if naming_conventions:
        outputter.print_response("Naming conventions", "OK")
    counter.increment_checks(5)


def check_file_properties(outputter):
    check_naming_conventions(outputter)

    points, checks, percentage = counter.get_score_percentage()
    outputter.print_md("### <u>File properties check summary: Points gained {0} out of {1}. Score: {2}</u>".format(points, checks, percentage))
# -*- coding: utf-8 -*-

import file_properties as fp
from score_counter import ScoreCounter

counter = ScoreCounter()

def check_naming_conventions(outputter):
    revit_filename, revit_file_path = fp.get_filename()

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

    if fp.contains_only_alphanumerics(revit_filename):
        counter.increment_points()
    else:
        naming_conventions = False
        outputter.print_response(
            "Naming conventions",
            "Filename <b><i>{0}</i></b> contains characters other than alphanumerics.".format(revit_filename),
            "red"
        ) 

    if fp.starts_with_capital_letter(revit_filename):
        counter.increment_points()
    else:
        naming_conventions = False
        outputter.print_response(
            "Naming conventions",
            "Filename <b><i>{0}</i></b> does not start with a capital letter.".format(revit_filename),
            "red"
        )

    if fp.contains_too_many_underscores(revit_filename):
        counter.increment_points()
    else:
        naming_conventions = False
        outputter.print_response(
            "Naming conventions",
            "Filename <b><i>{0}</i></b> does have too many underscores. Use maximum of one underscore before phase name.".format(revit_filename),
            "red"
        )
    if naming_conventions:
        outputter.print_response("Naming conventions", "OK")
    counter.increment_checks(5)


def check_file_properties(outputter):
    check_naming_conventions(outputter)

    return counter
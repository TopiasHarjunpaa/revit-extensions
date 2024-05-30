import re

from pyrevit import revit, DB, forms

def format_output_filename():   
    revit_file_path = revit.doc.PathName
    revit_filename = revit_file_path[:-4].split("\\")[-1]
    revit_filename = re.sub(r" \((ID [0-9]+)\)$", "", revit_filename)

    underscore_count = revit_filename.count("_")
    
    if re.search(r"[^a-zA-Z0-9_]", revit_filename):
        print("File naming convention is not followed!")
        print("Filename contains characters other than alphanumerics")
        print("---")


    if revit_filename[0].islower():
        print("File naming convention is not followed!")
        print("Filename does not start with a capital letter.")
        print("---")

    if underscore_count > 1:
        print("File naming convention is not followed!")
        print("Filename does have too many underscores. Use maximum of one underscore before phase name")
        print("---")       

    return revit_filename + ".pdf"

def plot_sheets_to_pdf(file_path):
    print("To be added later...")
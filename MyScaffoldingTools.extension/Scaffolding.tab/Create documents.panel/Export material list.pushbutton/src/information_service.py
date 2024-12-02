# -*- coding: utf-8 -*-

from datetime import date
from pyrevit import revit, DB
from translations import TRANSLATIONS
from parameters import get_language, get_project_information_params, INFO_PARAMS, HEADER_PARAMS
import file_properties as fp


def get_project_language():
    """Retrieves only language name from the project. Ignores language index
    which is second item of the tuple recieved from get_language -method.

    Returns:
        str: Language name as string (FIN, ENG or SWE)
    """
    language_name = get_language()[0]

    return language_name

def format_output_filename(outputter, language="ENG"):
    """Formats material list filename based on Revit model file name. Additionally, makes few simple checks if the
    predefined Revit file naming conventions are followed and notifies user if conventions are not followed.

    1. Obtain original Revit filename
    2. Remove .rvt suffix from the Revit filename
    3. Remove M-files ID suffix if exists (occurs when file is opened through M-files)
    4. Check following naming conventions:
        - Filename can not contain other than characters and alphanumerics
        - Filename should start with capital letter
        - Filename can contain zero or one underscore (if there are multiple files for different phases)
    5. Adds translated "Material list" text with underscore after the filename. Puts it before "_PhaseX" if phasing exists.
    6. Adds "xlsx" suffix

    Args:
        language (str, optional): Language selection. Defaults to "ENG".

    Returns:
        str: Formatted output filaname for material list
    """
    revit_filename = fp.get_filename()[0]

    if revit_filename == "ProjectUnknown":
        outputter.print_response("Revit file has no name", "In order to ensure correct naming convention, save the Revit file before proceeding material list export.", "red")
    
    if not fp.contains_only_alphanumerics(revit_filename):
        outputter.print_response("File naming conventions not followed", "Filename contains characters other than alphanumerics.", "red") 

    if not fp.starts_with_capital_letter(revit_filename):
        outputter.print_response("File naming conventions not followed", "Filename does not start with a capital letter.", "red") 

    if not fp.contains_too_many_underscores(revit_filename):
        outputter.print_response("File naming conventions not followed", "Filename does have too many underscores. Use maximum of one underscore before phase name.", "red")   

    material_list_text = TRANSLATIONS["Material list"].get(language, "ENG")

    if revit_filename.count("_") == 1:
        splitted_name = revit_filename.split("_")
        material_list_filename = splitted_name[0] + "_" + material_list_text + "_" + splitted_name[1] + ".xlsx"
        return material_list_filename

    return revit_filename + "_" + material_list_text + ".xlsx"

def get_project_parameters(outputter, language="ENG", total_weight="NA", total_price="NA"):
    """Finds project information parameters from the Revit project. Checks whether
    necessary parameters exists and adds date and totals parameters to the same dictionary. 
    Changes parameter names (key values) with translated parameter names based on the selected language.

    Args:
        language (str, optional): Language selection. Defaults to "ENG".
        total_weight (str, optional): Total weight of the material. Defaults to "NA".
        total_price (str, optional): Total price of the material. Defaults to "NA".

    Returns:
        Dict: Dictionary with translated keys and project parameter values.
    """

    translated_project_parameters = {}
    project_params = get_project_information_params()

    for header_name in INFO_PARAMS:
        if header_name not in project_params:
            project_params[header_name] = "NA"
            outputter.print_response(header_name, "Not found!", "red")

    for key in project_params.keys():
        translated_key = TRANSLATIONS[key].get(language, key)
        translated_project_parameters[key] = (translated_key, project_params.get(key, "NA"))

    date_key = TRANSLATIONS["Date"].get(language, "Date")
    translated_project_parameters["Date"] = (date_key, date.today().strftime('%Y-%m-%d'))

    totals = {
        "Total weight": "{:.2f} kg".format(total_weight).replace(".", ","),
        "Total price": "{:.2f} €".format(total_price).replace(".", ",")
    }

    for key, value in totals.items():
        translated_key = TRANSLATIONS[key].get(language, "NA")
        translated_project_parameters[key] = (translated_key, value)

    return translated_project_parameters

def get_additional_notes(language="ENG", notes={}):
    if len(notes) == 0:
        return None
    
    additional_notes = []
    note_number = 1
    additional_notes.append(TRANSLATIONS["Notes"].get(language, ""))
    

    if "Suspended" in notes:
        translated_note = "{0}) {1}!".format(note_number, TRANSLATIONS["Suspended"].get(language, notes["Suspended"]))
        additional_notes.append(translated_note)
        note_number += 1

    if "Anchoring" in notes and len(notes["Anchoring"]) > 0:
        translated_note = "{0}) {1}:".format(note_number, TRANSLATIONS["Anchoring"].get(language, ""))
        additional_notes.append(translated_note)

        for item in notes["Anchoring"]:
            additional_notes.append(item)

    return additional_notes

def get_headers(language="ENG"):
    headers = []
    main_language_key = "Product name {}".format(language)
    
    ordered_header_params = HEADER_PARAMS
    ordered_header_params.remove(main_language_key)
    ordered_header_params.insert(1, main_language_key)

    for key in ordered_header_params:
        translated_key = TRANSLATIONS[key].get(language, key)
        headers.append(translated_key)
    
    return headers

def get_schedule_information(schedule_name):
    schedule_data = []
    schedules = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewSchedule).ToElements()
    for schedule in schedules:
        if schedule.Name == schedule_name:
            table_data = schedule.GetTableData()
            section_data = table_data.GetSectionData(DB.SectionType.Body)
            num_of_rows = section_data.NumberOfRows
            num_of_cols = section_data.NumberOfColumns   
            for i in range(num_of_rows):
                row = []
                for j in range(num_of_cols):
                    cell_value = schedule.GetCellText(DB.SectionType.Body, i, j)
                    row.append(cell_value)
                schedule_data.append(row)
        else:
            print("ERROR:")
            print("Can not find schedule named as Material list! Rename the schedule as [Material list] you want to export")
            print("---")

    return schedule_data
# -*- coding: utf-8 -*-

from datetime import date
import re
from translations import REVIT_PARAMS, HEADER_PARAMS, TRANSLATIONS
from pyrevit import revit, DB

def get_project_language():
    global_params = DB.FilteredElementCollector(revit.doc).OfClass(DB.GlobalParameter)

    for param in global_params:
        if param.Name == "Project language":
            param_value = param.GetValue().Value
            if param_value == 1:
                return "FIN"
            if param_value == 2:
                return "ENG"
            if param_value == 3:
                return "SWE"

    print("Project language parameter is not found. English language as a default will be used.")
    print("In order to define project language. Make sure your global language parameter is set to integer between 1 to 3")
    print("---")

    return "ENG"

def format_output_filename(language="ENG"):
    revit_file_path = revit.doc.PathName
    revit_filename = revit_file_path[:-4].split("\\")[-1]
    material_list_text = "MaterialList" if language == "ENG" else TRANSLATIONS["Material list"].get(language, "")
    underscore_count = revit_filename.count("_")
    
    if re.search(r'[^a-zA-Z0-9_]', revit_filename):
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

    if underscore_count == 1:
        splitted_name = revit_filename.split("_")
        material_list_filename = splitted_name[0] + "_" + material_list_text + "_" + splitted_name[1] + ".xlsx"
        return material_list_filename

    return revit_filename + "_" + material_list_text + ".xlsx"

def get_project_parameters(language="ENG", total_weight="NA", total_price="NA"):
    translated_project_parameters = {}

    project_parameters = DB.FilteredElementCollector(revit.doc)\
                        .OfCategory(DB.BuiltInCategory.OST_ProjectInformation)\
                        .ToElements()[0].Parameters

    params_dict = {param.Definition.Name: param.AsString() for param in project_parameters}

    # Add translated parameters from Revit
    for key in REVIT_PARAMS:
        translated_key = TRANSLATIONS[key].get(language, key)
        translated_project_parameters[key] = (translated_key, params_dict.get(key, "NA"))

    # Add date
    date_key = TRANSLATIONS["Date"].get(language, "Date")
    translated_project_parameters["Date"] = (date_key, date.today().strftime('%Y-%m-%d'))

    # Add translated totals
    totals = {
        "Total weight": "{:,.2f} kg".format(total_weight),
        "Total price": "{:,.2f} €".format(total_price)
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
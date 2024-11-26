# -*- coding: utf-8 -*-

from pyrevit import revit, DB


def get_global_params():
    """Finds all global parameters from the Revit project and stores them into dictionary.
    
    Returns:
        Dict: Dictionary with global parameters.
    """

    global_params_dict = {}
    global_params = DB.FilteredElementCollector(revit.doc).OfClass(DB.GlobalParameter)

    for global_param in global_params:
        global_param_name = global_param.Name
        global_param_value = global_param.GetValue().Value
        global_params_dict[global_param_name] = global_param_value
    
    return global_params_dict

def get_language():
    language_number = get_global_params().get("Project language", "None")

    if language_number == 1:
        return "FIN", 0
    if language_number == 2:
        return "ENG", 1
    if language_number == 3:
        return "SWE", 2

    print("Project language parameter is not found. English language as a default will be used.")
    print("In order to define project language. Make sure your global language parameter is set to integer between 1 to 3")
    print("---")

    return "ENG", 1

def get_project_information_params():
    information_params_dict = {}
    param_names = ["Author", "Client Name", "Project Address", "Project Name", "Supervisor name", "Inspector name", "Drawing type"]

    project_params = revit.doc.ProjectInformation.Parameters

    for project_param in project_params:
        project_param_name = project_param.Definition.Name
        if project_param_name in param_names and project_param.StorageType == DB.StorageType.String:
            project_param_value = project_param.AsString()
            information_params_dict[project_param_name] = project_param_value

    return information_params_dict

def get_project_load_params():
    load_params_dict = {}

    project_params = revit.doc.ProjectInformation.Parameters

    for project_param in project_params:
        if project_param.IsShared and project_param.StorageType == DB.StorageType.String:
            load_param_name = project_param.Definition.Name
            load_param_value = project_param.AsString()
            load_params_dict[load_param_name] = load_param_value
    

    return load_params_dict
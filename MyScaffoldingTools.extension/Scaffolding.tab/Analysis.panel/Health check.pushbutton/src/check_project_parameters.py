# -*- coding: utf-8 -*-

from pyrevit import revit, DB

def get_global_parameters():
    """Finds all global parameters from the Revit project and stores them into dictionary.
        Checks whether all the necessary parameters exists and they are in correct range.

        Project language: Integer values 1, 2 or 3
        Company: Integer values 1, 2 or 3
        Show inspector name: Integer values 1 or 0 (Yes/No)
    
    Returns:
        Tuple(Dict, Int): Dictionary with global parameters and points from the parameter check.
    """

    global_params_dict = {}
    points = 0
    checks = 0
    global_params = DB.FilteredElementCollector(revit.doc).OfClass(DB.GlobalParameter)

    for global_param in global_params:
        global_param_name = global_param.Name
        global_param_value = global_param.GetValue().Value
        global_params_dict[global_param_name] = global_param_value
    
    if "Project language" in global_params_dict:
        if global_params_dict["Project language"] >= 1 and global_params_dict["Project language"] <= 3:
            print("Project language: OK")
            points += 1
        else:
            print("Project parameter: Invalid value! Must be between 1-3.")
    else:
        print("Project parameter: Not found!")
    checks += 1
    
    if "Company" in global_params_dict:
        if global_params_dict["Company"] >= 1 and global_params_dict["Company"] <= 3:
            print("Company: OK")
            points += 1
        else:
            print("Company: Invalid value! Must be between 1-3.")
    else:
        print("Company: Not found!")
    checks += 1

    if "Show inspector name" in global_params_dict:
        if global_params_dict["Show inspector name"] == 0 or global_params_dict["Show inspector name"] == 1:
            print("Show inspector name: OK")
            points += 1
        else:
            print("Show inspector name: Not found!")
    checks += 1
    
    return global_params_dict, points, checks

def get_project_information_params():
    information_params_dict = {}
    load_params_dict = {}
    param_names = ["Author", "Client Name", "Project Address", "Project Name", "Supervisor name", "Inspector name", "Drawing type"]
    information_points = 0
    information_checks = 0
    load_points = 0
    load_checks = 0

    project_params = revit.doc.ProjectInformation.Parameters

    for project_param in project_params:
        project_param_name = project_param.Definition.Name
        if project_param_name in param_names and project_param.StorageType == DB.StorageType.String:
            project_param_value = project_param.AsString()
            information_params_dict[project_param_name] = project_param_value
        else:
            if project_param.IsShared and project_param.StorageType == DB.StorageType.String:
                load_param_name = project_param.Definition.Name
                load_param_value = project_param.AsString()
                load_params_dict[load_param_name] = load_param_value
    
    for name in param_names:
        if name not in information_params_dict:
            print("{} parameter is missing from the project".format(name))
        else:
            information_points += 1
        information_checks += 1
    
    for key, value in information_params_dict.items():
        # TODO: Add check if Show inspector name is 0, then missing value for Inspector name is okey...

        if value is None or value == "":
            print("{}: Value is missing.".format(key))
        
        elif str(value).lower() == key.lower():
            print("{0}: Default value [{1}] is used. Change this to the correct one.".format(key, value))
        
        elif value == "Designer name":
            print("{0}: Default value [{1}] is used. Change this to the correct one.".format(key, value))
        
        else:
            print("{}: OK".format(key))
            information_points += 1
        information_checks += 1
    
    if len(load_params_dict) == 36:
        print("Number of Load parameters: OK")
        load_points += 1
    else:
        print("Load parameters: {}/36. Load parameters are missing from the project".format(len(load_params_dict)))
    load_checks += 1

    load_points += 1
    for value in load_params_dict.values():
        if value is None or value == "" or value == "NA":
            print("Load parameter values: Empty values are found. Calculate loads unless this is draft project.")
            load_points -= 1
            break
    load_checks += 1

    return information_params_dict, load_params_dict, information_points, information_checks, load_points, load_checks

def check_project_params():
    global_params, global_points, global_checks = get_global_parameters()
    info_params, load_params, info_points, info_checks, load_points, load_checks = get_project_information_params()
    project_param_points = global_points + info_points + load_points
    project_param_checks = global_checks + info_checks + load_checks

    return project_param_points, project_param_checks
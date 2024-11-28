# -*- coding: utf-8 -*-

from parameters import get_global_params, get_project_information_params, get_project_load_params

def check_global_parameters(output):
    """Finds all global parameters from the Revit project and stores them into dictionary.
        Checks whether all the necessary parameters exists and they are in correct range.

        Project language: Integer values 1, 2 or 3
        Company: Integer values 1, 2 or 3
        Show inspector name: Integer values 1 or 0 (Yes/No)
    
    Returns:
        Tuple(Dict, Int): Dictionary with global parameters and points from the parameter check.
    """

    global_params_dict = get_global_params()
    points = 0
    checks = 0
    
    if "Project language" in global_params_dict:
        if global_params_dict["Project language"] >= 1 and global_params_dict["Project language"] <= 3:
            response = "OK"
            points += 1
        else:
            response = "Invalid value! Must be between 1-3."
    else:
        response = "Not found!"
    
    output.print_md("**Project language parameter**: {0}".format(response))
    checks += 1

    #To be continued...
    
    if "Company" in global_params_dict:
        if global_params_dict["Company"] >= 1 and global_params_dict["Company"] <= 3:
            output.print_md("Company: OK")
            points += 1
        else:
            output.print_md("Company: Invalid value! Must be between 1-3.")
    else:
        output.print_md("Company: Not found!")
    checks += 1

    if "Show inspector name" in global_params_dict:
        # This check should not be needed, since Revit UI has tickbox selection here.
        if global_params_dict["Show inspector name"] == 0 or global_params_dict["Show inspector name"] == 1:
            output.print_md("Show inspector name: OK")
            points += 1
        else:
            output.print_md("Show inspector name: Invalid value! Must be Yes or No.")
    else:
        output.print_md("Show inspector name: Not found!")
    checks += 1
    
    return global_params_dict, points, checks

def check_project_params(output):
    information_params_dict = get_project_information_params()
    load_params_dict = get_project_load_params()
    param_names = ["Author", "Client Name", "Project Address", "Project Name", "Supervisor name", "Inspector name", "Drawing type"]
    information_points = 0
    information_checks = 0
    load_points = 0
    load_checks = 0
    
    for name in param_names:
        if name not in information_params_dict:
            output.print_md("{}: Not found!".format(name))
        else:
            information_points += 1
        information_checks += 1
    
    for key, value in information_params_dict.items():
        # TODO: Add check if Show inspector name is 0, then missing value for Inspector name is okey...

        if value is None or value == "":
            output.print_md("{}: Value is missing.".format(key))
        
        elif str(value).lower() == key.lower():
            output.print_md("{0}: Default value [{1}] is used. Change this to the correct one.".format(key, value))
        
        elif value == "Designer name":
            output.print_md("{0}: Default value [{1}] is used. Change this to the correct one.".format(key, value))
        
        else:
            output.print_md("{}: OK".format(key))
            information_points += 1
        information_checks += 1
    
    if len(load_params_dict) == 36:
        output.print_md("Number of Load parameters: OK")
        load_points += 1
    else:
        output.print_md("Load parameters: {}/36. Load parameters are missing from the project".format(len(load_params_dict)))
    load_checks += 1

    load_points += 1
    for value in load_params_dict.values():
        if value is None or value == "" or value == "NA":
            output.print_md("Load parameter values: Empty values are found. Calculate loads unless this is draft project.")
            load_points -= 1
            break
    load_checks += 1

    return information_params_dict, load_params_dict, information_points, information_checks, load_points, load_checks

def check_params(output):
    global_params, global_points, global_checks = check_global_parameters(output)
    info_params, load_params, info_points, info_checks, load_points, load_checks = check_project_params(output)
    project_param_points = global_points + info_points + load_points
    project_param_checks = global_checks + info_checks + load_checks

    return project_param_points, project_param_checks
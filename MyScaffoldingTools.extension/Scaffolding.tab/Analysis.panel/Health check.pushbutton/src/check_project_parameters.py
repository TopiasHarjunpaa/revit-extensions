# -*- coding: utf-8 -*-

from parameters import get_global_params, get_project_information_params, get_project_load_params
from score_counter import ScoreCounter

counter = ScoreCounter()

def evaluate_global_param(params_dict, param_name, min_value, max_value):
    if param_name in params_dict:
        if min_value <= params_dict[param_name] <= max_value:
            counter.increment_points()
            return "OK", "black"
        else:
            return "Invalid value! Must be between 1-3.", "red"
    
    return "Not found!", "orange"

def check_global_parameters(outputter):
    """Finds all global parameters from the Revit project and stores them into dictionary.
        Checks whether all the necessary parameters exists and they are in correct range.

        Project language: Integer values 1, 2 or 3
        Company: Integer values 1, 2 or 3
        Show inspector name: Integer values 1 or 0 (Yes/No)
    """

    outputter.print_md("### 1. Global parameter check:")
    global_params_dict = get_global_params()
    params_to_be_checked = [
        ("Project language", 1, 3),
        ("Company", 1, 3),
        ("Show inspector name", 0, 1),
    ]
    
    for param_name, min, max in params_to_be_checked:
        response, color = evaluate_global_param(global_params_dict, param_name, min, max)
        outputter.print_response(param_name, response, color)
        counter.increment_checks()

def check_all_info_params_exists(params_dict, params_to_be_checked, outputter):
    all_exists = True
    for name in params_to_be_checked:
        if name not in params_dict:
            outputter.print_response(name, "Not found!", "red")
            all_exists = False
        else:
            counter.increment_points()
        counter.increment_checks()
    if all_exists:
        outputter.print_response("Information parameters", "OK, all parameters exists in the project")

def check_info_param_values(params_dict, outputter):
    for key, value in params_dict.items():

        if value is None or value == "":
            if key == "Inspector name":
                outputter.print_response(key, "Value is missing. This is okey, if the project does not require inspector.", "red")
            else:
                outputter.print_response(key, "Value is missing.", "red")
        
        elif str(value).lower() == key.lower():
            outputter.print_response(key, "Default value <b><i>{0}</i></b> is used. Change this to correct one.".format(value), "red")
        
        elif value == "Designer name":
            outputter.print_response(key, "Default value <b><i>{0}</i></b> is used. Change this to correct one.".format(value), "red")
        
        else:
            outputter.print_response(key, "OK")
            counter.increment_points()
        counter.increment_checks()

def check_load_params(params_dict, number_of_load_params, outputter):
    if len(params_dict) >= number_of_load_params:
        outputter.print_response("Number of Load parameters", "OK")
        counter.increment_points()
    else:
        outputter.print_response("Number of Load parameters", "{}/39. Load parameters are missing from the project".format(len(params_dict)), "red")
    counter.increment_checks()

    empty_values = False
    for value in params_dict.values():
        if value is None or value == "" or value == "NA":
            empty_values = True
            outputter.print_response("Load parameter values", "Empty values are found. Calculate loads unless this is draft project.", "red")
            break
    
    if not empty_values:
        outputter.print_response("Load parameter values", "OK, no empty values are found.")
        counter.increment_points()
    counter.increment_checks()


def check_project_params(outputter, number_of_load_params=39):
    params_to_be_checked = [
        "Author",
        "Client Name",
        "Project Address",
        "Project Name",
        "Supervisor name",
        "Inspector name",
        "Drawing type"
    ]

    information_params_dict = get_project_information_params(params_to_be_checked)
    load_params_dict = get_project_load_params()
    
    outputter.print_md("### 2. Project information parameter check:")
    check_all_info_params_exists(information_params_dict, params_to_be_checked, outputter)
    check_info_param_values(information_params_dict, outputter)
    
    outputter.print_md("### 3. Load parameter check:")
    check_load_params(load_params_dict, number_of_load_params, outputter)

def check_params(outputter):
    check_global_parameters(outputter)
    check_project_params(outputter)

    return counter
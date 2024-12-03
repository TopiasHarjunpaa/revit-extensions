# -*- coding: utf-8 -*-

import re
from pyrevit import revit, DB
from views import get_project_views_and_viewports
from score_counter import ScoreCounter

counter = ScoreCounter()

def check_callout_name(section_name, outputter):
    if re.match(r"^DET([1-9]|[1-9][0-9])$", section_name):
        counter.increment_points()
        outputter.print_response("Callout name", "<b><i>{0}</i></b> is correctly named.".format(section_name))
    else:
        outputter.print_response("Callout name", "<b><i>{0}</i></b> is incorrectly named. Callout section should be named as DET[number] whereas number is value between 1 - 99.".format(section_name), "red")
    counter.increment_checks() 


def check_section_name(section_name, outputter):
    if re.match(r"^[A-Z1-9]$", section_name):
        counter.increment_points()
        outputter.print_response("Section name", "<b><i>{0}</i></b> is correctly named.".format(section_name))
    else:
        outputter.print_response("Section name", "<b><i>{0}</i></b> is incorrectly named. Use only single character and capitalized alphanumberic, such as A, B, 1 or 2.".format(section_name), "red")
    counter.increment_checks() 


def check_section_names_and_get_sections_in_viewports(sections, outputter):
    if len(sections) > 0:
        counter.increment_points()
    else:
        outputter.print_response("Section name", "No section views found on this project. At least one section should be used!", "red")
    counter.increment_checks()

    for section in sections:
        if section["view"].IsCallout:
            check_callout_name(section["view"].Name, outputter)             
        else:
            check_section_name(section["view"].Name, outputter)


def contains_annotation(view, annotation_name):
    annotations = DB.FilteredElementCollector(revit.doc, view.Id)\
                    .OfCategory(DB.BuiltInCategory.OST_GenericModelTags)\
                    .WhereElementIsNotElementType().ToElements()

    for annotation in annotations:
        if annotation.Name.startswith(annotation_name):
            return True
    
    return False


def contains_family_with_parameter_name(view, parameter_name):
    collector = DB.FilteredElementCollector(revit.doc, view.Id)\
                    .OfCategory(DB.BuiltInCategory.OST_GenericModel)\
                    .WhereElementIsNotElementType()

    for element in collector:
        if element.LookupParameter(parameter_name):
            return True

    return False


def check_annotations_in_section(view, parameter_name, component_name, annotation_name, outputter):
    contains_family = contains_family_with_parameter_name(view, parameter_name)
    contains_tag = contains_annotation(view, annotation_name)

    if contains_family and not contains_tag:
        outputter.print_response("Anchor tags in section <b><i>{0}</i></b>".format(view.Name), "Section has {0}, but no {1} -tags".format(component_name, annotation_name), "red")
    elif not contains_family:
        outputter.print_response("Anchor tags in section <b><i>{0}</i></b>".format(view.Name), "OK. Section does not have any {0}.".format(component_name))
        counter.increment_points()
    else:
        outputter.print_response("Anchor tags in section <b><i>{0}</i></b>".format(view.Name), "OK")
        counter.increment_points()
    counter.increment_checks()


def check_annotations_used_in_sections(sections, outputter):
    for section in sections:
        if section["in_viewport"]:
            check_annotations_in_section(section["view"], "Max X+", "anchoring components", "Anchor", outputter)
            check_annotations_in_section(section["view"], "Max Z+", "base plates", "Leg", outputter)
            check_annotations_in_section(section["view"], "Fill type", "roof system", "Lifting point", outputter)

def check_correct_view_port_type(views, correct_type, view_type_name, outputter):
        if len(views) == 0:
            outputter.print_response(
                "{0} viewport types".format(view_type_name),
                "No {0} viewports are found on the project. At least one should be used.".format(view_type_name),
                "red"
            )
        
        correct_types = True
        for view in views:
            if view["viewport_type"] != correct_type:
                correct_types = False
                outputter.print_response(
                    "{0} viewport types".format(view_type_name),
                    "Incorrect type for {0}. Type should be {1}".format(view["view"].Name, correct_type),
                    "red"
                ) 
        
        if correct_types:
            outputter.print_response("{} viewport types".format(view_type_name), "OK.")
            counter.increment_points()


def check_viewports_have_correct_types(views, outputter):
    floor_plan_views = [view for view in views.get("FloorPlan", []) if view["in_viewport"]]
    section_views = [view for view in views.get("Section", []) if view["in_viewport"] and not view["view"].IsCallout]
    section_callout_views = [view for view in views.get("Section", []) if view["in_viewport"] and view["view"].IsCallout]

    check_correct_view_port_type(floor_plan_views, "Title basic", "Layout", outputter)
    counter.increment_checks()

    check_correct_view_port_type(section_views, "Title section", "Section", outputter)
    counter.increment_checks()

    if len(section_callout_views) > 0:
        check_correct_view_port_type(section_callout_views, "Title basic", "Section callout", outputter)
        counter.increment_checks()
    else:
        outputter.print_response("Section callout viewport types", "OK. No viewports are found on the project.")


def check_material_list_headers(schedule, headers, num_of_cols, outputter):
    correct_headers = True
    counter.increment_checks()

    if len(headers) != num_of_cols:
        outputter.print_response(
            "Material list headers",
            "Incorrect number of columns. Expected {0}, found {1}.".format(len(headers), num_of_cols),
            "red"
        )
        correct_headers = False
    else:
        for col_index in range(num_of_cols):
            col_name = schedule.GetCellText(DB.SectionType.Body, 0, col_index)
            if headers[col_index] != col_name:
                correct_headers = False
                outputter.print_response(
                    "Material list headers",
                    "Incorrect headers. Column {0} is named as {1}. Should be {2}".format(col_index + 1, col_name, headers[col_index]),
                    "red"
                )
    
    if correct_headers:
        outputter.print_response("Material list headers", "OK.")
        counter.increment_points()

def check_material_list_column_cells(schedule, headers, num_of_rows, outputter):
    has_non_unique = False
    has_empty = False  
    counter.increment_checks(2)

    for col_index in range(1, 6):
        for row_index in range(1, num_of_rows):
            cell_value = schedule.GetCellText(DB.SectionType.Body, row_index, col_index)
            
            if cell_value == "<varies>":
                has_non_unique = True
            elif cell_value == "":
                has_empty = True

        if has_non_unique:
            outputter.print_response(
                "Material list contains only unique values",
                "Non-unique values found in the column: {0}.".format(headers[col_index]),
                "red"
            )
        if has_empty:
            outputter.print_response(
                "Material list does not contain empty values",
                "Empty values found in the column: {0}.".format(headers[col_index]),
                "red"
            )
    
    if not has_non_unique:
        counter.increment_points()
        outputter.print_response("Material list contains only unique values", "OK.")
    
    if not has_empty:
        counter.increment_points()
        outputter.print_response("Material list does not contain empty values", "OK.")


def check_material_list_content(schedule, outputter):
    headers = ["Count", "Product number", "Product name (FIN)", "Product name (ENG)", "Product name (SWE)", "Weight", "Length info", "Width info"]
    
    table_data = schedule.GetTableData()
    section_data = table_data.GetSectionData(DB.SectionType.Body)
    num_of_rows = section_data.NumberOfRows
    num_of_cols = section_data.NumberOfColumns

    check_material_list_headers(schedule, headers, num_of_cols, outputter)
    check_material_list_column_cells(schedule, headers, num_of_rows, outputter)


def check_schedule_names_and_get_material_schedule(schedules, outputter):
    material_list = None

    for schedule in schedules:
        if schedule["view"].Name == "Material list":
            material_list = schedule["view"]
    
    if material_list:
        counter.increment_points()
        outputter.print_response("Material list schedule name", "OK.")

        check_material_list_content(material_list, outputter)
    else:
        outputter.print_response("Material list schedule name:" "Incorrect. No schedule named as <b><i>Material list</i></b> found.", "red")
    counter.increment_checks()


def check_views(outputter):
    views = get_project_views_and_viewports()
    
    outputter.print_md("### 1. Section name check:")
    sections = views.get("Section", [])
    check_section_names_and_get_sections_in_viewports(sections, outputter)
    check_annotations_used_in_sections(sections, outputter)

    outputter.print_md("### 2. Viewport type check:")
    check_viewports_have_correct_types(views, outputter)

    outputter.print_md("### 3. Schedule check:")
    schedules = views.get("Schedule", [])
    check_schedule_names_and_get_material_schedule(schedules, outputter)

    return counter
# -*- coding: utf-8 -*-

import re
from pyrevit import revit, DB
from score_counter import ScoreCounter

counter = ScoreCounter()

def get_project_views_and_viewports():
    views = {}
    views_in_viewport = []
    viewport_types = {}

    view_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.View)
    viewport_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.Viewport)
    
    # NOTE: This could be refactored. No need separate list for views in viewport.
    for viewport in viewport_collector:
        viewport_id = viewport.ViewId
        viewport_type = revit.doc.GetElement(viewport.GetTypeId()).get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
        views_in_viewport.append(viewport_id)
        viewport_types[viewport_id] = viewport_type

    for view in view_collector:
        view_type = str(view.ViewType)
        view_id = view.Id

        if (not view.IsTemplate and view.CanBePrinted) or view_type == "Schedule":
            if view_type not in views:
                views[view_type] = []
            
            if view_id in views_in_viewport:
                views[view_type].append((view, True))
            else:
                views[view_type].append((view, False))

    return views, viewport_types

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

def check_section_names_and_get_sections_in_viewports(views, outputter):
    sections_in_viewports = []

    if "Section" in views and len(views["Section"]) > 0:
        counter.increment_points()
        for section in views["Section"]:
            section_name = section[0].Name

            if section[0].IsCallout:
                check_callout_name(section_name, outputter)             
            else:
                check_section_name(section_name, outputter)

            if section[1]:
                sections_in_viewports.append(section[0])
    else:
        outputter.print_response("Section name", "No section views found on this project. At least one section should be used!", "red")
    counter.increment_checks()
    
    return sections_in_viewports

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

def check_annotations_used_in_sections(sections_in_viewports, outputter):
    for section in sections_in_viewports:
        check_annotations_in_section(section, "Max X+", "anchoring components", "Anchor", outputter)
        check_annotations_in_section(section, "Max Z+", "base plates", "Leg", outputter)
        check_annotations_in_section(section, "Fill type", "roof system", "Lifting point", outputter)


def check_material_list_headers(schedule, headers, num_of_cols):
    if len(headers) == num_of_cols:
        for col_index in range(num_of_cols):
            col_name = schedule.GetCellText(DB.SectionType.Body, 0, col_index)
            if headers[col_index] != col_name:
                print("Material list headers: Incorrect headers. Column {0} is named as {1}. Should be {2}".format(col_index + 1, col_name, headers[col_index]))
                return 0
    print("Material list headers: OK")
    return 1

def check_material_list_column_cells(schedule, headers, col_index, num_of_rows):
    for row_index in range(1, num_of_rows):
        cell_value = schedule.GetCellText(DB.SectionType.Body, row_index, col_index)
        
        if cell_value == "<varies>":
            print("{0} column: Non-unique value from the the row number {1}".format(headers[col_index], row_index))
            return 0

        if cell_value == "":
            print("{0} column: Empty value from the the row number {1}".format(headers[col_index], row_index))
            return 0
    
         
    print("{} column: OK".format(headers[col_index]))
    return 1

def check_material_list_content(schedule):
    points = 0
    checks = 0
    headers = ["Count", "Product number", "Product name (FIN)", "Product name (ENG)", "Product name (SWE)", "Weight", "Length info", "Width info"]
    
    table_data = schedule.GetTableData()
    section_data = table_data.GetSectionData(DB.SectionType.Body)
    num_of_rows = section_data.NumberOfRows
    num_of_cols = section_data.NumberOfColumns

    points += check_material_list_headers(schedule, headers, num_of_cols)
    checks += 1

    for col_index in range(1, 6):
        points += check_material_list_column_cells(schedule, headers, col_index, num_of_rows)
        checks += 1
    
    return points, checks

def check_schedule_names_and_get_material_schedule(views):
    points = 0
    checks = 0
    material_list = None

    for schedule in views.get("Schedule", []):
        schedule_view = schedule[0]
        if schedule_view.Name == "Material list":
            material_list = schedule_view
    
    if material_list:
        points += 1
        print("Material list schedule name: OK.")

        results = check_material_list_content(material_list)
        points += results[0]
        checks += results[1]
    else:
        print("Material list schedule name: Incorrect. No schedule named as [Material list] found.")
    checks += 1

    return points, checks

def check_viewports_have_correct_types(views, viewport_types):
    def check_correct_types(types, correct_type, view_type):
        if len(types) == 0:
            print("{0} viewport types: No {0} viewports are found on the project. At least one should be used.".format(view_type))
            return 0
        
        correct_types = True
        for type in types:
            viewport_name = type[0].Name
            viewport_type = type[1]

            if viewport_type != correct_type:
                print("{0} viewport types: Incorrect type for {1}. Type should be {2}".format(view_type, viewport_name, correct_type))
                correct_types = False
        
        if correct_types:
            print("{} viewport types: OK.".format(view_type))
            return 1
        
        return 0
        
    points = 0
    checks = 0
    floor_plan_types = [(view[0], viewport_types[view[0].Id]) for view in views.get("FloorPlan", []) if view[1]]
    section_types = [(view[0], viewport_types[view[0].Id]) for view in views.get("Section", []) if view[1] and not view[0].IsCallout]
    section_callout_types = [(view[0], viewport_types[view[0].Id]) for view in views.get("Section", []) if view[1] and view[0].IsCallout]

    points += check_correct_types(floor_plan_types, "Title basic", "Layout")
    checks += 1

    points += check_correct_types(section_types, "Title section", "Section")
    checks += 1

    if len(section_callout_types) > 0:
        points += check_correct_types(section_callout_types, "Title basic", "Section callout")
        checks += 1
    else:
        print("Section callout viewport types: OK. No viewports are found on the project.")

    return points, checks

def check_views(outputter):
    views, viewport_types = get_project_views_and_viewports()
    
    outputter.print_md("### 1. Section name check:")
    sections_in_viewports = check_section_names_and_get_sections_in_viewports(views, outputter)
    check_annotations_used_in_sections(sections_in_viewports, outputter)

    outputter.print_md("### 2. Viewport type check:")
    # To be continued...
    check_viewports_have_correct_types(views, viewport_types)

    points, checks = check_schedule_names_and_get_material_schedule(views)



    points, checks, percentage = counter.get_score_percentage()
    outputter.print_md("### <u>Project view check summary: Points gained {0} out of {1}. Score: {2}</u>".format(points, checks, percentage))
# -*- coding: utf-8 -*-

import re
from pyrevit import revit, DB

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

def check_section_names_and_get_sections_in_viewports(views):
    sections_in_viewports = []
    points = 0
    checks = 0

    if len(views["Section"]) > 0:
        points += 1
        for section in views["Section"]:
            section_name = section[0].Name

            if section[0].IsCallout:
                if re.match(r"^DET([1-9]|[1-9][0-9])$", section_name):
                    points += 1
                    print("Section name: Correct name [{}].".format(section_name))
                else:
                    print("Section name: Incorrect name [{}]. Callout section should be named as DET[number] whereas number is value between 1 - 99.".format(section_name))
                checks += 1                
            else:
                if re.match(r"^[A-Z1-9]$", section_name):
                    points += 1
                    print("Section name: Correct name [{}].".format(section_name))
                else:
                    print("Section name: Incorrect name [{}]. Use only single character and capitalized alphanumberic, such as A, B, 1 or 2.".format(section_name))
                checks += 1

            if section[1]:
                sections_in_viewports.append(section[0])
    else:
        print("Section name: No section views found on this project.")
    checks += 1
    
    return sections_in_viewports, points, checks

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


def check_annotations_used_in_sections(sections_in_viewports):
    points = len(sections_in_viewports) * 3
    checks = len(sections_in_viewports) * 3

    for section in sections_in_viewports:
        contains_anchor_families = contains_family_with_parameter_name(section, "Max X+")
        contains_base_plate_families = contains_family_with_parameter_name(section, "Max Z+")
        contains_roof_system = contains_family_with_parameter_name(section, "Fill type")
        contains_anchor_tags = contains_annotation(section, "Anchor")
        contains_leg_tags = contains_annotation(section, "Leg")
        contains_lifting_points_tags = contains_annotation(section, "Lifting points")
        
        if contains_anchor_families and not contains_anchor_tags:
            print("Anchor tags in section [{}]: Incorrect. Section has anchoring components, but no anchor tags.".format(section.Name))
            points -= 1
        elif not contains_anchor_families:
            print("Anchor tags in section [{}]: OK. Section does not have any anchors.".format(section.Name))
        else:
            print("Anchor tags in section [{}]: OK".format(section.Name))

        if contains_base_plate_families and not contains_leg_tags:
            print("Leg tags in section [{}]: Incorrect. Section has base plates, but no leg tags.".format(section.Name))
            points -= 1
        elif not contains_base_plate_families:
            print("Leg tags in section [{}]: OK. Section does not have any base plates.".format(section.Name))
        else:
            print("Leg tags in section [{}]: OK".format(section.Name))

        if contains_roof_system and not contains_lifting_points_tags:
            print("Lifting point tags in section [{}]: Incorrect. Section has roof system, but no lifting point tags.".format(section.Name))
            points -= 1
        elif not contains_roof_system:
            print("Lifting point in section [{}]: OK. Section does not have roof system.".format(section.Name))
        else:
            print("Lifting point in section [{}]: OK".format(section.Name))

    return points, checks

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

    points += check_correct_types(section_callout_types, "Title basic", "Section callout")
    checks += 1

    return points, checks

def check_views():
    view_points = 0
    view_checks = 0

    views, viewport_types = get_project_views_and_viewports()
    sections_in_viewports, points, checks = check_section_names_and_get_sections_in_viewports(views)
    view_points += points
    view_checks += checks

    points, checks = check_annotations_used_in_sections(sections_in_viewports)
    view_points += points
    view_checks += checks

    points, checks = check_schedule_names_and_get_material_schedule(views)
    view_points += points
    view_checks += checks

    points, checks = check_viewports_have_correct_types(views, viewport_types)
    view_points += points
    view_checks += checks

    return view_points, view_checks
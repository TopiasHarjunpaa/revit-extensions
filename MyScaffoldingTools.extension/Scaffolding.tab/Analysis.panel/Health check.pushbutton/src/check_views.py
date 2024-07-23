# -*- coding: utf-8 -*-

import re
from pyrevit import revit, DB

def get_project_views():
    views = {}
    views_in_viewport = []

    view_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.View)
    viewport_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.Viewport)
    
    for viewport in viewport_collector:
        views_in_viewport.append(viewport.ViewId)

    for view in view_collector:
        view_type = str(view.ViewType)
        view_id = view.Id

        if not view.IsTemplate and view.CanBePrinted:
            if view_type not in views:
                views[view_type] = []
            
            if view_id in views_in_viewport:
                views[view_type].append((view, True))
            else:
                views[view_type].append((view, False))

    return views

def check_section_names_and_get_sections_in_viewports(views):
    sections_in_viewports = []
    points = 0
    checks = 0

    if len(views["Section"]) > 0:
        points += 1
        for section in views["Section"]:
            section_name = section[0].Name

            if re.match(r'^[A-Z1-9]$', section_name):
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
    points = len(sections_in_viewports) * 2
    checks = len(sections_in_viewports) * 2

    for section in sections_in_viewports:
        contains_anchor_families = contains_family_with_parameter_name(section, "Max X+")
        contains_base_plate_families = contains_family_with_parameter_name(section, "Max Z+")
        contains_anchor_tags = contains_annotation(section, "Anchor")
        contains_leg_tags = contains_annotation(section, "Leg")
        
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

    return points, checks

def check_views():
    view_points = 0
    view_checks = 0

    views = get_project_views()
    sections_in_viewports, points, checks = check_section_names_and_get_sections_in_viewports(views)
    view_points += points
    view_checks += checks

    points, checks = check_annotations_used_in_sections(sections_in_viewports)
    view_points += points
    view_checks += checks

    return view_points, view_checks
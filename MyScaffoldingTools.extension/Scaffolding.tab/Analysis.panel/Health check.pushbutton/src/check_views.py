# -*- coding: utf-8 -*-

import re
from pyrevit import revit, DB

def get_all_project_views():
    view_points = 1
    view_checks = 1
    views = {}
    views_in_viewport = []

    view_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.View)
    viewport_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.Viewport)
    
    for viewport in viewport_collector:
        views_in_viewport.append(viewport.ViewId)
        print(viewport.ViewId)

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
    
    if len(views["Section"]) > 0:
        view_points += 1
        for section_view in views["Section"]:
            section_name = section_view[0].Name
            print(section_name)
            print(section_view[1])

            if re.match(r'^[A-Z1-9]$', section_name):
                view_points += 1
            else:
                print("Section name: Incorrect name [{}]. Use only single character and capitalized alphanumberic, such as A, B, 1 or 2.".format(section_name))
            view_checks += 1
    else:
        print("Section name: No section views found on this project.")
    view_checks += 1
    
    return views, view_points, view_checks


def check_views():
    views, view_points, view_checks = get_all_project_views()

    return view_points, view_checks
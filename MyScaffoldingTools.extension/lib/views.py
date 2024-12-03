# -*- coding: utf-8 -*-

from pyrevit import revit, DB

def get_project_views_and_viewports():
    """Collects and organizes project views and associated viewport information.

    Returns:
        dict: A dictionary where the keys are view types, and the values are lists of dictionaries containing
              view details (view object, in_viewport, viewport_type).
    """

    view_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.View)
    viewport_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.Viewport)

    viewports = {
        viewport.ViewId: revit.doc.GetElement(viewport.GetTypeId())
        .get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_NAME)
        .AsString()
        for viewport in viewport_collector
    }

    views = {}
    for view in view_collector:
        if view.IsTemplate or not view.CanBePrinted:
            if str(view.ViewType) != "Schedule":
                continue

        view_type = str(view.ViewType)
        view_id = view.Id
        in_viewport = view_id in viewports

        if view_type not in views:
            views[view_type] = []

        views[view_type].append({
            "view": view,
            "in_viewport": in_viewport,
            "viewport_type": viewports.get(view_id, None) if in_viewport else None,
        })

    return views
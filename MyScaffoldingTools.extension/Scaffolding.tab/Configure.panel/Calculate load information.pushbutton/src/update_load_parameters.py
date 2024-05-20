# -*- coding: utf-8 -*-

from pyrevit import revit, DB

def update_load_parameters(load_params):
    collector = DB.FilteredElementCollector(revit.doc).WhereElementIsNotElementType().ToElements()

    with DB.Transaction(revit.doc, "Update load parameters") as t:
        t.Start()
        for element in collector:
            for param in element.Parameters:
                if param.IsShared and param.StorageType == DB.StorageType.String:
                    param_name = param.Definition.Name
                    if param_name in load_params.keys():
                        new_value = load_params[param_name]
                        param.Set(new_value)
        t.Commit()
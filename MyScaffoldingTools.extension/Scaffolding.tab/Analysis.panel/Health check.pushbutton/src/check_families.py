# -*- coding: utf-8 -*-

from pyrevit import revit, DB
from products import find_families_with_unique_product_numbers
from score_counter import ScoreCounter

counter = ScoreCounter()

def check_family_identity_data(element):
    for param in ["Product name (FI)", "Product name (EN)", "Product name (SWE)"]:
        element_type = revit.doc.GetElement(element.GetTypeId())
        type_param = element_type.LookupParameter(param)
        if type_param and type_param.StorageType == DB.StorageType.String:
            continue
    # TODO

def check_families(outputter):
    counter.increment_checks()
    counter.increment_points()
    
    points, checks, percentage = counter.get_score_percentage()
    outputter.print_md("### <u>Family check summary: Points gained {0} out of {1}. Score: {2}</u>".format(points, checks, percentage))

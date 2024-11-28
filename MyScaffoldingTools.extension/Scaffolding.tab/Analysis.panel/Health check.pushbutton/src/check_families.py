# -*- coding: utf-8 -*-

from pyrevit import revit, DB
from products import find_families_with_unique_product_numbers

def check_family_identity_data(element):
    for param in ["Product name (FI)", "Product name (EN)", "Product name (SWE)"]:
        element_type = revit.doc.GetElement(element.GetTypeId())
        type_param = element_type.LookupParameter(param)
        if type_param and type_param.StorageType == DB.StorageType.String:
            continue
    # TODO

def check_families():
    families_with_product_number = find_families_with_unique_product_numbers()
    
    return 1, 1
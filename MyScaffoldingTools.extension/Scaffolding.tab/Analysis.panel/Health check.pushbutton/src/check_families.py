# -*- coding: utf-8 -*-

from pyrevit import revit, DB

def get_product_number(element):
    """Finds family parameter named as Product number and returns it as a string.
    In Revit scaffolding families, product number should be always shared parameter,
    usually type parameter but sometimes instance parameter.

    Args:
        element: Autodesk.Revit.DB Element class.

    Returns:
        str: Product number as string. None if element does not contain product number parameter.
    """

    instance_param = element.LookupParameter("Product number")
    if instance_param and instance_param.StorageType == DB.StorageType.String:
        return instance_param.AsString()
    
    element_type = revit.doc.GetElement(element.GetTypeId())
    type_param = element_type.LookupParameter("Product number")
    if type_param and type_param.StorageType == DB.StorageType.String:
        return type_param.AsString()
    
    return None

def has_both_diagonal_params(element):
    """Checks if diagonal family is set as double bracing. Diagonal family contains
    two yes/no parameters and if both of them are checked as yes, then the it is modeled
    as double bracing.

    Args:
        element: Autodesk.Revit.DB Element class.

    Returns:
        bool: Returns true if double bracing else false.
    """

    left_diagonal_param = element.LookupParameter("Left handed diagonal")
    right_diagonal_param = element.LookupParameter("Right handed diagonal")

    if left_diagonal_param and right_diagonal_param:
        if left_diagonal_param.AsInteger() == 1 and right_diagonal_param.AsInteger() == 1:
            return True
    return False

def is_roof_system(element):
    """Checks if scaffolding family is roof system or not. Roof systems contains fill type
    parameter which is used to identify roof system.

    Args:
        element: Autodesk.Revit.DB Element class.

    Returns:
        bool: Returns true if roof system else false.
    """

    fill_type = element.LookupParameter("Fill type")
    
    return True if fill_type else False

def find_scaffolding_components():
    """Finds all scaffolding families in a Revit project which contains Product number (which are typically sub families).
    In addition to these, finds a main families (ie. functional families which controls the sub families) which may not
    have product number parameter, but are wanted to be proceeded during health check.

    Returns:
        list(Autodesk.Revit.DB, str): Sorted list of tuples where 1st item is Element class and 2nd item is product number.
    """

    collector = DB.FilteredElementCollector(revit.doc)\
                .OfCategory(DB.BuiltInCategory.OST_GenericModel)\
                .WhereElementIsNotElementType()
    
    scaffolding_families = []

    for element in collector:
        product_number = get_product_number(element)
        
        if product_number:
            scaffolding_families.append((element, product_number))
            continue

        if has_both_diagonal_params(element):
            scaffolding_families.append((element, "DOUBLE"))
        
        if is_roof_system(element):
            scaffolding_families.append((element, "ROOF"))
    
    return scaffolding_families

def check_families():
    print("Checking families...")
    score = find_scaffolding_components()
    print("...Family checking completed")

    return score
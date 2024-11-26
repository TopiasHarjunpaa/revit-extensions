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

def contains_family_with_parameter_name(element, parameter_name):
    """Identifies scaffolding family based on certain parameter.

    Args:
        element: Autodesk.Revit.DB Element class.
        parameter_name (str): Parameter name to be looked from the family. 

    Returns:
        bool: Returns true if parameter is in family else false.
    """

    return True if element.LookupParameter(parameter_name) else False

def sort_elements(elements, double_bracing = None, roof_system = None, anchor = None):
    """Sorts list of elements in predefined order to ensure proper coloring overrides.
    Items which are placed at the end of the list are main families which contains sub families and
    are wanted to be colored in same color than the main family.

    3. Roof system main family
    2. Diagonal braces main family if both diagonals are checked active
    1. Anchoring main family 

    Args:
        list(Autodesk.Revit.DB, str): List of tuples where 1st item is Element class and 2nd item is product number.
        double_bracing (str, optional): Product number for double braced families. Defaults to None.
        roof_system (bool, optional): Product number for roof system families. Defaults to None.
        anchor (bool, optional): Product number for anchoring families. Defaults to None.

    Returns:
        list: Sorted list of tuples.
    """

    def get_sort_key(element):
        product_number = element[1]

        if product_number == roof_system:
            return 3
        if product_number == double_bracing:
            return 2
        if product_number == anchor:
            return 1
        return 0

    return sorted(elements, key=get_sort_key)

def find_scaffolding_components(double_bracing = None, roof_system = None, anchor = None):
    """Finds all scaffolding families in a Revit project which contains Product number (which are typically sub families).
    In addition to these, finds a main families (ie. functional families which controls the sub families) which may not
    have product number parameter, but are wanted to be identified for color coding purposes. 
    Such main families can be included into search by defining "mock" product number for such types as argument.

    Args:
        double_bracing (str, optional): Product number for double braced families. Defaults to None.
        roof_system (bool, optional): Product number for roof system families. Defaults to None.
        anchor (bool, optional): Product number for anchoring families. Defaults to None.

    Returns:
        list(Autodesk.Revit.DB, str): Sorted list of tuples where 1st item is Element class and 2nd item is product number.
    """

    collector = DB.FilteredElementCollector(revit.doc)\
                .OfCategory(DB.BuiltInCategory.OST_GenericModel)\
                .WhereElementIsNotElementType()
    
    scaffolding_families = []

    for element in collector:
        product_number = get_product_number(element)
        is_double_bracing = False if double_bracing is None else has_both_diagonal_params(element)
        is_roof_system = False if roof_system is None else contains_family_with_parameter_name(element, "Fill type")
        is_anchor = False if anchor is None else contains_family_with_parameter_name(element, "Max X+")
        
        if product_number:
            scaffolding_families.append((element, product_number))

        if is_double_bracing:
            scaffolding_families.append((element, double_bracing))
        
        if is_roof_system:
            scaffolding_families.append((element, roof_system))
        
        if is_anchor:
            scaffolding_families.append((element, anchor))
    
    return sort_elements(scaffolding_families, double_bracing, roof_system, anchor)
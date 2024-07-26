# -*- coding: utf-8 -*-

from color_coding_rules import DOUBLE_BRACING, ROOF_SYSTEM, ANCHOR, get_color_for_product_number
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

def sort_elements(elements):
    """Sorts list of elements in predefined order to ensure proper coloring overrides.
    Items which are placed at the end of the list are main families which contains sub families and
    are wanted to be colored in same color than the main family.

    3. Roof system main family
    2. Diagonal braces main family if both diagonals are checked active
    1. Anchoring main family 

    Args:
        list(Autodesk.Revit.DB, str): List of tuples where 1st item is Element class and 2nd item is product number.

    Returns:
        list: Sorted list of tuples.
    """

    def get_sort_key(element):
        product_number = element[1]

        if product_number == ROOF_SYSTEM:
            return 3
        if product_number == DOUBLE_BRACING:
            return 2
        if product_number == ANCHOR:
            return 1
        return 0

    return sorted(elements, key=get_sort_key)

def find_scaffolding_components():
    """Finds all scaffolding families in a Revit project which contains Product number (which are typically sub families).
    In addition to these, finds a main families (ie. functional families which controls the sub families) which may not
    have product number parameter, but are wanted to be identified for color coding purposes.

    Returns:
        list(Autodesk.Revit.DB, str): Sorted list of tuples where 1st item is Element class and 2nd item is product number.
    """

    collector = DB.FilteredElementCollector(revit.doc)\
                .OfCategory(DB.BuiltInCategory.OST_GenericModel)\
                .WhereElementIsNotElementType()
    
    scaffolding_families = []

    for element in collector:
        product_number = get_product_number(element)
        is_roof_system = contains_family_with_parameter_name(element, "Fill type")
        is__anchor = contains_family_with_parameter_name(element, "Max X+")
        
        if product_number:
            scaffolding_families.append((element, product_number))

        if has_both_diagonal_params(element):
            scaffolding_families.append((element, DOUBLE_BRACING))
        
        if is_roof_system:
            scaffolding_families.append((element, ROOF_SYSTEM))
        
        if is__anchor:
            scaffolding_families.append((element, ANCHOR))
    
    return sort_elements(scaffolding_families)

def apply_color_overrides(element, product_number, ogs, solid_fill_pattern):
    """Applies graphical overrides to the scaffolding families. Product number
    is used to determine the color coding rules.

    Args:
        element: Autodesk.Revit.DB Element class.
        product_number (str): Product number as string.
        ogs: Autodesk.Revit.DB OverrideGraphicSettings class.
        solid_fill_pattern: Autodesk.Revit.DB FillPatternElement class.
    """

    color = get_color_for_product_number(product_number)
    ogs.SetSurfaceForegroundPatternId(solid_fill_pattern.Id)
    ogs.SetSurfaceForegroundPatternColor(color)
    
    apply_color_overrides_recursive(element, ogs)

def apply_color_overrides_recursive(element, ogs): 
    """Applies graphical overrides recursive to the scaffolding sub families.
    Makes sure that all sub families and their sub families are colored using
    the same rule than the main family.

    Args:
        element: Autodesk.Revit.DB Element class.
        ogs: Autodesk.Revit.DB OverrideGraphicSettings class.
    """

    revit.active_view.SetElementOverrides(element.Id, ogs)

    if hasattr(element, "GetSubComponentIds"):
        sub_components = element.GetSubComponentIds()
        for sub_element_id in sub_components:
            sub_element = revit.doc.GetElement(sub_element_id)
            apply_color_overrides_recursive(sub_element, ogs)

def color_code_components():
    """Finds scaffolding components, initializes the OverrideGraphicSettings class, selects solid fill pattern
    and overrides current graphical settings of the scaffolding components using predefined set of coloring rules.
    """
    
    elements_with_product_number = find_scaffolding_components()
    
    ogs = DB.OverrideGraphicSettings()
    solid_fill_pattern = DB.FillPatternElement.GetFillPatternElementByName(revit.doc, DB.FillPatternTarget.Drafting, "<Solid fill>")

    if solid_fill_pattern is None:
        print("Solid fill pattern not found. Please ensure it is available in the project.")
        return

    with DB.Transaction(revit.doc, "Override Graphics") as t:
        t.Start()
        for element, product_number in elements_with_product_number:
            apply_color_overrides(element, product_number, ogs, solid_fill_pattern)
        t.Commit()

def reset_graphic_overrides():
    """Resets graphical overrides to the Revit default settings. This is called from another extension module
    through distinct push button.
    """

    elements_with_product_number = find_scaffolding_components()
    
    ogs = DB.OverrideGraphicSettings()

    with DB.Transaction(revit.doc, "Reset Graphics") as t:
        t.Start()
        for element, _ in elements_with_product_number:
            revit.active_view.SetElementOverrides(element.Id, ogs)
        t.Commit()
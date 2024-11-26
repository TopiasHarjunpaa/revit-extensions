# -*- coding: utf-8 -*-

import math
from pyrevit import revit, DB
from products import find_scaffolding_components

BLUE = DB.Color(140, 120, 255)
ORANGE = DB.Color(255, 165, 0)
RED = DB.Color(255, 0, 0)
MAGENTA = DB.Color(255, 0, 255)
LIGHT_GREEN = DB.Color(160, 255, 160)
GREEN = DB.Color(120, 255, 120)
WHITE = DB.Color(255, 255, 255)
DOUBLE_BRACING = "DOUBLE"
ROOF_SYSTEM = "ROOF"
ANCHOR = "ANCHOR"

def get_color_for_product_number(product_number, color_rules):
    """Returns color for certain product based on set of color rules.

    Args:
        product_number (str): Product number as string.
        color_rules: List of tuples whereas first item is color and second item product number.

    Returns:
        Autodesk.Revit.DB.Color: Color based on product number.
    """

    for color, prefixes in color_rules[:-1]:
        if any(product_number.startswith(prefix) for prefix in prefixes):
            return color
    return color_rules[-1]


def blend_color_with_black(color, blend_factor):
    """Blends a given color with black by interpolating their RGB values.
    Returns black color if surface color (given as argument) is white.

    Args:
        color: Autodesk.Revit.DB.Color instance representing the original color.
        blend_factor (float): Blending factor (0 = black, 1 = original color).

    Returns:
        Autodesk.Revit.DB.Color: A new color that is a blend between the input color and black.
    """
    if color is WHITE:
        return DB.Color(0, 0, 0)
    
    r = int(color.Red * blend_factor)
    g = int(color.Green * blend_factor)
    b = int(color.Blue * blend_factor)
    return DB.Color(r, g, b)

def apply_color_overrides(element, product_number, ogs, solid_fill_pattern, color_rules, blend_factor):
    """Applies graphical overrides (surface and projection lines) to the scaffolding families. 
    Product number is used to determine the color coding rules.

    Args:
        element: Autodesk.Revit.DB Element class.
        product_number (str): Product number as string.
        ogs: Autodesk.Revit.DB OverrideGraphicSettings class.
        solid_fill_pattern: Autodesk.Revit.DB FillPatternElement class.
        color_rules: List of tuples whereas first item is color and second item product number.
        blend_factor (float): Blending factor (0 = black, 1 = original color).
    """

    color = get_color_for_product_number(product_number, color_rules)
    ogs.SetSurfaceForegroundPatternId(solid_fill_pattern.Id)
    ogs.SetSurfaceForegroundPatternColor(color)

    projection_color = blend_color_with_black(color, blend_factor)
    ogs.SetProjectionLineColor(projection_color)
    
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

def color_code_components(color_rules):
    """Finds scaffolding components, initializes the OverrideGraphicSettings class, selects solid fill pattern
    and overrides current graphical settings of the scaffolding components using set of coloring rules.

    Args:
        color_rules: List of tuples whereas first item is color and second item product number.
    """
    
    elements_with_product_number = find_scaffolding_components(DOUBLE_BRACING, ROOF_SYSTEM, ANCHOR)
    
    current_view_scale = revit.active_view.Scale
    blend_factor = min(0.65, max(0.15, (math.log(current_view_scale) - math.log(50)) / (math.log(500) - math.log(50))))

    ogs = DB.OverrideGraphicSettings()
    solid_fill_pattern = DB.FillPatternElement.GetFillPatternElementByName(revit.doc, DB.FillPatternTarget.Drafting, "<Solid fill>")

    if solid_fill_pattern is None:
        print("Solid fill pattern not found. Please ensure it is available in the project.")
        return

    with DB.Transaction(revit.doc, "Override Graphics") as t:
        t.Start()
        for element, product_number in elements_with_product_number:
            apply_color_overrides(element, product_number, ogs, solid_fill_pattern, color_rules, blend_factor)
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
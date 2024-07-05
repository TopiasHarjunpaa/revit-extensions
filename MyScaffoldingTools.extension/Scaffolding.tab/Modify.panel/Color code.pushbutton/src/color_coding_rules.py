# -*- coding: utf-8 -*-

from pyrevit import DB

BLUE = DB.Color(140, 120, 255)
ORANGE = DB.Color(255, 165, 0)
RED = DB.Color(255, 0, 0)
MAGENTA = DB.Color(255, 0, 255)
LIGHT_GREEN = DB.Color(160, 255, 160)
GREEN = DB.Color(120, 255, 120)
DOUBLE_BRACING = "DOUBLE"
ROOF_SYSTEM = "ROOF"

color_rules = [
    (MAGENTA, [DOUBLE_BRACING]),
    (LIGHT_GREEN, ["3801", "3862", "3863", "3812", "3802", "2675"]),
    (GREEN, ["3878", "3880"]),
    (ORANGE, ["2640", ROOF_SYSTEM]),
    (RED, ["AL"]),
]

def get_color_for_product_number(product_number):
    for color, prefixes in color_rules:
        if any(product_number.startswith(prefix) for prefix in prefixes):
            return color
    return BLUE
from color_code import (
    color_code_components,                 
    MAGENTA,
    LIGHT_GREEN,
    GREEN,
    ORANGE,
    RED,
    BLUE,
    DOUBLE_BRACING,
    ROOF_SYSTEM,
    ANCHOR,
    LIFTING_POINT
)

color_rules = [
    (MAGENTA, [DOUBLE_BRACING]),
    (LIGHT_GREEN, ["3801", "3862", "3863", "3812", "3802", "2675"]),
    (GREEN, ["3878", "3880"]),
    (ORANGE, ["2640", ROOF_SYSTEM]),
    (RED, [ANCHOR, LIFTING_POINT]),
    BLUE
]

def main():
    color_code_components(color_rules)

if __name__ == "__main__":
    main()


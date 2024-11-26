from color_code import (
    color_code_components,
    MAGENTA,
    RED,
    WHITE,
    DOUBLE_BRACING,
    ANCHOR
)

color_rules = [
    (MAGENTA, [DOUBLE_BRACING]),
    (RED, [ANCHOR]),
    WHITE
]

def main():
    color_code_components(color_rules)

if __name__ == "__main__":
    main()


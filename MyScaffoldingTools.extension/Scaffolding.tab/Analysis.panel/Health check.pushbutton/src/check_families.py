# -*- coding: utf-8 -*-

from pyrevit import revit
from collections import defaultdict
import re
from score_counter import ScoreCounter

counter = ScoreCounter()

def separate_main_families(elements):
    """Separates elements into two dictionaries (main families and sub families)
    with counts of each unique element.

    Args:
        elements (list): List of elements to process.

    Returns:
        tuple: Two dictionaries:
            - main_family_names: {element_name: count}
            - sub_family_names: {element_name: count}
    """

    main_family_names = defaultdict(int)
    sub_family_names = defaultdict(int)

    for element_id in elements:
        element = revit.doc.GetElement(element_id)
        name = element.Name if hasattr(element, "Name") else str(element)
        if re.match(r"^\d{2}_", name):
            main_family_names[name] += 1
        else:
            sub_family_names[name] += 1

    return dict(main_family_names), dict(sub_family_names)

def check_overlapping_families(outputter):
    """Reads and reports Revit warnings related to identical overlapping instances."""

    counter.increment_checks(2)
    doc = revit.doc
    warnings = doc.GetWarnings()

    if not warnings:
        counter.increment_points(2)
        outputter.print_response("Overlapping elements", "OK. No overlapping elements found.")
        return

    unique_elements = set()
    for warning in warnings:
        description = warning.GetDescriptionText()

        if "identical" in description.lower():
            unique_elements.update(warning.GetFailingElements())
            
 
    main_families, sub_families = separate_main_families(unique_elements)

    if main_families:
        outputter.print_response(
            "Overlapping main families",
            "There are identical overlapping main families. This results double counting in material list",
            "red"
        )
        main_family_string = ["{0} ({1} overlapping {2})".format(name, count / 2, "pairs" if count / 2 > 1 else "pair") for name, count in main_families.items()]
        outputter.print_list(main_family_string)
    else:
        counter.increment_points()
        outputter.print_response("Overlapping main families", "OK. There are no identical overlapping main families.")
        if sub_families:
            outputter.print_response(
            "Overlapping sub families",
            "There are identical overlapping sub families. This results double counting in material list",
            "red"
        )
        sub_family_string = ["{0} ({1} overlapping {2})".format(name, count / 2, "pairs" if count / 2 > 1 else "pair") for name, count in sub_families.items()]
        outputter.print_list(sub_family_string)
            

def check_families(outputter):
    check_overlapping_families(outputter)

    return counter

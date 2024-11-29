from src.check_families import check_families
from src.check_project_parameters import check_params
from src.check_file_properties import check_file_properties
from src.check_views import check_views
from outputter import Outputter

outputter = Outputter()

def main():
    outputter.print_md("# Health Check Results")
    
    outputter.print_md("## Checking families...")
    family_points, family_checks = check_families(outputter)
    family_score = family_points * 100 / family_checks
    outputter.print_md("Points gained {0} out of {1}. **Family score: {2} %**".format(family_points, family_checks, family_score))

    outputter.print_md("## Checking project parameters...")
    check_params(outputter)
    
    outputter.print_md("## Checking file properties...")
    check_file_properties(outputter)

    outputter.print_md("## Checking project views...")
    view_points, view_checks = check_views(outputter)
    view_score = view_points * 100 / view_checks
    outputter.print_md("Points gained {0} out of {1}. **View score: {2} %**".format(view_points, view_checks, view_score))

if __name__ == "__main__":
    main()


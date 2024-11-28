from pyrevit import output

from src.check_families import check_families
from src.check_project_parameters import check_params
from src.check_file_properties import check_file_properties
from src.check_views import check_views


def main():
    out = output.get_output()
    out.print_md("# Health Check Results")
    
    out.print_md("## Checking families...")
    family_points, family_checks = check_families(out)
    family_score = family_points * 100 / family_checks
    out.print_md("Points gained {0} out of {1}. **Family score: {2} %**".format(family_points, family_checks, family_score))

    out.print_md("## Checking project parameters...")
    project_param_points, project_param_checks = check_params(out)
    project_param_score = project_param_points * 100 / project_param_checks
    out.print_md("Points gained {0} out of {1}. **Project parameter score: {2} %**".format(project_param_points, project_param_checks, project_param_score))

    out.print_md("## Checking file properties...")
    file_points, file_checks = check_file_properties(out)
    file_score = file_points * 100 / file_checks
    out.print_md("Points gained {0} out of {1}. **File properties score: {2} %**".format(file_points, file_checks, file_score))


    out.print_md("## Checking project views...")
    view_points, view_checks = check_views(out)
    view_score = view_points * 100 / view_checks
    out.print_md("Points gained {0} out of {1}. **View score: {2} %**".format(view_points, view_checks, view_score))


if __name__ == "__main__":
    main()


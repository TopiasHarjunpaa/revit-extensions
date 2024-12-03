from src.check_families import check_families
from src.check_project_parameters import check_params
from src.check_file_properties import check_file_properties
from src.check_views import check_views
from outputter import Outputter

outputter = Outputter()

def main():
    outputter.print_md("# Health Check Results")
    
    outputter.print_md("## Checking families...")
    family_counter = check_families(outputter)

    outputter.print_md("## Checking project parameters...")
    param_counter = check_params(outputter)
    
    outputter.print_md("## Checking file properties...")
    file_counter = check_file_properties(outputter)

    outputter.print_md("## Checking project views...")
    view_counter = check_views(outputter)

    total_counter = family_counter + param_counter + file_counter + view_counter
    points, checks, percentage = total_counter.get_score_percentage()

    outputter.print_md("# Final Results:")
    outputter.print_md("### <u>Total points gained {0} out of {1}. Total score: {2}</u>".format(points, checks, percentage))

if __name__ == "__main__":
    main()


from src.check_families import check_families
from src.check_project_parameters import check_params
from src.check_file_properties import check_file_properties
from src.check_views import check_views
from outputter import Outputter

outputter = Outputter()

def main():
    outputter.print_md("# Health Check Results")
    
    outputter.print_md("## Checking families...")
    check_families(outputter)

    outputter.print_md("## Checking project parameters...")
    check_params(outputter)
    
    outputter.print_md("## Checking file properties...")
    check_file_properties(outputter)

    outputter.print_md("## Checking project views...")
    check_views(outputter)

if __name__ == "__main__":
    main()


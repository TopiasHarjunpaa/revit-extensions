from src.check_families import check_families
from src.check_project_parameters import check_project_params
from src.check_file_properties import check_file_properties


def main():
    print("Checking families...")
    family_points, family_checks = check_families()
    family_score = family_points * 100 / family_checks
    print("Family checking completed")
    print("Points gained {0} out of {1}. Family score: {2} %".format(family_points, family_checks, family_score))
    print("---")

    print("Checking project parameters...")
    project_param_points, project_param_checks = check_project_params()
    project_param_score = project_param_points * 100 / project_param_checks
    print("Project parameter checking completed")
    print("Points gained {0} out of {1}. Project parameter score: {2} %".format(project_param_points, project_param_checks, project_param_score))
    print("---")
    
    print("Checking file properties...")
    file_points, file_checks = check_file_properties()
    file_score = file_points * 100 / file_checks
    print("File properties checking completed")
    print("Points gained {0} out of {1}. File properties score: {2} %".format(file_points, file_checks, file_score))
    print("---")

if __name__ == "__main__":
    main()


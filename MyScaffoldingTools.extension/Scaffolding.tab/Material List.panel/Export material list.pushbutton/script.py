import os

from src.information_service import (
    get_project_language,
    get_project_parameters,
    get_additional_notes, 
    get_headers,
    get_schedule_information,
    format_output_filename
)
from src.file_service import get_master_data, write_to_xlsx
from src.material_list import create_material_list

def main():
    main_language = get_project_language()

    if main_language:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        master_file_path = os.path.join(base_dir, "assets", "master_material_list.csv")

        output_file_name = format_output_filename(main_language)
        output_file_path = os.path.join(base_dir, "assets", output_file_name)

        master_data = get_master_data(master_file_path)
        schedule_data = get_schedule_information("Material list")
        material_list, notes, totals = create_material_list(schedule_data, master_data, main_language)

        project_params = get_project_parameters(main_language, total_weight=totals[0], total_price=totals[1])
        project_notes = get_additional_notes(main_language, notes)
        headers = get_headers(main_language)
        
        if len(material_list) > 0:
            write_to_xlsx(project_params, project_notes, headers, material_list, output_file_path)
        else:
            print("Export cancelled. Verify that schedule is correctly named and project contains scaffolding material.")

if __name__ == "__main__":
    main()


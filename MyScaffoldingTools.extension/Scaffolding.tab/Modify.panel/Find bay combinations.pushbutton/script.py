from src.bay_input_form import show_bay_form
from src.find_bay_combo import print_bay_combo_information


def main():
    input_params = show_bay_form()
    if input_params:
        distance, tolerance, bay_filters = input_params
        print_bay_combo_information(distance, tolerance, bay_filters)

if __name__ == "__main__":
    main()


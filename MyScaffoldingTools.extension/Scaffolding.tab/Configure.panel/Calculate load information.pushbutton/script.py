from src.load_input_form import show_input_form
from src.calculate_load_Information import calculate_load_information
from src.update_load_parameters import update_load_parameters


def main():
    input_params = show_input_form()
    if input_params:
        load_params = calculate_load_information(input_params)
        update_load_parameters(load_params)

if __name__ == "__main__":
    main()


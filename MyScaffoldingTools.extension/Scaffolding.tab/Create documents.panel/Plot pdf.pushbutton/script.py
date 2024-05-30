import os

from src.plotter import format_output_filename, plot_sheets_to_pdf

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_file_name = format_output_filename()
    output_file_path = os.path.join(base_dir, "assets", output_file_name)
    
    plot_sheets_to_pdf(output_file_path)

if __name__ == "__main__":
    main()


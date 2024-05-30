import xlsxwriter
import csv
import os
from translations import REVIT_PARAMS

def get_master_data(file_path):
    with open(file_path, "rb") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader, None) # Skip the header
        data = []
        for row in reader:
            product_number = row[0]
            price = float(row[5].replace(",", "."))
            data.append([product_number, price])
    return data

def write_to_xlsx(project_params, notes, headers, material_list, file_path):
    workbook = xlsxwriter.Workbook(file_path)
    main_worksheet = workbook.add_worksheet("Main")
    list_worksheet = workbook.add_worksheet("List")
    row_counter = 1

    column_widths_main = [2, 20, 45, 15, 8.43, 8.43, 8.43, 8.43]
    column_widths_list = [2, 20, 45, 20, 20, 20, 45, 45]
    for i in range(8):
        main_worksheet.set_column(i, i, column_widths_main[i])
        list_worksheet.set_column(i, i, column_widths_list[i])
    main_worksheet.set_row(0, 12)
    list_worksheet.set_row(0, 12)

    project_param_format = workbook.add_format({"align": "center", "valign": "vcenter", "bg_color": "#ffe8cf", "border": 1})
    notes_bold_format = workbook.add_format({"align": "center", "valign": "vcenter", "bg_color": "#e6dfd8", "bold": True, "border": 1})
    notes_italic_format = workbook.add_format({"align": "center", "valign": "vcenter", "bg_color": "#e6dfd8", "italic": True, "border": 1})
    material_format = workbook.add_format({"align": "center", "valign": "vcenter"})
    number_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'num_format': '0.00'})


    # Main worksheet
    project_param_keys = REVIT_PARAMS + ["Date", "Total weight", "Total price"]
    for key in project_param_keys:
        param_name = project_params[key][0]
        param_value = project_params[key][1]
        main_worksheet.merge_range(row_counter, 1, row_counter, 3, "{0}: {1}".format(param_name, param_value), project_param_format)
        row_counter += 1

    if notes:
        row_counter += 1
        for idx, item in enumerate(notes):
            format_to_use = notes_bold_format if idx == 0 else notes_italic_format
            main_worksheet.merge_range(row_counter, 1, row_counter, 3, item, format_to_use)
            row_counter += 1
    
    row_counter += 2
    
    table_start_row_main = row_counter
    table_end_row_main = row_counter + len(material_list)
    table_range_main = "B{0}:D{1}".format(table_start_row_main, table_end_row_main)

    main_worksheet.add_table(table_range_main, {
        "columns": [{"header": col_name, "header_format": material_format, "format": material_format} for col_name in headers],
        "style": "Table Style Medium 14",
        "data": material_list
    })

    # List worksheet
    table_start_row_list = 2
    table_end_row_list = 2 + len(material_list)
    table_range_list = "B{0}:H{1}".format(table_start_row_list, table_end_row_list)
    
    list_worksheet.add_table(table_range_list, {
        "columns": [
            {
                "header": col_name,
                "header_format": material_format,
                "format": number_format if col_idx in [3, 4] else material_format
            } 
        for col_idx, col_name in enumerate(headers)
        ],
        "style": "Table Style Medium 14",
        "data": material_list
    })

    workbook.close()

    os.startfile(file_path)
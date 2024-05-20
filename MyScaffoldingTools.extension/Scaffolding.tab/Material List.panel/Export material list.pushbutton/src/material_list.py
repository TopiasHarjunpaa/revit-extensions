# -*- coding: utf-8 -*-

import re

def get_tarpaulin_parameters(length, width):
	tarpaulin_length = float(length)/1000
	tarpaulin_width = float(width)/1000
	tarpaulin_area = tarpaulin_length * tarpaulin_width
	return tarpaulin_length, tarpaulin_width, tarpaulin_area

def format_tarpaulin_product_number(product_number, length, width):
	if width != 2.572:
		return "KHTASAUS"
	return "{0}{1}".format(product_number, int(length))

def format_tarpaulin_names(fin, eng, swe, length, width):
	suffix = " {0:.2f} x {1:.2f} m".format(width, length).replace(".", ",")
	if width == 0.154:
		suffix = " {0:.3f} x {1:.2f} m".format(width, length).replace(".", ",")
	fin += suffix
	eng += suffix.replace("m", "M")
	swe += suffix
	return fin, eng, swe

def format_anchor_ledger_name(count, ledger_name):
    formatted_name = re.sub(r"\s*\(.*\)", "", ledger_name)
    formatted_name = " - {0} x {1}".format(count, formatted_name)

    return formatted_name

def create_material_list(schedule_data, master_data, language="ENG"):
	material_list = []
	language_index = {"FIN": 2, "ENG": 3, "SWE": 4}[language]
	total_weight = 0.00
	total_price = 0.00
	notes = {}
	roof_system = False

	if len(schedule_data) == 0:
		return material_list, notes, (total_weight, total_price)

	for product in schedule_data[1:]:
		count = int(product[0])
		product_number = product[1]
		name_fin = product[2]
		name_eng = product[3]
		name_swe = product[4]
		weight = float(product[5])
		total_weight += weight * int(count)
		found = False

		if product_number == "KHKATT" and len(product) >= 8:
			roof_system = True
			tarpaulin_length, tarpaulin_width, tarpaulin_area = get_tarpaulin_parameters(product[6], product[7])
			edited_product_number = format_tarpaulin_product_number(product_number, tarpaulin_length, tarpaulin_width)
			edited_name_fin, edited_name_eng, edited_name_swe = format_tarpaulin_names(name_fin, name_eng, name_swe, tarpaulin_length, tarpaulin_width)
			
			weight = round(tarpaulin_area * 0.67, 2)
			price = round(tarpaulin_area * 12.7, 2)
			total_weight += weight * int(count)
			total_price += price * int(count)

			row = [count, edited_product_number, edited_name_fin, edited_name_eng, edited_name_swe, weight, price]
			sorted_row = sort_rows(language_index, row)
			material_list.append(sorted_row)
			found = True # Do not add this row into material list
		else:
			for master_product in master_data:
				m_product_number = master_product[0]
				m_price = master_product[1]

				if product_number == m_product_number:
					row = [count, product_number, name_fin, name_eng, name_swe, weight, m_price]
					sorted_row = sort_rows(language_index, row)
					material_list.append(sorted_row)
					total_price += m_price * int(count)
					found = True # Do not add this row into material list
					break
		
		if product_number == "SUSPENDED":
			notes["Suspended"] = product[language_index]
			found = True # Do not add this row into material list
		
		if product_number.startswith("AL"):
			formatted_note = format_anchor_ledger_name(count, product[language_index])
			notes.setdefault("Anchoring", []).append(formatted_note)
			found = True # Do not add this row into material list

		if not found:
			row = [count, product_number, name_fin, name_eng, name_swe, weight, 0.00]
			sorted_row = sort_rows(language_index, row)
			material_list.append(sorted_row)
		
	if roof_system:
		row = [0, "KHPÄÄT", "Muista lisätä päätypeitteet", "REMEMBER GABLE TARPAULINS", "Komma ihåg gavelduk", 0.00, 0.00]
		sorted_row = sort_rows(language_index, row)
		material_list.append(sorted_row)

	return material_list, notes, (total_weight, total_price)

def sort_rows(language_index, row):
	"""Raw row order:
	0:	count
	1:	product number
	2:	name FIN
	3:	name ENG
	4:	name SWE
	5:	weight
	6:	price
	"""

	secondary_names_indexes = [2, 3, 4]
	secondary_names_indexes.remove(language_index)
	sorted_indexes = [1, language_index, 0, 5, 6] + secondary_names_indexes
	
	return [row[i] for i in sorted_indexes]
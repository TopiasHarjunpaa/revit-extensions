# -*- coding: utf-8 -*-

import re
import math

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

def calculate_wire_sets(length, set_40=0, set_60=0):
	if length > 2000000: # Just to prevent memory errors. Input shouldn't be this high anyways.
		print("Desired safety wire length is more than 2 kilometers. Only 60 m sets are used.")
		return set_40, int(math.ceil(float(length) / 600000))
	
	if length <= 0:
		return set_40, set_60
	
	if length > 80000:
		return calculate_wire_sets(length - 60000, set_40, set_60 + 1)
	
	result_40 = calculate_wire_sets(length - 40000, set_40 + 1, set_60)
	result_60 = calculate_wire_sets(length - 60000, set_40, set_60 + 1)

	if sum(result_40) < sum(result_60):
		return result_40
	
	elif sum(result_40) > sum(result_60):
		return result_60
	
	return result_40 if result_40[0] >= result_60[0] else result_60


def create_material_list(schedule_data, master_data, language="ENG"):
	material_list = []
	language_index = {"FIN": 2, "ENG": 3, "SWE": 4}[language]
	total_weight = 0.00
	total_price = 0.00
	notes = {}
	roof_system = False
	safety_wire_sets = (0, 0)

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
		
		if product_number == "VALJAS":
			wire_set_length = float(product[6])
			number_of_40_sets, number_of_60_sets = calculate_wire_sets(wire_set_length)
			safety_wire_sets = (safety_wire_sets[0] + count * number_of_40_sets, safety_wire_sets[1] + count * number_of_60_sets)
			found = True # Do not add this row into material list

		if not found:
			row = [count, product_number, name_fin, name_eng, name_swe, weight, 0.00]
			sorted_row = sort_rows(language_index, row)
			material_list.append(sorted_row)
		
	if roof_system:
		row = [0, "KHPÄÄT", "Muista lisätä päätypeitteet", "REMEMBER GABLE TARPAULINS", "Komma ihåg gavelduk", 0.00, 0.00]
		sorted_row = sort_rows(language_index, row)
		material_list.append(sorted_row)
	
	if safety_wire_sets != (0, 0):
		number_of_40_sets, number_of_60_sets = safety_wire_sets

		# At the moment these are just fixed values to get rough estimates.
		# Later on, read the values from master list.
		weight_40 = 25
		weight_60 = 35
		price_40 = 1500
		price_60 = 2000
		total_weight += number_of_40_sets * weight_40 + number_of_60_sets + weight_60
		total_price += number_of_40_sets * price_40 + number_of_60_sets * price_60

		if number_of_40_sets > 0:
			row = [number_of_40_sets, product_number + "40", name_fin + " 40 m", name_eng + " 40 M", name_swe + " 40 m", weight_40, price_40]
			sorted_row = sort_rows(language_index, row)
			material_list.append(sorted_row)

		if number_of_60_sets > 0:
			row = [number_of_60_sets, product_number + "60", name_fin + " 60 m", name_eng + " 60 M", name_swe + " 60 m", weight_60, price_60]
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